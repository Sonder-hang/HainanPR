"""十八项核心制度总览路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from typing import Optional
from collections import defaultdict

from app.database import get_db
from app.models.indicator import Indicator, IndicatorExecution
from app.schemas.core18_overview import (
    Core18OverviewResponse,
    IndicatorCardItem,
    OverviewResponse,
    IndicatorExecutionData,
)

router = APIRouter(tags=["十八项核心制度-总览"])


@router.get("/overview/", response_model=Core18OverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    """
    获取十八项核心制度总览统计
    """
    total = db.query(Indicator).filter(Indicator.indicator_type == "core18").count()
    computed = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.status == "success"
    ).count()
    pending = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.status == "pending"
    ).count()
    failed = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.status == "failed"
    ).count()

    return Core18OverviewResponse(
        total_indicators=total,
        computed_indicators=computed,
        pending_indicators=pending,
        failed_indicators=failed,
    )


@router.get("/indicators/")
def list_indicators(
    keyword: Optional[str] = Query(None, description="指标名称关键词"),
    category: Optional[str] = Query(None, description="指标分类"),
    db: Session = Depends(get_db),
):
    """
    获取十八项核心制度指标列表
    """
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    if category:
        q = q.filter(Indicator.category == category)
    indicators = q.order_by(Indicator.seq).all()

    return [
        {
            "id": ind.id,
            "name": ind.name,
            "category": ind.category or "",
            "seq": ind.seq,
            "scope": ind.scope or "",
            "formula": ind.formula or "",
            "description": ind.description or "",
            "numerator_desc": ind.numerator_desc or "",
            "denominator_desc": ind.denominator_desc or "",
            "calc_type": ind.calc_type or "ratio",
            "status": ind.status,
        }
        for ind in indicators
    ]


@router.get("/execution-data/", response_model=list[IndicatorExecutionData])
def get_execution_data(
    hospital_code: Optional[str] = Query(None, description="医院编码，province表示全省"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    db: Session = Depends(get_db),
):
    """
    获取指标执行数据
    根据医院和时间筛选，查询各指标的最近执行结果
    直接匹配 time_mode 和 time_value 字段（time_value 为空时不过滤）
    """
    indicators = db.query(Indicator).filter(
        Indicator.indicator_type == "core18"
    ).all()

    results = []
    for ind in indicators:
        query = db.query(IndicatorExecution).filter(
            IndicatorExecution.indicator_id == ind.id,
            IndicatorExecution.status == "success",
            IndicatorExecution.kind == "core18",
            IndicatorExecution.time_mode == time_mode,
        )
        # time_value 为空时不过滤（查任意时间）
        if time_value is not None:
            query = query.filter(IndicatorExecution.time_value == time_value)

        if hospital_code and hospital_code != "province":
            query = query.filter(
                cast(IndicatorExecution.hospital_codes, String).contains(hospital_code)
            )

        execution = query.order_by(
            IndicatorExecution.execution_time.desc()
        ).first()

        results.append(IndicatorExecutionData(
            indicator_id=ind.id,
            indicator_name=ind.name,
            category=ind.category or "",
            calc_type=ind.calc_type or "ratio",
            has_data=execution is not None,
            rate_percent=float(execution.rate_percent) if execution and execution.rate_percent is not None else None,
            numerator_count=execution.numerator_count if execution else None,
            denominator_count=execution.denominator_count if execution else None,
        ))

    return results


def _pick_execution(exec_list: list, hospital_code: Optional[str]):
    """从多条记录中选取最合适的一条。

    - 全省/无医院（hospital_code 为空或 province）：优先取 group_by_hospital=False 的纯全省执行记录；
      若无则降级取 group_by_hospital=True 的记录。
    - 指定医院（hospital_code 有效）：只取 group_by_hospital=True 且包含该医院的记录。

    每组内按 execution_time 取最新一条。
    """
    if not exec_list:
        return None

    is_province = not hospital_code or hospital_code == "province"

    if is_province:
        # 全省/无医院：优先取 group_by_hospital=False 的记录
        non_grouped = [r for r in exec_list if not r.group_by_hospital]
        if non_grouped:
            return max(non_grouped, key=lambda r: r.execution_time)
        # 降级：取 group_by_hospital=True 中 execution_time 最新的
        return max(exec_list, key=lambda r: r.execution_time)
    else:
        # 指定医院：严格筛选 group_by_hospital=True 且包含目标医院的记录
        filtered = [
            r for r in exec_list
            if r.group_by_hospital
            and isinstance(r.hospital_codes, list)
            and hospital_code in r.hospital_codes
        ]
        if not filtered:
            return None
        return max(filtered, key=lambda r: r.execution_time)


@router.get("/overview-data/", response_model=OverviewResponse)
def get_overview_data(
    hospital_code: Optional[str] = Query(None, description="医院编码，province表示全省"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    keyword: Optional[str] = Query(None, description="指标名称关键词"),
    category: Optional[str] = Query(None, description="指标分类"),
    db: Session = Depends(get_db),
):
    """
    总览页面统一接口 - 一次返回所有数据

    返回:
    - indicators: 所有指标卡片数据（包含指标信息和执行数据）
    - categories: 所有分类列表（用于筛选器）

    医院筛选逻辑:
    - 全省(province): 优先取 group_by_hospital=False 的纯全省记录，
      若无则降级取 group_by_hospital=True 的记录。
    - 具体医院: 查找 group_by_hospital=True 且 hospital_codes 包含该医院的执行记录，
      从 hospital_results 中获取对应医院的结果。
    """
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    if category:
        q = q.filter(Indicator.category == category)

    indicators = q.order_by(Indicator.seq).all()

    all_indicators_query = db.query(Indicator.category).filter(
        Indicator.indicator_type == "core18"
    ).distinct().all()
    categories = [cat[0] for cat in all_indicators_query if cat[0]]

    # 查询 core18 指标的执行记录（成功状态、匹配时间，只取 core18 类型）
    base_query = db.query(IndicatorExecution).filter(
        IndicatorExecution.status == "success",
        IndicatorExecution.kind == "core18",
        IndicatorExecution.time_mode == time_mode,
    )
    # time_value 为空时不过滤（查任意时间的历史记录）
    if time_value is not None:
        base_query = base_query.filter(IndicatorExecution.time_value == time_value)
    all_executions = base_query.all()

    # 按指标分组
    executions_by_indicator: dict = defaultdict(list)
    for rec in all_executions:
        executions_by_indicator[rec.indicator_id].append(rec)

    # 兜底：time_mode=NULL 的历史数据（只取 core18 类型）
    fallback_executions = db.query(IndicatorExecution).filter(
        IndicatorExecution.status == "success",
        IndicatorExecution.kind == "core18",
        IndicatorExecution.time_mode.is_(None),
    ).all()
    for rec in fallback_executions:
        executions_by_indicator[rec.indicator_id].append(rec)

    # 构建指标卡片数据
    indicator_cards = []
    for ind in indicators:
        exec_list = executions_by_indicator.get(ind.id, [])
        exec_record = _pick_execution(exec_list, hospital_code)

        rate_percent = None
        numerator_count = None
        denominator_count = None
        count_value = None
        has_data = False

        if exec_record:
            calc_type = ind.calc_type or "ratio"
            has_data = True
            if calc_type == "ratio":
                rate_percent = float(exec_record.rate_percent) if exec_record.rate_percent is not None else None
                numerator_count = exec_record.numerator_count
                denominator_count = exec_record.denominator_count
            else:
                count_value = getattr(exec_record, 'count', None)

        indicator_cards.append(IndicatorCardItem(
            id=ind.id,
            name=ind.name,
            category=ind.category or "",
            calc_type=ind.calc_type or "ratio",
            numerator_desc=ind.numerator_desc or "",
            denominator_desc=ind.denominator_desc or "",
            description=ind.description or "",
            has_data=has_data,
            rate_percent=rate_percent,
            numerator_count=numerator_count,
            denominator_count=denominator_count,
            count=count_value,
        ))

    return OverviewResponse(
        indicators=indicator_cards,
        categories=categories,
    )
