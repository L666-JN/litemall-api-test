# utils/assertions.py
"""
自定义断言模块 - 提供常用的 API 测试断言方法

支持 ApiResponse 和原生 requests.Response 两种输入。
"""
import time
from typing import Any, Dict, List, Optional, Union
import requests

from utils.logger import get_logger
from utils.response import ApiResponse

logger = get_logger(__name__)

# 可接受的响应类型
ResponseLike = Union[ApiResponse, requests.Response]


def _get_status_code(resp: ResponseLike) -> int:
    """从 ApiResponse 或 requests.Response 提取状态码"""
    if isinstance(resp, ApiResponse):
        return resp.status_code
    return resp.status_code


def _get_elapsed_seconds(resp: ResponseLike) -> float:
    """从 ApiResponse 或 requests.Response 提取耗时（秒）"""
    if isinstance(resp, ApiResponse):
        return resp.elapsed
    return resp.elapsed.total_seconds()


def _get_headers(resp: ResponseLike) -> dict:
    """从 ApiResponse 或 requests.Response 提取响应头"""
    if isinstance(resp, ApiResponse):
        return resp.headers
    return dict(resp.headers)


def _get_json(resp: ResponseLike) -> dict:
    """从 ApiResponse 或 requests.Response 提取 JSON 数据"""
    if isinstance(resp, ApiResponse):
        # 重建 litemall 标准结构
        return {"errno": resp.errno, "errmsg": resp.errmsg, "data": resp.data}
    try:
        return resp.json()
    except ValueError:
        return {}


class APIAssertions:
    """API 断言类"""

    @staticmethod
    def assert_status_code(
        response: ResponseLike,
        expected_status: int,
        message: Optional[str] = None
    ) -> None:
        """断言响应状态码"""
        actual = _get_status_code(response)
        message = message or f"期望状态码 {expected_status}，实际得到 {actual}"
        assert actual == expected_status, message
        logger.info(f"状态码断言通过: {expected_status}")

    @staticmethod
    def assert_response_time(
        response: ResponseLike,
        max_time: float,
        message: Optional[str] = None
    ) -> None:
        """断言响应时间"""
        actual_time = _get_elapsed_seconds(response)
        message = message or f"响应时间 {actual_time:.2f}s 超过最大值 {max_time}s"
        assert actual_time <= max_time, message
        logger.info(f"响应时间断言通过: {actual_time:.2f}s <= {max_time}s")

    @staticmethod
    def assert_json_structure(
        response: ResponseLike,
        expected_keys: List[str],
        message: Optional[str] = None
    ) -> None:
        """断言 JSON 响应包含指定的字段"""
        try:
            json_data = _get_json(response)
            missing_keys = [key for key in expected_keys if key not in json_data]
            message = message or f"JSON 缺少字段: {missing_keys}"
            assert not missing_keys, message
            logger.info(f"JSON 结构断言通过: 包含所有期望字段 {expected_keys}")
        except ValueError as e:
            raise AssertionError(f"响应不是有效的 JSON: {e}")

    @staticmethod
    def assert_field_value(
        response: ResponseLike,
        field: str,
        expected_value: Any,
        message: Optional[str] = None
    ) -> None:
        """断言 JSON 响应中指定字段的值"""
        try:
            json_data = _get_json(response)
            actual_value = json_data.get(field)
            message = message or f"字段 '{field}' 期望值 {expected_value}，实际值 {actual_value}"
            assert actual_value == expected_value, message
            logger.info(f"字段值断言通过: {field} = {expected_value}")
        except ValueError as e:
            raise AssertionError(f"响应不是有效的 JSON: {e}")

    @staticmethod
    def assert_list_not_empty(
        response: ResponseLike,
        message: Optional[str] = None
    ) -> None:
        """断言 JSON 响应是一个非空列表"""
        try:
            json_data = _get_json(response)
            message = message or "响应不是非空列表"
            assert isinstance(json_data, list) and len(json_data) > 0, message
            logger.info(f"列表非空断言通过: 共 {len(json_data)} 项")
        except ValueError as e:
            raise AssertionError(f"响应不是有效的 JSON: {e}")

    @staticmethod
    def assert_list_length(
        response: ResponseLike,
        expected_length: int,
        message: Optional[str] = None
    ) -> None:
        """断言 JSON 响应列表的长度"""
        try:
            json_data = _get_json(response)
            actual_length = len(json_data)
            message = message or f"期望列表长度 {expected_length}，实际 {actual_length}"
            assert actual_length == expected_length, message
            logger.info(f"列表长度断言通过: {expected_length}")
        except ValueError as e:
            raise AssertionError(f"响应不是有效的 JSON: {e}")

    @staticmethod
    def assert_header_present(
        response: ResponseLike,
        header_name: str,
        message: Optional[str] = None
    ) -> None:
        """断言响应头包含指定的字段"""
        message = message or f"响应头缺少字段: {header_name}"
        headers = _get_headers(response)
        assert header_name in headers, message
        logger.info(f"响应头断言通过: 包含 {header_name}")

    @staticmethod
    def assert_content_type(
        response: ResponseLike,
        expected_type: str = "application/json",
        message: Optional[str] = None
    ) -> None:
        """断言 Content-Type 响应头"""
        headers = _get_headers(response)
        actual_type = headers.get('Content-Type', '')
        message = message or f"期望 Content-Type: {expected_type}，实际: {actual_type}"
        assert expected_type in actual_type, message
        logger.info(f"Content-Type 断言通过: {actual_type}")


# ─── 便捷函数 ───

def assert_status(response: ResponseLike, expected_status: int) -> None:
    """断言状态码（便捷函数）"""
    APIAssertions.assert_status_code(response, expected_status)


def assert_time(response: ResponseLike, max_time: float) -> None:
    """断言响应时间（便捷函数）"""
    APIAssertions.assert_response_time(response, max_time)


def assert_json_keys(response: ResponseLike, expected_keys: List[str]) -> None:
    """断言 JSON 字段（便捷函数）"""
    APIAssertions.assert_json_structure(response, expected_keys)