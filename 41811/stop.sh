#!/bin/bash
# ============================================================
# 41811 医疗监管系统 - 停止所有服务
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo "========================================"
echo "   41811 医疗监管系统 - 停止所有服务"
echo "========================================"
echo ""

kill_by_pidfile() {
    local name=$1
    local pidfile="$LOG_DIR/${name}.pid"
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            sleep 1
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
            echo -e "${GREEN}[停止]${NC} $name (PID $pid)"
        else
            echo -e "${RED}[跳过]${NC} $name - 进程不存在"
        fi
        rm -f "$pidfile"
    else
        echo -e "${RED}[跳过]${NC} $name - 无 PID 文件"
    fi
}

kill_by_port() {
    local port=$1
    local name=$2
    local killed=0

    # 尝试多种匹配方式
    for pattern in \
        "0.0.0.0:$port" \
        "127.0.0.1:$port" \
        ":$port"; do

        while IFS= read -r line; do
            local pid=$(echo "$line" | grep -oP 'pid=\K[0-9]+' || echo "")
            [ -z "$pid" ] && continue

            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null
                sleep 1
                [ kill -0 "$pid" 2>/dev/null ] && kill -9 "$pid" 2>/dev/null
                echo -e "${GREEN}[停止]${NC} $name (端口 $port, PID $pid)"
                killed=1
            fi
        done < <(ss -tlnp 2>/dev/null | grep "$pattern" || true)
    done

    [ "$killed" -eq 0 ] && echo -e "${RED}[跳过]${NC} $name (端口 $port) - 未被占用"
}

kill_by_pidfile "text2sql_app"
kill_by_pidfile "backend_fastapi"
kill_by_pidfile "my-vue-app"

# 兜底：PID 文件丢失时按端口清理
kill_by_port 8000 "text2sql_app"
kill_by_port 8001 "backend_fastapi"
kill_by_port 5173 "my-vue-app"

# 清理
rm -f "$LOG_DIR"/*.pid "$LOG_DIR"/startup_info.txt
rm -rf "$SCRIPT_DIR/.venv"

echo ""
echo "========================================"
echo "   所有服务已停止"
echo "========================================"
echo ""
