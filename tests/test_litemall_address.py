"""
Litemall 地址模块测试 — wx-api 用户端前台接口

覆盖范围:
  - 地址列表 (GET /wx/address/list)               — 2 例
  - 地址详情 (GET /wx/address/detail)             — 3 + 1 例（+1 动态）
  - 地址保存 (POST /wx/address/save)              — 4 + 2 例（+2 动态：新建 / 更新）
  - 地址删除 (POST /wx/address/delete)            — 3 + 1 例（+1 动态）

用例来源: test_design/litemall_testcases.xlsx → tests/test_data/address_*_data.yaml
"""
import pytest
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.test_helpers import assert_expected


# ============================================================
#  地址列表 — GET /wx/address/list
# ============================================================

LIST_CASES = [
    "address_list_success",
    "address_list_unauthorized",
]


class TestLitemallAddressList:
    """地址列表接口 — GET /wx/address/list"""

    @pytest.mark.parametrize("case_id", LIST_CASES)
    def test_list(self, api_client: APIClient, authenticated_client: APIClient,
                  address_list_data: dict, case_id: str):
        case = address_list_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.get(case["endpoint"])
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

        # 成功时验证分页结构
        if resp.ok and resp.data:
            assert "total" in resp.data, "缺少 total 字段"
            assert "list" in resp.data, "缺少 list 字段"
            assert isinstance(resp.data["list"], list), "list 应为数组"


# ============================================================
#  地址详情 — GET /wx/address/detail
# ============================================================

DETAIL_CASES = [
    "address_detail_unauthorized",
    "address_detail_missing_id",
    "address_detail_nonexistent",
]


class TestLitemallAddressDetail:
    """地址详情接口 — GET /wx/address/detail"""

    @pytest.mark.parametrize("case_id", DETAIL_CASES)
    def test_detail(self, api_client: APIClient, authenticated_client: APIClient,
                    address_detail_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 缺id / 不存在"""
        case = address_detail_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        params = case.get("params")
        resp = client.get(case["endpoint"], params=params)
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_detail_valid(self, authenticated_client: APIClient,
                          valid_address_id: int):
        """动态用例 — 用实际存在的地址 id 查详情"""
        resp = authenticated_client.get("/wx/address/detail",
                                        params=f"id={valid_address_id}")
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"预期 errno=0，实际 errno={resp.errno}, errmsg={resp.errmsg}"
        assert resp.data is not None, "data 不应为空"

        # 验证地址核心字段
        for field in ["id", "name", "tel", "province", "city", "county",
                       "addressDetail", "areaCode", "isDefault"]:
            assert field in resp.data, f"缺少字段: {field}"
        assert resp.data["id"] == valid_address_id, \
            f"返回的地址 id 应为 {valid_address_id}，实际 {resp.data['id']}"


# ============================================================
#  地址保存 — POST /wx/address/save
# ============================================================

SAVE_CASES = [
    "address_save_unauthorized",
    "address_save_empty_body",
    "address_save_missing_fields",
    "address_save_update_nonexistent",
]


def _address_payload(**overrides):
    """构建地址保存/更新的标准请求体"""
    base = {
        "name": "测试用户",
        "tel": "13800138000",
        "province": "广东省",
        "city": "广州市",
        "county": "天河区",
        "addressDetail": "测试路100号",
        "areaCode": "440106",
        "isDefault": False,
    }
    base.update(overrides)
    return base


class TestLitemallAddressSave:
    """地址保存接口 — POST /wx/address/save"""

    @pytest.mark.parametrize("case_id", SAVE_CASES)
    def test_save(self, api_client: APIClient, authenticated_client: APIClient,
                  address_save_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 空body / 缺字段 / 更新不存在"""
        case = address_save_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_save_create(self, authenticated_client: APIClient):
        """动态用例 — 创建新地址，验证 data 返回新 id"""
        payload = _address_payload(name="新建地址")
        resp = authenticated_client.post("/wx/address/save", json=payload)

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"新建地址失败: errno={resp.errno}, errmsg={resp.errmsg}"
        assert resp.data is not None, "新建地址应返回 id"
        assert isinstance(resp.data, int), \
            f"新建地址返回应为整数 id，实际: {type(resp.data)}"
        new_id = resp.data

        # 验证地址列表中确实有这个地址
        list_resp = authenticated_client.get("/wx/address/list")
        assert list_resp.ok
        created = next(
            (a for a in list_resp.data.get("list", []) if a["id"] == new_id), None
        )
        assert created is not None, f"新建的地址 id={new_id} 应在列表中存在"
        assert created["name"] == "新建地址", \
            f"地址名应为'新建地址'，实际: {created['name']}"

        # 清理
        del_resp = authenticated_client.post("/wx/address/delete",
                                             json={"id": new_id})
        assert del_resp.ok, f"清理新建地址失败: {del_resp.errmsg}"

    def test_save_update(self, authenticated_client: APIClient,
                         valid_address_id: int):
        """动态用例 — 更新已有地址"""
        payload = _address_payload(
            id=valid_address_id,
            name="已更新地址",
            addressDetail="更新后的详细地址",
        )
        resp = authenticated_client.post("/wx/address/save", json=payload)

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"更新地址失败: errno={resp.errno}, errmsg={resp.errmsg}"

        # 验证更新生效
        detail_resp = authenticated_client.get("/wx/address/detail",
                                               params=f"id={valid_address_id}")
        assert detail_resp.ok
        assert detail_resp.data["name"] == "已更新地址", \
            f"name 应为'已更新地址'，实际: {detail_resp.data['name']}"
        assert detail_resp.data["addressDetail"] == "更新后的详细地址", \
            f"addressDetail 应更新"


# ============================================================
#  地址删除 — POST /wx/address/delete
# ============================================================

DELETE_CASES = [
    "address_delete_unauthorized",
    "address_delete_empty_body",
    "address_delete_nonexistent",
]


class TestLitemallAddressDelete:
    """地址删除接口 — POST /wx/address/delete"""

    @pytest.mark.parametrize("case_id", DELETE_CASES)
    def test_delete(self, api_client: APIClient, authenticated_client: APIClient,
                    address_delete_data: dict, case_id: str):
        """静态参数化用例 — 未认证 / 空body / 不存在"""
        case = address_delete_data[case_id]
        client = authenticated_client if case.get("need_auth") else api_client

        resp = client.post(case["endpoint"], json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

    def test_delete_success(self, authenticated_client: APIClient):
        """动态用例 — 创建地址后删除，验证已从列表中移除"""
        # 先创建一个地址用于删除
        payload = _address_payload(name="待删除地址")
        create_resp = authenticated_client.post("/wx/address/save", json=payload)
        assert create_resp.ok, f"创建地址失败: {create_resp.errmsg}"
        new_id = create_resp.data

        # 确认创建成功
        list_resp = authenticated_client.get("/wx/address/list")
        assert any(a["id"] == new_id
                   for a in list_resp.data.get("list", [])), \
            "删除前地址应在列表中"

        # 执行删除
        resp = authenticated_client.post("/wx/address/delete", json={"id": new_id})
        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == 0, f"删除失败: errno={resp.errno}, errmsg={resp.errmsg}"

        # 验证地址已不在列表中
        list_resp = authenticated_client.get("/wx/address/list")
        still_exists = any(
            a["id"] == new_id for a in list_resp.data.get("list", [])
        )
        assert not still_exists, f"删除后地址 id={new_id} 不应仍在列表中"
