# Litemall 接口自动化测试框架

基于 Python + pytest 的 Litemall 前台用户端 (wx-api) API 自动化测试框架。支持 Excel 用例设计 → YAML 数据驱动 → 参数化测试，含 Token 自动注入、HTML 报告。

## 目录结构

```
├── config/
│   ├── settings.py              # 环境配置（BASE_URL、timeout、重试等）
│   └── endpoints.py             # API 端点定义（wx-api 全量 34 个端点）
├── utils/
│   ├── api_client.py            # HTTP 客户端（Session + Token 自动注入）
│   ├── response.py              # ApiResponse 统一响应封装
│   ├── assertions.py            # 自定义断言
│   ├── logger.py                # 结构化日志
│   ├── test_data_manager.py     # 测试数据加载（YAML）
│   └── test_helpers.py          # 通用断言函数（assert_expected）
├── tests/
│   ├── conftest.py              # fixtures & hooks
│   ├── test_data/               # YAML 测试数据（由 Excel 自动生成）
│   │   ├── auth_*_data.yaml     # 认证模块（登录/登出/信息/注册/重置）
│   │   ├── goods_*_data.yaml    # 商品模块（列表/详情/分类/相关/统计）
│   │   ├── cart_*_data.yaml     # 购物车模块（列表/添加/更新/选中/删除/数量/结算）
│   │   ├── address_*_data.yaml  # 地址模块（列表/详情/保存/删除）
│   │   ├── order_*_data.yaml    # 订单模块（列表/详情/提交/取消/确认/删除/评价/商品）
│   │   └── home_data.yaml       # 首页模块（index / about）
│   ├── test_litemall_auth.py    # 认证模块（25 例）
│   ├── test_litemall_goods.py   # 商品模块（19 例）
│   ├── test_litemall_cart.py    # 购物车模块（29 例）
│   ├── test_litemall_address.py # 地址模块（16 例）
│   ├── test_litemall_order.py   # 订单模块（23 例）
│   └── test_litemall_home.py    # 首页模块（2 例）
├── test_design/
│   └── litemall_testcases.xlsx  # 用例设计 Excel（每个模块一个 sheet）
├── scripts/
│   ├── excel_to_yaml.py         # Excel → YAML 一键转换
│   └── create_master_excel.py   # 创建/重建空 Excel 模板
├── logs/                        # 运行日志
├── reports/                     # HTML 报告
├── pytest.ini                   # pytest 配置
├── requirements.txt
├── run_tests.py                 # 主入口脚本
└── README.md
```

## 测试概览

| 模块 | 测试文件 | 用例数 | 覆盖端点 |
|------|----------|--------|----------|
| 登录 | `test_litemall_auth.py` | 9 | `/wx/auth/login` |
| 登出 | `test_litemall_auth.py` | 3 | `/wx/auth/logout` |
| 用户信息 | `test_litemall_auth.py` | 3 | `/wx/auth/info` |
| 注册 | `test_litemall_auth.py` | 7 | `/wx/auth/register` |
| 密码重置 | `test_litemall_auth.py` | 3 | `/wx/auth/reset` |
| 商品列表 | `test_litemall_goods.py` | 8 | `/wx/goods/list` |
| 商品详情 | `test_litemall_goods.py` | 4 | `/wx/goods/detail` |
| 商品分类 | `test_litemall_goods.py` | 3 | `/wx/goods/category` |
| 相关商品 | `test_litemall_goods.py` | 3 | `/wx/goods/related` |
| 商品统计 | `test_litemall_goods.py` | 1 | `/wx/goods/count` |
| 购物车列表 | `test_litemall_cart.py` | 2 | `/wx/cart/index` |
| 购物车添加 | `test_litemall_cart.py` | 8 | `/wx/cart/add` |
| 快速添加 | `test_litemall_cart.py` | 4 | `/wx/cart/fastadd` |
| 购物车更新 | `test_litemall_cart.py` | 4 | `/wx/cart/update` |
| 购物车选中 | `test_litemall_cart.py` | 3 | `/wx/cart/checked` |
| 购物车删除 | `test_litemall_cart.py` | 3 | `/wx/cart/delete` |
| 购物车数量 | `test_litemall_cart.py` | 2 | `/wx/cart/goodscount` |
| 购物车结算 | `test_litemall_cart.py` | 3 | `/wx/cart/checkout` |
| 地址列表 | `test_litemall_address.py` | 2 | `/wx/address/list` |
| 地址详情 | `test_litemall_address.py` | 4 | `/wx/address/detail` |
| 地址保存 | `test_litemall_address.py` | 6 | `/wx/address/save` |
| 地址删除 | `test_litemall_address.py` | 4 | `/wx/address/delete` |
| 订单列表 | `test_litemall_order.py` | 2 | `/wx/order/list` |
| 订单详情 | `test_litemall_order.py` | 4 | `/wx/order/detail` |
| 订单提交 | `test_litemall_order.py` | 2 | `/wx/order/submit` |
| 订单取消 | `test_litemall_order.py` | 3 | `/wx/order/cancel` |
| 确认收货 | `test_litemall_order.py` | 2 | `/wx/order/confirm` |
| 订单删除 | `test_litemall_order.py` | 4 | `/wx/order/delete` |
| 订单评价 | `test_litemall_order.py` | 2 | `/wx/order/comment` |
| 订单商品 | `test_litemall_order.py` | 4 | `/wx/order/goods` |
| 首页数据 | `test_litemall_home.py` | 1 | `/wx/home/index` |
| 关于页面 | `test_litemall_home.py` | 1 | `/wx/home/about` |
| **合计** | | **114** | **32 个端点** |

## 环境要求

- Python 3.10+（使用本地 `py310` conda 环境）
- Litemall 后端运行在 `localhost:8088`

## 快速开始

```bash
# 1. 激活虚拟环境
conda activate py310

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行全部测试（推荐）
python run_tests.py

# 4. 或直接使用 pytest
pytest -v

# 5. 查看 HTML 报告
# 打开 reports/report.html
```

## 运行方式

```bash
# 主入口（自动检查后端连通性）
python run_tests.py                  # 全部测试
python run_tests.py -k auth          # 认证模块
python run_tests.py -k goods         # 商品模块
python run_tests.py -k cart          # 购物车模块
python run_tests.py -k address       # 地址模块
python run_tests.py -k order         # 订单模块
python run_tests.py -m smoke         # 冒烟测试
python run_tests.py -m smoke -n 4    # 4 线程并行

# 直接使用 pytest
pytest -v                                    # 全部测试
pytest tests/test_litemall_auth.py -v        # 认证模块
pytest tests/test_litemall_goods.py -v       # 商品模块
pytest tests/test_litemall_cart.py -v        # 购物车模块
pytest tests/test_litemall_address.py -v    # 地址模块
pytest tests/test_litemall_order.py -v      # 订单模块
pytest -k "login" -v                         # 按关键字过滤
pytest -k "goods_list" -v                    # 按用例名过滤
```

## 核心设计

### 1. 用例设计流程 — Excel → YAML → 参数化测试

```
test_design/litemall_testcases.xlsx   ← 唯一 Excel，每个模块一张 sheet
        │
        ▼  python scripts/excel_to_yaml.py
        │
tests/test_data/<模块>_data.yaml       ← YAML 测试数据
        │
        ▼  conftest.py fixture + parametrize
        │
tests/test_litemall_<模块>.py         ← pytest 参数化测试
```

用例在 Excel 中直接手写编辑，一键转换为 YAML。新增模块只需在 Excel 加一张 sheet，无需写生成脚本。

### 2. YAML 数据结构

```yaml
case_id:
  description: "默认商品列表"
  module: "商品列表"
  priority: "P0"
  method: "GET"
  need_auth: false
  endpoint: "/wx/goods/list"
  params: "page=1&size=10"          # GET 参数（可选）
  request:                           # POST 请求体（可选）
    username: "user123"
    password: "user123"
  expected:
    errno: 0                         # 精确匹配
    errno_not: 0                     # 不等于匹配
    errmsg: "成功"
    errmsg_contains: "不存在"
    has_data: true                   # data 有值/为空
    fields:                          # 嵌套字段检查
      - "list"
      - "userInfo.nickName"
```

### 3. 测试代码

```python
from utils.test_helpers import assert_expected

LOGIN_CASES = ["login_success", "login_wrong_password", ...]

class TestLitemallLogin:
    @pytest.mark.parametrize("case_id", LOGIN_CASES)
    def test_login(self, api_client, auth_login_data, case_id):
        case = auth_login_data[case_id]
        resp = api_client.post(case["endpoint"], json=case.get("request", {}))
        assert_expected(resp, case["expected"])  # YAML 中 expected 的所有断言
```

### 4. ApiResponse 统一响应封装

所有 HTTP 方法返回 `ApiResponse`，自动解析 `{errno, errmsg, data}`：

```python
resp = api_client.get("/wx/goods/list")

resp.errno      # 0
resp.errmsg     # "成功"
resp.data       # {"total": 238, "list": [...]}
resp.ok         # errno == 0
resp.is_unauthorized  # errno == 501
resp.is_bad_argument  # errno == 401
```

### 5. 两种客户端 Fixture

| fixture | scope | 说明 |
|---------|-------|------|
| `api_client` | session | 不携带 token，用于公开接口 |
| `authenticated_client` | function | 自动登录并注入 `X-Litemall-Token` |

```python
def test_public(self, api_client, goods_data):
    resp = api_client.get("/wx/goods/list")      # 无需认证

def test_authed(self, authenticated_client, auth_data):
    resp = authenticated_client.get("/wx/auth/info")  # 自动携带 token
```

### 6. 动态数据 Fixture

部分用例需要运行时获取的真实数据（如商品 id），通过 fixture 提供：

```python
# conftest.py
@pytest.fixture(scope='function')
def valid_goods_id(api_client):
    resp = api_client.get("/wx/goods/list", params="page=1&size=1")
    return resp.data["list"][0]["id"]

# 测试中使用
def test_detail_valid(self, api_client, valid_goods_id):
    resp = api_client.get(f"/wx/goods/detail?id={valid_goods_id}")
    assert resp.ok
```

## 测试的 API 端点

✓ = 已覆盖　　✗ = 待覆盖

| 模块 | 端点 | 状态 | 模块 | 端点 | 状态 |
|------|------|:--:|------|------|:--:|
| 认证 | `/wx/auth/login` | ✓ | 购物车 | `/wx/cart/index` | ✓ |
| | `/wx/auth/logout` | ✓ | | `/wx/cart/add` | ✓ |
| | `/wx/auth/info` | ✓ | | `/wx/cart/fastadd` | ✓ |
| | `/wx/auth/register` | ✓ | | `/wx/cart/update` | ✓ |
| | `/wx/auth/regCaptcha` | ✗ | | `/wx/cart/checked` | ✓ |
| | `/wx/auth/reset` | ✓ | | `/wx/cart/delete` | ✓ |
| | `/wx/auth/profile` | ✗ | | `/wx/cart/goodscount` | ✓ |
| 首页 | `/wx/home/index` | ✓ | | `/wx/cart/checkout` | ✓ |
| | `/wx/home/about` | ✓ | 地址 | `/wx/address/list` | ✓ |
| 商品 | `/wx/goods/list` | ✓ | | `/wx/address/detail` | ✓ |
| | `/wx/goods/detail` | ✓ | | `/wx/address/save` | ✓ |
| | `/wx/goods/category` | ✓ | | `/wx/address/delete` | ✓ |
| | `/wx/goods/related` | ✓ | 订单 | `/wx/order/list` | ✓ |
| | `/wx/goods/count` | ✓ | | `/wx/order/detail` | ✓ |
| | | | | `/wx/order/submit` | ✓ |
| | | | | `/wx/order/cancel` | ✓ |
| | | | | `/wx/order/confirm` | ✓ |
| | | | | `/wx/order/delete` | ✓ |
| | | | | `/wx/order/comment` | ✓ |
| | | | | `/wx/order/goods` | ✓ |

覆盖率：**32 / 34 = 94%**

## 新增测试模块

1. 在 `test_design/litemall_testcases.xlsx` 中添加新 sheet，手写用例
2. 运行 `python scripts/excel_to_yaml.py` 生成 YAML
3. 在 `tests/conftest.py` 中添加数据 fixture
4. 在 `tests/` 中创建 `test_litemall_<模块>.py`，导入 `assert_expected`

## 配置说明

`.env` 文件：

```
BASE_URL=http://localhost:8088
USERNAME=user123
PASSWORD=user123
ENV=dev
LOG_LEVEL=INFO
MAX_RETRIES=3
RETRY_DELAY=1
```

## CI/CD

GitHub Actions（`.github/workflows/tests.yml`）在 push/PR 到 `main`/`develop` 时触发，支持 ubuntu/windows/macos 三平台矩阵、并行执行和覆盖率报告。
