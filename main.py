from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.db_conf import async_engine
from models import Base
from routers import ai, favorite, history, news, users
from utils.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时自动建表（演示用；生产环境建议改用 Alembic 迁移）。"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="FastAPI Demo · AI掘金头条",
    description="基于 FastAPI + SQLAlchemy 异步 ORM 的新闻系统 Demo：用户认证、新闻浏览、收藏、浏览历史、Redis 缓存、AI 问答。",
    version="1.0.0",
    lifespan=lifespan,
)

# 注册全局异常处理器：所有错误统一返回 {code, message, data}
register_exception_handlers(app)

# 跨域配置：开发阶段允许所有来源，生产环境请指定具体源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载各业务模块路由
app.include_router(users.router)
app.include_router(news.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)


@app.get("/", summary="服务健康检查")
async def root():
    return {"message": "FastAPI Demo is running", "docs": "/docs"}
