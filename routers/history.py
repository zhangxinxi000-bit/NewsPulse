from fastapi import APIRouter, Depends, HTTPException, Query

from config.db_conf import get_db
from crud import history as history_crud
from crud import news as news_crud
from models.users import User
from schemas.history import HistoryAddRequest, HistoryResponse
from schemas.news import NewsItemBase
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["浏览历史模块"])


@router.post("/add", summary="添加浏览历史")
async def add_history(body: HistoryAddRequest, user: User = Depends(get_current_user), db=Depends(get_db)):
    news = await news_crud.get_news_detail(db, body.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")
    await history_crud.add_history(db, user.id, body.news_id)
    return success_response(message="记录成功")


@router.get("/list", summary="获取浏览历史列表")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    offset = (page - 1) * page_size
    rows = await history_crud.get_history_list(db, user.id, offset, page_size)
    total = await history_crud.get_history_count(db, user.id)

    data = {
        "list": [
            HistoryResponse(id=h.id, news=NewsItemBase.model_validate(news))
            for h, news in rows
        ],
        "total": total,
        "hasMore": (offset + len(rows)) < total,
    }
    return success_response(message="获取浏览历史列表成功", data=data)


@router.delete("/delete/{history_id}", summary="删除单条浏览历史")
async def delete_history(history_id: int, user: User = Depends(get_current_user), db=Depends(get_db)):
    history = await history_crud.get_history_by_id(db, history_id)
    if not history or history.user_id != user.id:
        raise HTTPException(status_code=404, detail="记录不存在")
    await history_crud.delete_history(db, history)
    return success_response(message="删除成功")


@router.delete("/clear", summary="清空浏览历史")
async def clear_history(user: User = Depends(get_current_user), db=Depends(get_db)):
    await history_crud.clear_history(db, user.id)
    return success_response(message="清空浏览历史成功")
