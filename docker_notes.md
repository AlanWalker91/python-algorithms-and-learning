# Docker 笔记:测开面试核心

> 学习日期:2025-05-23
> 主题:Docker 核心概念 + 测开常用场景
> 适用:测试开发工程师面试 & 实战

---

## 目录

- [一、核心概念](#一核心概念)
- [二、核心命令](#二核心命令)
- [三、Dockerfile](#三dockerfile)
- [四、docker-compose](#四docker-compose)
- [五、测开常用场景](#五测开常用场景)
- [六、面试问答模板](#六面试问答模板)
- [七、命令速查表](#七命令速查表)

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

## 六、面试问答模板

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

---

## 七、命令速查表

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

---

*Docker:测开面试核心概念 + 5 大常用场景 —— 完结。*
