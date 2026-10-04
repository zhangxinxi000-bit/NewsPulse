"""AI 问答模块：调用阿里云百炼（DashScope）兼容模式的通义千问大模型。

使用前配置 API Key（二选一）：
1. 环境变量：AI_API_KEY
2. 修改下方 AI_API_KEY 常量

未配置时接口正常返回提示，不影响其他功能。
问答记录写入 ai_chat 表：登录用户记录归属，匿名问答不记录归属；
登录用户可通过 GET /api/ai/history 查询自己的问答历史。
"""
import os
from typing import Optional

import httpx

from fastapi import APIRouter, Depends

from config.db_conf import get_db
from crud import ai as ai_crud
from models.users import User
from schemas.ai import ChatHistoryItem, ChatRequest
from utils.auth import get_current_user, get_current_user_optional
from utils.response import success_response

router = APIRouter(prefix="/api/ai", tags=["AI问答"])

AI_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "qwen-plus")


@router.post("/chat", summary="AI 问答（通义千问）")
async def chat(
    body: ChatRequest,
    user: Optional[User] = Depends(get_current_user_optional),
    db=Depends(get_db),
):
    if not AI_API_KEY:
        return success_response(
            message="AI 问答未启用",
            data={
                "answer": "AI 问答功能需要配置大模型 API Key：请在环境变量 AI_API_KEY 中设置（或修改 routers/ai.py 中的常量），模型默认为 qwen-plus。",
            },
        )

    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": body.question}],
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(AI_ENDPOINT, json=payload, headers=headers)
            resp.raise_for_status()
            answer = resp.json()["choices"][0]["message"]["content"]
            await ai_crud.save_chat_record(db, user.id if user else None, body.question, answer)
            return success_response(message="AI 回答成功", data={"answer": answer})
    except httpx.HTTPStatusError as e:
        return success_response(
            message="AI 服务调用失败",
            data={"answer": f"大模型接口返回错误（HTTP {e.response.status_code}），请检查 API Key 是否有效。"},
        )
    except Exception as e:
        return success_response(
            message="AI 服务调用失败",
            data={"answer": f"调用大模型时发生错误：{e}"},
        )


@router.get("/history", summary="AI 问答历史（需登录）")
async def chat_history(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    records = await ai_crud.get_chat_history(db, user.id, limit=min(limit, 100))
    data = [ChatHistoryItem.model_validate(r) for r in records]
    return success_response(message="获取问答历史成功", data=data)
