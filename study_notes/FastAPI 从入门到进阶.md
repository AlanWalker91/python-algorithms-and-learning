# FastAPI 从入门到进阶 · 系统学习路线图

## 你的画像
- **基础**：Python 熟练，无 Web 后端经验
- **目标**：REST API + AI/LLM 后端 + 微服务/企业级系统 + 面试求职
- **时间**：每周约 24 小时（建议 3~4 小时/天）
- **风格**：理论 + 代码结合，知识点配小练习

---

## 第一阶段：Web 后端基础（第 1–2 周）

**目标**：理解 HTTP、API 设计、Python Web 基础框架概念。

| 天数 | 内容 | 实践任务 |
|------|------|----------|
| 1–2 | HTTP 协议核心：请求/响应、状态码、方法、Header/Body | 用 `curl` 或 Postman 调用 3 个公开 API，观察响应结构 |
| 3–4 | JSON 数据格式、RESTful 设计原则、API 版本管理 | 为一个"图书管理"业务设计 RESTful 接口文档 |
| 5–6 | Python 异步编程基础：`async/await`、`asyncio`、事件循环 | 写 3 个 `asyncio` 小脚本：并发请求、定时任务、协程通信 |
| 7–8 | Web 框架通用概念：路由、请求处理、中间件、模板渲染 | 用 Flask 快速写一个"Hello API"（对比后续 FastAPI） |
| 9–12 | 数据库基础：SQL 关系型数据库（PostgreSQL）、ORM 思想 | 用 `psycopg2` 写原生 SQL CRUD；了解索引、事务 |
| 13–14 | **阶段检查**：把 Flask 的图书管理 API 用 FastAPI 重写初版 | 对比两者的代码量和类型提示差异 |

---

## 第二阶段：FastAPI 核心入门（第 3–4 周）

**目标**：熟练掌握 FastAPI 的基础用法，能独立搭建完整 API 项目。

| 天数 | 内容 | 实践任务 |
|------|------|----------|
| 15–16 | FastAPI 安装与项目结构；`@app.get/post/put/delete`；路径参数与查询参数 | 搭建项目骨架，实现带路径参数和查询参数的 API |
| 17–18 | Pydantic 数据模型：`BaseModel`、字段校验、嵌套模型、枚举 | 为图书/用户/订单设计 5 个以上 Pydantic Schema |
| 19–20 | 请求体（Request Body）、表单数据、文件上传 | 实现"创建图书+上传封面图"接口 |
| 21–22 | 响应模型、`response_model`、状态码、异常处理 `HTTPException` | 统一错误响应格式；自定义全局异常处理器 |
| 23–24 | 依赖注入系统：`Depends`、依赖嵌套、带 yield 的依赖（数据库连接池） | 实现数据库 session 依赖注入；写可复用的权限校验依赖 |
| 25–26 | 后台任务 `BackgroundTasks`、静态文件、模板引擎（Jinja2） | 实现"用户注册后异步发送欢迎邮件"（模拟） |
| 27–28 | **阶段检查**：完成一个完整的"图书管理系统 API" | 包含 CRUD、分页、搜索、文件上传、统一错误处理 |

---

## 第三阶段：FastAPI 进阶特性（第 5–6 周）

**目标**：掌握高级功能，为生产级和 AI 应用做准备。

| 天数 | 内容 | 实践任务 |
|------|------|----------|
| 29–30 | 安全与认证：OAuth2 + JWT（`python-jose` + `passlib`） | 实现注册/登录/刷新 Token；保护路由 |
| 31–32 | 中间件：自定义中间件、CORS、GZip、请求日志 | 实现请求耗时统计中间件和全局请求 ID |
| 33–34 | WebSocket 实时通信：`@app.websocket`、连接管理 | 实现一个简单在线聊天室或实时通知推送 |
| 35–36 | API 文档自定义：OpenAPI schema、标签分组、示例数据 | 美化 Swagger UI，为每个接口添加详细描述和示例 |
| 37–38 | 事件启动/关闭：`@app.on_event`/`lifespan`、配置管理（pydantic-settings） | 实现应用启动时数据库迁移检查、关闭时资源清理 |
| 39–40 | 测试：Pytest + `TestClient`、异步测试、依赖覆盖 | 为核心 API 写单元测试和集成测试，覆盖率达到 80%+ |
| 41–42 | **阶段检查**：把图书系统扩展为"多用户+权限+JWT+测试覆盖" | 完整跑通测试套件，验证文档和认证流程 |

---

## 第四阶段：AI / LLM 应用后端（第 7 周）

**目标**：将 FastAPI 与 AI 工作流结合，搭建 LLM 服务。

| 天数 | 内容 | 实践任务 |
|------|------|----------|
| 43–44 | 同步 vs 异步调用 OpenAI/Anthropic API；流式响应 `StreamingResponse` | 实现一个 `/chat` 接口，支持 SSE 流式输出 |
| 45–46 | 向量数据库入门：pgvector / ChromaDB；Embeddings 存储与检索 | 搭建"文档上传 -> 切分 -> Embedding -> 向量检索"流程 |
| 47–48 | RAG 完整链路：文档上传、向量化、检索、LLM 生成答案 | 实现一个可对话的知识库问答 API |
| 49 | 任务队列集成：`celery` / `arq` + Redis；长任务状态追踪 | 实现"异步文档处理"接口，可查询处理进度 |
| 50 | **阶段检查**：部署一个可运行的 AI 问答后端 | 包含文件上传、RAG 问答、流式输出、任务状态查询 |

---

## 第五阶段：微服务与企业级部署（第 8–9 周）

**目标**：掌握生产部署、性能优化、微服务架构。

| 天数 | 内容 | 实践任务 |
|------|------|----------|
| 51–52 | ASGI 服务器：`uvicorn` vs `hypercorn`；Worker 数量、多进程部署 | 用 `gunicorn` + `uvicorn.workers` 部署图书系统 |
| 53–54 | Docker 容器化：Dockerfile 编写、多阶段构建、.dockerignore | 为项目编写生产级 Dockerfile，镜像体积 < 200MB |
| 55–56 | 反向代理与负载均衡：Nginx / Traefik；HTTPS、域名配置 | 用 Docker Compose 部署：Nginx + FastAPI + PostgreSQL |
| 57–58 | 监控与日志：`prometheus_client` + Grafana、结构化日志（`structlog`） | 为 API 添加 `/metrics` 端点，配置 Prometheus 采集 |
| 59–60 | 微服务通信：`httpx` 异步 HTTP、gRPC 入门、消息队列（RabbitMQ/NATS） | 拆分为"用户服务"和"图书服务"，实现服务间调用 |
| 61–62 | 缓存策略：`redis-py`、接口缓存、限流 `slowapi` | 为高频查询接口加 Redis 缓存和速率限制 |
| 63–64 | **阶段检查**：完整 CI/CD 部署流水线 | GitHub Actions -> Docker Build -> 云服务器部署 |

---

## 第六阶段：面试强化与查漏补缺（第 10 周）

| 天数 | 内容 |
|------|------|
| 65–66 | 高频面试题梳理：FastAPI 优缺点、ASGI vs WSGI、依赖注入原理、Pydantic v2 变化 |
| 67–68 | 系统设计练习：设计一个"高并发短链服务"或"实时通知系统"，用 FastAPI 作为网关 |
| 69–70 | 源码阅读：挑 2~3 个 FastAPI 核心模块（依赖注入、路由匹配、异常处理）读源码 |
| 71–72 | 整理学习笔记 + 项目作品集，更新 GitHub，准备简历项目描述 |

---

## 配套资源推荐

**官方与核心文档**
- FastAPI 官方文档（中文翻译版）—— 第一参考
- Pydantic v2 官方文档 —— 数据模型必学
- Uvicorn / Starlette 文档 —— 理解底层 ASGI

**工具栈**
- 数据库：PostgreSQL + `asyncpg` / `sqlalchemy` (2.0 async)
- ORM：`sqlmodel`（FastAPI 作者出品，Pydantic + SQLAlchemy 结合）
- 缓存/队列：Redis + `celery` 或 `arq`
- 测试：`pytest` + `httpx` + `pytest-asyncio`
- 部署：Docker + Nginx + 云服务器（或 Render / Railway 练手）

**项目练手建议**
1. 图书管理系统 API（基础 CRUD + 认证）
2. 个人博客 API（文章、分类、评论、用户系统）
3. AI 知识库问答系统（RAG + 流式输出 + 文件上传）
4. 微服务电商雏形（用户/商品/订单服务拆分）

---

## 学习节奏建议

```text
每周 24 小时 ≈ 每天 3.5 小时
  ├── 1 小时：阅读文档/看视频教程
  ├── 1.5 小时：动手写代码
  └── 1 小时：整理笔记 + 复盘当天问题
```

**每两周做一次"阶段检查项目"**，不要只看不写。FastAPI 的精髓在于**类型安全 + 异步 + 自动生成文档**，每学一个知识点就问自己："这个特性如何帮我写出更健壮、更高性能的 API？"
