from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """注册请求（nickname/gender/bio/phone 可选）。"""

    username: str = Field(min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(description="邮箱")
    password: str = Field(min_length=6, max_length=100, description="密码")
    nickname: Optional[str] = Field(default=None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像URL")
    gender: Optional[Literal["male", "female", "unknown"]] = Field(default=None, description="性别")
    bio: Optional[str] = Field(default=None, max_length=200, description="个人简介")
    phone: Optional[str] = Field(default=None, max_length=20, pattern=r"^\+?\d{5,20}$", description="手机号")


class UserUpdate(BaseModel):
    """更新用户信息请求（部分字段可选）。"""

    nickname: Optional[str] = Field(default=None, max_length=50, description="昵称")
    bio: Optional[str] = Field(default=None, max_length=200, description="个人简介")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像URL")
    gender: Optional[Literal["male", "female", "unknown"]] = Field(default=None, description="性别")
    phone: Optional[str] = Field(default=None, max_length=20, pattern=r"^\+?\d{5,20}$", description="手机号")


class UserChangePassword(BaseModel):
    """修改密码请求。"""

    old_password: str = Field(min_length=6, max_length=100, description="原密码")
    new_password: str = Field(min_length=6, max_length=100, description="新密码")


class UserInfoResponse(BaseModel):
    """用户信息响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None


class UserAuthResponse(BaseModel):
    """登录/注册响应：返回令牌与用户信息。"""

    token: str
    user_info: UserInfoResponse
