from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.models import Product
from app.modules.product.repository import ProductRepository


class ProductService:
    def __init__(self, session: AsyncSession):
        self.repository = ProductRepository(session)

    async def list_products(self, category: str | None = None) -> list[Product]:
        return await self.repository.query_by_category(category)
