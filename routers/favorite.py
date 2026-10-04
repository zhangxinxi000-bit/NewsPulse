from fastapi import APIRouter, Depends, HTTPException, Query

from config.db_conf import get_db
from crud import favorite as favorite_crud
from crud import news as news_crud
from models.users import User
from schemas.favorite import FavoriteAddRequest, FavoriteResponse
from schemas.news import NewsItemBase
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["收藏模块"])


@router.get("/check", summary="检查新闻收藏状态")
async def check_favorite(news_id: int = Query(..., alias="newsId"), user: User = Depends(get_current_user), db=Depends(get_db)):
    favorite = await favorite_crud.get_favorite(db, user.id, news_id)
    return success_response(message="查询成功", data={"isFavorite": favorite is not None})


@router.post("/add", summary="添加收藏")
async def add_favorite(body: FavoriteAddRequest, user: User = Depends(get_current_user), db=Depends(get_db)):
    news = await news_crud.get_news_detail(db, body.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")
    if await favorite_crud.get_favorite(db, user.id, body.news_id):
        raise HTTPException(status_code=400, detail="该新闻已在收藏中")

    await favorite_crud.add_favorite(db, user.id, body.news_id)
    return success_response(message="收藏成功")


@router.delete("/remove", summary="取消收藏")
async def remove_favorite(news_id: int = Query(..., alias="newsId"), user: User = Depends(get_current_user), db=Depends(get_db)):
    ok = await favorite_crud.remove_favorite(db, user.id, news_id)
    if not ok:
        raise HTTPException(status_code=400, detail="该新闻未收藏")
    return success_response(message="取消收藏成功")


@router.get("/list", summary="获取收藏列表")
async def get_favorite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    offset = (page - 1) * page_size
    rows = await favorite_crud.get_favorite_list(db, user.id, offset, page_size)
    total = await favorite_crud.get_favorite_count(db, user.id)

    data = {
        "list": [
            FavoriteResponse(id=fav.id, news=NewsItemBase.model_validate(news))
            for fav, news in rows
        ],
        "total": total,
        "hasMore": (offset + len(rows)) < total,
    }
    return success_response(message="获取收藏列表成功", data=data)


@router.delete("/clear", summary="清空收藏")
async def clear_favorites(user: User = Depends(get_current_user), db=Depends(get_db)):
    await favorite_crud.clear_favorites(db, user.id)
    return success_response(message="清空收藏成功")
