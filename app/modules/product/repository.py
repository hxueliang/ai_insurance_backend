from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def query_by_category(self, category: str | None = None) -> list[Product]:
        conditions = [Product.status == 'active']

        if category:
            conditions.append(Product.category == category)

        result = await self.session.scalars(
            select(Product)
            .where(*conditions)
            .order_by(Product.id)
        )

        return result.all()

    async def find_limited_by_category(
            self,
            category: str,
            premium_min: Decimal | None,
            limit: int = 5
    ) -> list[Product]:
        conditions = [
            Product.status == 'active',
            Product.category == category
        ]

        if premium_min is not None:
            conditions.append(Product.min_premium <= premium_min)

        result = await self.session.scalars(
            select(Product)
            .where(*conditions)
            .order_by(
                Product.min_premium.asc().nullslast(),
                Product.id.asc()
            )
            .limit(limit)
        )

        return result.all()
