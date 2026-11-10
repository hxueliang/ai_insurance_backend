from fastapi.sse import ServerSentEvent
from langchain.messages import HumanMessage
from langchain_core.messages import AIMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.schema import ChatRequest
from app.modules.chat_thread.exceptions import ChatThreadNotFoundError
from app.modules.chat_thread.repository import ChatThreadRepository


class ChatService:
    def __init__(self, session: AsyncSession, agent: CompiledStateGraph):
        self.repository = ChatThreadRepository(session)
        self.agent = agent

    async def chat_stream(
            self,
            chat_request: ChatRequest,
            user_id: int,
    ):
        chat_thread = await self.repository.find_owned(
            str(chat_request.thread_id),
            user_id
        )
        if chat_thread is None:
            raise ChatThreadNotFoundError

        _input = {"messages": [HumanMessage(content=chat_request.message)]}
        config = {"configurable": {"thread_id": str(chat_request.thread_id)}}
        stream = await self.agent.astream_events(
            _input,
            config,
            version="v3"
        )

        async for event in stream:
            method = event['method']
            # 判断事件类型，可以是messages、interrupts等等
            if method == 'messages':
                data = event['params']['data'][0]
                if isinstance(data, AIMessage):
                    yield ServerSentEvent(data=data.text, event="message")
                elif data.get('delta') and data['delta'].get('text'):
                    yield ServerSentEvent(data=data['delta'].get('text'), event="message")

        yield ServerSentEvent(data="END", event="done")
