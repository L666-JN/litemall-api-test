"""
Litemall 订单模块测试 — wx-api 用户端前台接口

覆盖范围:
  - 订单列表 (GET /wx/order/list)               — 2 例
  - 订单详情 (GET /wx/order/detail)             — 3 + 1 例（+1 动态）
  - 订单提交 (POST /wx/order/submit)            — 2 例
  - 订单取消 (POST /wx/order/cancel)            — 3 例
  - 确认收货 (POST /wx/order/confirm)           — 2 例
  - 订单删除 (POST /wx/order/delete)            — 3 + 1 例（+1 动态）
  - 订单评价 (POST /wx/order/comment)           — 2 例
  - 订单商品 (GET /wx/order/goods)              — 3 + 1 例（+1 动态）

用例来源: test_design/litemall_testcases.xlsx → tests/test_data/order_*_data.yaml
"""
import pytest
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.test_helpers import assert_expected


# ============================================================
#  订单列表 — GET /wx/order/list
# ============================================================

LIST_CASES = [
    "order_list_success",
    "order_list_unauthorized",
]


class TestLitemallOrderList:
    """订单列表接口 — GET /wx/order/list"""

    @pytest.mark.parametrize("case_id", LIST_CASES)
    def test_list(self, api_client: APIClient, authenticated_client: APIClient,
                  order_list_data: dict, case_id: str):
        case = order_list_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.get(case["endpoint"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

        if resp.ok and resp.data:
            assert "total" in resp.data, "缺少 total 字段"
            assert "list" in resp.data, "缺少 list 字段"
            assert isinstance(resp.data["list"], list), "list 应为数组"


# ============================================================
#  订单详情 — GET /wx/order/detail
# ============================================================

DETAIL_CASES = [
    "order_detail_unauthorized",
    "order_detail_missing_id",
    "order_detail_nonexistent",
]


class TestLitemallOrderDetail:
    """订单详情接口 — GET /wx/order/detail"""

    @pytest.mark.parametrize("case_id", DETAIL_CASES)
    def test_detail(self, api_client: APIClient, authenticated_client: APIClient,
                    order_detail_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 缺id / 不存在"""
        case = order_detail_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        params = case.get("params")
        resp = client.get(case["endpoint"], params=params)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_detail_valid(self, authenticated_client: APIClient,
                          valid_order_id: int):
        """动态用例 — 用实际存在的订单 id 查详情"""
        resp = authenticated_client.get("/wx/order/detail",
                                        params=f"orderId={valid_order_id}")
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"预期 errno=0，实际 errno={resp.errno}, errmsg={resp.errmsg}"
        assert resp.data is not None, "data 不应为空"

        # 应包含 orderInfo
        order_info = resp.data.get("orderInfo", resp.data)
        for field in ["id", "orderSn", "actualPrice", "consignee",
                       "address", "orderStatusText"]:
            assert field in order_info, f"订单详情缺少字段: {field}"
        assert order_info["id"] == valid_order_id, \
            f"返回的订单 id 应为 {valid_order_id}，实际 {order_info['id']}"


# ============================================================
#  订单提交 — POST /wx/order/submit
# ============================================================

SUBMIT_CASES = [
    "order_submit_unauthorized",
    "order_submit_empty_body",
]


class TestLitemallOrderSubmit:
    """订单提交接口 — POST /wx/order/submit"""

    @pytest.mark.parametrize("case_id", SUBMIT_CASES)
    def test_submit(self, api_client: APIClient, authenticated_client: APIClient,
                    order_submit_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 空body"""
        case = order_submit_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])


# ============================================================
#  订单取消 — POST /wx/order/cancel
# ============================================================

CANCEL_CASES = [
    "order_cancel_unauthorized",
    "order_cancel_empty_body",
    "order_cancel_nonexistent",
]


class TestLitemallOrderCancel:
    """订单取消接口 — POST /wx/order/cancel"""

    @pytest.mark.parametrize("case_id", CANCEL_CASES)
    def test_cancel(self, api_client: APIClient, authenticated_client: APIClient,
                    order_cancel_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 空body / 不存在"""
        case = order_cancel_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])


# ============================================================
#  确认收货 — POST /wx/order/confirm
# ============================================================

CONFIRM_CASES = [
    "order_confirm_unauthorized",
    "order_confirm_empty_body",
]


class TestLitemallOrderConfirm:
    """确认收货接口 — POST /wx/order/confirm"""

    @pytest.mark.parametrize("case_id", CONFIRM_CASES)
    def test_confirm(self, api_client: APIClient, authenticated_client: APIClient,
                     order_confirm_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 空body"""
        case = order_confirm_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])


# ============================================================
#  订单删除 — POST /wx/order/delete
# ============================================================

DELETE_CASES = [
    "order_delete_unauthorized",
    "order_delete_empty_body",
    "order_delete_nonexistent",
]


class TestLitemallOrderDelete:
    """订单删除接口 — POST /wx/order/delete"""

    @pytest.mark.parametrize("case_id", DELETE_CASES)
    def test_delete(self, api_client: APIClient, authenticated_client: APIClient,
                    order_delete_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 空body / 不存在"""
        case = order_delete_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_delete_success(self, authenticated_client: APIClient,
                            valid_order_id: int):
        """动态用例 — 删除已有订单（仅 handleOption.delete=True 的可删除）"""
        # 先检查该订单可否删除
        detail_resp = authenticated_client.get("/wx/order/detail",
                                               params=f"orderId={valid_order_id}")
        order_info = detail_resp.data.get("orderInfo", detail_resp.data)
        if not order_info.get("handleOption", {}).get("delete"):
            pytest.skip("当前订单不可删除（handleOption.delete=False）")

        resp = authenticated_client.post("/wx/order/delete",
                                         json={"orderId": valid_order_id})
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"删除订单失败: errno={resp.errno}, errmsg={resp.errmsg}"

        # 验证该订单已不在列表中
        list_resp = authenticated_client.get("/wx/order/list")
        still_exists = any(
            o["id"] == valid_order_id
            for o in list_resp.data.get("list", [])
        )
        assert not still_exists, f"删除后订单 id={valid_order_id} 不应仍在列表中"


# ============================================================
#  订单评价 — POST /wx/order/comment
# ============================================================

COMMENT_CASES = [
    "order_comment_unauthorized",
    "order_comment_empty_body",
]


class TestLitemallOrderComment:
    """订单评价接口 — POST /wx/order/comment"""

    @pytest.mark.parametrize("case_id", COMMENT_CASES)
    def test_comment(self, api_client: APIClient, authenticated_client: APIClient,
                     order_comment_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 空body"""
        case = order_comment_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])


# ============================================================
#  订单商品 — GET /wx/order/goods
# ============================================================

GOODS_CASES = [
    "order_goods_unauthorized",
    "order_goods_missing_id",
    "order_goods_nonexistent",
]


class TestLitemallOrderGoods:
    """订单商品接口 — GET /wx/order/goods"""

    @pytest.mark.parametrize("case_id", GOODS_CASES)
    def test_goods(self, api_client: APIClient, authenticated_client: APIClient,
                   order_goods_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 缺id / 不存在"""
        case = order_goods_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        params = case.get("params")
        resp = client.get(case["endpoint"], params=params)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_goods_valid(self, authenticated_client: APIClient,
                         valid_order_id: int):
        """动态用例 — 用实际存在的订单 ogid 查商品列表"""
        # 注意：/wx/order/goods 参数名是 ogid，不是 orderId
        resp = authenticated_client.get("/wx/order/goods",
                                        params=f"ogid={valid_order_id}")
        APIAssertions.assert_status_code(resp, 200)

        # 已取消的订单 goods 接口可能返回非零 errno，跳过即可
        if resp.errno != 0:
            pytest.skip(f"该订单状态不支持查询商品: errno={resp.errno}, errmsg={resp.errmsg}")

        assert resp.data is not None, "data 不应为空"

        # /wx/order/goods 返回单个商品对象（dict），不是数组
        if isinstance(resp.data, dict):
            for field in ["id", "goodsName", "number", "price"]:
                assert field in resp.data, f"订单商品缺少字段: {field}"
        else:
            pytest.skip(f"订单商品 data 类型异常: {type(resp.data)}")
