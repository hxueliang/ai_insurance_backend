from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import ApplicationError
from app.core.logging import configure_logging, get_logger
from app.modules.chat_thread.router import router as router_chat_thread
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
    from app.infra.checkpointer import init_checkpointer, close_checkpointer
    from app.agants.insurance_advisor import init_insurance_agent
    try:
        await check_database()
        checkpointer = await init_checkpointer()
        agent = init_insurance_agent(checkpointer)
        yield
    finally:
        logger.info("应用关闭中...")
        await close_database()
        await close_checkpointer()


# 初始化FastApi
app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan,
)

app.include_router(router_product)
app.include_router(router_chat_thread)


@app.get("/healthy", summary="健康检查接口")
async def healthy() -> dict[str, str]:
    logger.info("健康检查接口正常调用。")
    return {"status": "OK"}


# 统一处理异常信息
@app.exception_handler(ApplicationError)
def handle_exception(request: Request, exc: ApplicationError):
    logger.error(f"处理异常, 请求路径: {request.url}, 异常代码: {exc.code}，异常信息: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message
        }
    )


if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False
    )
