from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News
from models.related_news import RelatedNews


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
    stmt = select(Category).order_by(Category.sort_order.asc(), Category.id.asc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_news_list(db: AsyncSession, category_id: Optional[int], skip: int = 0, limit: int = 10) -> list[News]:
    stmt = select(News)
    if category_id is not None:
        stmt = stmt.where(News.category_id == category_id)
    stmt = stmt.order_by(News.publish_time.desc(), News.id.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_news_count(db: AsyncSession, category_id: Optional[int]) -> int:
    stmt = select(func.count(News.id))
    if category_id is not None:
        stmt = stmt.where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_news_detail(db: AsyncSession, news_id: int) -> Optional[News]:
    return await db.get(News, news_id)


async def increase_news_views(db: AsyncSession, news_id: int) -> bool:
    """浏览量 +1，返回是否更新成功。"""
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5) -> list[News]:
    """相关推荐：优先使用 related_news 关联表，无数据时回退为同分类热门动态计算。"""
    # 1. related_news 静态关联表（人工维护的推荐位）
    stmt = (
        select(News)
        .join(RelatedNews, RelatedNews.related_news_id == News.id)
        .where(RelatedNews.news_id == news_id)
        .order_by(News.views.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    related = list(result.scalars().all())
    if related:
        return related

    # 2. 回退方案：同分类下按浏览量和发布时间排序
    stmt = (
        select(News)
        .where(News.category_id == category_id, News.id != news_id)
        .order_by(News.views.desc(), News.publish_time.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
