from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from app.modules.chat_thread.schemas import ChatThreadResponse, ChatThreadCreate, ChatHistoryResponse
from app.modules.chat_thread.service import ChatThreadService

router = APIRouter(prefix="/api/v1/chat-threads", tags=["会话管理的接口"])


async def get_service(
        request: Request,
        session: AsyncSession = Depends(get_session)
):
    agent = request.app.state.agent
    service = ChatThreadService(session, agent)
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
async def rename(
        request: ChatThreadCreate,
        thread_id: str,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service)
):
    """创建会话"""
    return await service.rename(thread_id, user_id, request.title)


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_thread(
        thread_id: str,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service)
):
    """删除会话"""
    await service.delete(thread_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{thread_id}/messages", response_model=ChatHistoryResponse)
async def get_chat_history(
        thread_id: str,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service)
):
    """获取会话历史消息"""
    return await service.get_chat_history(thread_id, user_id)
