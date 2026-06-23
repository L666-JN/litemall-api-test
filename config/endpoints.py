# config/endpoints.py
"""
Litemall API 端点管理 - 集中管理所有 API 端点路径
"""
from functools import lru_cache
from config.settings import get_settings


class Endpoints:
    """Litemall API 端点类 - 用户端前台接口 (wx-api)"""

    # 认证模块 ─ /wx/auth
    AUTH_LOGIN = "/wx/auth/login"
    AUTH_LOGOUT = "/wx/auth/logout"
    AUTH_INFO = "/wx/auth/info"
    AUTH_REGISTER = "/wx/auth/register"
    AUTH_REG_CAPTCHA = "/wx/auth/regCaptcha"
    AUTH_RESET = "/wx/auth/reset"
    AUTH_PROFILE = "/wx/auth/profile"

    # 首页模块 ─ /wx/home
    HOME_INDEX = "/wx/home/index"
    HOME_ABOUT = "/wx/home/about"

    # 商品模块 ─ /wx/goods
    GOODS_LIST = "/wx/goods/list"
    GOODS_DETAIL = "/wx/goods/detail"
    GOODS_CATEGORY = "/wx/goods/category"
    GOODS_RELATED = "/wx/goods/related"
    GOODS_COUNT = "/wx/goods/count"

    # 购物车模块 ─ /wx/cart
    CART_INDEX = "/wx/cart/index"
    CART_ADD = "/wx/cart/add"
    CART_FASTADD = "/wx/cart/fastadd"
    CART_UPDATE = "/wx/cart/update"
    CART_CHECKED = "/wx/cart/checked"
    CART_DELETE = "/wx/cart/delete"
    CART_GOODSCOUNT = "/wx/cart/goodscount"
    CART_CHECKOUT = "/wx/cart/checkout"

    # 地址模块 ─ /wx/address
    ADDRESS_LIST = "/wx/address/list"
    ADDRESS_DETAIL = "/wx/address/detail"
    ADDRESS_SAVE = "/wx/address/save"
    ADDRESS_DELETE = "/wx/address/delete"

    # 订单模块 ─ /wx/order
    ORDER_LIST = "/wx/order/list"
    ORDER_DETAIL = "/wx/order/detail"
    ORDER_SUBMIT = "/wx/order/submit"
    ORDER_CANCEL = "/wx/order/cancel"
    ORDER_CONFIRM = "/wx/order/confirm"
    ORDER_DELETE = "/wx/order/delete"
    ORDER_COMMENT = "/wx/order/comment"
    ORDER_GOODS = "/wx/order/goods"


class EndpointBuilder:
    """端点构建器 - 用于构建完整的 API URL"""

    @staticmethod
    @lru_cache(maxsize=128)
    def build_url(endpoint: str, **params) -> str:
        """
        构建完整的 API URL

        Args:
            endpoint: 端点路径
            **params: 路径参数

        Returns:
            完整的 API URL
        """
        base_url = get_settings().get_base_url()
        url = endpoint.format(**params)
        return f"{base_url}{url}"

    @classmethod
    def get_auth_login_url(cls) -> str:
        """获取登录 URL"""
        return cls.build_url(Endpoints.AUTH_LOGIN)

    @classmethod
    def get_auth_logout_url(cls) -> str:
        """获取登出 URL"""
        return cls.build_url(Endpoints.AUTH_LOGOUT)

    @classmethod
    def get_auth_info_url(cls) -> str:
        """获取用户信息 URL"""
        return cls.build_url(Endpoints.AUTH_INFO)

    @classmethod
    def get_auth_register_url(cls) -> str:
        """获取注册 URL"""
        return cls.build_url(Endpoints.AUTH_REGISTER)
