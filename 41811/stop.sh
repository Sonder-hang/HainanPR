#!/bin/bash
# 41811 医疗监管系统 - 停止脚本 (macOS/Linux)
# 用法: ./stop.sh

echo "========================================"
echo "41811 医疗监管系统 - 停止中..."
echo "========================================"

# 停止 text2sql 服务
echo "停止 text2sql 服务..."
pkill -f "python.*main.py" 2>/dev/null && echo "  ✓ text2sql 已停止" || echo "  - text2sql 未运行"

# 停止 backend FastAPI 服务
echo "停止 backend 服务..."
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "  ✓ backend 已停止" || echo "  - backend 未运行"

# 停止前端 Vite 服务
echo "停止前端服务..."
pkill -f "vite" 2>/dev/null && echo "  ✓ 前端 已停止" || echo "  - 前端 未运行"
pkill -f "node.*vite" 2>/dev/null && echo "  ✓ 前端 已停止" || echo "  - 前端 未运行"

echo ""
echo "========================================"
echo "所有服务已停止"
echo "========================================"
