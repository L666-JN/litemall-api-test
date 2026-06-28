"""
Litemall 首页模块测试 — wx-api 用户端前台接口

覆盖范围:
  - 首页数据 (GET /wx/home/index)    — 1 例
  - 关于页面 (GET /wx/home/about)    — 1 例

用例来源: test_design/litemall_testcases.xlsx → tests/test_data/home_data.yaml
"""
import pytest
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.test_helpers import assert_expected


class TestLitemallHome:
    """首页模块 — 均为公开接口，无需认证"""

    def test_index(self, api_client: APIClient, home_data: dict):
        """GET /wx/home/index — 验证首页各板块数据"""
        case = home_data["home_index_success"]
        resp = api_client.get(case["endpoint"])

        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

        # 验证各板块为非空 list
        for key in ["newGoodsList", "hotGoodsList", "banner", "channel", "brandList"]:
            assert key in resp.data, f"缺少板块: {key}"
            val = resp.data[key]
            assert isinstance(val, list), f"{key} 应为 list，实际: {type(val)}"

    def test_about(self, api_client: APIClient, home_data: dict):
        """GET /wx/home/about — 验证关于页面信息"""
        case = home_data["home_about_success"]
        resp = api_client.get(case["endpoint"])

        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])

        # 验证关键字段有值
        for key in ["name", "address", "phone"]:
            assert key in resp.data, f"缺少字段: {key}"
            assert resp.data[key], f"{key} 不应为空"
