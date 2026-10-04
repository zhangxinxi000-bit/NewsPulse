from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import users
from models.users import User


async def get_current_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """认证依赖：从请求头解析 Bearer Token 并查询用户。

    用法：`user: User = Depends(get_current_user)`
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")

    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")

    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的令牌或已经过期的令牌")
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """可选认证依赖：有有效 Token 时返回用户，否则返回 None（不抛 401）。

    用于"登录可用能力增强、未登录不阻塞"的接口（如 AI 问答记录归属）。
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    return await users.get_user_by_token(db, token)
