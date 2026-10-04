"""新闻读取的缓存逻辑（Cache-Aside 旁路策略）。

读取流程：先查 Redis → 命中直接返回；未命中查 MySQL → 回填缓存 → 返回。
写入/更新数据后：删除相关缓存，保证下次读取拿到最新数据。
Redis 不可用时自动降级为直查数据库。
"""
from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from config.cache_conf import (
    EXPIRE_CATEGORIES,
    EXPIRE_NEWS_DETAIL,
    EXPIRE_NEWS_LIST,
    EXPIRE_RELATED_NEWS,
    delete_cache_by_pattern,
    get_json_cache,
    set_cache,
)
from crud import news as news_crud
from models.news import Category, News
from schemas.news import NewsDetailResponse, NewsItemBase

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"
NEWS_DETAIL_PREFIX = "news:detail:"
RELATED_NEWS_PREFIX = "news:related:"


# ---------- 分类 ----------
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    cached = await get_json_cache(CATEGORIES_KEY)
    if cached:
        return cached

    categories = await news_crud.get_categories(db, skip, limit)
    if categories:
        await set_cache(CATEGORIES_KEY, jsonable_encoder(categories), EXPIRE_CATEGORIES)
    return categories


# ---------- 新闻列表 ----------
async def get_news_list(db: AsyncSession, category_id: Optional[int], skip: int = 0, limit: int = 10):
    # 页码 = 跳过的数量 // 每页数量 + 1
    page = skip // limit + 1
    key = _news_list_key(category_id, page, limit)

    cached = await get_json_cache(key)
    if cached:
        return [News(**item) for item in cached]

    news_list = await news_crud.get_news_list(db, category_id, skip, limit)
    if news_list:
        # ORM → Pydantic → 字典，写入缓存（by_alias=False 保持 Python 风格字段）
        data = [NewsItemBase.model_validate(n).model_dump(mode="json", by_alias=False) for n in news_list]
        await set_cache(key, data, EXPIRE_NEWS_LIST)
    return news_list


def _news_list_key(category_id: Optional[int], page: int, size: int) -> str:
    category_part = category_id if category_id is not None else "all"
    return f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"


async def invalidate_news_list_cache(category_id: Optional[int] = None):
    """数据更新后失效新闻列表缓存：精确失效或按前缀批量失效。"""
    if category_id is not None:
        await delete_cache_by_pattern(f"{NEWS_LIST_PREFIX}{category_id}:*")
    else:
        await delete_cache_by_pattern(f"{NEWS_LIST_PREFIX}*")


# ---------- 新闻详情 ----------
async def get_news_detail(db: AsyncSession, news_id: int):
    cached = await get_json_cache(f"{NEWS_DETAIL_PREFIX}{news_id}")
    if cached:
        return News(**cached)

    news = await news_crud.get_news_detail(db, news_id)
    if news:
        # 缓存数据需覆盖 News 的全部字段，才能用 News(**cached) 还原
        detail_data = NewsDetailResponse.model_validate(news).model_dump(mode="json", by_alias=False)
        await set_cache(f"{NEWS_DETAIL_PREFIX}{news_id}", detail_data, EXPIRE_NEWS_DETAIL)
    return news


async def invalidate_news_detail_cache(news_id: int):
    from config.cache_conf import delete_cache

    await delete_cache(f"{NEWS_DETAIL_PREFIX}{news_id}")


# ---------- 相关推荐 ----------
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    cached = await get_json_cache(key)
    if cached:
        return cached

    related = await news_crud.get_related_news(db, news_id, category_id, limit)
    data = [NewsItemBase.model_validate(n).model_dump(mode="json", by_alias=False) for n in related]
    await set_cache(key, data, EXPIRE_RELATED_NEWS)
    return data
