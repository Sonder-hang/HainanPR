"""Pydantic Schema - 指标管理"""
from pydantic import BaseModel, Field, model_serializer
from datetime import datetime as dt
from typing import Optional, Union


class IndicatorBase(BaseModel):
    name: str
    indicator_type: str = "four"
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
    platform_data_ready: bool = False
    priority: str = ""
    remark: str = ""
    regex_match: bool = False
    regex_rule: str = ""
    calc_type: str = "ratio"
    date_field: str = "discharge"  # discharge=出院时间, admission=入院时间


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorUpdate(BaseModel):
    name: Optional[str] = None
    indicator_type: Optional[str] = None
    category: Optional[str] = None
    seq: Optional[int] = None
    scope: Optional[str] = None
    work_content: Optional[str] = None
    rule_logic: Optional[str] = None
    formula: Optional[str] = None
    description: Optional[str] = None
    calc_method: Optional[str] = None
    sql_content: Optional[str] = None
    prompt_content: Optional[str] = None
    involved_tables: Optional[list] = None
    numerator_desc: Optional[str] = None
    denominator_desc: Optional[str] = None
    numerator_sql: Optional[str] = None
    denominator_sql: Optional[str] = None
    status: Optional[str] = None
    is_computable: Optional[bool] = None
    use_llm: Optional[bool] = None
    priority: Optional[str] = None
    remark: Optional[str] = None
    calc_type: Optional[str] = None
    date_field: Optional[str] = None  # discharge=出院时间, admission=入院时间, visit=就诊时间


class IndicatorResponse(IndicatorBase):
    id: int
    created_at: Optional[dt] = None
    updated_at: Optional[dt] = None

    model_config = {"from_attributes": True}


class IndicatorExecutionResponse(BaseModel):
    id: int
    indicator_id: int
    indicator_name: Optional[str] = ""
    execution_type: str = "manual"
    kind: str = "core18"
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
    count: Optional[int] = None  # 计数型指标的总数量
    rate_percent: Optional[float] = None
    rate_formula: str = ""
    result_text: str = ""
    preview_data: dict = {}
    denominator_preview_data: dict = {}
    error: str = ""
    attempts: list = []
    llm_thinking: str = ""
    llm_raw: str = ""
    cache_hit: bool = False
    request_id: str = ""
    conversation_id: str = ""
    status: str = "pending"
    execution_time: Optional[dt] = None
    duration_seconds: Optional[float] = None
    # 批量执行相关字段
    hospital_codes: Optional[list] = None  # 执行时选中的医院代码
    time_mode: Optional[str] = None  # monthly=月度, quarterly=季度
    time_value: Optional[str] = None  # 如 "2026-04" 或 "2026-Q1"
    date_field: Optional[str] = None  # discharge=出院时间, admission=入院时间, visit=就诊时间
    group_by_hospital: Optional[bool] = False  # 是否按医院分组执行
    hospital_results: Optional[list] = []  # 各医院执行结果列表

    model_config = {"from_attributes": True}


class PreviewPageRequest(BaseModel):
    execution_id: Union[int, str] = Field(description="执行记录 ID（数据库整数 ID 或前端临时字符串 ID）")
    target: str = "numerator"  # "numerator" | "denominator"
    page: int = 1
    page_size: int = 50


class PreviewPageResponse(BaseModel):
    ok: bool = True
    error: Optional[str] = None
    columns: list = []
    rows: list = []


class ExecuteRequest(BaseModel):
    business_type: Optional[str] = None
    calc_type: Optional[str] = None
    indicator_id: Optional[int] = None
    indicator_index: Optional[int] = None
    indicator_type: Optional[str] = None
    indicator_name: Optional[str] = None
    selected_tables: Optional[list[str]] = None
    indicator_formula: Optional[str] = ""
    supplement_info: Optional[str] = ""
    numerator_desc: Optional[str] = ""
    denominator_desc: Optional[str] = ""
    indicator_desc: Optional[str] = ""
    custom_system_prompt: Optional[str] = ""
    custom_user_message: Optional[str] = ""
    regenerate: Optional[dict] = None
    mode: Optional[str] = ""
    prompt_modified: bool = False
    conversation_id: Optional[str] = ""
    conversation_history: Optional[list] = None
    # 新增：执行记录持久化字段
    kind: Optional[str] = "core18"
    run_mode: Optional[str] = "immediate"
    time_range: Optional[str] = "全量"
    result_type: Optional[str] = "ratio"
    calc_method: Optional[str] = "SQL录入"
    scope: Optional[str] = ""
    logs: Optional[list] = None
    # 批量执行相关字段
    hospital_codes: Optional[list[str]] = None  # 选中的医院代码列表
    time_mode: Optional[str] = None  # monthly=月度, quarterly=季度
    time_value: Optional[str] = None  # 如 "2026-04" 或 "2026-Q1"
    date_field: Optional[str] = "discharge"  # discharge=出院时间(DSCG_DT_TM), admission=入院时间(ADMN_DT_TM)
    group_by_hospital: Optional[bool] = True  # 是否按医院分组执行


class ExecutionHistoryResponse(BaseModel):
    records: list[IndicatorExecutionResponse]
    total: int

    model_config = {"from_attributes": True}


class TestSqlRequest(BaseModel):
    sql: str
    limit: int = 200


class TestSqlResponse(BaseModel):
    ok: bool
    columns: list = []
    rows: list = []
    count: Optional[int] = None
    error: Optional[str] = None
    count_error: Optional[str] = None