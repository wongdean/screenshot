# Playwright 截图服务

一个基于 FastAPI 和 Playwright 的网页截图服务。

## 功能特性

- 支持全页截图
- 可调整截图高度比例
- 支持时间间隔按钮点击
- 使用手机端 UA 避免弹窗

## API 接口

### GET /screenshot

参数：
- `url` (必须): 目标网址
- `time_interval` (可选): 时间区间按钮文本，如 "1D", "7D"
- `height_scale` (可选): 高度缩放比例，默认 1.0，如 0.7, 0.75
- `wait_seconds` (可选): 等待时间，默认 3 秒

示例：
```
/screenshot?url=https://example.com&time_interval=1D&height_scale=0.75
```

## 部署到 Zeabur

1. 将代码推送到 GitHub 仓库
2. 在 Zeabur 控制台中选择 "Deploy from GitHub"
3. 选择你的仓库
4. Zeabur 会自动检测 Dockerfile 并开始构建
5. 部署完成后即可使用

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 启动服务
uvicorn main:app --reload
```

访问 http://localhost:8000 查看 API 文档。