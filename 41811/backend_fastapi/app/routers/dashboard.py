"""仪表盘路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.indicator import Indicator, IndicatorExecution

router = APIRouter(tags=["仪表盘"])


def _build_execution_alerts(db: Session):
    """
    从四要素执行记录构造预警列表。
    每条成功的执行记录生成一条预警，按 execution_time 降序排列。
    """
    # 查询最近 30 天内有成功执行记录的指标
    since = datetime.now() - timedelta(days=30)
    execs = (
        db.query(IndicatorExecution)
        .join(Indicator, Indicator.id == IndicatorExecution.indicator_id)
        .filter(
            IndicatorExecution.kind == "four",
            IndicatorExecution.status == "success",
            IndicatorExecution.execution_time >= since,
        )
        .order_by(IndicatorExecution.execution_time.desc())
        .limit(50)
        .all()
    )

    cat_to_key = {
        "人员要素": "personnel",
        "机构要素": "institution",
        "技术要素": "technology",
        "设备要素": "equipment",
    }
    alerts = []
    for e in execs:
        factor_key = cat_to_key.get(e.indicator.category, "technology") if e.indicator else "technology"
        indicator_name = e.indicator.name if e.indicator else e.indicator_name
        count = e.numerator_count
        msg = f"【{e.indicator.category}】{indicator_name}，执行结果：{count} 条" if count is not None else f"【{e.indicator.category}】{indicator_name}，执行完成"
        alerts.append({
            "id": e.id,
            "time": e.execution_time.isoformat() if e.execution_time else datetime.now().isoformat(),
            "factor": factor_key,
            "level": "high" if count and count > 0 else "warning",
            "message": msg,
            "hospital": "",
            "department": "",
            "patient_id": "",
            "handled": 0,
            "handled_by": "",
            "handled_time": None,
            "handler_comment": "",
        })
    return alerts


def _execution_stats(db: Session, time_mode: str = None, time_value: str = None, hospital_code: str = None):
    """
    按要素分类统计四要素执行记录的 numerator_count 总和（成功的记录）。
    支持时间筛选（按月/季度）和医院筛选。
    同时返回每个要素的 top 3 指标。
    """
    cat_to_key = {
        "人员要素": "personnel",
        "机构要素": "institution",
        "技术要素": "technology",
        "设备要素": "equipment",
    }
    stats = {"personnel": 0, "institution": 0, "technology": 0, "equipment": 0}
    # 存储每个要素的指标数据：key -> [(name, count), ...]
    top_indicators = {"personnel": [], "institution": [], "technology": [], "equipment": []}

    query = (
        db.query(IndicatorExecution)
        .join(Indicator, Indicator.id == IndicatorExecution.indicator_id)
        .filter(
            IndicatorExecution.kind == "four",
            IndicatorExecution.status == "success",
            IndicatorExecution.numerator_count.isnot(None),
        )
    )

    # 时间筛选
    if time_mode == "monthly" and time_value:
        query = query.filter(
            IndicatorExecution.run_mode == "monthly",
            IndicatorExecution.time_value == time_value,
        )
    elif time_mode == "quarterly" and time_value:
        query = query.filter(
            IndicatorExecution.run_mode == "quarterly",
            IndicatorExecution.time_value == time_value,
        )
    else:
        # 全量模式：只取 run_mode 为空或 immediate 的记录（即全量执行结果）
        query = query.filter(
            (IndicatorExecution.run_mode == None) | (IndicatorExecution.run_mode == "immediate")
        )

    # 医院筛选
    if hospital_code and hospital_code != "all":
        query = query.filter(IndicatorExecution.group_by_hospital == True)

    execs = query.order_by(IndicatorExecution.execution_time.desc()).all()

    # 每个指标只取最新一条，同时收集 top 指标
    seen = {}
    for e in execs:
        if e.indicator_id in seen:
            continue
        seen[e.indicator_id] = e
        if e.indicator and e.indicator.category in cat_to_key:
            key = cat_to_key[e.indicator.category]
            count = e.numerator_count or 0
            stats[key] += count
            # 收集指标名称和数量
            name = e.indicator.name if e.indicator else e.indicator_name
            top_indicators[key].append({"name": name, "count": count})

    # 对每个要素的指标按数量降序排序，取前3个
    for key in top_indicators:
        top_indicators[key] = sorted(top_indicators[key], key=lambda x: x["count"], reverse=True)[:3]

    return {
        "stats": stats,
        "top_indicators": top_indicators,
    }


@router.get("/overview/")
def dashboard_overview(
    time_mode: str = None,
    time_value: str = None,
    hospital_code: str = None,
    db: Session = Depends(get_db)
):
    result = _execution_stats(db, time_mode, time_value, hospital_code)
    stats = result["stats"]
    top_indicators = result["top_indicators"]

    personnel = stats.get("personnel", 0)
    institution = stats.get("institution", 0)
    technology = stats.get("technology", 0)
    equipment = stats.get("equipment", 0)
    total = personnel + institution + technology + equipment

    # alert_categories: 按指标维度聚合最新执行结果
    cat_to_key = {
        "人员要素": "personnel",
        "机构要素": "institution",
        "技术要素": "technology",
        "设备要素": "equipment",
    }

    query = (
        db.query(IndicatorExecution)
        .join(Indicator, Indicator.id == IndicatorExecution.indicator_id)
        .filter(
            IndicatorExecution.kind == "four",
            IndicatorExecution.status == "success",
        )
    )

    # 时间筛选
    if time_mode == "monthly" and time_value:
        query = query.filter(
            IndicatorExecution.run_mode == "monthly",
            IndicatorExecution.time_value == time_value,
        )
    elif time_mode == "quarterly" and time_value:
        query = query.filter(
            IndicatorExecution.run_mode == "quarterly",
            IndicatorExecution.time_value == time_value,
        )
    else:
        query = query.filter(
            (IndicatorExecution.run_mode == None) | (IndicatorExecution.run_mode == "immediate")
        )

    # 医院筛选
    if hospital_code and hospital_code != "all":
        query = query.filter(IndicatorExecution.group_by_hospital == True)

    recent = query.order_by(IndicatorExecution.execution_time.desc()).all()

    # 每个指标的最近一条成功记录
    seen_indicators = set()
    alert_categories = []
    for e in recent:
        if e.indicator_id in seen_indicators:
            continue
        seen_indicators.add(e.indicator_id)
        name = e.indicator.name if e.indicator else e.indicator_name
        color_map = {
            "人员要素": "#dc2626",
            "机构要素": "#7c3aed",
            "技术要素": "#ea580c",
            "设备要素": "#9333ea",
        }
        alert_categories.append({
            "name": name,
            "count": e.numerator_count or 0,
            "color": color_map.get(e.indicator.category, "#6b7280") if e.indicator else "#6b7280",
            "route": _category_route(e.indicator.category) if e.indicator else "/technology",
        })

    return {
        "personnel_alerts": personnel,
        "institution_alerts": institution,
        "technology_alerts": technology,
        "equipment_alerts": equipment,
        "recent_alerts": [],
        "alert_categories": alert_categories[:10],
        "factor_distribution": [
            {"name": "人员要素", "count": personnel, "color": "#0A6EFD", "percent": int(personnel / max(1, total) * 100), "route": "/personnel"},
            {"name": "机构要素", "count": institution, "color": "#7c3aed", "percent": int(institution / max(1, total) * 100), "route": "/institution"},
            {"name": "技术要素", "count": technology, "color": "#dc2626", "percent": int(technology / max(1, total) * 100), "route": "/technology"},
            {"name": "设备要素", "count": equipment, "color": "#ea580c", "percent": int(equipment / max(1, total) * 100), "route": "/equipment"},
        ],
        # 每个要素的 top 3 指标
        "top_indicators": {
            "personnel": top_indicators.get("personnel", []),
            "institution": top_indicators.get("institution", []),
            "technology": top_indicators.get("technology", []),
            "equipment": top_indicators.get("equipment", []),
        },
    }


def _category_route(category: str) -> str:
    routes = {
        "人员要素": "/personnel",
        "机构要素": "/institution",
        "技术要素": "/technology",
        "设备要素": "/equipment",
    }
    return routes.get(category, "/technology")


@router.get("/stats/")
def dashboard_stats(db: Session = Depends(get_db)):
    # 过去 30 天每日统计
    stats = _execution_stats(db)
    today = datetime.now().date()
    return [
        {
            "date": str(today - timedelta(days=i)),
            "personnel_alerts": stats.get("personnel", 0),
            "institution_alerts": stats.get("institution", 0),
            "technology_alerts": stats.get("technology", 0),
            "equipment_alerts": stats.get("equipment", 0),
            "total_alerts": sum(stats.values()),
            "high_risk_count": 0,
        }
        for i in range(30)
    ]


@router.get("/alerts/")
def alert_list(level: str = None, factor: str = None, handled: bool = None, db: Session = Depends(get_db)):
    alerts = _build_execution_alerts(db)
    if level:
        alerts = [a for a in alerts if a["level"] == level]
    if factor:
        alerts = [a for a in alerts if a["factor"] == factor]
    if handled is not None:
        alerts = [a for a in alerts if bool(a["handled"]) == handled]
    return alerts


@router.get("/factor-distribution/")
def factor_distribution(db: Session = Depends(get_db)):
    stats = _execution_stats(db)
    total = sum(stats.values())
    factors = [
        ("personnel", "人员要素", "#0A6EFD", "/personnel"),
        ("institution", "机构要素", "#7c3aed", "/institution"),
        ("technology", "技术要素", "#dc2626", "/technology"),
        ("equipment", "设备要素", "#ea580c", "/equipment"),
    ]
    result = []
    for key, name, color, route in factors:
        count = stats.get(key, 0)
        result.append({"name": name, "count": count, "color": color, "percent": int(count / max(1, total) * 100), "route": route})
    result.sort(key=lambda x: x["count"], reverse=True)
    return result
