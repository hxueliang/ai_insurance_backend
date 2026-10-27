from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.common.schemas import BaseSchema


class ChatThreadCreate(BaseSchema):
    """创建会话请求"""

    title: str = Field(default="新会话", min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return value.strip()


class ChatThreadResponse(BaseSchema):
    """会话响应"""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
