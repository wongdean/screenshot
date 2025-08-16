FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 安装Playwright浏览器
RUN playwright install chromium

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# 暴露端口
EXPOSE $PORT

# 启动应用
CMD ["sh", "start.sh"]