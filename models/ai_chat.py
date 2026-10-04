from typing import Optional

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class AiChat(Base):
    """AI 聊天记录表。

    user_id 允许为空：未登录用户也可使用 AI 问答（不记录归属）；
    登录用户问答时自动写入 user_id，可通过 GET /api/ai/history 查询。
    """

    __tablename__ = "ai_chat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="聊天记录ID")
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id"), nullable=True, index=True, comment="用户ID（可空，匿名问答不记录归属）"
    )
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="用户消息")
    response: Mapped[str] = mapped_column(Text, nullable=False, comment="AI回复")

    def __repr__(self):
        return f"<AiChat(id={self.id}, user_id={self.user_id})>"
