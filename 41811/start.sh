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

# 解决 uvicorn 命令找不到的问题：找到系统中可用的 Python + uvicorn
PYTHON_BIN="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="$(which python3 2>/dev/null)"
fi
if [ -z "$PYTHON_BIN" ]; then
    echo "错误: 找不到 Python，请先安装 Python 3.9+"
    exit 1
fi

echo "使用 Python: $PYTHON_BIN"

# 启动 backend FastAPI 服务（端口 8001，已集成 Text2SQL）
echo ""
echo "[1/4] 启动 backend FastAPI 服务 (端口 8001)..."
cd "$SCRIPT_DIR/backend_fastapi"
nohup "$PYTHON_BIN" -m uvicorn main:app --host 0.0.0.0 --port 8001 > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo "    backend 已启动，PID=$BACKEND_PID"
echo "    日志: $SCRIPT_DIR/logs/backend.log"

# 等待服务启动
sleep 3

# 检查后端是否启动成功
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "    错误: backend 启动失败，查看日志: $SCRIPT_DIR/logs/backend.log"
    tail -20 "$SCRIPT_DIR/logs/backend.log"
fi

# 启动前端 Vite 服务（端口 5173）
echo ""
echo "[2/4] 启动前端 Vite 服务 (端口 5173)..."
cd "$SCRIPT_DIR/my-vue-app"
nohup npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "    前端已启动，PID=$FRONTEND_PID"
echo "    日志: $SCRIPT_DIR/logs/frontend.log"

# 等待前端启动
sleep 4

# 启动 Celery Worker（后台异步执行指标任务）
echo ""
echo "[3/4] 启动 Celery Worker (后台)..."
cd "$SCRIPT_DIR/backend_fastapi"
nohup "$PYTHON_BIN" -m celery -A app.celery_app worker --loglevel=info > "$SCRIPT_DIR/logs/celery.log" 2>&1 &
CELERY_PID=$!
echo "    Celery Worker 已启动，PID=$CELERY_PID"
echo "    日志: $SCRIPT_DIR/logs/celery.log"

# 等待 Worker 启动
sleep 2

# 检查 Redis 是否运行
echo ""
echo "[4/4] 检查 Redis 连接..."
redis_ok=$(redis-cli ping 2>/dev/null)
if [ "$redis_ok" = "PONG" ]; then
    echo "    Redis 运行正常"
else
    echo "    ⚠ Redis 未运行，请确保 Redis 已启动（brew services start redis 或 redis-server）"
fi

echo ""
echo "========================================"
echo "启动完成！"
echo "========================================"
echo "前端:    http://localhost:5173"
echo "后端:    http://localhost:8001"
echo "API文档: http://localhost:8001/docs"
echo "Redis:   localhost:6379"
echo ""
echo "查看日志: tail -f logs/*.log"
echo "停止服务: ./stop.sh"
echo "========================================"
