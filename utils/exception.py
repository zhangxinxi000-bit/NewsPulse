class BusinessException(Exception):
    """业务异常：在路由层抛出，由全局异常处理器统一转换为响应。"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
