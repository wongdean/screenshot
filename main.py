# main.py

import asyncio
import io
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from PIL import Image

# 初始化 FastAPI 应用
app = FastAPI(
    title="Playwright Screenshot Service",
    description="一个功能强大的截图 API 服务，支持全页、元素和区域截图。",
    version="1.3.0", # 版本又升级了
)

@app.on_event("startup")
async def startup_event():
    print("正在安装 Playwright 浏览器 (如果尚未安装)...")
    import sys
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "playwright", "install", "chromium",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await process.communicate()
    print("Playwright 浏览器准备就绪。")

@app.get("/")
async def root():
    return {
        "message": "欢迎使用 Playwright 截图服务!",
        "docs_url": "/docs",
        "usage_example": "/screenshot?url=[URL]&time_interval=1D&height_scale=0.75"
    }

@app.get("/screenshot",
    summary="获取网页截图",
    description="支持全页截图，可选择调整高度比例。"
)
async def take_screenshot(
    url: str,
    time_interval: str | None = None,    # 时间区间按钮文本
    height_scale: float = 1.0,           # 高度缩放比例，如0.7、0.75等
    wait_seconds: int = 3
):
    """
    接收请求，执行截图任务。

    参数:
    - **url**: 必须，要截图的目标网址。
    - **time_interval**: 可选，要点击的时间区间按钮的文本。
    - **height_scale**: 可选，高度缩放比例，默认1.0（如0.7表示截取高度的70%）。
    - **wait_seconds**: 可选，页面加载后等待的秒数。
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL 参数是必须的")

    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch()
            
            # 使用手机端配置避免弹窗，禁用缓存确保获取最新内容
            context = await browser.new_context(
                **p.devices['iPhone 14 Pro Max'],
                ignore_https_errors=True
            )
            page = await context.new_page()
            
            # 禁用缓存确保获取最新页面内容
            await page.route("**/*", lambda route: route.continue_(headers={**route.request.headers, "Cache-Control": "no-cache, no-store, must-revalidate"}))
            
            # 等待网络空闲确保动态内容加载完成
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # 点击时间间隔按钮（如果提供）
            if time_interval:
                try:
                    button_selector = f"button:has-text('{time_interval}')"
                    await page.locator(button_selector).first.click(timeout=10000)
                except PlaywrightTimeoutError:
                    raise HTTPException(status_code=404, detail=f"未找到文本为 '{time_interval}' 的按钮。")
            
            # 等待页面稳定，确保动态内容更新完成
            await asyncio.sleep(wait_seconds)
            
            # 额外等待网络请求完成，确保K线数据加载
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeoutError:
                pass  # 如果等待超时，继续截图

            # 全页截图
            full_screenshot_bytes = await page.screenshot(full_page=True)
            
            # 如果需要调整高度
            if height_scale != 1.0:
                image = Image.open(io.BytesIO(full_screenshot_bytes))
                width, height = image.size
                new_height = int(height * height_scale)
                
                # 从顶部裁剪到指定高度
                cropped_image = image.crop((0, 0, width, new_height))
                
                # 转换回bytes
                output = io.BytesIO()
                cropped_image.save(output, format='PNG')
                screenshot_bytes = output.getvalue()
                print(f"成功截取全页并调整高度: {height_scale}")
            else:
                screenshot_bytes = full_screenshot_bytes
                print("成功截取全页")

            await browser.close()
            return Response(content=screenshot_bytes, media_type="image/png")

        except Exception as e:
            if browser: await browser.close()
            # 重新抛出已知的HTTP异常，避免被下面的通用异常覆盖
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"截图时发生未知错误: {str(e)}")