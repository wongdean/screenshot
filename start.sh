#!/bin/bash

# 启动脚本
echo "正在启动 Playwright 截图服务..."

# 设置环境变量
export PYTHONUNBUFFERED=1
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}

# 启动服务
uvicorn main:app --host $HOST --port $PORT --workers 1