"""
Litemall 认证模块测试 — wx-api 用户端前台接口

覆盖范围:
  - 登录 (POST /wx/auth/login)       — 9 个用例
  - 登出 (POST /wx/auth/logout)      — 3 个用例
  - 用户信息 (GET /wx/auth/info)      — 3 个用例
  - 注册 (POST /wx/auth/register)    — 7 个用例
  - 密码重置 (POST /wx/auth/reset)    — 3 个用例

用例来源: test_design/litemall_testcases.xlsx → tests/test_data/auth_*_data.yaml
"""
import pytest
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.test_helpers import assert_expected


# ============================================================
#  登录模块 — 全部无需认证，参数化
# ============================================================

LOGIN_CASES = [
    "login_success",
    "login_wrong_password",
    "login_nonexistent_user",
    "login_empty_username",
    "login_empty_password",
    "login_empty_both",
    "login_username_with_spaces",
    "login_sql_injection",
    "login_xss_attempt",
]


class TestLitemallLogin:
    """登录接口 — POST /wx/auth/login（数据驱动）"""

    @pytest.mark.parametrize("case_id", LOGIN_CASES)
    def test_login(self, api_client: APIClient, auth_login_data: dict, case_id: str):
        case = auth_login_data[case_id]
        endpoint = case["endpoint"]

        resp = api_client.post(endpoint, json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))

        # 登录成功时的额外校验
        if case_id == "login_success":
            assert resp.data is not None, "登录成功但 data 为空"
            assert "token" in resp.data, "登录成功但缺少 token"
            assert isinstance(resp.data["token"], str) and len(resp.data["token"]) > 0, \
                "token 应是非空字符串"
            if "userInfo" in resp.data:
                assert "nickName" in resp.data["userInfo"], \
                    f"userInfo 缺少 nickName: {resp.data['userInfo']}"

        assert_expected(resp, case["expected"])


# ============================================================
#  登出模块 — 部分需认证
# ============================================================

class TestLitemallLogout:
    """登出接口 — POST /wx/auth/logout"""

    def test_logout_with_token(self, authenticated_client: APIClient, auth_logout_data: dict):
        """带有效 token 登出 → errno:0"""
        case = auth_logout_data["logout_with_token"]
        resp = authenticated_client.post(case["endpoint"])
        APIAssertions.assert_status_code(resp, 200)
        assert_expected(resp, case["expected"])

    def test_logout_no_token(self, api_client: APIClient, auth_logout_data: dict):
        """不带 token 登出 → errno:501"""
        case = auth_logout_data["logout_no_token"]
        resp = api_client.post(case["endpoint"])
        APIAssertions.assert_status_code(resp, 200)
        assert_expected(resp, case["expected"])

    def test_logout_invalid_token(self, api_client: APIClient, auth_logout_data: dict):
        """带伪造 token 登出 → errno:501"""
        case = auth_logout_data["logout_invalid_token"]
        api_client.set_token("invalid_token_logout_test_fake_xyz")
        try:
            resp = api_client.post(case["endpoint"])
            APIAssertions.assert_status_code(resp, 200)
            assert_expected(resp, case["expected"])
        finally:
            api_client.set_token(None)


# ============================================================
#  用户信息模块 — 部分需认证
# ============================================================

class TestLitemallUserInfo:
    """用户信息接口 — GET /wx/auth/info"""

    def test_user_info_with_token(self, authenticated_client: APIClient, auth_info_data: dict):
        """带有效 token 获取用户信息 → errno:0, data 含 nickName 等"""
        case = auth_info_data["user_info_with_token"]
        resp = authenticated_client.get(case["endpoint"])
        APIAssertions.assert_status_code(resp, 200)
        assert_expected(resp, case["expected"])

    def test_user_info_no_token(self, api_client: APIClient, auth_info_data: dict):
        """不带 token 获取用户信息 → errno:501"""
        case = auth_info_data["user_info_no_token"]
        resp = api_client.get(case["endpoint"])
        APIAssertions.assert_status_code(resp, 200)
        assert_expected(resp, case["expected"])

    def test_user_info_invalid_token(self, api_client: APIClient, auth_info_data: dict):
        """带伪造 token 获取用户信息 → errno:501"""
        case = auth_info_data["user_info_invalid_token"]
        api_client.set_token("invalid_token_info_test_fake_xyz")
        try:
            resp = api_client.get(case["endpoint"])
            APIAssertions.assert_status_code(resp, 200)
            assert_expected(resp, case["expected"])
        finally:
            api_client.set_token(None)


# ============================================================
#  注册模块 — 全部无需认证，参数化
# ============================================================

REGISTER_CASES = [
    "register_missing_wxcode",
    "register_empty_username",
    "register_empty_password",
    "register_empty_mobile",
    "register_duplicate_username",
    "register_invalid_mobile",
    "register_short_password",
]


class TestLitemallRegister:
    """注册接口 — POST /wx/auth/register（数据驱动）"""

    @pytest.mark.parametrize("case_id", REGISTER_CASES)
    def test_register(self, api_client: APIClient, auth_register_data: dict, case_id: str):
        case = auth_register_data[case_id]
        endpoint = case["endpoint"]

        resp = api_client.post(endpoint, json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])


# ============================================================
#  密码重置模块 — 全部无需认证，参数化
# ============================================================

RESET_CASES = [
    "reset_with_valid_data",
    "reset_empty_password",
    "reset_empty_mobile",
]


class TestLitemallReset:
    """密码重置接口 — POST /wx/auth/reset（数据驱动）

    ⚠ 注意: reset_with_valid_data 依赖有效验证码，
    在真实环境中可能因验证码无效而返回非 0。
    """

    @pytest.mark.parametrize("case_id", RESET_CASES)
    def test_reset(self, api_client: APIClient, auth_reset_data: dict, case_id: str):
        case = auth_reset_data[case_id]
        endpoint = case["endpoint"]

        resp = api_client.post(endpoint, json=case.get("request", {}))
        APIAssertions.assert_status_code(resp, case.get("expected_status", 200))
        assert_expected(resp, case["expected"])
