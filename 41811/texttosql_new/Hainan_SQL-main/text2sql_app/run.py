#!/usr/bin/env python3
"""一键启动 Text-to-SQL 服务。在 text2sql_app 目录下运行: python run.py"""
import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("  Text-to-SQL 指标调试服务")
    print("  打开浏览器: http://127.0.0.1:8000")
    print("  日志页面:   http://127.0.0.1:8000/log")
    print("=" * 50)
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload=True)
