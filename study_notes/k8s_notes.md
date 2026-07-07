# K8s 笔记:测开面试核心

> 学习日期:2025-05-23
> 主题:K8s 核心概念 + 测开常用场景

---

## 目录

- [一、K8s 是什么](#一k8s-是什么)
- [二、六大核心概念](#二六大核心概念)
- [三、kubectl 常用命令](#三kubectl-常用命令)
- [四、测开常用场景](#四测开常用场景)
- [五、面试问答模板](#五面试问答模板)
- [六、命令速查表](#六命令速查表)

---

## 一、K8s 是什么

### 1.1 解决什么问题

Docker 解决了单台机器上的容器管理。但生产环境需要跨多台服务器：

```
问题 1:某台服务器挂了,容器怎么办?       → 自动故障恢复
问题 2:流量突然增加,需要更多实例?        → 自动扩缩容
问题 3:新版本发布,怎么不停服更新?        → 滚动更新
问题 4:几百个容器怎么统一管理?           → 统一编排
```

> **K8s 一句话**:K8s 是容器编排系统,让你用 YAML 文件管理成百上千个容器,实现自动部署、自动扩缩容、自动故障恢复。

### 1.2 K8s vs Docker 的关系

```
Docker = 造集装箱(单台机器的容器管理)
K8s    = 调度集装箱船队(跨多台机器的容器编排)
```

K8s 本身不造容器——它调度 Docker 镜像构建的容器。

---

## 二、六大核心概念

### 用奶茶连锁集团理解

```
K8s 集群 = 整个奶茶连锁集团
Node     = 每家分店(一台服务器)
Pod      = 一组员工(运行容器的最小单位)
Deployment = 加盟合同(声明要开几家店、怎么开)
Service  = 总客服电话(统一访问入口)
Namespace = 不同品牌线(隔离不同团队/环境)
```

### 2.1 Node(节点)= 一台服务器

```
K8s 集群:
┌─────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Node 1   │  │ Node 2   │  │Node 3  ││
│  │(服务器1) │  │(服务器2) │  │(服务器3)││
│  └──────────┘  └──────────┘  └────────┘│
└─────────────────────────────────────────┘
```

### 2.2 Pod = K8s 最小调度单位

- Pod 是 K8s 最小的部署/调度单位
- 一个 Pod 里可以有一个或多个容器
- **大部分情况:一个 Pod = 一个容器**
- 同一 Pod 里的容器**共享网络和存储**

```
┌─────────────────────┐
│       Pod           │
│  ┌───────────────┐  │
│  │  主应用容器   │  │
│  └───────────────┘  │
│  ┌───────────────┐  │ ← 共享同一个 IP
│  │  日志收集容器 │  │
│  └───────────────┘  │
└─────────────────────┘
```

### 2.3 Deployment = 声明式 Pod 管理

你不直接创建 Pod,而是创建 Deployment——告诉 K8s"我要几个 Pod,用什么镜像"。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3          # 要 3 个副本
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

**K8s 的核心哲学**:

> 你不说"在第 2 台服务器起容器",你说"我要 3 个副本"。K8s 自己决定在哪起,出问题自己重启。**声明式管理,而不是命令式管理**。

### 2.4 Service = 统一访问入口

Pod 重启后 IP 会变,Service 提供**固定的访问入口**:

```
外部请求                              Pod 1
    ↓                               ↗
Service(固定DNS) → 负载均衡 →    Pod 2
                               ↘
                                 Pod 3
```

### 2.5 Namespace = 环境隔离

```bash
# 不同团队/环境用 Namespace 隔离
namespace: dev        # 开发环境
namespace: staging    # 预发布环境
namespace: prod       # 生产环境
namespace: test       # 测试环境 ← 测开常用
```

### 2.6 ConfigMap + Secret = 配置管理

```yaml
# ConfigMap:非敏感配置
kind: ConfigMap
data:
  DB_HOST: "mysql-service"
  LOG_LEVEL: "INFO"

# Secret:敏感配置(密码/Token,base64 编码)
kind: Secret
data:
  DB_PASSWORD: MTIzNDU2
```

---

## 三、kubectl 常用命令

### 3.1 查看资源

```bash
# 查看 Pod
kubectl get pods
kubectl get pods -n test          # 指定 namespace
kubectl get pods -A               # 所有 namespace

# 查看详情(排查问题第一步)
kubectl describe pod my-pod-xxx

# 查看 Deployment/Service
kubectl get deployments
kubectl get services
```

### 3.2 日志(测开最常用)

```bash
# 查看日志
kubectl logs my-pod-xxx

# 实时跟踪(类似 tail -f)
kubectl logs -f my-pod-xxx

# 指定 namespace
kubectl logs -f my-pod-xxx -n test

# ⭐ 查看上次崩溃的日志(排查 CrashLoopBackOff 必用)
kubectl logs my-pod-xxx --previous
```

### 3.3 进入容器

```bash
# 进入容器内部
kubectl exec -it my-pod-xxx -- bash

# 指定 namespace
kubectl exec -it my-pod-xxx -n test -- bash

# 直接执行命令(不进入交互模式)
kubectl exec my-pod-xxx -- ls /app
```

### 3.4 部署操作

```bash
# 创建/更新资源
kubectl apply -f deployment.yaml

# 删除资源
kubectl delete -f deployment.yaml
kubectl delete pod my-pod-xxx

# 扩缩容
kubectl scale deployment nginx-deployment --replicas=5

# 查看滚动更新状态
kubectl rollout status deployment/nginx-deployment

# 回滚到上一个版本
kubectl rollout undo deployment/nginx-deployment
```

---

## 四、测开常用场景

### 场景 1:Pod 常见状态与排查

| 状态 | 含义 | 排查方向 |
|---|---|---|
| `Running` | 正常运行 | — |
| `Pending` | 等待调度 | 资源不足/镜像拉取中 |
| `CrashLoopBackOff` | 反复崩溃重启 | `logs --previous` 看报错 |
| `ImagePullBackOff` | 镜像拉取失败 | 检查镜像名/仓库权限 |
| `OOMKilled` | 内存不足被杀 | 增加内存限制 |
| `Terminating` | 正在删除 | 正常,等待即可 |

**`CrashLoopBackOff` 排查流程**:

```bash
# 1. 看当前日志
kubectl logs my-pod-xxx

# 2. 看上次崩溃的日志
kubectl logs my-pod-xxx --previous

# 3. 看 Pod 事件
kubectl describe pod my-pod-xxx
# 看最下面的 Events 部分
```

### 场景 2:在测试 Namespace 跑自动化测试

```yaml
# test-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: api-test-job
  namespace: test
spec:
  template:
    spec:
      containers:
      - name: pytest
        image: my-test-framework:1.0
        env:
        - name: BASE_URL
          value: "http://app-service:8080"
      restartPolicy: Never
```

```bash
# 提交测试 Job
kubectl apply -f test-job.yaml -n test

# 查看测试进度
kubectl get pods -n test
kubectl logs -f api-test-job-xxx -n test

# 测试完清理
kubectl delete job api-test-job -n test
```

### 场景 3:排查测试环境服务问题

```bash
# 1. 看所有 Pod 状态
kubectl get pods -n test

# 2. 发现 Pod 异常,看详情
kubectl describe pod my-app-xxx -n test

# 3. 看日志
kubectl logs my-app-xxx -n test --previous

# 4. 进容器排查
kubectl exec -it my-app-xxx -n test -- bash
```

---

## 五、面试问答模板

### Q1:"K8s 和 Docker 的关系?"

> "Docker 负责单台机器的容器管理,K8s 负责跨多台机器的容器编排。Docker 是'造集装箱',K8s 是'调度集装箱船队'。K8s 使用 Docker 镜像,但不止于 Docker——它管理这些容器的调度、扩缩容和故障恢复。"

### Q2:"Pod 和容器的区别?"

> "Pod 是 K8s 的最小调度单位,一个 Pod 里可以有一个或多个容器。同一 Pod 里的容器共享网络和存储。大部分情况一个 Pod 只有一个容器,多容器 Pod 适合'主应用 + 辅助进程'的场景。"

### Q3:"Deployment 和 Pod 的区别?"

> "Pod 是运行中的实例,Deployment 是对 Pod 的声明式管理。你告诉 K8s'我要 3 个 Pod',Deployment 保证集群里始终有 3 个 Pod 在跑——某个挂了就自动重建。你不直接操作 Pod,而是操作 Deployment。"

### Q4:"K8s 的 Service 是干什么的?"

> "Pod 重启后 IP 会变,Service 提供固定的访问入口。外部请求打到 Service,Service 做负载均衡分发给后端多个 Pod。相当于一个稳定的'门牌号',不管后面的 Pod 怎么变,入口地址不变。"

### Q5:"测开怎么用 K8s?"

> "主要三个场景:
>
> 第一,在测试 Namespace 隔离测试环境——不影响开发和生产。
>
> 第二,用 K8s Job 跑自动化测试——提交一个测试 Job,K8s 分配资源跑完销毁,测试报告通过日志或挂载卷收集。
>
> 第三,排查测试环境问题——`kubectl get pods` 看状态,`kubectl logs --previous` 看崩溃日志,`kubectl exec` 进容器排查。"

---

## 六、命令速查表

| 命令 | 用途 |
|---|---|
| `kubectl get pods -n <ns>` | 查看 Pod 列表 |
| `kubectl describe pod <pod>` | 查看 Pod 详情和事件 |
| `kubectl logs -f <pod>` | 实时查看日志 |
| `kubectl logs <pod> --previous` | 查看上次崩溃日志 |
| `kubectl exec -it <pod> -- bash` | 进入容器 |
| `kubectl apply -f file.yaml` | 创建/更新资源 |
| `kubectl delete -f file.yaml` | 删除资源 |
| `kubectl scale deploy <name> --replicas=N` | 扩缩容 |
| `kubectl rollout undo deploy/<name>` | 回滚版本 |
| `kubectl get pods -A` | 查看所有 namespace 的 Pod |

---

*K8s:测开面试核心概念 + 常用命令 —— 完结。*
