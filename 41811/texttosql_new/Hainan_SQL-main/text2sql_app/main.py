"""Text-to-SQL 演示后端：支持三种指标类型，含新增指标、Prompt 预览、SQL 测试。"""
import json
import subprocess
import sys
import time
import traceback
import uuid
from datetime import date, datetime, timezone
from datetime import time as time_cls
from decimal import Decimal
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import RedirectResponse

from config import (
    EXTRACT_TABLES_SCRIPT,
    PREVIEW_ROW_LIMIT,
    ROOT,
    SQL_CACHE_ENABLED,
    SQL_RETRY_MAX,
    SQL_RETRY_MAX_DUAL,
    STATIC_DIR,
)
from llm_client import (
    chat_completion_dual_sql,
    chat_completion_multiturn,
    get_model_name,
    iter_stream_completion_chunks,
    iter_stream_multiturn_chunks,
    merged_stream_parse_dual_sql,
    merged_stream_parse_single_sql,
    merged_stream_parse_analysis,
    parse_dual_sql_json,
    parse_single_sql_json,
    parse_analysis_json,
)
from logging_utils import (
    delete_logs_by_request_id,
    group_logs_for_api,
    log_event,
    log_llm_dual,
    log_llm_dual_pending,
    log_llm_round,
)
from prompt_builder import (
    SYSTEM_PROMPT_DUAL,
    SYSTEM_PROMPT_STAT,
    SYSTEM_PROMPT_ANALYSIS,
    append_prompt_log_entry,
    build_dual_retry_suffix,
    build_prompt_preview,
    build_regenerate_from_request,
    build_stat_regenerate_from_request,
    build_stat_retry_suffix,
    build_analysis_retry_suffix,
    filter_tables_for_prompt,
    format_schema_block,
    get_all_table_names_with_comments,
    get_indicator_type,
    load_indicators,
    load_prompt_log,
    load_tables_catalog,
    merge_indicator_prompt_fields,
    save_indicators,
    user_message_dual,
    user_message_stat,
    user_message_analysis,
)
from sql_cache import get_sql_pair, invalidate, make_cache_key, set_sql_pair
from sql_runner import execute_count, execute_counts_parallel, execute_limited, execute_limited_parallel

app = FastAPI(title="Text-to-SQL Hainan", version="0.2.0")


@app.middleware("http")
async def redirect_when_host_is_zero(request: Request, call_next):
    hn = (request.url.hostname or "").strip("[]")
    if hn in ("0.0.0.0", "::ffff:0.0.0.0"):
        fixed = request.url.replace(hostname="127.0.0.1")
        return RedirectResponse(str(fixed), status_code=307)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================== 请求模型 ==========================

class RegenerateContext(BaseModel):
    previous_numerator_sql: Optional[str] = None
    previous_denominator_sql: Optional[str] = None
    numerator_error: Optional[str] = None
    denominator_error: Optional[str] = None
    previous_sql: Optional[str] = None
    sql_error: Optional[str] = None
    user_feedback: Optional[str] = None


class RunRequest(BaseModel):
    indicator_index: Optional[int] = Field(None, description="指标.json 数组下标（已有指标）")
    indicator_type: Optional[str] = Field(None, description="指标类型（新增指标时指定）")
    indicator_name: Optional[str] = Field(None, description="指标名（新增指标时指定）")
    selected_tables: Optional[list[str]] = None
    indicator_formula: Optional[str] = None
    supplement_info: Optional[str] = None
    numerator_desc: Optional[str] = None
    denominator_desc: Optional[str] = None
    indicator_desc: Optional[str] = None
    custom_system_prompt: Optional[str] = None
    custom_user_message: Optional[str] = None
    regenerate: Optional[RegenerateContext] = None
    mode: Optional[str] = Field(None, description="前端操作模式: select/create/edit")
    prompt_modified: bool = Field(False, description="用户是否修改了默认 prompt")
    conversation_id: Optional[str] = Field(None, description="会话 ID，再生成时复用")
    conversation_history: Optional[list[dict]] = Field(None, description="多轮对话历史 [{assistant_raw, user_feedback}]")


class TestSqlRequest(BaseModel):
    sql: str = Field(..., description="要测试的 SQL 语句")
    limit: int = Field(200, description="返回行数上限")


class AddIndicatorRequest(BaseModel):
    指标名: str
    类型: str
    指标计算公式: Optional[str] = ""
    分子描述: Optional[str] = ""
    分母描述: Optional[str] = ""
    指标描述: Optional[str] = ""
    涉及到表: list[str] = []
    numerator_sql: Optional[str] = ""
    denominator_sql: Optional[str] = ""
    sql: Optional[str] = ""
    system_prompt: Optional[str] = ""
    user_message: Optional[str] = ""


class PromptPreviewRequest(BaseModel):
    indicator_index: Optional[int] = None
    indicator_type: Optional[str] = None
    indicator_name: Optional[str] = None
    selected_tables: Optional[list[str]] = None
    indicator_formula: Optional[str] = None
    numerator_desc: Optional[str] = None
    denominator_desc: Optional[str] = None
    indicator_desc: Optional[str] = None


# ========================== 新阶段请求模型 ==========================

class UnderstandRequest(BaseModel):
    """对话1: 任务理解请求"""
    selected_tables: list[str]
    user_question: str
    indicator_type: str = "统计型"
    indicator_name: Optional[str] = None
    indicator_formula: Optional[str] = None
    numerator_desc: Optional[str] = None
    denominator_desc: Optional[str] = None
    indicator_desc: Optional[str] = None


class ContentPipelineRequest(BaseModel):
    """内容管道请求（独立调用）"""
    selected_tables: list[str]
    confirmed_question: str


class StructurePipelineRequest(BaseModel):
    """结构管道请求（独立调用）"""
    confirmed_question: str
    identifiers: dict


class GenerateSqlRequest(BaseModel):
    """对话2: SQL生成请求"""
    understanding: dict  # 对话1输出的理解结果
    identifiers: Optional[dict] = None  # 内容管道输出
    structure: Optional[dict] = None  # 结构管道输出
    selected_tables: list[str]
    indicator_type: str
    indicator_name: Optional[str] = None
    indicator_formula: Optional[str] = None
    numerator_desc: Optional[str] = None
    denominator_desc: Optional[str] = None
    indicator_desc: Optional[str] = None
    conversation_id: Optional[str] = None
    conversation_history: Optional[list[dict]] = None
    regenerate: Optional[RegenerateContext] = None


class LogicCheckRequest(BaseModel):
    """对话3: 逻辑检查请求"""
    sql: str
    original_intent: str
    original_question: str


class ContinueGenerateRequest(BaseModel):
    """用户确认理解后继续生成"""
    understanding: dict  # 用户确认的理解结果
    selected_tables: list[str]
    indicator_type: str
    indicator_name: Optional[str] = None
    indicator_formula: Optional[str] = None
    numerator_desc: Optional[str] = None
    denominator_desc: Optional[str] = None
    indicator_desc: Optional[str] = None
    # 前端分步调用时，中间结果直接传给后端
    identifiers: Optional[dict] = None  # 内容管道结果
    structure: Optional[dict] = None  # 结构管道结果
    use_content_pipeline: bool = True  # 是否在后端执行内容管道
    use_structure_pipeline: bool = True  # 是否在后端执行结构管道


# ========================== 工具函数 ==========================

def _json_default_for_sse(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat(sep=" ", timespec="seconds")
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, time_cls):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode("utf-8", errors="replace")
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _sse_format(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=_json_default_for_sse)}\n\n"


def _rate_formula(num: Optional[int], den: Optional[int]) -> Optional[str]:
    if num is None or den is None:
        return None
    if den == 0:
        return f"{num}/{den}=（分母为0无意义）"
    r = num / den
    if r == int(r):
        r_str = str(int(r))
    else:
        r_str = f"{r:.6f}".rstrip("0").rstrip(".")
    return f"{num}/{den}={r_str}"


def _build_indicator_from_request(body: RunRequest) -> dict[str, Any]:
    """从请求参数构建指标 dict（无论是已有指标还是新增指标）。"""
    if body.indicator_index is not None:
        indicators = load_indicators()
        if body.indicator_index >= len(indicators):
            raise HTTPException(400, detail="indicator_index 越界")
        indicator = merge_indicator_prompt_fields(
            indicators[body.indicator_index],
            indicator_formula=body.indicator_formula,
            supplement_info=body.supplement_info,
            numerator_desc=body.numerator_desc,
            denominator_desc=body.denominator_desc,
            indicator_desc=body.indicator_desc,
        )
    else:
        itype = body.indicator_type or "分子分母比值型"
        indicator = {
            "指标名": body.indicator_name or "临时指标",
            "类型": itype,
            "涉及到表": body.selected_tables or [],
        }
        if itype == "分子分母比值型":
            indicator["指标计算公式"] = body.indicator_formula or ""
            indicator["分子描述"] = body.numerator_desc or ""
            indicator["分母描述"] = body.denominator_desc or ""
        else:
            indicator["指标描述"] = body.indicator_desc or ""
        indicator = merge_indicator_prompt_fields(indicator)
    if body.indicator_type:
        indicator["类型"] = body.indicator_type
    return indicator


_MODE_LABELS = {"select": "查看已有指标", "create": "新增指标", "edit": "编辑指标"}


def _build_multiturn_messages(
    sys_prompt: str,
    base_user_msg: str,
    conversation_history: list[dict],
    user_feedback: str = "",
) -> list[dict[str, str]]:
    """将会话历史构建为多轮 messages 列表。"""
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": base_user_msg},
    ]
    for rnd in conversation_history:
        raw = rnd.get("assistant_raw", "")
        if raw:
            messages.append({"role": "assistant", "content": raw})
        fb = rnd.get("user_feedback", "")
        if fb:
            messages.append({"role": "user", "content": fb + "\n\n请根据以上反馈修正，仍然只输出 JSON。"})
    if user_feedback:
        messages.append({"role": "user", "content": user_feedback + "\n\n请根据以上反馈修正，仍然只输出 JSON。"})
    return messages


def _build_regen_feedback_text(body: "RunRequest") -> str:
    """从 regenerate 上下文构建用于多轮对话的用户反馈消息。"""
    regen = body.regenerate
    if not regen:
        return ""
    parts = []
    if regen.denominator_error:
        parts.append(f"分母SQL执行错误: {regen.denominator_error}")
    if regen.numerator_error:
        parts.append(f"分子SQL执行错误: {regen.numerator_error}")
    if regen.sql_error:
        parts.append(f"SQL执行错误: {regen.sql_error}")
    if regen.user_feedback:
        parts.append(f"修改建议: {regen.user_feedback}")
    return "\n".join(parts)


def _mode_label(mode: Optional[str]) -> str:
    return _MODE_LABELS.get(mode or "", "未知")


# ========================== 基础端点 ==========================

@app.get("/api/health")
def health():
    return {"ok": True, "model": get_model_name()}


@app.get("/api/indicators")
def api_indicators():
    try:
        data = load_indicators()
    except FileNotFoundError as e:
        raise HTTPException(500, detail=str(e)) from e
    return {"indicators": data}


@app.get("/api/tables_list")
def api_tables_list():
    """返回所有表名及其业务定义/注释。"""
    try:
        catalog = load_tables_catalog()
    except FileNotFoundError as e:
        raise HTTPException(500, detail=str(e)) from e
    return {"tables": get_all_table_names_with_comments(catalog)}


@app.get("/api/column_meanings")
def api_column_meanings():
    """英文字段名 -> 中文含义（来自 tables.json），供前端表头展示。同名字段多表并存时合并含义。"""
    try:
        catalog = load_tables_catalog()
    except FileNotFoundError as e:
        raise HTTPException(500, detail=str(e)) from e
    meanings: dict[str, str] = {}
    for t in catalog.get("tables") or []:
        for col in t.get("字段列表") or []:
            name = (col.get("字段名") or "").strip()
            if not name:
                continue
            cn = (col.get("中文含义") or "").strip()
            if not cn:
                continue
            if name not in meanings:
                meanings[name] = cn
            elif cn not in meanings[name]:
                meanings[name] = f"{meanings[name]} / {cn}"
    return {"meanings": meanings}


@app.post("/api/refresh_tables")
def api_refresh_tables():
    """执行 extract_tables.py 更新 tables.json。"""
    if not EXTRACT_TABLES_SCRIPT.is_file():
        raise HTTPException(500, detail=f"脚本不存在: {EXTRACT_TABLES_SCRIPT}")
    try:
        result = subprocess.run(
            [sys.executable, str(EXTRACT_TABLES_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return {
                "ok": False,
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-2000:],
            }
        return {"ok": True, "stdout": result.stdout[-2000:]}
    except subprocess.TimeoutExpired:
        raise HTTPException(504, detail="extract_tables.py 执行超时")
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/api/test_sql")
def api_test_sql(body: TestSqlRequest):
    """执行用户提供的 SQL 并返回结果预览。"""
    sql = body.sql.strip()
    if not sql:
        raise HTTPException(400, detail="SQL 为空")
    cols, rows, err = execute_limited(sql, limit=body.limit)
    cnt, cnt_err = execute_count(sql)
    return {
        "ok": err is None,
        "columns": cols,
        "rows": rows,
        "count": cnt,
        "error": err,
        "count_error": cnt_err,
    }


@app.post("/api/indicators/add")
def api_add_indicator(body: AddIndicatorRequest):
    """新增指标到 指标.json，同时记录 prompt。"""
    request_id = str(uuid.uuid4())
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    log_event(
        "indicator_add",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "指标名": body.指标名,
            "类型": body.类型,
            "涉及到表": body.涉及到表,
        },
        request_id=request_id,
    )

    indicators = load_indicators()
    new_ind: dict[str, Any] = {
        "指标名": body.指标名,
        "类型": body.类型,
        "涉及到表": body.涉及到表,
    }
    if body.类型 == "分子分母比值型":
        new_ind["指标计算公式"] = body.指标计算公式 or ""
        new_ind["分子描述"] = body.分子描述 or ""
        new_ind["分母描述"] = body.分母描述 or ""
        new_ind["numerator_sql"] = body.numerator_sql or ""
        new_ind["denominator_sql"] = body.denominator_sql or ""
    else:
        new_ind["指标描述"] = body.指标描述 or ""
        new_ind["sql"] = body.sql or ""
    if body.system_prompt:
        new_ind["last_system_prompt"] = body.system_prompt
    if body.user_message:
        new_ind["last_user_message"] = body.user_message
    indicators.append(new_ind)
    save_indicators(indicators)

    log_event(
        "indicator_add_complete",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "指标名": body.指标名,
            "指标下标": len(indicators) - 1,
        },
        request_id=request_id,
    )

    return {"ok": True, "index": len(indicators) - 1, "indicator": new_ind}


@app.put("/api/indicators/{index}")
def api_update_indicator(index: int, body: AddIndicatorRequest):
    """更新已有指标的 SQL 等字段，同时记录 prompt。"""
    request_id = str(uuid.uuid4())
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    log_event(
        "indicator_update",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "指标下标": index,
            "指标名": body.指标名,
            "类型": body.类型,
            "涉及到表": body.涉及到表,
        },
        request_id=request_id,
    )

    indicators = load_indicators()
    if index < 0 or index >= len(indicators):
        raise HTTPException(400, detail="index 越界")
    ind = indicators[index]
    ind["指标名"] = body.指标名
    ind["类型"] = body.类型
    ind["涉及到表"] = body.涉及到表
    if body.类型 == "分子分母比值型":
        ind["指标计算公式"] = body.指标计算公式 or ""
        ind["分子描述"] = body.分子描述 or ""
        ind["分母描述"] = body.分母描述 or ""
        ind["numerator_sql"] = body.numerator_sql or ""
        ind["denominator_sql"] = body.denominator_sql or ""
    else:
        ind["指标描述"] = body.指标描述 or ""
        ind["sql"] = body.sql or ""
    if body.system_prompt:
        ind["last_system_prompt"] = body.system_prompt
    if body.user_message:
        ind["last_user_message"] = body.user_message
    save_indicators(indicators)

    log_event(
        "indicator_update_complete",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "指标下标": index,
            "指标名": body.指标名,
        },
        request_id=request_id,
    )
    return {"ok": True, "indicator": ind}


@app.delete("/api/indicators/{index}")
def api_delete_indicator(index: int):
    """删除指定下标的指标。"""
    indicators = load_indicators()
    if index < 0 or index >= len(indicators):
        raise HTTPException(400, detail="index 越界")
    removed = indicators.pop(index)
    save_indicators(indicators)
    return {"ok": True, "removed": removed["指标名"]}


@app.get("/api/prompt_log")
def api_prompt_log():
    """返回 prompt_log.json 全部内容。"""
    return load_prompt_log()


@app.get("/api/prompt_log/{indicator_name}")
def api_prompt_log_by_name(indicator_name: str):
    """返回某个指标的 prompt 历史。"""
    log = load_prompt_log()
    entries = log.get(indicator_name, [])
    return {"indicator_name": indicator_name, "history": entries}


@app.post("/api/prompt_preview")
def api_prompt_preview(body: PromptPreviewRequest):
    """构建并返回 Prompt 预览（不调用模型）。"""
    run_body = RunRequest(
        indicator_index=body.indicator_index,
        indicator_type=body.indicator_type,
        indicator_name=body.indicator_name,
        selected_tables=body.selected_tables,
        indicator_formula=body.indicator_formula,
        numerator_desc=body.numerator_desc,
        denominator_desc=body.denominator_desc,
        indicator_desc=body.indicator_desc,
    )
    indicator = _build_indicator_from_request(run_body)
    table_names = body.selected_tables or indicator.get("涉及到表") or []
    if not table_names:
        return {"system_prompt": "", "user_message": "", "error": "未选择表"}
    try:
        catalog = load_tables_catalog()
        tables = filter_tables_for_prompt(catalog, table_names)
        schema_text = format_schema_block(tables)
        preview = build_prompt_preview(indicator, schema_text)
        return preview
    except Exception as e:
        return {"system_prompt": "", "user_message": "", "error": str(e)}


# ========================== 新阶段 API：任务理解（对话1） ==========================

@app.post("/api/understand")
def api_understand(body: UnderstandRequest):
    """
    对话1: 任务理解与前置检查
    返回模型对任务的理解结果，供用户确认
    """
    from prompt_builder import (
        SYSTEM_PROMPT_UNDERSTAND,
        user_message_understand,
        parse_understanding_json,
    )

    request_id = str(uuid.uuid4())
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    log_event(
        "understand_start",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "用户问题": body.user_question,
            "指标类型": body.indicator_type,
            "涉及表": body.selected_tables,
        },
        request_id=request_id,
    )

    try:
        table_names = body.selected_tables
        if not table_names:
            raise HTTPException(400, detail="未选择表")

        catalog = load_tables_catalog()
        tables = filter_tables_for_prompt(catalog, table_names)
        schema_text = format_schema_block(tables)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_UNDERSTAND},
            {"role": "user", "content": user_message_understand(schema_text, body.user_question)},
        ]

        t_llm0 = time.perf_counter()
        raw_response, thinking = chat_completion_multiturn(messages)
        llm_sec = time.perf_counter() - t_llm0

        understanding = parse_understanding_json(raw_response)

        log_event(
            "understand_end",
            {
                "本次请求时间戳": request_ts_iso,
                "request_id": request_id,
                "llm耗时秒": round(llm_sec, 3),
                "理解结果": understanding,
                "模型思考": thinking,
                "模型原文": raw_response,
            },
            request_id=request_id,
        )

        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": True,
            "understanding": understanding,
            "llm_thinking": thinking,
            "llm_raw": raw_response,
            "tables": table_names,
            "system_prompt": SYSTEM_PROMPT_UNDERSTAND,
            "user_message": user_message_understand(schema_text, body.user_question),
        }

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log_event("understand_error", {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "错误类型": type(e).__name__,
            "错误信息": str(e),
            "traceback": tb[-12000:] if len(tb) > 12000 else tb,
        }, request_id=request_id)
        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": False,
            "error": str(e),
        }


# ========================== 新阶段 API：内容管道（独立调用） ==========================

@app.post("/api/content_pipeline")
def api_content_pipeline(body: ContentPipelineRequest):
    """
    内容管道：标识符识别
    独立调用，不占对话
    """
    from prompt_builder import (
        SYSTEM_PROMPT_CONTENT_PIPELINE,
        user_message_content_pipeline,
        parse_content_pipeline_json,
    )

    request_id = str(uuid.uuid4())
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    log_event(
        "content_pipeline_start",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "确认的问题": body.confirmed_question,
            "涉及表": body.selected_tables,
        },
        request_id=request_id,
    )

    try:
        catalog = load_tables_catalog()
        tables = filter_tables_for_prompt(catalog, body.selected_tables)
        schema_text = format_schema_block(tables)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_CONTENT_PIPELINE},
            {"role": "user", "content": user_message_content_pipeline(schema_text, body.confirmed_question)},
        ]

        t_llm0 = time.perf_counter()
        raw_response, thinking = chat_completion_multiturn(messages)
        llm_sec = time.perf_counter() - t_llm0

        identifiers = parse_content_pipeline_json(raw_response)

        log_event(
            "content_pipeline_end",
            {
                "本次请求时间戳": request_ts_iso,
                "request_id": request_id,
                "llm耗时秒": round(llm_sec, 3),
                "标识符": identifiers,
                "模型思考": thinking,
                "模型原文": raw_response,
            },
            request_id=request_id,
        )

        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": True,
            "identifiers": identifiers,
            "llm_thinking": thinking,
            "llm_raw": raw_response,
            "system_prompt": SYSTEM_PROMPT_CONTENT_PIPELINE,
            "user_message": user_message_content_pipeline(schema_text, body.confirmed_question),
        }

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log_event("content_pipeline_error", {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "错误类型": type(e).__name__,
            "错误信息": str(e),
            "traceback": tb[-12000:] if len(tb) > 12000 else tb,
        }, request_id=request_id)
        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": False,
            "error": str(e),
        }


# ========================== 新阶段 API：结构管道（独立调用） ==========================

@app.post("/api/structure_pipeline")
def api_structure_pipeline(body: StructurePipelineRequest):
    """
    结构管道：SQL语法推导
    独立调用，不占对话
    """
    from prompt_builder import (
        SYSTEM_PROMPT_STRUCTURE_PIPELINE,
        user_message_structure_pipeline,
        parse_structure_pipeline_json,
    )

    request_id = str(uuid.uuid4())
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    log_event(
        "structure_pipeline_start",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "确认的问题": body.confirmed_question,
            "标识符": body.identifiers,
        },
        request_id=request_id,
    )

    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_STRUCTURE_PIPELINE},
            {"role": "user", "content": user_message_structure_pipeline(body.confirmed_question, json.dumps(body.identifiers, ensure_ascii=False))},
        ]

        t_llm0 = time.perf_counter()
        raw_response, thinking = chat_completion_multiturn(messages)
        llm_sec = time.perf_counter() - t_llm0

        structure = parse_structure_pipeline_json(raw_response)

        log_event(
            "structure_pipeline_end",
            {
                "本次请求时间戳": request_ts_iso,
                "request_id": request_id,
                "llm耗时秒": round(llm_sec, 3),
                "SQL结构": structure,
                "模型思考": thinking,
                "模型原文": raw_response,
            },
            request_id=request_id,
        )

        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": True,
            "structure": structure,
            "llm_thinking": thinking,
            "llm_raw": raw_response,
            "system_prompt": SYSTEM_PROMPT_STRUCTURE_PIPELINE,
            "user_message": user_message_structure_pipeline(body.confirmed_question, json.dumps(body.identifiers, ensure_ascii=False)),
        }

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log_event("structure_pipeline_error", {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "错误类型": type(e).__name__,
            "错误信息": str(e),
            "traceback": tb[-12000:] if len(tb) > 12000 else tb,
        }, request_id=request_id)
        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": False,
            "error": str(e),
        }


# ========================== 新阶段 API：继续生成（用户确认后） ==========================

@app.post("/api/continue_generate")
def api_continue_generate(body: ContinueGenerateRequest):
    """
    用户确认理解后，继续执行内容管道、结构管道和SQL生成
    返回SQL生成结果
    """
    request_id = str(uuid.uuid4())
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    log_event(
        "continue_generate_start",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "用户确认的理解": body.understanding,
            "指标类型": body.indicator_type,
            "涉及表": body.selected_tables,
        },
        request_id=request_id,
    )

    try:
        catalog = load_tables_catalog()
        tables = filter_tables_for_prompt(catalog, body.selected_tables)
        schema_text = format_schema_block(tables)

        # 优先使用前端传入的中间结果，否则在后端执行
        identifiers = body.identifiers
        structure = body.structure

        # 内容管道（仅当前端未传入时）
        if body.use_content_pipeline and not identifiers:
            content_result = _call_content_pipeline(schema_text, body.understanding.get("查询意图", ""))
            if content_result["ok"]:
                identifiers = content_result.get("identifiers")
            log_event("content_pipeline_result", content_result, request_id=request_id)

        # 结构管道（仅当前端未传入时）
        if body.use_structure_pipeline and identifiers and not structure:
            structure_result = _call_structure_pipeline(
                body.understanding.get("查询意图", ""),
                identifiers
            )
            if structure_result["ok"]:
                structure = structure_result.get("structure")
            log_event("structure_pipeline_result", structure_result, request_id=request_id)

        # 构建指标信息
        indicator = {
            "指标名": body.indicator_name or "临时指标",
            "类型": body.indicator_type,
            "指标计算公式": body.indicator_formula or "",
            "分子描述": body.numerator_desc or "",
            "分母描述": body.denominator_desc or "",
            "指标描述": body.indicator_desc or "",
            "补充信息": body.understanding.get("查询意图", ""),
        }

        # 使用现有的SQL生成逻辑
        is_ratio = body.indicator_type == "分子分母比值型"
        if is_ratio:
            result = _generate_dual_sql_new(
                indicator, body.selected_tables, schema_text,
                request_id, request_ts_iso, identifiers, structure
            )
        else:
            result = _generate_single_sql_new(
                indicator, body.selected_tables, schema_text,
                request_id, request_ts_iso, body.indicator_type,
                identifiers, structure
            )

        log_event(
            "continue_generate_end",
            {
                "本次请求时间戳": request_ts_iso,
                "request_id": request_id,
                "SQL生成结果": result.get("ok"),
                "identifiers": identifiers,
                "structure": structure,
            },
            request_id=request_id,
        )

        result["identifiers"] = identifiers
        result["structure"] = structure
        return result

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log_event("continue_generate_error", {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "错误类型": type(e).__name__,
            "错误信息": str(e),
            "traceback": tb[-12000:] if len(tb) > 12000 else tb,
        }, request_id=request_id)
        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": False,
            "error": str(e),
        }


def _call_content_pipeline(schema_text: str, confirmed_question: str) -> dict:
    """调用内容管道"""
    from prompt_builder import (
        SYSTEM_PROMPT_CONTENT_PIPELINE,
        user_message_content_pipeline,
        parse_content_pipeline_json,
    )
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_CONTENT_PIPELINE},
            {"role": "user", "content": user_message_content_pipeline(schema_text, confirmed_question)},
        ]
        raw_response, thinking = chat_completion_multiturn(messages)
        identifiers = parse_content_pipeline_json(raw_response)
        return {
            "ok": True,
            "identifiers": identifiers,
            "llm_thinking": thinking,
            "llm_raw": raw_response,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _call_structure_pipeline(confirmed_question: str, identifiers: dict) -> dict:
    """调用结构管道"""
    from prompt_builder import (
        SYSTEM_PROMPT_STRUCTURE_PIPELINE,
        user_message_structure_pipeline,
        parse_structure_pipeline_json,
    )
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_STRUCTURE_PIPELINE},
            {"role": "user", "content": user_message_structure_pipeline(confirmed_question, json.dumps(identifiers, ensure_ascii=False))},
        ]
        raw_response, thinking = chat_completion_multiturn(messages)
        structure = parse_structure_pipeline_json(raw_response)
        return {
            "ok": True,
            "structure": structure,
            "llm_thinking": thinking,
            "llm_raw": raw_response,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _generate_dual_sql_new(indicator, table_names, schema_text, request_id, request_ts_iso, identifiers, structure) -> dict:
    """生成双SQL（分子分母型）"""
    from prompt_builder import (
        SYSTEM_PROMPT_DUAL,
        user_message_dual,
    )
    from llm_client import parse_dual_sql_json

    conversation_id = str(uuid.uuid4())

    # 构建增强的提示信息
    supplemental = ""
    if identifiers:
        supplemental += f"\n\n【标识符识别结果】\n{json.dumps(identifiers, ensure_ascii=False, indent=2)}"
    if structure:
        supplemental += f"\n\n【SQL结构推导】\n{json.dumps(structure, ensure_ascii=False, indent=2)}"

    indicator_with_supplement = dict(indicator)
    indicator_with_supplement["补充信息"] = (indicator.get("补充信息") or "") + supplemental

    sys_prompt = SYSTEM_PROMPT_DUAL
    user_msg = user_message_dual(indicator_with_supplement, schema_text, regenerate_section="")

    log_event("generate_dual_start", {
        "request_id": request_id,
        "conversation_id": conversation_id,
        "system_prompt": sys_prompt,
        "user_message": user_msg,
    }, request_id=request_id)

    t_llm0 = time.perf_counter()
    raw_response, thinking = chat_completion_multiturn([
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_msg},
    ])
    llm_sec = time.perf_counter() - t_llm0

    num_sql, den_sql = parse_dual_sql_json(raw_response)

    # 执行验证
    (cn, en), (cd, ed) = execute_counts_parallel(num_sql, den_sql)

    both_ok = en is None and cn is not None and ed is None and cd is not None

    if both_ok:
        cols_n, rows_n, prev_n_err = execute_limited(num_sql, limit=PREVIEW_ROW_LIMIT)
        cols_d, rows_d, prev_d_err = execute_limited(den_sql, limit=PREVIEW_ROW_LIMIT)
        rate = round(cn * 100.0 / cd, 4) if cd and cn is not None else None

        log_event("generate_dual_end", {
            "request_id": request_id,
            "conversation_id": conversation_id,
            "ok": True,
            "numerator_sql": num_sql,
            "denominator_sql": den_sql,
            "numerator_count": cn,
            "denominator_count": cd,
            "rate": rate,
            "llm耗时秒": round(llm_sec, 3),
        }, request_id=request_id)

        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "conversation_id": conversation_id,
            "ok": True,
            "indicator_type": "分子分母比值型",
            "numerator_sql": num_sql,
            "denominator_sql": den_sql,
            "numerator_count": cn,
            "denominator_count": cd,
            "rate_percent": rate,
            "preview_columns": cols_n,
            "preview_rows": rows_n,
            "denominator_preview_columns": cols_d,
            "denominator_preview_rows": rows_d,
            "llm_thinking": thinking,
            "llm_raw": raw_response,
            "system_prompt": sys_prompt,
            "user_message": user_msg,
        }
    else:
        log_event("generate_dual_end", {
            "request_id": request_id,
            "conversation_id": conversation_id,
            "ok": False,
            "numerator_sql": num_sql,
            "denominator_sql": den_sql,
            "numerator_error": en,
            "denominator_error": ed,
            "llm耗时秒": round(llm_sec, 3),
        }, request_id=request_id)

        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "conversation_id": conversation_id,
            "ok": False,
            "indicator_type": "分子分母比值型",
            "numerator_sql": num_sql,
            "denominator_sql": den_sql,
            "numerator_error": en,
            "denominator_error": ed,
            "error": f"分子错误: {en}, 分母错误: {ed}",
            "llm_thinking": thinking,
            "llm_raw": raw_response,
            "system_prompt": sys_prompt,
            "user_message": user_msg,
        }


def _generate_single_sql_new(indicator, table_names, schema_text, request_id, request_ts_iso, itype, identifiers, structure) -> dict:
    """生成单SQL（统计型/大模型分析型）"""
    from prompt_builder import (
        SYSTEM_PROMPT_STAT,
        SYSTEM_PROMPT_ANALYSIS,
        user_message_stat,
        user_message_analysis,
    )
    from llm_client import parse_single_sql_json

    conversation_id = str(uuid.uuid4())
    is_analysis = (itype == "大模型分析型")

    sys_prompt = SYSTEM_PROMPT_ANALYSIS if is_analysis else SYSTEM_PROMPT_STAT
    build_user_msg = user_message_analysis if is_analysis else user_message_stat

    # 构建增强的提示信息
    supplemental = ""
    if identifiers:
        supplemental += f"\n\n【标识符识别结果】\n{json.dumps(identifiers, ensure_ascii=False, indent=2)}"
    if structure:
        supplemental += f"\n\n【SQL结构推导】\n{json.dumps(structure, ensure_ascii=False, indent=2)}"

    indicator_with_supplement = dict(indicator)
    indicator_with_supplement["补充信息"] = (indicator.get("补充信息") or "") + supplemental

    user_msg = build_user_msg(indicator_with_supplement, schema_text, regenerate_section="")

    log_event("generate_single_start", {
        "request_id": request_id,
        "conversation_id": conversation_id,
        "indicator_type": itype,
        "system_prompt": sys_prompt,
        "user_message": user_msg,
    }, request_id=request_id)

    t_llm0 = time.perf_counter()
    raw_response, thinking = chat_completion_multiturn([
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_msg},
    ])
    llm_sec = time.perf_counter() - t_llm0

    sql = parse_single_sql_json(raw_response)

    # 执行验证
    cnt, err = execute_count(sql)

    if err is None and cnt is not None:
        cols, rows, prev_err = execute_limited(sql, limit=PREVIEW_ROW_LIMIT)

        log_event("generate_single_end", {
            "request_id": request_id,
            "conversation_id": conversation_id,
            "ok": True,
            "sql": sql,
            "count": cnt,
            "indicator_type": itype,
            "llm耗时秒": round(llm_sec, 3),
        }, request_id=request_id)

        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "conversation_id": conversation_id,
            "ok": True,
            "indicator_type": itype,
            "sql": sql,
            "count": cnt,
            "preview_columns": cols,
            "preview_rows": rows,
            "llm_thinking": thinking,
            "llm_raw": raw_response,
            "system_prompt": sys_prompt,
            "user_message": user_msg,
        }
    else:
        log_event("generate_single_end", {
            "request_id": request_id,
            "conversation_id": conversation_id,
            "ok": False,
            "sql": sql,
            "error": err,
            "indicator_type": itype,
            "llm耗时秒": round(llm_sec, 3),
        }, request_id=request_id)

        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "conversation_id": conversation_id,
            "ok": False,
            "indicator_type": itype,
            "sql": sql,
            "error": err,
            "llm_thinking": thinking,
            "llm_raw": raw_response,
            "system_prompt": sys_prompt,
            "user_message": user_msg,
        }


# ========================== 新阶段 API：逻辑检查（对话3） ==========================

@app.post("/api/logic_check")
def api_logic_check(body: LogicCheckRequest):
    """
    对话3: 逻辑一致性检查
    仅当SQL执行结果为空时触发
    """
    from prompt_builder import (
        SYSTEM_PROMPT_LOGIC_CHECK,
        user_message_sql_to_nl,
        user_message_logic_compare,
        parse_logic_check_json,
    )

    request_id = str(uuid.uuid4())
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    log_event(
        "logic_check_start",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "SQL": body.sql,
            "原需求": body.original_intent,
        },
        request_id=request_id,
    )

    try:
        conv3_messages = [
            {"role": "system", "content": SYSTEM_PROMPT_LOGIC_CHECK},
        ]

        # Step 1: SQL转自然语言
        t1 = time.perf_counter()
        messages_step1 = conv3_messages + [
            {"role": "user", "content": user_message_sql_to_nl(body.sql)},
        ]
        raw_step1, thinking_step1 = chat_completion_multiturn(messages_step1)
        step1_sec = time.perf_counter() - t1

        try:
            result_step1 = parse_logic_check_json(raw_step1)
            sql_understanding = result_step1.get("sql理解", "")
        except Exception:
            # 如果解析失败，尝试提取文本描述
            sql_understanding = raw_step1.strip()

        log_event(
            "logic_check_step1",
            {
                "本次请求时间戳": request_ts_iso,
                "request_id": request_id,
                "SQL理解": sql_understanding,
                "耗时秒": round(step1_sec, 3),
            },
            request_id=request_id,
        )

        # Step 2: 逻辑对比
        t2 = time.perf_counter()
        messages_step2 = conv3_messages + [
            {"role": "user", "content": user_message_sql_to_nl(body.sql)},
            {"role": "assistant", "content": raw_step1},
            {"role": "user", "content": user_message_logic_compare(body.original_intent, sql_understanding)},
        ]
        raw_step2, thinking_step2 = chat_completion_multiturn(messages_step2)
        step2_sec = time.perf_counter() - t2

        logic_result = parse_logic_check_json(raw_step2)

        log_event(
            "logic_check_end",
            {
                "本次请求时间戳": request_ts_iso,
                "request_id": request_id,
                "逻辑检查结果": logic_result,
                "Step1耗时秒": round(step1_sec, 3),
                "Step2耗时秒": round(step2_sec, 3),
            },
            request_id=request_id,
        )

        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": True,
            "sql_understanding": sql_understanding,
            "logic_result": logic_result,
            "llm_thinking_step1": thinking_step1,
            "llm_thinking_step2": thinking_step2,
            "llm_raw_step1": raw_step1,
            "llm_raw_step2": raw_step2,
            "system_prompt": SYSTEM_PROMPT_LOGIC_CHECK,
        }

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log_event("logic_check_error", {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "错误类型": type(e).__name__,
            "错误信息": str(e),
            "traceback": tb[-12000:] if len(tb) > 12000 else tb,
        }, request_id=request_id)
        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": False,
            "error": str(e),
        }


# ========================== 核心 /api/run（支持三种类型） ==========================

@app.post("/api/run")
def api_run(body: RunRequest):
    request_id = str(uuid.uuid4())
    conversation_id = body.conversation_id or request_id
    is_regen = body.conversation_id is not None
    round_number = (len(body.conversation_history) + 1) if body.conversation_history else 1
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    try:
        indicator = _build_indicator_from_request(body)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, detail=str(e))

    itype = get_indicator_type(indicator)
    mode_label = _mode_label(body.mode)
    user_feedback = _build_regen_feedback_text(body) if is_regen else ""
    log_event(
        "run_start",
        {
            "本次请求时间戳": request_ts_iso,
            "request_id": request_id,
            "conversation_id": conversation_id,
            "轮次": round_number,
            "是否再生成": is_regen,
            "用户反馈": user_feedback or None,
            "指标名": indicator.get("指标名"),
            "指标类型": itype,
            "操作模式": mode_label,
            "请求参数": body.model_dump(),
        },
        request_id=request_id,
    )

    try:
        table_names = body.selected_tables or indicator.get("涉及到表") or []
        if not table_names:
            raise HTTPException(400, detail="未配置涉及表")

        catalog = load_tables_catalog()
        tables = filter_tables_for_prompt(catalog, table_names)
        missing = set(table_names) - {t.get("表名") for t in tables}
        if missing:
            raise HTTPException(400, detail=f"tables.json 中找不到表: {sorted(missing)}")

        schema_text = format_schema_block(tables)

        if itype == "分子分母比值型":
            return _run_dual(body, indicator, table_names, schema_text, request_id, request_ts_iso, conversation_id)
        elif itype == "统计型":
            return _run_single(body, indicator, table_names, schema_text, request_id, request_ts_iso, "统计型", conversation_id)
        else:
            return _run_single(body, indicator, table_names, schema_text, request_id, request_ts_iso, "大模型分析型", conversation_id)

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log_event("run_fatal", {
            "本次请求时间戳": request_ts_iso,
            "错误类型": type(e).__name__,
            "错误信息": str(e),
            "traceback": tb[-12000:] if len(tb) > 12000 else tb,
        }, request_id=request_id)
        return {
            "request_id": request_id,
            "request_ts_iso": request_ts_iso,
            "ok": False,
            "indicator": indicator,
            "indicator_type": itype,
            "error": str(e),
        }


def _run_dual(body, indicator, table_names, schema_text, request_id, request_ts_iso, conversation_id):
    """分子分母比值型的完整生成流程，支持多轮对话。"""
    from config import SQL_CACHE_ENABLED as _cache_on

    cache_key = make_cache_key(
        body.indicator_index or 0, table_names, indicator, schema_text
    )

    sys_prompt = body.custom_system_prompt or SYSTEM_PROMPT_DUAL
    base_dual = body.custom_user_message or user_message_dual(indicator, schema_text, regenerate_section="")
    _actual_sys_prompt = sys_prompt
    _actual_user_msg = base_dual

    is_multiturn = bool(body.conversation_history)
    user_feedback = _build_regen_feedback_text(body) if is_multiturn else ""
    initial_regen = "" if is_multiturn else build_regenerate_from_request(body.regenerate)

    num_attempts: list[dict[str, Any]] = []
    den_attempts: list[dict[str, Any]] = []
    raw_n = raw_d = ""
    think_n: Optional[str] = None
    think_d: Optional[str] = None
    num_sql = den_sql = ""
    num_count: Optional[int] = None
    den_count: Optional[int] = None
    cache_hit = False

    if _cache_on and not body.custom_system_prompt and not body.custom_user_message:
        hit = get_sql_pair(cache_key)
        if hit:
            num_sql, den_sql = hit
            cache_hit = True
            log_event("cache_hit", {"指标名": indicator.get("指标名"), "涉及表": table_names}, request_id=request_id)
            (cn, en), (cd, ed) = execute_counts_parallel(num_sql, den_sql)
            num_attempts.append({"attempt": 0, "sql": num_sql, "count": cn, "error": en})
            den_attempts.append({"attempt": 0, "sql": den_sql, "count": cd, "error": ed})
            if en is None and ed is None and cn is not None and cd is not None:
                num_count, den_count = cn, cd
                (cols_n, rows_n, prev_n_err), (cols_d, rows_d, prev_d_err) = execute_limited_parallel(
                    num_sql, den_sql, limit=PREVIEW_ROW_LIMIT
                )
                rate = round(num_count * 100.0 / den_count, 4) if den_count and num_count is not None else None
                return _dual_response(request_id, request_ts_iso, True, indicator, table_names,
                                      num_sql, den_sql, num_count, den_count, rate,
                                      cols_n, rows_n, prev_n_err, cols_d, rows_d, prev_d_err,
                                      num_attempts, den_attempts, think_n, raw_n, think_d, raw_d, cache_hit,
                                      conversation_id=conversation_id)
            invalidate(cache_key)
            cache_hit = False
            num_attempts.clear()
            den_attempts.clear()

    retry_suffix = ""
    last_en: Optional[str] = None
    last_ed: Optional[str] = None

    for attempt in range(1, SQL_RETRY_MAX_DUAL + 1):
        if is_multiturn:
            messages = _build_multiturn_messages(sys_prompt, base_dual, body.conversation_history, user_feedback)
            if attempt > 1 and retry_suffix:
                messages.append({"role": "user", "content": retry_suffix})
            user_msg_for_log = user_feedback or "(多轮对话)"
        else:
            suffix = initial_regen if attempt == 1 else retry_suffix
            user_msg_for_log = base_dual.rstrip() + "\n\n" + suffix if suffix else base_dual
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_msg_for_log},
            ]

        log_llm_dual_pending(
            request_id=request_id, 摘要=f"第{attempt}轮 双SQL生成",
            attempt=attempt, system_prompt=sys_prompt,
            user_message=user_msg_for_log if not is_multiturn else f"[多轮第{len(body.conversation_history or [])+1}轮] {user_feedback[:200]}",
        )

        t_llm0 = time.perf_counter()
        raw_msg, thinking = chat_completion_multiturn(messages)
        num_sql, den_sql = parse_dual_sql_json(raw_msg)
        raw = raw_msg
        llm_sec = time.perf_counter() - t_llm0
        raw_n = raw_d = raw
        think_n = think_d = thinking

        t_sql0 = time.perf_counter()
        (cn, en), (cd, ed) = execute_counts_parallel(num_sql, den_sql)
        sql_sec = time.perf_counter() - t_sql0
        num_attempts.append({"attempt": attempt, "sql": num_sql, "count": cn, "error": en})
        den_attempts.append({"attempt": attempt, "sql": den_sql, "count": cd, "error": ed})

        both_ok = en is None and cn is not None and ed is None and cd is not None

        preview_n_cols: list = []
        preview_n_rows: list = []
        preview_n_err: Optional[str] = None
        preview_d_cols: list = []
        preview_d_rows: list = []
        preview_d_err: Optional[str] = None
        if both_ok:
            (preview_n_cols, preview_n_rows, preview_n_err), (preview_d_cols, preview_d_rows, preview_d_err) = execute_limited_parallel(
                num_sql, den_sql, limit=PREVIEW_ROW_LIMIT
            )

        log_llm_dual(
            request_id=request_id,
            摘要=f"第{attempt}轮 {'成功' if both_ok else '失败'}",
            attempt=attempt,
            system_prompt=sys_prompt,
            user_message=user_msg_for_log,
            模型思考过程=thinking,
            模型返回的原始全文=raw,
            分子解析SQL=num_sql,
            分母解析SQL=den_sql,
            分子sql执行计数=cn,
            分子sql执行错误=en,
            分母sql执行计数=cd,
            分母sql执行错误=ed,
            llm_duration_sec=llm_sec,
            sql分子计数耗时秒=sql_sec,
            sql分母计数耗时秒=sql_sec,
            分子预览列名=preview_n_cols if both_ok else None,
            分子预览行=preview_n_rows if both_ok else None,
            分子预览错误=preview_n_err,
            分母预览列名=preview_d_cols if both_ok else None,
            分母预览行=preview_d_rows if both_ok else None,
            分母预览错误=preview_d_err,
        )

        if both_ok:
            num_count, den_count = cn, cd
            set_sql_pair(cache_key, num_sql, den_sql)
            cols_n, rows_n, prev_n_err = preview_n_cols, preview_n_rows, preview_n_err
            cols_d, rows_d, prev_d_err = preview_d_cols, preview_d_rows, preview_d_err
            rate = round(num_count * 100.0 / den_count, 4) if den_count and num_count is not None else None
            log_event("run_end_ok", {
                "本次请求时间戳": request_ts_iso,
                "numerator_sql": num_sql, "denominator_sql": den_sql,
                "numerator_count": num_count, "denominator_count": den_count,
                "rate_percent": rate, "rate_formula": _rate_formula(num_count, den_count),
                "尝试轮数": attempt, "llm耗时秒": round(llm_sec, 3),
            }, request_id=request_id)
            if body.prompt_modified:
                append_prompt_log_entry(
                    indicator.get("指标名", "未命名"),
                    system_prompt=_actual_sys_prompt,
                    user_message=_actual_user_msg,
                    result_ok=True,
                    sql_summary=f"numerator: {num_sql[:120]}... | denominator: {den_sql[:120]}...",
                    timestamp=request_ts_iso,
                )
            return _dual_response(request_id, request_ts_iso, True, indicator, table_names,
                                  num_sql, den_sql, num_count, den_count, rate,
                                  cols_n, rows_n, prev_n_err, cols_d, rows_d, prev_d_err,
                                  num_attempts, den_attempts, think_n, raw_n, think_d, raw_d, False,
                                  conversation_id=conversation_id)

        last_en = en or (None if cn is not None else "分子 COUNT 失败")
        last_ed = ed or (None if cd is not None else "分母 COUNT 失败")
        retry_suffix = build_dual_retry_suffix(
            numerator_sql=num_sql, denominator_sql=den_sql,
            numerator_error=last_en or "（分子无错误信息）",
            denominator_error=last_ed or "（分母无错误信息）",
        )

    err_msg = f"双 SQL 在 {SQL_RETRY_MAX_DUAL} 次尝试后仍无法通过 MySQL 校验"
    log_event("run_end_partial", {
        "本次请求时间戳": request_ts_iso, "error": err_msg,
        "最后分子SQL": num_sql, "最后分母SQL": den_sql,
        "最后分子错误": last_en, "最后分母错误": last_ed,
    }, request_id=request_id)
    if body.prompt_modified:
        append_prompt_log_entry(
            indicator.get("指标名", "未命名"),
            system_prompt=_actual_sys_prompt,
            user_message=_actual_user_msg,
            result_ok=False,
            sql_summary=err_msg,
            timestamp=request_ts_iso,
        )
    return _dual_response(request_id, request_ts_iso, False, indicator, table_names,
                          num_sql, den_sql, None, None, None,
                          [], [], last_en, [], [], last_ed,
                          num_attempts, den_attempts, think_n, raw_n, think_d, raw_d, False, err_msg,
                          conversation_id=conversation_id)


def _dual_response(rid, ts, ok, indicator, tables, nsql, dsql, nc, dc, rate,
                    cols_n, rows_n, nerr, cols_d, rows_d, derr,
                    nattempts, dattempts, thinkn, rawn, thinkd, rawd, cache_hit, error=None,
                    conversation_id=None):
    return {
        "request_id": rid, "request_ts_iso": ts, "ok": ok,
        "conversation_id": conversation_id or rid,
        "indicator": indicator, "indicator_type": "分子分母比值型",
        "selected_tables": tables,
        "numerator_sql": nsql, "denominator_sql": dsql,
        "numerator_count": nc, "denominator_count": dc,
        "rate_percent": rate, "rate_formula": _rate_formula(nc, dc),
        "error": error,
        "numerator_preview_error": nerr, "denominator_preview_error": derr,
        "numerator_attempts": nattempts, "denominator_attempts": dattempts,
        "preview_columns": cols_n, "preview_rows": rows_n,
        "denominator_preview_columns": cols_d, "denominator_preview_rows": rows_d,
        "numerator_llm_thinking": thinkn, "numerator_llm_raw": rawn or None,
        "denominator_llm_thinking": thinkd, "denominator_llm_raw": rawd or None,
        "cache_hit": cache_hit,
    }


def _run_single(body, indicator, table_names, schema_text, request_id, request_ts_iso, itype, conversation_id):
    """统计型/大模型分析型的单条 SQL 生成流程，支持多轮对话。"""
    from llm_client import chat_completion_single_sql, chat_completion_analysis

    is_analysis = (itype == "大模型分析型")
    sys_prompt = body.custom_system_prompt or (SYSTEM_PROMPT_ANALYSIS if is_analysis else SYSTEM_PROMPT_STAT)
    build_user_msg = user_message_analysis if is_analysis else user_message_stat
    base_msg = body.custom_user_message or build_user_msg(indicator, schema_text, regenerate_section="")
    _actual_sys_prompt = sys_prompt
    _actual_user_msg = base_msg

    is_multiturn = bool(body.conversation_history)
    user_feedback = _build_regen_feedback_text(body) if is_multiturn else ""

    regen = body.regenerate
    initial_regen = "" if is_multiturn else (build_stat_regenerate_from_request(regen) if regen else "")

    attempts: list[dict[str, Any]] = []
    sql = ""
    analysis_text = ""
    raw = ""
    thinking: Optional[str] = None
    count: Optional[int] = None
    retry_suffix = ""
    last_err: Optional[str] = None

    for attempt in range(1, SQL_RETRY_MAX + 1):
        if is_multiturn:
            messages = _build_multiturn_messages(sys_prompt, base_msg, body.conversation_history, user_feedback)
            if attempt > 1 and retry_suffix:
                messages.append({"role": "user", "content": retry_suffix})
            user_msg = f"[多轮第{len(body.conversation_history or [])+1}轮] {user_feedback[:200]}"
        else:
            suffix = initial_regen if attempt == 1 else retry_suffix
            user_msg = base_msg.rstrip() + "\n\n" + suffix if suffix else base_msg
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_msg},
            ]

        t_llm0 = time.perf_counter()
        if is_multiturn:
            raw_msg, thinking = chat_completion_multiturn(messages)
            raw = raw_msg
            if is_analysis:
                from llm_client import parse_analysis_json as _paj
                sql, analysis_text = _paj(raw)
            else:
                sql = parse_single_sql_json(raw)
        else:
            if is_analysis:
                raw, sql, analysis_text, thinking = chat_completion_analysis(sys_prompt, user_msg)
            else:
                raw, sql, thinking = chat_completion_single_sql(sys_prompt, user_msg)
        llm_sec = time.perf_counter() - t_llm0

        t_sql0 = time.perf_counter()
        cnt, err = execute_count(sql)
        sql_sec = time.perf_counter() - t_sql0
        attempts.append({"attempt": attempt, "sql": sql, "count": cnt, "error": err})

        log_llm_round(
            request_id=request_id,
            摘要=f"第{attempt}轮 {itype} {'成功' if err is None and cnt is not None else '失败'}",
            phase=itype,
            attempt=attempt,
            system_prompt=sys_prompt,
            user_message=user_msg,
            模型思考过程=thinking,
            模型返回的原始全文=raw,
            解析得到的SQL语句=sql,
            sql执行计数=cnt,
            sql执行错误=err,
            llm_duration_sec=llm_sec,
            sql_count_duration_sec=sql_sec,
        )

        if err is None and cnt is not None:
            count = cnt
            cols, rows, prev_err = execute_limited(sql, limit=PREVIEW_ROW_LIMIT)
            log_event("run_end_ok", {
                "本次请求时间戳": request_ts_iso, "sql": sql,
                "count": count, "indicator_type": itype,
                "尝试轮数": attempt, "llm耗时秒": round(llm_sec, 3),
            }, request_id=request_id)
            if body.prompt_modified:
                append_prompt_log_entry(
                    indicator.get("指标名", "未命名"),
                    system_prompt=_actual_sys_prompt,
                    user_message=_actual_user_msg,
                    result_ok=True,
                    sql_summary=sql[:200],
                    timestamp=request_ts_iso,
                )
            return {
                "request_id": request_id, "request_ts_iso": request_ts_iso, "ok": True,
                "conversation_id": conversation_id,
                "indicator": indicator, "indicator_type": itype, "selected_tables": table_names,
                "sql": sql, "count": count, "analysis": analysis_text,
                "preview_columns": cols, "preview_rows": rows, "preview_error": prev_err,
                "attempts": attempts,
                "llm_thinking": thinking, "llm_raw": raw or None,
                "error": None,
            }

        last_err = err or "COUNT 失败"
        retry_suffix = build_analysis_retry_suffix(sql=sql, error=last_err) if is_analysis else build_stat_retry_suffix(sql=sql, error=last_err)

    err_msg = f"SQL 在 {SQL_RETRY_MAX} 次尝试后仍无法通过 MySQL 校验: {last_err}"
    log_event("run_end_partial", {
        "本次请求时间戳": request_ts_iso, "error": err_msg,
        "最后SQL": sql, "最后错误": last_err,
    }, request_id=request_id)
    if body.prompt_modified:
        append_prompt_log_entry(
            indicator.get("指标名", "未命名"),
            system_prompt=_actual_sys_prompt,
            user_message=_actual_user_msg,
            result_ok=False,
            sql_summary=err_msg,
            timestamp=request_ts_iso,
        )
    return {
        "request_id": request_id, "request_ts_iso": request_ts_iso, "ok": False,
        "conversation_id": conversation_id,
        "indicator": indicator, "indicator_type": itype, "selected_tables": table_names,
        "sql": sql or None, "count": None, "analysis": analysis_text,
        "preview_columns": [], "preview_rows": [], "preview_error": last_err,
        "attempts": attempts,
        "llm_thinking": thinking, "llm_raw": raw or None,
        "error": err_msg,
    }


# ========================== 流式 /api/run/stream ==========================

@app.post("/api/run/stream")
def api_run_stream(body: RunRequest):
    request_id = str(uuid.uuid4())
    conversation_id = body.conversation_id or request_id
    request_ts_iso = datetime.now(timezone.utc).isoformat()

    try:
        indicator = _build_indicator_from_request(body)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, detail=str(e))

    itype = get_indicator_type(indicator)
    table_names = body.selected_tables or indicator.get("涉及到表") or []
    if not table_names:
        raise HTTPException(400, detail="未配置涉及表")

    catalog = load_tables_catalog()
    tables = filter_tables_for_prompt(catalog, table_names)
    missing = set(table_names) - {t.get("表名") for t in tables}
    if missing:
        raise HTTPException(400, detail=f"tables.json 中找不到表: {sorted(missing)}")

    schema_text = format_schema_block(tables)

    stream_headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    if itype == "分子分母比值型":
        gen = _stream_dual(body, indicator, table_names, schema_text, request_id, request_ts_iso, conversation_id)
    else:
        gen = _stream_single(body, indicator, table_names, schema_text, request_id, request_ts_iso, itype, conversation_id)

    return StreamingResponse(gen, media_type="text/event-stream; charset=utf-8", headers=stream_headers)


def _stream_dual(body, indicator, table_names, schema_text, request_id, request_ts_iso, conversation_id):
    """分子分母比值型的流式生成，支持多轮对话。"""
    mode_label = _mode_label(body.mode)
    is_multiturn = bool(body.conversation_history)
    user_feedback = _build_regen_feedback_text(body) if is_multiturn else ""
    is_regen = body.conversation_id is not None
    round_number = (len(body.conversation_history) + 1) if body.conversation_history else 1
    yield _sse_format("start", {"request_id": request_id, "request_ts_iso": request_ts_iso, "conversation_id": conversation_id, "indicator_type": "分子分母比值型"})
    log_event("run_start", {
        "本次请求时间戳": request_ts_iso, "request_id": request_id,
        "conversation_id": conversation_id,
        "轮次": round_number, "是否再生成": is_regen, "用户反馈": user_feedback or None,
        "指标名": indicator.get("指标名"), "指标类型": "分子分母比值型",
        "操作模式": mode_label,
    }, request_id=request_id)

    sys_prompt = body.custom_system_prompt or SYSTEM_PROMPT_DUAL
    base_dual = body.custom_user_message or user_message_dual(indicator, schema_text, regenerate_section="")
    _actual_sys_prompt = sys_prompt
    _actual_user_msg = base_dual
    initial_regen = "" if is_multiturn else build_regenerate_from_request(body.regenerate)

    num_attempts: list[dict[str, Any]] = []
    den_attempts: list[dict[str, Any]] = []
    raw_n = raw_d = ""
    think_n: Optional[str] = None
    think_d: Optional[str] = None
    num_sql = den_sql = ""
    num_count: Optional[int] = None
    den_count: Optional[int] = None
    retry_suffix = ""
    last_en: Optional[str] = None
    last_ed: Optional[str] = None

    try:
        for attempt in range(1, SQL_RETRY_MAX_DUAL + 1):
            if is_multiturn:
                messages = _build_multiturn_messages(sys_prompt, base_dual, body.conversation_history, user_feedback)
                if attempt > 1 and retry_suffix:
                    messages.append({"role": "user", "content": retry_suffix})
                user_msg = f"[多轮第{len(body.conversation_history or [])+1}轮] {user_feedback[:200]}"
            else:
                suffix = initial_regen if attempt == 1 else retry_suffix
                user_msg = base_dual.rstrip() + "\n\n" + suffix if suffix else base_dual
                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_msg},
                ]

            yield _sse_format("attempt_start", {"attempt": attempt, "max_attempts": SQL_RETRY_MAX_DUAL})

            reasoning_parts: list[str] = []
            content_parts: list[str] = []
            t_llm0 = time.perf_counter()
            try:
                for kind, piece in iter_stream_multiturn_chunks(messages):
                    if kind == "reasoning":
                        reasoning_parts.append(piece)
                    else:
                        content_parts.append(piece)
                    yield _sse_format("llm_delta", {"role": kind, "text": piece})
            except RuntimeError as e:
                yield _sse_format("error", {"message": str(e)})
                yield _sse_format("done", {"request_id": request_id, "ok": False, "error": str(e), "indicator_type": "分子分母比值型"})
                return

            llm_sec = time.perf_counter() - t_llm0
            yield _sse_format("llm_end", {"attempt": attempt, "llm_seconds": round(llm_sec, 3)})

            try:
                raw, num_sql, den_sql, thinking = merged_stream_parse_dual_sql(reasoning_parts, content_parts)
            except ValueError as e:
                num_attempts.append({"attempt": attempt, "sql": "", "count": None, "error": str(e)})
                den_attempts.append({"attempt": attempt, "sql": "", "count": None, "error": str(e)})
                if attempt < SQL_RETRY_MAX_DUAL:
                    retry_suffix = f"【上次回复无法解析为合法 JSON】\n{e}\n请只输出一个 JSON 对象。\n"
                    continue
                break

            raw_n = raw_d = raw
            think_n = think_d = thinking

            yield _sse_format("phase", {"phase": "mysql_count"})
            (cn, en), (cd, ed) = execute_counts_parallel(num_sql, den_sql)
            num_attempts.append({"attempt": attempt, "sql": num_sql, "count": cn, "error": en})
            den_attempts.append({"attempt": attempt, "sql": den_sql, "count": cd, "error": ed})

            both_ok = en is None and cn is not None and ed is None and cd is not None

            s_preview_n_cols: list = []
            s_preview_n_rows: list = []
            s_preview_n_err: Optional[str] = None
            s_preview_d_cols: list = []
            s_preview_d_rows: list = []
            s_preview_d_err: Optional[str] = None

            if both_ok:
                yield _sse_format("phase", {"phase": "mysql_preview"})
                (s_preview_n_cols, s_preview_n_rows, s_preview_n_err), (s_preview_d_cols, s_preview_d_rows, s_preview_d_err) = execute_limited_parallel(
                    num_sql, den_sql, limit=PREVIEW_ROW_LIMIT
                )

            log_llm_dual(
                request_id=request_id,
                摘要=f"第{attempt}轮 流式 {'成功' if both_ok else '失败'}",
                attempt=attempt,
                system_prompt=sys_prompt, user_message=user_msg,
                模型思考过程=thinking, 模型返回的原始全文=raw,
                分子解析SQL=num_sql, 分母解析SQL=den_sql,
                分子sql执行计数=cn, 分子sql执行错误=en,
                分母sql执行计数=cd, 分母sql执行错误=ed,
                llm_duration_sec=llm_sec,
                分子预览列名=s_preview_n_cols if both_ok else None,
                分子预览行=s_preview_n_rows if both_ok else None,
                分子预览错误=s_preview_n_err,
                分母预览列名=s_preview_d_cols if both_ok else None,
                分母预览行=s_preview_d_rows if both_ok else None,
                分母预览错误=s_preview_d_err,
            )

            if both_ok:
                num_count, den_count = cn, cd
                cols_n, rows_n, prev_n_err = s_preview_n_cols, s_preview_n_rows, s_preview_n_err
                cols_d, rows_d, prev_d_err = s_preview_d_cols, s_preview_d_rows, s_preview_d_err
                rate = round(num_count * 100.0 / den_count, 4) if den_count and num_count is not None else None
                log_event("run_end_ok", {
                    "本次请求时间戳": request_ts_iso,
                    "numerator_sql": num_sql, "denominator_sql": den_sql,
                    "numerator_count": num_count, "denominator_count": den_count,
                    "rate_percent": rate, "rate_formula": _rate_formula(num_count, den_count),
                    "尝试轮数": attempt, "llm耗时秒": round(llm_sec, 3),
                }, request_id=request_id)
                if body.prompt_modified:
                    append_prompt_log_entry(
                        indicator.get("指标名", "未命名"),
                        system_prompt=_actual_sys_prompt, user_message=_actual_user_msg,
                        result_ok=True, sql_summary=f"num: {num_sql[:100]}... | den: {den_sql[:100]}...",
                        timestamp=request_ts_iso,
                    )
                yield _sse_format("done", _dual_response(
                    request_id, request_ts_iso, True, indicator, table_names,
                    num_sql, den_sql, num_count, den_count, rate,
                    cols_n, rows_n, prev_n_err, cols_d, rows_d, prev_d_err,
                    num_attempts, den_attempts, think_n, raw_n, think_d, raw_d, False,
                    conversation_id=conversation_id
                ))
                return

            last_en = en or (None if cn is not None else "分子 COUNT 失败")
            last_ed = ed or (None if cd is not None else "分母 COUNT 失败")
            retry_suffix = build_dual_retry_suffix(
                numerator_sql=num_sql, denominator_sql=den_sql,
                numerator_error=last_en or "", denominator_error=last_ed or "",
            )

        if body.prompt_modified:
            append_prompt_log_entry(
                indicator.get("指标名", "未命名"),
                system_prompt=_actual_sys_prompt, user_message=_actual_user_msg,
                result_ok=False, sql_summary=f"双 SQL {SQL_RETRY_MAX_DUAL} 次均未通过",
                timestamp=request_ts_iso,
            )
        log_event("run_end_partial", {
            "本次请求时间戳": request_ts_iso,
            "error": f"双 SQL 在 {SQL_RETRY_MAX_DUAL} 次尝试后仍无法通过 MySQL 校验",
            "最后分子SQL": num_sql, "最后分母SQL": den_sql,
            "最后分子错误": last_en, "最后分母错误": last_ed,
        }, request_id=request_id)
        yield _sse_format("done", _dual_response(
            request_id, request_ts_iso, False, indicator, table_names,
            num_sql, den_sql, None, None, None,
            [], [], last_en, [], [], last_ed,
            num_attempts, den_attempts, think_n, raw_n, think_d, raw_d, False,
            f"双 SQL 在 {SQL_RETRY_MAX_DUAL} 次尝试后仍无法通过 MySQL 校验",
            conversation_id=conversation_id
        ))
    except Exception as e:
        yield _sse_format("error", {"message": str(e)})
        yield _sse_format("done", {"request_id": request_id, "ok": False, "error": str(e), "indicator_type": "分子分母比值型"})


def _stream_single(body, indicator, table_names, schema_text, request_id, request_ts_iso, itype, conversation_id):
    """统计型/大模型分析型的流式生成，支持多轮对话。"""
    is_analysis = (itype == "大模型分析型")
    mode_label = _mode_label(body.mode)
    is_multiturn = bool(body.conversation_history)
    user_feedback = _build_regen_feedback_text(body) if is_multiturn else ""
    is_regen = body.conversation_id is not None
    round_number = (len(body.conversation_history) + 1) if body.conversation_history else 1
    yield _sse_format("start", {"request_id": request_id, "request_ts_iso": request_ts_iso, "conversation_id": conversation_id, "indicator_type": itype})
    log_event("run_start", {
        "本次请求时间戳": request_ts_iso, "request_id": request_id,
        "conversation_id": conversation_id,
        "轮次": round_number, "是否再生成": is_regen, "用户反馈": user_feedback or None,
        "指标名": indicator.get("指标名"), "指标类型": itype,
        "操作模式": mode_label,
    }, request_id=request_id)

    sys_prompt = body.custom_system_prompt or (SYSTEM_PROMPT_ANALYSIS if is_analysis else SYSTEM_PROMPT_STAT)
    build_user_msg = user_message_analysis if is_analysis else user_message_stat
    base_msg = body.custom_user_message or build_user_msg(indicator, schema_text, regenerate_section="")
    _actual_sys_prompt = sys_prompt
    _actual_user_msg = base_msg
    initial_regen = "" if is_multiturn else (build_stat_regenerate_from_request(body.regenerate) if body.regenerate else "")

    attempts: list[dict[str, Any]] = []
    sql = ""
    analysis_text = ""
    raw = ""
    thinking: Optional[str] = None
    retry_suffix = ""
    last_err: Optional[str] = None

    try:
        for attempt in range(1, SQL_RETRY_MAX + 1):
            if is_multiturn:
                messages = _build_multiturn_messages(sys_prompt, base_msg, body.conversation_history, user_feedback)
                if attempt > 1 and retry_suffix:
                    messages.append({"role": "user", "content": retry_suffix})
                user_msg = f"[多轮第{len(body.conversation_history or [])+1}轮] {user_feedback[:200]}"
            else:
                suffix = initial_regen if attempt == 1 else retry_suffix
                user_msg = base_msg.rstrip() + "\n\n" + suffix if suffix else base_msg
                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_msg},
                ]

            yield _sse_format("attempt_start", {"attempt": attempt, "max_attempts": SQL_RETRY_MAX})

            reasoning_parts: list[str] = []
            content_parts: list[str] = []
            t_llm0 = time.perf_counter()
            try:
                for kind, piece in iter_stream_multiturn_chunks(messages):
                    if kind == "reasoning":
                        reasoning_parts.append(piece)
                    else:
                        content_parts.append(piece)
                    yield _sse_format("llm_delta", {"role": kind, "text": piece})
            except RuntimeError as e:
                yield _sse_format("error", {"message": str(e)})
                yield _sse_format("done", {"request_id": request_id, "ok": False, "error": str(e), "indicator_type": itype})
                return

            llm_sec = time.perf_counter() - t_llm0
            yield _sse_format("llm_end", {"attempt": attempt, "llm_seconds": round(llm_sec, 3)})

            try:
                if is_analysis:
                    raw, sql, analysis_text, thinking = merged_stream_parse_analysis(reasoning_parts, content_parts)
                else:
                    raw, sql, thinking = merged_stream_parse_single_sql(reasoning_parts, content_parts)
            except ValueError as e:
                attempts.append({"attempt": attempt, "sql": "", "count": None, "error": str(e)})
                if attempt < SQL_RETRY_MAX:
                    retry_suffix = f"【上次回复无法解析为合法 JSON】\n{e}\n请只输出合法 JSON。\n"
                    continue
                break

            yield _sse_format("phase", {"phase": "mysql_count"})
            cnt, err = execute_count(sql)
            attempts.append({"attempt": attempt, "sql": sql, "count": cnt, "error": err})

            log_llm_round(
                request_id=request_id,
                摘要=f"第{attempt}轮 流式 {itype} {'成功' if err is None and cnt is not None else '失败'}",
                phase=itype,
                attempt=attempt,
                system_prompt=sys_prompt, user_message=user_msg,
                模型思考过程=thinking, 模型返回的原始全文=raw,
                解析得到的SQL语句=sql,
                sql执行计数=cnt, sql执行错误=err,
                llm_duration_sec=llm_sec,
            )

            if err is None and cnt is not None:
                yield _sse_format("phase", {"phase": "mysql_preview"})
                cols, rows, prev_err = execute_limited(sql, limit=PREVIEW_ROW_LIMIT)
                log_event("run_end_ok", {
                    "本次请求时间戳": request_ts_iso, "sql": sql,
                    "count": cnt, "indicator_type": itype,
                    "尝试轮数": attempt, "llm耗时秒": round(llm_sec, 3),
                }, request_id=request_id)
                if body.prompt_modified:
                    append_prompt_log_entry(
                        indicator.get("指标名", "未命名"),
                        system_prompt=_actual_sys_prompt, user_message=_actual_user_msg,
                        result_ok=True, sql_summary=sql[:200],
                        timestamp=request_ts_iso,
                    )
                yield _sse_format("done", {
                    "request_id": request_id, "request_ts_iso": request_ts_iso, "ok": True,
                    "conversation_id": conversation_id,
                    "indicator": indicator, "indicator_type": itype, "selected_tables": table_names,
                    "sql": sql, "count": cnt, "analysis": analysis_text,
                    "preview_columns": cols, "preview_rows": rows, "preview_error": prev_err,
                    "attempts": attempts, "llm_thinking": thinking, "llm_raw": raw or None, "error": None,
                })
                return

            last_err = err or "COUNT 失败"
            retry_suffix = build_analysis_retry_suffix(sql=sql, error=last_err) if is_analysis else build_stat_retry_suffix(sql=sql, error=last_err)

        if body.prompt_modified:
            append_prompt_log_entry(
                indicator.get("指标名", "未命名"),
                system_prompt=_actual_sys_prompt, user_message=_actual_user_msg,
                result_ok=False, sql_summary=f"SQL {SQL_RETRY_MAX} 次均未通过: {last_err}",
                timestamp=request_ts_iso,
            )
        log_event("run_end_partial", {
            "本次请求时间戳": request_ts_iso,
            "error": f"SQL 在 {SQL_RETRY_MAX} 次尝试后仍无法通过校验: {last_err}",
            "最后SQL": sql, "最后错误": last_err,
        }, request_id=request_id)
        yield _sse_format("done", {
            "request_id": request_id, "request_ts_iso": request_ts_iso, "ok": False,
            "conversation_id": conversation_id,
            "indicator": indicator, "indicator_type": itype, "selected_tables": table_names,
            "sql": sql or None, "count": None, "analysis": analysis_text,
            "preview_columns": [], "preview_rows": [], "preview_error": last_err,
            "attempts": attempts, "llm_thinking": thinking, "llm_raw": raw or None,
            "error": f"SQL 在 {SQL_RETRY_MAX} 次尝试后仍无法通过校验: {last_err}",
        })
    except Exception as e:
        yield _sse_format("error", {"message": str(e)})
        yield _sse_format("done", {"request_id": request_id, "ok": False, "error": str(e), "indicator_type": itype})


# ========================== 日志与页面 ==========================

@app.get("/api/logs")
def api_logs(max_requests: int = 40):
    return {"requests": group_logs_for_api(max_requests=max_requests)}


@app.delete("/api/logs/{request_id}")
def api_logs_delete(request_id: str):
    result = delete_logs_by_request_id(request_id)
    if not result.get("ok"):
        raise HTTPException(400, detail=result.get("error", "删除失败"))
    if result.get("removed", 0) == 0:
        raise HTTPException(404, detail="未找到该 request_id 的日志行")
    return result


@app.get("/log")
def log_page():
    path = STATIC_DIR / "log.html"
    if not path.is_file():
        raise HTTPException(404, detail="static/log.html 缺失")
    return FileResponse(path)


@app.get("/")
def index_page():
    index = STATIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(404, detail="static/index.html 缺失")
    return FileResponse(index)
