# utils/response.py
"""
统一 API 响应封装 — 自动解析 litemall 响应结构，消除模板代码

litemall 统一响应格式:
    { "errno": 0, "errmsg": "成功", "data": {...} }

使用方式:
    resp = client.get("/wx/auth/info")
    assert resp.ok                        # errno == 0
    assert resp.errno == 501              # 直接访问业务状态码
    print(resp.data["userInfo"])          # 直接访问 data 字段
    print(resp.elapsed)                   # 响应耗时（秒）
"""
from dataclasses import dataclass, field
from typing import Any, Optional
import requests
import logging

logger = logging.getLogger("api_test")


@dataclass
class ApiResponse:
    """统一的 API 响应对象，自动解析 errno / errmsg / data"""

    status_code: int
    errno: int
    errmsg: str
    data: Any
    elapsed: float
    headers: dict
    raw: requests.Response = field(repr=False)

    # ─── 便捷属性 ───

    @property
    def ok(self) -> bool:
        """业务成功（errno == 0）"""
        return self.errno == 0

    @property
    def is_unauthorized(self) -> bool:
        """未登录（errno == 501）"""
        return self.errno == 501

    @property
    def is_bad_argument(self) -> bool:
        """参数错误（errno == 401）"""
        return self.errno == 401

    # ─── 构造方法 ───

    @classmethod
    def from_response(cls, resp: requests.Response) -> "ApiResponse":
        """
        从 requests.Response 构建 ApiResponse

        自动提取 litemall 标准字段，非 JSON 响应容错处理。
        """
        try:
            body = resp.json()
        except (ValueError, requests.JSONDecodeError):
            body = {}

        instance = cls(
            status_code=resp.status_code,
            errno=body.get("errno", -1),
            errmsg=body.get("errmsg", ""),
            data=body.get("data"),
            elapsed=resp.elapsed.total_seconds(),
            headers=dict(resp.headers),
            raw=resp,
        )

        # 自动记录响应日志
        logger.info(
            f"响应 [{resp.request.method}] {resp.url} → "
            f"HTTP {resp.status_code} | errno={instance.errno} | "
            f"耗时={instance.elapsed:.2f}s"
        )

        return instance

    def __repr__(self) -> str:
        data_preview = str(self.data)
        if len(data_preview) > 120:
            data_preview = data_preview[:120] + "..."
        return (
            f"ApiResponse(errno={self.errno}, errmsg='{self.errmsg}', "
            f"data={data_preview}, elapsed={self.elapsed:.2f}s)"
        )
