"""日志工具模块"""
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """获取配置好的 Logger 实例

    Args:
        name: Logger 名称

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
