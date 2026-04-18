"""应用入口：组装所有组件"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.config import settings

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="工程化重构的宠物护理知识库系统"
)

# 注册路由
app.include_router(router)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")