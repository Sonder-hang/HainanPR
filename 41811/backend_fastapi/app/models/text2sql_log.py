"""SQLAlchemy 数据库模型 - Text2SQL 日志"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.database import Base


class Text2SQLLog(Base):
    __tablename__ = "text2sql_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    user_question = Column(Text, default="")
    generated_sql = Column(Text, default="")
    sql_valid = Column(Boolean, default=False)
    sql_error = Column(Text, default="")
    execution_time = Column(DateTime, server_default=func.now())
    duration_ms = Column(Integer, nullable=True)
    selected_tables = Column(JSON, default=list)
    llm_model = Column(String(100), default="")
    request_id = Column(String(100), default="")
    session_id = Column(String(100), default="")
    status = Column(String(20), default="pending")
    result_preview = Column(JSON, default=dict)
    result_count = Column(Integer, nullable=True)
    indicator_name = Column(String(200), default="")
    indicator_type = Column(String(50), default="")
