from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


async def get_favorite(db: AsyncSession, user_id: int, news_id: int) -> Optional[Favorite]:
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_favorite(db: AsyncSession, user_id: int, news_id: int) -> Favorite:
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.flush()
    await db.refresh(favorite)
    return favorite


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_favorite_list(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20):
    """收藏列表：关联新闻信息，按收藏时间倒序。"""
    stmt = (
        select(Favorite, News)
        .join(News, News.id == Favorite.news_id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.id.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()  # list[(Favorite, News)]


async def get_favorite_count(db: AsyncSession, user_id: int) -> int:
    stmt = select(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    return len(result.scalars().all())


async def clear_favorites(db: AsyncSession, user_id: int) -> int:
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
