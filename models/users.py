from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="加密密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL")
    gender: Mapped[str] = mapped_column(String(10), default="unknown", nullable=False, comment="性别 male/female/unknown")
    bio: Mapped[Optional[str]] = mapped_column(String(200), comment="个人简介")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, comment="手机号")

    tokens: Mapped[list["UserToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class UserToken(Base):
    """用户认证令牌：登录/注册后生成，7 天有效。"""

    __tablename__ = "user_token"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="令牌ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True, comment="用户ID")
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")

    user: Mapped["User"] = relationship(back_populates="tokens")

    def __repr__(self):
        return f"<UserToken(user_id={self.user_id}, expires_at={self.expires_at})>"
