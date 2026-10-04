from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Favorite(Base):
    """用户收藏记录（一个用户对一条新闻只能收藏一次）。"""

    __tablename__ = "favorite"
    __table_args__ = (UniqueConstraint("user_id", "news_id", name="uq_user_news"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True, comment="用户ID")
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True, comment="新闻ID")

    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, news_id={self.news_id})>"
