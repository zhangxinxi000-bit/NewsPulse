"""数据库迁移脚本：把 demo 表结构对齐课程 database.sql（幂等，可重复执行）。

做的事情：
1. create_all 建缺失的新表：related_news（新闻关联）、ai_chat（AI 聊天记录）
2. user 表补充 gender / phone 列（SQLite ALTER TABLE ADD COLUMN）
3. 导入课程测试账号 admin（密码重置为 admin123，bcrypt 加密），已存在则跳过

用法：
    .venv\\Scripts\\python scripts\\migrate_db.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text  # noqa: E402

from config.db_conf import AsyncSessionLocal, async_engine  # noqa: E402
from models import Base  # noqa: E402
from models.users import User  # noqa: E402
from utils.security import get_hash_password  # noqa: E402


async def column_exists(conn, table: str, column: str) -> bool:
    result = await conn.execute(text(f"PRAGMA table_info({table})"))
    cols = [row[1] for row in result.fetchall()]
    return column in cols


async def migrate():
    # 1. 建新表（related_news / ai_chat）
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("建表完成（related_news / ai_chat 已就绪）")

    # 2. user 表加列
    async with async_engine.begin() as conn:
        if not await column_exists(conn, "user", "gender"):
            await conn.execute(
                text("ALTER TABLE user ADD COLUMN gender VARCHAR(10) NOT NULL DEFAULT 'unknown'")
            )
            print("user 表新增列 gender")
        else:
            print("user 表已有 gender 列，跳过")

        if not await column_exists(conn, "user", "phone"):
            await conn.execute(text("ALTER TABLE user ADD COLUMN phone VARCHAR(20)"))
            print("user 表新增列 phone")
        else:
            print("user 表已有 phone 列，跳过")

    # 3. 导入课程测试账号 admin（密码 admin123）
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        exists = (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
        if exists:
            print("admin 账号已存在，跳过")
        else:
            db.add(
                User(
                    username="admin",
                    email="admin@demo.com",
                    hashed_password=get_hash_password("admin123"),
                    nickname="测试用户",
                    gender="unknown",
                    bio="这是一个测试账号",
                )
            )
            await db.commit()
            print("已创建 admin 测试账号（用户名 admin，密码 admin123）")

    print("迁移完成")


if __name__ == "__main__":
    asyncio.run(migrate())
