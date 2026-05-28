# Docker 笔记:测开面试核心增强版

> 学习日期:2025-05-23`r`n> 优化日期:2026-05-28`r`n> 主题:Docker 核心概念 + 镜像构建 + 网络存储 + 测开常用场景 + 实战排障`r`n> 适用:测试开发工程师面试、接口自动化、集成测试、CI/CD 与环境排查

---

## 目录

- [一、核心概念](#一核心概念)
- [二、核心命令](#二核心命令)
- [三、Dockerfile](#三dockerfile)
- [四、docker-compose](#四docker-compose)
- [五、测开常用场景](#五测开常用场景)
- [六、Docker 架构与镜像分层](#六docker-架构与镜像分层)
- [七、Dockerfile 进阶与最佳实践](#七dockerfile-进阶与最佳实践)
- [八、Docker 网络与容器间通信](#八docker-网络与容器间通信)
- [九、Volume / Bind Mount / tmpfs](#九volume--bind-mount--tmpfs)
- [十、健康检查、资源限制与退出码](#十健康检查资源限制与退出码)
- [十一、docker compose 进阶](#十一docker-compose-进阶)
- [十二、常见故障排查手册](#十二常见故障排查手册)
- [十三、Testcontainers 与 pytest 集成](#十三testcontainers-与-pytest-集成)
- [十四、镜像仓库与安全实践](#十四镜像仓库与安全实践)
- [十五、实战命令增强](#十五实战命令增强)
- [十六、面试问答模板](#十六面试问答模板)
- [十七、命令速查表](#十七命令速查表)
---

## 一、核心概念

### 1.1 Docker 是什么

> **把代码 + 运行环境打包成一个"集装箱"(容器),在任何有 Docker 的机器上都能跑,环境完全一致。**

解决的核心问题:"在我电脑上能跑,在你电脑上跑不了"。

### 1.2 三个核心概念

| 概念 | 类比 | 特点 |
|---|---|---|
| **镜像(Image)** | 饺子模具 | 只读模板,可以创建容器 |
| **容器(Container)** | 做出来的饺子 | 镜像运行起来的实例 |
| **Dockerfile** | 制作模具的菜谱 | 描述如何构建镜像 |

```
Dockerfile → docker build → 镜像 → docker run → 容器
 (菜谱)        (制作)       (模具)    (实例化)    (运行中的进程)
```

### 1.3 Docker vs 虚拟机

```
虚拟机:                          Docker 容器:
每个 VM 有独立 OS → 几 GB        共享宿主机 OS → 几十 MB
启动需要几分钟                   启动需要几秒
完整系统隔离                     进程+文件系统隔离
```

> **金句**:"虚拟机是完整 OS 隔离,Docker 容器共享宿主机 OS 内核,只隔离进程。更轻量、更快。测试环境首选 Docker。"

### 1.4 端口映射

```
宿主机(你的电脑)              容器内部
     :3306  ←─────────────────→  :3306 (MySQL 监听)
     :8080  ←─────────────────→  :80   (Nginx 监听)

-p 宿主机端口:容器端口
-p 3306:3306   宿主机 3306 → 容器 3306
-p 8080:80     宿主机 8080 → 容器 80
```

---

## 二、核心命令

### 2.1 镜像操作

```bash
# 拉取镜像
docker pull mysql:8.0
docker pull python:3.11

# 查看本地镜像
docker images

# 删除镜像
docker rmi mysql:8.0

# 构建镜像
docker build -t my-app:1.0 .
# -t = 打标签(名字:版本)  . = Dockerfile 在当前目录
```

### 2.2 容器操作

```bash
# ⭐ 启动容器(完整参数版)
docker run \
  -d \                              # 后台运行
  --name my-mysql \                 # 容器名字
  -p 3306:3306 \                    # 端口映射
  -e MYSQL_ROOT_PASSWORD=123456 \   # 环境变量
  -v /data/mysql:/var/lib/mysql \   # 数据卷挂载
  mysql:8.0

# 查看运行中的容器
docker ps

# 查看所有容器(含已停止)
docker ps -a

# 停止/启动/删除
docker stop my-mysql
docker start my-mysql
docker rm my-mysql

# 停止并删除(一步)
docker stop my-mysql && docker rm my-mysql

# ⭐ 进入容器内部(排查问题)
docker exec -it my-mysql bash
# -i 交互模式  -t 分配终端

# 查看日志
docker logs my-mysql
docker logs -f my-mysql    # 实时跟踪(类似 tail -f)

# 运行完自动删除(测试场景用)
docker run --rm my-test-framework:1.0
```

### 2.3 常用参数速记

| 参数 | 含义 |
|---|---|
| `-d` | 后台运行(detach) |
| `--name` | 给容器起名字 |
| `-p 宿主:容器` | 端口映射 |
| `-e KEY=VALUE` | 设置环境变量 |
| `-v 宿主路径:容器路径` | 数据卷挂载(持久化数据) |
| `--rm` | 容器停止后自动删除 |
| `-it` | 交互式终端(进入容器用) |

---

## 三、Dockerfile

### 3.1 常用指令

| 指令 | 用途 | 示例 |
|---|---|---|
| `FROM` | 基础镜像 | `FROM python:3.11-slim` |
| `WORKDIR` | 工作目录 | `WORKDIR /app` |
| `COPY` | 复制文件 | `COPY . .` |
| `RUN` | 构建时执行命令 | `RUN pip install -r requirements.txt` |
| `ENV` | 设置环境变量 | `ENV PORT=8080` |
| `EXPOSE` | 声明端口(文档用) | `EXPOSE 8080` |
| `CMD` | 容器启动时执行 | `CMD ["python", "app.py"]` |

### 3.2 测开框架的 Dockerfile 模板

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 先复制依赖文件(利用 Docker 缓存层,加速重复构建)
COPY requirements.txt .
RUN pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --no-cache-dir

# 再复制代码
COPY . .

# 运行测试
CMD ["pytest", "tests/", "-v", "--alluredir=./allure-results"]
```

**为什么先 COPY requirements.txt 再 COPY 代码?**

Docker 构建时每一层都有缓存。如果代码改了但依赖没变,**只会重新执行 `COPY . .` 之后的层,不会重新 pip install**——大幅加速构建。

### 3.3 构建和运行

```bash
# 构建
docker build -t my-test-framework:1.0 .

# 运行测试
docker run --rm my-test-framework:1.0

# 运行并挂载测试报告目录(这样宿主机能看到报告)
docker run --rm \
  -v $(pwd)/allure-results:/app/allure-results \
  my-test-framework:1.0
```

---

## 四、docker-compose

### 4.1 为什么需要 docker-compose

测试一个项目需要多个服务(MySQL + Redis + 应用),每个都 `docker run` 很麻烦。docker-compose 用一个 YAML 文件定义所有服务,一条命令启动。

### 4.2 核心命令

```bash
docker-compose up -d      # 后台启动所有服务
docker-compose ps         # 查看所有服务状态
docker-compose logs -f    # 查看所有服务日志
docker-compose down       # 停止并删除所有容器
docker-compose down -v    # 停止并删除容器 + 数据卷
```

### 4.3 测试环境 docker-compose.yml 模板

```yaml
version: "3.8"

services:
  # 数据库
  mysql:
    image: mysql:8.0
    container_name: test-mysql
    environment:
      MYSQL_ROOT_PASSWORD: "123456"
      MYSQL_DATABASE: "test_db"
      MYSQL_USER: "tester"
      MYSQL_PASSWORD: "test123"
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 3s
      retries: 10

  # 缓存
  redis:
    image: redis:7.0
    container_name: test-redis
    ports:
      - "6379:6379"

  # 应用服务
  app:
    build: .
    container_name: test-app
    ports:
      - "8080:8080"
    environment:
      DB_HOST: mysql          # 用服务名作为主机名
      DB_PORT: 3306
      DB_NAME: test_db
      REDIS_HOST: redis
    depends_on:
      mysql:
        condition: service_healthy    # 等 MySQL 健康检查通过再启动
```

---

## 五、测开常用场景

### 场景 1:一行命令起测试数据库

```bash
# 起一个干净的 MySQL
docker run -d \
  --name test-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=test_db \
  mysql:8.0

# 测试完销毁
docker stop test-mysql && docker rm test-mysql
```

**测开每天用**:测试前起干净环境,测试后销毁,完全不污染本机。

### 场景 2:pytest + Docker 测试数据库

```python
# conftest.py
import pytest
import subprocess
import time
import pymysql

@pytest.fixture(scope="session", autouse=True)
def docker_mysql():
    """测试会话开始时起 MySQL 容器,结束时销毁"""
    # 启动容器
    subprocess.run([
        "docker", "run", "-d",
        "--name", "pytest-mysql",
        "-p", "3307:3306",
        "-e", "MYSQL_ROOT_PASSWORD=123456",
        "-e", "MYSQL_DATABASE=test_db",
        "mysql:8.0"
    ], check=True)

    # 等待 MySQL 就绪
    time.sleep(15)

    yield    # 测试在这里运行

    # 销毁容器
    subprocess.run(["docker", "stop", "pytest-mysql"])
    subprocess.run(["docker", "rm", "pytest-mysql"])
```

### 场景 3:CI/CD 中的完整测试流程

```bash
#!/bin/bash
# ci_test.sh

set -e    # 任何命令失败立即退出

echo "=== 启动测试环境 ==="
docker-compose up -d

echo "=== 等待服务就绪 ==="
sleep 15

echo "=== 运行测试 ==="
docker-compose run --rm app pytest tests/ -v

echo "=== 清理环境 ==="
docker-compose down

echo "=== 测试完成 ==="
```

**`set -e`**:任何命令失败就立即退出脚本——CI 里必须加,否则测试失败了脚本还继续跑。

### 场景 4:进入容器排查问题

```bash
# 进入 MySQL 容器执行 SQL
docker exec -it test-mysql mysql -uroot -p123456

# 进入应用容器查看日志
docker exec -it test-app bash
tail -f /var/log/app/service.log

# 不进入容器,直接看日志
docker logs -f test-app
docker logs --tail 100 test-app    # 看最后 100 行
```

### 场景 5:数据卷——持久化测试数据

```bash
# 挂载数据卷,容器删了数据还在
docker run -d \
  --name test-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -v mysql-data:/var/lib/mysql \    # 命名数据卷
  mysql:8.0

# 查看数据卷
docker volume ls
docker volume rm mysql-data    # 删除数据卷
```

---

## 六、Docker 架构与镜像分层

### 6.1 Docker 架构

```text
用户输入 docker 命令
        ↓
Docker Client
        ↓
Docker Daemon(dockerd)
        ↓
管理镜像、容器、网络、数据卷
        ↓
从 Registry 拉取/推送镜像
```

| 组件 | 作用 |
|---|---|
| Docker Client | 接收 `docker` 命令 |
| Docker Daemon | 真正管理镜像、容器、网络、数据卷 |
| Docker Registry | 镜像仓库,如 Docker Hub、Harbor |
| Image | 只读模板 |
| Container | 镜像运行起来的实例 |

面试表达:

> 我们执行的 `docker` 命令是客户端,Docker Daemon 才是真正干活的进程。Daemon 负责创建容器、构建镜像、管理网络和数据卷,镜像可以从 Registry 拉取或推送。

### 6.2 镜像分层 Layer

Docker 镜像不是一个完整大文件,而是由多层只读 layer 叠加组成。

```text
python:3.11-slim 基础层
        ↓
安装依赖层 RUN pip install ...
        ↓
复制代码层 COPY . .
        ↓
启动命令层 CMD ...
```

特点:

- 每条 `RUN`、`COPY`、`ADD` 通常会生成新层。
- 相同 layer 可以被多个镜像复用。
- 构建时如果前面的层没变,可以直接使用缓存。
- 所以应该先复制依赖文件,再复制业务代码。

### 6.3 写时复制 Copy-on-Write

容器启动时不会复制一整份镜像,而是在只读镜像层上加一层可写层。

```text
只读镜像层:系统文件、依赖、代码
可写容器层:容器运行后产生的改动
```

如果容器修改文件,改动会写入容器自己的可写层,不会影响原镜像。

面试表达:

> Docker 轻量的原因之一是镜像分层和写时复制。多个容器可以共享同一份只读镜像层,每个容器只维护自己的可写层。

---

## 七、Dockerfile 进阶与最佳实践

### 7.1 ENTRYPOINT 和 CMD 的区别

```dockerfile
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8080"]
```

| 指令 | 作用 |
|---|---|
| `ENTRYPOINT` | 固定入口命令 |
| `CMD` | 默认启动命令或默认参数 |

理解:

```text
ENTRYPOINT 更像“固定执行谁”
CMD 更像“默认参数是什么”
```

运行时:

```bash
docker run my-app:1.0 --port 9090
```

这里 `--port 9090` 会覆盖默认 CMD 参数。

### 7.2 ARG 和 ENV

```dockerfile
ARG APP_VERSION=dev
ENV ENVIRONMENT=test
```

| 指令 | 作用 | 生命周期 |
|---|---|---|
| `ARG` | 构建时变量 | 只在 build 阶段有效 |
| `ENV` | 环境变量 | 镜像和容器运行时都存在 |

构建时传参:

```bash
docker build --build-arg APP_VERSION=1.0 -t my-app:1.0 .
```

### 7.3 USER:不要总用 root 运行

```dockerfile
RUN useradd -m appuser
USER appuser
```

原因:

- 降低容器逃逸或误操作风险。
- 避免容器内进程以 root 权限运行。
- 更接近生产安全要求。

### 7.4 HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

查看健康状态:

```bash
docker ps
```

### 7.5 .dockerignore

`.dockerignore` 用来排除不需要复制进镜像的文件。

```text
.git
__pycache__
.pytest_cache
node_modules
allure-results
.env
*.log
```

好处:

- 减少构建上下文大小。
- 加快构建速度。
- 避免把敏感文件打进镜像。

### 7.6 多阶段构建

适合前端、Go、Java 等需要构建产物的项目。

```dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

优点:

- 构建阶段有完整工具链。
- 运行阶段只保留最终产物。
- 镜像更小,攻击面更少。

### 7.7 Dockerfile 最佳实践

- 使用明确版本,不要在生产使用 `latest`。
- 优先使用小镜像,如 `python:3.11-slim`。
- 先复制依赖文件,再复制代码,充分利用缓存。
- 不要把密码、Token 写进 Dockerfile。
- 使用 `.dockerignore` 排除无关文件。
- 尽量用非 root 用户运行。
- 一个容器只跑一个主进程。
- 构建后可做镜像漏洞扫描。

---

## 八、Docker 网络与容器间通信

### 8.1 常见网络模式

| 网络模式 | 说明 |
|---|---|
| `bridge` | 默认模式,容器通过虚拟网桥通信 |
| `host` | 容器共享宿主机网络 |
| `none` | 容器无网络 |
| 自定义 bridge | 推荐用于多个容器互相访问 |

常用命令:

```bash
docker network ls
docker network inspect bridge
docker network create test-net
```

### 8.2 容器名通信

在同一个自定义网络中,容器可以用容器名互相访问。

```bash
# 创建网络
docker network create test-net

# 启动 MySQL
docker run -d \
  --name mysql \
  --network test-net \
  -e MYSQL_ROOT_PASSWORD=123456 \
  mysql:8.0

# 启动应用容器,应用里 DB_HOST=mysql
docker run --rm \
  --network test-net \
  -e DB_HOST=mysql \
  my-app:1.0
```

应用连接 MySQL:

```text
host=mysql
port=3306
```

这和 docker compose 里用服务名访问服务是同一个逻辑。

### 8.3 端口映射再理解

```bash
docker run -p 8080:80 nginx
```

含义:

```text
宿主机 8080 -> 容器 80
```

注意:

- 容器之间通信通常不需要 `-p`,走 Docker 网络即可。
- `-p` 是为了让宿主机或外部访问容器。

### 8.4 网络排查命令

```bash
# 查看容器 IP、网络、端口映射
docker inspect container_name

# 查看端口映射
docker port container_name

# 临时起一个 curl 容器测试网络
docker run --rm --network test-net curlimages/curl:latest http://app:8080/health
```

---

## 九、Volume / Bind Mount / tmpfs

### 9.1 三种挂载方式

| 类型 | 说明 | 适合场景 |
|---|---|---|
| volume | Docker 管理的数据卷 | MySQL、Redis 等持久化数据 |
| bind mount | 挂载宿主机指定路径 | 本地代码、配置文件、测试报告 |
| tmpfs | 挂载到内存 | 临时文件、敏感临时数据 |

### 9.2 volume

```bash
docker volume create mysql-data

docker run -d \
  --name mysql \
  -v mysql-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  mysql:8.0
```

查看和删除:

```bash
docker volume ls
docker volume inspect mysql-data
docker volume rm mysql-data
```

### 9.3 bind mount

```bash
# 把当前目录挂载到容器 /app
docker run --rm -v $(pwd):/app -w /app python:3.11 pytest tests/
```

适合:

- 本地代码调试。
- 挂载配置文件。
- 导出测试报告。

### 9.4 tmpfs

```bash
docker run --tmpfs /tmp my-app:1.0
```

特点:

- 数据存在内存里。
- 容器停止后数据消失。
- 适合临时数据。

---

## 十、健康检查、资源限制与退出码

### 10.1 HEALTHCHECK 与健康状态

Dockerfile:

```dockerfile
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

compose:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 10s
  timeout: 3s
  retries: 3
```

查看:

```bash
docker ps
docker inspect container_name
```

### 10.2 资源限制

```bash
# 限制内存和 CPU
docker run --memory=512m --cpus=1 my-app:1.0
```

查看资源使用:

```bash
docker stats
```

常见结论:

- 内存超过限制,容器可能被 OOM kill。
- CPU 超过限制通常会被限速。
- 压测时建议结合 `docker stats` 观察容器资源。

### 10.3 容器退出码

查看退出码:

```bash
docker ps -a
docker inspect container_name --format='{{.State.ExitCode}}'
```

常见退出码:

| 退出码 | 含义 |
|---|---|
| 0 | 正常退出 |
| 1 | 应用错误 |
| 125 | Docker 命令本身失败 |
| 126 | 命令不可执行 |
| 127 | 命令不存在 |
| 137 | SIGKILL,常见 OOM 或被强杀 |
| 143 | SIGTERM,优雅停止 |

### 10.4 stop 和 kill 区别

```bash
docker stop container_name
docker kill container_name
```

区别:

- `docker stop`:先发 SIGTERM,等待一段时间后再 SIGKILL。
- `docker kill`:直接强制杀死。

---

## 十一、docker compose 进阶

### 11.1 新旧命令区别

```bash
# 老版本
docker-compose up -d

# 新版本 Docker Compose v2
docker compose up -d
```

现在更推荐 `docker compose`。

### 11.2 常用字段

```yaml
services:
  app:
    build: .
    image: my-app:1.0
    container_name: test-app
    command: pytest tests/ -v
    working_dir: /app
    environment:
      ENV: test
    volumes:
      - .:/app
    ports:
      - "8080:8080"
    networks:
      - test-net
    restart: unless-stopped
    depends_on:
      mysql:
        condition: service_healthy

networks:
  test-net:
```

字段说明:

| 字段 | 作用 |
|---|---|
| `build` | 指定构建上下文 |
| `image` | 指定镜像名 |
| `command` | 覆盖容器默认命令 |
| `working_dir` | 容器工作目录 |
| `environment` | 环境变量 |
| `volumes` | 挂载目录或数据卷 |
| `ports` | 端口映射 |
| `networks` | 指定网络 |
| `restart` | 重启策略 |
| `depends_on` | 服务依赖 |

### 11.3 compose 常用排查命令

```bash
docker compose ps
docker compose logs -f app
docker compose exec app bash
docker compose run --rm app pytest tests/ -v
docker compose config
```

`docker compose config` 可以展开并校验 compose 配置。

---

## 十二、常见故障排查手册

### 12.1 容器启动后立刻退出

排查:

```bash
docker ps -a
docker logs container_name
docker inspect container_name --format='{{.State.ExitCode}}'
```

常见原因:

- 主进程执行完就退出。
- CMD/ENTRYPOINT 写错。
- 应用启动报错。
- 缺少环境变量或配置文件。

### 12.2 端口访问不通

排查:

```bash
docker ps
docker port container_name
docker logs container_name
```

检查点:

- 是否配置了 `-p 宿主端口:容器端口`。
- 应用是否监听 `0.0.0.0`,而不是只监听 `127.0.0.1`。
- 容器内服务是否真的启动。
- 宿主机端口是否被占用。

### 12.3 容器连不上 MySQL / Redis

检查点:

- 是否在同一个 Docker 网络。
- 是否使用服务名/容器名作为 host。
- 端口用的是容器端口,不是宿主机映射端口。
- 数据库是否健康就绪。

示例:

```bash
docker network inspect test-net
docker logs mysql
docker exec -it app bash
```

### 12.4 镜像构建失败

常见原因:

- Dockerfile 路径不对。
- 构建上下文太大。
- 依赖下载失败。
- `COPY` 的文件被 `.dockerignore` 排除了。
- 基础镜像拉取失败。

排查:

```bash
docker build --no-cache -t my-app:debug .
```

### 12.5 容器内没有 bash

很多精简镜像没有 bash,可以用 sh:

```bash
docker exec -it container_name sh
```

### 12.6 磁盘被 Docker 占满

查看占用:

```bash
docker system df
```

清理无用资源:

```bash
docker container prune
docker image prune
docker system prune
```

危险命令:

```bash
docker volume prune
```

`volume prune` 可能删除测试数据库数据,执行前必须确认。

---

## 十三、Testcontainers 与 pytest 集成

手动用 `subprocess` 起容器可以工作,但更推荐 Testcontainers 管理测试依赖。

### 13.1 MySQL 示例

```python
from testcontainers.mysql import MySqlContainer


def test_mysql_container():
    with MySqlContainer("mysql:8.0") as mysql:
        conn_url = mysql.get_connection_url()
        assert conn_url
```

### 13.2 Redis 示例

```python
from testcontainers.redis import RedisContainer


def test_redis_container():
    with RedisContainer("redis:7") as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)
        assert host
        assert port
```

### 13.3 优势

- 自动拉起依赖容器。
- 自动等待服务就绪。
- 测试结束自动清理。
- 更适合集成测试和 CI。
- 减少手写启动/清理脚本。

---

## 十四、镜像仓库与安全实践

### 14.1 镜像仓库

常见仓库:

- Docker Hub。
- 公司私有 Harbor。
- 云厂商镜像仓库。

常用命令:

```bash
# 登录仓库
docker login registry.example.com

# 打标签
docker tag my-app:1.0 registry.example.com/test/my-app:1.0

# 推送镜像
docker push registry.example.com/test/my-app:1.0

# 拉取镜像
docker pull registry.example.com/test/my-app:1.0
```

### 14.2 安全实践

- 不要把密码、Token、私钥写进镜像。
- 不要把 `.env`、证书、测试报告等无关文件打进镜像。
- 生产镜像不要使用 `latest`。
- 尽量使用官方镜像或可信基础镜像。
- 使用非 root 用户运行容器。
- 镜像发布前进行漏洞扫描。
- 删除不必要的构建工具和缓存。

---

## 十五、实战命令增强

### 15.1 inspect / stats / top / diff

```bash
# 查看容器详细信息
docker inspect container_name

# 查看 CPU/内存/网络/磁盘 IO
docker stats

# 查看容器内进程
docker top container_name

# 查看容器文件系统变化
docker diff container_name
```

### 15.2 日志增强

```bash
# 看最后 100 行
docker logs --tail 100 container_name

# 看最近 10 分钟日志
docker logs --since 10m container_name

# 实时跟踪最近 200 行
docker logs -f --tail 200 container_name
```

### 15.3 复制文件

```bash
# 从容器复制到宿主机
docker cp container_name:/app/report ./report

# 从宿主机复制到容器
docker cp ./config.yaml container_name:/app/config.yaml
```

### 15.4 清理命令

```bash
# 查看 Docker 占用空间
docker system df

# 清理停止的容器
docker container prune

# 清理悬空镜像
docker image prune

# 清理未使用网络
docker network prune

# 清理未使用数据卷,危险
docker volume prune

# 综合清理,谨慎
docker system prune
```

---

## 十六、面试问答模板

### Q1:"Docker 镜像和容器的关系?"

> "镜像是只读的模板,容器是镜像运行起来的实例。类比:镜像是饺子模具,容器是用模具做出来的饺子。一个镜像可以启动多个容器,每个容器相互独立。"

### Q2:"Docker 和虚拟机的区别?"

> "虚拟机每个 VM 有独立的 OS,几 GB 起步,启动几分钟。Docker 容器共享宿主机 OS 内核,只隔离进程和文件系统,几十 MB,秒级启动。测试环境用 Docker 更轻量更快。"

### Q3:"测开为什么用 Docker?"

> "三个核心价值:
>
> **环境一致性**——开发、测试、生产用同一个镜像,消灭'在我机器上能跑'的问题。
>
> **快速搭建测试环境**——一条命令起干净的 MySQL/Redis,测完销毁,不污染本机。
>
> **接入 CI/CD**——每次跑测试都是干净的容器环境,测试结果可靠可重复。"

### Q4:"docker-compose 是干什么的?"

> "docker-compose 用一个 YAML 文件定义多个服务(比如应用 + MySQL + Redis),用一条命令(`docker-compose up`)启动所有服务,并管理它们之间的依赖关系。测试环境管理的标配工具。"

### Q5:"Dockerfile 中 CMD 和 RUN 的区别?"

> "`RUN` 在**构建镜像时**执行,结果固化到镜像层里(比如安装依赖)。`CMD` 在**容器启动时**执行(比如启动应用)。一个 Dockerfile 可以有多个 `RUN`,但通常只有一个 `CMD`。"

### Q6:"Docker 为什么轻量?"

> "Docker 容器共享宿主机内核,不需要像虚拟机一样启动完整操作系统。同时 Docker 镜像是分层的,多个容器可以共享只读镜像层,每个容器只维护自己的可写层,这叫写时复制。"

### Q7:"CMD 和 ENTRYPOINT 的区别?"

> "ENTRYPOINT 更像固定入口命令,CMD 更像默认命令或默认参数。`docker run image xxx` 通常会覆盖 CMD,但不会直接替换 ENTRYPOINT。常见写法是 ENTRYPOINT 指定程序,CMD 提供默认参数。"

### Q8:"Docker 容器之间怎么通信?"

> "推荐创建自定义 bridge 网络,把容器加入同一个网络。这样容器之间可以用容器名或 compose 服务名访问,比如应用连接 MySQL 时 host 写 `mysql`,port 写容器端口 `3306`。"

### Q9:"volume 和 bind mount 有什么区别?"

> "volume 由 Docker 管理,适合数据库等持久化数据。bind mount 是把宿主机指定路径挂进容器,适合本地代码、配置文件和测试报告。tmpfs 则存内存里,容器停止后数据消失。"

### Q10:"容器启动后立刻退出怎么排查?"

> "先 `docker ps -a` 看状态和退出码,再 `docker logs` 看应用报错,必要时 `docker inspect` 看启动命令和环境变量。常见原因是主进程执行完、CMD 写错、配置缺失或应用启动失败。"

### Q11:"Docker 端口访问不通怎么排查?"

> "先看 `docker ps` 是否有端口映射,再用 `docker port` 确认宿主端口到容器端口的映射。然后看应用是否监听容器内正确端口,并确认监听地址是 `0.0.0.0` 而不是只监听 `127.0.0.1`。"

### Q12:"Dockerfile 怎么优化镜像大小?"

> "使用更小的基础镜像,用 `.dockerignore` 排除无关文件,合并清理缓存,固定依赖版本,对需要构建产物的项目使用多阶段构建,运行阶段只保留最终产物。"
---

## 十七、命令速查表

### 镜像

| 命令 | 用途 |
|---|---|
| `docker pull 镜像:版本` | 拉取镜像 |
| `docker images` | 查看本地镜像 |
| `docker rmi 镜像` | 删除镜像 |
| `docker build -t 名字:版本 .` | 构建镜像 |

### 容器

| 命令 | 用途 |
|---|---|
| `docker run -d --name 名字 -p 宿主:容器 镜像` | 启动容器 |
| `docker ps` | 查看运行中的容器 |
| `docker ps -a` | 查看所有容器 |
| `docker stop 容器` | 停止容器 |
| `docker rm 容器` | 删除容器 |
| `docker exec -it 容器 bash` | 进入容器 |
| `docker logs -f 容器` | 实时查看日志 |

### docker-compose

| 命令 | 用途 |
|---|---|
| `docker-compose up -d` | 后台启动所有服务 |
| `docker-compose ps` | 查看服务状态 |
| `docker-compose logs -f` | 查看所有服务日志 |
| `docker-compose down` | 停止并删除容器 |
| `docker-compose down -v` | 停止并删除容器+数据卷 |

### 网络

| 命令 | 用途 |
|---|---|
| `docker network ls` | 查看网络 |
| `docker network create test-net` | 创建自定义网络 |
| `docker network inspect test-net` | 查看网络详情 |
| `docker run --network test-net ...` | 容器加入指定网络 |
| `docker port 容器` | 查看端口映射 |

### 数据卷和挂载

| 命令 | 用途 |
|---|---|
| `docker volume ls` | 查看数据卷 |
| `docker volume inspect 卷名` | 查看数据卷详情 |
| `docker volume rm 卷名` | 删除数据卷 |
| `docker run -v 卷名:/path 镜像` | 使用命名 volume |
| `docker run -v $(pwd):/app 镜像` | 使用 bind mount |
| `docker run --tmpfs /tmp 镜像` | 使用 tmpfs |

### 排障

| 命令 | 用途 |
|---|---|
| `docker inspect 容器` | 查看容器详细信息 |
| `docker stats` | 查看资源使用 |
| `docker top 容器` | 查看容器进程 |
| `docker diff 容器` | 查看容器文件变化 |
| `docker logs --tail 100 容器` | 查看最后 100 行日志 |
| `docker logs --since 10m 容器` | 查看最近 10 分钟日志 |
| `docker inspect 容器 --format='{{.State.ExitCode}}'` | 查看退出码 |
| `docker cp 容器:/path ./local` | 从容器复制文件 |

### 清理

| 命令 | 用途 |
|---|---|
| `docker system df` | 查看 Docker 空间占用 |
| `docker container prune` | 清理停止容器 |
| `docker image prune` | 清理悬空镜像 |
| `docker network prune` | 清理未使用网络 |
| `docker volume prune` | 清理未使用数据卷,危险 |
| `docker system prune` | 综合清理,谨慎 |

### 镜像仓库

| 命令 | 用途 |
|---|---|
| `docker login registry` | 登录镜像仓库 |
| `docker tag app:1.0 registry/app:1.0` | 打远程仓库标签 |
| `docker push registry/app:1.0` | 推送镜像 |
| `docker pull registry/app:1.0` | 拉取镜像 |
---

## 学习建议

如果用于测开面试和实战,建议按下面顺序掌握:

1. 镜像、容器、Dockerfile、Registry 的关系。
2. docker run、logs、exec、ps、inspect、stats。
3. Dockerfile 缓存、CMD/ENTRYPOINT、多阶段构建、.dockerignore。
4. Docker 网络、容器名通信、端口映射。
5. volume、bind mount、测试报告和数据库数据持久化。
6. compose 编排 MySQL、Redis、应用和测试服务。
7. 容器退出码、OOM、端口不通、构建失败等排障模型。
8. CI/CD 中用容器跑自动化测试,复杂场景可用 Testcontainers。

一句话总结:

> Docker 对测开的核心价值是让测试环境可复制、可销毁、可自动化。面试不要只背命令,要能讲清楚镜像怎么构建、容器怎么通信、数据怎么持久化、服务起不来怎么排查。

---

*Docker:测开面试核心增强版 —— 完结。*

