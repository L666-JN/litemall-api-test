# Litemall 接口自动化测试框架

基于 Python + pytest 的 Litemall 前台用户端 (wx-api) API 自动化测试框架，支持测试数据分离、Token 自动注入、业务流测试和 HTML 报告。

## 目录结构

```
├── config/
│   ├── settings.py           # 环境配置（BASE_URL、timeout、重试等）
│   └── endpoints.py          # API 端点定义（全量 wx-api）
├── utils/
│   ├── api_client.py         # HTTP 客户端（Session + Token 自动注入）
│   ├── response.py           # ApiResponse 统一响应封装
│   ├── assertions.py         # 自定义断言
│   ├── logger.py             # 结构化日志
│   └── test_data_manager.py  # 测试数据加载（YAML）
├── tests/
│   ├── conftest.py           # fixtures & hooks
│   ├── test_data/
│   │   ├── auth_data.yaml    # 登录模块测试数据
│   │   └── shopping_flow.yaml # 下单业务流测试数据
│   ├── test_litemall_auth.py # 登录模块（9 条用例）
│   └── test_shopping_flow.py # 下单全流程（8 步联动）
├── logs/                     # 运行日志
├── reports/                  # HTML 报告输出
├── pytest.ini                # pytest 配置
├── requirements.txt
├── .env                      # 本地环境变量
└── README.md
```

## 测试概览

| 模块 | 测试文件 | 用例数 | 说明 |
|------|----------|--------|------|
| 用户认证 | `test_litemall_auth.py` | 9 | 登录 ×5、用户信息 / 登出（含免登态校验） |
| 下单业务流 | `test_shopping_flow.py` | 8 | 首页 → 详情 → 建地址 → 加购 → 结算 → 下单 → 列表 → 详情 |

## 环境要求

- Python 3.10+（使用本地 `py310` conda 环境）
- Litemall 后端运行在 `localhost:8088`

## 快速开始

```bash
# 1. 激活虚拟环境
conda activate py310

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行全部测试
pytest -v

# 4. 查看 HTML 报告
# 打开 reports/report.html
```

## 运行方式

```bash
pytest -v                              # 全部测试
pytest tests/test_litemall_auth.py -v  # 仅登录模块
pytest tests/test_shopping_flow.py -v  # 仅业务流
pytest -m smoke                        # 冒烟测试
pytest -k "login" -v                   # 按关键字过滤
```

## 核心设计

### 1. 测试数据与代码分离

测试数据集中存放在 `tests/test_data/` 的 YAML 文件中，测试代码通过 fixture 读取：

```yaml
# tests/test_data/auth_data.yaml
login_success:
  description: "正确的用户名密码登录成功"
  request:
    username: "user123"
    password: "user123"
  expected:
    errno: 0
    errmsg: "成功"
    has_token: true
    nickName: "user123"
```

```python
# 测试代码中使用 @pytest.mark.parametrize 注入
LOGIN_CASES = ["login_success", "login_wrong_password", "login_nonexistent_user",
               "login_empty_username", "login_empty_password"]

class TestLitemallLogin:
    @pytest.mark.parametrize("case_id", LOGIN_CASES)
    def test_login(self, api_client, auth_data, case_id):
        case = auth_data[case_id]
        resp = api_client.post(Endpoints.AUTH_LOGIN, json=case["request"])
        assert resp.errno == case["expected"]["errno"]  # ApiResponse 自动解析
```

新增测试用例只需在 YAML 中添加数据节点，无需修改测试代码。

### 2. Token 自动注入（Session + Fixture）

框架提供 `authenticated_client` fixture，自动登录并将 JWT token 注入 `X-Litemall-Token` 请求头：

```python
# 需要 token 的测试 → 用 authenticated_client，无需手动传 headers
def test_get_user_info(self, authenticated_client, auth_data):
    resp = authenticated_client.get(Endpoints.AUTH_INFO)
    assert resp.ok  # ApiResponse 自动解析 errno

# 不需要 token 的测试 → 用 api_client
def test_without_token(self, api_client):
    resp = api_client.get(Endpoints.AUTH_INFO)
    assert resp.is_unauthorized  # errno == 501
```

实现原理：`APIClient` 内部维护 `requests.Session`，`set_token()` 将 token 写入 `session.headers`，后续所有请求自动携带。

### 3. 业务流测试（步骤间共享状态）

下单流程 8 个步骤通过类变量串联，前一步的结果（goodsId、productId、addressId、orderId）传递给后续步骤：

```
首页(index) → 商品详情(detail) → 创建地址(save) → 加入购物车(add)
    → 结算(checkout) → 提交订单(submit) → 订单列表(list) → 订单详情(detail)
```

```python
class TestShoppingFlow:
    goods_id: int = None
    product_id: int = None
    address_id: int = None
    order_id: int = None

    def test_01_home_index(self, api_client, shopping_data):
        # 获取首页新品，存 goods_id 到类变量
        TestShoppingFlow.goods_id = response.json()["data"]["newGoodsList"][0]["id"]

    def test_02_goods_detail(self, api_client, shopping_data):
        # 用上一步的 goods_id 查详情
        response = api_client.get(Endpoints.GOODS_DETAIL, params={"id": self.goods_id})
```

### 4. ApiResponse 统一响应封装

所有 HTTP 方法返回 `ApiResponse` 对象，自动解析 litemall 的 `{errno, errmsg, data}` 结构，无需手动 `.json()`：

```python
resp = api_client.get(Endpoints.AUTH_INFO)

# 直接访问业务字段，无需 .json()
print(resp.errno)      # 0
print(resp.errmsg)     # "成功"
print(resp.data)       # {"nickName": "user123", ...}

# 便捷属性
assert resp.ok                  # errno == 0
assert resp.is_unauthorized     # errno == 501
assert resp.is_bad_argument     # errno == 401
```

### 5. 自定义断言

```python
APIAssertions.assert_status_code(response, 200)       # 状态码
APIAssertions.assert_response_time(response, 2.0)     # 响应时间
APIAssertions.assert_json_structure(response, [...])  # JSON 结构
APIAssertions.assert_list_not_empty(response)         # 非空列表
```

## 测试的 API 端点

### 认证模块 `/wx/auth`

| 端点 | 方法 | 需登录 |
|------|------|--------|
| `/wx/auth/login` | POST | 否 |
| `/wx/auth/logout` | POST | 是/否 |
| `/wx/auth/info` | GET | 是/否 |
| `/wx/auth/register` | POST | 否 |
| `/wx/auth/profile` | POST | 是 |

### 首页 `/wx/home`

| 端点 | 方法 | 需登录 |
|------|------|--------|
| `/wx/home/index` | GET | 否 |
| `/wx/home/about` | GET | 否 |

### 商品 `/wx/goods`

| 端点 | 方法 | 需登录 |
|------|------|--------|
| `/wx/goods/detail` | GET | 否 |
| `/wx/goods/list` | GET | 否 |
| `/wx/goods/category` | GET | 否 |

### 购物车 `/wx/cart`

| 端点 | 方法 | 需登录 |
|------|------|--------|
| `/wx/cart/add` | POST | 是 |
| `/wx/cart/index` | GET | 是 |
| `/wx/cart/checkout` | GET | 是 |
| `/wx/cart/update` | POST | 是 |
| `/wx/cart/delete` | POST | 是 |

### 地址 `/wx/address`

| 端点 | 方法 | 需登录 |
|------|------|--------|
| `/wx/address/list` | GET | 是 |
| `/wx/address/save` | POST | 是 |
| `/wx/address/delete` | POST | 是 |

### 订单 `/wx/order`

| 端点 | 方法 | 需登录 |
|------|------|--------|
| `/wx/order/submit` | POST | 是 |
| `/wx/order/list` | GET | 是 |
| `/wx/order/detail` | GET | 是 |
| `/wx/order/cancel` | POST | 是 |
| `/wx/order/confirm` | POST | 是 |
| `/wx/order/delete` | POST | 是 |

## 扩展新模块

1. 在 `tests/test_data/` 中创建 YAML 数据文件
2. 在 `tests/conftest.py` 中添加对应的 fixture
3. 在 `tests/` 中创建测试文件

```python
# tests/conftest.py — 添加 fixture
@pytest.fixture(scope='function')
def goods_data(test_data) -> dict:
    return test_data.load_yaml('goods_data')

# tests/test_litemall_goods.py — 编写测试
class TestLitemallGoods:
    def test_goods_list(self, api_client, goods_data):
        case = goods_data["goods_list"]
        response = api_client.get(Endpoints.GOODS_LIST)
        APIAssertions.assert_status_code(response, 200)
        assert response.json()["errno"] == case["expected"]["errno"]
```

## 配置说明

`.env` 文件：

```
BASE_URL=http://localhost:8088   # Litemall 后端地址
USERNAME=user123                 # 测试账号（数据库种子用户）
PASSWORD=user123                 # 测试密码
ENV=dev                          # 环境标识
LOG_LEVEL=INFO                   # 日志级别
MAX_RETRIES=3                    # 失败重试次数
RETRY_DELAY=1                    # 重试间隔（秒）
```

## CI/CD

GitHub Actions 配置位于 `.github/workflows/tests.yml`，支持自动运行测试、生成报告和多平台执行。
