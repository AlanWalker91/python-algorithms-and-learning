# FastAPI 系统学习计划（入门 → 进阶）

## 概览

基于你的背景（Python 基础 OK，后端经验少，每周 20+ 小时，目标求职转岗 + 项目实战 + 系统提升，项目方向 AI 应用后端），本路线以 **5 周高强度冲刺** 完成从入门到能独立开发 AI 后端并上线部署。学完后你将拥有一套完整的 FastAPI + AI 实战项目，足以写入简历。

---

## 第一阶段：筑基期（第 1 周）

### 目标：掌握 Python 异步编程 + FastAPI 核心基础

| 模块 | 内容 | 产出 |
|------|------|------|
| Python 异步补完 | `async/await`、`asyncio` 事件循环、协程概念 | 能写基础的异步爬虫 / 并发请求 |
| FastAPI 起步 | 路径操作、`Request/Response`、路径参数、查询参数、`Pydantic` 模型校验 | 能写带数据校验的 RESTful 接口 |
| 请求与响应 | `Body`、`Form`、`File/UploadFile`、`Header`、`Cookie`、`Response` 自定义 | 能处理文件上传、表单提交、自定义响应头 |
| 依赖注入系统 | `Depends`、依赖嵌套、子依赖、可缓存依赖 | 理解依赖注入的核心设计模式 |
| 配置与环境 | `pydantic-settings`、`.env`、多环境配置 | 能区分 dev/prod 配置 |

### 推荐资源
- 官方文档：https://fastapi.tiangolo.com/learn/
- 《FastAPI 现代 Python Web 开发》（书）
- 异步基础：Real Python asyncio 教程

### 阶段产出
> 一个 CRUD 小 Demo：用户注册/登录信息的增删改查 API，带 Pydantic 校验和基础依赖注入。

---

## 第二阶段：数据库与持久化（第 2 周）

### 目标：熟练操作关系型数据库 + 异步 ORM

| 模块 | 内容 | 产出 |
|------|------|------|
| SQLAlchemy 2.0 | `DeclarativeBase`、`Mapped` 类型提示、引擎与会话 | 能写类型安全的模型定义 |
| 异步数据库 | `asyncpg` + `create_async_engine`、`AsyncSession` | 能写全异步的 CRUD |
| 关系与查询 | 一对多、多对多、关联加载（`selectinload`、`joinedload`） | 能处理复杂关联查询 |
| Alembic 迁移 | 数据库版本管理、升级/回滚、自动生成迁移脚本 | 能管理数据库 schema 变更 |
| 连接池与性能 | `pool_pre_ping`、连接池配置、N+1 问题排查 | 知道如何优化数据库访问 |

### 推荐资源
- SQLAlchemy 2.0 官方文档
- Alembic 官方文档
- 教程：https://docs.sqlalchemy.org/en/20/tutorial/

### 阶段产出
> 升级第一阶段 Demo：接入 PostgreSQL + SQLAlchemy 2.0 异步 ORM，实现完整的用户、文章、评论系统，含 Alembic 迁移。

---

## 第三阶段：认证、安全与工程化（第 3 周）

### 目标：掌握生产级 API 的安全与架构能力

| 模块 | 内容 | 产出 |
|------|------|------|
| JWT 认证 | `python-jose` + `passlib`，`OAuth2PasswordBearer` 流程 | 实现完整的注册/登录/JWT 鉴权 |
| 权限控制 | RBAC 角色权限设计、路由依赖做权限校验 | 不同角色访问不同接口 |
| 中间件与异常 | 自定义中间件、全局异常处理器、`HTTPException` | 统一错误响应格式 |
| 后台任务 | `BackgroundTasks`、Celery/`arq` 异步任务队列 | 能处理邮件发送、耗时计算 |
| 缓存 | `Redis` + `aioredis`/`redis-py`、缓存策略设计 | 热点数据缓存 |
| 测试 | `pytest` + `httpx.AsyncClient`、`TestClient`、fixtures、mock | 能写接口测试覆盖核心逻辑 |
| 日志与监控 | `loguru`/`structlog`、请求 ID 追踪、性能指标 | 有基本可观测性 |

### 推荐资源
- FastAPI 安全文档（Security）
- pytest 官方文档
- Celery / arq 文档

### 阶段产出
> 在第二阶段项目基础上：加入 JWT 认证（普通用户/管理员角色）、Redis 缓存、Celery 异步邮件任务、pytest 测试套件（覆盖率 >70%）。

---

## 第四阶段：AI 应用后端实战（第 4 周）

### 目标：掌握 LLM 集成、流式响应、RAG 知识库等 AI 后端核心技能

| 模块 | 内容 | 产出 |
|------|------|------|
| OpenAI API 集成 | `openai` SDK、对话补全、function calling | 能封装自己的 LLM 服务层 |
| 流式响应 | `StreamingResponse`、`async for` 流式输出、SSE | 实现 ChatGPT 式打字效果 |
| RAG 知识库 | 文档切分、Embedding 生成、向量数据库（pgvector / Chroma） | 能构建基于私有数据的问答系统 |
| 多轮对话管理 | 对话历史存储、上下文窗口管理 | 有状态的对话系统 |
| 异步任务处理 | 长任务（文档解析、批量 Embedding）丢入队列 | 大文件处理不阻塞接口 |
| 提示词工程 | 系统提示词模板、动态 Prompt 组装 | 可控的 AI 输出质量 |

### 推荐资源
- OpenAI API 官方文档
- LangChain / LlamaIndex 文档（选学，先理解底层再决定用不用框架）
- 《Building LLM Apps》相关章节

### 阶段产出
> **核心项目：AI 知识库问答系统**
> - 用户上传文档（PDF/Word/TXT）
> - 后台解析并切分 → Embedding → 存入 pgvector
> - 用户提问 → 检索相关片段 → 组装 Prompt → 流式返回答案
> - 支持多轮对话，对话历史持久化
> - 完整的 JWT 认证 + 用户隔离

---

## 第五阶段：部署、DevOps 与简历包装（第 5 周）

### 目标：项目上线 + 简历可写

| 模块 | 内容 | 产出 |
|------|------|------|
| Docker 容器化 | `Dockerfile` 多阶段构建、`docker-compose`（API + DB + Redis + Nginx） | 一键启动完整环境 |
| 反向代理 | Nginx / Traefik、HTTPS、域名配置 | 生产级访问入口 |
| 云部署 | 阿里云/腾讯云/Render/Railway 部署实践 | 项目可公网访问 |
| CI/CD | GitHub Actions 自动化测试 + 构建 + 部署 | 代码提交自动部署 |
| 文档与 API 文档 | 自动生成的 Swagger/OpenAPI、README 项目说明 | 可直接给面试官看的仓库 |
| 简历包装 | 项目描述 STAR 法则、技术亮点提炼、面试常见问题准备 | 能回答"你为什么用 FastAPI"等问题 |

### 推荐资源
- Docker 官方文档
- 目标云平台的部署文档
- GitHub Actions 文档

### 阶段产出
> - 项目部署到公网，有 HTTPS 域名
> - GitHub 仓库有完整 README + API 文档链接
> - 简历中新增"AI 知识库问答系统"项目项

---

## 学习强度分配建议（每周 20+ 小时）

```text
周一至周五：每天 3-4 小时
  - 1.5h 理论学习（文档/视频/书）
  - 1.5h 动手编码
  - 1h 复习/笔记整理/复盘

周末：每天 6-8 小时
  - 集中推进阶段产出项目
  - 补齐当周未完成的模块
```

---

## 关键里程碑检查点

| 周次 | 检查点 | 必须达到 |
|------|--------|---------|
| 第 1 周末 | CRUD Demo | 能用 Postman/curl 完整测试增删改查 |
| 第 2 周末 | 数据库 Demo | 数据持久化到 PostgreSQL，有迁移脚本 |
| 第 3 周末 | 认证 Demo | JWT 认证通过，测试覆盖核心接口 |
| 第 4 周末 | AI 项目 MVP | 能上传文档、提问、收到 AI 回答 |
| 第 5 周末 | 上线 + 简历 | 项目公网可访问，简历已更新 |

---

## 备选扩展（有余力时）

- **WebSocket 实时通信**：AI 对话中的实时推送场景
- **GraphQL**：`strawberry-graphql` 与 FastAPI 集成
- **微服务架构**：拆分用户服务 / AI 服务 / 文件服务
- **监控告警**：Prometheus + Grafana 监控 API 性能
- **限流与熔断**：`slowapi` 限流、容错设计