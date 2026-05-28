"""十八项核心制度 - 指标分析台数据路由

分析台各子组件根据自身时间筛选条件独立请求数据。
- /indicator-config/   : 获取指标元数据（含 template_type 等，用于切换模板）
- /indicator-data/      : 获取单个指标的图表数据（各组件按自身时间筛选调用）
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import cast, String, func as sql_func
from typing import Optional

from app.database import get_db
from app.models.indicator import Indicator, IndicatorExecution
from app.schemas.core18_indicator_config import (
    IndicatorConfigResponse,
    IndicatorConfigData,
)

router = APIRouter(tags=["十八项核心制度-指标分析台"])

# ============================================================
# DB 指标名称 -> cascader key 的精确映射（与分析台 cascade 数据源一致）
# ============================================================
DB_NAME_TO_KEY: dict[str, str] = {
    "患者入院 48 小时内转科的比例": "transferWithin48HoursRate",
    "患者入院 8 小时内查房率": "patientAdmissionRoundRate",
    "上级医师查房记录规范率": "seniorPhysicianRoundRate",
    "住院患者非计划手术率": "unplannedSurgeryRate",
    "急会诊及时到位率": "emergencyConsultationTimelyRate",
    "急会诊有效率": "emergencyConsultationEffectiveRate",
    "普通会诊及时完成率": "regularConsultationTimelyRate",
    "普通会诊有效率": "regularConsultationEffectiveRate",
    "手术患者特级护理/一级护理出院率": "surgicalSpecialCareDischargeRate",
    "非计划再次住院/手术患者疑难病例讨论完成率": "unplannedRehospitalizationSurgeryDiscussionRate",
    "非计划再次住院/手术患者疑难病例讨论记录完整率": "unplannedRehospitalizationSurgeryDiscussionCompleteRate",
    "高额异常费用患者进行疑难病例讨论的占比": "highCostDiscussionRate",
    "急危重症患者抢救成功率": "criticalCareSuccessRate",
    "术前讨论完成率": "preoperativeDiscussionRate",
    "术者参加术前讨论率": "surgeonParticipationInPreoperativeDiscussionRate",
    "术前讨论计划手术一致率": "preoperativePlanConsistencyRate",
    "实际手术术者与计划手术术者一致率": "surgeonConsistencyRate",
    "死亡病例讨论 5 日完成率": "deathCaseDiscussionWithin5DaysRate",
    "科主任主持死亡病例讨论率": "departmentDirectorPresideDeathDiscussionRate",
    "长期医嘱当日终止率": "longTermOrderTerminationRate",
    "手术医师手术时间重合率": "surgeonTimeOverlapRate",
    "麻醉医师手术时间重合率": "anesthesiologistTimeOverlapRate",
    "四级手术与三级手术并发症发生率比": "complicationRateRatio",
    "四级手术与三级手术患者死亡率比": "mortalityRateRatio",
    "四级手术术前多学科讨论完成率": "preoperativeMultidisciplinaryDiscussionRateForLevel4",
    "三、四级手术实际开展率": "level3And4SurgeryImplementationRate",
    "危急值报告时间": "criticalValueReportTime",
    "住院患者危急值当日及时处置率": "criticalValueTimelyDisposalRate",
    "特殊使用级抗菌药物使用会诊率": "specialAntibioticConsultationRate",
    "临床用血后评估记录率": "bloodUsageEvaluationRate",
    "术中自体血回输率": "autologousBloodTransfusionRate",
    "主要诊断ICD-10编码亚目种类数": "icd10Subcategories",
    "主要手术ICD-9-CM-3四位码种类数": "icd9Cm3Categories",
    "死亡或出院预期转归不良患者": "deathPatientDefinition",
    "住院患者死亡疾病谱": "deathDiseaseSpectrum",
    "住院患者死亡手术谱": "deathSurgicalSpectrum",
    "患者住院、新生儿、手术患者住院总死亡率": "overallMortalityRate",
    "非预期再住院情况分析": "unexpectedRehospitalizationAnalysis",
    "非计划重返手术室再手术分析": "unplannedReturnToORAnalysis",
    "住院患者围手术期死亡率": "perioperativeMortality",
    "手术并发症发生率": "surgicalComplication",
    "I类切口手术抗菌药物预防使用率": "antibioticProphylaxis",
    "住院手术患者VTE发生率": "vteIncidence",
}

# cascader key -> template_type（精确映射）
KEY_TO_TEMPLATE_TYPE: dict[str, str] = {
    "deathPatientDefinition": "STRUCTURE",
    "deathDiseaseSpectrum": "STRUCTURE",
    "deathSurgicalSpectrum": "STRUCTURE",
    "icd10Subcategories": "STRUCTURE",
    "icd9Cm3Categories": "STRUCTURE-special",
    "overallMortalityRate": "COMPOSITE",
    "perioperativeMortality": "COMPOSITE",
    "unexpectedRehospitalizationAnalysis": "COMPOSITE",
    "unplannedReturnToORAnalysis": "COMPOSITE",
    "complicationRateRatio": "RATE-special",
    "mortalityRateRatio": "RATE-special",
    "surgicalComplication": "RATE",
}

# 死亡相关指标集合（决定 showDeathToggle）
DEATH_INDICATOR_KEYS = {
    "deathPatientDefinition", "deathDiseaseSpectrum", "deathSurgicalSpectrum",
    "overallMortalityRate", "perioperativeMortality",
    "deathCaseDiscussionWithin5DaysRate", "departmentDirectorPresideDeathDiscussionRate",
}


def _build_config(
    ind: Indicator,
    cascader_key: str,
    db: Session,
    hospital_code: Optional[str],
    time_mode: str,
    time_value: Optional[str],
) -> IndicatorConfigResponse:
    """构建单个指标的配置响应（不含子组件图表数据）"""
    template_type = ind.template_type or KEY_TO_TEMPLATE_TYPE.get(
        cascader_key,
        "RATE" if ind.calc_type == "ratio" else "STRUCTURE"
    )

    is_death = cascader_key in DEATH_INDICATOR_KEYS
    title = ind.name

    # 构建基础配置
    cfg = IndicatorConfigResponse(
        indicator_key=cascader_key,
        indicator_id=ind.id,
        indicator_name=ind.name,
        template_type=template_type,  # type: ignore
        title=title,
        showDeathToggle=is_death,
    )

    # 设置模板相关标题
    if template_type == "STRUCTURE":
        cfg.leftTitle = "排行榜"
        cfg.leftChartTitle = f"{title} TOP10"
        cfg.leftChartColor = "#E5455F" if is_death else "#2E57E5"
        cfg.totalCountLabel = f"{title}总量"
    elif template_type == "STRUCTURE-special":
        cfg.leftTitle = f"{title}排行榜"
        cfg.leftChartTitle1 = "治疗性操作 TOP10"
        cfg.leftChartTitle2 = "诊断性操作 TOP10"
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
    """查询指定指标的执行记录（最新成功记录）"""
    query = db.query(IndicatorExecution).filter(
        IndicatorExecution.indicator_id == indicator_id,
        IndicatorExecution.status == "success",
        IndicatorExecution.time_mode == time_mode,
    )
    if time_value:
        query = query.filter(IndicatorExecution.time_value == time_value)
    if hospital_code and hospital_code != "province":
        query = query.filter(
            cast(IndicatorExecution.hospital_codes, String).contains(hospital_code)
        )
    return query.order_by(IndicatorExecution.execution_time.desc()).first()


def _query_trend_records(
    db: Session,
    indicator_id: int,
    time_mode: str,
    years: list[int],
) -> list[IndicatorExecution]:
    """查询近 N 年所有月度/季度执行记录（用于聚合年度趋势）"""
    patterns = []
    for y in years:
        if time_mode == "monthly":
            patterns.extend([f"{y}-{str(m).zfill(2)}" for m in range(1, 13)])
        else:
            patterns.extend([f"{y}-Q{q}" for q in range(1, 5)])
    return db.query(IndicatorExecution).filter(
        IndicatorExecution.indicator_id == indicator_id,
        IndicatorExecution.status == "success",
        IndicatorExecution.time_mode == time_mode,
        IndicatorExecution.time_value.in_(patterns),
    ).order_by(IndicatorExecution.time_value.asc()).all()


def _extract_execution_values(
    exec_record: Optional[IndicatorExecution],
    hospital_code: Optional[str],
):
    """从执行记录中提取 rate/numerator/denominator 数值"""
    if not exec_record:
        return None, None, None, False

    rate_percent = None
    numerator_count = None
    denominator_count = None
    has_data = False

    if hospital_code == "province" or not hospital_code:
        has_data = True
        rate_percent = float(exec_record.rate_percent) if exec_record.rate_percent is not None else None
        numerator_count = exec_record.numerator_count
        denominator_count = exec_record.denominator_count
    else:
        if exec_record.group_by_hospital and exec_record.hospital_codes and exec_record.hospital_results:
            hospital_codes = exec_record.hospital_codes
            if isinstance(hospital_codes, list) and hospital_code in hospital_codes:
                hospital_results = exec_record.hospital_results
                if isinstance(hospital_results, list):
                    for result in hospital_results:
                        if isinstance(result, dict) and result.get("hospital_code") == hospital_code:
                            has_data = True
                            rate_percent = result.get("ratio_percent")
                            numerator_count = result.get("numerator_count")
                            denominator_count = result.get("denominator_count")
                            break

    return rate_percent, numerator_count, denominator_count, has_data


# ============================================================
# 路由
# ============================================================

@router.get("/indicator-config/", response_model=list[IndicatorConfigResponse])
def get_indicator_configs(
    hospital_code: Optional[str] = Query(None, description="医院编码，province表示全省"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    db: Session = Depends(get_db),
):
    """
    获取所有 core18 指标的分析台配置（含模板类型）。
    用于分析台页面切换指标时加载配置信息。

    指标元数据（template_type / title / showDeathToggle 等）从数据库获取，
    图表数据由各子组件按自身时间筛选独立请求 /indicator-data/ 接口。
    """
    indicators = db.query(Indicator).filter(
        Indicator.indicator_type == "core18"
    ).order_by(Indicator.seq).all()

    configs = []
    for ind in indicators:
        cascader_key = DB_NAME_TO_KEY.get(ind.name, "")
        cfg = _build_config(ind, cascader_key, db, hospital_code, time_mode, time_value)
        configs.append(cfg)

    return configs


@router.get("/indicator-data/")
def get_indicator_data(
    indicator_key: str = Query(..., description="指标 key（cascader key）"),
    hospital_code: Optional[str] = Query(None, description="医院编码"),
    time_mode: str = Query("monthly", description="时间模式: monthly | quarterly"),
    time_value: Optional[str] = Query(None, description="时间值: 2026-05 | 2026-Q1"),
    data_type: Optional[str] = Query(None, description="数据类型: card | trend | hospital | all（默认all）"),
    selected_hospitals: Optional[str] = Query(None, description="医院编码列表，逗号分隔，用于hospital类型精确过滤"),
    db: Session = Depends(get_db),
):
    """
    获取指定指标在指定时间/医院条件下的图表数据。

    data_type 参数决定返回内容：
    - card    : 卡片数据（精确 time_value 的 rate）
    - trend   : 趋势数据（近 3 年趋势，当前年按月/季展开）
    - hospital: 医院对比数据（selected_hospitals 精确过滤）
    - all     : 全部数据（默认，兼容现有逻辑）

    数据来源：indicator_execution 表，按 time_mode + time_value 匹配最新成功记录。
    """
    # 通过 cascader key 找到对应指标
    indicator_name = None
    for db_name, key in DB_NAME_TO_KEY.items():
        if key == indicator_key:
            indicator_name = db_name
            break

    if not indicator_name:
        return {"error": f"未找到指标 key: {indicator_key}"}

    ind = db.query(Indicator).filter(
        Indicator.indicator_type == "core18",
        Indicator.name == indicator_name,
    ).first()

    if not ind:
        return {"error": f"未找到指标: {indicator_name}"}

    template_type = ind.template_type or KEY_TO_TEMPLATE_TYPE.get(
        indicator_key,
        "RATE" if ind.calc_type == "ratio" else "STRUCTURE"
    )

    current_year = 2026  # 可替换为 datetime.now().year

    # ---- card data ----
    exec_record = _query_execution(db, ind.id, hospital_code, time_mode, time_value)
    rate_percent, numerator_count, denominator_count, has_data = _extract_execution_values(
        exec_record, hospital_code
    )

    # ---- trend data ----
    # 趋势数据取数逻辑：
    # - RATE / RATE-special：取 rate_percent（比值型指标）
    # - STRUCTURE / STRUCTURE-special / COMPOSITE：取 count（总数/病例数），代表该时间段的疾病谱规模
    records = _query_trend_records(db, ind.id, time_mode, [current_year - 2, current_year - 1, current_year])
    from collections import defaultdict
    period_values: dict = defaultdict(list)

    # STRUCTURE 型指标（排行榜型）用 count（总数），比值型指标用 rate_percent
    is_count_type_trend = template_type in ("STRUCTURE", "STRUCTURE-special", "COMPOSITE")
    for rec in records:
        if rec.time_value:
            val = None
            if is_count_type_trend:
                # 计数型指标：取 numerator_count（排行榜总数量）
                val = rec.numerator_count
            else:
                # 比值型指标：取 rate_percent
                val = rec.rate_percent
            if val is not None:
                period_values[rec.time_value].append(float(val))

    def last(lst):
        """取最后一个非空值：统一取最近一次执行结果，避免多记录时取平均导致小数或不必要的平滑"""
        valid = [v for v in lst if v is not None]
        return valid[-1] if valid else None

    def yearly_sum(period_values: dict, year: int) -> Optional[float]:
        """非当年年度聚合：各月取最近一次执行结果后求和，适用于计数型（保持整数）；比值型也用此方式保持语义一致"""
        total = 0.0
        has_any = False
        for m in range(1, 13):
            label = f"{year}-{str(m).zfill(2)}"
            v = last(period_values.get(label, []))
            if v is not None:
                total += v
                has_any = True
        return round(total, 2) if has_any else None

    x_labels: list = []
    y_values: list = []
    for y in [current_year - 2, current_year - 1, current_year]:
        if y == current_year:
            if time_mode == "monthly":
                for m in range(1, 13):
                    label = f"{y}-{str(m).zfill(2)}"
                    x_labels.append(f"{m}月")
                    y_values.append(last(period_values.get(label, [])))
            else:
                for q in range(1, 5):
                    label = f"{y}-Q{q}"
                    x_labels.append(f"Q{q}")
                    y_values.append(last(period_values.get(label, [])))
        else:
            x_labels.append(str(y))
            y_values.append(yearly_sum(period_values, y))

    # ---- hospital data ----
    # 解析前端传入的医院列表（逗号分隔，如 "all,h001,h002"）
    # "all" 表示全省，和具体医院一起返回
    include_all = False
    filter_hospitals: Optional[list] = None
    if selected_hospitals:
        raw = [h.strip() for h in selected_hospitals.split(",") if h.strip()]
        include_all = "all" in raw
        specific_hospitals = [h for h in raw if h != "all"]
        if specific_hospitals:
            filter_hospitals = specific_hospitals

    hospital_comparison_actual: dict = {}

    # STRUCTURE 型指标用 count（总数），比值型指标用 rate_percent
    is_count_type_hosp = template_type in ("STRUCTURE", "STRUCTURE-special", "COMPOSITE")
    all_value = numerator_count if is_count_type_hosp else rate_percent

    # 1. 全省数据
    if include_all and all_value is not None:
        year_key = time_value.split("-")[0] if time_value else str(current_year)
        hospital_comparison_actual["all"] = {"2024": None, "2025": None, "2026": None, year_key: all_value}

    # 2. 各医院数据：从 group_by_hospital 记录中取 hospital_results
    hospital_exec_query = db.query(IndicatorExecution).filter(
        IndicatorExecution.indicator_id == ind.id,
        IndicatorExecution.status == "success",
        IndicatorExecution.time_mode == time_mode,
        IndicatorExecution.group_by_hospital == True,
    )
    if time_value:
        hospital_exec_query = hospital_exec_query.filter(
            IndicatorExecution.time_value == time_value
        )
    hospital_records = hospital_exec_query.order_by(
        IndicatorExecution.execution_time.desc()
    ).all()

    for rec in hospital_records:
        if rec.hospital_codes and rec.hospital_results:
            for result in rec.hospital_results:
                if isinstance(result, dict):
                    hc = str(result.get("hospital_code", ""))
                    # 如果指定了具体医院列表，只保留列表内的医院
                    if filter_hospitals and hc not in filter_hospitals:
                        continue
                    if hc and hc not in hospital_comparison_actual:
                        hospital_comparison_actual[hc] = {"2024": None, "2025": None, "2026": None}
                        if time_value:
                            year_key = time_value.split("-")[0]
                            # STRUCTURE 型用 count，比值型用 ratio_percent
                            hosp_val = result.get("count") if is_count_type_hosp else result.get("ratio_percent")
                            hospital_comparison_actual[hc][year_key] = hosp_val

    # ---- 构建响应（根据 data_type 返回不同子集） ----
    # 统一的基础字段
    base = {
        "indicator_key": indicator_key,
        "indicator_id": ind.id,
        "template_type": template_type,
        "has_data": has_data,
        "time_mode": time_mode,
        "time_value": time_value or "",
    }

    if data_type == "card":
        return {
            **base,
            "has_data": has_data,
            "rate_percent": rate_percent,
            "numerator_count": numerator_count,
            "denominator_count": denominator_count,
            "cardData": {
                "actual": {time_value or str(current_year): rate_percent} if has_data and rate_percent is not None else {},
                "estimated": {},
            },
        }

    if data_type == "trend":
        if template_type in ("RATE", "RATE-special"):
            return {
                **base,
                "timeTrendData": {
                    "actual": {"years": x_labels, "rates": y_values},
                    "estimated": {"years": x_labels, "rates": []},
                },
            }
        else:
            return {
                **base,
                "timeTrendData": {
                    "actual": {"years": x_labels, "data": y_values},
                    "estimated": {"years": x_labels, "data": []},
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

    # 构建排行榜/子项数据辅助函数
    def _build_ranking_left_data(exec_rec, time_val):
        """从 exec_record.subitem_data 构建 STRUCTURE 型 leftData

        STRUCTURE 的排行榜数据直接存储为数组：
          subitem_data = [{ranking_key: "A099", ranking_value: 1}, ...]
        转换为前端所需格式：
          leftData = { actual: [{name: "A099", value: 1}, ...], estimated: [] }
        注意：不再嵌套 time_val，直接返回图表数组，前端按 dataSource = localLeftData['actual'] 取用
        """
        subitem = exec_rec.subitem_data if exec_rec else None
        if subitem and isinstance(subitem, list):
            chart_data = []
            for item in subitem:
                if isinstance(item, dict):
                    name = str(item.get("ranking_key") or item.get("ranking_name") or "")
                    value = float(item.get("ranking_value") or 0)
                    chart_data.append({"name": name, "value": value})
            # 返回图表数组（无 time_val 嵌套），与前端 updateSingleChart 直接取用 actual 数组的逻辑对齐
            return {"actual": chart_data, "estimated": []}
        return {"actual": [], "estimated": []}

    def _build_composite_left_data(exec_rec, time_val):
        """从 exec_record.subitem_data 构建 COMPOSITE 型 leftData 和 dataTypes"""
        subitem = exec_rec.subitem_data if exec_rec else None
        if subitem and isinstance(subitem, list) and len(subitem) > 0:
            # 复合率型：[{"key": "clear_same_day", "name": "...", "rate": 0.5}, ...]
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
            # 复合计数型：排行榜格式
            return _build_ranking_left_data(exec_rec, time_val), None
        return [], {"actual": {time_val: {}}, "estimated": {}}

    if data_type == "left":
        if template_type == "STRUCTURE-special":
            # totalCount 暂用 numerator_count，后续可拆分为治疗性/诊断性分别统计
            total = exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0)
            return {
                **base,
                "totalCount": total,
                "leftData1": {"actual": [], "estimated": []},
                "leftData2": {"actual": [], "estimated": []},
            }
        elif template_type == "STRUCTURE":
            total = exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0)
            return {
                **base,
                "totalCount": total,
                "leftData": _build_ranking_left_data(exec_record, time_value or str(current_year)),
            }
        elif template_type == "COMPOSITE":
            data_types, left_data = _build_composite_left_data(exec_record, time_value or str(current_year))
            return {
                **base,
                "leftData": left_data,
                "dataTypes": data_types,
            }
        else:
            return {
                **base,
                "leftData": {
                    "actual": {time_value or str(current_year): []},
                    "estimated": {},
                },
            }

    # data_type == "all" 或 None：返回全部数据（兼容现有逻辑）
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
    elif template_type == "STRUCTURE":
        return {
            **base,
            "numerator_count": numerator_count,
            "totalCount": exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0),
            "leftData": _build_ranking_left_data(exec_record, time_value or str(current_year)),
            "timeTrendData": {
                "actual": {"years": x_labels, "data": y_values},
                "estimated": {"years": x_labels, "data": []},
            },
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }
    elif template_type == "STRUCTURE-special":
        return {
            **base,
            "numerator_count": numerator_count,
            "totalCount": exec_record.count if exec_record and exec_record.count is not None else (numerator_count or 0),
            "leftData1": {"actual": [], "estimated": []},
            "leftData2": {"actual": [], "estimated": []},
            "timeTrendData": {
                "actual": {"years": x_labels, "data": y_values},
                "estimated": {"years": x_labels, "data": []},
            },
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }
    elif template_type == "COMPOSITE":
        data_types, left_data = _build_composite_left_data(exec_record, time_value or str(current_year))
        return {
            **base,
            "rate_percent": rate_percent,
            "numerator_count": numerator_count,
            "dataTypes": data_types,
            "leftData": left_data,
            "timeTrendData": {
                "actual": {"years": x_labels, "data": y_values},
                "estimated": {"years": x_labels, "data": []},
            },
            "hospitalComparisonData": {
                "actual": hospital_comparison_actual,
                "estimated": {},
            },
        }
    else:
        return {"indicator_key": indicator_key, "has_data": False}
