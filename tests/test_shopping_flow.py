# tests/test_shopping_flow.py
"""
Litemall 消费者下单业务流测试

链路：
  首页 → 商品详情 → 创建地址 → 加入购物车 → 结算 → 提交订单 → 订单列表 → 订单详情
"""
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.logger import get_logger
from config.endpoints import Endpoints

logger = get_logger(__name__)


class TestShoppingFlow:
    """消费者下单全流程测试（步骤间通过类变量共享数据）"""

    goods_id: int = None
    product_id: int = None
    address_id: int = None
    cart_id: int = None
    coupon_id: int = None
    order_id: int = None

    # ───────── 步骤 1：首页 ─────────
    def test_01_home_index(self, api_client: APIClient, shopping_data: dict):
        """首页获取新品列表，取出第一个商品 ID"""
        case = shopping_data["home_index"]
        resp = api_client.get(Endpoints.HOME_INDEX)

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"]
        for field in case["expected"]["fields"]:
            assert field in resp.data, f"缺少字段: {field}"

        new_goods = resp.data["newGoodsList"]
        assert len(new_goods) > 0, "首页无新品数据"
        TestShoppingFlow.goods_id = new_goods[0]["id"]

        logger.info(f"[1/7] 首页 → 商品: {new_goods[0]['name']} (id={self.goods_id})")

    # ───────── 步骤 2：商品详情 ─────────
    def test_02_goods_detail(self, api_client: APIClient, shopping_data: dict):
        """查看商品详情，获取 productId"""
        case = shopping_data["goods_detail"]
        resp = api_client.get(
            Endpoints.GOODS_DETAIL,
            params={"id": TestShoppingFlow.goods_id}
        )

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"]
        for field in case["expected"]["fields"]:
            assert field in resp.data, f"缺少字段: {field}"

        products = resp.data["productList"]
        assert len(products) > 0, "商品无可用规格"
        TestShoppingFlow.product_id = products[0]["id"]

        logger.info(f"[2/7] 商品详情 → productId={self.product_id}, 价格={products[0]['price']}")

    # ───────── 步骤 3：创建收货地址 ─────────
    def test_03_create_address(self, authenticated_client: APIClient, shopping_data: dict):
        """创建收货地址（下单必要条件）"""
        case = shopping_data["address_save"]
        resp = authenticated_client.post(
            Endpoints.ADDRESS_SAVE,
            json=case["request"]
        )

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"], \
            f"创建地址失败: {resp.errmsg}"

        # data 直接是地址 ID（整数）
        TestShoppingFlow.address_id = resp.data

        logger.info(f"[3/8] 地址创建成功 → addressId={self.address_id}")

    # ───────── 步骤 4：加入购物车 ─────────
    def test_04_cart_add(self, authenticated_client: APIClient, shopping_data: dict):
        """加入购物车"""
        case = shopping_data["cart_add"]
        resp = authenticated_client.post(Endpoints.CART_ADD, json={
            "goodsId": TestShoppingFlow.goods_id,
            "productId": TestShoppingFlow.product_id,
            "number": case["request"]["number"]
        })

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"], \
            f"加购失败: {resp.errmsg}"

        logger.info(f"[4/7] 加入购物车 → 商品数={resp.data}")

    # ───────── 步骤 5：购物车结算 ─────────
    def test_05_cart_checkout(self, authenticated_client: APIClient, shopping_data: dict):
        """结算，获取运费和实付金额"""
        case = shopping_data["cart_checkout"]
        resp = authenticated_client.get(
            Endpoints.CART_CHECKOUT,
            params={"addressId": TestShoppingFlow.address_id}
        )

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"], \
            f"结算失败: {resp.errmsg}"
        for field in case["expected"]["fields"]:
            assert field in resp.data, f"缺少字段: {field}"

        TestShoppingFlow.cart_id = resp.data.get("cartId", 0)
        TestShoppingFlow.coupon_id = resp.data.get("couponId", -1)

        logger.info(
            f"[5/7] 结算 → 总价={resp.data['goodsTotalPrice']}, "
            f"运费={resp.data['freightPrice']}, 实付={resp.data['actualPrice']}"
        )

    # ───────── 步骤 6：提交订单 ─────────
    def test_06_order_submit(self, authenticated_client: APIClient, shopping_data: dict):
        """提交订单"""
        case = shopping_data["order_submit"]
        resp = authenticated_client.post(Endpoints.ORDER_SUBMIT, json={
            "cartId": TestShoppingFlow.cart_id,
            "addressId": TestShoppingFlow.address_id,
            "couponId": TestShoppingFlow.coupon_id,
            "message": "自动化测试订单"
        })

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"], \
            f"下单失败: {resp.errmsg}"

        TestShoppingFlow.order_id = resp.data["orderId"]

        logger.info(f"[6/7] 下单成功 → orderId={self.order_id}")

    # ───────── 步骤 7：订单列表 ─────────
    def test_07_order_list(self, authenticated_client: APIClient, shopping_data: dict):
        """查看订单列表"""
        case = shopping_data["order_list"]
        resp = authenticated_client.get(Endpoints.ORDER_LIST)

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"]

        logger.info(f"[7/7] 订单列表 → 共 {resp.data['total']} 个订单")

    # ───────── 步骤 8：订单详情 ─────────
    def test_08_order_detail(self, authenticated_client: APIClient, shopping_data: dict):
        """查看订单详情"""
        case = shopping_data["order_detail"]
        resp = authenticated_client.get(
            Endpoints.ORDER_DETAIL,
            params={"orderId": TestShoppingFlow.order_id}
        )

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"], \
            f"订单详情获取失败: {resp.errmsg}"
        for field in case["expected"]["fields"]:
            assert field in resp.data, f"缺少字段: {field}"

        info = resp.data["orderInfo"]
        logger.info(
            f"[8/7] 订单详情 → 订单号={info['orderSn']}, "
            f"状态={info.get('orderStatus')}, 金额={info['actualPrice']}"
        )
