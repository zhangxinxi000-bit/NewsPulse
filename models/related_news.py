from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class RelatedNews(Base):
    """相关新闻关联表（推荐系统）：news_id 与 related_news_id 双向唯一。

    用于维护静态推荐关联；若表中无数据，相关推荐回退为
    同分类热门动态计算（见 crud/news.py get_related_news）。
    """

    __tablename__ = "related_news"
    __table_args__ = (UniqueConstraint("news_id", "related_news_id", name="news_related_unique"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="关联ID")
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True, comment="新闻ID")
    related_news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True, comment="相关新闻ID")

    def __repr__(self):
        return f"<RelatedNews(news_id={self.news_id}, related_news_id={self.related_news_id})>"
