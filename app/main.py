from app.core.config import settings

from app.core.logging import configure_logging, get_logger

# 日志配置
configure_logging(settings.logging.level)
# 获取日志器
logger = get_logger(__name__)
