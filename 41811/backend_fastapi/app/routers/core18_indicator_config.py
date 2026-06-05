"""十八项核心制度 - 指标分析台数据路由

分析台各子组件根据自身时间筛选条件独立请求数据。
- /indicator-config/   : 获取指标元数据（含 template_type 等，用于切换模板）
- /indicator-data/      : 获取单个指标的图表数据（各组件按自身时间筛选调用）
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
)
from app.services.core18_execution_selector import (
    get_latest_execution_for_scope,
    get_latest_grouped_execution,
    get_latest_trend_executions_by_time_value,
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


def _resolve_template_type(ind: Indicator) -> str:
    if ind.template_type:
        return ind.template_type
    return "RATE" if ind.calc_type == "ratio" else "STRUCTURE"


def _is_special_death_patient_indicator(ind: Indicator) -> bool:
    return ind.name == SPECIAL_DEATH_PATIENT_NAME


def _build_config(
    ind: Indicator,
) -> IndicatorConfigResponse:
    """构建单个指标的配置响应（不含子组件图表数据）"""
    template_type = _resolve_template_type(ind)
    is_death = ind.name in DEATH_TOGGLE_INDICATOR_NAMES
    title = ind.name

    cfg = IndicatorConfigResponse(
        indicator_id=ind.id,
        indicator_name=ind.name,
        template_type=template_type,  # type: ignore[arg-type]
        title=title,
        showDeathToggle=is_death,
    )

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
    elif template_type == "COMPOSITE":
        cfg.leftTitle = f"{title}细分"
        cfg.timeComparisonTitle = f"{title}趋势分析"
        cfg.hospitalComparisonTitle = f"{title}医院对比"

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
    return [latest_by_time_value[time_value] for time_value in time_values if time_value in latest_by_time_value]


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
    return now.year, ((now.month - 1) // 3) + 1


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


def _get_primary_value(exec_record: IndicatorExecution, template_type: str) -> Optional[float]:
    if template_type in ("STRUCTURE", "STRUCTURE-special"):
        for value in (exec_record.count, exec_record.numerator_count):
            if value is not None:
                return float(value)
        return None

    if template_type == "COMPOSITE":
        subitem_cfg = exec_record.indicator.subitem_config if exec_record.indicator else None
        subitem_type = subitem_cfg.get("type") if isinstance(subitem_cfg, dict) else None
        if subitem_type == "COMPOSITE_RATE":
            return float(exec_record.rate_percent) if exec_record.rate_percent is not None else None
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
    ).order_by(Indicator.seq).all()

    return [_build_config(ind) for ind in indicators]


@router.get("/indicator-data/")
def get_indicator_data(
    indicator_id: int = Query(..., description="指标 ID"),
    hospital_code: Optional[str] = Query(None, description="医院编码"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    data_type: Optional[str] = Query(None, description="数据类型: card | trend | hospital | left | all（默认all）"),
    selected_hospitals: Optional[str] = Query(None, description="医院编码列表，逗号分隔，用于hospital类型精确过滤"),
    death_type_filter: Optional[str] = Query(None, description="死亡类型筛选: actual=离院方式死亡, estimated=转归死亡（仅死亡相关指标支持）"),
    db: Session = Depends(get_db),
):
    ind = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.id == indicator_id,
    ).first()
    if not ind:
        return {"error": f"未找到指标: {indicator_id}"}

    template_type = _resolve_template_type(ind)
    current_year = datetime.now().year

    exec_record = _query_execution(db, ind.id, hospital_code, time_mode, time_value)
    rate_percent, numerator_count, denominator_count, has_data = _extract_execution_values(exec_record)

    has_explicit_trend_anchor = bool(time_value)
    trend_window = _build_month_window(_parse_month_anchor(time_value), has_explicit_trend_anchor) if time_mode == "monthly" else _build_quarter_window(_parse_quarter_anchor(time_value), has_explicit_trend_anchor)
    trend_query_labels = [query_label for query_label, _ in trend_window]
    trend_display_labels = [display_label for _, display_label in trend_window]
    records = _query_trend_records(db, ind.id, time_mode, trend_query_labels, hospital_code)

    trend_value_map: dict[str, Optional[float]] = {}
    for record in records:
        if record.time_value:
            trend_value_map[record.time_value] = _get_primary_value(record, template_type)

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

    grouped_execution = get_latest_grouped_execution(
        db=db,
        indicator_id=ind.id,
        time_mode=time_mode,
        time_value=time_value,
    )
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
                elif template_type == "COMPOSITE" and isinstance(ind.subitem_config, dict) and ind.subitem_config.get("type") == "COMPOSITE_RATE":
                    hospital_value = result.get("ratio_percent")
                elif template_type == "COMPOSITE":
                    hospital_value = result.get("count")
                    if hospital_value is None:
                        hospital_value = result.get("numerator_count")
                else:
                    hospital_value = result.get("ratio_percent")
                hospital_comparison_actual[hospital_code_value][year_key] = hospital_value

    base = {
        "indicator_id": ind.id,
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

    def _build_ranking_left_data(exec_rec, indicator_name: str, death_filter: Optional[str]):
        subitem = exec_rec.subitem_data if exec_rec else None
        if subitem and isinstance(subitem, list):
            chart_data = []
            for item in subitem:
                if isinstance(item, dict):
                    name = str(item.get("ranking_key") or item.get("ranking_name") or "")
                    value = float(item.get("ranking_value") or 0)
                    if indicator_name == "住院患者死亡疾病谱" and death_filter:
                        item_death_type = item.get("death_type") or ""
                        expected_type = "离院方式死亡" if death_filter == "actual" else "转归死亡"
                        if item_death_type != expected_type:
                            continue
                    chart_data.append({"name": name, "value": value})
            chart_data.sort(key=lambda item: item["value"], reverse=True)
            return {"actual": chart_data, "estimated": []}
        return {"actual": [], "estimated": []}

    def _build_multi_ranking_left_data(exec_rec, subitem_config: dict):
        subitem = exec_rec.subitem_data if exec_rec else []
        rankings_cfg = subitem_config.get("rankings", [])
        result = {}
        for cfg in rankings_cfg:
            prefix = cfg.get("key_prefix", "")
            ranking_id = cfg.get("id", "")
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
            result[ranking_id] = {"actual": items[:cfg.get("limit", 20)], "estimated": []}
        return result

    def _build_composite_left_data(exec_rec, time_val):
        subitem = exec_rec.subitem_data if exec_rec else None
        if subitem and isinstance(subitem, list) and len(subitem) > 0:
            first = subitem[0]
            if "key" in first:
                data_types = [
                    {"key": str(item.get("key", "")), "name": str(item.get("name", ""))}
                    for item in subitem if isinstance(item, dict)
                ]
                left_data = {
                    "actual": {
                        time_val: {str(item.get("key", "")): float(item.get("rate") or 0) for item in subitem if isinstance(item, dict)}
                    },
                    "estimated": {},
                }
                return data_types, left_data
            return None, _build_ranking_left_data(exec_rec, ind.name, death_type_filter)
        return [], {"actual": {time_val: {}}, "estimated": {}}

    if data_type == "left":
        if template_type == "STRUCTURE-special":
            subitem_cfg = ind.subitem_config if isinstance(ind.subitem_config, dict) else None
            if subitem_cfg and subitem_cfg.get("type") == "COMPOSITE_MULTI_RANKING":
                multi_data = _build_multi_ranking_left_data(exec_record, subitem_cfg)
                return {
                    **base,
                    "totalCount": exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0),
                    "multiRankingData": multi_data,
                    "leftData": {},
                    "leftData1": {},
                    "leftData2": {},
                }
            subitem = exec_record.subitem_data if exec_record else None
            left1, left2 = _build_special_left_data(subitem)
            total = exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0)
            return {
                **base,
                "totalCount": total,
                "leftData": left1,
                "leftData1": left1,
                "leftData2": left2,
            }
        if template_type == "STRUCTURE":
            total = exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0)
            return {
                **base,
                "totalCount": total,
                "leftData": _build_ranking_left_data(exec_record, ind.name, death_type_filter),
            }
        if template_type == "COMPOSITE":
            data_types, left_data = _build_composite_left_data(exec_record, time_value or str(current_year))
            return {
                **base,
                "leftData": left_data,
                "dataTypes": data_types,
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
    if template_type == "STRUCTURE":
        return {
            **base,
            "numerator_count": numerator_count,
            "totalCount": exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0),
            "leftData": _build_ranking_left_data(exec_record, ind.name, death_type_filter),
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
            multi_data = _build_multi_ranking_left_data(exec_record, subitem_cfg)
            return {
                **base,
                "numerator_count": numerator_count,
                "totalCount": exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0),
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
        subitem = exec_record.subitem_data if exec_record else None
        left1, left2 = _build_special_left_data(subitem)
        total = exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0)
        return {
            **base,
            "numerator_count": numerator_count,
            "totalCount": total,
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
    if template_type == "COMPOSITE":
        data_types, left_data = _build_composite_left_data(exec_record, time_value or str(current_year))
        trend_key = "rates" if isinstance(ind.subitem_config, dict) and ind.subitem_config.get("type") == "COMPOSITE_RATE" else "data"
        return {
            **base,
            "rate_percent": rate_percent,
            "numerator_count": numerator_count,
            "dataTypes": data_types,
            "leftData": left_data,
            "timeTrendData": {
                "actual": {"years": x_labels, trend_key: y_values},
                "estimated": {"years": x_labels, trend_key: []},
            },
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }

    return {"indicator_id": ind.id, "has_data": False}
