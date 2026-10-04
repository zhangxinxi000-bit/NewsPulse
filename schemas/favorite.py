from pydantic import BaseModel, Field

from schemas.news import NewsItemBase


class FavoriteAddRequest(BaseModel):
    """添加收藏请求。"""

    news_id: int = Field(gt=0, description="新闻ID")


class FavoriteResponse(BaseModel):
    """收藏记录响应（含新闻摘要）。"""

    id: int
    news: NewsItemBase
