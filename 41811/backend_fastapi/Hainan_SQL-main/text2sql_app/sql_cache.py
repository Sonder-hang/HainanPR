"""指标+表结构 → 分子/分母 SQL 的进程内 LRU 缓存（跳过重复 LLM）。"""
from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from pathlib import Path
from threading import Lock
from typing import Any, Optional

from config import INDICATORS_JSON, SQL_CACHE_MAX_ENTRIES, SQL_CACHE_ENABLED, TABLES_JSON

_lock = Lock()
_store: OrderedDict[str, tuple[str, str]] = OrderedDict()


def _file_sig(p: Path) -> str:
    try:
        st = p.stat()
        return f"{st.st_mtime_ns}:{st.st_size}"
    except OSError:
        return "0:0"


def make_cache_key(
    indicator_index: int,
    table_names: list[str],
    indicator: dict[str, Any],
    schema_text: str,
) -> str:
    """配置或表文件变更会使 key 变化，从而自动失效。"""
    ind_min = {
        "指标名": indicator.get("指标名"),
        "指标计算公式": indicator.get("指标计算公式"),
        "补充信息": indicator.get("补充信息"),
        "涉及到表": indicator.get("涉及到表"),
    }
    payload = {
        "i": indicator_index,
        "tables": table_names,
        "indicator": ind_min,
        "schema": schema_text,
        "sig_tables": _file_sig(TABLES_JSON),
        "sig_ind": _file_sig(INDICATORS_JSON),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_sql_pair(key: str) -> Optional[tuple[str, str]]:
    if not SQL_CACHE_ENABLED:
        return None
    with _lock:
        if key in _store:
            _store.move_to_end(key)
            return _store[key]
    return None


def set_sql_pair(key: str, numerator_sql: str, denominator_sql: str) -> None:
    if not SQL_CACHE_ENABLED:
        return
    with _lock:
        _store[key] = (numerator_sql, denominator_sql)
        _store.move_to_end(key)
        while len(_store) > SQL_CACHE_MAX_ENTRIES:
            _store.popitem(last=False)


def invalidate(key: str) -> None:
    with _lock:
        _store.pop(key, None)
