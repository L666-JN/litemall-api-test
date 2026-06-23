# tests/test_litemall_auth.py
"""
Litemall 用户认证 API 测试用例（数据驱动）
基路径: /wx/auth
"""
import pytest
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.logger import get_logger
from config.endpoints import Endpoints

logger = get_logger(__name__)

# 登录测试用例 ID 列表
LOGIN_CASES = [
    "login_success",
    "login_wrong_password",
    "login_nonexistent_user",
    "login_empty_username",
    "login_empty_password",
]


class TestLitemallLogin:
    """Litemall 登录测试类"""

    @pytest.mark.parametrize("case_id", LOGIN_CASES)
    def test_login(self, api_client: APIClient, auth_data: dict, case_id: str):
        """数据驱动的登录测试"""
        case = auth_data[case_id]
        expected = case["expected"]

        resp = api_client.post(Endpoints.AUTH_LOGIN, json=case["request"])
        APIAssertions.assert_status_code(resp, 200)

        # 验证 errno
        if "errno" in expected:
            assert resp.errno == expected["errno"], \
                f"[{case_id}] errno 不匹配: 期望 {expected['errno']}, 实际 {resp.errno}"
        elif "errno_not" in expected:
            assert resp.errno != expected["errno_not"], \
                f"[{case_id}] errno 不应为 {expected['errno_not']}, 实际: {resp}"

        # 验证 errmsg
        if "errmsg" in expected:
            assert resp.errmsg == expected["errmsg"]
        elif "errmsg_contains" in expected:
            assert expected["errmsg_contains"] in resp.errmsg, \
                f"[{case_id}] errmsg 不包含 '{expected['errmsg_contains']}': {resp.errmsg}"

        # 成功时验证返回数据
        if expected.get("errno") == 0:
            if expected.get("has_token"):
                assert resp.data.get("token"), "缺少 token"
                TestLitemallLogin._token = resp.data["token"]
            if "nickName" in expected:
                assert resp.data["userInfo"]["nickName"] == expected["nickName"]

        logger.info(f"[{case_id}] 通过: {case['description']}")


class TestLitemallAuth:
    """Litemall 认证后接口测试类（需 token）"""

    def test_get_user_info_with_token(self, authenticated_client: APIClient, auth_data: dict):
        """测试：登录后获取用户信息（fixture 自动注入 token）"""
        case = auth_data["user_info"]
        resp = authenticated_client.get(Endpoints.AUTH_INFO)

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"]
        for field in case["expected"]["fields"]:
            assert field in resp.data, f"缺少字段: {field}"

        logger.info(f"通过: {case['description']}")

    def test_get_user_info_without_token(self, api_client: APIClient, auth_data: dict):
        """测试：未登录获取用户信息返回 501"""
        case = auth_data["user_info_no_token"]
        resp = api_client.get(Endpoints.AUTH_INFO)

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"]
        assert resp.errmsg == case["expected"]["errmsg"]

        logger.info(f"通过: {case['description']}")

    def test_logout_with_token(self, authenticated_client: APIClient, auth_data: dict):
        """测试：登录后登出（fixture 自动注入 token）"""
        case = auth_data["logout"]
        resp = authenticated_client.post(Endpoints.AUTH_LOGOUT)

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"]
        assert resp.errmsg == case["expected"]["errmsg"]

        logger.info(f"通过: {case['description']}")

    def test_logout_without_token(self, api_client: APIClient, auth_data: dict):
        """测试：未登录登出返回 501"""
        case = auth_data["logout_no_token"]
        resp = api_client.post(Endpoints.AUTH_LOGOUT)

        APIAssertions.assert_status_code(resp, 200)
        assert resp.errno == case["expected"]["errno"]
        assert resp.errmsg == case["expected"]["errmsg"]

        logger.info(f"通过: {case['description']}")
