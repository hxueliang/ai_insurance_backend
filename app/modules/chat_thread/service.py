from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_thread.models import ChatThread
from app.modules.chat_thread.repository import ChatThreadRepository


class ChatThreadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ChatThreadRepository(session)

    async def add(self, user_id: int, title: str):
        async with self.session.begin():
            chat_thread = ChatThread(user_id=user_id, title=title)
            return await self.repository.add(chat_thread)
