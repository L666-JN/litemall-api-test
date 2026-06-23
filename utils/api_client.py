# utils/api_client.py
"""
API 客户端 - 封装 requests 库，提供统一的 HTTP 请求接口
"""
import time
from typing import Any, Dict, Optional, Tuple
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from config.settings import get_settings
from config.endpoints import EndpointBuilder
from utils.logger import get_logger


logger = get_logger(__name__)


class APIClient:
    """API 客户端类 - 封装所有 HTTP 请求"""

    def __init__(self, base_url: Optional[str] = None):
        """
        初始化 API 客户端

        Args:
            base_url: API 基础 URL，默认使用配置文件中的值
        """
        self.base_url = base_url or get_settings().get_base_url()
        self.timeout = get_settings().TIMEOUT
        self.max_retries = get_settings().MAX_RETRIES
        self.retry_delay = get_settings().RETRY_DELAY
        self.session = requests.Session()
        self._token: Optional[str] = None

    def set_token(self, token: str) -> None:
        """设置认证 token，后续请求自动携带 X-Litemall-Token"""
        self._token = token
        self.session.headers.update({"X-Litemall-Token": token})
        logger.info("已设置认证 token")

    def clear_token(self) -> None:
        """清除认证 token"""
        self._token = None
        self.session.headers.pop("X-Litemall-Token", None)
        logger.info("已清除认证 token")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        with_auth: bool = False
    ) -> requests.Response:
        """
        发送 HTTP 请求（带重试机制）

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE, PATCH)
            endpoint: 端点路径
            params: URL 参数
            data: 表单数据
            json: JSON 数据
            headers: 请求头
            with_auth: 是否携带认证令牌

        Returns:
            响应对象

        Raises:
            RequestException: 请求失败
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = get_settings().get_headers(with_auth)

        if headers:
            request_headers.update(headers)

        retry_count = 0
        last_exception = None

        while retry_count <= self.max_retries:
            try:
                logger.info(f"发送 {method} 请求: {url}")
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json,
                    headers=request_headers,
                    timeout=self.timeout
                )

                logger.info(
                    f"响应: {response.status_code} - "
                    f"耗时: {response.elapsed.total_seconds():.2f}s"
                )

                return response

            except Timeout as e:
                last_exception = e
                logger.warning(f"请求超时 (尝试 {retry_count + 1}/{self.max_retries + 1})")
            except ConnectionError as e:
                last_exception = e
                logger.warning(f"连接错误 (尝试 {retry_count + 1}/{self.max_retries + 1})")
            except RequestException as e:
                last_exception = e
                logger.error(f"请求失败: {e}")
                raise

            retry_count += 1
            if retry_count <= self.max_retries:
                time.sleep(self.retry_delay)

        # 所有重试都失败
        logger.error(f"请求失败，已重试 {self.max_retries} 次")
        raise RequestException(f"请求失败: {last_exception}")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        with_auth: bool = False
    ) -> requests.Response:
        """发送 GET 请求"""
        return self._make_request(
            method='GET',
            endpoint=endpoint,
            params=params,
            headers=headers,
            with_auth=with_auth
        )

    def post(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        with_auth: bool = False
    ) -> requests.Response:
        """发送 POST 请求"""
        return self._make_request(
            method='POST',
            endpoint=endpoint,
            json=json,
            data=data,
            headers=headers,
            with_auth=with_auth
        )

    def put(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        with_auth: bool = False
    ) -> requests.Response:
        """发送 PUT 请求"""
        return self._make_request(
            method='PUT',
            endpoint=endpoint,
            json=json,
            data=data,
            headers=headers,
            with_auth=with_auth
        )

    def patch(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        with_auth: bool = False
    ) -> requests.Response:
        """发送 PATCH 请求"""
        return self._make_request(
            method='PATCH',
            endpoint=endpoint,
            json=json,
            data=data,
            headers=headers,
            with_auth=with_auth
        )

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        with_auth: bool = False
    ) -> requests.Response:
        """发送 DELETE 请求"""
        return self._make_request(
            method='DELETE',
            endpoint=endpoint,
            params=params,
            headers=headers,
            with_auth=with_auth
        )

    def close(self):
        """关闭会话"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()