# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指引。

## 项目概述

基于 Python + pytest 的 Litemall 电商后端（wx-api / 用户端前台接口）API 自动化测试框架。测试针对本地 localhost:8088 运行的 Litemall 实例。

## 常用命令

### 主入口（推荐）

```bash
python run_tests.py                  # 全部测试（自动检查后端连通性 → 运行 → 输出报告）
python run_tests.py -k auth          # 认证模块
python run_tests.py -k shopping      # 下单业务流
python run_tests.py -m smoke         # 冒烟测试
python run_tests.py -m smoke -n 4    # 4 线程并行冒烟
python run_tests.py --cov            # 带覆盖率
python run_tests.py --no-report      # 不生成 HTML 报告
python run_tests.py -f test_litemall_auth.py  # 指定测试文件
```

`run_tests.py` 会在运行前自动检查 Litemall 后端是否可达，不可达时直接报错退出。更多选项见 `python run_tests.py --help`。

### 直接使用 pytest

```bash
# 激活 conda 环境
conda activate py310

# 安装依赖
pip install -r requirements.txt

# 运行全部测试（详细输出，HTML 报告输出到 reports/report.html）
pytest -v

# 运行单个测试文件
pytest tests/test_litemall_auth.py -v
pytest tests/test_shopping_flow.py -v

# 按名称运行单个测试
pytest -k "test_login[login_success]" -v

# 按标记运行
pytest -m smoke -v
pytest -m api -v

# 并行运行（需要 pytest-xdist）
pytest -n auto -v

# 带覆盖率运行
pytest --cov=tests --cov-report=html
```

## 架构设计

### 响应层 — 所有 HTTP 调用都返回 `ApiResponse`

`APIClient` 从不返回原始的 `requests.Response`。所有方法（`get`、`post`、`put`、`patch`、`delete`）都返回 `ApiResponse`（定义在 `utils/response.py`），该对象自动解析 Litemall 的标准响应结构：

```
{ "errno": 0, "errmsg": "成功", "data": {...} }
```

直接使用 `resp.errno`、`resp.errmsg`、`resp.data` — 无需手动调用 `.json()`。便捷属性：`resp.ok`（errno==0）、`resp.is_unauthorized`（errno==501）、`resp.is_bad_argument`（errno==401）。

### 两种客户端 fixture — `api_client` 与 `authenticated_client`

- **`api_client`**（`tests/conftest.py:25`）：会话级别作用域，不携带 token。所有请求以未认证状态发出。
- **`authenticated_client`**（`tests/conftest.py:130`）：函数级别作用域。创建时自动使用 `.env` 中的凭据调用 `/wx/auth/login`，提取 JWT token，并将 `X-Litemall-Token` 写入 `session.headers`。此后通过该客户端发出的所有请求都自动携带 token。任何需要登录的接口都应使用此 fixture。

Token 注入通过 `APIClient.set_token(token)` 实现，该方法调用 `self.session.headers.update({"X-Litemall-Token": token})` — token 持久化在 requests 的 Session 对象上，而非每次请求单独传递的 dict。

### 数据驱动测试 — YAML → fixture → parametrize

测试数据存放在 `tests/test_data/*.yaml` 文件中，由 `TestDataManager`（`utils/test_data_manager.py`）加载。每个 YAML 文件是一个以用例名称为 key 的扁平字典：

```yaml
case_name:
  description: "..."
  request: { ... }       # POST 请求体（JSON）
  expected: { errno: 0, ... }
```

测试用例通过用例 ID 字符串进行参数化：

```python
LOGIN_CASES = ["login_success", "login_wrong_password", ...]

class TestLitemallLogin:
    @pytest.mark.parametrize("case_id", LOGIN_CASES)
    def test_login(self, api_client, auth_data, case_id):
        case = auth_data[case_id]   # 字典查找
        resp = api_client.post(Endpoints.AUTH_LOGIN, json=case["request"])
        assert resp.errno == case["expected"]["errno"]
```

新增测试用例只需在 YAML 文件中添加数据节点、并将其 key 加入 parametrize 列表即可，无需修改测试代码。

### 业务流测试 — 通过类变量在步骤间传递状态

`TestShoppingFlow`（`tests/test_shopping_flow.py`）执行一个 8 步的下单流程。步骤通过方法名排序（`test_01_`、`test_02_`、…、`test_08_`）。中间结果（`goods_id`、`product_id`、`address_id`、`order_id`）存储在类级别属性中，供后续步骤读取：

```
home/index → goods/detail → address/save → cart/add → cart/checkout → order/submit → order/list → order/detail
```

**注意**：部分步骤使用 `api_client`（无需认证），部分使用 `authenticated_client`。fixture 的选择在每个测试方法的参数中决定。

### 自定义断言

`APIAssertions`（`utils/assertions.py`）通过 `ResponseLike` 联合类型同时接受 `ApiResponse` 和原始 `requests.Response`。常用断言方法：`assert_status_code`、`assert_response_time`、`assert_json_structure`、`assert_list_not_empty`、`assert_content_type`。

### 端点常量

所有 API 路径以类属性的形式定义在 `Endpoints`（`config/endpoints.py`）中，按模块组织（AUTH_*、HOME_*、GOODS_*、CART_*、ADDRESS_*、ORDER_*）。`EndpointBuilder.build_url()` 使用 LRU 缓存拼接完整 URL，但测试代码通常只将端点路径传给 `APIClient`，由后者内部自动拼接 `base_url`。

### 日志

`utils/logger.py` 提供 `get_logger(name)` → 返回一个同时拥有控制台（stdout）和文件（`logs/api_test.log`）处理器的 logger。`conftest.py` 中的 `test_setup_teardown` autouse fixture 会记录每个测试的开始和结束横幅。

### 配置

项目根目录的 `.env` 文件设置 `BASE_URL`、凭据、`LOG_LEVEL` 和重试参数。`Settings`（`config/settings.py`）通过 `python-dotenv` 读取这些值并以类属性形式暴露。通过 `from config.settings import get_settings` 访问。

## 新增测试模块

1. 在 `tests/test_data/` 中创建 `<模块名>_data.yaml` 测试数据文件
2. 在 `tests/conftest.py` 中添加调用 `test_data.load_yaml('<模块名>_data')` 的 fixture
3. 在 `tests/` 中创建 `test_litemall_<模块名>.py` 测试文件，使用参数化测试类
4. 如需新增端点，在 `config/endpoints.py` 中添加对应常量

## CI

GitHub Actions（`.github/workflows/tests.yml`）在 push/PR 到 `main` 和 `develop` 分支时触发：
- 在 ubuntu/windows/macos 三平台上使用 Python 3.10 矩阵运行
- 单独的 `test-parallel` job 使用 `pytest -n auto` 并行执行
- 覆盖率 job 并上传至 Codecov
- 制品：HTML 报告和日志，保留 7 天
