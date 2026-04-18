"""应用入口：组装所有组件"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os
from app.api.routes import router
from app.config import settings

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="工程化重构的宠物护理知识库系统"
)

# 注册API路由
app.include_router(router)

# 静态文件挂载
app.mount("/static", StaticFiles(directory="static"), name="static")

# 根路径直接返回 index.html（适配 Hugging Face）
@app.get("/", response_class=HTMLResponse)
def root():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return {
        "message": f"{settings.app_name} 运行中",
        "docs": "/docs",
        "web": "/static/index.html"
    }
