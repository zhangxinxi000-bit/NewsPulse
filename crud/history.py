from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history(db: AsyncSession, user_id: int, news_id: int) -> History:
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.flush()
    await db.refresh(history)
    return history


async def get_history_list(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20):
    """浏览历史列表：关联新闻信息，按浏览时间倒序。"""
    stmt = (
        select(History, News)
        .join(News, News.id == History.news_id)
        .where(History.user_id == user_id)
        .order_by(History.id.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()  # list[(History, News)]


async def get_history_count(db: AsyncSession, user_id: int) -> int:
    stmt = select(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    return len(result.scalars().all())


async def get_history_by_id(db: AsyncSession, history_id: int) -> Optional[History]:
    return await db.get(History, history_id)


async def delete_history(db: AsyncSession, history: History) -> None:
    await db.delete(history)
    await db.commit()


async def clear_history(db: AsyncSession, user_id: int) -> int:
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
