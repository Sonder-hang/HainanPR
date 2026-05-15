"""SQLAlchemy 数据库模型 - 仪表盘"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class DashboardAlert(Base):
    __tablename__ = "dashboard_alert"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, server_default=func.now())
    factor = Column(String(20), nullable=False)
    level = Column(String(20), default="warning")
    message = Column(Text, default="")
    hospital = Column(String(200), default="")
    department = Column(String(100), default="")
    patient_id = Column(String(100), default="")
    handled = Column(Integer, default=0)
    handled_by = Column(String(100), default="")
    handled_time = Column(DateTime, nullable=True)
    handler_comment = Column(Text, default="")


class DashboardStatistics(Base):
    __tablename__ = "dashboard_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, unique=True)
    personnel_alerts = Column(Integer, default=0)
    institution_alerts = Column(Integer, default=0)
    technology_alerts = Column(Integer, default=0)
    equipment_alerts = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
