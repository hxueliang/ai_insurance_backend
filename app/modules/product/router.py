from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from app.modules.product.schemas import ProductResponse
from app.modules.product.service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["product"])


def get_productS_service(session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    yield service


@router.get("", response_model=list[ProductResponse])
async def get_products(
        category: str | None = None,
        service: ProductService = Depends(get_productS_service)
) -> list[ProductResponse]:
    return await service.list_products(category)


@router.get("/candidates", response_model=list[ProductResponse])
async def get_candidates(
        categories: list[str] = Query(min_length=1),
        premium_min: Decimal | None = None,
        limit_per_category: int = 5,
        service: ProductService = Depends(get_productS_service)
) -> list[ProductResponse]:
    print(categories, '====categories')
    return await service.list_candidates(
        categories=categories,
        premium_min=premium_min,
        limit_per_category=limit_per_category
    )
