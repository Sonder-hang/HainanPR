"""十八项核心制度 - 指标分析台数据路由

分析台各子组件根据自身时间筛选条件独立请求数据。
- /indicator-config/   : 获取指标元数据（含 sub_indicators 等，用于切换模板和子指标）
- /indicator-data/     : 获取单个指标的图表数据（各组件按自身时间筛选调用）
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

def _is_composite_parent_indicator(db: Session, name: str) -> bool:
    """判断是否为复合指标父级：名称含'-' 且数据库中存在以此为前缀的子指标"""
    if "-" not in name:
        return False
    prefix = name + "-"
    exists = db.query(Indicator.id).filter(
        Indicator.name.startswith(prefix),
        Indicator.name != name,
        Indicator.indicator_type == "core18",
    ).first()
    return bool(exists)


def _get_parent_indicator_name(name: str) -> Optional[str]:
    """获取子指标的父级名称：名称含'-' 且数据库中存在以此为前缀的父级"""
    if "-" not in name:
        return None
    return name


def _is_rate_special_indicator(name: str) -> bool:
    """判断是否为率比型：指标名含'死亡率比'或'发生率比'"""
    return "死亡率比" in name or "发生率比" in name


def _resolve_template_type(ind: Indicator) -> str:
    if ind.template_type:
        if ind.template_type == "COMPOSITE":
            return "RATE"
        return ind.template_type
    return "RATE" if ind.calc_type == "ratio" else "STRUCTURE"


def _build_sub_indicators_for_composite(
    db: Session, parent_name: str
) -> list[SubIndicatorItem]:
    """查询某父级下所有子指标，构建子指标下拉选项"""
    prefix = parent_name + "-"
    subs = db.query(Indicator).filter(
        Indicator.name.startswith(prefix),
        Indicator.name != parent_name,
        Indicator.indicator_type == "core18",
    ).order_by(Indicator.id).all()

    items = []
    for sub in subs:
        sub_name_part = sub.name[len(prefix):]
        template = _resolve_template_type(sub)
        if template == "STRUCTURE" or template == "STRUCTURE-special":
            view_mode = "structure"
        else:
            view_mode = "rate"
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
    prefix = parent_name + "-"
    subs = db.query(Indicator).filter(
        Indicator.name.startswith(prefix),
        Indicator.name != parent_name,
        Indicator.indicator_type == "core18",
    ).order_by(Indicator.id).all()

    items = []
    items.append(SubIndicatorItem(
        indicator_id=parent_id,
        display_name="率比",
        view_mode="ratio",
    ))
    for sub in subs:
        sub_name_part = sub.name[len(prefix):]
        items.append(SubIndicatorItem(
            indicator_id=sub.id,
            display_name=sub_name_part,
            view_mode="rate",
        ))
    return items


def _get_table_headers(ind: Indicator) -> Optional[list[str]]:
    """获取 TABLE 类型指标的表头配置"""
    if ind.name == SPECIAL_DEATH_PATIENT_NAME:
        return ["患者ID", "患者姓名", "科室名称", "医院名称", "操作"]
    return None


def _build_config(
    ind: Indicator,
    db: Session,
) -> Optional[IndicatorConfigResponse]:
    """构建单个指标的配置响应（不含子组件图表数据）"""
    name = ind.name
    template_type = _resolve_template_type(ind)

    is_parent = _is_composite_parent_indicator(db, name)
    is_rate_special = _is_rate_special_indicator(name)

    if is_parent:
        return None

    is_death = name in DEATH_TOGGLE_INDICATOR_NAMES
    title = name

    cfg = IndicatorConfigResponse(
        indicator_id=ind.id,
        indicator_name=name,
        template_type=template_type,
        title=title,
        showDeathToggle=is_death,
        is_parent_indicator=False,
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
        if template_type == "RATE-special":
            cfg.rateLabel = "率比"
            cfg.rateUnit = ""
            cfg.maxRate = 10
            cfg.yAxisUnit = ""
        if is_rate_special:
            cfg.sub_indicators = _build_sub_indicators_for_rate_special(db, name, ind.id)
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


@router.get("/indicator-config/", response_model=list[IndicatorConfigResponse])
def get_indicator_configs(
    hospital_code: Optional[str] = Query(None, description="医院编码，province表示全省"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    db: Session = Depends(get_db),
):
    indicators = db.query(Indicator).filter(
        Indicator.indicator_type == "core18"
    ).order_by(Indicator.seq, Indicator.id).all()

    configs = []
    for ind in indicators:
        cfg = _build_config(ind, db)
        if cfg is not None:
            configs.append(cfg)

    return configs


@router.get("/indicator-data/")
def get_indicator_data(
    indicator_id: int = Query(..., description="指标 ID"),
    hospital_code: Optional[str] = Query(None, description="医院编码"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    data_type: Optional[str] = Query(None, description="数据类型: card | trend | hospital | left | all"),
    selected_hospitals: Optional[str] = Query(None, description="医院编码列表，逗号分隔"),
    death_type_filter: Optional[str] = Query(None, description="死亡类型筛选: actual=离院方式死亡, estimated=转归死亡"),
    db: Session = Depends(get_db),
):
    ind = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.id == indicator_id,
    ).first()
    if not ind:
        return {"error": f"未找到指标: {indicator_id}"}

    name = ind.name
    template_type = _resolve_template_type(ind)
    current_year = datetime.now().year
    is_province = is_province_scope(hospital_code)

    # ── 分组执行记录（始终查询，用于 hospital_results 和趋势）──────────────
    grouped_execution = get_latest_grouped_execution(
        db=db,
        indicator_id=ind.id,
        time_mode=time_mode,
        time_value=time_value,
    )

    # ── 全省 vs 具体医院的数据来源选择 ────────────────────────────────
    # 全省：从 exec_record 直接取（group_by_hospital=False 或兜底）
    # 具体医院：从 hospital_results 中取对应字典
    exec_record = _query_execution(db, ind.id, hospital_code, time_mode, time_value)
    hosp_result = _get_hospital_result(grouped_execution, hospital_code)

    # 比值/计数值的来源
    if is_province:
        rate_percent, numerator_count, denominator_count, has_data = _extract_execution_values(exec_record)
    else:
        # 具体医院：必须从 hospital_results 取
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
                rate_percent = hosp_result.get("ratio_percent")
                if rate_percent is not None:
                    rate_percent = float(rate_percent)
        else:
            numerator_count, denominator_count, rate_percent, has_data = None, None, None, False

    # ── 趋势数据（全省从 exec_record 取，具体医院从 hospital_results 取）──
    trend_window = _build_month_window(_parse_month_anchor(time_value), bool(time_value)) if time_mode == "monthly" else _build_quarter_window(_parse_quarter_anchor(time_value), bool(time_value))
    trend_query_labels = [query_label for query_label, _ in trend_window]
    trend_display_labels = [display_label for _, display_label in trend_window]

    trend_value_map: dict[str, Optional[float]] = {}

    if is_province:
        records = _query_trend_records(db, ind.id, time_mode, trend_query_labels, hospital_code)
        for record in records:
            if record.time_value:
                trend_value_map[record.time_value] = _get_primary_value(record, template_type)
    else:
        # 具体医院趋势：从各时间段的 grouped_execution 中取 hospital_results
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
        raw = [hospital.strip() for hospital in selected_hospitals.split(",") if hospital.strip()]
        include_all = "all" in raw
        specific_hospitals = [hospital for hospital in raw if hospital != "all"]
        if specific_hospitals:
            filter_hospitals = specific_hospitals

    hospital_comparison_actual: dict = {}
    all_value = _get_primary_value(exec_record, template_type) if exec_record else None
    if include_all and all_value is not None:
        year_key = time_value.split("-")[0] if time_value else str(current_year)
        hospital_comparison_actual["all"] = {"2024": None, "2025": None, "2026": None, year_key: all_value}

    # grouped_execution 已在上面定义，直接复用
    if grouped_execution and isinstance(grouped_execution.hospital_results, list):
        for result in grouped_execution.hospital_results:
            if not isinstance(result, dict):
                continue
            hospital_code_value = str(result.get("hospital_code", ""))
            if filter_hospitals and hospital_code_value not in filter_hospitals:
                continue
            if not hospital_code_value:
                continue
            if hospital_code_value not in hospital_comparison_actual:
                hospital_comparison_actual[hospital_code_value] = {"2024": None, "2025": None, "2026": None}
            if time_value:
                year_key = time_value.split("-")[0]
                if template_type in ("STRUCTURE", "STRUCTURE-special"):
                    hospital_value = result.get("count")
                    if hospital_value is None:
                        hospital_value = result.get("numerator_count")
                else:
                    hospital_value = result.get("ratio_percent")
                hospital_comparison_actual[hospital_code_value][year_key] = hospital_value

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
        # STRUCTURE/STRUCTURE-special 的排行榜数据来自 hospital_results 的 subitem_data
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
            "leftData": {
                "actual": {time_value or str(current_year): []},
                "estimated": {},
            },
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
    # data_type == "all" 的 STRUCTURE/STRUCTURE-special 回退分支（同 left 数据源）
    # left_subitem_data / left_total 已在上面设置好，直接复用
    if template_type == "STRUCTURE":
        return {
            **base,
            "numerator_count": numerator_count,
            "totalCount": left_total,
            "leftData": _build_ranking_left_data(left_subitem_data, ind.name, death_type_filter),
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
        if subitem_cfg and subitem_cfg.get("type") == "COMPOSITE_MULTI_RANKING":
            multi_data = _build_multi_ranking_left_data(left_subitem_data, subitem_cfg)
            return {
                **base,
                "numerator_count": numerator_count,
                "totalCount": left_total,
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
        left1, left2 = _build_special_left_data(left_subitem_data)
        return {
            **base,
            "numerator_count": numerator_count,
            "totalCount": left_total,
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
