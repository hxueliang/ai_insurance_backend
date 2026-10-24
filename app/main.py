from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.modules.product.router import router as router_product

# 日志配置
configure_logging(settings.logging.level)
# 获取日志器
logger = get_logger(__name__)


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.app.name}，应用正在启动...")
    from app.infra.database import check_database, close_database
    try:
        await check_database()
        yield
    finally:
        logger.info("应用关闭中...")
        await close_database()


# 初始化FastApi
app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan,
)

app.include_router(router_product)


@app.get("/healthy", summary="健康检查接口")
async def healthy() -> dict[str, str]:
    logger.info("健康检查接口正常调用。")
    return {"status": "OK"}


if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False
    )
