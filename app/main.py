# -*- coding: utf-8 -*-
"""FastAPI 入口"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import API_HOST, API_PORT, LOG_LEVEL
from app.core.database import db
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.router_factory import RouterFactory, LOTTERY_CONFIGS

# 日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化，关闭时清理"""
    logger.info("=" * 50)
    logger.info("[App] 彩票数据统计与可视化系统 启动中...")
    # 初始化数据库
    db.init_database()
    # 启动定时采集
    start_scheduler()
    logger.info(f"[App] 服务就绪: http://{API_HOST}:{API_PORT}")
    logger.info("=" * 50)
    yield
    # 关闭
    stop_scheduler()
    logger.info("[App] 服务已停止")


app = FastAPI(
    title="彩票数据统计与可视化系统",
    description="5 类彩票数据爬取、清洗、存储、统计、可视化",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS（允许前端跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 5 个子路由（RouterFactory 自动生成）
for cfg in LOTTERY_CONFIGS:
    app.include_router(RouterFactory.build(cfg))

# 挂载前端静态文件
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/")
def root():
    return RedirectResponse(url="/frontend/index.html")


@app.get("/api/health")
def health():
    return {"code": 200, "message": "ok", "data": {"status": "running"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)
