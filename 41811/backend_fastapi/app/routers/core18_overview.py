"""十八项核心制度总览路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.indicator import Indicator
from app.schemas.core18_overview import (
    Core18OverviewResponse,
    IndicatorCardItem,
    OverviewResponse,
    IndicatorExecutionData,
)
from app.services.core18_execution_selector import get_latest_execution_for_scope

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
            "category": ind.category,
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
    直接匹配 time_mode 和 time_value 字段
    """
    # 查询所有 core18 指标
    indicators = db.query(Indicator).filter(
        Indicator.indicator_type == "core18"
    ).all()

    results = []
    for ind in indicators:
        execution = get_latest_execution_for_scope(
            db=db,
            indicator_id=ind.id,
            time_mode=time_mode,
            time_value=time_value,
            hospital_code=hospital_code,
        )

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
    - 全省(province): 从 indicator_execution 表的直接字段获取数据
      (rate_percent, numerator_count, denominator_count)
      若同一指标有多条记录，取最新的

    - 具体医院: 查找 group_by_hospital=true 且 hospital_codes 包含该医院的执行记录，
      从 hospital_results 中获取对应医院的结果
      若同一医院有多条执行记录，取最新的
    """
    # 构建指标基础查询
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    if category:
        q = q.filter(Indicator.category == category)

    indicators = q.order_by(Indicator.seq).all()

    # 收集所有分类
    all_indicators_query = db.query(Indicator.category).filter(
        Indicator.indicator_type == "core18"
    ).distinct().all()
    categories = [cat[0] for cat in all_indicators_query if cat[0]]

    # 按指标分组，每组取最合适的一条执行记录
    indicator_cards = []
    for ind in indicators:
        exec_record = get_latest_execution_for_scope(
            db=db,
            indicator_id=ind.id,
            time_mode=time_mode,
            time_value=time_value,
            hospital_code=hospital_code,
        )

        # 根据医院筛选逻辑获取数据
        rate_percent = None
        numerator_count = None
        denominator_count = None
        count_value = None
        has_data = False

        if exec_record:
            calc_type = ind.calc_type or "ratio"
            template_type = ind.template_type
            has_data = True
            # 计数型指标：STRUCTURE / STRUCTURE-special / 计数型 COMPOSITE_RANKING → 取 count
            # 比值型指标：RATE / COMPOSITE_RATE → 取 rate_percent
            if calc_type == "count" or template_type in ("STRUCTURE", "STRUCTURE-special"):
                count_value = exec_record.count
            else:
                rate_percent = float(exec_record.rate_percent) if exec_record.rate_percent is not None else None
                numerator_count = exec_record.numerator_count
                denominator_count = exec_record.denominator_count

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
