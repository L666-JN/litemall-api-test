# utils/logger.py
"""
日志配置模块 - 提供结构化日志记录功能
"""
import logging
import sys
from pathlib import Path
from config.settings import get_settings


def setup_logger(name: str = 'api_test') -> logging.Logger:
    """
    配置并返回日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        配置好的日志记录器
    """
    settings = get_settings()

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # 文件处理器
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # 日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 全局日志记录器
logger = setup_logger()


def get_logger(name: str = 'api_test') -> logging.Logger:
    """获取日志记录器"""
    return setup_logger(name)