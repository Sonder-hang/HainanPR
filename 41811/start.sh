#!/bin/bash
# 41811 医疗监管系统 - 启动脚本
# 停止: kill $(pgrep -f "uvicorn main:app") $(pgrep -f "python run.py") && npm run dev --prefix my-vue-app

cd /home/ubuntu/41811_fullstack/41811

# 后台启动 text2sql 服务（端口 8000）
cd backend_fastapi/Hainan_SQL-main/text2sql_app
nohup python run.py > /tmp/text2sql.log 2>&1 &
echo "text2sql 已在后台启动，PID=$!"

# 等待 text2sql 服务就绪
sleep 3

# 后台启动 main backend（端口 8001）
cd /home/ubuntu/41811_fullstack/41811/backend_fastapi
nohup uvicorn main:app --host 0.0.0.0 --port 8001 --app-dir . > /tmp/backend.log 2>&1 &
echo "main backend 已在后台启动，PID=$!"

# 前台启动前端（保持运行）
cd /home/ubuntu/41811_fullstack/41811/my-vue-app
npm run dev