# tests/conftest.py
"""
pytest 配置文件 - 定义 fixtures 和 hooks
"""
import pytest
import sys
from pathlib import Path
from typing import Any, Dict, Generator

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_client import APIClient
from utils.test_data_manager import get_test_data_manager
from utils.logger import get_logger
from config.settings import get_settings


logger = get_logger(__name__)


# ========== Fixtures ==========

@pytest.fixture(scope='session')
def api_client() -> APIClient:
    """
    API 客户端 fixture（会话级别）

    Yields:
        APIClient 实例
    """
    client = APIClient()
    logger.info("创建 API 客户端")
    yield client
    client.close()
    logger.info("关闭 API 客户端")


@pytest.fixture(scope='function')
def test_data() -> get_test_data_manager:
    """
    测试数据管理器 fixture

    Yields:
        TestDataManager 实例
    """
    return get_test_data_manager()


@pytest.fixture(scope='function')
def base_url() -> str:
    """
    基础 URL fixture

    Returns:
        API 基础 URL
    """
    return get_settings().get_base_url()


@pytest.fixture(scope='function')
def headers() -> Dict[str, str]:
    """
    请求头 fixture

    Returns:
        请求头字典
    """
    return get_settings().get_headers()


@pytest.fixture(scope='function')
def auth_headers() -> Dict[str, str]:
    """
    带认证的请求头 fixture

    Returns:
        带认证令牌的请求头字典
    """
    return get_settings().get_headers(with_auth=True)


@pytest.fixture(scope='function')
def timeout() -> int:
    """
    超时时间 fixture

    Returns:
        超时时间（秒）
    """
    return get_settings().TIMEOUT


# ========== 数据驱动测试 Fixtures ==========

@pytest.fixture(scope='function')
def auth_data(test_data) -> dict:
    """
    认证模块测试数据 fixture

    Args:
        test_data: 测试数据管理器

    Returns:
        认证测试数据
    """
    return test_data.load_yaml('auth_data')


@pytest.fixture(scope='function')
def shopping_data(test_data) -> dict:
    """
    购物流程测试数据 fixture

    Args:
        test_data: 测试数据管理器

    Returns:
        购物流程测试数据
    """
    return test_data.load_yaml('shopping_flow')


# ========== 参数化测试数据 ==========


# ========== 认证夹具 ==========

@pytest.fixture(scope='function')
def authenticated_client(auth_data: dict) -> APIClient:
    """
    已认证的 API 客户端 fixture

    自动登录并设置 X-Litemall-Token，后续请求无需手动传 token。

    Args:
        auth_data: 认证测试数据

    Yields:
        已设置 token 的 APIClient 实例
    """
    client = APIClient()
    login_case = auth_data["login_success"]
    login_resp = client.post("/wx/auth/login", json=login_case["request"])
    token = login_resp.data["token"]
    client.set_token(token)
    logger.info("已创建认证客户端")
    yield client
    client.close()
    logger.info("已关闭认证客户端")


# ========== Hooks ==========

def pytest_configure(config):
    """
    pytest 配置 hook

    Args:
        config: pytest 配置对象
    """
    # 自定义标记
    config.addinivalue_line('markers', 'smoke: 冒烟测试')
    config.addinivalue_line('markers', 'regression: 回归测试')
    config.addinivalue_line('markers', 'api: API 测试')
    config.addinivalue_line('markers', 'slow: 慢速测试')


def pytest_collection_modifyitems(config, items):
    """
    修改测试集合 hook - 自动添加标记

    Args:
        config: pytest 配置对象
        items: 测试项列表
    """
    for item in items:
        # 根据测试文件名自动添加标记
        if 'test_users' in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif 'test_products' in str(item.fspath):
            item.add_marker(pytest.mark.api)


def pytest_report_header(config):
    """
    自定义测试报告头部

    Args:
        config: pytest 配置对象

    Returns:
        报告头部信息
    """
    settings = get_settings()
    return [
        f"测试环境: {settings.ENV}",
        f"基础 URL: {settings.get_base_url()}",
        f"超时时间: {settings.TIMEOUT}秒",
    ]


@pytest.fixture(autouse=True)
def test_setup_teardown(request):
    """
    自动 fixture - 用于每个测试的 setup 和 teardown

    Args:
        request: pytest 请求对象
    """
    logger.info(f"\n========== 开始测试: {request.node.name} ==========")
    yield
    logger.info(f"========== 结束测试: {request.node.name} ==========\n")