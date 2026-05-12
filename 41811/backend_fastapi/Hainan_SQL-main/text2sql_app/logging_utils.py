"""工作流 JSONL 日志（每条 llm_round 聚合：发给模型的内容、思考、返回与 SQL）。"""
import json
import time
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from config import LOG_DIR, LOG_PREVIEW_ROW_LIMIT


def _ensure_log_dir() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR


def log_event(
    event: str,
    payload: Optional[dict[str, Any]] = None,
    *,
    request_id: Optional[str] = None,
) -> None:
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": event,
    }
    if request_id:
        row["request_id"] = request_id
    if payload:
        row["payload"] = payload
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _json_safe_value(v: Any) -> Any:
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    if isinstance(v, datetime):
        return v.isoformat(sep=" ", timespec="seconds")
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, (bytes, bytearray)):
        return v.decode("utf-8", errors="replace")
    return str(v)


def _json_safe_row(d: dict[str, Any]) -> dict[str, Any]:
    return {str(k): _json_safe_value(v) for k, v in d.items()}


def log_llm_round(
    *,
    request_id: str,
    摘要: str,
    phase: str,
    attempt: int,
    system_prompt: str,
    user_message: str,
    模型思考过程: Optional[str],
    模型返回的原始全文: str,
    解析得到的SQL语句: str,
    sql执行计数: Optional[int] = None,
    sql执行错误: Optional[str] = None,
    llm_duration_sec: Optional[float] = None,
    sql_count_duration_sec: Optional[float] = None,
) -> None:
    """写入一条人类可读的 LLM 交互记录（仍为单行 JSON，便于 jq）。"""
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": "llm_round",
        "request_id": request_id,
        "摘要": 摘要,
        "phase": phase,
        "attempt": attempt,
        "发给模型的_system提示": system_prompt,
        "发给模型的用户消息": user_message,
        "模型思考过程": 模型思考过程,
        "模型返回的原始全文": 模型返回的原始全文,
        "解析得到的SQL语句": 解析得到的SQL语句,
        "sql执行计数": sql执行计数,
        "sql执行错误": sql执行错误,
    }
    if llm_duration_sec is not None:
        row["llm耗时秒"] = round(llm_duration_sec, 3)
    if sql_count_duration_sec is not None:
        row["sql计数耗时秒"] = round(sql_count_duration_sec, 3)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def log_llm_dual(
    *,
    request_id: str,
    摘要: str,
    attempt: int,
    system_prompt: str,
    user_message: str,
    模型思考过程: Optional[str],
    模型返回的原始全文: str,
    分子解析SQL: str,
    分母解析SQL: str,
    分子sql执行计数: Optional[int],
    分子sql执行错误: Optional[str],
    分母sql执行计数: Optional[int],
    分母sql执行错误: Optional[str],
    llm_duration_sec: Optional[float] = None,
    sql分子计数耗时秒: Optional[float] = None,
    sql分母计数耗时秒: Optional[float] = None,
    分子预览列名: Optional[list[str]] = None,
    分子预览行: Optional[list[dict[str, Any]]] = None,
    分子预览错误: Optional[str] = None,
    分母预览列名: Optional[list[str]] = None,
    分母预览行: Optional[list[dict[str, Any]]] = None,
    分母预览错误: Optional[str] = None,
) -> None:
    """单次 LLM 产出分子+分母 SQL 的一轮记录（与 llm_round 并列写入时间线）。"""
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": "llm_dual",
        "request_id": request_id,
        "摘要": 摘要,
        "phase": "dual",
        "attempt": attempt,
        "发给模型的_system提示": system_prompt,
        "发给模型的用户消息": user_message,
        "模型思考过程": 模型思考过程,
        "模型返回的原始全文": 模型返回的原始全文,
        "分子解析SQL": 分子解析SQL,
        "分母解析SQL": 分母解析SQL,
        "分子sql执行计数": 分子sql执行计数,
        "分子sql执行错误": 分子sql执行错误,
        "分母sql执行计数": 分母sql执行计数,
        "分母sql执行错误": 分母sql执行错误,
    }
    if llm_duration_sec is not None:
        row["llm耗时秒"] = round(llm_duration_sec, 3)
    if sql分子计数耗时秒 is not None:
        row["sql分子计数耗时秒"] = round(sql分子计数耗时秒, 3)
    if sql分母计数耗时秒 is not None:
        row["sql分母计数耗时秒"] = round(sql分母计数耗时秒, 3)
    if (
        分子预览列名 is not None
        or 分子预览行 is not None
        or 分子预览错误 is not None
        or 分母预览列名 is not None
        or 分母预览行 is not None
        or 分母预览错误 is not None
    ):
        lim = int(LOG_PREVIEW_ROW_LIMIT)
        row["分子预览列名"] = list(分子预览列名 or [])
        row["分子预览行"] = [
            _json_safe_row(r) for r in (分子预览行 or [])[:lim]
        ]
        if 分子预览错误 is not None:
            row["分子预览错误"] = 分子预览错误
        row["分母预览列名"] = list(分母预览列名 or [])
        row["分母预览行"] = [
            _json_safe_row(r) for r in (分母预览行 or [])[:lim]
        ]
        if 分母预览错误 is not None:
            row["分母预览错误"] = 分母预览错误
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def log_llm_dual_pending(
    *,
    request_id: str,
    摘要: str,
    attempt: int,
    system_prompt: str,
    user_message: str,
) -> None:
    """
    在发起 Chat Completions **之前**写入：便于日志页轮询时立刻看到已发送的 system/user，
    而不必等模型整段返回（非流式接口下这段时间可能长达数十秒）。
    """
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": "llm_dual_pending",
        "request_id": request_id,
        "摘要": 摘要,
        "phase": "dual_pending",
        "attempt": attempt,
        "发给模型的_system提示": system_prompt,
        "发给模型的用户消息": user_message,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_all_log_lines() -> list[dict[str, Any]]:
    """读取 logs 下所有 workflow_*.jsonl 行（按文件名排序后按行顺序）。"""
    _ensure_log_dir()
    if not LOG_DIR.is_dir():
        return []
    lines: list[dict[str, Any]] = []
    for path in sorted(LOG_DIR.glob("workflow_*.jsonl")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue
    return lines


def group_logs_for_api(max_requests: int = 30) -> list[dict[str, Any]]:
    """
    将 JSONL 按 conversation_id 聚合为多轮对话展示结构。
    每个 conversation 包含多个 round（每个 round 对应一个 request_id）。
    """
    raw = read_all_log_lines()
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    for row in raw:
        rid = row.get("request_id")
        if not rid:
            continue
        if rid not in by_id:
            by_id[rid] = {
                "request_id": rid,
                "ts_iso": row.get("ts_iso"),
                "conversation_id": None,
                "run": None,
                "llm_rounds": [],
                "end": None,
                "fatal": None,
            }
            order.append(rid)
        bucket = by_id[rid]
        if row.get("ts_iso") and bucket["ts_iso"]:
            if row.get("ts_iso", "") > bucket["ts_iso"]:
                bucket["ts_iso"] = row["ts_iso"]

        ev = row.get("event")
        if ev == "run_start":
            bucket["run"] = row
            payload = row.get("payload", {})
            cid = payload.get("conversation_id")
            if cid:
                bucket["conversation_id"] = cid
        elif ev in ("llm_round", "llm_dual", "llm_dual_pending"):
            bucket["llm_rounds"].append(row)
        elif ev in ("run_end_ok", "run_end_partial"):
            bucket["end"] = row
        elif ev == "run_fatal":
            bucket["fatal"] = row

    by_cid: dict[str, dict[str, Any]] = {}
    cid_order: list[str] = []

    seen_rids: set[str] = set()
    for rid in reversed(order):
        if rid in seen_rids:
            continue
        seen_rids.add(rid)
        bucket = by_id[rid]
        cid = bucket.get("conversation_id") or rid
        if cid not in by_cid:
            by_cid[cid] = {
                "conversation_id": cid,
                "ts_iso": bucket["ts_iso"],
                "rounds": [],
            }
            cid_order.append(cid)
        by_cid[cid]["rounds"].append(bucket)
        if bucket["ts_iso"] and bucket["ts_iso"] > (by_cid[cid]["ts_iso"] or ""):
            by_cid[cid]["ts_iso"] = bucket["ts_iso"]

    for conv in by_cid.values():
        conv["rounds"].sort(key=lambda r: r.get("ts_iso") or "")

    cid_order.sort(key=lambda c: by_cid[c].get("ts_iso") or "", reverse=True)
    return [by_cid[c] for c in cid_order[:max_requests]]


def _collect_request_ids_for_conversation(conversation_id: str) -> set[str]:
    """找到属于该 conversation_id 的所有 request_id。"""
    rids: set[str] = {conversation_id}
    all_lines = read_all_log_lines()
    for row in all_lines:
        ev = row.get("event")
        if ev == "run_start":
            payload = row.get("payload", {})
            cid = payload.get("conversation_id")
            rid = row.get("request_id")
            if cid == conversation_id and rid:
                rids.add(rid)
    return rids


def delete_logs_by_request_id(request_id: str) -> dict[str, Any]:
    """
    从 logs 下所有 workflow_*.jsonl 中删除匹配的行。
    支持删除单个 request_id 或整个 conversation_id 对应的所有日志。
    """
    _ensure_log_dir()
    rid_target = (request_id or "").strip()
    if not rid_target:
        return {"ok": False, "removed": 0, "files": [], "error": "request_id 为空"}

    target_ids = _collect_request_ids_for_conversation(rid_target)

    removed_total = 0
    files_touched: list[str] = []

    for path in sorted(LOG_DIR.glob("workflow_*.jsonl")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_lines = f.readlines()
        except OSError:
            continue

        kept: list[str] = []
        n_drop = 0
        for line in raw_lines:
            stripped = line.strip()
            if not stripped:
                kept.append(line)
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError:
                kept.append(line)
                continue
            if obj.get("request_id") in target_ids:
                n_drop += 1
            else:
                kept.append(line)

        if n_drop:
            files_touched.append(path.name)
            removed_total += n_drop
            tmp = path.with_suffix(path.suffix + ".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                f.writelines(kept)
            tmp.replace(path)

    return {
        "ok": True,
        "removed": removed_total,
        "files": files_touched,
    }


# ========================== 新阶段日志函数 ==========================

def log_understand_round(
    *,
    request_id: str,
    system_prompt: str,
    user_message: str,
    模型思考过程: Optional[str],
    模型返回的原始全文: str,
    理解结果: dict,
    llm_duration_sec: Optional[float] = None,
) -> None:
    """记录任务理解阶段的日志（对话1）。"""
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": "understand_round",
        "phase": "任务理解",
        "request_id": request_id,
        "发给模型的_system提示": system_prompt,
        "发给模型的用户消息": user_message,
        "模型思考过程": 模型思考过程,
        "模型返回的原始全文": 模型返回的原始全文,
        "理解结果": 理解结果,
    }
    if llm_duration_sec is not None:
        row["llm耗时秒"] = round(llm_duration_sec, 3)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def log_content_pipeline_round(
    *,
    request_id: str,
    system_prompt: str,
    user_message: str,
    模型思考过程: Optional[str],
    模型返回的原始全文: str,
    标识符结果: dict,
    llm_duration_sec: Optional[float] = None,
) -> None:
    """记录内容管道阶段的日志。"""
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": "content_pipeline",
        "phase": "内容管道",
        "request_id": request_id,
        "发给模型的_system提示": system_prompt,
        "发给模型的用户消息": user_message,
        "模型思考过程": 模型思考过程,
        "模型返回的原始全文": 模型返回的原始全文,
        "标识符结果": 标识符结果,
    }
    if llm_duration_sec is not None:
        row["llm耗时秒"] = round(llm_duration_sec, 3)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def log_structure_pipeline_round(
    *,
    request_id: str,
    system_prompt: str,
    user_message: str,
    模型思考过程: Optional[str],
    模型返回的原始全文: str,
    SQL结构结果: dict,
    llm_duration_sec: Optional[float] = None,
) -> None:
    """记录结构管道阶段的日志。"""
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": "structure_pipeline",
        "phase": "结构管道",
        "request_id": request_id,
        "发给模型的_system提示": system_prompt,
        "发给模型的用户消息": user_message,
        "模型思考过程": 模型思考过程,
        "模型返回的原始全文": 模型返回的原始全文,
        "SQL结构结果": SQL结构结果,
    }
    if llm_duration_sec is not None:
        row["llm耗时秒"] = round(llm_duration_sec, 3)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def log_logic_check_round(
    *,
    request_id: str,
    system_prompt: str,
    step1_user_message: str,
    step1_assistant_message: str,
    step2_user_message: str,
    step2_assistant_message: str,
    模型思考过程_step1: Optional[str],
    模型思考过程_step2: Optional[str],
    SQL理解: str,
    逻辑检查结果: dict,
    step1_duration_sec: Optional[float] = None,
    step2_duration_sec: Optional[float] = None,
) -> None:
    """记录逻辑检查阶段的日志（对话3）。"""
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": "logic_check",
        "phase": "逻辑一致性检查",
        "request_id": request_id,
        "发给模型的_system提示": system_prompt,
        "Step1_User消息": step1_user_message,
        "Step1_Assistant回复": step1_assistant_message,
        "Step2_User消息": step2_user_message,
        "Step2_Assistant回复": step2_assistant_message,
        "模型思考过程_Step1": 模型思考过程_step1,
        "模型思考过程_Step2": 模型思考过程_step2,
        "SQL理解": SQL理解,
        "逻辑检查结果": 逻辑检查结果,
    }
    if step1_duration_sec is not None:
        row["Step1耗时秒"] = round(step1_duration_sec, 3)
    if step2_duration_sec is not None:
        row["Step2耗时秒"] = round(step2_duration_sec, 3)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def log_workflow_complete(
    *,
    request_id: str,
    total_rounds: int,
    phases: list[str],
    total_llm_seconds: float,
    final_result: dict,
) -> None:
    """记录完整工作流完成的日志。"""
    _ensure_log_dir()
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = LOG_DIR / f"workflow_{day}.jsonl"
    row: dict[str, Any] = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "event": "workflow_complete",
        "request_id": request_id,
        "总轮次": total_rounds,
        "执行的阶段": phases,
        "总LLM耗时秒": round(total_llm_seconds, 3),
        "最终结果": final_result,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
