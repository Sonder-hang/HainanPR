"""监控数据路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import random

from app.database import get_db
from app.models.monitoring import Hospital
from app.schemas.monitoring import HospitalResponse, AlertCategoryResponse

router = APIRouter(tags=["四要素监管"])


def _mock_personnel_violations():
    physicians = [{"Name": "赵伟", "id": "D001"}, {"Name": "王芳", "id": "D002"}, {"Name": "李强", "id": "D003"}]
    types_ = [
        ("unauthorized_prescription", "越权开具特殊级抗生素"),
        ("spatial_trail_anomaly", "25分钟内跨越30公里"),
        ("multi_practice_conflict", "多点执业机构冲突"),
        ("antibiotic_abuse", "抗生素使用不规范"),
    ]
    return [
        {
            "id": i + 1,
            "physician_name": p["Name"],
            "physician_id": p["id"],
            "violation_type": t[0],
            "violation_details": f"{p['Name']}存在{t[1]}的违规行为。",
            "prescription_count": random.randint(1, 50),
            "distance_traveled": round(random.uniform(20, 80), 1),
            "time_window": random.randint(15, 60),
        }
        for i, (p, t) in enumerate([(random.choice(physicians), random.choice(types_)) for _ in range(15)])
    ]


def _mock_institution_anomalies():
    hospitals = ["省立第一医院", "市中心医院", "县人民医院"]
    types_ = [
        ("bed_overflow", "床位溢出", "住院收治超出核定床位"),
        ("registration_overload", "挂号超载", "单日挂号量突破历史最高"),
        ("capacity_exceeded", "收治能力超限", "急诊收治超过承载能力"),
    ]
    return [
        {
            "id": i + 1,
            "anomaly_type": t[0],
            "anomaly_details": f"{h}{t[2]}。",
            "threshold_value": random.randint(500, 1000),
            "actual_value": 0,
            "excess_percent": 0,
        }
        for i, (h, t) in enumerate([(random.choice(hospitals), random.choice(types_)) for _ in range(10)])
    ]


def _mock_technology_warnings():
    hospitals = ["省立第一医院", "市中心医院", "县人民医院"]
    types_ = [
        ("minor_protection", "分级护理强制报告"),
        ("patient_flow", "患者流转监测异常"),
        ("restricted_tech", "限制类技术一致性不符"),
        ("single_disease", "单病种畸变预警"),
        ("minors_protection", "未成年人高风险诊断"),
    ]
    return [
        {
            "id": i + 1,
            "warning_type": t[0],
            "warning_details": f"{h}存在{t[1]}相关问题。",
            "patient_name": f"患者{i+1:03d}",
            "patient_id": f"P{i+1:06d}",
            "risk_level": random.choice(["low", "medium", "high"]),
        }
        for i, (h, t) in enumerate([(random.choice(hospitals), random.choice(types_)) for _ in range(12)])
    ]


def _mock_equipment_anomalies():
    hospitals = ["省立第一医院", "市中心医院", "县人民医院"]
    equipment_list = [("CT", "CT设备阳性率异常"), ("MRI", "核磁共振使用超时"), ("X-Ray", "X光机维护逾期"), ("超声", "超声设备效能低下")]
    types_ = ["positive_rate_abnormal", "overdue_maintenance", "usage_anomaly", "efficiency_low"]
    return [
        {
            "id": i + 1,
            "equipment_name": f"{h}-{eq}",
            "equipment_code": f"EQ{i+1:04d}",
            "anomaly_type": random.choice(types_),
            "anomaly_details": f"{eq}{detail}。",
            "positive_rate": round(random.uniform(85, 99), 2) if "CT" in eq else None,
            "usage_hours": round(random.uniform(1000, 5000), 1),
        }
        for i, (h, (eq, detail)) in enumerate([(random.choice(hospitals), random.choice(equipment_list)) for _ in range(8)])
    ]


@router.get("/personnel/")
def personnel_monitoring():
    violations = _mock_personnel_violations()
    return {
        "total_violations": len(violations),
        "unresolved_violations": len(violations[:10]),
        "violations_by_type": {},
        "recent_violations": violations[:10],
        "physicians_at_risk": [
            {"name": "赵伟", "violations": 5, "level": "high"},
            {"name": "王芳", "violations": 3, "level": "medium"},
            {"name": "李强", "violations": 2, "level": "low"},
        ],
    }


@router.get("/institution/")
def institution_monitoring():
    anomalies = _mock_institution_anomalies()
    return {
        "total_anomalies": len(anomalies),
        "unresolved_anomalies": len(anomalies[:5]),
        "anomalies_by_type": {},
        "hospitals_over_capacity": [
            {"name": "省立第一医院", "type": "床位溢出", "excess": "15%"},
            {"name": "市中心医院", "type": "挂号超载", "excess": "8%"},
        ],
        "recent_anomalies": anomalies[:10],
    }


@router.get("/technology/")
def technology_monitoring():
    warnings = _mock_technology_warnings()
    return {
        "total_warnings": len(warnings),
        "unresolved_warnings": len(warnings[:8]),
        "warnings_by_type": {},
        "high_risk_warnings": [
            {"patient": "患者023", "type": "未成年人高风险诊断", "hospital": "县人民医院"},
            {"patient": "患者089", "type": "限制类技术一致性不符", "hospital": "省立第一医院"},
        ],
        "recent_warnings": warnings[:10],
    }


@router.get("/equipment/")
def equipment_monitoring():
    anomalies = _mock_equipment_anomalies()
    return {
        "total_anomalies": len(anomalies),
        "unresolved_anomalies": len(anomalies[:5]),
        "anomalies_by_type": {},
        "equipment_needing_attention": [
            {"name": "县人民医院-CT", "positive_rate": "95%", "status": "需关注"},
            {"name": "市中心医院-MRI", "usage_hours": "4800h", "status": "接近上限"},
        ],
        "recent_anomalies": anomalies[:10],
    }


@router.get("/alert-categories/", response_model=list[AlertCategoryResponse])
def alert_categories():
    return [
        {"name": "越权开具抗生素", "count": 36, "color": "#dc2626", "route": "/personnel?tab=r1"},
        {"name": "时空轨迹异常", "count": 28, "color": "#7c3aed", "route": "/personnel?tab=r2"},
        {"name": "多点执业冲突", "count": 19, "color": "#2563eb", "route": "/personnel?tab=r3"},
        {"name": "超范围经营", "count": 15, "color": "#ea580c", "route": "/institution?tab=r4"},
        {"name": "收治能力超限", "count": 23, "color": "#9333ea", "route": "/institution?tab=r5"},
    ]


@router.get("/hospitals/", response_model=list[HospitalResponse])
def hospital_list(db: Session = Depends(get_db)):
    return db.query(Hospital).filter(Hospital.is_active == 1).order_by(Hospital.name).all()
