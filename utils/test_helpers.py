"""
公共测试辅助函数 — 供所有测试模块使用
"""
from typing import List


def assert_expected(resp, expected: dict):
    """
    根据 YAML 中的 expected 字段统一断言

    支持: errno / errno_not / errmsg / errmsg_contains / has_data / fields
    """
    # errno 精确匹配
    if "errno" in expected:
        assert resp.errno == expected["errno"], \
            f"预期 errno={expected['errno']}，实际 errno={resp.errno}, errmsg={resp.errmsg}"

    # errno 否定匹配
    if "errno_not" in expected:
        assert resp.errno != expected["errno_not"], \
            f"预期 errno != {expected['errno_not']}，实际 errno={resp.errno}, errmsg={resp.errmsg}"

    # errmsg 精确匹配
    if "errmsg" in expected:
        assert resp.errmsg == expected["errmsg"], \
            f"预期 errmsg='{expected['errmsg']}'，实际 errmsg='{resp.errmsg}'"

    # errmsg 包含
    if "errmsg_contains" in expected:
        assert expected["errmsg_contains"] in (resp.errmsg or ""), \
            f"预期 errmsg 包含 '{expected['errmsg_contains']}'，实际 errmsg='{resp.errmsg}'"

    # data 有/无值
    if expected.get("has_data") is True:
        assert resp.data is not None, f"预期 data 不为空，实际 data={resp.data}"
    elif expected.get("has_data") is False:
        assert not resp.data, f"预期 data 为空，实际 data={resp.data}"

    # data 嵌套字段检查
    if "fields" in expected:
        for field in expected["fields"]:
            _check_nested_field(resp.data, field)


def _check_nested_field(data, field_path: str):
    """
    检查嵌套字段是否存在且不为 None
    支持点号: "userInfo.nickName" → data["userInfo"]["nickName"]
    """
    parts = field_path.split(".")
    current = data
    for part in parts:
        assert isinstance(current, dict), \
            f"字段路径 '{field_path}' 中间节点 '{part}' 不是 dict: {type(current)}"
        assert part in current, \
            f"预期字段 '{field_path}' 不存在于 data 中（缺少 '{part}'）"
        current = current[part]
    assert current is not None, f"字段 '{field_path}' 存在但值为 None"
