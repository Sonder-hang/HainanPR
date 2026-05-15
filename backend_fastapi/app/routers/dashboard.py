"""仪表盘路由"""
from fastapi import APIRouter
import random
from datetime import datetime, timedelta

router = APIRouter(tags=["仪表盘"])


def _mock_alerts():
    factors = ["personnel", "institution", "technology", "equipment"]
    levels = ["high", "warning"]
    messages = [
        "【人员要素】赵伟医师25分钟内跨越30公里产生门诊处方记录。",
        "【人员要素】越权开具特殊级抗生素（美罗培南）预警。",
        "【机构要素】省立第一医院单日住院收治人数超出核定床位数。",
        "【技术要素】县人民医院疑似侵害未成年人高风险诊断线索。",
        "【设备要素】某县人民医院CT设备阳性率异常，高达95%。",
        "【人员要素】王芳医师跨多点执业机构开具处方异常。",
        "【机构要素】某医院门诊挂号量单日突破历史最高记录。",
        "【技术要素】未经审批开展三类医疗技术预警。",
        "【设备要素】某医院呼吸机使用时长超设计寿命预警。",
    ]
    alerts = []
    now = datetime.now()
    for i in range(20):
        alerts.append({
            "id": i + 1,
            "time": (now - timedelta(hours=i * random.randint(1, 3))).isoformat(),
            "factor": random.choice(factors),
            "level": random.choice(levels),
            "message": random.choice(messages),
            "hospital": "省立第一医院" if i % 3 == 0 else "县人民医院",
            "department": "",
            "patient_id": "",
            "handled": random.choice([0, 0, 1]),
            "handled_by": "",
            "handled_time": None,
            "handler_comment": "",
        })
    return alerts


@router.get("/overview/")
def dashboard_overview():
    alerts = _mock_alerts()
    personnel = len([a for a in alerts if a["factor"] == "personnel" and not a["handled"]])
    institution = len([a for a in alerts if a["factor"] == "institution" and not a["handled"]])
    technology = len([a for a in alerts if a["factor"] == "technology" and not a["handled"]])
    equipment = len([a for a in alerts if a["factor"] == "equipment" and not a["handled"]])
    total = len(alerts)
    return {
        "personnel_alerts": personnel,
        "institution_alerts": institution,
        "technology_alerts": technology,
        "equipment_alerts": equipment,
        "recent_alerts": alerts[:10],
        "alert_categories": [
            {"name": "越权开具抗生素", "count": 36, "color": "#dc2626", "route": "/personnel?tab=r1"},
            {"name": "时空轨迹异常", "count": 28, "color": "#7c3aed", "route": "/personnel?tab=r2"},
            {"name": "多点执业冲突", "count": 19, "color": "#2563eb", "route": "/personnel?tab=r3"},
            {"name": "超范围经营", "count": 15, "color": "#ea580c", "route": "/institution?tab=r4"},
            {"name": "收治能力超限", "count": 23, "color": "#9333ea", "route": "/institution?tab=r5"},
        ],
        "factor_distribution": [
            {"name": "人员要素", "count": personnel, "color": "#0A6EFD", "percent": int(personnel / max(1, total) * 100), "route": "/personnel"},
            {"name": "机构要素", "count": institution, "color": "#7c3aed", "percent": int(institution / max(1, total) * 100), "route": "/institution"},
            {"name": "技术要素", "count": technology, "color": "#dc2626", "percent": int(technology / max(1, total) * 100), "route": "/technology"},
            {"name": "设备要素", "count": equipment, "color": "#ea580c", "percent": int(equipment / max(1, total) * 100), "route": "/equipment"},
        ],
    }


@router.get("/stats/")
def dashboard_stats():
    today = datetime.now().date()
    return [
        {
            "id": i + 1,
            "date": str(today - timedelta(days=i)),
            "personnel_alerts": random.randint(20, 50),
            "institution_alerts": random.randint(10, 30),
            "technology_alerts": random.randint(40, 80),
            "equipment_alerts": random.randint(15, 40),
            "total_alerts": random.randint(85, 200),
            "high_risk_count": random.randint(5, 20),
        }
        for i in range(30)
    ]


@router.get("/alerts/")
def alert_list(level: str = None, factor: str = None, handled: bool = None):
    alerts = _mock_alerts()
    if level:
        alerts = [a for a in alerts if a["level"] == level]
    if factor:
        alerts = [a for a in alerts if a["factor"] == factor]
    if handled is not None:
        alerts = [a for a in alerts if bool(a["handled"]) == handled]
    return alerts


@router.get("/factor-distribution/")
def factor_distribution():
    alerts = _mock_alerts()
    total = len(alerts)
    factors = [
        ("personnel", "人员要素", "#0A6EFD", "/personnel"),
        ("institution", "机构要素", "#7c3aed", "/institution"),
        ("technology", "技术要素", "#dc2626", "/technology"),
        ("equipment", "设备要素", "#ea580c", "/equipment"),
    ]
    result = []
    for key, name, color, route in factors:
        count = len([a for a in alerts if a["factor"] == key])
        result.append({"name": name, "count": count, "color": color, "percent": int(count / max(1, total) * 100), "route": route})
    result.sort(key=lambda x: x["count"], reverse=True)
    return result
