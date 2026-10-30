from langchain.messages import HumanMessage, AIMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_thread.exceptions import ChatThreadNotFoundError
from app.modules.chat_thread.models import ChatThread
from app.modules.chat_thread.repository import ChatThreadRepository
from app.modules.chat_thread.schemas import ChatMessageResponse, ChatHistoryResponse


class ChatThreadService:
    def __init__(self, session: AsyncSession, agent: CompiledStateGraph):
        self.session = session
        self.agent = agent
        self.repository = ChatThreadRepository(session)

    async def add(self, user_id: int, title: str):
        async with self.session.begin():
            chat_thread = ChatThread(user_id=user_id, title=title)
            await self.repository.add(chat_thread)
            return chat_thread

    async def list_by_user_id(self, user_id: int):
        return await self.repository.list_by_user_id(user_id)

    async def rename(self, thread_id: str, user_id: int, title: str):
        async with self.session.begin():
            chat_thread = await self.repository.find_owned(thread_id, user_id)
            if not chat_thread:
                raise ChatThreadNotFoundError

            chat_thread.title = title
            await self.session.flush()
            await self.session.refresh(chat_thread)
            return chat_thread

    async def delete(self, thread_id: str, user_id: int) -> None:
        async with self.session.begin():
            chat_thread = await self.repository.find_owned(thread_id, user_id)
            if not chat_thread:
                raise ChatThreadNotFoundError

            await self.agent.checkpointer.adelete_thread(thread_id)
            await self.repository.delete(chat_thread)

    async def get_chat_history(self, thread_id: str, user_id: int):
        chat_thread = await self.repository.find_owned(thread_id, user_id)
        if not chat_thread:
            raise ChatThreadNotFoundError

        config = {"configurable": {"thread_id": thread_id}}

        snapshot = await self.agent.aget_state(config)

        messages = []

        for message in snapshot.values.get("messages", []):
            if isinstance(message, HumanMessage):
                role = 'user'
            elif isinstance(message, AIMessage):
                role = 'assistant'
            else:
                continue
            if not message.text:
                continue

            messages.append(ChatMessageResponse(role=role, content=message.text))

        return ChatHistoryResponse(thread_id=thread_id, messages=messages)
