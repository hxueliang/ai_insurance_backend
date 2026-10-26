from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.models import Product
from app.modules.product.repository import ProductRepository


class ProductService:
    def __init__(self, session: AsyncSession):
        self.repository = ProductRepository(session)

    async def list_products(self, category: str | None = None) -> list[Product]:
        return await self.repository.query_by_category(category)

    async def list_candidates(
            self,
            categories: list[str],
            premium_min: Decimal | None,
            limit_per_category: int,
    ):
        candidate_products: list[Product] = []
        for category in categories:
            result = await self.repository.find_limited_by_category(
                category=category,
                premium_min=premium_min,
                limit=limit_per_category
            )

            candidate_products.extend(result)

        return candidate_products
