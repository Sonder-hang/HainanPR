"""Pydantic Schema - 监控数据"""
from pydantic import BaseModel
from typing import Optional


class HospitalResponse(BaseModel):
    id: str
    hospital_code: Optional[str] = None
    name: str
    level: str = ""
    hospital_type: str = ""
    region: str = ""
    address: str = ""
    contact: str = ""
    bed_count: int = 0
    is_active: int = 1

    class Config:
        from_attributes = True


class AlertCategoryResponse(BaseModel):
    name: str
    count: int
    color: str = ""
    route: str = ""
