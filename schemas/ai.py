from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """AI 问答请求。"""

    question: str = Field(min_length=1, max_length=2000, description="用户问题")


class ChatHistoryItem(BaseModel):
    """AI 聊天历史记录（单条）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    response: str
    created_at: Optional[datetime] = None
