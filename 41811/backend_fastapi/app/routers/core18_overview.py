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
from app.services.core18_execution_selector import (
    get_latest_execution_for_scope,
    get_latest_grouped_execution,
    is_province_scope,
)

router = APIRouter(tags=["十八项核心制度-总览"])


def _is_composite_parent_indicator(db: Session, name: str) -> bool:
    """判断是否为复合指标父级"""
    if "-" not in name:
        return False
    prefix = name + "-"
    exists = db.query(Indicator.id).filter(
        Indicator.name.startswith(prefix),
        Indicator.name != name,
        Indicator.indicator_type == "core18",
    ).first()
    return bool(exists)


def _resolve_template_type(ind: Indicator) -> str:
    if ind.template_type:
        return ind.template_type
    return "RATE" if ind.calc_type == "ratio" else "STRUCTURE"


def _get_hospital_result(
    grouped_execution,
    hospital_code: Optional[str],
):
    """从分组执行记录的 hospital_results 中找到对应医院的数据"""
    if not grouped_execution or not grouped_execution.hospital_results:
        return None
    if not isinstance(grouped_execution.hospital_results, list):
        return None
    for result in grouped_execution.hospital_results:
        if isinstance(result, dict) and result.get("hospital_code") == hospital_code:
            return result
    return None


@router.get("/overview/", response_model=Core18OverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    """
    获取十八项核心制度总览统计（排除复合指标父级）
    """
    total = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
    ).count()

    computed = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.status == "success",
    ).count()

    pending = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.status == "pending",
    ).count()

    failed = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.status == "failed",
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
    获取十八项核心制度指标列表（排除复合指标父级）
    """
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    if category:
        q = q.filter(Indicator.category == category)
    indicators = q.order_by(Indicator.seq, Indicator.id).all()

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
        if not _is_composite_parent_indicator(db, ind.name)
    ]


@router.get("/execution-data/", response_model=list[IndicatorExecutionData])
def get_execution_data(
    hospital_code: Optional[str] = Query(None, description="医院编码，province表示全省"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    db: Session = Depends(get_db),
):
    """
    获取指标执行数据（排除复合指标父级）
    """
    indicators = db.query(Indicator).filter(
        Indicator.indicator_type == "core18"
    ).all()

    is_province = is_province_scope(hospital_code)
    results = []
    for ind in indicators:
        if _is_composite_parent_indicator(db, ind.name):
            continue

        exec_record = get_latest_execution_for_scope(
            db=db,
            indicator_id=ind.id,
            time_mode=time_mode,
            time_value=time_value,
            hospital_code=hospital_code,
        )
        template_type = _resolve_template_type(ind)

        rate_percent = None
        numerator_count = None
        denominator_count = None
        has_data = False

        if is_province:
            if exec_record:
                has_data = True
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    numerator_count = exec_record.numerator_count
                    denominator_count = exec_record.denominator_count
                    rate_percent = float(exec_record.count) if exec_record.count is not None else None
                else:
                    rate_percent = float(exec_record.rate_percent) if exec_record and exec_record.rate_percent is not None else None
                    numerator_count = exec_record.numerator_count if exec_record else None
                    denominator_count = exec_record.denominator_count if exec_record else None
        else:
            grouped = get_latest_grouped_execution(
                db=db, indicator_id=ind.id, time_mode=time_mode, time_value=time_value,
            )
            hosp_result = _get_hospital_result(grouped, hospital_code)
            if hosp_result and isinstance(hosp_result, dict):
                has_data = hosp_result.get("status") == "success"
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    numerator_count = hosp_result.get("numerator_count")
                    denominator_count = hosp_result.get("denominator_count")
                    rate_percent = float(hosp_result.get("count")) if hosp_result.get("count") is not None else None
                else:
                    numerator_count = hosp_result.get("numerator_count")
                    denominator_count = hosp_result.get("denominator_count")
                    rp = hosp_result.get("ratio_percent")
                    rate_percent = float(rp) if rp is not None else None

        results.append(IndicatorExecutionData(
            indicator_id=ind.id,
            indicator_name=ind.name,
            category=ind.category or "",
            calc_type=ind.calc_type or "ratio",
            has_data=has_data,
            rate_percent=rate_percent,
            numerator_count=numerator_count,
            denominator_count=denominator_count,
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
    总览页面统一接口 - 一次返回所有数据（排除复合指标父级，子指标单独展示卡片）

    - 复合指标父级不展示（通过名称含'-'且存在子指标判断）
    - 子指标独立生成卡片，卡片 name 为子指标展示名（截取父级前缀后的部分）
    """
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    if category:
        q = q.filter(Indicator.category == category)

    indicators = q.order_by(Indicator.seq, Indicator.id).all()

    all_indicators_query = db.query(Indicator.category).filter(
        Indicator.indicator_type == "core18"
    ).distinct().all()
    categories = [cat[0] for cat in all_indicators_query if cat[0]]

    indicator_cards = []
    for ind in indicators:
        ind_name = ind.name

        if _is_composite_parent_indicator(db, ind_name):
            continue

        exec_record = get_latest_execution_for_scope(
            db=db,
            indicator_id=ind.id,
            time_mode=time_mode,
            time_value=time_value,
            hospital_code=hospital_code,
        )
        template_type = _resolve_template_type(ind)
        is_province = is_province_scope(hospital_code)

        rate_percent = None
        numerator_count = None
        denominator_count = None
        count_value = None
        has_data = False

        if is_province:
            if exec_record:
                has_data = True
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    count_value = exec_record.count
                else:
                    rate_percent = float(exec_record.rate_percent) if exec_record.rate_percent is not None else None
                    numerator_count = exec_record.numerator_count
                    denominator_count = exec_record.denominator_count
        else:
            # 具体医院：从 hospital_results 取
            grouped = get_latest_grouped_execution(
                db=db, indicator_id=ind.id, time_mode=time_mode, time_value=time_value,
            )
            hosp_result = _get_hospital_result(grouped, hospital_code)
            if hosp_result and isinstance(hosp_result, dict):
                has_data = hosp_result.get("status") == "success"
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    count_value = hosp_result.get("count")
                else:
                    numerator_count = hosp_result.get("numerator_count")
                    denominator_count = hosp_result.get("denominator_count")
                    rp = hosp_result.get("ratio_percent")
                    rate_percent = float(rp) if rp is not None else None

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
