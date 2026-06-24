# tests/conftest.py
"""
pytest 配置文件 - 定义 fixtures 和 hooks
"""
import pytest
import sys
from pathlib import Path
from typing import Dict

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_client import APIClient
from utils.test_data_manager import TestDataManager, get_test_data_manager
from utils.logger import get_logger
from config.settings import get_settings


logger = get_logger(__name__)


# ========== 基础 Fixtures ==========

@pytest.fixture(scope='session')
def api_client() -> APIClient:
    """
    API 客户端 fixture（会话级别，不携带 token）

    Yields:
        APIClient 实例
    """
    client = APIClient()
    logger.info("创建 API 客户端（未认证）")
    yield client
    client.close()
    logger.info("关闭 API 客户端")


@pytest.fixture(scope='function')
def test_data() -> TestDataManager:
    """
    测试数据管理器 fixture

    Returns:
        TestDataManager 实例
    """
    return get_test_data_manager()


@pytest.fixture(scope='function')
def base_url() -> str:
    """API 基础 URL"""
    return get_settings().get_base_url()


@pytest.fixture(scope='function')
def headers() -> Dict[str, str]:
    """请求头字典"""
    return get_settings().get_headers()


@pytest.fixture(scope='function')
def timeout() -> int:
    """超时时间（秒）"""
    return get_settings().TIMEOUT


# ========== 认证模块数据 Fixtures ==========

@pytest.fixture(scope='function')
def auth_login_data(test_data: TestDataManager) -> dict:
    """登录模块测试数据"""
    return test_data.load_yaml('auth_login_data')


@pytest.fixture(scope='function')
def auth_logout_data(test_data: TestDataManager) -> dict:
    """登出模块测试数据"""
    return test_data.load_yaml('auth_logout_data')


@pytest.fixture(scope='function')
def auth_info_data(test_data: TestDataManager) -> dict:
    """用户信息模块测试数据"""
    return test_data.load_yaml('auth_info_data')


@pytest.fixture(scope='function')
def auth_register_data(test_data: TestDataManager) -> dict:
    """注册模块测试数据"""
    return test_data.load_yaml('auth_register_data')


@pytest.fixture(scope='function')
def auth_reset_data(test_data: TestDataManager) -> dict:
    """密码重置模块测试数据"""
    return test_data.load_yaml('auth_reset_data')


# ========== 商品模块数据 Fixtures ==========

@pytest.fixture(scope='function')
def goods_list_data(test_data: TestDataManager) -> dict:
    """商品列表测试数据"""
    return test_data.load_yaml('goods_list_data')


@pytest.fixture(scope='function')
def goods_detail_data(test_data: TestDataManager) -> dict:
    """商品详情测试数据"""
    return test_data.load_yaml('goods_detail_data')


@pytest.fixture(scope='function')
def goods_category_data(test_data: TestDataManager) -> dict:
    """商品分类测试数据"""
    return test_data.load_yaml('goods_category_data')


@pytest.fixture(scope='function')
def goods_related_data(test_data: TestDataManager) -> dict:
    """相关商品测试数据"""
    return test_data.load_yaml('goods_related_data')


@pytest.fixture(scope='function')
def goods_count_data(test_data: TestDataManager) -> dict:
    """商品统计测试数据"""
    return test_data.load_yaml('goods_count_data')


# ========== 动态数据 Fixtures ==========

@pytest.fixture(scope='function')
def valid_goods_id(api_client: APIClient) -> int:
    """从 goods/list 动态获取一个有效商品 id"""
    resp = api_client.get("/wx/goods/list", params="page=1&size=1")
    return resp.data["list"][0]["id"]


@pytest.fixture(scope='function')
def valid_category_id(api_client: APIClient, valid_goods_id: int) -> int:
    """从 goods/detail 获取商品所属分类 id"""
    resp = api_client.get(f"/wx/goods/detail", params=f"id={valid_goods_id}")
    return resp.data["info"]["categoryId"]


# ========== 兼容旧引用的合并数据 Fixture ==========

@pytest.fixture(scope='function')
def auth_data(test_data: TestDataManager) -> dict:
    """认证模块全部测试数据（合并版，兼容旧引用）"""
    return test_data.load_yaml('auth_data')


# ========== 认证客户端 Fixture ==========

@pytest.fixture(scope='function')
def authenticated_client(auth_login_data: dict) -> APIClient:
    """
    已认证的 API 客户端 fixture

    自动使用 login_success 用例的凭据登录并设置 token，
    后续请求无需手动传 token。

    Args:
        auth_login_data: 登录测试数据

    Yields:
        已设置 token 的 APIClient 实例
    """
    client = APIClient()
    login_case = auth_login_data["login_success"]
    login_resp = client.post(login_case["endpoint"], json=login_case["request"])
    token = login_resp.data["token"]
    client.set_token(token)
    logger.info("已创建认证客户端")
    yield client
    client.close()
    logger.info("已关闭认证客户端")


# ========== Hooks ==========

def pytest_configure(config):
    """pytest 配置 hook"""
    config.addinivalue_line('markers', 'smoke: 冒烟测试')
    config.addinivalue_line('markers', 'regression: 回归测试')
    config.addinivalue_line('markers', 'api: API 测试')
    config.addinivalue_line('markers', 'slow: 慢速测试')
    config.addinivalue_line('markers', 'P0: 最高优先级用例')
    config.addinivalue_line('markers', 'P1: 高优先级用例')
    config.addinivalue_line('markers', 'P2: 中优先级用例')


def pytest_collection_modifyitems(config, items):
    """
    修改测试集合 hook — 按模块文件名自动打标记
    """
    for item in items:
        fspath = str(item.fspath)

        # 按测试文件名自动添加模块标记
        if 'auth' in fspath:
            item.add_marker(pytest.mark.api)
        elif 'shopping' in fspath:
            item.add_marker(pytest.mark.api)

        # 按用例优先级自动打标（从 parametrize 的 case_id 推断）
        if hasattr(item, 'callspec'):
            case_id = item.callspec.params.get('case_id', '')
            if case_id:
                # 可以在这里根据 case_id 前缀打标记
                pass


def pytest_report_header(config):
    """自定义测试报告头部"""
    settings = get_settings()
    return [
        f"测试环境: {settings.ENV}",
        f"基础 URL: {settings.get_base_url()}",
        f"超时时间: {settings.TIMEOUT}秒",
    ]


@pytest.fixture(autouse=True)
def test_setup_teardown(request):
    """自动 fixture - 每个测试的 setup 和 teardown 日志"""
    logger.info(f"\n{'='*10} 开始测试: {request.node.name} {'='*10}")
    yield
    logger.info(f"{'='*10} 结束测试: {request.node.name} {'='*10}\n")
