"""Pydantic Schema - 十八项核心制度"""
from pydantic import BaseModel
from typing import Optional, Any


class Core18IndicatorCreate(BaseModel):
    name: str
    category: str = ""
    seq: int = 0
    scope: str = ""
    work_content: str = ""
    rule_logic: str = ""
    formula: str = ""
    description: str = ""
    calc_method: str = "none"
    sql_content: str = ""
    prompt_content: str = ""
    involved_tables: list = []
    numerator_desc: str = ""
    denominator_desc: str = ""
    numerator_sql: str = ""
    denominator_sql: str = ""
    status: str = "pending"
    is_computable: bool = True
    use_llm: bool = False
    priority: str = ""
    remark: str = ""


class Core18IndicatorUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    seq: Optional[int] = None
    scope: Optional[str] = None
    work_content: Optional[str] = None
    rule_logic: Optional[str] = None
    formula: Optional[str] = None
    description: Optional[str] = None
    calc_method: Optional[str] = None
    sql_content: Optional[str] = None
    involved_tables: Optional[list] = None
    numerator_desc: Optional[str] = None
    denominator_desc: Optional[str] = None
    numerator_sql: Optional[str] = None
    denominator_sql: Optional[str] = None
    status: Optional[str] = None
    is_computable: Optional[bool] = None
    priority: Optional[str] = None
    remark: Optional[str] = None


class Core18IndicatorResponse(BaseModel):
    id: int
    name: str
    category: str = ""
    seq: int = 0
    scope: str = ""
    work_content: str = ""
    rule_logic: str = ""
    formula: str = ""
    description: str = ""
    calc_method: str = "none"
    sql_content: str = ""
    prompt_content: str = ""
    involved_tables: list = []
    numerator_desc: str = ""
    denominator_desc: str = ""
    numerator_sql: str = ""
    denominator_sql: str = ""
    status: str = "pending"
    is_computable: bool = True
    use_llm: bool = False
    priority: str = ""
    remark: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class Core18ExecutionLogResponse(BaseModel):
    id: int
    indicator_id: int
    indicator_name: Optional[str] = None
    execution_type: str = "manual"
    run_mode: str = "immediate"
    time_range: str = "全量"
    result_type: str = "ratio"
    calc_method: str = "SQL录入"
    scope: str = ""
    logs: list = []
    numerator_sql: str = ""
    denominator_sql: str = ""
    sql: str = ""
    numerator_count: Optional[int] = None
    denominator_count: Optional[int] = None
    rate_percent: Optional[float] = None
    rate_formula: str = ""
    result_text: str = ""
    preview_data: dict = {}
    denominator_preview_data: dict = {}
    error: str = ""
    numerator_error: str = ""
    denominator_error: str = ""
    attempts: list = []
    llm_thinking: str = ""
    llm_raw: str = ""
    cache_hit: bool = False
    request_id: str = ""
    conversation_id: str = ""
    status: str = "pending"
    execution_time: Optional[str] = None
    duration_seconds: Optional[float] = None

    class Config:
        from_attributes = True
