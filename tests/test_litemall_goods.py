"""
Litemall 商品模块测试 — wx-api 用户端前台接口

覆盖范围:
  - 商品列表 (GET /wx/goods/list)         — 8 + 0 例（全部静态参数化）
  - 商品详情 (GET /wx/goods/detail)       — 3 + 1 例（+1 动态 id）
  - 商品分类 (GET /wx/goods/category)     — 2 + 1 例（+1 动态 id）
  - 相关商品 (GET /wx/goods/related)      — 2 + 1 例（+1 动态 id）
  - 商品统计 (GET /wx/goods/count)        — 1 例

用例来源: test_design/litemall_testcases.xlsx → tests/test_data/goods_*_data.yaml
"""
import pytest
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.test_helpers import assert_expected


# ============================================================
#  商品列表 — 全部无需认证，参数化
# ============================================================

LIST_CASES = [
    "goods_list_default",
    "goods_list_page2_size3",
    "goods_list_keyword_valid",
    "goods_list_keyword_none",
    "goods_list_is_new",
    "goods_list_is_hot",
    "goods_list_empty_category",
    "goods_list_sort_invalid",
]


class TestLitemallGoodsList:
    """商品列表接口 — GET /wx/goods/list（数据驱动）"""

    @pytest.mark.parametrize("case_id", LIST_CASES)
    def test_list(self, api_client: APIClient, goods_list_data: dict, case_id: str):
        case = goods_list_data[case_id]
        endpoint = case["endpoint"]
        params = case.get("params")

        resp = api_client.get(endpoint, params=params)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

        # 列表类用例：data.list 应为数组
        if resp.ok and resp.data and "list" in resp.data:
            assert isinstance(resp.data["list"], list), \
                f"list 字段应为数组: {type(resp.data['list'])}"

        # keyword_valid：应包含 filterCategoryList
        if case_id == "goods_list_keyword_valid" and resp.ok:
            assert "filterCategoryList" in resp.data, \
                "关键词搜索结果应包含 filterCategoryList"


# ============================================================
#  商品详情 — 参数化（静态）+ 动态
# ============================================================

DETAIL_CASES = [
    "goods_detail_missing_id",
    "goods_detail_zero_id",
    "goods_detail_nonexistent",
]


class TestLitemallGoodsDetail:
    """商品详情接口 — GET /wx/goods/detail"""

    @pytest.mark.parametrize("case_id", DETAIL_CASES)
    def test_detail(self, api_client: APIClient, goods_detail_data: dict, case_id: str):
        """静态参数化用例 — 缺id / id=0 / 不存在"""
        case = goods_detail_data[case_id]
        endpoint = case["endpoint"]
        params = case.get("params")

        resp = api_client.get(endpoint, params=params)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_detail_valid(self, api_client: APIClient, valid_goods_id: int):
        """动态用例 — 用实际存在的商品 id 查详情"""
        resp = api_client.get("/wx/goods/detail", params=f"id={valid_goods_id}")
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"预期 errno=0，实际 errno={resp.errno}"
        assert resp.data is not None, "data 不应为空"
        # 验证关键字段
        for field in ["info", "specificationList", "productList",
                       "attribute", "issue", "comment"]:
            assert field in resp.data, f"缺少字段: {field}"
        # info 子字段
        info_fields = ["id", "name", "categoryId", "brief", "isOnSale"]
        for field in info_fields:
            assert field in resp.data["info"], f"info 缺少字段: {field}"


# ============================================================
#  商品分类 — 参数化（静态）+ 动态
# ============================================================

CATEGORY_CASES = [
    "goods_category_missing_id",
    "goods_category_nonexistent",
]


class TestLitemallGoodsCategory:
    """商品分类接口 — GET /wx/goods/category"""

    @pytest.mark.parametrize("case_id", CATEGORY_CASES)
    def test_category(self, api_client: APIClient, goods_category_data: dict, case_id: str):
        """静态参数化用例 — 缺id / 不存在"""
        case = goods_category_data[case_id]
        endpoint = case["endpoint"]
        params = case.get("params")

        resp = api_client.get(endpoint, params=params)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_category_valid(self, api_client: APIClient, valid_category_id: int):
        """动态用例 — 用实际存在的分类 id 查分类"""
        resp = api_client.get("/wx/goods/category", params=f"id={valid_category_id}")
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"预期 errno=0，实际 errno={resp.errno}"
        assert resp.data is not None, "data 不应为空"
        for field in ["currentCategory", "brotherCategory", "parentCategory"]:
            assert field in resp.data, f"缺少字段: {field}"


# ============================================================
#  相关商品 — 参数化（静态）+ 动态
# ============================================================

RELATED_CASES = [
    "goods_related_missing_id",
    "goods_related_invalid_id",
]


class TestLitemallGoodsRelated:
    """相关商品接口 — GET /wx/goods/related"""

    @pytest.mark.parametrize("case_id", RELATED_CASES)
    def test_related(self, api_client: APIClient, goods_related_data: dict, case_id: str):
        """静态参数化用例 — 缺id / 不存在"""
        case = goods_related_data[case_id]
        endpoint = case["endpoint"]
        params = case.get("params")

        resp = api_client.get(endpoint, params=params)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_related_valid(self, api_client: APIClient, valid_goods_id: int):
        """动态用例 — 用实际存在的商品 id 查相关商品"""
        resp = api_client.get("/wx/goods/related", params=f"id={valid_goods_id}")
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"预期 errno=0，实际 errno={resp.errno}"
        assert resp.data is not None, "data 不应为空"
        for field in ["list"]:
            assert field in resp.data, f"缺少字段: {field}"


# ============================================================
#  商品统计 — 全部无需认证，参数化
# ============================================================

COUNT_CASES = [
    "goods_count_default",
]


class TestLitemallGoodsCount:
    """商品统计接口 — GET /wx/goods/count"""

    @pytest.mark.parametrize("case_id", COUNT_CASES)
    def test_count(self, api_client: APIClient, goods_count_data: dict, case_id: str):
        case = goods_count_data[case_id]
        endpoint = case["endpoint"]

        resp = api_client.get(endpoint)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

        # data 是整数标量（非对象），类型校验
        if resp.ok:
            assert isinstance(resp.data, int), \
                f"count 的 data 应为整数，实际类型: {type(resp.data)}"
            assert resp.data > 0, f"商品总数应 > 0，实际: {resp.data}"
