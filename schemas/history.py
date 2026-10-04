from pydantic import BaseModel, Field

from schemas.news import NewsItemBase


class HistoryAddRequest(BaseModel):
    """添加浏览历史请求。"""

    news_id: int = Field(gt=0, description="新闻ID")


class HistoryResponse(BaseModel):
    """浏览历史响应（含新闻摘要）。"""

    id: int
    news: NewsItemBase
