"""十八项核心制度总览路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.indicator import Indicator
from app.schemas.core18_overview import (
    Core18OverviewResponse,
    IndicatorCardItem,
    SubIndicatorCardItem,
    OverviewResponse,
    IndicatorExecutionData,
)
from app.services.core18_execution_selector import (
    get_latest_execution_for_scope,
    get_latest_grouped_execution,
    is_province_scope,
)

router = APIRouter(tags=["十八项核心制度-总览"])


# ============================================================
# 辅助函数
# ============================================================

def _is_sub_indicator(name: str) -> tuple[bool, Optional[str]]:
    """判断是否为子指标：名称含'--'双短横线，前缀为父指标名"""
    if "--" not in name:
        return False, None
    parts = name.split("--", 1)
    parent_name = parts[0]
    child_name = parts[1] if len(parts) > 1 else ""
    if not parent_name or not child_name:
        return False, None
    return True, parent_name


def _is_rate_ratio_parent(name: str) -> bool:
    """判断是否为率比型父指标：名称含'死亡率比'或'发生率比'"""
    return "死亡率比" in name or "发生率比" in name


def _get_children_by_parent_name(
    db: Session,
    parent_name: str,
    keyword: Optional[str] = None,
) -> list[Indicator]:
    """根据父指标名查询所有子指标，按ID升序"""
    prefix = parent_name + "--"
    q = db.query(Indicator).filter(
        Indicator.name.startswith(prefix),
        Indicator.indicator_type == "core18",
    )
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    return q.order_by(Indicator.id).all()


def _get_parent_names_from_all(
    db: Session,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
) -> list[str]:
    """扫描所有指标，提取出父指标名集合（去重），按字母序排列"""
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    if category:
        q = q.filter(Indicator.category == category)
    parent_names = set()
    for ind in q.all():
        is_sub, parent_name = _is_sub_indicator(ind.name)
        if is_sub and parent_name:
            parent_names.add(parent_name)
    return sorted(parent_names)


def _resolve_template_type(ind: Indicator) -> str:
    if ind.template_type:
        if ind.template_type == "COMPOSITE":
            return "RATE"
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


def _get_sub_card_data(
    db: Session,
    sub: Indicator,
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
) -> SubIndicatorCardItem:
    """获取单个子指标的执行数据（用于总览卡片内嵌展示）"""
    template_type = _resolve_template_type(sub)
    rate_percent = None
    count_val = None
    is_province = is_province_scope(hospital_code)

    if is_province:
        exec_rec = get_latest_execution_for_scope(
            db=db,
            indicator_id=sub.id,
            time_mode=time_mode,
            time_value=time_value,
            hospital_code=hospital_code,
        )
        if exec_rec:
            if template_type in ("STRUCTURE", "STRUCTURE-special"):
                count_val = exec_rec.count if exec_rec.count is not None else exec_rec.numerator_count
            else:
                rate_percent = float(exec_rec.rate_percent) if exec_rec.rate_percent is not None else None
    else:
        grouped = get_latest_grouped_execution(
            db=db, indicator_id=sub.id,
            time_mode=time_mode, time_value=time_value,
        )
        hosp_result = _get_hospital_result(grouped, hospital_code)
        if hosp_result and isinstance(hosp_result, dict):
            if template_type in ("STRUCTURE", "STRUCTURE-special"):
                count_val = hosp_result.get("count")
                if count_val is None:
                    count_val = hosp_result.get("numerator_count")
            else:
                rp = hosp_result.get("ratio_percent")
                rate_percent = float(rp) if rp is not None else None

    sub_name_part = sub.name.split("--", 1)[1] if "--" in sub.name else sub.name
    return SubIndicatorCardItem(
        indicator_id=sub.id,
        display_name=sub_name_part,
        rate_percent=rate_percent,
        count=count_val,
        calc_type=sub.calc_type or "ratio",
    )


def _calculate_rate_ratio(
    db: Session,
    subs: list[Indicator],
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
) -> Optional[float]:
    """对子指标的最新执行记录即时计算率比: max(rate) / min(rate)

    - 过滤 None 和 0 的率（避免数据缺失或除零）
    - 至少需要 2 个有效率才计算率比
    - 结果四舍五入保留 4 位小数
    """
    rates = []
    is_province = is_province_scope(hospital_code)

    for sub in subs:
        if is_province:
            exec_rec = get_latest_execution_for_scope(
                db=db,
                indicator_id=sub.id,
                time_mode=time_mode,
                time_value=time_value,
                hospital_code=hospital_code,
            )
            if exec_rec and exec_rec.rate_percent not in (None, 0):
                rates.append(float(exec_rec.rate_percent))
        else:
            grouped = get_latest_grouped_execution(
                db=db, indicator_id=sub.id,
                time_mode=time_mode, time_value=time_value,
            )
            hosp_result = _get_hospital_result(grouped, hospital_code)
            if hosp_result and isinstance(hosp_result, dict):
                rp = hosp_result.get("ratio_percent")
                if rp not in (None, 0):
                    rates.append(float(rp))
    if len(rates) >= 2:
        return round(max(rates) / min(rates), 4)
    return None


def _build_virtual_parent_card(
    db: Session,
    parent_name: str,
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
) -> Optional[IndicatorCardItem]:
    """构建虚拟父指标卡片"""
    children = _get_children_by_parent_name(db, parent_name)
    if not children:
        return None

    is_rate_ratio = _is_rate_ratio_parent(parent_name)
    template_type = "RATE-special" if is_rate_ratio else "RATE"

    # 计算率比（率比型）
    rate_ratio = None
    if is_rate_ratio:
        rate_ratio = _calculate_rate_ratio(
            db, children, hospital_code, time_mode, time_value
        )

    # 构建子指标内嵌列表
    sub_cards = [
        _get_sub_card_data(db, sub, hospital_code, time_mode, time_value)
        for sub in children
    ]

    # 取第一个子指标的基本信息作为父卡片的基本字段
    first_sub = children[0]
    is_province = is_province_scope(hospital_code)

    # 获取第一个子指标的执行数据
    exec_rec = get_latest_execution_for_scope(
        db=db,
        indicator_id=first_sub.id,
        time_mode=time_mode,
        time_value=time_value,
        hospital_code=hospital_code,
    )

    rate_percent = None
    numerator_count = None
    denominator_count = None
    count_value = None
    has_data = False

    if is_province:
        if exec_rec:
            if template_type in ("STRUCTURE", "STRUCTURE-special"):
                count_value = exec_rec.count
                numerator_count = exec_rec.numerator_count
                has_data = (count_value is not None) or (numerator_count is not None)
            elif is_rate_ratio:
                has_data = rate_ratio is not None
            else:
                has_data = True
                rate_percent = float(exec_rec.rate_percent) if exec_rec.rate_percent is not None else None
                numerator_count = exec_rec.numerator_count
                denominator_count = exec_rec.denominator_count
    else:
        grouped = get_latest_grouped_execution(
            db=db, indicator_id=first_sub.id,
            time_mode=time_mode, time_value=time_value,
        )
        hosp_result = _get_hospital_result(grouped, hospital_code)
        if hosp_result and isinstance(hosp_result, dict):
            if template_type in ("STRUCTURE", "STRUCTURE-special"):
                count_value = hosp_result.get("count")
                numerator_count_hosp = hosp_result.get("numerator_count")
                has_data = (count_value is not None) or (numerator_count_hosp is not None)
            elif is_rate_ratio:
                has_data = rate_ratio is not None
            else:
                has_data = hosp_result.get("status") == "success"
                numerator_count = hosp_result.get("numerator_count")
                denominator_count = hosp_result.get("denominator_count")
                rp = hosp_result.get("ratio_percent")
                rate_percent = float(rp) if rp is not None else None

    # 虚拟父指标卡片ID = 最小子指标ID的绝对值（取负数以标识虚拟）
    virtual_id = -children[0].id

    return IndicatorCardItem(
        id=virtual_id,
        name=parent_name,
        category=first_sub.category or "",
        calc_type=first_sub.calc_type or "ratio",
        numerator_desc=first_sub.numerator_desc or "",
        denominator_desc=first_sub.denominator_desc or "",
        description=first_sub.description or "",
        has_data=has_data,
        rate_percent=rate_percent,
        numerator_count=numerator_count,
        denominator_count=denominator_count,
        count=count_value,
        is_virtual_parent=True,
        parent_name=parent_name,
        sub_indicators=sub_cards,
        rate_ratio=rate_ratio,
    )


def _build_regular_card(
    db: Session,
    ind: Indicator,
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
) -> Optional[IndicatorCardItem]:
    """构建普通（非子指标）指标卡片"""
    exec_rec = get_latest_execution_for_scope(
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
        if exec_rec:
            if template_type in ("STRUCTURE", "STRUCTURE-special"):
                # STRUCTURE 类型：优先取 count，回退 numerator_count，都没有则无数据
                count_value = exec_rec.count
                numerator_count = exec_rec.numerator_count
                has_data = (count_value is not None) or (numerator_count is not None)
            else:
                has_data = True
                rate_percent = float(exec_rec.rate_percent) if exec_rec.rate_percent is not None else None
                numerator_count = exec_rec.numerator_count
                denominator_count = exec_rec.denominator_count
    else:
        grouped = get_latest_grouped_execution(
            db=db, indicator_id=ind.id,
            time_mode=time_mode, time_value=time_value,
        )
        hosp_result = _get_hospital_result(grouped, hospital_code)
        if hosp_result and isinstance(hosp_result, dict):
            if template_type in ("STRUCTURE", "STRUCTURE-special"):
                count_value = hosp_result.get("count")
                numerator_count_hosp = hosp_result.get("numerator_count")
                has_data = (count_value is not None) or (numerator_count_hosp is not None)
            else:
                has_data = hosp_result.get("status") == "success"
                numerator_count = hosp_result.get("numerator_count")
                denominator_count = hosp_result.get("denominator_count")
                rp = hosp_result.get("ratio_percent")
                rate_percent = float(rp) if rp is not None else None

    return IndicatorCardItem(
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
        is_virtual_parent=False,
    )


@router.get("/overview/", response_model=Core18OverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    """
    获取十八项核心制度总览统计
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
    获取十八项核心制度指标列表（排除子指标，返回普通指标+虚拟父指标）
    """
    # 子指标不直接返回，父指标通过虚拟方式构建
    # 普通指标（不含"--"的）
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    if category:
        q = q.filter(Indicator.category == category)
    indicators = q.order_by(Indicator.seq, Indicator.id).all()

    results = []
    for ind in indicators:
        is_sub, _ = _is_sub_indicator(ind.name)
        if is_sub:
            continue
        results.append({
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
        })

    return results


@router.get("/execution-data/", response_model=list[IndicatorExecutionData])
def get_execution_data(
    hospital_code: Optional[str] = Query(None, description="医院编码，province表示全省"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    db: Session = Depends(get_db),
):
    """
    获取指标执行数据（子指标不单独展示，虚拟父指标计算率比）
    """
    # 子指标不单独展示
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    indicators = q.all()

    results = []
    for ind in indicators:
        is_sub, parent_name = _is_sub_indicator(ind.name)
        if is_sub:
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

        if is_province_scope(hospital_code):
            if exec_record:
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    # STRUCTURE 类型：优先取 count，回退 numerator_count，都没有则无数据
                    numerator_count = exec_record.numerator_count
                    count_from_record = exec_record.count
                    rate_percent = float(count_from_record) if count_from_record is not None else None
                    has_data = (count_from_record is not None) or (numerator_count is not None)
                else:
                    has_data = True
                    rate_percent = float(exec_record.rate_percent) if exec_record and exec_record.rate_percent is not None else None
                    numerator_count = exec_record.numerator_count if exec_record else None
                    denominator_count = exec_record.denominator_count if exec_record else None
        else:
            grouped = get_latest_grouped_execution(
                db=db, indicator_id=ind.id, time_mode=time_mode, time_value=time_value,
            )
            hosp_result = _get_hospital_result(grouped, hospital_code)
            if hosp_result and isinstance(hosp_result, dict):
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    numerator_count = hosp_result.get("numerator_count")
                    count_from_hosp = hosp_result.get("count")
                    rate_percent = float(count_from_hosp) if count_from_hosp is not None else None
                    has_data = (count_from_hosp is not None) or (numerator_count is not None)
                else:
                    has_data = hosp_result.get("status") == "success"
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
    总览页面统一接口 - 一次返回所有数据

    - 普通指标：直接生成卡片
    - 子指标：通过名称含'--'识别，动态构建虚拟父指标卡片
    - 子指标本身不单独展示卡片
    - 率比型虚拟父指标：即时计算率比 max(rate)/min(rate)
    """
    # 获取所有分类
    all_q = db.query(Indicator.category).filter(Indicator.indicator_type == "core18")
    if keyword:
        all_q = all_q.filter(Indicator.name.contains(keyword))
    if category:
        all_q = all_q.filter(Indicator.category == category)
    categories = [cat[0] for cat in all_q.distinct().all() if cat[0]]

    indicator_cards: list[IndicatorCardItem] = []

    # 1. 普通指标（不含"--"，非子指标）
    all_q2 = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        all_q2 = all_q2.filter(Indicator.name.contains(keyword))
    if category:
        all_q2 = all_q2.filter(Indicator.category == category)
    for ind in all_q2.order_by(Indicator.seq, Indicator.id).all():
        is_sub, _ = _is_sub_indicator(ind.name)
        if is_sub:
            continue
        card = _build_regular_card(db, ind, hospital_code, time_mode, time_value)
        if card:
            indicator_cards.append(card)

    # 2. 虚拟父指标（从子指标扫描得到）
    parent_names = _get_parent_names_from_all(db, keyword, category)
    for parent_name in parent_names:
        # 过滤分类
        children = _get_children_by_parent_name(db, parent_name)
        if children and children[0].category == category:
            pass
        if children and keyword:
            child_names = " ".join(c.name for c in children)
            if keyword not in parent_name and keyword not in child_names:
                continue
        card = _build_virtual_parent_card(db, parent_name, hospital_code, time_mode, time_value)
        if card:
            indicator_cards.append(card)

    return OverviewResponse(
        indicators=indicator_cards,
        categories=categories,
    )
