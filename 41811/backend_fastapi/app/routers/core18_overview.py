"""十八项核心制度总览路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

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
        # 构建查询条件
        query = db.query(IndicatorExecution).filter(
            IndicatorExecution.indicator_id == ind.id,
            IndicatorExecution.status == "success",
            IndicatorExecution.time_mode == time_mode,
            IndicatorExecution.time_value == time_value,
        )

        # 医院筛选（如果指定了医院）
        # hospital_codes 存储为 JSON 数组
        if hospital_code and hospital_code != "province":
            from sqlalchemy import cast, String
            query = query.filter(
                cast(IndicatorExecution.hospital_codes, String).contains(hospital_code)
            )

        # 取最新一条记录
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

    # 查询所有 core18 指标的执行记录
    base_query = db.query(IndicatorExecution).filter(
        IndicatorExecution.status == "success",
        IndicatorExecution.time_mode == time_mode,
        IndicatorExecution.time_value == time_value,
    )

    all_executions = base_query.all()

    # 按指标分组，每组取最新的执行记录
    # 结构: {indicator_id: {execution_record}}
    latest_execution_map = {}
    for exec_record in all_executions:
        ind_id = exec_record.indicator_id
        if ind_id not in latest_execution_map:
            latest_execution_map[ind_id] = exec_record
        else:
            if exec_record.execution_time > latest_execution_map[ind_id].execution_time:
                latest_execution_map[ind_id] = exec_record

    # 构建指标卡片数据
    indicator_cards = []
    for ind in indicators:
        exec_record = latest_execution_map.get(ind.id)

        # 根据医院筛选逻辑获取数据
        rate_percent = None
        numerator_count = None
        denominator_count = None
        count_value = None
        has_data = False

        if exec_record:
            calc_type = ind.calc_type or "ratio"

            if hospital_code == "province" or not hospital_code:
                # 全省：直接从 indicator_execution 表的字段获取
                has_data = True
                if calc_type == "ratio":
                    # 比值型指标
                    rate_percent = float(exec_record.rate_percent) if exec_record.rate_percent is not None else None
                    numerator_count = exec_record.numerator_count
                    denominator_count = exec_record.denominator_count
                else:
                    # 计数型指标
                    count_value = exec_record.count
            else:
                # 具体医院：需要从 hospital_results 中获取
                if exec_record.group_by_hospital and exec_record.hospital_codes and exec_record.hospital_results:
                    # 检查 hospital_codes 中是否包含目标医院
                    hospital_codes = exec_record.hospital_codes
                    if isinstance(hospital_codes, list) and hospital_code in hospital_codes:
                        # 从 hospital_results 中查找对应医院的结果
                        hospital_results = exec_record.hospital_results
                        if isinstance(hospital_results, list):
                            for result in hospital_results:
                                if isinstance(result, dict) and result.get("hospital_code") == hospital_code:
                                    has_data = True
                                    if calc_type == "ratio":
                                        # 比值型指标
                                        rate_percent = result.get("ratio_percent")
                                        numerator_count = result.get("numerator_count")
                                        denominator_count = result.get("denominator_count")
                                    else:
                                        # 计数型指标
                                        count_value = result.get("count")
                                    break

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
