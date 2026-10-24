from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from app.modules.product.schemas import ProductResponse
from app.modules.product.service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["product"])


@router.get("", response_model=list[ProductResponse])
async def get_products(
        category: str | None = None,
        session: AsyncSession = Depends(get_session)
) -> list[ProductResponse]:
    service = ProductService(session)

    return await service.list_products(category)
