"""十八项核心制度 - 指标分析台数据路由

分析台各子组件根据自身时间筛选条件独立请求数据。
- /indicator-config/ : 获取指标元数据（虚拟父指标 + 子指标下拉选项）
- /indicator-data/   : 获取单个指标的图表数据（支持虚拟父指标率比后计算）
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func as sql_func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.indicator import Indicator, IndicatorExecution
from app.schemas.core18_indicator_config import (
    IndicatorConfigResponse,
    IndicatorConfigData,
    SubIndicatorItem,
)
from app.services.core18_execution_selector import (
    get_latest_execution_for_scope,
    get_latest_grouped_execution,
    get_latest_trend_executions_by_time_value,
    is_province_scope,
)

router = APIRouter(tags=["十八项核心制度-指标分析台"])

SPECIAL_DEATH_PATIENT_NAME = "死亡或出院预期转归不良患者"
DEATH_TOGGLE_INDICATOR_NAMES = {
    SPECIAL_DEATH_PATIENT_NAME,
    "住院患者死亡疾病谱",
    "住院患者死亡手术谱",
    "患者住院、新生儿、手术患者住院总死亡率",
    "住院患者围手术期死亡率",
    "死亡病例讨论 5 日完成率",
    "科主任主持死亡病例讨论率",
}


# ============================================================
# 子指标识别辅助函数
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


def _resolve_template_type(ind: Indicator) -> str:
    if ind.template_type:
        if ind.template_type == "COMPOSITE":
            return "RATE"
        return ind.template_type
    return "RATE" if ind.calc_type == "ratio" else "STRUCTURE"


def _get_children_by_parent_name(db: Session, parent_name: str) -> list[Indicator]:
    """根据父指标名查询所有子指标，按ID升序"""
    prefix = parent_name + "--"
    return db.query(Indicator).filter(
        Indicator.name.startswith(prefix),
        Indicator.indicator_type == "core18",
    ).order_by(Indicator.id).all()


def _get_parent_names_from_all(db: Session) -> list[str]:
    """扫描所有指标，提取出父指标名集合（去重），按字母序排列"""
    parent_names = set()
    for ind in db.query(Indicator).filter(Indicator.indicator_type == "core18").all():
        is_sub, parent_name = _is_sub_indicator(ind.name)
        if is_sub and parent_name:
            parent_names.add(parent_name)
    return sorted(parent_names)


def _build_sub_indicators_for_composite(
    db: Session, parent_name: str
) -> list[SubIndicatorItem]:
    """查询某父级下所有子指标，构建子指标下拉选项"""
    subs = _get_children_by_parent_name(db, parent_name)
    items = []
    for sub in subs:
        sub_name_part = sub.name.split("--", 1)[1] if "--" in sub.name else sub.name
        template = _resolve_template_type(sub)
        view_mode = "structure" if template in ("STRUCTURE", "STRUCTURE-special") else "rate"
        items.append(SubIndicatorItem(
            indicator_id=sub.id,
            display_name=sub_name_part,
            view_mode=view_mode,
        ))
    return items


def _build_sub_indicators_for_rate_special(
    db: Session, parent_name: str, parent_id: int
) -> list[SubIndicatorItem]:
    """为率比型指标构建子指标下拉选项（含率比本身和子指标）"""
    subs = _get_children_by_parent_name(db, parent_name)
    items = []
    items.append(SubIndicatorItem(
        indicator_id=parent_id,
        display_name="率比",
        view_mode="ratio",
    ))
    for sub in subs:
        sub_name_part = sub.name.split("--", 1)[1] if "--" in sub.name else sub.name
        items.append(SubIndicatorItem(
            indicator_id=sub.id,
            display_name=sub_name_part,
            view_mode="rate",
        ))
    return items


def _calculate_rate_ratio(
    db: Session,
    subs: list[Indicator],
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
) -> Optional[float]:
    """对子指标的最新执行记录即时计算率比: max(rate) / min(rate)"""
    rates = []
    for sub in subs:
        exec_rec = get_latest_execution_for_scope(
            db=db,
            indicator_id=sub.id,
            time_mode=time_mode,
            time_value=time_value,
            hospital_code=hospital_code,
        )
        if exec_rec and exec_rec.rate_percent is not None:
            rates.append(float(exec_rec.rate_percent))
    if len(rates) >= 2:
        return max(rates) / min(rates)
    return None


def _get_table_headers(ind: Indicator) -> Optional[list[str]]:
    """获取 TABLE 类型指标的表头配置"""
    if ind.name == SPECIAL_DEATH_PATIENT_NAME:
        return ["患者ID", "患者姓名", "科室名称", "医院名称", "操作"]
    return None


def _build_config(
    ind: Indicator,
    db: Session,
) -> Optional[IndicatorConfigResponse]:
    """构建单个普通指标（非子指标）的配置响应"""
    name = ind.name
    template_type = _resolve_template_type(ind)
    is_death = name in DEATH_TOGGLE_INDICATOR_NAMES
    title = name

    cfg = IndicatorConfigResponse(
        indicator_id=ind.id,
        indicator_name=name,
        template_type=template_type,
        title=title,
        showDeathToggle=is_death,
        is_virtual_parent=False,
    )

    if template_type == "TABLE":
        cfg.table_headers = _get_table_headers(ind)
        return cfg

    subitem_cfg = ind.subitem_config if isinstance(ind.subitem_config, dict) else None
    subitem_type = subitem_cfg.get("type") if subitem_cfg else None
    if template_type == "STRUCTURE":
        cfg.leftTitle = "排行榜"
        chart_limit = subitem_cfg.get("limit", 20) if subitem_cfg else 20
        cfg.leftChartTitle = f"{title} TOP{chart_limit}"
        cfg.leftChartColor = "#E5455F" if is_death else "#2E57E5"
        cfg.totalCountLabel = f"{title}总量"
        cfg.rankingMode = "single"
        cfg.data.leftChartLimit = chart_limit
    elif template_type == "STRUCTURE-special":
        cfg.leftTitle = f"{title}排行榜"
        cfg.leftChartTitle1 = "治疗性操作 TOP10"
        cfg.leftChartTitle2 = "诊断性操作 TOP10"
        if subitem_type == "COMPOSITE_MULTI_RANKING":
            cfg.rankingMode = "multi"
            rankings = subitem_cfg.get("rankings", [])
            if len(rankings) >= 2:
                cfg.leftChartTitle1 = rankings[0].get("name", "排行榜1")
                cfg.leftChartColor1 = rankings[0].get("color", "#12B881")
                cfg.leftChartTitle2 = rankings[1].get("name", "排行榜2")
                cfg.leftChartColor2 = rankings[1].get("color", "#2E57E5")
        else:
            cfg.rankingMode = "double"
    elif template_type in ("RATE", "RATE-special"):
        cfg.leftTitle = f"{title}百分率直观展示"
        cfg.timeComparisonTitle = f"{title}趋势分析"
        cfg.hospitalComparisonTitle = f"{title}医院对比"

    return cfg


def _build_virtual_parent_config(
    db: Session,
    parent_name: str,
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
) -> Optional[IndicatorConfigResponse]:
    """构建虚拟父指标配置"""
    children = _get_children_by_parent_name(db, parent_name)
    if not children:
        return None

    is_rate_ratio = _is_rate_ratio_parent(parent_name)
    is_death = parent_name in DEATH_TOGGLE_INDICATOR_NAMES
    # template_type 取第一个子指标的 template；率比型仍用 "RATE-special"，复合率型用 "RATE"
    first_child_template = _resolve_template_type(children[0])
    template_type = "RATE-special" if is_rate_ratio else first_child_template

    # 虚拟父指标ID = 最小子指标ID的绝对值（取负数以标识虚拟）
    virtual_id = -children[0].id

    cfg = IndicatorConfigResponse(
        indicator_id=virtual_id,
        indicator_name=parent_name,
        template_type=template_type,
        title=parent_name,
        showDeathToggle=is_death,
        is_virtual_parent=True,
        parent_name=parent_name,
    )

    if is_rate_ratio:
        cfg.rateLabel = "率比"
        cfg.rateUnit = ""
        cfg.maxRate = 10
        cfg.yAxisUnit = ""
        cfg.leftTitle = f"{parent_name}率比展示"
        cfg.timeComparisonTitle = f"{parent_name}趋势分析"
        cfg.hospitalComparisonTitle = f"{parent_name}医院对比"
        cfg.sub_indicators = _build_sub_indicators_for_rate_special(db, parent_name, virtual_id)
        cfg.rate_ratio_value = _calculate_rate_ratio(
            db, children, hospital_code, time_mode, time_value
        )
    else:
        cfg.leftTitle = f"{parent_name}百分率展示"
        cfg.timeComparisonTitle = f"{parent_name}趋势分析"
        cfg.hospitalComparisonTitle = f"{parent_name}医院对比"
        cfg.sub_indicators = _build_sub_indicators_for_composite(db, parent_name)

    return cfg


def _query_execution(
    db: Session,
    indicator_id: int,
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
) -> Optional[IndicatorExecution]:
    return get_latest_execution_for_scope(
        db=db,
        indicator_id=indicator_id,
        time_mode=time_mode,
        time_value=time_value,
        hospital_code=hospital_code,
    )


def _query_trend_records(
    db: Session,
    indicator_id: int,
    time_mode: str,
    time_values: list[str],
    hospital_code: Optional[str] = None,
) -> list[IndicatorExecution]:
    latest_by_time_value = get_latest_trend_executions_by_time_value(
        db=db,
        indicator_id=indicator_id,
        time_mode=time_mode,
        time_values=time_values,
        hospital_code=hospital_code,
    )
    return [
        latest_by_time_value[time_value]
        for time_value in time_values
        if time_value in latest_by_time_value
    ]


def _parse_month_anchor(time_value: Optional[str]) -> tuple[int, int]:
    if time_value:
        try:
            year_str, month_str = time_value.split("-")
            year = int(year_str)
            month = int(month_str)
            if 1 <= month <= 12:
                return year, month
        except (ValueError, AttributeError):
            pass
    now = datetime.now()
    return now.year, now.month


def _parse_quarter_anchor(time_value: Optional[str]) -> tuple[int, int]:
    if time_value:
        try:
            year_str, quarter_str = time_value.split("-Q")
            year = int(year_str)
            quarter = int(quarter_str)
            if 1 <= quarter <= 4:
                return year, quarter
        except (ValueError, AttributeError):
            pass
    now = datetime.now()
    return now.year, (now.month - 1) // 3 + 1


def _shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    month_index = (year * 12 + (month - 1)) + offset
    shifted_year = month_index // 12
    shifted_month = month_index % 12 + 1
    return shifted_year, shifted_month


def _shift_quarter(year: int, quarter: int, offset: int) -> tuple[int, int]:
    quarter_index = (year * 4 + (quarter - 1)) + offset
    shifted_year = quarter_index // 4
    shifted_quarter = quarter_index % 4 + 1
    return shifted_year, shifted_quarter


def _build_month_window(anchor: tuple[int, int], has_explicit_anchor: bool) -> list[tuple[str, str]]:
    year, month = anchor
    offsets = list(range(-6, 6)) if has_explicit_anchor else list(range(-11, 1))
    result = []
    for offset in offsets:
        shifted_year, shifted_month = _shift_month(year, month, offset)
        result.append((f"{shifted_year}-{str(shifted_month).zfill(2)}", f"{shifted_year}-{shifted_month}"))
    return result


def _build_quarter_window(anchor: tuple[int, int], has_explicit_anchor: bool) -> list[tuple[str, str]]:
    year, quarter = anchor
    offsets = [-2, -1, 0, 1] if has_explicit_anchor else [-3, -2, -1, 0]
    result = []
    for offset in offsets:
        shifted_year, shifted_quarter = _shift_quarter(year, quarter, offset)
        result.append((f"{shifted_year}-Q{shifted_quarter}", f"{shifted_year}-Q{shifted_quarter}"))
    return result


def _build_special_left_data(subitem) -> tuple:
    def _build_from_items(items: list) -> dict:
        chart_data = []
        for item in items:
            if isinstance(item, dict):
                name = str(item.get("ranking_key") or item.get("ranking_name") or "")
                value = float(item.get("ranking_value") or 0)
                chart_data.append({"name": name, "value": value})
        return {"actual": chart_data, "estimated": []}

    if not subitem or not isinstance(subitem, list):
        return {"actual": [], "estimated": []}, {"actual": [], "estimated": []}

    op_t_items, op_d_items = [], []
    for item in subitem:
        if not isinstance(item, dict):
            continue
        key = str(item.get("ranking_key") or "")
        if key.startswith("OP_T_"):
            op_t_items.append(item)
        elif key.startswith("OP_D_"):
            op_d_items.append(item)

    if not op_t_items and not op_d_items:
        return _build_from_items(subitem), {"actual": [], "estimated": []}

    return _build_from_items(op_t_items or subitem), _build_from_items(op_d_items)


def _extract_execution_values(exec_record: Optional[IndicatorExecution]):
    if not exec_record:
        return None, None, None, False
    return (
        float(exec_record.rate_percent) if exec_record.rate_percent is not None else None,
        exec_record.numerator_count,
        exec_record.denominator_count,
        True,
    )


def _get_hospital_result(
    grouped_execution: Optional[IndicatorExecution],
    hospital_code: Optional[str],
) -> Optional[dict]:
    """从分组执行记录的 hospital_results 中找到对应医院的数据"""
    if not grouped_execution or not grouped_execution.hospital_results:
        return None
    if not isinstance(grouped_execution.hospital_results, list):
        return None
    for result in grouped_execution.hospital_results:
        if isinstance(result, dict) and result.get("hospital_code") == hospital_code:
            return result
    return None


def _get_primary_value(exec_record: IndicatorExecution, template_type: str) -> Optional[float]:
    if template_type in ("STRUCTURE", "STRUCTURE-special"):
        for value in (exec_record.count, exec_record.numerator_count):
            if value is not None:
                return float(value)
        return None
    return float(exec_record.rate_percent) if exec_record.rate_percent is not None else None


# ============================================================
# API 端点
# ============================================================

@router.get("/indicator-config/", response_model=list[IndicatorConfigResponse])
def get_indicator_configs(
    hospital_code: Optional[str] = Query(None, description="医院编码，province表示全省"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    db: Session = Depends(get_db),
):
    """
    获取指标配置列表：
    - 普通指标：直接返回配置
    - 虚拟父指标：通过子指标名称前缀关系动态构建，附加子指标下拉选项
    - 子指标本身不在此接口中返回
    """
    configs: list[IndicatorConfigResponse] = []

    # 1. 普通指标（不含"--"，非子指标）
    for ind in db.query(Indicator).filter(Indicator.indicator_type == "core18").order_by(Indicator.seq, Indicator.id).all():
        is_sub, _ = _is_sub_indicator(ind.name)
        if is_sub:
            continue
        cfg = _build_config(ind, db)
        if cfg is not None:
            configs.append(cfg)

    # 2. 虚拟父指标（通过子指标扫描得到）
    parent_names = _get_parent_names_from_all(db)
    for parent_name in parent_names:
        cfg = _build_virtual_parent_config(db, parent_name, hospital_code, time_mode, time_value)
        if cfg is not None:
            configs.append(cfg)

    return configs


@router.get("/indicator-data/")
def get_indicator_data(
    indicator_id: int = Query(..., description="指标ID，负数表示虚拟父指标"),
    hospital_code: Optional[str] = Query(None, description="医院编码"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    data_type: Optional[str] = Query(None, description="数据类型: card | trend | hospital | left | all"),
    selected_hospitals: Optional[str] = Query(None, description="医院编码列表，逗号分隔"),
    death_type_filter: Optional[str] = Query(None, description="死亡类型筛选: actual=离院方式死亡, estimated=转归死亡"),
    sub_indicator: Optional[int] = Query(None, description="子指标ID（率比型选择子指标时使用）"),
    db: Session = Depends(get_db),
):
    """
    获取指标数据，支持：
    - 普通子指标查询（indicator_id > 0）
    - 虚拟父指标查询（indicator_id < 0）：率比型即取即算
    """
    is_virtual_parent = indicator_id < 0

    if is_virtual_parent:
        # 虚拟父指标：通过子指标ID找到父指标名
        real_sub_id = abs(indicator_id)
        sub_ind = db.query(Indicator).filter(Indicator.id == real_sub_id).first()
        if not sub_ind:
            return {"error": f"未找到子指标: {real_sub_id}"}
        is_sub_check, parent_name = _is_sub_indicator(sub_ind.name)
        if not is_sub_check or not parent_name:
            return {"error": f"指标 {real_sub_id} 不是子指标"}
        children = _get_children_by_parent_name(db, parent_name)
        if not children:
            return {"error": f"未找到父指标 {parent_name} 的子指标"}

        is_rate_ratio = _is_rate_ratio_parent(parent_name)
        is_province = is_province_scope(hospital_code)
        current_year = datetime.now().year

        # 计算率比（全省/医院场景统一）
        rate_ratio = None
        if is_rate_ratio:
            rate_ratio = _calculate_rate_ratio(db, children, hospital_code, time_mode, time_value)

        base = {
            "indicator_id": indicator_id,
            "indicator_name": parent_name,
            "template_type": "RATE-special" if is_rate_ratio else "RATE",
            "has_data": rate_ratio is not None,
            "time_mode": time_mode,
            "time_value": time_value or "",
            "is_virtual_parent": True,
            "parent_name": parent_name,
            "rate_ratio_value": rate_ratio,
        }

        # 如果指定了 sub_indicator（用户在下拉框选择了子指标），则返回子指标的数据
        if sub_indicator is not None:
            sub_ind_target = db.query(Indicator).filter(Indicator.id == sub_indicator).first()
            if sub_ind_target:
                return _get_indicator_data_for_sub(
                    db, sub_ind_target, hospital_code, time_mode, time_value,
                    data_type, selected_hospitals, death_type_filter,
                )
            return {"error": f"未找到子指标: {sub_indicator}"}

        # 率比型数据处理
        if is_rate_ratio:
            return _get_rate_ratio_data(
                db, children, hospital_code, time_mode, time_value,
                data_type, selected_hospitals, parent_name, rate_ratio, current_year, is_province,
            )

        # 复合率型/计数型：返回第一个子指标的数据
        if children:
            first_child = children[0]
            return _get_indicator_data_for_sub(
                db, first_child, hospital_code, time_mode, time_value,
                data_type, selected_hospitals, death_type_filter,
            )
        return {"indicator_id": indicator_id, "has_data": False}

    # 普通子指标查询
    ind = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.id == indicator_id,
    ).first()
    if not ind:
        return {"error": f"未找到指标: {indicator_id}"}

    return _get_indicator_data_for_sub(
        db, ind, hospital_code, time_mode, time_value,
        data_type, selected_hospitals, death_type_filter,
    )


def _get_indicator_data_for_sub(
    db: Session,
    ind: Indicator,
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
    data_type: Optional[str],
    selected_hospitals: Optional[str],
    death_type_filter: Optional[str],
) -> dict:
    """为单个子指标获取数据"""
    name = ind.name
    template_type = _resolve_template_type(ind)
    current_year = datetime.now().year
    is_province = is_province_scope(hospital_code)

    grouped_execution = get_latest_grouped_execution(
        db=db,
        indicator_id=ind.id,
        time_mode=time_mode,
        time_value=time_value,
    )
    exec_record = _query_execution(db, ind.id, hospital_code, time_mode, time_value)
    hosp_result = _get_hospital_result(grouped_execution, hospital_code)

    if is_province:
        rate_percent, numerator_count, denominator_count, has_data = _extract_execution_values(exec_record)
    else:
        if hosp_result and isinstance(hosp_result, dict):
            has_data = hosp_result.get("status") == "success"
            if template_type in ("STRUCTURE", "STRUCTURE-special"):
                numerator_count = hosp_result.get("numerator_count")
                denominator_count = hosp_result.get("denominator_count")
                count_from_result = hosp_result.get("count")
                if count_from_result is not None:
                    rate_percent = float(count_from_result)
                elif numerator_count is not None:
                    rate_percent = float(numerator_count)
                else:
                    rate_percent = None
            else:
                numerator_count = hosp_result.get("numerator_count")
                denominator_count = hosp_result.get("denominator_count")
                rp = hosp_result.get("ratio_percent")
                rate_percent = float(rp) if rp is not None else None
        else:
            numerator_count, denominator_count, rate_percent, has_data = None, None, None, False

    trend_window = _build_month_window(_parse_month_anchor(time_value), bool(time_value)) if time_mode == "monthly" else _build_quarter_window(_parse_quarter_anchor(time_value), bool(time_value))
    trend_query_labels = [q for q, _ in trend_window]
    trend_display_labels = [d for _, d in trend_window]

    trend_value_map: dict[str, Optional[float]] = {}
    if is_province:
        records = _query_trend_records(db, ind.id, time_mode, trend_query_labels, hospital_code)
        for record in records:
            if record.time_value:
                trend_value_map[record.time_value] = _get_primary_value(record, template_type)
    else:
        for time_val in trend_query_labels:
            time_exec = get_latest_grouped_execution(db, ind.id, time_mode, time_val)
            time_hosp_result = _get_hospital_result(time_exec, hospital_code)
            if time_hosp_result and isinstance(time_hosp_result, dict):
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    v = time_hosp_result.get("count") or time_hosp_result.get("numerator_count")
                else:
                    v = time_hosp_result.get("ratio_percent")
                trend_value_map[time_val] = float(v) if v is not None else None

    x_labels = trend_display_labels
    y_values = [trend_value_map.get(label) for label in trend_query_labels]

    include_all = False
    filter_hospitals: Optional[list[str]] = None
    if selected_hospitals:
        raw = [h.strip() for h in selected_hospitals.split(",") if h.strip()]
        include_all = "all" in raw
        specific_hospitals = [h for h in raw if h != "all"]
        if specific_hospitals:
            filter_hospitals = specific_hospitals

    hospital_comparison_actual: dict = {}
    all_value = _get_primary_value(exec_record, template_type) if exec_record else None
    if include_all and all_value is not None:
        year_key = time_value.split("-")[0] if time_value else str(current_year)
        hospital_comparison_actual["all"] = {"2024": None, "2025": None, "2026": None, year_key: all_value}

    if grouped_execution and isinstance(grouped_execution.hospital_results, list):
        for result in grouped_execution.hospital_results:
            if not isinstance(result, dict):
                continue
            hosp_code_val = str(result.get("hospital_code", ""))
            if filter_hospitals and hosp_code_val not in filter_hospitals:
                continue
            if not hosp_code_val:
                continue
            if hosp_code_val not in hospital_comparison_actual:
                hospital_comparison_actual[hosp_code_val] = {"2024": None, "2025": None, "2026": None}
            if time_value:
                year_key = time_value.split("-")[0]
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    hosp_val = result.get("count")
                    if hosp_val is None:
                        hosp_val = result.get("numerator_count")
                else:
                    hosp_val = result.get("ratio_percent")
                hospital_comparison_actual[hosp_code_val][year_key] = hosp_val

    base = {
        "indicator_id": ind.id,
        "indicator_name": name,
        "template_type": template_type,
        "has_data": has_data,
        "time_mode": time_mode,
        "time_value": time_value or "",
    }

    if data_type == "card":
        return {
            **base,
            "rate_percent": rate_percent,
            "numerator_count": numerator_count,
            "denominator_count": denominator_count,
            "cardData": {
                "actual": {time_value or str(current_year): rate_percent} if has_data and rate_percent is not None else {},
                "estimated": {},
            },
        }

    if data_type == "trend":
        trend_payload = {"years": x_labels, "rates": y_values} if template_type in ("RATE", "RATE-special") else {"years": x_labels, "data": y_values}
        return {
            **base,
            "timeTrendData": {
                "actual": trend_payload,
                "estimated": {"years": x_labels, "rates": []} if template_type in ("RATE", "RATE-special") else {"years": x_labels, "data": []},
            },
        }

    if data_type == "hospital":
        return {
            **base,
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }

    def _build_ranking_left_data(subitem_data, indicator_name: str, death_filter: Optional[str]):
        subitem = subitem_data
        if subitem and isinstance(subitem, list):
            chart_data = []
            for item in subitem:
                if isinstance(item, dict):
                    name_str = str(item.get("ranking_key") or item.get("ranking_name") or "")
                    value = float(item.get("ranking_value") or 0)
                    if indicator_name == "住院患者死亡疾病谱" and death_filter:
                        item_death_type = item.get("death_type") or ""
                        expected_type = "离院方式死亡" if death_filter == "actual" else "转归死亡"
                        if item_death_type != expected_type:
                            continue
                    chart_data.append({"name": name_str, "value": value})
            chart_data.sort(key=lambda item: item["value"], reverse=True)
            return {"actual": chart_data, "estimated": []}
        return {"actual": [], "estimated": []}

    def _build_multi_ranking_left_data(subitem_data, subitem_config: dict):
        subitem = subitem_data if subitem_data is not None else []
        rankings_cfg = subitem_config.get("rankings", [])
        result = {}
        for cfg_item in rankings_cfg:
            prefix = cfg_item.get("key_prefix", "")
            ranking_id = cfg_item.get("id", "")
            items = []
            for item in subitem:
                if isinstance(item, dict):
                    key = str(item.get("ranking_key") or "")
                    if prefix and not key.startswith(prefix):
                        continue
                    display_name = key[len(prefix):] if prefix else key
                    items.append({
                        "name": display_name,
                        "value": float(item.get("ranking_value") or 0),
                    })
            items.sort(key=lambda item: item["value"], reverse=True)
            result[ranking_id] = {"actual": items[:cfg_item.get("limit", 20)], "estimated": []}
        return result

    if data_type == "left":
        left_subitem_data = None
        left_total = 0
        if is_province:
            if exec_record and exec_record.subitem_data:
                left_subitem_data = exec_record.subitem_data
            left_total = exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0)
        else:
            if hosp_result and isinstance(hosp_result, dict):
                left_subitem_data = hosp_result.get("subitem_data")
                left_total = hosp_result.get("count") or hosp_result.get("numerator_count") or 0
            else:
                left_subitem_data = None
                left_total = 0

        if template_type == "STRUCTURE-special":
            subitem_cfg = ind.subitem_config if isinstance(ind.subitem_config, dict) else None
            if subitem_cfg and subitem_cfg.get("type") == "COMPOSITE_MULTI_RANKING":
                multi_data = _build_multi_ranking_left_data(left_subitem_data, subitem_cfg)
                return {
                    **base,
                    "totalCount": left_total,
                    "multiRankingData": multi_data,
                    "leftData": {},
                    "leftData1": {},
                    "leftData2": {},
                }
            left1, left2 = _build_special_left_data(left_subitem_data)
            return {
                **base,
                "totalCount": left_total,
                "leftData": left1,
                "leftData1": left1,
                "leftData2": left2,
            }
        if template_type == "STRUCTURE":
            return {
                **base,
                "totalCount": left_total,
                "leftData": _build_ranking_left_data(left_subitem_data, ind.name, death_type_filter),
            }
        return {
            **base,
            "leftData": {"actual": {time_value or str(current_year): []}, "estimated": {}},
        }

    if template_type in ("RATE", "RATE-special"):
        return {
            **base,
            "rate_percent": rate_percent,
            "numerator_count": numerator_count,
            "denominator_count": denominator_count,
            "cardData": {
                "actual": {time_value or str(current_year): rate_percent} if has_data and rate_percent is not None else {},
                "estimated": {},
            },
            "timeTrendData": {
                "actual": {"years": x_labels, "rates": y_values},
                "estimated": {"years": x_labels, "rates": []},
            },
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }
    if template_type == "STRUCTURE":
        return {
            **base,
            "numerator_count": numerator_count,
            "totalCount": left_total if "left_total" in dir() else 0,
            "leftData": _build_ranking_left_data(
                exec_record.subitem_data if exec_record else None, ind.name, death_type_filter
            ),
            "timeTrendData": {
                "actual": {"years": x_labels, "data": y_values},
                "estimated": {"years": x_labels, "data": []},
            },
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }
    if template_type == "STRUCTURE-special":
        subitem_cfg = ind.subitem_config if isinstance(ind.subitem_config, dict) else None
        left_sub = exec_record.subitem_data if exec_record else None
        if subitem_cfg and subitem_cfg.get("type") == "COMPOSITE_MULTI_RANKING":
            multi_data = _build_multi_ranking_left_data(left_sub, subitem_cfg)
            return {
                **base,
                "numerator_count": numerator_count,
                "totalCount": 0,
                "multiRankingData": multi_data,
                "leftData": {},
                "leftData1": {},
                "leftData2": {},
                "timeTrendData": {
                    "actual": {"years": x_labels, "data": y_values},
                    "estimated": {"years": x_labels, "data": []},
                },
                "hospitalComparisonData": {
                    "actual": hospital_comparison_actual,
                    "estimated": {},
                },
            }
        left1, left2 = _build_special_left_data(left_sub)
        return {
            **base,
            "numerator_count": numerator_count,
            "totalCount": 0,
            "leftData": left1,
            "leftData1": left1,
            "leftData2": left2,
            "timeTrendData": {
                "actual": {"years": x_labels, "data": y_values},
                "estimated": {"years": x_labels, "data": []},
            },
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }

    return {"indicator_id": ind.id, "has_data": False}


def _get_rate_ratio_data(
    db: Session,
    children: list[Indicator],
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
    data_type: Optional[str],
    selected_hospitals: Optional[str],
    parent_name: str,
    rate_ratio: Optional[float],
    current_year: int,
    is_province: bool,
) -> dict:
    """为率比型虚拟父指标构建数据，即取即算"""
    base = {
        "indicator_id": -children[0].id,
        "indicator_name": parent_name,
        "template_type": "RATE-special",
        "has_data": rate_ratio is not None,
        "time_mode": time_mode,
        "time_value": time_value or "",
        "is_virtual_parent": True,
        "parent_name": parent_name,
        "rate_ratio_value": rate_ratio,
    }

    if data_type == "card":
        return {
            **base,
            "rate_percent": rate_ratio,
            "cardData": {
                "actual": {time_value or str(current_year): rate_ratio} if rate_ratio is not None else {},
                "estimated": {},
            },
        }

    # 趋势数据：取各子指标的趋势，聚合为率比趋势
    trend_window = _build_month_window(_parse_month_anchor(time_value), bool(time_value)) if time_mode == "monthly" else _build_quarter_window(_parse_quarter_anchor(time_value), bool(time_value))
    trend_query_labels = [q for q, _ in trend_window]
    trend_display_labels = [d for _, d in trend_window]

    trend_ratios: list[Optional[float]] = []
    for time_val in trend_query_labels:
        sub_rates = []
        for sub in children:
            exec_rec = get_latest_execution_for_scope(
                db=db, indicator_id=sub.id,
                time_mode=time_mode, time_value=time_val,
                hospital_code=hospital_code,
            )
            if exec_rec and exec_rec.rate_percent is not None:
                sub_rates.append(float(exec_rec.rate_percent))
        if len(sub_rates) >= 2:
            trend_ratios.append(max(sub_rates) / min(sub_rates))
        else:
            trend_ratios.append(None)

    if data_type == "trend":
        return {
            **base,
            "timeTrendData": {
                "actual": {"years": trend_display_labels, "rates": trend_ratios},
                "estimated": {"years": trend_display_labels, "rates": []},
            },
        }

    # 医院对比：取各子指标在对应医院的率，聚合为率比
    include_all = False
    filter_hospitals: Optional[list[str]] = None
    if selected_hospitals:
        raw = [h.strip() for h in selected_hospitals.split(",") if h.strip()]
        include_all = "all" in raw
        specific_hospitals = [h for h in raw if h != "all"]
        if specific_hospitals:
            filter_hospitals = specific_hospitals

    hospital_comparison_actual: dict = {}
    year_key = time_value.split("-")[0] if time_value else str(current_year)
    if include_all and rate_ratio is not None:
        hospital_comparison_actual["all"] = {"2024": None, "2025": None, "2026": None, year_key: rate_ratio}

    grouped = get_latest_grouped_execution(
        db=db, indicator_id=children[0].id,
        time_mode=time_mode, time_value=time_value,
    )
    if grouped and isinstance(grouped.hospital_results, list):
        for result in grouped.hospital_results:
            if not isinstance(result, dict):
                continue
            hosp_code = str(result.get("hospital_code", ""))
            if filter_hospitals and hosp_code not in filter_hospitals:
                continue
            if not hosp_code:
                continue
            sub_rates_hosp = []
            for sub in children:
                sub_grouped = get_latest_grouped_execution(
                    db=db, indicator_id=sub.id,
                    time_mode=time_mode, time_value=time_value,
                )
                if sub_grouped and isinstance(sub_grouped.hospital_results, list):
                    for sub_res in sub_grouped.hospital_results:
                        if isinstance(sub_res, dict) and sub_res.get("hospital_code") == hosp_code:
                            rp = sub_res.get("ratio_percent")
                            if rp is not None:
                                sub_rates_hosp.append(float(rp))
                            break
            hosp_ratio = None
            if len(sub_rates_hosp) >= 2:
                hosp_ratio = max(sub_rates_hosp) / min(sub_rates_hosp)
            if hosp_code not in hospital_comparison_actual:
                hospital_comparison_actual[hosp_code] = {"2024": None, "2025": None, "2026": None}
            hospital_comparison_actual[hosp_code][year_key] = hosp_ratio

    if data_type == "hospital":
        return {
            **base,
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }

    # data_type == "all" 或缺省：返回完整数据
    return {
        **base,
        "rate_percent": rate_ratio,
        "cardData": {
            "actual": {time_value or str(current_year): rate_ratio} if rate_ratio is not None else {},
            "estimated": {},
        },
        "timeTrendData": {
            "actual": {"years": trend_display_labels, "rates": trend_ratios},
            "estimated": {"years": trend_display_labels, "rates": []},
        },
        "hospitalComparisonData": {
            "actual": hospital_comparison_actual,
            "estimated": {},
        },
    }
