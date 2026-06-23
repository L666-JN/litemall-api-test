# config/settings.py
"""
配置管理模块 - 加载和管理环境配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录（settings.py 在 config/ 下，向上两级）
BASE_DIR = Path(__file__).parent.parent

# 加载环境变量
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Settings:
    """配置类 - 统一管理所有配置项"""

    # API 配置 - Litemall (端口 8088)
    BASE_URL: str = os.getenv('BASE_URL', 'http://localhost:8088')
    API_VERSION: str = os.getenv('API_VERSION', '')
    TIMEOUT: int = int(os.getenv('TIMEOUT', '30'))

    # 认证配置
    USERNAME: str = os.getenv('USERNAME', '')
    PASSWORD: str = os.getenv('PASSWORD', '')
    AUTH_TOKEN: str = os.getenv('AUTH_TOKEN', '')

    # 测试配置
    ENV: str = os.getenv('ENV', 'dev')  # dev, test, prod
    HEADERS: dict = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # 日志配置
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.path.join(BASE_DIR, 'logs', 'api_test.log')

    # 重试配置
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY: int = int(os.getenv('RETRY_DELAY', '1'))

    @classmethod
    def get_base_url(cls) -> str:
        """获取完整的 API 基础 URL"""
        if cls.API_VERSION:
            return f"{cls.BASE_URL}/{cls.API_VERSION}".rstrip('/')
        return cls.BASE_URL.rstrip('/')

    @classmethod
    def get_headers(cls, with_auth: bool = False) -> dict:
        """获取请求头"""
        headers = cls.HEADERS.copy()
        if with_auth and cls.AUTH_TOKEN:
            # litemall 使用 X-Litemall-Token 请求头
            headers['X-Litemall-Token'] = cls.AUTH_TOKEN
        return headers

    @classmethod
    def get_test_data_path(cls) -> Path:
        """获取测试数据目录"""
        return BASE_DIR / 'tests' / 'test_data'


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings