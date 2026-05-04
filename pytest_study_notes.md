# 🧪 Python 接口自动化测试 —— 学习笔记

> 从"会写脚本"到"会设计框架"的进阶之路

---

## 📐 阶段 0：思想奠基

### 测试金字塔

```
        /  UI 测试  \        ← 慢、贵、脆弱（最少）
       / 接口(API)测试 \      ← 性价比最高（重点投入）
      /   单元测试      \     ← 快、便宜（最多）
```

| 层级 | 速度 | 成本 | 稳定性 | 覆盖重点 |
|------|------|------|--------|----------|
| 单元测试 | 毫秒级 | 低 | 高 | 函数/方法逻辑 |
| 接口测试 | 秒级 | 中 | 中高 | 业务流程、数据流转 |
| UI 测试 | 十秒级 | 高 | 低 | 用户交互、页面展示 |

### 接口自动化的企业价值

- **回归效率**：100 条用例手工 2 天 → 自动化 10 分钟
- **持续集成**：每次代码提交自动跑测试，快速发现问题
- **ROI 公式**：`ROI = (手工成本 × 执行次数 - 自动化开发成本) / 自动化开发成本`
- 一般跑 **5 次以上**就开始回本

### 测试开发 vs 普通测试

| 维度 | 普通自动化 | 测试开发 |
|------|-----------|---------|
| 核心能力 | 会用工具写脚本 | 能设计框架、开发工具 |
| 代码量 | 写用例 | 写框架 + 用例 + 工具 |
| 面试考点 | 工具使用 | 架构设计 + 编码能力 |

---

## 🌿 阶段 1：V1 框架 —— 脚本时代

### HTTP 协议核心（面试必考）

#### 请求方法

| 方法 | 用途 | 幂等性 | 请求体 |
|------|------|--------|--------|
| GET | 获取资源 | ✅ 幂等 | 无 |
| POST | 创建资源 | ❌ 非幂等 | 有 |
| PUT | 全量更新 | ✅ 幂等 | 有 |
| DELETE | 删除资源 | ✅ 幂等 | 通常无 |
| PATCH | 局部更新 | ❌ 非幂等 | 有 |

> **幂等性**：同一个请求执行多次，结果和执行一次一样。

#### 状态码分类

| 范围 | 含义 | 常见 |
|------|------|------|
| 1xx | 信息性 | 100 Continue |
| 2xx | 成功 | **200 OK**, 201 Created, 204 No Content |
| 3xx | 重定向 | 301 永久, **302 临时**, 304 未修改 |
| 4xx | 客户端错误 | **400 Bad Request**, **401 未认证**, **403 禁止**, **404 Not Found** |
| 5xx | 服务端错误 | **500 Internal**, 502 Bad Gateway, **503 Service Unavailable** |

#### Cookie vs Session vs Token

| 机制 | 存储位置 | 特点 |
|------|---------|------|
| Cookie | 客户端浏览器 | 自动携带，有大小限制（4KB） |
| Session | 服务端内存 | 通过 Cookie 中的 SessionID 关联 |
| Token (JWT) | 客户端任意位置 | 无状态，服务端不存储，适合分布式 |

### Requests 库精讲

#### 参数传递方式（高频踩坑）

```python
import requests

# 1. params → URL 查询参数（GET 请求常用）
requests.get(url, params={"key": "value"})
# 实际请求：url?key=value

# 2. data → 表单编码（application/x-www-form-urlencoded）
requests.post(url, data={"user": "admin"})

# 3. json → JSON 格式（application/json）—— 最常用
requests.post(url, json={"user": "admin"})

# 4. files → 文件上传（multipart/form-data）
requests.post(url, files={"file": open("test.png", "rb")})
```

> ⚠️ **data vs json 的区别**：
> - `data` 发送表单格式，Content-Type 为 `application/x-www-form-urlencoded`
> - `json` 发送 JSON 格式，Content-Type 为 `application/json`
> - 不要同时使用两者！

#### 响应对象常用属性

```python
resp = requests.get(url)
resp.status_code   # 状态码：200
resp.json()        # 响应体解析为字典
resp.text          # 响应体原始文本
resp.headers       # 响应头（字典）
resp.cookies       # 响应 Cookie
resp.elapsed       # 请求耗时
```

#### Session 会话保持

```python
# 自动管理 Cookie，适合需要登录态的场景
session = requests.Session()
session.post(login_url, json={"user": "admin", "pwd": "123"})
# 后续请求自动带上登录 Cookie
session.get(profile_url)
```

---

## 🌳 阶段 2：V2 框架 —— Pytest 时代

### 2.1 用例发现规则（面试必考）

Pytest 自动发现测试用例的三条规则：

| 层级 | 规则 | 示例 |
|------|------|------|
| **文件名** | 以 `test_` 开头 **或** `_test` 结尾 | `test_login.py`、`login_test.py` |
| **类名** | 以 `Test` 开头（大写 T，且不能有 `__init__`） | `class TestLogin:` |
| **函数名** | 以 `test_` 开头（小写） | `def test_login_success():` |

```python
# ✅ 正确
class TestLogin:
    def test_success(self):
        pass

# ❌ 错误 - 类名小写
class testLogin:
    def test_success(self):
        pass

# ❌ 错误 - 有 __init__
class TestLogin:
    def __init__(self):  # Pytest 会跳过这个类！
        pass
```

### 2.2 常用命令行参数

```bash
pytest -v              # 详细模式，显示每条用例名称和结果
pytest -s              # 显示 print 输出（默认被捕获）
pytest -k "login"      # 只运行名称包含 "login" 的用例
pytest -m "smoke"      # 只运行标记为 @pytest.mark.smoke 的用例
pytest -x              # 遇到第一个失败就停止
pytest --maxfail=3     # 失败 3 个后停止
pytest --tb=short      # 简短的错误回溯信息
```

### 2.3 Fixture 机制（重中之重）

#### 基本用法

```python
import pytest

@pytest.fixture
def login_token():
    """前置：获取登录 token"""
    token = "abc123"  # 实际调用登录接口
    yield token       # yield 之前 = setup，之后 = teardown
    print("清理工作")  # yield 之后 = teardown

def test_get_user(login_token):
    """用例通过参数名自动注入 fixture"""
    assert login_token == "abc123"
```

#### Fixture 的 5 种 Scope（面试高频）

| Scope | 执行频率 | 适用场景 |
|-------|---------|---------|
| `function`（默认） | 每个测试函数执行一次 | 数据隔离要求高的场景 |
| `class` | 每个测试类执行一次 | 类级别的共享资源 |
| `module` | 每个 `.py` 文件执行一次 | 文件级别的数据库连接 |
| `package` | 每个包（目录）执行一次 | 包级别的环境初始化 |
| `session` | 整个 pytest 运行执行一次 | 全局登录 token、数据库连接池 |

#### 📊 Scope 执行次数计算（面试原题）

> **场景**：10 个测试文件，每个文件 5 条用例（共 50 条）

| Scope | 执行次数 | 计算逻辑 |
|-------|---------|---------|
| `session` | **1 次** | 整个运行只执行 1 次 |
| `module` | **10 次** | 每个文件执行 1 次 |
| `function` | **50 次** | 每条用例执行 1 次 |

```python
@pytest.fixture(scope="session")
def db_connection():
    """整个测试运行只连接一次数据库"""
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="module")
def test_data():
    """每个文件加载一次测试数据"""
    return load_data()

@pytest.fixture(scope="function")
def clean_cart():
    """每条用例前清空购物车"""
    clear_cart()
    yield
    clear_cart()
```

#### yield 的 setup/teardown 机制

```python
@pytest.fixture
def database():
    # ===== Setup 阶段（yield 之前）=====
    db = connect_db()
    create_test_data(db)
    
    yield db  # 把 db 传给测试用例
    
    # ===== Teardown 阶段（yield 之后）=====
    cleanup_test_data(db)
    db.close()
```

#### autouse 自动应用

```python
@pytest.fixture(autouse=True)
def log_test_name(request):
    """所有用例自动执行，不需要显式传参"""
    print(f"\n▶ 开始执行: {request.node.name}")
    yield
    print(f"\n◀ 执行完毕: {request.node.name}")
```

### 2.4 参数化 `@pytest.mark.parametrize`

```python
import pytest

# 单参数
@pytest.mark.parametrize("username", ["admin", "user1", "user2"])
def test_login(username):
    print(f"测试用户: {username}")

# 多参数
@pytest.mark.parametrize("username, password, expected", [
    ("admin", "123456", 200),
    ("admin", "wrong",  401),
    ("",      "123456", 400),
])
def test_login_multi(username, password, expected):
    # resp = login(username, password)
    # assert resp.status_code == expected
    pass
```

#### 参数化 + Fixture 组合使用

```python
@pytest.fixture(scope="session")
def login_session():
    """全局登录，获取 session"""
    session = requests.Session()
    session.post(login_url, json=creds)
    return session

@pytest.mark.parametrize("item_id", [1001, 1002, 1003])
def test_add_to_cart(login_session, item_id):
    """fixture 先执行获取 session，然后每个参数化数据都跑一次"""
    resp = login_session.post(cart_url, json={"item_id": item_id})
    assert resp.status_code == 200
```

### 2.5 conftest.py 层级机制（90% 候选人答不全）

#### 核心规则

1. **不需要 import**：Pytest 自动加载 `conftest.py` 中的 fixture
2. **就近原则**：优先使用距离测试文件最近的 `conftest.py`
3. **向下生效**：父目录的 `conftest.py` 对所有子目录生效
4. **可覆盖**：子目录的同名 fixture 覆盖父目录的

```
project/
├── conftest.py          # 全局 fixture（所有用例可用）
│   └── login_token      # 全局登录 token
├── tests/
│   ├── conftest.py      # tests 目录级 fixture
│   │   └── db_conn      # 测试专用数据库连接
│   ├── test_user/
│   │   ├── conftest.py  # 模块级 fixture（只对 test_user 生效）
│   │   │   └── test_user_data
│   │   └── test_user_api.py
│   └── test_order/
│       └── test_order_api.py  # 可用全局 + tests 级 fixture
```

#### 面试标准答法

> **Q：conftest.py 是什么？怎么用？**
>
> A：conftest.py 是 Pytest 的**全局 fixture 共享文件**，有三个特点：
> 1. **不需要 import**，Pytest 自动识别加载
> 2. **作用域由位置决定**，放在哪个目录就对那个目录及子目录生效
> 3. **遵循就近原则**，子目录的同名 fixture 会覆盖父目录的
>
> 常见用法：在根目录 conftest.py 里放 `scope="session"` 的登录 fixture，所有用例共享同一个 token。

### 2.6 全局登录 Token 的最佳实践

```python
# conftest.py（项目根目录）
import pytest
import requests

@pytest.fixture(scope="session")
def login_token():
    """整个测试运行只登录一次，所有用例共享 token"""
    resp = requests.post(
        "http://api.example.com/login",
        json={"username": "admin", "password": "123456"}
    )
    token = resp.json()["token"]
    yield token
    # teardown：如果需要登出
    # requests.post("http://api.example.com/logout", headers={"Authorization": token})

@pytest.fixture(scope="session")
def auth_headers(login_token):
    """封装带 token 的请求头"""
    return {"Authorization": f"Bearer {login_token}"}
```

---

## 🌳 阶段 2.5：Hook 钩子函数

### 核心概念

Hook = Pytest 预留的**"插槽"**：
- **你不调用它，Pytest 在特定时机自动调用它**
- 写在 `conftest.py` 里即可生效
- 不需要装饰器（除了 `hookwrapper`）

### 常用 Hook 一览

| Hook 函数 | 触发时机 | 典型用途 |
|-----------|---------|---------|
| `pytest_runtest_setup(item)` | 每条用例执行**前** | 打印用例名、前置检查 |
| `pytest_runtest_teardown(item)` | 每条用例执行**后** | 打印耗时、清理资源 |
| `pytest_runtest_makereport(item, call)` | 用例结果生成时 | 失败自动截图/记录日志 |
| `pytest_collection_modifyitems(items)` | 用例收集完成后 | 按优先级排序、过滤用例 |
| `pytest_configure(config)` | Pytest 启动时 | 注册自定义 marker、初始化配置 |

### 关键知识点

1. **Hook 参数是单条 `item`**，不是列表（每条用例触发一次）
2. **跨 Hook 共享数据用模块级变量**（不能用局部变量）
3. **`makereport` 要用 `hookwrapper=True` + `yield`** 拿 `report`

### 标准实现：用例计时 + 失败标记

```python
# conftest.py
import time
import pytest

# 模块级字典，跨函数共享数据
_start_times = {}

def pytest_runtest_setup(item):
    """每条用例执行前自动触发"""
    print(f"\n🚀 即将执行: {item.name}")
    _start_times[item.nodeid] = time.perf_counter()

def pytest_runtest_teardown(item):
    """每条用例执行后自动触发"""
    elapsed = time.perf_counter() - _start_times.pop(item.nodeid, 0)
    print(f"\n⏱️ {item.name} 耗时: {elapsed:.3f}s")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例结果生成时，判断是否失败"""
    outcome = yield                    # 让 Pytest 先生成 report
    report = outcome.get_result()      # 拿到 report 对象
    if report.when == "call" and report.failed:
        print(f"\n❌ FAILED: {item.name}")
```

> ⚠️ `report.when` 有三个值：`"setup"` / `"call"` / `"teardown"`，
> 我们通常只关心 `"call"`（用例执行阶段）的失败。

---

## 🌲 阶段 3：V3 框架 —— 分层架构（进行中）

### 核心思想：关注点分离

**痛点**：用例里既有"技术细节"又有"业务逻辑"，耦合太紧。

**解决方案**：让每一层只干一件事。

### 五层架构

```
📦 framework/
├── ⚙️ config/         # 配置层：环境配置（base_url、超时时间）
├── 🔧 utils/          # 工具层：日志、加解密、数据库连接
├── 🌐 api/            # 接口层：每个接口封装成类/方法
├── 📊 data/           # 数据层：YAML/Excel/CSV 测试数据
├── 🧪 testcases/      # 用例层：只写业务逻辑
└── conftest.py        # 全局 Fixture
```

| 层 | 职责 | 变更原因 |
|----|------|---------|
| 配置层 | 管理环境变量、URL、超时 | 换环境时只改这里 |
| 工具层 | 提供通用能力 | 新增通用功能时改这里 |
| 接口层 | 封装 HTTP 请求为业务方法 | 接口变更时只改这里 |
| 数据层 | 管理测试数据 | 换数据时只改这里 |
| 用例层 | 编排业务流程 + 断言 | 业务逻辑变更时改这里 |

### 分层前 vs 分层后

```python
# ❌ 分层前：所有东西混在一起
def test_create_order():
    # 登录（技术细节）
    resp = requests.post("http://dev.api.com/login",
                         json={"user": "admin", "pwd": "123"})
    token = resp.json()["token"]
    # 加购（技术细节 + 业务）
    requests.post("http://dev.api.com/cart/add",
                  headers={"Authorization": f"Bearer {token}"},
                  json={"item_id": 1001})
    # 下单（技术细节 + 业务）
    resp = requests.post("http://dev.api.com/order/create",
                         headers={"Authorization": f"Bearer {token}"})
    assert resp.json()["status"] == "success"
```

```python
# ✅ 分层后：用例只写业务流程
def test_create_order(login_token, test_data):
    CartAPI.add_item(login_token, test_data["item_id"])
    order = OrderAPI.create(login_token)
    assert order["status"] == "success"
```

> 🎯 **一眼看懂业务，技术细节全部下沉到接口层和工具层。**

---

## 📋 面试高频题速查

### HTTP 相关

| 题目 | 答案要点 |
|------|---------|
| GET vs POST 区别？ | GET 幂等、无请求体、参数在 URL；POST 非幂等、有请求体 |
| Cookie/Session/Token 区别？ | Cookie 客户端存储；Session 服务端存储；Token 无状态 |
| 常见状态码？ | 200/301/302/400/401/403/404/500/502/503 |

### Pytest 相关

| 题目 | 答案要点 |
|------|---------|
| 用例发现规则？ | 文件 test_/\_test，类 Test 开头，函数 test_ 开头 |
| Fixture scope 有几种？ | 5 种：function/class/module/package/session |
| conftest.py 作用？ | 全局共享 fixture，不需要 import，就近原则 |
| yield 在 fixture 里的作用？ | yield 前 = setup，yield 后 = teardown |
| 参数化怎么用？ | `@pytest.mark.parametrize("参数名", [数据列表])` |

### 框架设计相关

| 题目 | 答案要点 |
|------|---------|
| 框架分几层？ | 配置层/工具层/接口层/数据层/用例层 |
| 为什么要分层？ | 关注点分离，降低耦合，提高可维护性 |
| 接口关联怎么处理？ | 上一个接口返回值通过 fixture 或变量传给下一个 |

---

## 🗺️ 学习路线全景图

```
✅ 阶段 0：思想奠基 → 测试金字塔、ROI、岗位认知
✅ 阶段 1：V1 脚本时代 → HTTP、Requests、第一个测试
✅ 阶段 2：V2 Pytest 时代 → Fixture、参数化、conftest、Hook
🔄 阶段 3：V3 分层架构 → 五层设计、接口封装、数据驱动（进行中）
⬜ 阶段 4：V4 工程化 → Allure 报告、重试、并发、Mock
⬜ 阶段 5：V5 持续集成 → Git、Docker、Jenkins、通知
```

---

*最后更新：2026-05-04*
