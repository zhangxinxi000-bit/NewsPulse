import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserCreate, UserUpdate
from utils.security import get_hash_password, verify_password

# Token 有效期：7 天
TOKEN_EXPIRE_DAYS = 7


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """创建用户（密码使用 bcrypt 加密，支持昵称/性别/简介/手机号等可选字段）。"""
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_hash_password(user_in.password),
        nickname=user_in.nickname,
        avatar=user_in.avatar,
        gender=user_in.gender or "unknown",
        bio=user_in.bio,
        phone=user_in.phone,
    )
    db.add(user)
    await db.flush()  # 先落库拿到自增 id，随后创建 Token
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """校验用户名密码，成功返回用户。"""
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ---------- Token ----------
async def create_token(db: AsyncSession, user_id: int) -> str:
    """为用户生成 7 天有效的随机 Token。"""
    token = secrets.token_hex(32)  # 64 位十六进制，不可预测
    expires_at = datetime.now() + timedelta(days=TOKEN_EXPIRE_DAYS)
    db.add(UserToken(user_id=user_id, token=token, expires_at=expires_at))
    await db.commit()
    return token


async def get_user_by_token(db: AsyncSession, token: str) -> Optional[User]:
    """根据 Token 查询有效用户（未过期）。"""
    stmt = (
        select(User)
        .join(UserToken, UserToken.user_id == User.id)
        .where(UserToken.token == token, UserToken.expires_at > datetime.now())
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ---------- 更新 ----------
async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    data = user_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        if value is not None:
            setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> bool:
    """修改密码：校验原密码正确后更新。"""
    if not verify_password(old_password, user.hashed_password):
        return False
    user.hashed_password = get_hash_password(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True
