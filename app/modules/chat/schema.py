from uuid import UUID

from pydantic import Field

from app.common.schemas import BaseSchema


class ChatRequest(BaseSchema):
    """基础对话请求"""

    thread_id: UUID
    message: str = Field(min_length=1)
