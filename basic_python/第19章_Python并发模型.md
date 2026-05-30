# 第19章：Python 并发模型

> **核心思想**：并发指同时处理多件事（结构问题），并行指同时做多件事（执行问题）。Python 原生提供三种并发方式：线程（threading）、进程（multiprocessing）、协程（asyncio）。理解它们各自的适用场景和局限，是写出高性能 Python 程序的关键。

---

## 目录

1. [知识框架总览](#1-知识框架总览)
2. [核心术语定义](#2-核心术语定义)
3. [GIL 详解：10条关键认知](#3-gil-详解10条关键认知)
4. [三种并发模型的实战对比：旋转指针示例](#4-三种并发模型的实战对比旋转指针示例)
5. [GIL 真正的影响：CPU密集型 vs I/O密集型](#5-gil-真正的影响cpu密集型-vs-io密集型)
6. [自建进程池：多进程素数检测](#6-自建进程池多进程素数检测)
7. [多核世界中的 Python](#7-多核世界中的-python)
8. [三种模型对比速查](#8-三种模型对比速查)
9. [常见误区与陷阱](#9-常见误区与陷阱)

---

## 1. 知识框架总览

```
第19章 Python 并发模型
│
├── 核心概念体系
│   ├── 并发 vs 并行（同时处理 vs 同时执行）
│   ├── 执行单元：进程 / 线程 / 协程
│   ├── 同步原语：队列 / 锁 / 信号量 / Event
│   └── 争用：资源争用 / CPU争用
│
├── GIL（全局解释器锁）
│   ├── 作用：保护解释器内部状态
│   ├── 释放时机：I/O操作、time.sleep()、C扩展
│   ├── 影响：CPU密集型多线程无法真正并行
│   └── 绕过：多进程（ProcessPoolExecutor）
│
├── 三种并发方式对比
│   ├── 线程（threading）
│   │   ├── 适合：I/O 密集型
│   │   ├── 同步：threading.Event / Lock
│   │   └── 调度：抢占式（OS负责，每5ms切换）
│   ├── 进程（multiprocessing）
│   │   ├── 适合：CPU 密集型
│   │   ├── 通信：队列 / 管道（需序列化）
│   │   └── 隔离：独立内存空间
│   └── 协程（asyncio）
│       ├── 适合：I/O 密集型（高并发低开销）
│       ├── 调度：协作式（显式 yield/await）
│       └── ⚠️ 不能有阻塞代码，否则冻结事件循环
│
├── 自建进程池（生产者-消费者模式）
│   ├── SimpleQueue / 毒药丸模式
│   └── → 更好方案：concurrent.futures（第20章）
│
└── 多核世界中的 Python
    ├── 系统管理：线程/协程即可
    ├── 数据科学：NumPy/PyTorch 释放GIL
    ├── WSGI 应用服务器：多进程（Gunicorn等）
    └── 分布式任务队列：Celery / RQ
```

---

## 2. 核心术语定义

### 2.1 并发 vs 并行

```
并发（Concurrency）：同时处理多件事（结构上的概念）
  → 单核CPU可以并发（时间片轮转）
  → 关注的是"如何组织多个任务"

并行（Parallelism）：同时执行多件事（执行上的概念）
  → 需要多核CPU / 多GPU / 集群
  → 关注的是"真正同时运行"

关系：并行是并发的特例。所有并行系统都是并发的，反之不成立。
```

### 2.2 执行单元（Python 原生支持三种）

| 执行单元 | 内存 | 通信方式 | 调度方式 | 启动开销 |
|---------|------|---------|---------|---------|
| **进程** | 独立内存空间 | 管道/队列/内存映射（需序列化）| 抢占式（OS）| 高 |
| **线程** | 共享进程内存 | 直接共享对象（需加锁）| 抢占式（OS）| 中 |
| **协程** | 共享线程内存 | 直接共享（单线程，无竞争）| 协作式（显式yield）| 极低 |

### 2.3 同步原语

```python
# ---- 队列（Queue）：执行单元间传递数据的标准方式 ----
# threading.Queue / multiprocessing.SimpleQueue / asyncio.Queue
# 特点：线程安全，支持 FIFO / LIFO / 优先级队列

# ---- 锁（Lock）：保护共享数据，防止数据竞争 ----
import threading
lock = threading.Lock()
with lock:                    # 持有锁期间，其他线程等待
    shared_data.update(...)   # 修改共享状态

# ---- 事件（Event）：线程间信号通知 ----
done = threading.Event()
done.set()                    # 发送信号（设为True）
done.wait(timeout=0.1)        # 等待信号，超时返回False

# ---- 信号量（Semaphore）：限制并发数量 ----
# 计数器：acquire()减1，release()加1，为0时阻塞
# asyncio.Semaphore(n) 限制最多n个协程同时活跃
```

### 2.4 争用（Contention）

```
资源争用：多个执行单元同时竞争同一把锁 / 同一个队列
CPU 争用：多个线程/进程竞争CPU时间片
GIL 争用：多个Python线程竞争全局解释器锁
```

---

## 3. GIL 详解：10条关键认知

> **⚠️ 重点**：GIL（Global Interpreter Lock，全局解释器锁）是Python并发的核心约束，必须深刻理解。

```
01. Python解释器每个实例是一个进程。
    → 用 multiprocessing 或 concurrent.futures 启动额外进程。

02. 解释器默认只用一个线程运行用户代码。
    → 用 threading 或 concurrent.futures 启动额外线程。

03. GIL 是一把锁，任意时刻只有一个线程能持有它。
    → 即使有多个CPU核，同时只有一个Python线程在执行。

04. 解释器每5毫秒自动释放GIL，让其他线程竞争。
    → 可用 sys.setswitchinterval(s) 调整这个间隔。

05. Python代码无法直接控制GIL。
    → 只有C扩展（NumPy等）可以在运行时主动释放GIL。

06. 标准库中所有发起系统调用的函数均会释放GIL。
    → 包括：磁盘I/O、网络I/O、time.sleep()
    → NumPy/SciPy的CPU密集函数、zlib/bz2压缩函数也释放GIL。

07. C扩展可以启动不受GIL影响的非Python线程。
    → 这些线程可以读写 bytearray / array.array / NumPy数组。

08. GIL对网络I/O的影响相对较小。
    → 因为I/O期间GIL已释放，线程等待期间让出控制权。

09. GIL会降低CPU密集型Python线程的速度。
    → 多线程CPU密集任务，性能甚至不如单线程（有线程切换开销）。

10. 要在多核上运行CPU密集型代码，必须使用多进程。
    → 每个Python进程有自己的GIL，互不影响。
```

**GIL 释放时机总结**：

```python
import time, threading

def cpu_bound():
    # GIL 全程持有，其他线程无法运行Python代码
    result = sum(range(10_000_000))

def io_bound():
    time.sleep(3)  # ← GIL 在这里释放！其他线程可以运行

def network_io():
    import urllib.request
    urllib.request.urlopen('https://example.com')  # ← 等待网络时释放GIL
```

---

## 4. 三种并发模型的实战对比：旋转指针示例

> 同一个任务（显示旋转动画 + 等待慢操作），用三种方式实现，对比差异。

### 4.1 线程版（threading）

```python
import itertools
import time
from threading import Thread, Event


def spin(msg: str, done: Event) -> None:
    """在单独线程中运行的动画函数。

    done: threading.Event 实例，用于线程间通信（发送停止信号）。
    """
    for char in itertools.cycle(r'\|/-'):       # 无限循环字符序列
        status = f'\r{char} {msg}'              # \r 把光标移到行头
        print(status, end='', flush=True)
        if done.wait(0.1):                      # 等待0.1秒；若事件被设置则立即返回True
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')              # 清空动画行


def slow() -> int:
    """模拟慢速操作（网络请求、数据库查询等）。

    关键：time.sleep() 会释放 GIL，让 spin 线程能继续运行。
    """
    time.sleep(3)
    return 42


def supervisor() -> int:
    done = Event()                              # 线程间通信的信号对象

    # 创建线程，target是要运行的函数，args是传递给target的参数
    spinner = Thread(target=spin, args=('thinking!', done))
    print(f'spinner object: {spinner}')         # 显示线程对象（初始状态）
    spinner.start()                             # ⬅️ 启动线程（spin开始运行）

    result = slow()                             # ⬅️ 主线程阻塞在这里，spin线程并发运行

    done.set()                                  # ⬅️ 发送停止信号（设 Event 为 True）
    spinner.join()                              # ⬅️ 等待 spin 线程结束
    return result


def main() -> None:
    result = supervisor()
    print(f'Answer: {result}')


if __name__ == '__main__':
    main()
```

### 4.2 进程版（multiprocessing）

```python
# spinner_proc.py：与线程版几乎相同，只是把 Thread 换成 Process
import itertools
import time
from multiprocessing import Process, Event
from multiprocessing import synchronize  # ← 类型提示需要额外导入


def spin(msg: str, done: synchronize.Event) -> None:
    # 与线程版的 spin 函数完全相同
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        if done.wait(0.1):
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')


def slow() -> int:
    time.sleep(3)
    return 42


def supervisor() -> int:
    done = Event()                              # multiprocessing.Event（底层用信号量实现）

    # Process API 与 Thread API 基本相同
    spinner = Process(target=spin, args=('thinking!', done))
    print(f'spinner object: {spinner}')         # 显示进程对象（含父进程ID）
    spinner.start()                             # 启动子进程（一个全新的Python解释器）

    result = slow()

    done.set()
    spinner.join()
    return result


# 关键区别：
# - 每个子进程有独立的GIL，可真正利用多核
# - 跨进程通信的对象需要序列化（pickle），有额外开销
# - Event 底层通过操作系统信号量（semaphore）实现
```

### 4.3 协程版（asyncio）⭐

```python
# spinner_async.py：使用协程实现，无需线程锁
import asyncio
import itertools


async def spin(msg: str) -> None:
    """协程动画函数。

    不需要 done Event，因为协程可以被 Task.cancel() 取消。
    """
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, flush=True, end='')
        try:
            await asyncio.sleep(0.1)            # ⬅️ 关键：暂停0.1秒，把控制权交还事件循环
        except asyncio.CancelledError:          # ⬅️ 收到取消信号时抛出
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')


async def slow() -> int:
    await asyncio.sleep(3)                      # ⬅️ 暂停3秒，让事件循环驱动其他协程
    # ⚠️ 绝对不能用 time.sleep(3)！那会阻塞整个事件循环，spin永远无法运行
    return 42


async def supervisor() -> int:
    # 三种驱动协程的方式：
    # 1. asyncio.create_task(coro())  → 调度运行，立即返回Task，不等待
    # 2. await coro()                  → 运行并等待，阻塞当前协程直到完成
    # 3. asyncio.run(coro())           → 在常规函数中启动事件循环（程序入口）

    spinner = asyncio.create_task(spin('thinking!'))    # 调度 spin，立即返回 Task
    print(f'spinner object: {spinner}')

    result = await slow()                               # 运行 slow 并等待，期间 spin 可以运行

    spinner.cancel()                                    # 发送取消信号（抛出 CancelledError）
    return result


def main() -> None:
    result = asyncio.run(supervisor())                  # 启动事件循环
    print(f'Answer: {result}')


if __name__ == '__main__':
    main()
```

### 4.4 三版 supervisor 对比

| 对比项 | 线程版 | 协程版 |
|--------|--------|--------|
| 创建并发单元 | `Thread(target=spin, args=(...))` | `asyncio.create_task(spin(...))` |
| 启动 | `spinner.start()` | 自动调度 |
| 停止信号 | `done.set()`（Event）| `spinner.cancel()`（Task方法）|
| 等待结束 | `spinner.join()` | 自动处理 |
| 慢操作 | `slow()`（阻塞当前线程）| `await slow()`（让出控制权）|
| 安全性 | 需要显式同步（锁/Event）| 天然安全（任意时刻只有一个协程运行）|

> **⚠️ 最重要的认知**：asyncio 是单线程的。任何时刻只有一个协程在运行。
> 在协程中调用 `time.sleep()` 或 CPU密集型函数，会冻结整个事件循环！

```python
# ❌ 错误：协程中使用阻塞调用，冻结事件循环
async def slow():
    time.sleep(3)           # 阻塞主线程3秒，spin 完全无法运行
    return 42

# ✅ 正确：使用异步sleep，把控制权交还给事件循环
async def slow():
    await asyncio.sleep(3)  # 暂停3秒，事件循环驱动其他协程
    return 42

# ✅ 临时方案：CPU密集操作中定期让出控制权（不推荐，降低性能50%）
async def is_prime_async(n):
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0:
            return False
        if i % 100_000 == 1:
            await asyncio.sleep(0)  # 每10万次迭代让出一次控制权
    return True
```

---

## 5. GIL 真正的影响：CPU密集型 vs I/O密集型

### 5.1 素数检测实验（CPU密集型）

```python
import math


def is_prime(n: int) -> bool:
    """素数检测函数（CPU密集型，耗时约3.3秒）。"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    root = math.isqrt(n)
    for i in range(3, root + 1, 2):
        if n % i == 0:
            return False
    return True
```

**把旋转指针的 `slow()` 替换为 `is_prime(5_000_111_000_222_021)` 的结果**：

| 并发模型 | 旋转指针结果 | 原因 |
|---------|-------------|------|
| **multiprocessing版** | ✅ 正常旋转 | spin在子进程，主进程做素数检测，互不干扰 |
| **threading版** | ✅ 正常旋转 | Python每5ms中断线程，spin有机会运行（GIL切换）|
| **asyncio版** | ❌ 完全冻结 | is_prime阻塞事件循环，spin的协程无法调度 |

### 5.2 关键结论

```
CPU密集型任务的选择：
  ✅ multiprocessing / ProcessPoolExecutor → 真正并行，绕开GIL
  ⚠️ threading → 有GIL争用，性能比单线程还差（有上下文切换开销）
  ❌ asyncio → 完全不适合，冻结事件循环

I/O密集型任务的选择：
  ✅ asyncio → 高并发低开销，协程切换成本极低
  ✅ threading → 可行，I/O期间释放GIL，线程可以交错执行
  ⚠️ multiprocessing → 可行但浪费，进程启动成本高
```

---

## 6. 自建进程池：多进程素数检测

> 本节展示使用队列手动实现进程池，理解"生产者-消费者"模式。实际项目应使用更高级的 `concurrent.futures`（第20章）。

### 6.1 核心模式：职程 + 毒药丸

```python
import sys
from time import perf_counter
from typing import NamedTuple
from multiprocessing import Process, SimpleQueue, cpu_count
from multiprocessing import queues
from primes import is_prime, NUMBERS  # 待检测的数列


class PrimeResult(NamedTuple):
    """存储素数检测结果的具名元组。"""
    n: int          # 被检测的数
    prime: bool     # 是否为素数
    elapsed: float  # 检测用时


# 类型别名（增强可读性）
JobQueue = queues.SimpleQueue[int]
ResultQueue = queues.SimpleQueue[PrimeResult]


def check(n: int) -> PrimeResult:
    """检测单个数是否为素数，计时并返回结果。"""
    t0 = perf_counter()
    prime = is_prime(n)
    return PrimeResult(n, prime, perf_counter() - t0)


def worker(jobs: JobQueue, results: ResultQueue) -> None:
    """职程函数：从任务队列取数，检测，结果放入结果队列。

    使用 0 作为"毒药丸"（哨符），收到后退出循环。
    """
    while n := jobs.get():                      # 取出任务；0 为假值，退出循环
        results.put(check(n))                   # 执行检测，放入结果
    results.put(PrimeResult(0, False, 0.0))     # 发送结束信号给主进程


def start_jobs(procs: int, jobs: JobQueue, results: ResultQueue) -> None:
    """把所有待检测的数放入队列，然后启动指定数量的工作进程。"""
    for n in NUMBERS:
        jobs.put(n)                             # 放入待检测的数

    for _ in range(procs):
        proc = Process(target=worker, args=(jobs, results))
        proc.start()                            # 启动工作进程
        jobs.put(0)                             # 为每个进程发送一个"毒药丸"（终止信号）


def main() -> None:
    procs = cpu_count() if len(sys.argv) < 2 else int(sys.argv[1])
    print(f'Checking {len(NUMBERS)} numbers with {procs} processes:')

    t0 = perf_counter()
    jobs: JobQueue = SimpleQueue()
    results: ResultQueue = SimpleQueue()

    start_jobs(procs, jobs, results)

    # 收集结果，直到所有进程都发送了结束信号
    checked = procs_done = 0
    while procs_done < procs:
        n, prime, elapsed = results.get()
        if n == 0:
            procs_done += 1             # 收到结束信号
        else:
            checked += 1
            label = 'P' if prime else ' '
            print(f'{n:16} {label} {elapsed:9.6f}s')

    elapsed = perf_counter() - t0
    print(f'{checked} checks in {elapsed:.2f}s')


if __name__ == '__main__':
    main()
```

### 6.2 毒药丸模式说明

```python
# 哨符（毒药丸）的设计原则：
# 1. 每个工作进程对应一个毒药丸（worker取到后退出循环）
# 2. 毒药丸也要放入队列中传递，worker才能感知到停止信号
# 3. None 是常用哨符，但跨进程时 None 经pickle序列化后同一性不保证
#    更安全的方案是使用 0（整数）或专门定义的哨符类

# 进程数与性能关系（实验结论）：
# - 进程数 = CPU物理核数 时，性能最优
# - 进程数 > CPU核数 时，性能不再提升（CPU争用）
# - 超线程（Hyper-threading）报告的逻辑核数不等于物理核数
```

---

## 7. 多核世界中的 Python

> 尽管有 GIL，Python 在多核环境下依然能蓬勃发展，原因在于：

### 7.1 系统管理领域

- 主要是 I/O 操作（SSH、HTTP、数据库），线程/协程足够
- 工具：Ansible、Salt、Fabric
- 不受 GIL 限制

### 7.2 数据科学领域

- NumPy/SciPy/TensorFlow 等库用 C/Fortran 实现，计算时释放 GIL
- Dask：并行计算库，支持分布式集群
- GPU 加速：PyTorch / TensorFlow

### 7.3 WSGI 应用服务器（Web开发）

```
典型部署架构：

[客户端] → [HTTP服务器(Nginx)] → [WSGI应用服务器] → [Python应用进程×N]
                                   (Gunicorn/uWSGI)

关键：WSGI服务器自动为每个请求分配一个Python进程/线程
用户无需了解threading/multiprocessing，并发由框架处理。

主流 WSGI 服务器：
- Gunicorn：简单易用，推荐首选
- uWSGI：功能丰富，配置复杂
- mod_wsgi：Apache专用
- NGINX Unit：多语言支持

ASGI（异步版WSGI）：
- 支持 async/await，适合 WebSocket 和长连接
- 框架：FastAPI、aiohttp、Sanic
- 服务器：uvicorn、hypercorn
```

### 7.4 分布式任务队列

```python
# 适用场景：
# - 发送邮件/短信
# - 生成PDF/报表
# - 图片/视频处理
# - 定时任务

# 主流工具：
# - Celery：功能最丰富，支持Redis/RabbitMQ
# - RQ（Redis Queue）：简单轻量

# 生产者-消费者模式：
# [Web进程(生产者)] → [消息队列(Redis)] → [Worker进程(消费者)]
#
# 优点：
# - 解耦：生产者和消费者独立运行
# - 弹性：可动态增减Worker数量
# - 可靠：任务持久化，不怕进程崩溃
```

---

## 8. 三种模型对比速查

### 8.1 核心特征对比

| | threading | multiprocessing | asyncio |
|--|-----------|-----------------|---------|
| **调度方式** | 抢占式（OS负责）| 抢占式（OS负责）| 协作式（程序控制）|
| **内存** | 共享（需加锁）| 独立（需序列化）| 共享（单线程安全）|
| **GIL影响** | 受限（CPU密集型无效）| 不受限（每进程独立GIL）| 不受限（单线程）|
| **启动开销** | 低 | 高（新解释器实例）| 极低 |
| **通信** | 共享变量/Queue | Queue/Pipe（pickle）| 直接共享 |
| **适合场景** | I/O密集型 | CPU密集型 | I/O密集型（高并发）|
| **最大并发数** | 受内存限制 | 受CPU核数限制 | 数万个协程 |

### 8.2 场景选型指南

```
问题是 I/O 密集型？（网络/磁盘/数据库等待）
  ├── 高并发（数千连接）→ asyncio
  └── 普通并发（数十连接）→ threading 或 asyncio

问题是 CPU 密集型？（计算、图像处理、压缩）
  ├── 有 C/Fortran 扩展（NumPy等）→ threading 可能足够
  └── 纯 Python 计算 → multiprocessing / ProcessPoolExecutor

需要跨机器分布式？
  └── 分布式任务队列（Celery/RQ）

快速开发 Web 应用？
  └── WSGI服务器（Gunicorn）自动处理并发，无需手动管理线程
```

---

## 9. 常见误区与陷阱

### ❌ 误区一：在 asyncio 协程中使用阻塞调用

```python
# ❌ 错误：冻结整个事件循环3秒
async def slow_task():
    time.sleep(3)              # 阻塞主线程

# ✅ 正确：让出控制权
async def slow_task():
    await asyncio.sleep(3)     # 挂起协程，事件循环继续运行

# ✅ 正确：CPU密集型任务委托给进程
async def cpu_task():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, cpu_heavy_func)
```

### ❌ 误区二：以为多线程能加速 CPU 密集型任务

```python
# ❌ 错误认知：更多线程 = 更快
import threading

def prime_check(n):
    return is_prime(n)

threads = [threading.Thread(target=prime_check, args=(n,)) for n in numbers]
# 实际上：由于 GIL，这些线程是串行的，性能比单线程还差（有线程切换开销）

# ✅ 正确：CPU密集型用多进程
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as executor:
    results = list(executor.map(prime_check, numbers))  # 真正并行
```

### ❌ 误区三：忘记 multiprocessing 跨进程通信需要序列化

```python
# ⚠️ 注意：放入 multiprocessing.Queue 的对象必须能被 pickle 序列化
# 以下类型无法序列化：lambda、闭包、文件句柄、数据库连接

# ❌ 错误
queue.put(lambda x: x * 2)   # lambda 无法 pickle

# ✅ 正确：只传递可序列化的数据
queue.put({'n': 5, 'result': True})
```

### ❌ 误区四：误以为协程可以在任意地方使用 await

```python
# ❌ 错误：在普通函数中使用 await
def regular_function():
    result = await some_coroutine()  # SyntaxError!

# ✅ 正确：await 只能在 async def 函数中使用
async def async_function():
    result = await some_coroutine()
```

### ❌ 误区五：以为线程是解决所有并发问题的唯一方案

```python
# 线程的问题：
# 1. 共享状态难以正确保护（需要锁，容易死锁）
# 2. 调试困难（竞态条件难以复现）
# 3. CPU密集型任务受GIL限制

# 更好的模式：
# - 用消息传递代替共享状态（队列）
# - 用协程代替线程（I/O密集型）
# - 用进程代替线程（CPU密集型）
# - 用任务队列代替自己管理线程（生产环境）
```

---

*整理自《流畅的Python（第2版）》第19章 | 知识点覆盖：19.2-19.9*
