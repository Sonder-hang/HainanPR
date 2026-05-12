"""Pydantic Schema - Text2SQL 日志"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime as dt


class Text2SQLLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_question: str = ""
    generated_sql: str = ""
    sql_valid: bool = False
    sql_error: str = ""
    execution_time: Optional[dt] = None
    duration_ms: Optional[int] = None
    selected_tables: list = []
    llm_model: str = ""
    request_id: str = ""
    session_id: str = ""
    status: str = "pending"
    result_preview: dict = {}
    result_count: Optional[int] = None
    indicator_name: str = ""
    indicator_type: str = ""

    model_config = {"from_attributes": True}
