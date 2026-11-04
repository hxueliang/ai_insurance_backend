"""构建 RAG 知识库：解析所有保险产品条款，切分父子块后分别写入 Milvus 和 PostgreSQL。

用法：
    uv run python scripts/ingest_rag.py
    uv run python scripts/ingest_rag.py --product-id 9 10 11 12
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 直接以脚本方式运行时，把项目根目录加入模块搜索路径，保证能导入 app 包
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_milvus import BM25BuiltInFunction, Milvus
from langchain_ollama import OllamaEmbeddings

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.infra.database import AsyncSessionFactory, close_database
from app.modules.product.models import Product
from app.modules.product.service import ProductService
from app.rag.pipeline import RAGPipeline

logger = get_logger(__name__)

# 向量模型与 Milvus Collection 配置，参考 notebooks/n34_rag_demo.ipynb
EMBEDDING_MODEL = "qwen3-embedding:0.6b"
EMBEDDING_DIMENSIONS = 1024
COLLECTION_NAME = "insurance_collection"

# 网络接口不稳定时的产品级重试策略
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10


def build_vector_store() -> Milvus:
    """初始化 EmbeddingModel 与 Milvus VectorStore（Collection 不存在时自动创建）。"""
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return Milvus(
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
        builtin_function=BM25BuiltInFunction(analyzer_params={"type": "chinese"}),
        vector_field=["dense", "sparse"],
        connection_args={"uri": settings.rag.milvus_url},
        auto_id=True,
    )


async def load_products() -> list[Product]:
    """查询所有上架的保险产品。"""
    async with AsyncSessionFactory() as session:
        service = ProductService(session)
        return await service.list_products()


async def ingest_one(
        pipeline: RAGPipeline,
        product: Product,
        index: int,
        total: int,
) -> bool:
    """构建单个产品的知识库，失败时重试。返回是否成功。"""
    for attempt in range(1, MAX_RETRIES + 1):
        logger.info(
            f"正在处理产品 [{index}/{total}]（第 {attempt} 次）："
            f"id={product.id}, name={product.name}, clause={product.clause_name}"
        )
        try:
            await pipeline.ingest(product)
            logger.info(f"产品 id={product.id} 知识库构建完成✅️")
            return True
        except Exception:
            logger.exception(f"产品 id={product.id} 知识库构建失败❌")
            if attempt < MAX_RETRIES:
                logger.info(f"等待 {RETRY_DELAY_SECONDS} 秒后重试...")
                await asyncio.sleep(RETRY_DELAY_SECONDS)
    return False


async def ingest_all(pipeline: RAGPipeline, products: list[Product]) -> int:
    """逐个产品构建知识库，返回失败数量。单个产品失败不影响后续产品。"""
    failed = 0

    for index, product in enumerate(products, start=1):
        if not await ingest_one(pipeline, product, index, len(products)):
            failed += 1

    return failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="构建 RAG 知识库")
    parser.add_argument(
        "--product-id",
        type=int,
        nargs="+",
        help="只处理指定产品 id，默认处理全部产品",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    configure_logging(settings.logging.level)

    products = await load_products()
    if args.product_id:
        wanted = set(args.product_id)
        products = [product for product in products if product.id in wanted]
        logger.info(f"只处理指定产品 id：{sorted(wanted)}")

    logger.info(f"共查询到 {len(products)} 个产品，开始构建 RAG 知识库...")
    if not products:
        logger.warning("没有可处理的产品，退出。")
        return 0

    pipeline = RAGPipeline(build_vector_store())
    try:
        failed = await ingest_all(pipeline, products)
    finally:
        pipeline.close()
        await close_database()

    succeeded = len(products) - failed
    logger.info(f"RAG 知识库构建结束：成功 {succeeded} 个，失败 {failed} 个。")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
