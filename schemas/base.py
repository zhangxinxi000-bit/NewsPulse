from typing import Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    """统一响应结构：{code, message, data}。实际响应由 utils.response 生成。"""

    code: int = 200
    message: str = "success"
    data: Any = None
