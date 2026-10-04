from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data=None):
    """统一成功响应格式：{code, message, data}。

    使用 jsonable_encoder 保证 ORM / Pydantic 对象都能正确序列化。
    """
    content = {
        "code": 200,
        "message": message,
        "data": data,
    }
    return JSONResponse(content=jsonable_encoder(content))
