from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from app.modules.chat_thread.schemas import ChatThreadResponse, ChatThreadCreate
from app.modules.chat_thread.service import ChatThreadService

router = APIRouter(prefix="/api/v1/chat-threads", tags=["会话管理的接口"])


async def get_service(session: AsyncSession = Depends(get_session)):
    service = ChatThreadService(session)
    return service


@router.post("", response_model=ChatThreadResponse)
async def create_chat_thread(
        request: ChatThreadCreate,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service)
):
    """创建会话"""
    return await service.add(user_id, request.title)


@router.get("", response_model=list[ChatThreadResponse])
async def list_by_user_id(
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service)
):
    """查询会话列表"""
    return await service.list_by_user_id(user_id)


@router.patch("/{thread_id}", response_model=ChatThreadResponse)
async def create_chat_thread(
        request: ChatThreadCreate,
        thread_id: str,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service)
):
    """创建会话"""
    return await service.rename(thread_id, user_id, request.title)
