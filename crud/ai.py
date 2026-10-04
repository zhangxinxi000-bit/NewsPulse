from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ai_chat import AiChat


async def save_chat_record(
    db: AsyncSession,
    user_id: Optional[int],
    message: str,
    response: str,
) -> AiChat:
    """保存一条 AI 问答记录（匿名问答 user_id 为空）。"""
    record = AiChat(user_id=user_id, message=message, response=response)
    db.add(record)
    await db.commit()
    return record


async def get_chat_history(db: AsyncSession, user_id: int, limit: int = 20) -> list[AiChat]:
    """查询指定用户的 AI 问答历史（按时间倒序）。"""
    stmt = (
        select(AiChat)
        .where(AiChat.user_id == user_id)
        .order_by(AiChat.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
