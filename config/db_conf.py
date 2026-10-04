from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库连接地址
# 默认使用 SQLite（开箱即用，无需安装数据库）
# 如需切换 MySQL：安装 aiomysql 后改为
#   ASYNC_DATABASE_URL = "mysql+aiomysql://root:密码@localhost:3306/news_app?charset=utf8mb4"
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,          # 开发时可改为 True 输出 SQL 日志
    pool_pre_ping=True,  # 连接前检查，避免使用失效连接
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 依赖项：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
