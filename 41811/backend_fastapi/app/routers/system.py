"""系统配置路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.monitoring import Hospital
from app.services.text2sql import Text2SQLService

router = APIRouter(tags=["系统配置"])


@router.get("/health/")
def health_check():
    service = Text2SQLService()
    backend_health = service.health_check()
    return {
        "ok": True,
        "service": "FastAPI Backend",
        "version": "1.0.0",
        "backend_health": backend_health,
    }


@router.get("/config/")
def system_config():
    return {
        "indicator_types": [
            {"value": "four", "label": "四要素监管指标"},
            {"value": "core18", "label": "十八项核心制度指标"},
        ],
        "calc_methods": [
            {"value": "none", "label": "无"},
            {"value": "textToSql", "label": "Text-to-SQL"},
            {"value": "sql", "label": "SQL录入"},
            {"value": "prompt", "label": "Prompt"},
        ],
        "factor_types": [
            {"value": "personnel", "label": "人员要素"},
            {"value": "institution", "label": "机构要素"},
            {"value": "technology", "label": "技术要素"},
            {"value": "equipment", "label": "设备要素"},
        ],
    }


@router.get("/hospitals/")
def hospital_list(db: Session = Depends(get_db)):
    """获取医疗机构列表（从本地 hospital 表）"""
    from app.models.monitoring import Hospital
    hospitals = db.query(Hospital).filter(Hospital.is_active == 1).order_by(Hospital.name).all()
    return [{"value": h.id, "label": h.name, "level": h.level, "type": h.hospital_type, "hospital_code": h.hospital_code} for h in hospitals]


@router.post("/refresh-tables/")
def refresh_tables():
    service = Text2SQLService()
    return service.refresh_tables()
