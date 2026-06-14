# FastAPI 系统学习笔记（SDET 视角）

> 面向测试开发的 FastAPI 知识体系：从设计哲学到测试落地。
> 学习框架：**地基 → 主干 → 灵魂 → 进阶 → 深水区**，五层递进。
> 每个知识点附 **原理 + 对比表 + 面试话术**。

---

## 总览：五层学习地图

| 层 | 主题 | 核心一句话 | SDET 价值 |
|---|---|---|---|
| 一 · 地基 | 类型驱动 + ASGI | 类型注解放在「公开可读」处，工具来利用它 | 理解 422 校验机制 |
| 二 · 主干 | Pydantic 双向校验 | 模型即用例规格书 | 从模型反推边界用例 |
| 三 · 灵魂 | 依赖注入 Depends | 声明依赖，框架自动注入 | `dependency_overrides` 做最干净的 mock |
| 四 · 进阶 | 中间件 / 后台任务 / 异步生态 | 异步不能断链 | 性能排查、后台任务测试 |
| 五 · 深水区 | TestClient 实战 | 内存发请求，不起服务 | CI 友好的接口自动化 |

**贯穿全篇的一条主线**：FastAPI 的所有「魔法」都源自一个动作——**读你写的类型注解**，然后替你完成转换、校验、文档、注入。一次声明，框架代劳。

---

## 第一层 · 地基：类型驱动与 ASGI

### 1.1 类型注解为什么是命脉

**原理**：Python 自身在运行时**完全不管**类型注解。`def f(x: int)` 传字符串照样跑，注解只是挂在函数签名上的元数据。但正因为它放在「所有工具都能读到」的位置，FastAPI 才能用 `inspect` 读取它，一次声明换来四件事：

| FastAPI 用类型注解做的事 | Flask 路由里的 `int` 能做吗 |
|---|---|
| 数据转换（`"3"` → `3`） | ✅ 能（唯一重合） |
| 校验失败自动返回 **422** | ❌ Flask 直接 404，不说原因 |
| 自动生成 `/docs` OpenAPI 文档 | ❌ 完全没有 |
| IDE 自动补全与类型检查 | ❌ 字符串里的东西 IDE 看不懂 |

**关键区别**：Flask 的 `int` 写在路由字符串 `<int:user_id>` 里，是路由系统的私有财产，匹配完即弃；FastAPI 的 `int` 写在函数参数注解 `user_id: int` 上，是公开声明，校验、文档、IDE 全来蹭它。

**例**：
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```
- 访问 `/users/3` → `{"id": 3}`
- 访问 `/users/abc` 或 `/users/3.5` → **422**，且不会偷偷取整（绝不猜测用户意图）

### 1.2 标志性状态码 422

校验失败 FastAPI 默认返回 **422 Unprocessable Entity**，而非 400。这是 FastAPI 的「指纹」，响应体会精确告诉调用方哪个字段错在哪。

### 1.3 ASGI 与异步的本质

**原理**：异步的高并发**不是因为算得快，而是因为「等的时候不浪费」**。

| 模型 | 等 IO 时 worker 在干嘛 | 结果 |
|---|---|---|
| 同步（WSGI/Flask） | 卡死干等，被这个请求独占 | 要靠多进程堆并发，内存吃紧 |
| 异步（ASGI/FastAPI） | 撒手去处理别的请求，IO 回来再切回 | 单 worker 填满等待空档，高并发 |

**只对 IO 密集有效**：等数据库、等网络这类「有等待空档」的场景才受益。纯 CPU 计算没有等待空档，塞进 `async` 会堵死整个事件循环。

**分工链（面试必背）**：
```
uvicorn (ASGI 服务器，管连接和事件循环)
   ↓ ASGI 协议（插座标准）
FastAPI (框架，写接口逻辑，本身不处理连接)
```
对应旧世界：`gunicorn → WSGI → Flask`。

> **面试话术**：「FastAPI 是 ASGI 框架，本身不处理网络连接，要靠 uvicorn 这类 ASGI 服务器来跑。异步的本质是 IO 等待时让出事件循环，所以只对 IO 密集场景有效；CPU 密集任务塞进 async 会阻塞整个事件循环。」

---

## 第二层 · 主干：Pydantic 双向校验

### 2.1 声明式校验取代手写 if

**原理**：把请求体定义成一个 `BaseModel` 类，FastAPI 读这个类每个字段的类型注解（机制同第一层，只是从单值放大到整个对象），自动完成存在性、类型、范围、格式校验，多个错误一次性报告。

**例**：手写校验需二十行 if，Pydantic 三行搞定。
```python
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    username: str = Field(min_length=3)
    age: int = Field(ge=0, le=150)
    email: EmailStr
```

**Field 常用约束**：

| 写法 | 管什么 |
|---|---|
| `gt` / `ge` / `lt` / `le` | 数值范围（> / ≥ / < / ≤） |
| `min_length` / `max_length` | 字符串/列表长度 |
| `pattern` | 正则匹配（如手机号 `^1\d{10}$`） |
| `default` | 默认值（没传时用它） |

### 2.2 模型即用例规格书（SDET 核心）

开发写下 `Field` 约束的那一刻，测试的边界用例就已确定。**单个字段从三个维度反推用例**：

| 维度 | 针对 `quantity: int = Field(ge=1, le=99)` 的用例 | 预期 |
|---|---|---|
| **数值边界** | 0 / 1 / 99 / 100 | 422 / 通过 / 通过 / 422 |
| **类型** | `"abc"`（字符串）、`1.5`（小数） | 422 / 422 |
| **存在性** | 漏传字段、显式 `null` | 422 / 422 |

> **面试话术**：「我设计 API 用例时先读 Pydantic 模型，每个字段从数值边界、类型、存在性三个维度反推等价类——约束即用例。」

### 2.3 response_model：输出过滤与安全测试

**原理**：Pydantic 在 FastAPI 里是**双向**的。`response_model` 指定一个「对外模型」，框架在返回前用它把数据套一遍，模型上没有的字段被强制过滤——想漏都漏不掉。

**例**：防止密码 hash 泄露（OWASP 敏感数据暴露）。
```python
class UserPublic(BaseModel):       # 对外模型，只放安全字段
    id: int
    username: str
    email: str
    # 没有 hashed_password、没有 is_admin

@app.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: int):
    user = db.query(...)           # 捞出完整记录（含密码）
    return user                    # 框架按 UserPublic 过滤后才输出
```

| 方向 | 模型管什么 | SDET 测什么 |
|---|---|---|
| 进（请求体） | 校验输入合法性 | 边界 / 类型 / 存在性 |
| 出（response_model） | 过滤输出、藏敏感字段 | 响应里有没有混进 `password`/`token` 等敏感字段 |

> **面试话术**：「我会对照 `response_model` 检查响应体，确认没有 password、token 这类敏感字段泄露——把功能测试和安全测试连起来。」

---

## 第三层 · 灵魂：依赖注入 Depends

### 3.1 它解决什么

**原理**：消除「每个接口都要做、但跟业务无关」的公共逻辑（验登录、开 DB 会话）。你不手动调用，而是在参数签名里**声明依赖**，框架在执行接口前自动先跑依赖、把返回值注入进来。

**例**：
```python
def get_current_user(token: str):
    user = verify_token(token)
    if user is None:
        raise HTTPException(401)
    return user

@app.get("/profile")
def profile(user = Depends(get_current_user)):   # 声明依赖，不手动调
    return {"name": user.name}                    # 进函数时 user 已就绪
```

### 3.2 与 pytest fixture 是同一个思想

| | pytest fixture | FastAPI Depends |
|---|---|---|
| 怎么声明需要 | 测试函数参数名写 fixture 名 | 参数 `= Depends(函数)` |
| 谁来执行 | pytest 自动调 | FastAPI 自动调 |
| 拿到什么 | fixture 返回值 | 依赖函数返回值 |
| 解决什么 | 测试间共享的准备逻辑 | 接口间共享的准备逻辑 |
| 能否嵌套 | fixture 可依赖 fixture | 依赖可依赖依赖 |

### 3.3 dependency_overrides：杀手锏

**原理**：依赖的值是框架**从外面注入**的，那「注入什么」就由框架配置说了算。测试时用 `app.dependency_overrides` 这张「替换表」，一行把真依赖换成假的，**不用起任何 mock 服务**。

**例**：
```python
def get_fake_db():
    return FakeDB(...)

app.dependency_overrides[get_db] = get_fake_db   # 一行：凡是要 get_db 的地方改用假的
# 测完：app.dependency_overrides.clear()
```

| | 起 Mock 服务 | dependency_overrides |
|---|---|---|
| 要起进程吗 | 要，真跑一个服务 | 不用，纯内存替换 |
| 从哪里骗 | 外部（网络层） | 内部（框架直接换掉） |
| 代码量 | 一套配置 + 服务 | 一行 |
| 适合场景 | 测真·外部依赖（第三方 API） | 测自己接口逻辑、隔离 DB |

> **面试话术**：「我用 pytest fixture 加 `dependency_overrides` 组合。fixture 负责造内存假 DB 并在测试前后替换和清理，`dependency_overrides` 负责接进 app——因为接口的 db 本来就是 Depends 注入的，测试时换掉注入源就能完全隔离真实数据库，还能精确控制返回数据。不用起任何 mock 服务，纯内存替换，快且干净。」

---

## 第四层 · 进阶：中间件 / 后台任务 / 异步生态

### 4.1 请求生命周期（位置关系）

```
请求进来
  → 中间件(进)        记开始时间、CORS、全局校验
    → 依赖 Depends    验登录、开 DB 会话
      → 接口函数      业务逻辑 + 登记后台任务
    → 中间件(出)      算总耗时、塞 header
  → 响应发出
                      → 后台任务跑（响应之后才执行！）
```

### 4.2 中间件 Middleware

**原理**：包在所有接口最外层的全局横切层，每个请求进出各过一次。`call_next` 之前 = 请求进去前；`call_next` 之后 = 响应出来后。

**例**：给每个响应加服务端处理耗时。
```python
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response
```

| | 中间件 | 依赖 Depends |
|---|---|---|
| 范围 | 全局，所有请求无差别 | 按接口挑，声明了才生效 |
| 能拿到具体参数吗 | 拿不到（在参数解析前） | 能（它就是在准备参数） |
| 用途 | 耗时统计、CORS、全局日志 | 验登录、开 DB 会话 |

**SDET 价值**：上面的 `X-Process-Time` 给出**服务端真实处理时间**（排除网络），压测时读 header 即可定位「慢在服务端还是网络」。中间件「一处错全局崩」，需专门测（如 CORS 是否对预期源放行）。

### 4.3 后台任务 BackgroundTasks

**原理**：`add_task` 只登记不立即执行，FastAPI **先发响应、再跑任务**。

**两条铁律**：

| 铁律 | 原因 |
|---|---|
| 只放「失败也不影响本次操作正确性」的事 | 失败无法回传给用户 |
| 任务内部必须自己处理异常和日志 | 响应已发出，异常没人接 |

**判断标准**：这件事失败了，会不会影响用户本次操作的正确性？
- 发欢迎邮件 → 失败不影响注册结果 → 可丢后台
- 扣款/写订单/存用户 → 失败毁掉本次操作 → 必须当场做完、失败回滚

**例**：
```python
@app.post("/register")
def register(user: UserRegister, background: BackgroundTasks):
    save_user(user)                              # 核心：当场做完
    background.add_task(send_email, user.email)  # 非核心：登记后台
    return {"msg": "注册成功"}                    # 立刻返回
```

**SDET 价值**：后台任务在响应后才跑，**测接口响应覆盖不到它**，必须把任务函数单独做单元测试或用 mock 断言其被正确调用。

> **面试话术（何时上 Celery）**：「BackgroundTasks 适合轻量、丢了也认的活，跟 app 同进程、重启即丢。当任务重要到要重试、要持久化、要监控、要横向扩展 worker 时，就该上 Celery 这类独立任务队列——它把任务丢进 Redis/RabbitMQ，由独立 worker 进程执行。」

### 4.4 异步生态：不能断链

**原理**：`async def` 接口要真异步，链路里每一环都得是 async，**混进一个同步阻塞库就退化成假异步**，堵死事件循环。

**反例（假异步陷阱）**：
```python
import requests
@app.get("/proxy")
async def proxy():
    resp = requests.get("https://slow-api.com")   # 同步库！卡住不让出
    return resp.json()                             # 高并发下堵死全服务
```

**正解**：用异步库 + `await`。
```python
import httpx
@app.get("/proxy")
async def proxy():
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://slow-api.com")   # await：等时让出
    return resp.json()
```

**async def vs def（反直觉但关键）**：

| 接口主要在干嘛 | 该用 | 为什么 |
|---|---|---|
| 等 IO（async DB、async HTTP） | `async def` | 等待时让出事件循环 |
| 重计算 / 调用同步阻塞库 | `def`（普通同步） | FastAPI 把 def 丢进**线程池**，不堵事件循环 |
| 轻量返回 JSON | 都行 | 无所谓 |

> **面试话术**：「async def 适合 IO 等待，普通 def 适合 CPU 密集或同步阻塞调用，因为 FastAPI 会把 def 丢进线程池避免阻塞事件循环。压测发现 async 接口并发上不去，先查链路里是否混了 requests、老版 pymysql 这类同步阻塞库。」

### 4.5 CORS 名词解释

浏览器默认禁止网页向「别的域名」发请求（跨域）。CORS 是后端通过响应 header（`Access-Control-Allow-Origin` 等）声明「我允许某些源访问」。FastAPI 用 `CORSMiddleware` 配置。

**易错点**：CORS 是**浏览器**的限制，Postman/curl/TestClient 等非浏览器工具不受影响——所以常「代码测着没事，前端一接就报 CORS 错」。

---

## 第五层 · 深水区：TestClient 实战

### 5.1 TestClient 的精髓

**原理**：用法像 `requests`，但**不起服务、不走网络、没有端口**——直接在内存里把请求喂给 `app` 对象。和 `dependency_overrides` 是同一个哲学：app 是可直接调用、可直接改配置的对象。

| | requests + 真服务 | TestClient |
|---|---|---|
| 要先起服务吗 | 要，uvicorn 起在端口 | 不要，内存直接调 app |
| 走网络吗 | 走，有开销和不确定性 | 不走，纯内存，快且稳 |
| 适合 | 端到端 / 冒烟 | 单元 / 集成 |
| 在 CI 里 | 要编排服务启动 | 一条 pytest 直接跑 |

> **面试话术**：「TestClient 不依赖起服务，一条 pytest 就能在流水线里跑完接口测试，不用在 CI 里编排服务启动和健康检查，集成进 gate 非常干净。」（注：TestClient 测代码逻辑，不测真实部署；端到端冒烟仍需 requests 打真服务。）

### 5.2 完整测试范例（串起前四层）

```python
import pytest
from fastapi.testclient import TestClient
from main import app, get_db

@pytest.fixture
def client_with_fake_db():
    fake = FakeDB()                                   # 造内存假 DB
    app.dependency_overrides[get_db] = lambda: fake   # 第三层：换掉真依赖
    yield TestClient(app)
    app.dependency_overrides.clear()                  # 测完清理，别污染别的测试

def test_create_user_success(client_with_fake_db):
    resp = client_with_fake_db.post("/users", json={"username": "alan", "password": "123456"})
    assert resp.status_code == 201
    assert resp.json()["username"] == "alan"
    assert "password" not in resp.json()              # 第二层：验 response_model 过滤了密码
```

### 5.3 负向用例的两个严谨度要点

```python
def test_create_user_missing_username(client_with_fake_db):
    resp = client_with_fake_db.post("/users", json={"password": "123456"})  # 漏 username
    assert resp.status_code == 422
    assert "username" in str(resp.json())     # 断言错误确实指向 username
```

1. **负向用例必须基于模型设计**：`password: ""` 是否触发 422，取决于模型有没有 `min_length` 约束；脱离模型凭感觉选非法值，可能根本测不到你以为的东西。选「漏掉必填字段」最稳——无论模型怎么写都必然 422。
2. **断言要断到点子上**：不只断言「是 422」，还要断言「422 是因为目标字段」，否则接口因别的原因返回 422 时用例会**假性通过**。

---

## 高频面试题与答案

**Q1. FastAPI 参数校验失败返回什么状态码？为什么不是 400？**
返回 **422 Unprocessable Entity**。这是 FastAPI（基于 Pydantic）的标志性状态码，表示请求格式合法但语义校验不通过，响应体会精确指出哪个字段错在哪。

**Q2. FastAPI 和 uvicorn 是什么关系？**
FastAPI 是 **ASGI 框架**，只负责写接口逻辑，本身不处理网络连接；uvicorn 是 **ASGI 服务器**，负责监听端口、管理连接和事件循环。两者通过 ASGI 协议对接。类比旧世界的 Flask（WSGI 框架）+ gunicorn。

**Q3. 异步框架为什么能扛高并发？是因为算得更快吗？**
不是算得快，是**等的时候不浪费**。IO 等待（等 DB、等网络）时，异步 worker 让出事件循环去处理别的请求，IO 回来再切回。所以只对 **IO 密集**场景有效。

**Q4. 在 async def 接口里写一段纯 CPU 计算会怎样？**
会**堵死整个服务**。CPU 计算没有 IO 等待空档，永不让出事件循环，独占线程，导致所有请求（包括轻量接口）被阻塞。正解：重计算用普通 `def`（FastAPI 自动丢线程池）或交给进程池/Celery。

**Q5. async def 和普通 def 在 FastAPI 里有什么区别？什么时候用哪个？**
`async def` 跑在事件循环线程上，适合 IO 等待型（用 async 库 + await）；普通 `def` 会被 FastAPI 丢进**线程池**执行，不阻塞事件循环，适合 CPU 密集或调用同步阻塞库的场景。

**Q6. 什么是「假异步」？怎么排查？**
`async def` 接口里调用了同步阻塞库（如 `requests`、老版 `pymysql`），该库卡住时不让出事件循环，导致异步退化、并发堵死。排查方向：压测发现 async 接口并发上不去，检查链路是否混入同步阻塞库，换成 `httpx` 等 async 库 + `await`。

**Q7. 如何设计 FastAPI 接口的测试用例？**
先读 Pydantic 模型，针对每个字段从**数值边界、类型、存在性**三个维度反推等价类——约束即用例。正向测 happy path，负向测越界/类型错/缺字段（基于模型选必然触发 422 的非法值）。

**Q8. 写接口自动化测试时，怎么做到不依赖真实数据库？**
用 **pytest fixture + dependency_overrides** 组合。fixture 造内存假 DB 并在测试前后替换和清理，`dependency_overrides` 把假依赖接进 app。因为 db 是 Depends 注入的，换掉注入源即可隔离真实数据库，纯内存替换，不用起 mock 服务。

**Q9. Depends 和中间件有什么区别？**
中间件是**全局**横切，所有请求无差别经过，在参数解析之前，拿不到具体接口参数（适合耗时统计、CORS、全局日志）；Depends 是**按接口**声明，能拿到/准备具体参数（适合验登录、开 DB 会话）。

**Q10. response_model 有什么用？对测试意味着什么？**
它指定对外模型，框架返回前按它过滤字段，防止敏感数据（密码 hash、token、is_admin）泄露。测试时应对照 response_model 断言响应体不含敏感字段，把功能测试和安全测试结合。

**Q11. BackgroundTasks 和 Celery 怎么选？**
BackgroundTasks 适合轻量、丢了也认、与 app 同进程的活（发邮件、写日志）；当任务需要重试、持久化、监控、横向扩展时用 Celery（独立任务队列 + 独立 worker + 消息队列）。

**Q12. 测一个带后台任务的接口要注意什么？**
后台任务在**响应发出之后**才执行，测接口响应覆盖不到它。必须把任务函数单独做单元测试，或用 mock 断言其被正确调用。

**Q13. TestClient 和用 requests 测有什么区别？**
TestClient 不起服务、不走网络，内存里直接调 app，快且 CI 友好，适合单元/集成测试；requests 打真服务走网络，适合端到端/冒烟测试（验证真实部署）。两者分工而非替代。

**Q14. 写负向用例有哪些容易踩的坑？**
① 凭感觉选非法值——是否触发 422 取决于模型约束，应基于模型设计，或选「漏必填字段」这种必然失败的值；② 只断言状态码不断言错误原因——会导致用例假性通过，应断言错误确实指向目标字段。

---

## 后续可自学清单（用到再查，无新思想）

- `APIRouter`：拆分大型项目的路由
- 异步 ORM：SQLAlchemy 2.0 async / Tortoise ORM + await 查询
- OAuth2 + JWT 完整认证流程（基于 Depends）
- WebSocket：实时双向通信
- `lifespan`：应用启动/关闭钩子（替代旧的 startup/shutdown 事件）
- `@field_validator` / 嵌套模型：Pydantic 自定义校验与复杂结构
