"""SQLAlchemy 数据库模型 - 医院准入标准"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Date, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class HospitalAdmissionStandard(Base):
    __tablename__ = "hospital_admission_standard"

    id = Column(Integer, primary_key=True, autoincrement=True)
    standard_code = Column(String(100), unique=True, nullable=False)
    standard_name = Column(String(300), nullable=False)
    category = Column(String(100), default="")
    level = Column(String(20), default="")
    requirement = Column(Text, default="")
    documents_needed = Column(JSON, default=list)
    check_items = Column(JSON, default=list)
    pass_threshold = Column(String(200), default="")
    status = Column(String(20), default="pending")
    approved_hospital_id = Column(String(50), nullable=True)
    approved_hospital_name = Column(String(200), default="")
    approved_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    license_no = Column(String(100), default="")
    license_front_image = Column(String(500), default="")
    license_back_image = Column(String(500), default="")
    other_images = Column(JSON, default=list)
    remark = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
