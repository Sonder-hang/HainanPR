"""MySQL 执行（只读场景）；自动建立 SSH 隧道连接服务器数据库。"""
import atexit
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any, Optional

import pymysql
from pymysql.cursors import DictCursor

from config import (
    MYSQL_CONNECT_TIMEOUT_SEC,
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_READ_TIMEOUT_SEC,
    MYSQL_USER,
    SSH_HOST,
    SSH_KEY_PATH,
    SSH_PASSWORD,
    SSH_PORT,
    SSH_REMOTE_BIND,
    SSH_TUNNEL_ENABLED,
    SSH_USER,
)

_tunnel = None
_tunnel_lock = Lock()


def _patch_paramiko():
    """修复 paramiko 3.x 移除 DSSKey 导致 sshtunnel 报错的兼容问题。"""
    import paramiko
    if not hasattr(paramiko, "DSSKey"):
        paramiko.DSSKey = type(None)


def _ensure_tunnel():
    """按需启动 SSH 隧道（进程级单例），返回 (host, port) 供 pymysql 使用。"""
    global _tunnel
    if not SSH_TUNNEL_ENABLED:
        return MYSQL_HOST, int(MYSQL_PORT)

    with _tunnel_lock:
        if _tunnel is not None and _tunnel.is_active:
            return "127.0.0.1", _tunnel.local_bind_port

        _patch_paramiko()
        from sshtunnel import SSHTunnelForwarder

        tunnel_kw: dict = {
            "ssh_username": SSH_USER,
            "remote_bind_address": SSH_REMOTE_BIND,
            "local_bind_address": ("127.0.0.1", 0),
            "set_keepalive": 30,
        }
        if (SSH_PASSWORD or "").strip():
            tunnel_kw["ssh_password"] = SSH_PASSWORD
        key_path = (SSH_KEY_PATH or "").strip()
        if key_path:
            tunnel_kw["ssh_pkey"] = os.path.expanduser(key_path)
        _tunnel = SSHTunnelForwarder((SSH_HOST, int(SSH_PORT)), **tunnel_kw)
        _tunnel.start()
        atexit.register(_shutdown_tunnel)
        print(f"[SSH 隧道] 已建立: 127.0.0.1:{_tunnel.local_bind_port} → {SSH_HOST}:{SSH_REMOTE_BIND[1]}")
        return "127.0.0.1", _tunnel.local_bind_port


def _shutdown_tunnel():
    global _tunnel
    if _tunnel is not None:
        try:
            _tunnel.stop()
        except Exception:
            pass
        _tunnel = None


def db_connect():
    host, port = _ensure_tunnel()
    return pymysql.connect(
        host=host,
        port=int(port),
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset="utf8mb4",
        cursorclass=DictCursor,
        connect_timeout=int(MYSQL_CONNECT_TIMEOUT_SEC),
        read_timeout=int(MYSQL_READ_TIMEOUT_SEC),
    )


def _clean_sql(sql: str) -> str:
    """去掉末尾空白和分号（可重复执行直到干净为止）。"""
    while True:
        stripped = sql.rstrip().rstrip(";").rstrip()
        if stripped == sql:
            break
        sql = stripped
    return sql


def execute_limited(
    sql: str,
    *,
    limit: int,
) -> tuple[list[str], list[dict[str, Any]], Optional[str]]:
    if not sql.strip():
        return [], [], "SQL 为空"
    sql = _clean_sql(sql)

    # 如果原 SQL 已有 LIMIT / OFFSET，会与外层 LIMIT 冲突，先去掉
    import re
    sql_no_limit = re.sub(r'\bLIMIT\s+[\d\s,+-]+\s*$', '', sql, flags=re.IGNORECASE).rstrip().rstrip(";").rstrip()
    sql_no_limit = _clean_sql(sql_no_limit)

    wrapped = f"SELECT _inner.* FROM ({sql_no_limit}) AS _inner LIMIT {int(limit)}"
    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(wrapped)
                rows = cur.fetchall()
                if not rows:
                    cols: list[str] = []
                else:
                    cols = list(rows[0].keys())
                return cols, list(rows), None
        finally:
            conn.close()
    except Exception as e:
        return [], [], str(e)


def execute_count(sql: str) -> tuple[Optional[int], Optional[str]]:
    if not sql.strip():
        return None, "SQL 为空"
    sql = _clean_sql(sql)
    import re
    sql_no_limit = re.sub(r'\bLIMIT\s+[\d\s,+-]+\s*$', '', sql, flags=re.IGNORECASE).rstrip().rstrip(";").rstrip()
    sql_no_limit = _clean_sql(sql_no_limit)
    wrapped = f"SELECT COUNT(*) AS cnt FROM ({sql_no_limit}) AS _cnt_sub"
    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(wrapped)
                row = cur.fetchone()
                if not row:
                    return 0, None
                return int(row.get("cnt", 0)), None
        finally:
            conn.close()
    except Exception as e:
        return None, str(e)


def execute_counts_parallel(
    sql_num: str,
    sql_den: str,
) -> tuple[
    tuple[Optional[int], Optional[str]],
    tuple[Optional[int], Optional[str]],
]:
    with ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(execute_count, sql_num)
        f2 = pool.submit(execute_count, sql_den)
        return f1.result(), f2.result()


def execute_limited_parallel(
    sql_num: str,
    sql_den: str,
    *,
    limit: int,
) -> tuple[
    tuple[list[str], list[dict[str, Any]], Optional[str]],
    tuple[list[str], list[dict[str, Any]], Optional[str]],
]:
    with ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(execute_limited, sql_num, limit=limit)
        f2 = pool.submit(execute_limited, sql_den, limit=limit)
        return f1.result(), f2.result()


# ---------------------------------------------------------------------------
# 全量执行（无 LIMIT）：用于真正导出全部数据到大几万行的真实场景
# ---------------------------------------------------------------------------

def execute_full(
    sql: str,
) -> tuple[list[str], list[dict[str, Any]], Optional[str]]:
    """不带 LIMIT，取全部数据。适合导出、报表等场景。"""
    if not sql.strip():
        return [], [], "SQL 为空"
    sql = _clean_sql(sql)

    try:
        conn = db_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                if not rows:
                    cols: list[str] = []
                else:
                    cols = list(rows[0].keys())
                return cols, list(rows), None
        finally:
            conn.close()
    except Exception as e:
        return [], [], str(e)


def execute_full_parallel(
    sql_num: str,
    sql_den: str,
) -> tuple[
    tuple[list[str], list[dict[str, Any]], Optional[str]],
    tuple[list[str], list[dict[str, Any]], Optional[str]],
]:
    """并行全量执行分子/分母 SQL，不加 LIMIT。"""
    with ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(execute_full, sql_num)
        f2 = pool.submit(execute_full, sql_den)
        return f1.result(), f2.result()
