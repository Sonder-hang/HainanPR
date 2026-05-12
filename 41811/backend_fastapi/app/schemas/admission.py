"""Pydantic Schema - 医院准入标准"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime as dt


class AdmissionStandardBase(BaseModel):
    standard_code: str
    standard_name: str
    category: str = ""
    level: str = ""
    requirement: str = ""
    documents_needed: list = []
    check_items: list = []
    pass_threshold: str = ""
    status: str = "pending"
    approved_hospital_id: Optional[str] = None
    approved_hospital_name: str = ""
    approved_date: Optional[date] = None
    expiry_date: Optional[date] = None
    license_no: str = ""
    license_front_image: str = ""
    license_back_image: str = ""
    other_images: list = []
    remark: str = ""


class AdmissionStandardCreate(AdmissionStandardBase):
    pass


class AdmissionStandardUpdate(BaseModel):
    standard_code: Optional[str] = None
    standard_name: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    requirement: Optional[str] = None
    documents_needed: Optional[list] = None
    check_items: Optional[list] = None
    pass_threshold: Optional[str] = None
    status: Optional[str] = None
    approved_hospital_id: Optional[str] = None
    approved_hospital_name: Optional[str] = None
    approved_date: Optional[date] = None
    expiry_date: Optional[date] = None
    license_no: Optional[str] = None
    license_front_image: Optional[str] = None
    license_back_image: Optional[str] = None
    other_images: Optional[list] = None
    remark: Optional[str] = None


class AdmissionStandardResponse(AdmissionStandardBase):
    id: int
    created_at: Optional[dt] = None
    updated_at: Optional[dt] = None

    model_config = {"from_attributes": True}
