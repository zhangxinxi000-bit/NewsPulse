from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CategoryResponse(BaseModel):
    """新闻分类响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int


class NewsItemBase(BaseModel):
    """新闻列表项（不含正文，减小列表载荷）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int
    views: int
    publish_time: Optional[datetime] = None


class RelatedNewsResponse(BaseModel):
    """相关推荐新闻。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    views: int


class NewsDetailResponse(BaseModel):
    """新闻详情响应（含正文）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    content: str
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int
    views: int
    publish_time: Optional[datetime] = None


class NewsListData(BaseModel):
    """新闻列表分页数据。"""

    list: List[NewsItemBase]
    total: int
    has_more: bool
