# utils/assertions.py
"""
自定义断言模块 - 提供常用的 API 测试断言方法
"""
import time
from typing import Any, Dict, List, Optional
import requests

from utils.logger import get_logger


logger = get_logger(__name__)


class APIAssertions:
    """API 断言类"""

    @staticmethod
    def assert_status_code(
        response: requests.Response,
        expected_status: int,
        message: Optional[str] = None
    ) -> None:
        """
        断言响应状态码

        Args:
            response: 响应对象
            expected_status: 期望的状态码
            message: 自定义错误消息
        """
        message = message or f"期望状态码 {expected_status}，实际得到 {response.status_code}"
        assert response.status_code == expected_status, message
        logger.info(f"状态码断言通过: {expected_status}")

    @staticmethod
    def assert_response_time(
        response: requests.Response,
        max_time: float,
        message: Optional[str] = None
    ) -> None:
        """
        断言响应时间

        Args:
            response: 响应对象
            max_time: 最大响应时间（秒）
            message: 自定义错误消息
        """
        actual_time = response.elapsed.total_seconds()
        message = message or f"响应时间 {actual_time:.2f}s 超过最大值 {max_time}s"
        assert actual_time <= max_time, message
        logger.info(f"响应时间断言通过: {actual_time:.2f}s <= {max_time}s")

    @staticmethod
    def assert_json_structure(
        response: requests.Response,
        expected_keys: List[str],
        message: Optional[str] = None
    ) -> None:
        """
        断言 JSON 响应包含指定的字段

        Args:
            response: 响应对象
            expected_keys: 期望的字段列表
            message: 自定义错误消息
        """
        try:
            json_data = response.json()
            missing_keys = [key for key in expected_keys if key not in json_data]
            message = message or f"JSON 缺少字段: {missing_keys}"
            assert not missing_keys, message
            logger.info(f"JSON 结构断言通过: 包含所有期望字段 {expected_keys}")
        except ValueError as e:
            raise AssertionError(f"响应不是有效的 JSON: {e}")

    @staticmethod
    def assert_field_value(
        response: requests.Response,
        field: str,
        expected_value: Any,
        message: Optional[str] = None
    ) -> None:
        """
        断言 JSON 响应中指定字段的值

        Args:
            response: 响应对象
            field: 字段名
            expected_value: 期望的值
            message: 自定义错误消息
        """
        try:
            json_data = response.json()
            actual_value = json_data.get(field)
            message = message or f"字段 '{field}' 期望值 {expected_value}，实际值 {actual_value}"
            assert actual_value == expected_value, message
            logger.info(f"字段值断言通过: {field} = {expected_value}")
        except ValueError as e:
            raise AssertionError(f"响应不是有效的 JSON: {e}")

    @staticmethod
    def assert_list_not_empty(
        response: requests.Response,
        message: Optional[str] = None
    ) -> None:
        """
        断言 JSON 响应是一个非空列表

        Args:
            response: 响应对象
            message: 自定义错误消息
        """
        try:
            json_data = response.json()
            message = message or "响应不是非空列表"
            assert isinstance(json_data, list) and len(json_data) > 0, message
            logger.info(f"列表非空断言通过: 共 {len(json_data)} 项")
        except ValueError as e:
            raise AssertionError(f"响应不是有效的 JSON: {e}")

    @staticmethod
    def assert_list_length(
        response: requests.Response,
        expected_length: int,
        message: Optional[str] = None
    ) -> None:
        """
        断言 JSON 响应列表的长度

        Args:
            response: 响应对象
            expected_length: 期望的长度
            message: 自定义错误消息
        """
        try:
            json_data = response.json()
            actual_length = len(json_data)
            message = message or f"期望列表长度 {expected_length}，实际 {actual_length}"
            assert actual_length == expected_length, message
            logger.info(f"列表长度断言通过: {expected_length}")
        except ValueError as e:
            raise AssertionError(f"响应不是有效的 JSON: {e}")

    @staticmethod
    def assert_header_present(
        response: requests.Response,
        header_name: str,
        message: Optional[str] = None
    ) -> None:
        """
        断言响应头包含指定的字段

        Args:
            response: 响应对象
            header_name: 响应头名称
            message: 自定义错误消息
        """
        message = message or f"响应头缺少字段: {header_name}"
        assert header_name in response.headers, message
        logger.info(f"响应头断言通过: 包含 {header_name}")

    @staticmethod
    def assert_content_type(
        response: requests.Response,
        expected_type: str = "application/json",
        message: Optional[str] = None
    ) -> None:
        """
        断言 Content-Type 响应头

        Args:
            response: 响应对象
            expected_type: 期望的内容类型
            message: 自定义错误消息
        """
        actual_type = response.headers.get('Content-Type', '')
        message = message or f"期望 Content-Type: {expected_type}，实际: {actual_type}"
        assert expected_type in actual_type, message
        logger.info(f"Content-Type 断言通过: {actual_type}")


# 便捷函数
def assert_status(response: requests.Response, expected_status: int) -> None:
    """断言状态码（便捷函数）"""
    APIAssertions.assert_status_code(response, expected_status)


def assert_time(response: requests.Response, max_time: float) -> None:
    """断言响应时间（便捷函数）"""
    APIAssertions.assert_response_time(response, max_time)


def assert_json_keys(response: requests.Response, expected_keys: List[str]) -> None:
    """断言 JSON 字段（便捷函数）"""
    APIAssertions.assert_json_structure(response, expected_keys)