from app.core.exceptions import ApplicationError


class ChatThreadNotFoundError(ApplicationError):
    """当前会话不存在或不属属于当前用户"""
    status_code: int = 400  # 默认状态码
    code: str = "CHAT_THREAD_NOT_FOUND"  # 默认异常code
    message: str = "会话不存在或者不属于当前用户"  # 默认异常提示
