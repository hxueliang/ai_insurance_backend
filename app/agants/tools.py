from decimal import Decimal

from fastapi.encoders import jsonable_encoder
from langchain.tools import tool

from app.core.logging import get_logger
from app.infra.database import AsyncSessionFactory
from app.modules.product.models import Product
from app.modules.product.service import ProductService

logger = get_logger(__name__)


@tool
async def query_candidate_products(
        categories: list[str],
        premium_min: Decimal | None = None,
        limit_per_category: int = 5,
):
    """
    根据险种和保费条件查询可用于推荐的候选保险产品。当用户咨询具体保险产品或需要保险产品推荐时使用。

    Args:
        categories: 产品分类列表，可选值为 medical、critical_illness、life、accident。
        premium_min: 最低保费上限，可选参数，只返回最低保费小于该值的产品。
        limit_per_category: 每个险种最多返回的产品数量，可选参数，默认5。
    """

    logger.info("=" * 50 + "query_candidate_products" + "=" * 50)

    async with AsyncSessionFactory() as session:
        service = ProductService(session)
        candidate_products: list[Product] = await service.list_candidates(
            categories=categories,
            premium_min=premium_min,
            limit_per_category=limit_per_category
        )

        return jsonable_encoder(candidate_products)


@tool
async def query_product_clause(
        query: str,
        k: int,
        product_id: int,
) -> str:
    """查询指定保险产品的条款内容。

    Args:
        query: 需要从保险条款中查询的问题。
        k: 返回多少个结果
        product_id: 保险产品ID。
    """
    from app.rag import retriever

    logger.info("=" * 50 + "query_product_clause" + "=" * 50)
    chunks = await retriever.retrieve(query, k, product_id)

    logger.info(f"query: {query}")
    logger.info(f"k: {k}")
    logger.info(f"product_id: {product_id}")
    # logger.info(chunks)
    if not chunks:
        return "没有查询到相关保险条款。"

    res = "\n\n".join(
        f"章节：{' > '.join(chunk.section_path)}\n"
        f"内容：{chunk.content}"
        for chunk in chunks
    )
    logger.info(f"tool-res: {str(res)}")

    return res
