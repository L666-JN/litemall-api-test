"""
Litemall 购物车模块测试 — wx-api 用户端前台接口

覆盖范围:
  - 购物车列表 (GET /wx/cart/index)           — 2 例
  - 购物车添加 (POST /wx/cart/add)            — 7 + 1 例（+1 动态）
  - 快速添加 (POST /wx/cart/fastadd)          — 3 + 1 例（+1 动态）
  - 购物车更新 (POST /wx/cart/update)         — 3 + 1 例（+1 动态）
  - 购物车选中 (POST /wx/cart/checked)        — 2 + 1 例（+1 动态）
  - 购物车删除 (POST /wx/cart/delete)         — 2 + 1 例（+1 动态）
  - 购物车数量 (GET /wx/cart/goodscount)      — 2 例
  - 购物车结算 (GET /wx/cart/checkout)        — 2 + 1 例（+1 动态）

用例来源: test_design/litemall_testcases.xlsx → tests/test_data/cart_*_data.yaml
"""
import pytest
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.test_helpers import assert_expected


# ============================================================
#  购物车列表 — GET /wx/cart/index
# ============================================================

INDEX_CASES = [
    "cart_index_success",
    "cart_index_unauthorized",
]


class TestLitemallCartIndex:
    """购物车列表接口 — GET /wx/cart/index"""

    @pytest.mark.parametrize("case_id", INDEX_CASES)
    def test_index(self, api_client: APIClient, authenticated_client: APIClient,
                   cart_index_data: dict, case_id: str):
        case = cart_index_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.get(case["endpoint"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

        # 成功时应包含 cartTotal 和 cartList
        if resp.ok and resp.data:
            assert "cartTotal" in resp.data, "缺少 cartTotal 字段"
            assert isinstance(resp.data.get("cartTotal", {}), dict), \
                "cartTotal 应为 dict"
            assert "cartList" in resp.data, "缺少 cartList 字段"
            assert isinstance(resp.data.get("cartList", []), list), \
                "cartList 应为 list"


# ============================================================
#  购物车添加 — POST /wx/cart/add
# ============================================================

ADD_CASES = [
    "cart_add_unauthorized",
    "cart_add_missing_goodsId",
    "cart_add_missing_productId",
    "cart_add_missing_number",
    "cart_add_zero_number",
    "cart_add_nonexistent_goods",
    "cart_add_nonexistent_product",
]


class TestLitemallCartAdd:
    """购物车添加接口 — POST /wx/cart/add"""

    @pytest.mark.parametrize("case_id", ADD_CASES)
    def test_add(self, api_client: APIClient, authenticated_client: APIClient,
                 cart_add_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 缺字段 / 无效值 / 不存在商品"""
        case = cart_add_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case["request"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_add_success(self, authenticated_client: APIClient,
                         valid_goods_product_pair: dict):
        """动态用例 — 用实际存在的商品 id + productId 加购"""
        pair = valid_goods_product_pair
        resp = authenticated_client.post("/wx/cart/add", json={
            "goodsId": pair["goodsId"],
            "number": 1,
            "productId": pair["productId"],
        })
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"预期 errno=0，实际 errno={resp.errno}, errmsg={resp.errmsg}"

        # 验证购物车确实有该商品
        index_resp = authenticated_client.get("/wx/cart/index")
        assert index_resp.ok, "加购后购物车应可访问"
        in_cart = any(
            it["goodsId"] == pair["goodsId"]
            for it in index_resp.data.get("cartList", [])
        )
        assert in_cart, f"加购后购物车应包含 goodsId={pair['goodsId']}"


# ============================================================
#  快速添加 — POST /wx/cart/fastadd
# ============================================================

FASTADD_CASES = [
    "cart_fastadd_unauthorized",
    "cart_fastadd_missing_goodsId",
    "cart_fastadd_nonexistent_goods",
]


class TestLitemallCartFastAdd:
    """快速添加接口 — POST /wx/cart/fastadd"""

    @pytest.mark.parametrize("case_id", FASTADD_CASES)
    def test_fastadd(self, api_client: APIClient, authenticated_client: APIClient,
                     cart_fastadd_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 缺字段 / 不存在商品"""
        case = cart_fastadd_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case["request"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_fastadd_success(self, authenticated_client: APIClient,
                             valid_goods_product_pair: dict):
        """动态用例 — 用实际存在的商品快速加购"""
        pair = valid_goods_product_pair
        resp = authenticated_client.post("/wx/cart/fastadd", json={
            "goodsId": pair["goodsId"],
            "number": 1,
            "productId": pair["productId"],
        })
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"预期 errno=0，实际 errno={resp.errno}, errmsg={resp.errmsg}"


# ============================================================
#  购物车更新 — POST /wx/cart/update
# ============================================================

UPDATE_CASES = [
    "cart_update_unauthorized",
    "cart_update_missing_goodsId",
    "cart_update_nonexistent",
]


class TestLitemallCartUpdate:
    """购物车更新接口 — POST /wx/cart/update"""

    @pytest.mark.parametrize("case_id", UPDATE_CASES)
    def test_update(self, api_client: APIClient, authenticated_client: APIClient,
                    cart_update_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 缺字段 / 不存在条目"""
        case = cart_update_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case["request"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_update_success(self, authenticated_client: APIClient,
                            cart_with_item: dict):
        """动态用例 — 修改购物车中已有条目的数量"""
        item = cart_with_item
        resp = authenticated_client.post("/wx/cart/update", json={
            "id": item["id"],
            "number": 5,
            "goodsId": item["goodsId"],
            "productId": item["productId"],
        })
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"预期 errno=0，实际 errno={resp.errno}, errmsg={resp.errmsg}"

        # 验证数量已更新
        index_resp = authenticated_client.get("/wx/cart/index")
        updated = next(
            (it for it in index_resp.data.get("cartList", [])
             if it["id"] == item["id"]), None
        )
        assert updated is not None, "更新后购物车条目应存在"
        assert updated["number"] == 5, \
            f"预期 number=5，实际 number={updated['number']}"


# ============================================================
#  购物车选中 — POST /wx/cart/checked
# ============================================================

CHECKED_CASES = [
    "cart_checked_unauthorized",
    "cart_checked_nonexistent_product",
]


class TestLitemallCartChecked:
    """购物车选中接口 — POST /wx/cart/checked"""

    @pytest.mark.parametrize("case_id", CHECKED_CASES)
    def test_checked(self, api_client: APIClient, authenticated_client: APIClient,
                     cart_checked_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 无效 productId"""
        case = cart_checked_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case["request"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_checked_toggle(self, authenticated_client: APIClient,
                            cart_with_item: dict):
        """动态用例 — 切换购物车条目的选中状态"""
        item = cart_with_item

        # 取消选中
        resp = authenticated_client.post("/wx/cart/checked", json={
            "isChecked": 0,
            "productIds": [item["productId"]],
        })
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"取消选中失败: errno={resp.errno}"

        # 查看购物车，验证状态
        index_resp = authenticated_client.get("/wx/cart/index")
        uncheck = next(
            (it for it in index_resp.data.get("cartList", [])
             if it["productId"] == item["productId"]), None
        )
        assert uncheck is not None, "条目应仍在购物车中"
        assert not uncheck.get("checked"), "取消选中后 checked 应为 False"

        # 重新选中
        resp = authenticated_client.post("/wx/cart/checked", json={
            "isChecked": 1,
            "productIds": [item["productId"]],
        })
        assert resp.errno == 0, f"重新选中失败: errno={resp.errno}"

        index_resp = authenticated_client.get("/wx/cart/index")
        check = next(
            (it for it in index_resp.data.get("cartList", [])
             if it["productId"] == item["productId"]), None
        )
        assert check.get("checked"), "重新选中后 checked 应为 True"


# ============================================================
#  购物车删除 — POST /wx/cart/delete
# ============================================================

DELETE_CASES = [
    "cart_delete_unauthorized",
    "cart_delete_nonexistent_product",
]


class TestLitemallCartDelete:
    """购物车删除接口 — POST /wx/cart/delete"""

    @pytest.mark.parametrize("case_id", DELETE_CASES)
    def test_delete(self, api_client: APIClient, authenticated_client: APIClient,
                    cart_delete_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 无效 productId"""
        case = cart_delete_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case["request"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_delete_success(self, authenticated_client: APIClient,
                            cart_with_item: dict):
        """动态用例 — 删除购物车中的条目（cart_with_item 已预创建）"""
        item = cart_with_item
        resp = authenticated_client.post("/wx/cart/delete", json={
            "productIds": [item["productId"]],
        })
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"删除失败: errno={resp.errno}, errmsg={resp.errmsg}"

        # 验证该条目已不在购物车中
        index_resp = authenticated_client.get("/wx/cart/index")
        still_in = any(
            it["productId"] == item["productId"]
            for it in index_resp.data.get("cartList", [])
        )
        assert not still_in, "删除后该条目不应仍在购物车中"


# ============================================================
#  购物车数量 — GET /wx/cart/goodscount
# ============================================================

COUNT_CASES = [
    "cart_count_no_auth",
    "cart_count_success",
]


class TestLitemallCartCount:
    """购物车数量接口 — GET /wx/cart/goodscount"""

    @pytest.mark.parametrize("case_id", COUNT_CASES)
    def test_count(self, api_client: APIClient, authenticated_client: APIClient,
                   cart_count_data: dict, case_id: str):
        """参数化用例 — 未认证 / 已认证查数量"""
        case = cart_count_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.get(case["endpoint"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

        # 成功后 data 应为整数 >= 0
        if resp.ok:
            assert isinstance(resp.data, int), \
                f"goodscount 的 data 应为整数，实际类型: {type(resp.data)}"
            assert resp.data >= 0, f"购物车数量应 >= 0，实际: {resp.data}"


# ============================================================
#  购物车结算 — GET /wx/cart/checkout
# ============================================================

CHECKOUT_CASES = [
    "cart_checkout_unauthorized",
    "cart_checkout_default_params",
]


class TestLitemallCartCheckout:
    """购物车结算接口 — GET /wx/cart/checkout"""

    @pytest.mark.parametrize("case_id", CHECKOUT_CASES)
    def test_checkout(self, api_client: APIClient, authenticated_client: APIClient,
                      cart_checkout_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 缺参数"""
        case = cart_checkout_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        params = case.get("params")
        resp = client.get(case["endpoint"], params=params)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_checkout_success(self, authenticated_client: APIClient,
                              cart_with_item: dict):
        """动态用例 — 有购物车条目时结算预览"""
        item = cart_with_item
        resp = authenticated_client.get("/wx/cart/checkout", params=(
            "cartId=0&addressId=0&couponId=0"
            "&userCouponId=0&grouponRulesId=0"
        ))
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, \
            f"预期 errno=0，实际 errno={resp.errno}, errmsg={resp.errmsg}"
        assert resp.data is not None, "checkout data 不应为空"

        # 结算返回应包含核心字段
        for field in ["checkedGoodsList", "goodsTotalPrice", "actualPrice",
                       "orderTotalPrice", "freightPrice"]:
            assert field in resp.data, f"checkout 缺少字段: {field}"

        # checkedGoodsList 应为数组且非空
        assert isinstance(resp.data["checkedGoodsList"], list), \
            "checkedGoodsList 应为 list"
        assert len(resp.data["checkedGoodsList"]) > 0, \
            "已选中的购物车商品列表不应为空"
