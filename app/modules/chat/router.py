from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from fastapi.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from app.modules.chat.schema import ChatRequest
from app.modules.chat.service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["与AI对话接口"])


async def get_service(
        request: Request,
        session: AsyncSession = Depends(get_session)
):
    agent = request.app.state.agent
    return ChatService(session, agent)


@router.post("", response_class=EventSourceResponse)
async def chat(
        request: ChatRequest,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatService = Depends(get_service)
):
    async for sse in service.chat_stream(request, user_id):
        yield sse
