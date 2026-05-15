"""OpenAI 兼容 Chat Completions。"""
import json
import re
import time
from typing import Iterator, Literal, Optional, Tuple

import httpx
from openai import APIConnectionError, APITimeoutError, OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_HTTP_TRUST_ENV,
    OPENAI_MODEL,
    OPENAI_SEED,
    OPENAI_TEMPERATURE,
    OPENAI_TIMEOUT_SEC,
)

_client: Optional[OpenAI] = None


def _resolve_temperature(explicit: Optional[float]) -> float:
    return OPENAI_TEMPERATURE if explicit is None else explicit


def _seed_kwargs() -> dict:
    if OPENAI_SEED is None:
        return {}
    return {"seed": OPENAI_SEED}


def get_client() -> OpenAI:
    global _client
    if _client is None:
        http_client = httpx.Client(
            timeout=OPENAI_TIMEOUT_SEC,
            trust_env=OPENAI_HTTP_TRUST_ENV,
        )
        _client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL.rstrip("/"),
            http_client=http_client,
        )
    return _client


def get_model_name() -> str:
    return OPENAI_MODEL


def strip_sql_fences(raw: str) -> str:
    text = raw.strip()
    m = re.match(r"^```(?:sql)?\s*([\s\S]*?)```\s*$", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def take_first_statement(sql: str) -> str:
    """只保留第一条语句，去掉末尾分号。"""
    s = strip_sql_fences(sql).strip()
    if ";" in s:
        s = s.split(";", 1)[0].strip()
    return s


def extract_thinking_from_content(text: str) -> Tuple[Optional[str], str]:
    """
    从正文中拆分「思考」与「剩余内容」（供提取 SQL）。
    兼容 XML 风格 think 标签与常见闭合标记。
    """
    t = text.strip()
    if not t:
        return None, ""

    close_m = re.search(r"\x3c/\x74hink\x3e", t, re.IGNORECASE)
    if close_m:
        think = t[: close_m.start()].strip()
        rest = t[close_m.end() :].strip()
        think = re.sub(r"^\s*\x3cthink\x3e\s*", "", think, count=1, flags=re.IGNORECASE)
        return (think or None), rest

    m = re.match(
        r"^\s*\x3cthink\x3e([\s\S]*?)\x3c/\x74hink\x3e\s*([\s\S]*)$",
        t,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        think = m.group(1).strip() or None
        return think, m.group(2).strip()

    return None, t


def chat_completion(
    system_prompt: str,
    user_message: str,
    *,
    temperature: Optional[float] = None,
) -> tuple[str, str, Optional[str]]:
    """
    返回 (模型返回的原始全文, 清洗后单条 SQL, 模型思考过程或 None)。

    思考过程优先取接口字段 reasoning_content / reasoning；
    否则尝试从正文中的 think 标签或闭合标签前文本解析。

    对短暂断连会最多重试 3 次（间隔递增）。
    """
    model = get_model_name()
    t = _resolve_temperature(temperature)
    resp = None

    for attempt in range(3):
        try:
            client = get_client()
            resp = client.chat.completions.create(
                model=model,
                temperature=t,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                **_seed_kwargs(),
            )
            break
        except (APIConnectionError, APITimeoutError) as e:
            if attempt < 2:
                time.sleep(1.0 + attempt * 1.5)
                global _client
                _client = None
                continue
            raise RuntimeError(
                "调用 LLM 时网络连接失败（已重试 3 次）。"
                "常见原因：1) 系统/终端设置了 HTTPS_PROXY 且代理异常，可在 config.py 保持 "
                "OPENAI_HTTP_TRUST_ENV = False，并在终端执行 unset HTTPS_PROXY HTTP_PROXY；"
                "2) api.vveai.com 暂时不可用或阻断；3) 本机防火墙/网络不稳。"
                f" 原始错误: {e}"
            ) from e

    assert resp is not None
    msg = resp.choices[0].message
    raw_full = (msg.content or "").strip()

    thinking: Optional[str] = None
    for attr in ("reasoning_content", "reasoning"):
        v = getattr(msg, attr, None)
        if isinstance(v, str) and v.strip():
            thinking = v.strip()
            break

    body_for_sql = raw_full
    if thinking is None:
        parsed_think, remainder = extract_thinking_from_content(raw_full)
        if parsed_think is not None:
            thinking = parsed_think
            body_for_sql = remainder
        else:
            body_for_sql = raw_full
    else:
        body_for_sql = raw_full

    sql = take_first_statement(body_for_sql)
    return raw_full, sql, thinking


def _strip_json_fence(text: str) -> str:
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*([\s\S]*?)```\s*$", t, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return t


def _extract_json_object(raw: str) -> dict:
    """从模型回复中提取第一个完整的 JSON 对象。"""
    t = _strip_json_fence(raw)
    start = t.find("{")
    end = t.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("回复中未找到 JSON 对象")
    return json.loads(t[start : end + 1])


def parse_dual_sql_json(raw: str) -> tuple[str, str]:
    """
    从模型回复中解析 {"numerator_sql":"...","denominator_sql":"..."}。
    兼容外围说明文字，取第一个 { 与最后一个 } 之间的 JSON。
    """
    obj = _extract_json_object(raw)
    n = (obj.get("numerator_sql") or obj.get("分子sql") or "").strip()
    d = (obj.get("denominator_sql") or obj.get("分母sql") or "").strip()
    if not n or not d:
        raise ValueError("JSON 中缺少有效的 numerator_sql 或 denominator_sql")
    return take_first_statement(n), take_first_statement(d)


def parse_single_sql_json(raw: str) -> str:
    """解析 {"sql":"..."} 格式的单条 SQL 返回。"""
    obj = _extract_json_object(raw)
    s = (obj.get("sql") or "").strip()
    if not s:
        raise ValueError("JSON 中缺少有效的 sql 字段")
    return take_first_statement(s)


def parse_analysis_json(raw: str) -> tuple[str, str]:
    """解析 {"sql":"...","analysis":"..."} 格式的分析型返回。"""
    obj = _extract_json_object(raw)
    s = (obj.get("sql") or "").strip()
    a = (obj.get("analysis") or "").strip()
    if not s:
        raise ValueError("JSON 中缺少有效的 sql 字段")
    return take_first_statement(s), a


def _call_chat(
    messages: list[dict[str, str]],
    *,
    temperature: Optional[float] = None,
    stream: bool = False,
):
    """底层 Chat Completions 调用（含重试），支持单轮和多轮。"""
    model = get_model_name()
    t = _resolve_temperature(temperature)
    resp = None
    for attempt in range(3):
        try:
            client = get_client()
            resp = client.chat.completions.create(
                model=model,
                temperature=t,
                messages=messages,
                stream=stream,
                **_seed_kwargs(),
            )
            return resp
        except (APIConnectionError, APITimeoutError) as e:
            if attempt < 2:
                time.sleep(1.0 + attempt * 1.5)
                global _client
                _client = None
                continue
            raise RuntimeError(
                "调用 LLM 时网络连接失败（已重试 3 次）。"
                "常见原因：1) 系统/终端设置了 HTTPS_PROXY 且代理异常，可在 config.py 保持 "
                "OPENAI_HTTP_TRUST_ENV = False，并在终端执行 unset HTTPS_PROXY HTTP_PROXY；"
                "2) api.vveai.com 暂时不可用或阻断；3) 本机防火墙/网络不稳。"
                f" 原始错误: {e}"
            ) from e
    raise RuntimeError("LLM 调用未返回有效响应")


def _extract_response(resp) -> tuple[str, Optional[str]]:
    """从 Chat Completions 响应中提取 (raw_content, thinking)。"""
    msg = resp.choices[0].message
    raw_full = (msg.content or "").strip()
    thinking: Optional[str] = None
    for attr in ("reasoning_content", "reasoning"):
        v = getattr(msg, attr, None)
        if isinstance(v, str) and v.strip():
            thinking = v.strip()
            break
    return raw_full, thinking


def chat_completion_message(
    system_prompt: str,
    user_message: str,
    *,
    temperature: Optional[float] = None,
) -> tuple[str, Optional[str]]:
    """
    仅返回 (message.content 全文, 思考过程)；不做 SQL 截取。
    与 chat_completion 相同的重试策略。
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    resp = _call_chat(messages, temperature=temperature)
    return _extract_response(resp)


def chat_completion_multiturn(
    messages: list[dict[str, str]],
    *,
    temperature: Optional[float] = None,
) -> tuple[str, Optional[str]]:
    """多轮对话，返回 (raw_content, thinking)。messages 为完整消息列表。"""
    resp = _call_chat(messages, temperature=temperature)
    return _extract_response(resp)


def chat_completion_dual_sql(
    system_prompt: str,
    user_message: str,
    *,
    temperature: Optional[float] = None,
) -> tuple[str, str, str, Optional[str]]:
    """一次调用解析出 (raw, numerator_sql, denominator_sql, thinking)。"""
    raw, thinking = chat_completion_message(system_prompt, user_message, temperature=temperature)
    num_sql, den_sql = parse_dual_sql_json(raw)
    return raw, num_sql, den_sql, thinking


def chat_completion_single_sql(
    system_prompt: str,
    user_message: str,
    *,
    temperature: Optional[float] = None,
) -> tuple[str, str, Optional[str]]:
    """一次调用解析出 (raw, sql, thinking)。"""
    raw, thinking = chat_completion_message(system_prompt, user_message, temperature=temperature)
    sql = parse_single_sql_json(raw)
    return raw, sql, thinking


def chat_completion_analysis(
    system_prompt: str,
    user_message: str,
    *,
    temperature: Optional[float] = None,
) -> tuple[str, str, str, Optional[str]]:
    """一次调用解析出 (raw, sql, analysis, thinking)。"""
    raw, thinking = chat_completion_message(system_prompt, user_message, temperature=temperature)
    sql, analysis = parse_analysis_json(raw)
    return raw, sql, analysis, thinking


StreamChunkKind = Literal["reasoning", "content"]


def _iter_stream_from_messages(
    messages: list[dict[str, str]],
    *,
    temperature: Optional[float] = None,
) -> Iterator[tuple[StreamChunkKind, str]]:
    """底层流式调用，接受完整 messages 列表。"""
    model = get_model_name()
    t = _resolve_temperature(temperature)
    for attempt in range(3):
        try:
            client = get_client()
            stream = client.chat.completions.create(
                model=model,
                temperature=t,
                messages=messages,
                stream=True,
                **_seed_kwargs(),
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta is None:
                    continue
                for attr in ("reasoning_content", "reasoning"):
                    rc = getattr(delta, attr, None)
                    if isinstance(rc, str) and rc:
                        yield ("reasoning", rc)
                        break
                cc = getattr(delta, "content", None)
                if isinstance(cc, str) and cc:
                    yield ("content", cc)
            return
        except (APIConnectionError, APITimeoutError) as e:
            if attempt < 2:
                time.sleep(1.0 + attempt * 1.5)
                global _client
                _client = None
                continue
            raise RuntimeError(
                "流式调用 LLM 时网络连接失败（已重试 3 次）。"
                "可尝试关闭代理或检查 OPENAI_HTTP_TRUST_ENV / 网关可用性。"
                f" 原始错误: {e}"
            ) from e
    raise RuntimeError("流式调用 LLM 未返回有效流")


def iter_stream_completion_chunks(
    system_prompt: str,
    user_message: str,
    *,
    temperature: Optional[float] = None,
) -> Iterator[tuple[StreamChunkKind, str]]:
    """单轮流式 Chat Completions。"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    yield from _iter_stream_from_messages(messages, temperature=temperature)


def iter_stream_multiturn_chunks(
    messages: list[dict[str, str]],
    *,
    temperature: Optional[float] = None,
) -> Iterator[tuple[StreamChunkKind, str]]:
    """多轮流式 Chat Completions。"""
    yield from _iter_stream_from_messages(messages, temperature=temperature)


def _merge_stream_parts(
    reasoning_parts: list[str],
    content_parts: list[str],
) -> tuple[str, str, Optional[str]]:
    """合并流式部分，返回 (raw_full, body_for_json, thinking)。"""
    reasoning = "".join(reasoning_parts).strip()
    raw_full = "".join(content_parts).strip()
    if reasoning:
        return raw_full, raw_full, reasoning
    parsed_think, remainder = extract_thinking_from_content(raw_full)
    body = remainder if parsed_think is not None else raw_full
    return raw_full, body, parsed_think


def merged_stream_parse_dual_sql(
    reasoning_parts: list[str],
    content_parts: list[str],
) -> tuple[str, str, str, Optional[str]]:
    """
    将流式累积的 reasoning / content 合并后解析双 SQL。
    返回 (assistant 正文 raw, numerator_sql, denominator_sql, thinking)。
    """
    raw_full, body, thinking = _merge_stream_parts(reasoning_parts, content_parts)
    num_sql, den_sql = parse_dual_sql_json(body)
    return raw_full, num_sql, den_sql, thinking


def merged_stream_parse_single_sql(
    reasoning_parts: list[str],
    content_parts: list[str],
) -> tuple[str, str, Optional[str]]:
    """流式解析单条 SQL，返回 (raw, sql, thinking)。"""
    raw_full, body, thinking = _merge_stream_parts(reasoning_parts, content_parts)
    sql = parse_single_sql_json(body)
    return raw_full, sql, thinking


def merged_stream_parse_analysis(
    reasoning_parts: list[str],
    content_parts: list[str],
) -> tuple[str, str, str, Optional[str]]:
    """流式解析分析型，返回 (raw, sql, analysis, thinking)。"""
    raw_full, body, thinking = _merge_stream_parts(reasoning_parts, content_parts)
    sql, analysis = parse_analysis_json(body)
    return raw_full, sql, analysis, thinking
