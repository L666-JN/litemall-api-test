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


# ========== 购物车模块数据 Fixtures ==========

@pytest.fixture(scope='function')
def cart_index_data(test_data: TestDataManager) -> dict:
    """购物车列表测试数据"""
    return test_data.load_yaml('cart_index_data')


@pytest.fixture(scope='function')
def cart_add_data(test_data: TestDataManager) -> dict:
    """购物车添加测试数据"""
    return test_data.load_yaml('cart_add_data')


@pytest.fixture(scope='function')
def cart_fastadd_data(test_data: TestDataManager) -> dict:
    """购物车快速添加测试数据"""
    return test_data.load_yaml('cart_fastadd_data')


@pytest.fixture(scope='function')
def cart_update_data(test_data: TestDataManager) -> dict:
    """购物车更新测试数据"""
    return test_data.load_yaml('cart_update_data')


@pytest.fixture(scope='function')
def cart_checked_data(test_data: TestDataManager) -> dict:
    """购物车选中测试数据"""
    return test_data.load_yaml('cart_checked_data')


@pytest.fixture(scope='function')
def cart_delete_data(test_data: TestDataManager) -> dict:
    """购物车删除测试数据"""
    return test_data.load_yaml('cart_delete_data')


@pytest.fixture(scope='function')
def cart_count_data(test_data: TestDataManager) -> dict:
    """购物车数量测试数据"""
    return test_data.load_yaml('cart_count_data')


@pytest.fixture(scope='function')
def cart_checkout_data(test_data: TestDataManager) -> dict:
    """购物车结算测试数据"""
    return test_data.load_yaml('cart_checkout_data')


# ========== 地址模块数据 Fixtures ==========

@pytest.fixture(scope='function')
def address_list_data(test_data: TestDataManager) -> dict:
    """地址列表测试数据"""
    return test_data.load_yaml('address_list_data')


@pytest.fixture(scope='function')
def address_detail_data(test_data: TestDataManager) -> dict:
    """地址详情测试数据"""
    return test_data.load_yaml('address_detail_data')


@pytest.fixture(scope='function')
def address_save_data(test_data: TestDataManager) -> dict:
    """地址保存测试数据"""
    return test_data.load_yaml('address_save_data')


@pytest.fixture(scope='function')
def address_delete_data(test_data: TestDataManager) -> dict:
    """地址删除测试数据"""
    return test_data.load_yaml('address_delete_data')


# ========== 订单模块数据 Fixtures ==========

@pytest.fixture(scope='function')
def order_list_data(test_data: TestDataManager) -> dict:
    """订单列表测试数据"""
    return test_data.load_yaml('order_list_data')


@pytest.fixture(scope='function')
def order_detail_data(test_data: TestDataManager) -> dict:
    """订单详情测试数据"""
    return test_data.load_yaml('order_detail_data')


@pytest.fixture(scope='function')
def order_submit_data(test_data: TestDataManager) -> dict:
    """订单提交测试数据"""
    return test_data.load_yaml('order_submit_data')


@pytest.fixture(scope='function')
def order_cancel_data(test_data: TestDataManager) -> dict:
    """订单取消测试数据"""
    return test_data.load_yaml('order_cancel_data')


@pytest.fixture(scope='function')
def order_confirm_data(test_data: TestDataManager) -> dict:
    """确认收货测试数据"""
    return test_data.load_yaml('order_confirm_data')


@pytest.fixture(scope='function')
def order_delete_data(test_data: TestDataManager) -> dict:
    """订单删除测试数据"""
    return test_data.load_yaml('order_delete_data')


@pytest.fixture(scope='function')
def order_comment_data(test_data: TestDataManager) -> dict:
    """订单评价测试数据"""
    return test_data.load_yaml('order_comment_data')


@pytest.fixture(scope='function')
def order_goods_data(test_data: TestDataManager) -> dict:
    """订单商品测试数据"""
    return test_data.load_yaml('order_goods_data')


# ========== 首页模块数据 Fixtures ==========

@pytest.fixture(scope='function')
def home_data(test_data: TestDataManager) -> dict:
    """首页测试数据"""
    return test_data.load_yaml('home_data')


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


@pytest.fixture(scope='function')
def valid_address_id(authenticated_client: APIClient) -> int:
    """从 address/list 动态获取一个有效地址 id"""
    resp = authenticated_client.get("/wx/address/list")
    addr_list = resp.data.get("list", []) if isinstance(resp.data, dict) else []
    if addr_list:
        return addr_list[0]["id"]
    # 如果没有地址，创建一个
    save_resp = authenticated_client.post("/wx/address/save", json={
        "name": "FixtAddr",
        "tel": "13800138000",
        "province": "广东省",
        "city": "广州市",
        "county": "天河区",
        "addressDetail": "测试路100号",
        "areaCode": "440106",
        "isDefault": False,
    })
    return save_resp.data  # data is the new address id


@pytest.fixture(scope='function')
def valid_order_id(authenticated_client: APIClient) -> int:
    """从 order/list 动态获取一个有效订单 id（取最新的）"""
    resp = authenticated_client.get("/wx/order/list")
    orders = resp.data.get("list", []) if isinstance(resp.data, dict) else []
    if orders:
        return orders[0]["id"]
    raise pytest.skip("没有可用的订单（需要先通过购物车+地址下单）")


@pytest.fixture(scope='function')
def valid_goods_product_pair(api_client: APIClient) -> dict:
    """
    获取一个有效的 goodsId -> productId 配对

    从 goods/list 取第一个商品，再用 goods/detail 查其首个 productId，
    返回 {'goodsId': int, 'productId': int}。
    """
    # 获取一个有效商品
    resp = api_client.get("/wx/goods/list", params="page=1&size=1")
    goods_id = resp.data["list"][0]["id"]

    # 获取该商品的 productId
    resp = api_client.get(f"/wx/goods/detail", params=f"id={goods_id}")
    product_id = resp.data["productList"][0]["id"]

    return {"goodsId": goods_id, "productId": product_id}


@pytest.fixture(scope='function')
def cart_with_item(authenticated_client: APIClient, valid_goods_product_pair: dict) -> dict:
    """
    在购物车中创建一个条目，返回条目信息，测试结束后自动清理。

    返回 dict: {'id': int, 'goodsId': int, 'productId': int, ...}
    """
    pair = valid_goods_product_pair
    # 先清空购物车，确保干净起点
    index_resp = authenticated_client.get("/wx/cart/index")
    for item in index_resp.data.get("cartList", []):
        authenticated_client.post("/wx/cart/delete",
                                  json={"productIds": [item["productId"]]})

    # 添加商品到购物车
    add_resp = authenticated_client.post("/wx/cart/add", json={
        "goodsId": pair["goodsId"],
        "number": 2,
        "productId": pair["productId"],
    })
    assert add_resp.ok, f"cart_with_item 加购失败: errno={add_resp.errno}, errmsg={add_resp.errmsg}"

    # 获取购物车条目详情
    index_resp = authenticated_client.get("/wx/cart/index")
    cart_list = index_resp.data["cartList"]
    assert len(cart_list) > 0, "cart_with_item: 购物车为空"
    item = cart_list[0]

    yield item

    # 清理：删除购物车中所有条目
    index_resp = authenticated_client.get("/wx/cart/index")
    for it in index_resp.data.get("cartList", []):
        authenticated_client.post("/wx/cart/delete",
                                  json={"productIds": [it["productId"]]})


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
