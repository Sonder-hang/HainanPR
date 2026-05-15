"""SQLAlchemy 数据库模型 - 四要素监控记录"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Hospital(Base):
    __tablename__ = "hospital"

    id = Column(String(50), primary_key=True)
    hospital_code = Column(String(50), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    level = Column(String(20), default="")
    hospital_type = Column(String(20), default="")
    region = Column(String(100), default="")
    address = Column(String(300), default="")
    contact = Column(String(50), default="")
    bed_count = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())


class FourElementsMonitoringRecord(Base):
    __tablename__ = "four_elements_monitoring_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(String(50), nullable=True)
    factor = Column(String(20), nullable=False)
    record_type = Column(String(100), default="")
    title = Column(String(200), default="")
    description = Column(Text, default="")
    severity = Column(String(20), default="medium")
    status = Column(String(20), default="pending")
    alert_time = Column(DateTime, server_default=func.now())
    resolved_time = Column(DateTime, nullable=True)
    handler = Column(String(100), default="")
    handler_comment = Column(Text, default="")
    related_indicator_id = Column(Integer, nullable=True)
    extra_data = Column(JSON, default=dict)


class PersonnelViolation(Base):
    __tablename__ = "personnel_violation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("four_elements_monitoring_record.id", ondelete="CASCADE"), nullable=False)
    physician_name = Column(String(100), default="")
    physician_id = Column(String(50), default="")
    violation_type = Column(String(50), default="")
    violation_details = Column(Text, default="")
    prescription_count = Column(Integer, default=0)
    distance_traveled = Column(Float, default=0)
    time_window = Column(Integer, default=0)


class InstitutionAnomaly(Base):
    __tablename__ = "institution_anomaly"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("four_elements_monitoring_record.id", ondelete="CASCADE"), nullable=False)
    anomaly_type = Column(String(50), default="")
    anomaly_details = Column(Text, default="")
    threshold_value = Column(Integer, default=0)
    actual_value = Column(Integer, default=0)
    excess_percent = Column(Float, default=0)


class TechnologyWarning(Base):
    __tablename__ = "technology_warning"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("four_elements_monitoring_record.id", ondelete="CASCADE"), nullable=False)
    warning_type = Column(String(50), default="")
    warning_details = Column(Text, default="")
    patient_name = Column(String(100), default="")
    patient_id = Column(String(50), default="")
    risk_level = Column(String(20), default="medium")


class EquipmentAnomaly(Base):
    __tablename__ = "equipment_anomaly"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("four_elements_monitoring_record.id", ondelete="CASCADE"), nullable=False)
    equipment_name = Column(String(200), default="")
    equipment_code = Column(String(50), default="")
    anomaly_type = Column(String(50), default="")
    anomaly_details = Column(Text, default="")
    positive_rate = Column(Float, nullable=True)
    usage_hours = Column(Float, default=0)
