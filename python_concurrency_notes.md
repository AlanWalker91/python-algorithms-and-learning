# Python 并发与异步编程学习笔记

> 学习日期：2025-05-19
> 主题：asyncio、threading、性能测试方法论
> 适用：测试开发工程师面试 & 实战

---

## 目录

- [一、心智模型：奶茶店三兄弟](#一心智模型奶茶店三兄弟)
- [二、asyncio 核心机制](#二asyncio-核心机制)
- [三、threading 核心机制](#三threading-核心机制)
- [四、三种并发方案的边界](#四三种并发方案的边界)
- [五、GIL 深度理解](#五gil-深度理解)
- [六、async 的传染性](#六async-的传染性)
- [七、性能测试方法论（实战踩坑）](#七性能测试方法论实战踩坑)
- [八、面试问答模板](#八面试问答模板)
- [九、关键代码模板](#九关键代码模板)
- [十、未完成清单（下次学习的钩子）](#十未完成清单下次学习的钩子)

---

## 一、心智模型：奶茶店三兄弟

**核心比喻**：所有并发方案都可以套到"奶茶店处理订单"上。

| 现实场景 | 并发方案 | 形象 |
|---|---|---|
| 一个老板眼睛扫，谁等就盯下一个 | **asyncio 协程** | 1 个人 + 单线程事件循环 |
| 雇 10 个员工，各自盯自己的客人 | **threading 多线程** | 多个原生线程 + OS 调度 |
| 开 10 家分店，各自独立运营 | **multiprocessing 多进程** | 多个独立 Python 解释器 |

### 三个核心要素的翻译

| 现实 | 代码 |
|---|---|
| 100 个订单 | `urls = [...]` 任务列表 |
| 每个客人做奶茶要等 | 每个 `await` / I/O 等待 |
| "最多 10 个人"的限制 | `Semaphore(10)` 或 `max_workers=10` |
| 老板"同时盯着所有客人" | `asyncio.gather()` |
| 一杯做好交付 | `return` / `await response.json()` |

---

## 二、asyncio 核心机制

### 2.1 加速的本质

> **asyncio 加速 = 把多个任务的"等待时间"叠在一起**

```
requests 串行:
  请求1 ━━等响应━━ 收结果1 请求2 ━━等响应━━ 收结果2 ...
       CPU闲着         CPU闲着  (总耗时 = N × 单次耗时)

asyncio 并发 (N=10):
  请求1 ━━━━━━ 等 ━━━━━━ 收结果1
       请求2 ━━━━━━ 等 ━━━━━━ 收结果2
            请求3 ━━━━━━ 等 ━━━━━━ 收结果3
            ...
  ↑ "等"重叠了，总耗时 ≈ 单个请求耗时
```

**关键认知**：asyncio 只对 **I/O 密集型**有用——CPU 密集任务没有"等待时间"可以叠，反而会因为协程切换变慢。

### 2.2 Semaphore 的真相

❌ **错误心智模型**：Semaphore 是保安，第 11 个人来了就拒绝
✅ **正确心智模型**：Semaphore 是 "10 把椅子 + 无限长的队伍"

```python
async def fetch_one(url):
    async with semaphore:        # 取号:没号就在这里 await 等
        # 真正干活的代码:发请求、等响应
        ...
```

- 11+ 个任务来了不会被拒绝，而是**在 `async with` 这一行睡觉**
- 不占 CPU，只是 await 等着
- 有人离开（async with 退出），下一个自动进入

### 2.3 gather 的关键性质

```python
results = await asyncio.gather(*tasks)
```

**三个必记的事实**：

1. **会阻塞**直到所有任务完成（不是发完就返回）
2. 返回的 `results` 顺序 = 传入的 `tasks` 顺序（**不是完成顺序**）
3. 必须用 `*tasks` 解包——传 `tasks`（列表）会被当成单个任务

### 2.4 `*` 解包语法（顺手补的高频考点）

```python
# 定义时的 *  —— 收集（多个参数 → 元组）
def f(*args):
    print(args)   # (1, 2, 3)

# 调用时的 *  —— 打散（列表 → 多个参数）
nums = [1, 2, 3]
f(*nums)  # 等价于 f(1, 2, 3)
```

**口诀**：定义时收集，调用时打散。

### 2.5 实测数据：N=1 vs N=10

亲手实验结果：**5 倍加速**（不是 10 倍）

**为什么不是 10 倍**？因为每个请求的耗时不是纯等待：

```
总时间 ≈ (网络等待时间 / 并发数) + CPU时间 × N
                ↓                     ↓
          并发数提高它在变小        这部分不变（GIL）
```

**结论**：并发数是上限，不是实际加速比。实际加速比 = f(单请求等待时间占比, 服务器处理能力, 客户端 CPU 开销)。

---

## 三、threading 核心机制

### 3.1 ThreadPoolExecutor 是现代写法

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_one, urls))
```

**为什么用线程池而不是手动 Thread**：

- 不用手动 start/join
- 自动复用线程，控制并发数
- `with` 退出时自动 `shutdown(wait=True)` —— 等所有任务完成

### 3.2 threading 与 asyncio 的形状对比

| | asyncio | threading |
|---|---|---|
| 并发上限怎么设 | 创建很多任务 + `Semaphore(10)` 限流 | 直接 `max_workers=10` 限制线程数 |
| 收集结果 | `await gather(*tasks)` | `list(executor.map(...))` 或 `with` 退出 |
| 顺序保证 | gather 保证 | map 保证 |
| 任务成本 | 极低（KB 级） | 较高（MB 级栈） |
| 切换由谁主导 | 自己主动让出（await） | OS 强制抢占 |

### 3.3 关键陷阱：`requests.get` vs `requests.Session()`

❌ **错误写法**——每次握手，慢：

```python
def fetch_one(url):
    return requests.get(url).json()   # 每次新建连接
```

✅ **正确写法**——复用连接：

```python
session = requests.Session()
def fetch_one(url):
    return session.get(url).json()    # 共享连接池
```

**机制**：
- `requests.get()` → 每次 DNS + TCP 握手 + TLS 握手 + 关闭
- `requests.Session()` → HTTP Keep-Alive，连接复用

**面试提醒**：对比 asyncio 时一定要用 Session，否则比的不是"协程 vs 线程"，是"有没有连接池"。

---

## 四、三种并发方案的边界

### 决策树

```
              我的瓶颈在哪？
                   │
        ┌──────────┴──────────┐
        │                     │
  I/O 密集（等网络/磁盘）   CPU 密集（计算/解析）
        │                     │
   ┌────┴────┐                │
   │         │                │
 并发量小   并发量大       multiprocessing
 (几十~几百) (几千+)        绕过 GIL，利用多核
   │         │
threading   asyncio
线程池      协程
```

### 实际能扛的并发量级

| 方案 | 并发量级 | 限制原因 |
|---|---|---|
| threading | **几十到几百** | 每线程 ~8MB 栈 + OS 调度 + GIL 争抢 |
| asyncio | **几千到几万**（单进程） | 协程是用户态对象，KB 级 |
| 协程 + 多进程 | **十万级** | 多进程各跑事件循环 |

> ⚠️ **常见错误**：很多人以为线程能扛几千几万——这是把"理论上可以创建"和"实际能流畅运行"搞混了。**几百是线程的真实上限**。

### 三句话口诀

1. **I/O 密集 + 中小并发** → `threading` / `ThreadPoolExecutor`
2. **I/O 密集 + 高并发** → `asyncio`（前提：生态都是 async 版本）
3. **CPU 密集** → `multiprocessing`（唯一能绕过 GIL 的方案）

---

## 五、GIL 深度理解

### 5.1 为什么有 GIL 还能加速 I/O？

> **GIL 只保护"正在执行 Python 字节码"的时候。线程进入 I/O 等待时会主动释放 GIL，让其他线程拿到 GIL 去执行。**

所以 I/O 密集场景下：
- 一个线程在等网络 → 释放 GIL → 另一个线程可以执行 Python 代码
- 多个线程的"等待时间"被叠加 → 加速效果

### 5.2 协程让出 vs 线程让出的区别

| | 协程 | 线程 |
|---|---|---|
| 谁来让出 | **自己主动**（遇到 await） | **OS 强制**（时间片到 or I/O 阻塞） |
| 让出时机可预测吗 | 可（只在 await 点） | 不可（随时可能切） |
| 是否需要锁 | 大部分不需要 | **必须**（共享数据时） |

### 5.3 为什么 multiprocessing 能绕过 GIL？

每个进程有**独立的 Python 解释器**和**独立的 GIL**。多进程 = 真并行（多核同时运算）。

**代价**：
- 进程比线程重（独立内存空间）
- 进程间通信麻烦（pickle 序列化）
- Windows 启动方式有坑（spawn vs fork）

---

## 六、async 的传染性

### 6.1 现象

> 一旦项目用了 asyncio，整条 I/O 调用链上的库都必须是异步版本。

### 6.2 同步库 vs 异步库对照表

| 同步库 ❌ | 异步替代 ✅ |
|---|---|
| `requests` | `aiohttp` / `httpx` |
| `pymysql` | `aiomysql` / `asyncpg` |
| `redis-py`（旧版） | `aioredis` |
| `time.sleep()` | `asyncio.sleep()` |
| 同步 `open()` | `aiofiles` |

### 6.3 翻车现场——为什么会差 100 倍

```python
# 代码 A（错）
async def fetch_and_process(url):
    async with session.get(url) as resp:
        data = await resp.json()
    time.sleep(2)             # ← 阻塞事件循环！
    return data

# 代码 B（对）
async def fetch_and_process(url):
    async with session.get(url) as resp:
        data = await resp.json()
    await asyncio.sleep(2)    # ← 让出控制权
    return data
```

100 个并发任务运行结果：
- **B：约 2 秒**（100 个 sleep 叠加）
- **A：约 200 秒**（每个 time.sleep 卡住整个事件循环 → 退化成串行）

**核心机制**：asyncio 事件循环是**单线程**的，一个同步阻塞调用会冻住**所有**协程。

### 6.4 兜底方案：run_in_executor

如果某个第三方库没有异步版本，可以用 `loop.run_in_executor()` 把它丢到线程池：

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def call_sync_lib(arg):
    loop = asyncio.get_event_loop()
    # 把同步函数丢到线程池，不阻塞事件循环
    result = await loop.run_in_executor(None, sync_function, arg)
    return result
```

> **面试加分句**："asyncio 最大的代价是它的传染性——一旦混进同步库就会阻塞整个事件循环。兜底方案是用 `run_in_executor` 把同步调用扔到线程池里。"

---

## 七、性能测试方法论（实战踩坑）

> **本节是今天最值钱的内容——这是测开真正的"工作能力"**

### 7.1 第一原则

> **压测目标，而不是压测工具。如果"工具/环境"本身比"目标"弱，你测的就是工具，不是目标。**

### 7.2 单次跑数没意义——必须用统计量

```python
import statistics

times = []
for _ in range(10):
    start = time.perf_counter()
    # 跑一次测试
    times.append(time.perf_counter() - start)

print(f"中位数: {statistics.median(times):.3f}s")
print(f"P95:    {sorted(times)[int(len(times)*0.95)]:.3f}s")
print(f"最快:   {min(times):.3f}s")
print(f"最慢:   {max(times):.3f}s")
```

**为什么用中位数而不是平均数**：偶尔一次特别慢（网络抖动）会把平均数拉飞，但**不影响中位数**。

**P95 是什么**："95% 的请求比这个快"——比平均响应时间有意义得多。

### 7.3 标准流程

1. **预热**：先发几个请求让 DNS 缓存、连接池热起来
2. **隔离变量**：本地 mock，去掉公网网络抖动
3. **多轮测**：至少 5-10 轮
4. **看统计**：中位数 + P95，不看单次

### 7.4 我今天亲历的两次踩坑

#### 坑 1：`HTTPServer` 是单线程的

```python
# ❌ 单线程：一次只能处理一个请求
server = HTTPServer(('localhost', 8000), Handler)

# ✅ 多线程：每个请求开线程处理
server = ThreadingHTTPServer(('localhost', 8000), Handler)
```

**现象**：客户端并发数设 10 时被服务端"拒绝连接"，因为服务端 backlog 满了。
**误判**：本以为是 asyncio 不行，实际是 mock 服务扛不住。

#### 坑 2：`ThreadingHTTPServer` 性能也很差

每个请求新开**原生线程**（没有线程池复用），高并发下：
- 实测每个请求实际网络时间 **2148ms**（mock 只 sleep 100ms）
- 多出来的 2 秒**全在服务端排队**

**结果数据**（50 个请求，并发 10，mock sleep 100ms）：

| 方案 | 中位耗时 | 理论值 |
|---|---|---|
| asyncio + aiohttp | **1.30s** | 0.5s |
| threading + requests.Session | **10.77s** | 0.5s |

**差距 8 倍**——但这不是"asyncio 比 threading 快 8 倍"！

### 7.5 怎么解读这个 8 倍

❌ **不专业的报告**："asyncio 比 threading 快 8 倍"

✅ **专业的报告**：

> "在 ThreadingHTTPServer mock 服务、50 并发、模拟 100ms 处理时间的场景下，
> asyncio 中位耗时 1.3s，threading 10.8s。差距主要来源于服务端在高连接数下
> 的处理瓶颈被客户端连接管理开销放大。在生产级 async 服务器下，两者差距
> 预计会缩小到 20% 以内。"

**这就是测开岗位想要的水平**——给场景、给数字、给归因、给边界。

### 7.6 排查瓶颈的通用思路

把请求拆开计时：

```python
def fetch(url):
    t0 = time.perf_counter()
    r = session.get(url)
    t1 = time.perf_counter()
    data = r.json()
    t2 = time.perf_counter()
    return (t1-t0, t2-t1)   # (网络时间, CPU 解析时间)
```

看哪段时间长，瓶颈就在哪。**这是工作里最常用的排查手段**。

### 7.7 真实工作中的瓶颈定位思考

被问"为什么我们 API 比竞品慢 3 倍"时，要会拆：

```
[客户端] → [网络] → [服务端 nginx] → [应用代码] → [DB/缓存] → [回程]
   ↑          ↑           ↑              ↑            ↑
 压测工具   带宽限速    连接数限制    代码 CPU 慢    DB 连接池满
```

每一段都可能是瓶颈，**必须分段测量**。

---

## 八、面试问答模板

### 8.1 "asyncio 加速的原理"

> "asyncio 加速的本质是**把多个任务的等待时间叠在一起**。事件循环单线程，遇到 `await` 时主动让出控制权去调度其他协程。所以它只对 **I/O 密集**有效——CPU 密集任务没有等待时间可叠，反而因为协程切换开销变慢。"

### 8.2 "为什么 asyncio 加速比小于并发数"（你跑出 5 倍而不是 10 倍）

> "并发数是上限，不是实际加速比。一个请求的耗时不只有等待时间，还有 CPU 实际干活的部分（构造请求、JSON 解析、协程调度等）。
>
> 这些 CPU 部分受 GIL 限制，**同一时刻只有一个协程在执行**，没法被叠加。所以加速比 = 等待时间占比决定的。如果换成响应慢的接口，加速比会更接近并发数。"

### 8.3 "GIL 存在为什么多线程还能加速 I/O"

> "GIL 只保护'正在执行 Python 字节码'的时候。一个线程进入 I/O 等待时会**主动释放 GIL**，让其他线程拿到 GIL 去执行。所以 I/O 密集场景下，多线程的等待时间能叠加。
>
> 但 CPU 密集场景下，GIL 一直被持有，多线程退化成串行，必须用 multiprocessing 才能绕过 GIL。"

### 8.4 "asyncio / threading / multiprocessing 怎么选"

> "看瓶颈类型和并发量：
> - **I/O 密集 + 中小并发**（几十几百）→ threading，写法简单，兼容老库
> - **I/O 密集 + 高并发**（几千+）→ asyncio，前提是整条调用链都是 async 版本
> - **CPU 密集** → multiprocessing，唯一能绕过 GIL 的方案"

### 8.5 "asyncio 有什么缺点/踩过什么坑"

> "asyncio 最大的代价是**传染性**——一旦项目用了 asyncio，整条 I/O 调用链上的库都必须是异步版本。如果中间混进一个同步库（比如 requests 或 pymysql），它会**阻塞整个事件循环**——不只是当前协程卡住，所有其他在 await 的协程都跟着卡死。
>
> 引入前要先确认生态。如果某个第三方库没有异步版本，可以用 **`loop.run_in_executor()`** 把它丢到线程池里跑，避免阻塞事件循环。"

### 8.6 "你怎么做接口性能测试"

> "几个原则：
> 1. **多轮取统计量**——单次跑数会被网络抖动污染，用中位数和 P95
> 2. **预热再测**——让 DNS 缓存、连接池热起来再开始计时
> 3. **隔离变量**——用本地 mock 排除公网噪音
> 4. **拆段计时**——把请求拆成网络段和 CPU 段，定位真正的瓶颈
> 5. **警惕测试工具本身是瓶颈**——如果工具比目标弱，测出来的就是工具
>
> 报告时要给**场景 + 数字 + 归因 + 边界**，不要只给绝对结论。"

---

## 九、关键代码模板

### 9.1 asyncio + aiohttp 并发请求

```python
import asyncio
import aiohttp

async def fetch_one(session, semaphore, url):
    async with semaphore:
        async with session.get(url) as response:
            return await response.json()

async def main():
    urls = [f"https://example.com/{i}" for i in range(100)]
    semaphore = asyncio.Semaphore(10)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks)  # 注意 * 解包

    return results

asyncio.run(main())
```

### 9.2 threading + requests.Session 并发请求

```python
from concurrent.futures import ThreadPoolExecutor
import requests

urls = [f"https://example.com/{i}" for i in range(100)]
session = requests.Session()       # 关键：复用连接

def fetch_one(url):
    return session.get(url).json()

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_one, urls))
```

### 9.3 asyncio 调用同步库（run_in_executor 兜底）

```python
import asyncio

def sync_blocking_function(arg):
    """假设这是个同步库的调用"""
    import time
    time.sleep(1)
    return f"result for {arg}"

async def main():
    loop = asyncio.get_event_loop()

    # 把同步函数丢进线程池，不阻塞事件循环
    tasks = [
        loop.run_in_executor(None, sync_blocking_function, i)
        for i in range(10)
    ]
    results = await asyncio.gather(*tasks)
    return results

asyncio.run(main())
```

### 9.4 严肃版性能测试模板

```python
import statistics
import time

def benchmark(name, runner, rounds=10):
    # 预热
    runner()

    # 正式测试
    times = []
    for _ in range(rounds):
        start = time.perf_counter()
        runner()
        times.append(time.perf_counter() - start)

    print(f"{name:15s} "
          f"中位数={statistics.median(times):.3f}s  "
          f"P95={sorted(times)[int(len(times)*0.95)]:.3f}s  "
          f"最快={min(times):.3f}s  "
          f"最慢={max(times):.3f}s")
```

### 9.5 本地 mock HTTP 服务

```python
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import threading, time

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(0.1)  # 模拟处理时间
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"id": 1, "title": "test"}')
    def log_message(self, *args): pass  # 静默日志

# 注意用 ThreadingHTTPServer，不是 HTTPServer
server = ThreadingHTTPServer(('localhost', 8000), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
time.sleep(0.5)  # 等服务起来
```

> ⚠️ **提醒**：`ThreadingHTTPServer` 性能依然有限（每请求开新线程，无池）。生产级 mock 应该用 FastAPI + uvicorn。

---

## 十、未完成清单（下次学习的钩子）

按重要性排序：

1. **`gather` vs `as_completed` vs `TaskGroup`**
   - `gather`：等所有完成，按顺序返回
   - `as_completed`：谁先完成处理谁，迭代器
   - `TaskGroup`（Python 3.11+）：异常时自动取消其他任务，更安全

2. **线程安全：Lock / Queue / 竞态条件**
   - 多个线程改同一个变量为什么会出问题
   - Lock / RLock / Semaphore 在 threading 里的用法
   - `queue.Queue` 做生产者-消费者

3. **`asyncio.Queue`**——异步生产者-消费者模式

4. **协程的取消和超时**
   - `asyncio.wait_for(coro, timeout=5)`
   - `CancelledError` 处理

5. **`async with semaphore` 异常时会不会释放**（之前留的伏笔）

6. **multiprocessing 实战**
   - `Pool.map` vs `Pool.apply_async`
   - 进程间通信：`Queue` / `Pipe` / `Manager`
   - pickle 坑、Windows 启动方式

7. **生产级 mock 服务**
   - FastAPI + uvicorn 起一个真正能扛压的本地服务
   - 重做 asyncio vs threading 的"公平对比"

8. **pytest-asyncio**——在 pytest 里测异步代码

---

## 附录：今天的学习路径

```
起点：感觉很"空"，不知道从何下手
   ↓
诊断：脑子里没有结构骨架
   ↓
奶茶店模型 → 建立直觉骨架
   ↓
Semaphore = 椅子 + 隐式排队
   ↓
gather = 等所有任务完成，保持顺序
   ↓
* 解包语法（顺手补的）
   ↓
亲手实验：N=1 vs N=10 → 跑出 5 倍
   ↓
分析 5 倍而非 10 倍 → 理解"等待时间叠加 ≠ CPU 时间叠加"
   ↓
GIL 限制 → asyncio 只适合 I/O 密集
   ↓
对比 threading / multiprocessing → 三方案边界
   ↓
async 传染性 → 同步库阻塞事件循环
   ↓
threading 实战 → ThreadPoolExecutor + Session
   ↓
性能测试踩坑 → HTTPServer 单线程 / ThreadingHTTPServer 性能差
   ↓
终点：建立"用数据反推系统瓶颈"的能力
```

---

## 给自己的话

今天最重要的收获不是"学会了 asyncio 和 threading"——这些是知识点，看博客也能学会。

**真正值钱的是**：
- 学会了"看懂 ≠ 会用"的元认知
- 学会了用奶茶店模型把抽象概念翻译成直觉
- 学会了"性能数据要带场景和归因"的测开思维
- 亲手踩过两次"测试环境本身是瓶颈"的坑

**这些经验比任何书本知识都扎实——可以直接写进简历、讲给面试官听**。

> 简历亮点示例：
> "搭建本地 mock 服务进行 asyncio vs threading 性能对比测试，
> 识别出 Python 标准库 HTTPServer 单线程瓶颈和 ThreadingHTTPServer
> 高并发性能问题，掌握中位数/P95 等统计指标和预热、控制变量等
> 性能测试方法论。"

继续加油！🚀
