#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 MySQL 库 Hainan 提取表结构（含字段 COMMENT），写入 tables.json。
自动使用 text2sql_app/config.py 中的数据库和 SSH 隧道配置。
"""

import json
import os
from typing import Any, Optional, Tuple

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
    TABLES_JSON,
)

OUTPUT_JSON = str(TABLES_JSON)


def _patch_paramiko():
    """修复 paramiko 3.x 移除 DSSKey 导致 sshtunnel 报错的兼容问题。"""
    import paramiko
    if not hasattr(paramiko, "DSSKey"):
        paramiko.DSSKey = type(None)


def _connect():
    import pymysql

    if SSH_TUNNEL_ENABLED:
        _patch_paramiko()
        from sshtunnel import SSHTunnelForwarder

        tunnel_kw: dict = {
            "ssh_username": SSH_USER,
            "remote_bind_address": SSH_REMOTE_BIND,
            "local_bind_address": ("127.0.0.1",),
        }
        if (SSH_PASSWORD or "").strip():
            tunnel_kw["ssh_password"] = SSH_PASSWORD
        key_path = (SSH_KEY_PATH or "").strip()
        if key_path:
            tunnel_kw["ssh_pkey"] = os.path.expanduser(key_path)
        tunnel = SSHTunnelForwarder((SSH_HOST, int(SSH_PORT)), **tunnel_kw)
        tunnel.start()
        conn = pymysql.connect(
            host="127.0.0.1",
            port=tunnel.local_bind_port,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=int(MYSQL_CONNECT_TIMEOUT_SEC),
            read_timeout=int(MYSQL_READ_TIMEOUT_SEC),
        )
        conn._ssh_tunnel = tunnel
        return conn
    else:
        return pymysql.connect(
            host=MYSQL_HOST,
            port=int(MYSQL_PORT),
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=int(MYSQL_CONNECT_TIMEOUT_SEC),
            read_timeout=int(MYSQL_READ_TIMEOUT_SEC),
        )


def fetch_table_comments(conn) -> dict[str, str]:
    sql = """
        SELECT TABLE_NAME, TABLE_COMMENT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
    """
    with conn.cursor() as cur:
        cur.execute(sql, (MYSQL_DATABASE,))
        return {r["TABLE_NAME"]: (r["TABLE_COMMENT"] or "").strip() for r in cur.fetchall()}


def fetch_columns(conn) -> list[dict[str, Any]]:
    sql = """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            ORDINAL_POSITION,
            COLUMN_TYPE,
            COLUMN_COMMENT,
            COLUMN_KEY,
            IS_NULLABLE,
            EXTRA,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    with conn.cursor() as cur:
        cur.execute(sql, (MYSQL_DATABASE,))
        return list(cur.fetchall())


def fetch_foreign_keys(conn) -> dict[tuple[str, str], tuple[str, str]]:
    sql = """
        SELECT
            k.TABLE_NAME,
            k.COLUMN_NAME,
            k.REFERENCED_TABLE_NAME,
            k.REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
        INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS t
            ON k.CONSTRAINT_SCHEMA = t.CONSTRAINT_SCHEMA
            AND k.TABLE_NAME = t.TABLE_NAME
            AND k.CONSTRAINT_NAME = t.CONSTRAINT_NAME
        WHERE k.TABLE_SCHEMA = %s
          AND t.CONSTRAINT_TYPE = 'FOREIGN KEY'
          AND k.REFERENCED_TABLE_NAME IS NOT NULL
    """
    with conn.cursor() as cur:
        cur.execute(sql, (MYSQL_DATABASE,))
        out: dict[tuple[str, str], tuple[str, str]] = {}
        for r in cur.fetchall():
            out[(r["TABLE_NAME"], r["COLUMN_NAME"])] = (
                r["REFERENCED_TABLE_NAME"],
                r["REFERENCED_COLUMN_NAME"],
            )
        return out


def build_constraint_note(col: dict[str, Any], fk: Optional[Tuple[str, str]]) -> str:
    parts: list[str] = []
    if col["COLUMN_KEY"] == "PRI":
        parts.append("主键 PK")
    if col["COLUMN_KEY"] == "UNI":
        parts.append("唯一 UK")
    if fk:
        parts.append(f"外键 FK：对应 {fk[0]}.{fk[1]}")
    if col["IS_NULLABLE"] == "NO" and col["COLUMN_KEY"] != "PRI":
        parts.append("非空")
    if col.get("EXTRA") == "auto_increment":
        parts.append("自增")
    if not parts:
        return ""
    return "；".join(parts)


def split_comment_meaning_and_extra(comment: str) -> tuple[str, str]:
    c = (comment or "").strip()
    return c, ""


def default_business_definition(table_name: str, table_comment: str) -> str:
    if table_comment:
        return table_comment
    return f"业务表 {table_name}（请根据监管场景补充一句话业务定义）"


def default_granularity(table_name: str) -> str:
    return f"每行代表 {table_name} 的一条记录（请按实际业务改为如：单条医嘱、单个科室规则）"


def format_field_line(name: str, col_type: str, meaning_cn: str, constraint: str) -> str:
    constraint = constraint.strip()
    if constraint:
        return f"- {name} [{col_type}]: {meaning_cn} ({constraint})"
    return f"- {name} [{col_type}]: {meaning_cn}"


def build_formatted_block(rec: dict[str, Any]) -> str:
    lines = [
        f"表名：{rec['表名']}",
        f"业务定义：{rec['业务定义']}",
        f"数据粒度：{rec['数据粒度']}",
        "",
        "字段列表：",
    ]
    for f in rec["字段列表"]:
        lines.append(
            format_field_line(f["字段名"], f["数据类型"], f["中文含义"], f.get("约束说明") or "")
        )
    lines.append("")
    lines.append("注意事项：")
    note = rec.get("注意事项") or "请根据业务补充过滤逻辑或特殊计算要求。"
    if isinstance(note, list):
        for n in note:
            lines.append(f"- {n}")
    else:
        lines.append(f"- {note}")
    return "\n".join(lines)


def main() -> None:
    conn = _connect()
    tunnel = getattr(conn, "_ssh_tunnel", None)
    try:
        table_comments = fetch_table_comments(conn)
        columns = fetch_columns(conn)
        fks = fetch_foreign_keys(conn)

        by_table: dict[str, list[dict[str, Any]]] = {}
        for c in columns:
            by_table.setdefault(c["TABLE_NAME"], []).append(c)

        tables_out: list[dict[str, Any]] = []
        for table_name in sorted(by_table.keys()):
            cols = by_table[table_name]
            t_comment = table_comments.get(table_name, "")

            field_rows: list[dict[str, Any]] = []
            for col in cols:
                fk = fks.get((table_name, col["COLUMN_NAME"]))
                meaning, _ = split_comment_meaning_and_extra(col["COLUMN_COMMENT"] or "")
                if not meaning:
                    meaning = col["COLUMN_NAME"]
                constraint = build_constraint_note(col, fk)
                field_rows.append({
                    "字段名": col["COLUMN_NAME"],
                    "数据类型": col["COLUMN_TYPE"],
                    "中文含义": meaning,
                    "约束说明": constraint,
                })

            rec = {
                "表名": table_name,
                "业务定义": default_business_definition(table_name, t_comment),
                "数据粒度": default_granularity(table_name),
                "字段列表": field_rows,
                "注意事项": "请根据业务补充过滤逻辑或特殊计算要求。",
                "formatted_text": "",
            }
            rec["formatted_text"] = build_formatted_block(rec)
            tables_out.append(rec)

        payload = {
            "database": MYSQL_DATABASE,
            "charset": "utf8mb4",
            "tables": tables_out,
        }

        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        print(f"已写入: {OUTPUT_JSON}，共 {len(tables_out)} 张表")
    finally:
        conn.close()
        if tunnel:
            tunnel.stop()


if __name__ == "__main__":
    main()
