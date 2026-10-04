from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class History(Base):
    """用户浏览历史记录。"""

    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="历史记录ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True, comment="用户ID")
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True, comment="新闻ID")

    def __repr__(self):
        return f"<History(user_id={self.user_id}, news_id={self.news_id})>"
