from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from config.db_conf import get_db
from crud import news as news_crud
from crud import news_cache
from models.news import Category, News
from schemas.news import NewsDetailResponse, NewsItemBase

router = APIRouter(prefix="/api/news", tags=["新闻模块"])


@router.get("/categories", summary="获取新闻分类")
async def get_categories(skip: int = 0, limit: int = Query(100, le=200), db=Depends(get_db)):
    categories = await news_cache.get_categories(db, skip, limit)
    return {"code": 200, "message": "获取新闻分类成功", "data": categories}


@router.get("/list", summary="获取新闻列表（支持分类筛选与分页）")
async def get_news_list(
    category_id: Optional[int] = Query(default=None, alias="categoryId", description="分类ID，不传则返回全部"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize", description="每页数量"),
    db=Depends(get_db),
):
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    total = await news_crud.get_news_count(db, category_id)

    data = {
        "list": [NewsItemBase.model_validate(n) for n in news_list],
        "total": total,
        "hasMore": (offset + len(news_list)) < total,
    }
    return {"code": 200, "message": "获取新闻列表成功", "data": data}


@router.get("/detail", summary="获取新闻详情（浏览量+1，返回相关推荐）")
async def get_news_detail(news_id: int = Query(..., alias="id"), db=Depends(get_db)):
    news = await news_cache.get_news_detail(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 浏览量 +1（真实数据走数据库，不依赖缓存）
    await news_crud.increase_news_views(db, news.id)

    # 刷新当前详情缓存中的浏览量
    await news_cache.invalidate_news_detail_cache(news.id)

    related_news = await news_cache.get_related_news(db, news.id, news.category_id)
    news_detail = NewsDetailResponse.model_validate(news)

    data = news_detail.model_dump(mode="json")
    data["relatedNews"] = related_news
    return {"code": 200, "message": "获取新闻详情成功", "data": data}
