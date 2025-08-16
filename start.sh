#!/bin/bash

# 启动脚本
echo "正在启动 Playwright 截图服务..."

# 设置环境变量
export PYTHONUNBUFFERED=1
export HOST=${HOST:-0.0.0.0}
export PORT=${WEB_PORT:-${PORT:-8000}}
export TZ=${TZ:-Asia/Shanghai}

# 显示当前时区信息
echo "当前时区: $(date '+%Z %z')"
echo "当前时间: $(date)"

# 启动服务
uvicorn main:app --host $HOST --port $PORT --workers 1