from uuid import UUID, uuid4

from sqlalchemy import String, BigInteger
from sqlalchemy.dialects.postgresql.base import UUID as PG_UUID
from sqlalchemy.orm import mapped_column, Mapped

from app.common.models import Base, CreateAtUpdateAtMixin


class ChatThread(Base, CreateAtUpdateAtMixin):
    """客服会话"""

    __tablename__ = "chat_threads"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(
        String(200),
        default="新会话",
        server_default="新会话",
    )
