"""SQLAlchemy 数据库模型 - 十八项核心制度"""
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Core18Indicator(Base):
    __tablename__ = "core18_indicator"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), default="")
    seq = Column(Integer, default=0)
    scope = Column(Text, default="")
    work_content = Column(Text, default="")
    rule_logic = Column(Text, default="")
    formula = Column(Text, default="")
    description = Column(Text, default="")
    calc_method = Column(String(20), default="none")
    sql_content = Column(Text, default="")
    prompt_content = Column(Text, default="")
    involved_tables = Column(JSON, default=list)
    numerator_desc = Column(Text, default="")
    denominator_desc = Column(Text, default="")
    numerator_sql = Column(Text, default="")
    denominator_sql = Column(Text, default="")
    status = Column(String(20), default="pending")
    is_computable = Column(Boolean, default=True)
    use_llm = Column(Boolean, default=False)
    priority = Column(String(20), default="")
    remark = Column(Text, default="")
    calc_type = Column(String(20), default="ratio")
    date_field = Column(String(20), default="discharge")
    template_type = Column(String(30), nullable=True)
    subitem_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    execution_logs = relationship("Core18ExecutionLog", back_populates="indicator", cascade="all, delete-orphan")


class Core18ExecutionLog(Base):
    __tablename__ = "core18_execution_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(Integer, ForeignKey("core18_indicator.id", ondelete="CASCADE"), nullable=False)
    indicator_name = Column(String(200), default="")
    execution_type = Column(String(20), default="manual")
    run_mode = Column(String(20), default="immediate")
    time_range = Column(String(50), default="全量")
    result_type = Column(String(20), default="ratio")
    calc_method = Column(String(20), default="SQL录入")
    scope = Column(String(50), default="")
    logs = Column(JSON, default=list)
    numerator_sql = Column(Text, default="")
    denominator_sql = Column(Text, default="")
    sql = Column(Text, default="")
    numerator_count = Column(Integer, nullable=True)
    denominator_count = Column(Integer, nullable=True)
    rate_percent = Column(Float, nullable=True)
    rate_formula = Column(String(200), default="")
    result_text = Column(Text, default="")
    preview_data = Column(JSON, default=dict)
    denominator_preview_data = Column(JSON, default=dict)
    error = Column(Text, default="")
    numerator_error = Column(Text, default="")
    denominator_error = Column(Text, default="")
    attempts = Column(JSON, default=list)
    llm_thinking = Column(Text, default="")
    llm_raw = Column(Text, default="")
    cache_hit = Column(Boolean, default=False)
    request_id = Column(String(100), default="")
    conversation_id = Column(String(100), default="")
    status = Column(String(20), default="pending")
    execution_time = Column(DateTime, server_default=func.now())
    duration_seconds = Column(Float, nullable=True)
    subitem_data = Column(JSON, nullable=True)

    indicator = relationship("Core18Indicator", back_populates="execution_logs")
