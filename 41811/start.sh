#!/bin/bash
# 41811 医疗监管系统 - 启动脚本 (macOS/Linux)
# 用法: ./start.sh
# 停止: ./stop.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo "41811 医疗监管系统 - 启动中..."
echo "========================================"

# 停止已有服务（避免端口冲突）
./stop.sh 2>/dev/null

# 启动 text2sql 服务（端口 8000）
echo ""
echo "[1/3] 启动 text2sql 服务 (端口 8000)..."
cd "$SCRIPT_DIR/backend_fastapi/Hainan_SQL-main/text2sql_app"
nohup python main.py > "$SCRIPT_DIR/logs/text2sql.log" 2>&1 &
echo "    text2sql 已启动，PID=$!"
echo "    日志: $SCRIPT_DIR/logs/text2sql.log"

# 等待服务启动
sleep 2

# 启动 backend FastAPI 服务（端口 8001）
echo ""
echo "[2/3] 启动 backend FastAPI 服务 (端口 8001)..."
cd "$SCRIPT_DIR/backend_fastapi"
nohup uvicorn main:app --host 0.0.0.0 --port 8001 > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
echo "    backend 已启动，PID=$!"
echo "    日志: $SCRIPT_DIR/logs/backend.log"

# 等待服务启动
sleep 2

# 启动前端 Vite 服务（端口 5173）
echo ""
echo "[3/3] 启动前端 Vite 服务 (端口 5173)..."
cd "$SCRIPT_DIR/my-vue-app"
nohup npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
echo "    前端已启动"
echo "    日志: $SCRIPT_DIR/logs/frontend.log"

# 等待前端启动
sleep 3

echo ""
echo "========================================"
echo "启动完成！"
echo "========================================"
echo "前端:    http://localhost:5173"
echo "后端:    http://localhost:8001"
echo "API文档: http://localhost:8001/docs"
echo "Text2SQL: http://localhost:8000"
echo ""
echo "查看日志: tail -f logs/*.log"
echo "停止服务: ./stop.sh"
echo "========================================"
