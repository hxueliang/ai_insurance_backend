from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_thread.models import ChatThread


class ChatThreadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, chat_thread: ChatThread):
        self.session.add(chat_thread)
        await self.session.commit()

    async def list_by_user_id(self, user_id: int):
        result = await self.session.scalars(
            select(ChatThread)
            .where(ChatThread.user_id == user_id)
            .order_by(
                ChatThread.updated_at.desc(),
                ChatThread.created_at.desc()
            )
        )
        return result.all()

    async def find_owned(self, thread_id: str, user_id: int) -> ChatThread:
        return await self.session.scalar(
            select(ChatThread)
            .where(ChatThread.id == thread_id, ChatThread.user_id == user_id)
        )
