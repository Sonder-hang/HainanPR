#!/usr/bin/env python3
"""
测试 MySQL 连接（自动使用 config.py 中的配置，含 SSH 隧道）。
用法：python test_mysql_connection.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))

from sql_runner import db_connect
from config import (
    MYSQL_DATABASE,
    MYSQL_USER,
    SSH_HOST,
    SSH_TUNNEL_ENABLED,
    SSH_USER,
)


def main() -> int:
    if SSH_TUNNEL_ENABLED:
        print(
            f"通过 SSH 隧道：跳板 {SSH_HOST}（SSH 用户: {SSH_USER}）"
            f" → MySQL 库 {MYSQL_DATABASE}（MySQL 用户: {MYSQL_USER}）"
        )
    else:
        print(f"直连 MySQL 库 {MYSQL_DATABASE}（MySQL 用户: {MYSQL_USER}）")

    try:
        conn = db_connect()
    except Exception as e:
        print(f"连接失败: {type(e).__name__}: {e}")
        return 1

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok, DATABASE() AS db, VERSION() AS version")
            row = cur.fetchone()
        print("连接成功。")
        print(f"  SELECT 1 / 当前库 / 版本: {row}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
