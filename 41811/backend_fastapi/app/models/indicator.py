"""SQLAlchemy 数据库模型 - 指标管理"""
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Indicator(Base):
    __tablename__ = "indicator"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    indicator_type = Column(String(20), default="four")
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
    platform_data_ready = Column(Boolean, default=False)
    priority = Column(String(20), default="")
    remark = Column(Text, default="")
    regex_match = Column(Boolean, default=False)
    regex_rule = Column(Text, default="")
    calc_type = Column(String(20), default="ratio")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    executions = relationship("IndicatorExecution", back_populates="indicator", cascade="all, delete-orphan")


class IndicatorExecution(Base):
    __tablename__ = "indicator_execution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(Integer, ForeignKey("indicator.id", ondelete="CASCADE"), nullable=False)
    indicator_name = Column(String(200), default="")  # 冗余存储，防止指标被删除后名称丢失
    execution_type = Column(String(20), default="manual")
    kind = Column(String(20), default="core18")          # four | core18
    run_mode = Column(String(20), default="immediate")    # immediate | monthly | quarterly
    time_range = Column(String(50), default="全量")       # 时间范围描述
    result_type = Column(String(20), default="ratio")    # ratio | count
    calc_method = Column(String(20), default="SQL录入")  # SQL录入 | 大模型Prompt
    scope = Column(String(50), default="")               # 执行范围：全省 | hospital_a | hospital_b | hospital_c
    logs = Column(JSON, default=list)                    # 执行日志
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

    indicator = relationship("Indicator", back_populates="executions")


class TableMetadata(Base):
    __tablename__ = "table_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), unique=True, nullable=False)
    business_definition = Column(Text, default="")
    data_granularity = Column(Text, default="")
    remarks = Column(Text, default="")
    field_count = Column(Integer, default=0)
    formatted_text = Column(Text, default="")
    last_synced = Column(DateTime, server_default=func.now())
    source = Column(String(50), default="text2sql")

    columns = relationship("ColumnMetadata", back_populates="table", cascade="all, delete-orphan")


class ColumnMetadata(Base):
    __tablename__ = "column_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("table_metadata.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    data_type = Column(String(50), default="")
    meaning_cn = Column(String(500), default="")
    field_constraint = Column(Text, default="")

    table = relationship("TableMetadata", back_populates="columns")
