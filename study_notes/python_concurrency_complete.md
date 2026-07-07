# Python 并发与异步编程学习笔记

> 学习日期：2025-05-19
> 主题：asyncio、threading、性能测试方法论

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
# 笔记补丁:线程安全完整版

> 拼接到原笔记的"三、threading 核心机制"之后,作为 3.4 ~ 3.8 节

---

## 3.4 为什么需要锁:竞态条件

### 核心翻车现场

```python
counter = 0

def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1   # ← 这一行不是原子操作!

# 两个线程并发,结果不是 2,000,000,而是随机数
```

### 为什么?GIL ≠ 线程安全

`counter += 1` 在字节码层面是 **3 步**:

```
LOAD_GLOBAL counter      ← 读
LOAD_CONST 1
BINARY_ADD               ← 算
STORE_GLOBAL counter     ← 写
     ↑
GIL 可能在任意一步切换线程 → 丢失更新
```

> **面试金句**:"GIL 保证字节码级别的原子性,**不保证 Python 语句级别的原子性**。`counter += 1` 是多条字节码,中间可能被切换,所以多线程下需要锁。"

---

## 3.5 Lock:基础锁

### 心智模型:收银机的钥匙

```
       共享资源
          │
     ┌────┴────┐
     │ 一把钥匙 │
     └────┬────┘
          │
   ┌──────┼──────┐
   │      │      │
 线程A  线程B  线程C
   ↑
 一次只有一个能拿到,其他在 with lock: 这一行睡觉
```

### 标准用法

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    with lock:           # 拿锁,没拿到就等
        counter += 1
    # 出 with 自动释放
```

### 三条铁律

1. **`with lock:` 优于手动 acquire/release** —— 异常安全,出 with 必定释放
2. **缩进决定临界区边界** —— 哪行受锁保护看缩进
3. **check-then-act 必须在同一个锁里** —— "先检查再操作"不能拆成两段

### check-then-act 反例(转账 bug)

```python
# ❌ 错误:检查和扣款没在同一个锁里
def transfer(amount):
    with lock:
        if balance >= amount:    # 检查
            pass
    balance -= amount            # 出锁了再扣,可能超支

# ✅ 正确:检查和扣款都在锁里
def transfer(amount):
    with lock:
        if balance < amount:
            raise ValueError("余额不足")
        balance -= amount        # 检查 + 修改原子完成
        return balance
```

---

## 3.6 RLock:可重入锁

### Lock 的死锁陷阱

```python
lock = threading.Lock()

def outer():
    with lock:           # T1 拿到锁
        inner()

def inner():
    with lock:           # T1 又想拿同一把锁 → 自己等自己 → 死锁
        ...
```

**Lock 不认人**——它只看"我被拿了吗",不看"谁拿的"。同一线程二次 acquire **会和别人抢锁一样卡死**。

### RLock 解药

```python
lock = threading.RLock()   # 只改这一行
# 其他代码不变 → 正常运行
```

**RLock 认人**——内部记录 owner 和 reentry count。同一线程再拿 → count+1,直接通过;释放 → count-1,归零才真正释放。

### Lock vs RLock 选型

| | Lock | RLock |
|---|---|---|
| 性能 | 略快 | 略慢(owner 检查) |
| 嵌套调用安全 | ❌ 死锁 | ✅ 允许 |
| 适合 | 简单临界区 + 性能敏感 | 库代码 / 函数会被嵌套 |
| **新手建议** | | ⭐ **默认选这个,更安全** |

---

## 3.7 Queue:生产者-消费者(实战 90% 用这个)

### 核心理念

> **生产代码里 90% 的线程间通信不用 Lock,用 Queue。**
>
> Queue 把"锁 + 数据结构"封装成开箱即用的线程安全工具,你只用 put/get,**内部所有锁管理都帮你做好了**。

### 心智模型:传送带

```
[生产者] → put → [传送带 Queue] → get → [消费者]
                  ↑
                 满了自动让生产者等
                 空了自动让消费者等
                 完全没有竞态条件
```

### 标准生产者-消费者模板

```python
import queue
import threading

q = queue.Queue(maxsize=10)
SENTINEL = None     # "毒丸",表示流结束

def producer():
    for item in data_source:
        q.put(item)         # 满了自动等
    # 发毒丸通知消费者下班
    for _ in range(NUM_CONSUMERS):
        q.put(SENTINEL)

def consumer(name):
    while True:
        item = q.get()      # 空了自动等
        if item is SENTINEL:
            break            # 收到毒丸,优雅退出
        process(item)
        q.task_done()        # 标记任务完成

# 启动
threading.Thread(target=producer).start()
for i in range(3):
    threading.Thread(target=consumer, args=(f"worker-{i}",)).start()

q.join()    # 等所有任务被 task_done
```

### Queue 核心方法速查

| 方法 | 行为 |
|---|---|
| `q.put(item)` | 放入,满了阻塞 |
| `q.get()` | 取出,空了阻塞 |
| `q.put_nowait(item)` | 满了立刻抛 `queue.Full` |
| `q.get_nowait()` | 空了立刻抛 `queue.Empty` |
| `q.put(item, timeout=5)` | 等 5 秒抛 `queue.Full` |
| `q.get(timeout=5)` | 等 5 秒抛 `queue.Empty` |
| `q.task_done()` | 标记"这个任务我做完了" |
| `q.join()` | 等所有 put 进去的都被 task_done |

### "毒丸"模式(面试常考)

**问题**:消费者用 `while True` 死循环,怎么优雅退出?

**答案**:用一个特殊值(通常是 None)做"流结束"标记。消费者拿到就 break。

### Queue 三兄弟

| 类 | 行为 | 场景 |
|---|---|---|
| `queue.Queue` | FIFO | 默认选择 |
| `queue.LifoQueue` | LIFO(栈) | DFS 算法 |
| `queue.PriorityQueue` | 按优先级 | P0/P1 优先级任务 |

```python
import queue
pq = queue.PriorityQueue()
pq.put((1, "紧急"))     # 数字越小越优先
pq.put((3, "普通"))
pq.put((2, "重要"))
pq.get()   # (1, "紧急")
```

---

## 3.8 工具选型决策树

```
我需要线程间共享数据?
      │
      ├─ 共享一个简单变量(计数器、累加值)
      │     └─→ threading.Lock + with 块
      │
      ├─ 函数会嵌套调用 / 写库代码
      │     └─→ threading.RLock
      │
      ├─ 控制并发数量上限(N 个资源)
      │     └─→ threading.Semaphore(N)
      │
      ├─ 持续流入的任务流(生产者-消费者)
      │     └─→ queue.Queue ⭐ 优先选这个
      │
      ├─ 一批任务并发执行,收集结果
      │     └─→ ThreadPoolExecutor.map
      │
      └─ 优先级任务调度
            └─→ queue.PriorityQueue
```

### 关键原则:能用 Queue 就别用 Lock

> **手写锁太容易出 bug**(死锁、忘释放、临界区漏边界、check-then-act 拆分)。
> **Queue 已经把这些问题解决了**。能用 Queue 表达的场景,优先 Queue。

---

## 3.9 面试问答模板

### Q1:"Python 多线程是不是没用?(因为 GIL)"

> "不准确。GIL 让 Python 多线程**在 CPU 密集场景下没有加速效果**——因为同一时刻只有一个线程能执行 Python 字节码。
>
> 但 I/O 密集场景下,线程在等 I/O 时会**主动释放 GIL**,其他线程可以拿到 GIL 执行,所以 I/O 密集多线程仍然有效。
>
> CPU 密集场景应该用 multiprocessing,绕过 GIL 利用多核。"

### Q2:"counter += 1 是原子操作吗?"

> "不是。它在字节码层面是读、加、写三步,多线程下会丢失更新。需要用 Lock 保护。
>
> GIL 保证的是字节码级别的原子性,不保证 Python 语句级别的原子性。"

### Q3:"Lock 和 RLock 的区别?"

> "Lock 不认人——同一线程二次 acquire 也会死锁(自己等自己)。RLock 认人——内部记录 owner 和重入次数,同一线程可以重复 acquire。
>
> 库代码、可能嵌套调用的场景必须用 RLock。性能敏感且确定不嵌套的场景可以用 Lock。"

### Q4:"生产者消费者模式怎么实现?消费者怎么优雅退出?"

> "用 `queue.Queue` 做缓冲。生产者 put,消费者 get,Queue 内部已经处理了所有同步问题,不需要手写锁。
>
> 优雅退出用'毒丸'模式——生产者结束后 put 一个特殊值(比如 None),消费者拿到就 break。需要给每个消费者发一个毒丸。"

### Q5:"什么时候用 ThreadPoolExecutor,什么时候用 Queue?"

> "ThreadPoolExecutor 适合**一批任务并发处理**——任务集合已知,跑完就结束。
>
> Queue 适合**持续流入的任务流**和**多级流水线**——比如监控系统不断接收新检查任务,工作线程持续消费。两者经常配合:用 ThreadPoolExecutor 跑工作线程,用 Queue 做任务缓冲。"

---

## 3.10 关键代码模板

### 模板 1:简单计数器

```python
from threading import Lock
counter = 0
lock = Lock()

def increment():
    global counter
    with lock:
        counter += 1
```

### 模板 2:生产者-消费者(完整可运行版)

```python
import queue, threading, time

q = queue.Queue(maxsize=10)
SENTINEL = None
NUM_CONSUMERS = 3

def producer():
    for i in range(20):
        q.put(f"task-{i}")
        time.sleep(0.1)
    for _ in range(NUM_CONSUMERS):
        q.put(SENTINEL)

def consumer(name):
    while True:
        item = q.get()
        if item is SENTINEL:
            print(f"{name} 退出")
            break
        print(f"{name} 处理 {item}")
        time.sleep(0.3)
        q.task_done()

threading.Thread(target=producer).start()
threads = [threading.Thread(target=consumer, args=(f"w{i}",)) for i in range(NUM_CONSUMERS)]
for t in threads: t.start()
for t in threads: t.join()
```

### 模板 3:带优先级的任务调度

```python
import queue, threading

pq = queue.PriorityQueue()

def worker():
    while True:
        priority, task = pq.get()
        if task is None:
            break
        print(f"执行 P{priority}: {task}")
        pq.task_done()

t = threading.Thread(target=worker)
t.start()

pq.put((3, "普通报表"))
pq.put((1, "紧急告警"))      # 会先被处理
pq.put((2, "重要邮件"))
pq.put((0, None))            # 毒丸,最高优先级让它最先被消费
t.join()
```

---

## 3.11 给自己的话

到这里,threading 的核心你已经齐了:

- ✅ ThreadPoolExecutor(批处理)
- ✅ requests.Session(连接池陷阱)
- ✅ Lock / RLock(共享变量保护)
- ✅ Queue / PriorityQueue(生产者-消费者)
- ✅ "毒丸"模式(优雅退出)

**这套组合拳已经能覆盖测开工作里 95% 的并发场景**。剩下的 5%(分布式、跨进程通信)那是 multiprocessing 和消息队列的事了。
# Python 并发学习笔记 Part 3:任务编排、实战项目与生产级踩坑

> 学习日期:2025-05-22
> 主题:任务编排、协程取消与超时、生产者-消费者实战、Windows IPv6 大坑
> 衔接:Part 1(基础并发)+ Part 2(线程安全)的续篇

---

## 目录

- [一、任务编排:四种"收任务"的姿势](#一任务编排四种收任务的姿势)
- [二、协程的取消与超时](#二协程的取消与超时)
- [三、实战项目:多线程网页健康检查器](#三实战项目多线程网页健康检查器)
- [四、Windows IPv6 大坑:今天最值钱的发现](#四windows-ipv6-大坑今天最值钱的发现)
- [五、增量开发方法论](#五增量开发方法论)
- [六、面试问答模板(衔接版)](#六面试问答模板衔接版)
- [七、完整可运行代码](#七完整可运行代码)
- [八、给自己的话](#八给自己的话)

---

## 一、任务编排:四种"收任务"的姿势

### 1.1 核心问题

`asyncio.gather` 不是万能的——它有两个固有局限:
- **全部完成才返回**——不能"边完成边处理"
- **异常后其他任务不会自动取消**——产生"幽灵任务"

不同场景需要不同的 API。

### 1.2 四种 API 完整对比

| API | 返回时机 | 顺序 | 异常处理 | 适合场景 |
|---|---|---|---|---|
| `gather(*tasks)` | 全部完成 | 提交顺序 | 立刻抛(其他后台跑⚠️) | 简单全收 |
| `gather(*, return_exceptions=True)` | 全部完成 | 提交顺序 | 异常进结果列表 | 压测/批处理报告 |
| `as_completed(tasks)` | 谁先完成谁先出 | 完成顺序 | 迭代时抛 | 进度条/流式处理 |
| `wait(*, return_when=FIRST_COMPLETED)` | 第一个完成 | - | 看 done 集合 | 抢先式查询 |
| `TaskGroup()` (3.11+) | 全部完成 | 用 task.result() | **自动取消兄弟** ⭐ | 生产级 |

### 1.3 gather 默认行为的陷阱

**经典翻车点**:gather 抛异常时,**其他任务不会被自动取消**,会继续在后台跑——这就是 **fire-and-forget** 陷阱。

```
任务1 ✓
任务2 ✓
任务3 ✗ ← 抛异常,gather 立刻抛出
任务4..100 → 继续跑(没人收结果) ← 你不知道它们还在
```

**修复方法**:Python 3.11+ 用 `TaskGroup`,或手动 cancel。

### 1.4 return_exceptions=True 用法

```python
results = await asyncio.gather(*tasks, return_exceptions=True)

for i, r in enumerate(results):
    if isinstance(r, Exception):
        print(f"任务 {i} 失败: {r}")
    else:
        print(f"任务 {i} 成功: {r}")

# 结果列表示例:
# [
#     {'id': 1, ...},              # 成功
#     ValueError('bad url'),        # 异常被放在这里
#     {'id': 3, ...},              # 成功
# ]
```

### 1.5 as_completed:边完成边处理

```python
tasks = [fetch_one(url) for url in urls]

for coro in asyncio.as_completed(tasks):
    result = await coro          # 谁先完成谁先拿到
    print(f"刚到一个结果: {result}")
```

**适合**:
- 进度条
- 流式处理(早到的早处理,降低延迟)
- 提前停止(找到第一个满足条件就 break)

**坑**:迭代出来的不是按提交顺序,是按**完成顺序**。如果需要"知道这个结果对应哪个 URL",得让 fetch_one 把 url 也一起 return。

### 1.6 asyncio.wait:更底层的"等"

```python
done, pending = await asyncio.wait(
    tasks, return_when=asyncio.FIRST_COMPLETED
)
# done 是已完成的任务集合
# pending 是还在跑的任务集合,需要手动取消!
for t in pending:
    t.cancel()
```

**三种返回时机**:

| 参数 | 含义 |
|---|---|
| `ALL_COMPLETED`(默认) | 全完成才返回(类似 gather) |
| `FIRST_COMPLETED` | 第一个完成就返回 |
| `FIRST_EXCEPTION` | 第一个异常或全完成才返回 |

### 1.7 TaskGroup:Python 3.11+ 的结构化并发

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_one(url1))
        task2 = tg.create_task(fetch_one(url2))
        task3 = tg.create_task(fetch_one(url3))
    # 出了 async with,所有任务保证已完成

    print(task1.result(), task2.result(), task3.result())
```

**比 gather 强的三点**:

1. **异常时自动取消兄弟任务** ⭐ 没有 fire-and-forget 问题
2. **多个异常合并成 ExceptionGroup**——能看到所有失败,不是只看到第一个
3. **结构化并发**——任务生命周期被 `async with` 严格限制

### 1.8 选型决策树

```
                 我要怎么收任务?
                       │
        ┌──────────────┼──────────────┬───────────────┐
        │              │              │               │
   "全部要齐"       "边完成边处理"   "拿到第一个就停"  "生产级,任一失败全停"
        │              │              │               │
     gather       as_completed   asyncio.wait      TaskGroup (3.11+)
                                 (FIRST_COMPLETED)
        │
   要异常容错?
        │
   return_exceptions=True
```

---

## 二、协程的取消与超时

### 2.1 取消是**协作式**的,不是强制式的

> **核心认知:`task.cancel()` 只是发信号(纸条),不会立刻杀死任务。**

```
task.cancel() 实际做的事:
1. 给任务标记"被取消了"
2. 任务下次执行到 await 时,在 await 点抛出 CancelledError
3. 如果任务没有 await 点(纯 CPU 循环),cancel() 完全无效
```

### 2.2 经典翻车场景:纯 CPU 循环无法被取消

```python
async def slow_calculation():
    total = 0
    for i in range(10**9):    # 10 亿次循环,纯 CPU,没有 await
        total += i * i
    return total

async def main():
    task = asyncio.create_task(slow_calculation())
    await asyncio.sleep(0.1)
    task.cancel()             # 发信号,但任务没 await 点
    await asyncio.sleep(2)    # 这个 sleep 也会被卡!
```

**为什么 sleep(2) 也被卡?**

asyncio 事件循环是**单线程**的。slow_calculation 是 CPU 循环,占着事件循环不放,**main 的 sleep(2) 也无法被唤醒**——必须等 slow_calculation 跑完。

> **金句**:"asyncio 的所有时间承诺都是'至少',不是'刚好'——前提是事件循环空闲。任何 CPU 密集任务都会让整个事件循环失去时间精度。"

### 2.3 清理资源的标准写法

```python
async def task_with_cleanup():
    try:
        await do_something()
        await do_more()
    except asyncio.CancelledError:
        await close_connection()    # 做清理
        raise                        # ⭐ 必须 re-raise!
```

**两条铁律**:
1. **try/except CancelledError 是允许的**——只要是为了清理
2. **必须 re-raise**——否则取消语义被吞掉,上层以为任务正常完成

### 2.4 "等取消真正生效"的标准模式

```python
task.cancel()
try:
    await task              # 等任务处理完取消信号
except asyncio.CancelledError:
    pass
```

**为什么需要这一段**?因为 `cancel()` 只是发信号,如果你想确认任务真的停了(而不是只是"被通知了"),必须 await 它。

### 2.5 超时 = 自动 cancel 的语法糖

```python
# 写法 1:任何 Python 版本
result = await asyncio.wait_for(fetch_one(url), timeout=5)

# 写法 2:Python 3.11+,适合多个 await 的代码块
async with asyncio.timeout(5):
    result = await fetch_one(url)
    other_result = await process(result)
```

`wait_for` 内部做的事:
1. 启动协程
2. 同时启动一个 5 秒计时器
3. 谁先完成
   - 协程先 → 返回结果
   - 计时器先 → 调用 `cancel()` → 抛 `TimeoutError`

### 2.6 测开必背模板:超时 + 异常容错

```python
async def fetch_with_timeout(url, timeout=5):
    try:
        return await asyncio.wait_for(fetch_one(url), timeout=timeout)
    except asyncio.TimeoutError:
        return {"url": url, "error": "timeout"}
    except Exception as e:
        return {"url": url, "error": str(e)}

async def main():
    urls = [...]
    tasks = [fetch_with_timeout(url) for url in urls]
    results = await asyncio.gather(*tasks)
    # 不需要 return_exceptions——因为已经在内部把异常转成 dict 了
```

**这个模式在测开工作里会用 100 次。**

---

## 三、实战项目:多线程网页健康检查器

> **今天最重要的实战——把所学的所有 threading 知识串起来。**

### 3.1 项目架构图

```
                    [URL 列表 (20 个)]
                            │
                            ↓
                  ┌─────────────────────┐
                  │  1 个 producer 线程  │  (循环 put URL,完发毒丸)
                  └──────────┬──────────┘
                             │ put
                             ↓
                  ╔═══════════════════════╗
                  ║  task_queue (任务队列)  ║  ← 装 URL 字符串
                  ╚═══════════════════════╝
                             │ get
                  ┌──────────┴──────────┐
                  │   3 个 worker 线程   │  (get URL → 请求 → put 结果)
                  └──────────┬──────────┘
                             │ put
                             ↓
                  ╔═══════════════════════╗
                  ║ result_queue (结果队列) ║  ← 装结果字典
                  ╚═══════════════════════╝
                             │ get
                             ↓
                  ┌─────────────────────┐
                  │ 1 个 reporter 线程  │  (实时打印 + 统计)
                  └──────────┬──────────┘
                             ↓
                       [最终统计报告]
```

### 3.2 三个角色的职责单一性

| 角色 | 数量 | 职责 |
|---|---|---|
| producer | 1 个 | put URL → put 毒丸(N 个) |
| worker | N 个(=3) | get URL → 请求 → put 结构化结果 |
| reporter | 1 个 | get 结果 → 打印 → 统计 |

**关键设计原则**:**每个角色职责单一**——不要让 worker 既请求又打印,这样难以扩展和测试。

### 3.3 队列的命名原则

**按"装什么"命名,不要按"谁放谁取"命名**:

| ❌ 错误命名 | ✅ 正确命名 | 装什么 |
|---|---|---|
| 生产者队列 | task_queue | URL 字符串 |
| 消费者队列 | result_queue | 结果字典 |

**为什么**?同一个队列**对生产者来说是出口,对消费者来说是入口**——按"谁"来命名一定会绕晕。

### 3.4 多级毒丸传递

```
producer 完成 → 给 task_queue 发 3 个毒丸(每个 worker 一个)
                          ↓
3 个 worker 收到毒丸,退出
                          ↓
所有 worker join 完成后 → 主线程给 result_queue 发 1 个毒丸
                          ↓
reporter 收到毒丸,打印最终统计,退出
                          ↓
主线程 join reporter,结束
```

**关键洞察**:reporter 的毒丸**由主线程在 worker 全部 join 完之后发**——不能由 worker 发,因为 worker 不知道"我是不是最后一个"。

> **面试加分点**:多级流水线的毒丸传递,90% 候选人想不到。

### 3.5 结构化结果设计(测开规范)

**不要用字符串**(`f"✅ {url} → 200"`),用 **dict**:

```python
# 成功
{"url": url, "status": "ok", "code": 200, "elapsed_ms": 105}

# 超时
{"url": url, "status": "timeout", "elapsed_ms": 5000}

# 错误
{"url": url, "status": "error", "error": "ConnectionError: ..."}
```

**好处**:
- 可统计(Counter)
- 可写文件(json.dumps)
- 可分析(filter/sort)
- 可上报(发到日志系统)

### 3.6 关键陷阱:start/join 顺序

```python
# ❌ 错误:start 一个 join 一个 → 并发退化成串行
for w in workers:
    w.start()
    w.join()        # 等它跑完才启动下一个

# ✅ 正确:先全部 start,再全部 join
for w in workers:
    w.start()
for w in workers:
    w.join()
```

**核心原则**:**先全部 start = 真正并发;再全部 join = 等所有完成**。

### 3.7 调试技巧:打印线程名 + 单次耗时

排查并发问题的标准手段:

```python
def worker():
    name = threading.current_thread().name
    while True:
        url = task_queue.get()
        if url is SENTINEL:
            break
        
        t0 = time.perf_counter()
        try:
            resp = session.get(url, timeout=5)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            print(f"[{name}] {url} → {resp.status_code} ({elapsed_ms:.0f}ms)")
        except Exception as e:
            print(f"[{name}] {url} → 失败: {e}")
```

**这两个信息能告诉你**:
- 多个 worker 名字交替出现 → 真并发
- 只有一个 worker 名字 → 没并发(可能阻塞、可能没启动)
- 单次耗时和理论值是否一致 → 是不是被外部因素拖累

---

## 四、Windows IPv6 大坑:今天最值钱的发现

> **这是今天最值钱的一条经验——别人书上学不到,只能踩过才知道。**

### 4.1 现象

同一份代码,**只改一个字**(`localhost` → `127.0.0.1`):

| URL | 单次请求耗时 | 总耗时(20 个并发) |
|---|---|---|
| `http://localhost:8000/...` | ~2150ms | **15 秒** |
| `http://127.0.0.1:8000/...` | ~70-300ms | **1.2 秒** |

**12 倍的性能差异,只来自一个域名解析**。

### 4.2 根本原因:Windows 的 IPv6 优先解析

```
请求 localhost 时,Windows 默认流程:
  1. 先查 IPv6 解析 (::1)
  2. 尝试 IPv6 连接 → 失败(超时,因为多数本地服务只监听 IPv4)
  3. 回退到 IPv4 (127.0.0.1)
  4. 真正连接成功

每次请求都走这个流程 → 每次多 ~2 秒
```

而 `127.0.0.1` **直接是 IP 字面量,跳过所有 DNS 解析,瞬间连接**。

### 4.3 这个坑的杀伤力

**专门坑测开**——而且非常难发现:

- 在 Linux/Mac 上**完全没问题**(它们的 IPv6 回退快)
- `ping localhost` 看起来一切正常
- 浏览器访问 `http://localhost` 不慢(浏览器有自己的处理)
- **只在多线程/高并发下表现明显**
- 单线程跑也慢,但因为基数小不容易注意

### 4.4 正确做法(测开必知)

**三个解决方案**:

1. **本地测试统一用 `127.0.0.1`,不用 `localhost`** ⭐ 最简单
2. 在 hosts 文件里把 `::1 localhost` 那行注释掉(禁用 IPv6 解析)
3. 在请求库里强制走 IPv4(配置复杂,不推荐)

### 4.5 这个坑教会的更大道理

**今天我们经历了两次完全独立的踩坑,得到同一个结论**:

| 第一次踩坑 | 第二次踩坑 |
|---|---|
| asyncio vs threading 对比 | 多线程健康检查器 |
| 发现 asyncio 比 threading 快 8 倍 | 发现总耗时 15 秒 |
| 误判:"asyncio 真厉害" | 误判:"3 并发没生效" |
| **真相**:测试环境是瓶颈 | **真相**:Windows localhost 解析是瓶颈 |

> **核心教训**:**测试结果反常时,先怀疑测试环境,不要急着相信结论。**

### 4.6 一个反思:权威也会错

我作为陪你学的角色,**今天误判了两次**:
- 把第一次的差距归因于"ThreadingHTTPServer 设计差"
- 第二次猜"队列阻塞 / 串行启动"

而**真相是你自己改 `localhost` → `127.0.0.1` 发现的**(可能不是有意为之,但结果暴露了真相)。

> **金句**:"不要 100% 相信任何'权威分析'——包括导师、文档、StackOverflow。**真相只在数据里**。"

---

## 五、增量开发方法论

> **这一节不是关于并发的,是关于"怎么写复杂代码不混乱"的元方法。**

### 5.1 今天经历的真实"乱"

第一次尝试写多线程项目时,代码长这样(摘要):

```python
def producer_q():
    q.put(url for url in urls)    # ❌ bug:put 了生成器对象

def customer_q():
    while True:
        item = q.get()
        if item is SENTINEL:
            print(f"{结束了}")    # ❌ bug:f-string 语法错

def result_q():
    res = q.                      # ❌ 写到一半断了

def main():
    t = threading.Thread(target=customer_q)
    t.start()                      # ❌ 只启动了 1 个组件
    t.join()
```

**当时的感受**:"思路有点乱,写的乱七八糟的。"

### 5.2 乱的真正原因不是知识不够

**是设计步骤跳了**——上来就写代码,**没有先画数据流图**。

> **专业程序员写并发代码,90% 的时间花在设计上,10% 才在键盘上。**

### 5.3 正确的步骤:分 4 步,每步跑通再走下一步

| 步骤 | 范围 | 验证目标 |
|---|---|---|
| Step 1 | 只写 producer + 1 个 print 验证 | URL 真的被 put 进去了 |
| Step 2 | 加 1 个 worker | 单 worker 能消费 |
| Step 3 | 扩展到 3 个 worker + 异常处理 | 真并发 + 异常被捕获 |
| Step 4 | 加 result_queue + reporter + 统计 | 完整流水线 |

**每一步跑通了再走下一步**。不要想着"一次写完"。

### 5.4 这个方法的英文名:**Incremental Development(增量开发)**

工业界标准做法,**写复杂系统不混乱的唯一办法**。

### 5.5 不只是写代码——所有"感觉很乱"的场景都适用

- 学习一个大主题感觉抓不住重点 → 拆成小块,每块吃透再下一块
- 准备面试感觉范围太广 → 一个考点一个考点准备
- 写技术文档无从下手 → 先列大纲,再填每一节

---

## 六、面试问答模板(衔接版)

### 6.1 "asyncio 的 gather 有什么坑?"

> "gather 有两个固有局限:
> 
> 第一,它必须等所有任务完成才返回,不能边完成边处理。这种场景应该用 `as_completed` 或 `asyncio.wait(FIRST_COMPLETED)`。
> 
> 第二,默认行为下如果一个任务抛异常,gather 会立刻把异常抛给调用者,但**其他任务不会被自动取消**,会继续在后台跑——这就是有名的 fire-and-forget 陷阱。如果想容错可以用 `return_exceptions=True`,如果是 Python 3.11+ 可以用 `TaskGroup`,它会在异常时自动取消所有兄弟任务。"

### 6.2 "task.cancel() 之后任务会立刻停止吗?"

> "不会。cancel() 是**协作式**的——它只是给任务发一个信号,任务在**下一个 await 点**才会抛出 `CancelledError`。如果任务没有 await 点(比如纯 CPU 循环),cancel() **完全无效**——任务会一直跑完。
> 
> 而且 asyncio 是单线程事件循环,一个不让出的 CPU 任务会**冻住整个事件循环**——其他任务的 sleep、timeout、cancel 都会失去时间精度。这是 asyncio 最大的陷阱之一。
> 
> 修复方式:CPU 密集任务必须用 multiprocessing,不能用 asyncio 或 threading(GIL)。"

### 6.3 "怎么实现一个生产者-消费者?消费者怎么优雅退出?"

> "用 `queue.Queue` 做缓冲。生产者 put,消费者 get,Queue 内部已经处理了所有同步问题,不需要手写锁。
> 
> 优雅退出用**毒丸模式**——生产者结束后 put 一个特殊值(通常是 None),消费者拿到就 break。**关键细节**:有 N 个消费者就要 put N 个毒丸,因为每个消费者只会消费一个。
> 
> 多级流水线场景下(比如 worker → reporter),reporter 的毒丸应该**由主线程在 worker 全部 join 完之后发**,不能由 worker 发——因为 worker 不知道'我是不是最后一个'。"

### 6.4 "你做性能测试时遇到反常数据,怎么排查?"

> "我会按这个流程:
> 
> **第一步**:不要相信单次跑数,先取多轮的中位数和 P95。
> 
> **第二步**:把请求拆分计时——比如把网络时间和 CPU 解析时间分开统计,看瓶颈在哪段。
> 
> **第三步**:对照数据和理论值。比如 mock 服务 sleep 100ms,3 并发 20 个请求理论 ~0.7s,如果实测 15s,**差距 20 倍肯定不是抖动,一定有系统性问题**。
> 
> **第四步**:**先怀疑测试环境,不要急着改业务代码**。常见的坑有:
> - 测试工具单线程或并发能力差(比如 Python `HTTPServer` 是单线程的)
> - DNS 解析问题(比如 Windows 上 `localhost` 走 IPv6 失败回退)
> - 测试机网卡或带宽受限
> - 共享资源锁竞争
> 
> 我在本地测试时踩过一个具体的坑——Windows 上用 `localhost` 比 `127.0.0.1` 慢 12 倍,因为先走 IPv6 解析失败再回退 IPv4。**所以本地测试我现在统一用 `127.0.0.1`**。"

### 6.5 "增量开发是什么?为什么重要?"

> "增量开发是先实现最简单能跑的版本,跑通后再一点点加复杂度——每一步都保证可运行、可验证。
> 
> 它重要是因为人脑的工作记忆有上限。复杂系统一次性写出来必然乱——不是技术问题,是认知负荷问题。把它拆成多步,每步只关注一件事,代码自然就清晰了。
> 
> 我最近写一个多线程健康检查器时亲身体验过——第一次想一口气写完,结果代码乱七八糟。改成分 4 步走(producer → 1 worker → 3 worker + 异常 → 加 reporter + 统计),每步跑通再下一步,**反而比一口气写更快**,而且 bug 极少。"

---

## 七、完整可运行代码

### 7.1 mock 服务(单独的文件 mock_server.py)

```python
import time
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(0.1)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"id": 1}')
    def log_message(self, *args):
        pass

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8000), Handler)
    print("Mock 服务已启动: http://127.0.0.1:8000")
    server.serve_forever()
```

### 7.2 多线程健康检查器(完整版)

```python
import threading
import queue
import requests
import time
from collections import Counter

# ===== 配置 =====
SENTINEL = None
NUM_WORKERS = 3
# ⭐ 关键:用 127.0.0.1 不用 localhost,避免 Windows IPv6 解析坑
urls = [f"http://127.0.0.1:8000/users/{i}" for i in range(20)]

# ===== 共享资源 =====
task_queue = queue.Queue()
result_queue = queue.Queue()
session = requests.Session()    # 全局复用,避免重复 TCP 握手


# ===== 三个角色 =====
def producer():
    """生产者:put URL 到任务队列,完后发毒丸"""
    for url in urls:
        task_queue.put(url)
    # N 个 worker 需要 N 个毒丸
    for _ in range(NUM_WORKERS):
        task_queue.put(SENTINEL)


def worker():
    """工作线程:get URL → 请求 → put 结构化结果"""
    name = threading.current_thread().name
    while True:
        url = task_queue.get()
        if url is SENTINEL:
            break
        
        t0 = time.perf_counter()
        try:
            resp = session.get(url, timeout=5)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            result = {
                "url": url,
                "status": "ok",
                "code": resp.status_code,
                "elapsed_ms": elapsed_ms,
            }
        except requests.exceptions.Timeout:
            result = {
                "url": url,
                "status": "timeout",
                "elapsed_ms": 5000,
            }
        except requests.exceptions.RequestException as e:
            result = {
                "url": url,
                "status": "error",
                "error": str(e),
            }
        
        result_queue.put(result)


def reporter():
    """报告线程:从结果队列消费,实时打印 + 最终统计"""
    stats = Counter()
    results = []
    
    while True:
        item = result_queue.get()
        if item is SENTINEL:
            break
        
        results.append(item)
        stats[item['status']] += 1
        
        # 实时打印
        if item['status'] == 'ok':
            print(f"✅ {item['url']} → {item['code']} ({item['elapsed_ms']:.0f}ms)")
        elif item['status'] == 'timeout':
            print(f"⏱️  {item['url']} → 超时")
        else:
            print(f"❌ {item['url']} → {item['error']}")
    
    # 最终统计
    print("\n========== 最终报告 ==========")
    print(f"总数: {len(results)}")
    print(f"成功: {stats['ok']}")
    print(f"超时: {stats['timeout']}")
    print(f"错误: {stats['error']}")


# ===== 主流程 =====
def main():
    t0 = time.perf_counter()
    
    p = threading.Thread(target=producer, name="producer")
    workers = [threading.Thread(target=worker, name=f"worker-{i}") 
               for i in range(NUM_WORKERS)]
    r = threading.Thread(target=reporter, name="reporter")
    
    # ⭐ 先全部 start——保证真正并发
    p.start()
    for w in workers:
        w.start()
    r.start()
    
    # 等 producer 和 worker 完成
    p.join()
    for w in workers:
        w.join()
    
    # ⭐ 关键:所有 worker 完成后,主线程给 reporter 发毒丸
    result_queue.put(SENTINEL)
    r.join()
    
    print(f"\n总耗时: {time.perf_counter() - t0:.2f}s")


if __name__ == "__main__":
    main()
```

### 7.3 运行方式

```bash
# 终端 1:启动 mock 服务
python mock_server.py

# 终端 2:启动健康检查器
python health_checker.py
```

**预期输出**(20 个 URL + 3 并发 + 100ms sleep):

```
✅ http://127.0.0.1:8000/users/0 → 200 (105ms)
✅ http://127.0.0.1:8000/users/1 → 200 (102ms)
✅ http://127.0.0.1:8000/users/2 → 200 (108ms)
...
========== 最终报告 ==========
总数: 20
成功: 20
超时: 0
错误: 0

总耗时: 1.20s
```

---

## 八、给自己的话

### 8.1 今天真正学到了什么

不只是 asyncio / threading 的 API,而是:

- **奶茶店心智模型** —— 把抽象概念翻译成生活直觉
- **增量开发** —— 写复杂代码不混乱的元方法
- **数据驱动调试** —— 不要猜,先测,看数据反推真相
- **测试环境怀疑论** —— 反常数据出现时,先怀疑测试环境
- **结构化思考** —— 三层角色分工、双队列、多级毒丸

### 8.2 简历亮点

这个 50 行小项目,完全可以写进简历:

> "独立实现基于生产者-消费者模式的多线程 HTTP 健康检查工具,支持
> 多级队列、毒丸优雅退出、结构化结果汇总。在性能测试中识别 Windows
> 上 `localhost` 的 IPv6 解析陷阱(延迟从 15s 优化至 1.2s,**12 倍提升**)。"

**这一句**比"熟练掌握 Python 多线程"有说服力 100 倍——因为它有具体场景、具体方法、具体数字、具体洞察。

### 8.3 真正的下一步

按未完成清单,推荐顺序:

1. **multiprocessing 实战** —— CPU 密集场景的最后一块拼图
2. **pytest-asyncio** —— 测开真正用得到的"在 pytest 里写异步测试"
3. **`asyncio.Queue`** —— 协程版的生产者消费者(跟今天学的 queue.Queue 形成对称)

### 8.4 学习方法的迁移

今天用的这套方法——**奶茶店模型 → 亲手实验 → 解读数据 → 用自己的话讲一遍**——可以**完全照搬**到你接下来准备的所有科目:

- 计算机网络
- 数据库
- 操作系统
- Linux 命令
- 测开框架原理

**这套方法本身,比任何一个具体知识点都值钱。**

---

## 附录:今天的学习路径

```
起点:thread 项目"思路有点乱,写的乱七八糟"
   ↓
回退到设计:先画数据流图
   ↓
识别 3 个角色 + 2 个队列
   ↓
Step 1.5:1 producer + 1 worker → 跑通(失败,没启动 mock 服务)
   ↓
验证异常处理工作正常
   ↓
Step 3:扩展到 3 worker → 总耗时 15 秒(诡异)
   ↓
我误判:"先 start 再 join 可解决"
   ↓
你按建议改 → 还是 15 秒 → 我的猜测错了
   ↓
加诊断日志:线程名 + 单次耗时
   ↓
发现每个请求稳定 2150ms,3 worker 真并发
   ↓
你独立改 localhost → 127.0.0.1 → 总耗时 1.2 秒
   ↓
真凶大白:Windows IPv6 解析陷阱
   ↓
Step 4:加 reporter + 统计 → 完整版跑通
   ↓
终点:50 行生产级多线程程序 + 一次"亲手破案"的工程经验
```

---

*本笔记衔接 Part 1(基础并发)和 Part 2(线程安全),三份合在一起,
覆盖测开面试 80%+ 的并发考点,以及生产级代码的核心实践。*
# Python 并发学习笔记 Part 4:multiprocessing + pytest-asyncio

> 学习日期:2025-05-23
> 主题:multiprocessing 实战、pytest-asyncio 异步测试
> 衔接:Part 1-3 的续篇,并发知识体系收官

---

## 目录

- [一、multiprocessing 核心](#一multiprocessing-核心)
- [二、pytest-asyncio 异步测试](#二pytest-asyncio-异步测试)
- [三、并发知识体系总览](#三并发知识体系总览)
- [四、面试问答模板](#四面试问答模板)
- [五、关键代码模板](#五关键代码模板)

---

## 一、multiprocessing 核心

### 1.1 心智模型:开分店

```
线程(threading):                    进程(multiprocessing):

┌─────────────────────┐             ┌──────────┐  ┌──────────┐
│  1 家店              │             │  分店 1   │  │  分店 2   │
│  员工共用 1 个厨房    │             │  自己的厨房│  │  自己的厨房│
│  → 抢资源要加锁      │             │  自己的收银│  │  自己的收银│
└─────────────────────┘             └──────────┘  └──────────┘
                                    → 完全独立,不用加锁
                                    → 分店间传数据要"快递"(pickle 序列化)
```

三个关键推论:

1. **不用加锁** —— 每个进程有独立内存
2. **真并行** —— 4 个进程跑在 4 个 CPU 核上,同时计算
3. **代价** —— 进程间传数据要 pickle 序列化,比线程共享内存慢得多

### 1.2 两种 API:Pool vs ProcessPoolExecutor

```python
# 方式 1:multiprocessing.Pool(底层,面试常考)
from multiprocessing import Pool
with Pool(4) as pool:
    results = pool.map(compute, chunks)

# 方式 2:ProcessPoolExecutor(现代包装,API 与 ThreadPoolExecutor 统一)
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(compute, chunks))
```

**两者性能几乎一样**(实测差距 < 3%)。

| | `multiprocessing.Pool` | `ProcessPoolExecutor` |
|---|---|---|
| 所属模块 | `multiprocessing` | `concurrent.futures` |
| API 风格 | 自己的风格 | **跟 ThreadPoolExecutor 统一** |
| 参数名 | `processes=4` | `max_workers=4` |
| `map` 返回 | 列表 | 迭代器 |
| 错误处理 | 较原始 | 更好(Future.exception()) |
| 日常开发 | | ⭐ **优先选这个** |
| 面试 | ⭐ **常考这个** | |

**"秒切"心智模型**:从线程切到进程,只改一个单词:

```python
# I/O 密集:
with ThreadPoolExecutor(max_workers=10) as ex: ...

# CPU 密集:
with ProcessPoolExecutor(max_workers=4) as ex: ...
# 其他代码完全不变
```

### 1.3 实测数据:CPU 密集场景(4 段 × 2500 万次平方和)

```
串行:                8.35s  (基准)
ThreadPoolExecutor:  8.26s  (加速 1.0x) ← GIL,等于没加速
ProcessPoolExecutor: 3.04s  (加速 2.7x) ← 真并行!
multiprocessing.Pool: 2.98s  (加速 2.8x) ← 真并行!
```

**ThreadPoolExecutor 加速 1.0x** = GIL 的铁证:4 线程轮流用一台计算器,跟 1 人没区别。

### 1.4 加速比为什么不到 4x?

| 开销来源 | 说明 |
|---|---|
| 进程启动 | 创建 4 个独立 Python 解释器 |
| pickle 序列化 | 数据传给子进程 + 结果传回主进程 |
| OS 调度 | 4 进程抢 CPU 核 |

> **金句**:"multiprocessing 的加速比不会达到理论值,因为有进程启动和 pickle 序列化开销。最适合'**计算重、数据轻**'的场景。"

### 1.5 反面教材:任务太轻,慢 3365 倍

实测:100 个 `n * n` 的极轻任务:

```
串行:   0.1ms
多进程: 336.5ms
多进程比串行慢 3365 倍!
```

**计算 0.1ms,管理 336ms** —— 大炮打蚊子。

**经验阈值**:单任务计算时间**至少几十毫秒以上**,multiprocessing 才有正收益。

### 1.6 解决"任务太轻"的方法:chunking(分块)

```python
def compute_batch(numbers):
    """把一批任务打包成一个"""
    return [n * n for n in numbers]

data = list(range(1_000_000))
chunk_size = len(data) // 4
batches = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

with Pool(4) as pool:
    results = pool.map(compute_batch, batches)
```

不传 100 万次"算 1 个",传 4 次"算 25 万个"——**减少进程间通信次数**。

### 1.7 三大坑

#### 坑 1:pickle 限制

传给 Pool 的函数必须是**模块顶层定义的**:

```python
# ❌ lambda 不能 pickle
pool.map(lambda x: x*x, data)

# ❌ 局部函数不能 pickle
def main():
    def compute(n): return n*n
    pool.map(compute, data)

# ✅ 模块顶层函数
def compute(n): return n*n
pool.map(compute, data)
```

#### 坑 2:Windows 必须 `if __name__ == '__main__'`

```python
if __name__ == '__main__':
    with Pool(4) as pool:
        pool.map(compute, data)
```

Windows 用 spawn 创建子进程,**会重新 import 模块**。没保护 → 无限递归创建子进程。

#### 坑 3:进程间不能共享普通变量

```python
# ❌ 这样不行:子进程有独立内存,改不了主进程的 counter
counter = 0
def increment():
    global counter
    counter += 1    # 改的是子进程自己的副本

# ✅ 用 multiprocessing.Value 或 Queue 做进程间通信
```

### 1.8 混合场景的处理策略

当一个任务**既有 I/O 又有 CPU**时:

```
步骤 1:从数据库读数据  ← I/O(用 threading 或 asyncio)
          ↓
步骤 2:复杂数学计算    ← CPU(用 multiprocessing)
          ↓
步骤 3:写入结果        ← I/O
```

**分阶段处理,各用各的最优工具**。不要试图用一种方案解决所有问题。

### 1.9 I/O 密集的磁盘陷阱

10 线程并发读 10 个 1GB 文件:
- **SSD** → 有效(SSD 支持并行 I/O)
- **HDD** → 反而更慢(磁头来回寻道 = 磁盘抖动)

> **精准回答**:"取决于磁盘类型。SSD 上 threading 有效;HDD 上多线程并发读反而更慢,应该串行。"

---

## 二、pytest-asyncio 异步测试

### 2.1 核心问题:为什么普通 pytest 测不了 async

```python
async def fetch_user(user_id):
    return {"id": user_id}

def test_fetch_user():
    result = fetch_user(1)     # ← 返回的是 coroutine 对象,不是 dict!
    assert result['id'] == 1   # ❌ TypeError
```

`async def` 不加 `await` 直接调用 → 返回协程对象,不执行。

### 2.2 pytest-asyncio 做的事

> **让你直接写 `async def test_xxx`,pytest 自动帮你驱动事件循环。**

```bash
pip install pytest-asyncio
```

### 2.3 两种使用模式

| 模式 | 配置 | 写法 |
|---|---|---|
| strict(默认) | 不需要 | 每个 async test 加 `@pytest.mark.asyncio` |
| auto(推荐) | `pytest.ini` 里加 `asyncio_mode = auto` | 直接写 `async def test_xxx` |

**推荐 auto 模式**:

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

### 2.4 async fixture

把异步资源(如 HTTP session)提取成 fixture:

```python
# conftest.py
import pytest
import aiohttp

@pytest.fixture(scope="session")
async def session():
    async with aiohttp.ClientSession() as s:
        yield s
    # 整个测试会话结束才关闭
```

**不需要额外装饰器**——pytest-asyncio 看到 `async def` fixture 自动用事件循环驱动。

### 2.5 fixture scope 对异步资源的影响

| scope | 行为 | 适合 |
|---|---|---|
| `"function"`(默认) | 每个测试创建/销毁一次 | 需要完全隔离(数据库写操作) |
| `"session"` | 整个会话共享 | **只读资源**(HTTP session、连接池) |
| `"module"` | 同一文件共享 | 介于两者之间 |

**HTTP session 推荐 `scope="session"`**——无状态,共享不影响隔离。

### 2.6 完整文件结构

```
async_tests/
├── pytest.ini          # asyncio_mode = auto
├── conftest.py         # async fixture: session
├── mock_server.py      # 本地 mock HTTP 服务
└── test_api.py         # 异步测试用例
```

### 2.7 pytest fixture 三要素回顾

#### @pytest.fixture 是依赖注入

```python
@pytest.fixture
def db_connection():
    conn = create_connection()
    yield conn           # ← setup:测试用这个
    conn.close()         # ← teardown:自动清理

def test_query(db_connection):     # ← 参数名 = fixture 名,自动注入
    result = db_connection.execute("SELECT 1")
    assert result == 1
```

- `yield` 之前 = setup(准备)
- `yield` 之后 = teardown(清理)
- scope 参数决定共享范围

#### conftest.py 是 fixture 的自动发现文件

```
project/
├── conftest.py          ← 公共 fixture,所有测试自动可用
├── tests/
│   ├── conftest.py      ← 目录专用 fixture
│   ├── test_user.py     ← 能用两层 conftest 的所有 fixture
│   └── test_order.py
```

**不需要 import**——pytest 自动发现同目录及父目录的 conftest.py。

#### @pytest.mark.parametrize 是参数化

```python
@pytest.mark.parametrize("user_id, expected_name", [
    (1, "Alice"),
    (2, "Bob"),
    (3, "Charlie"),
])
async def test_get_user(session, user_id, expected_name):
    # 自动生成 3 个独立测试用例
    ...
```

---

## 三、并发知识体系总览

经过 Part 1-4,你的并发知识体系完整了:

```
                     Python 并发全景图
                          │
          ┌───────────────┼───────────────┐
          │               │               │
       asyncio        threading      multiprocessing
     (协程/事件循环)    (多线程)        (多进程)
          │               │               │
     ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
     │         │     │         │     │         │
   gather    await  Pool     Lock   Pool    pickle
   as_completed     Executor Queue  Executor chunking
   TaskGroup        Session  RLock
   wait_for         Semaphore
   Semaphore
```

### 选型决策树(最终版)

```
我的瓶颈在哪?
     │
     ├── I/O 密集(网络/磁盘)
     │     │
     │     ├── 并发量 < 几百 → threading + ThreadPoolExecutor
     │     └── 并发量 几千+ → asyncio(前提:生态都是 async 版)
     │
     ├── CPU 密集(计算/解析)
     │     │
     │     ├── 任务重(单任务 > 几十ms) → multiprocessing
     │     └── 任务轻(单任务 < 1ms) → chunking 打包后再 multiprocessing
     │
     └── 混合(I/O + CPU)
           └── 分阶段:I/O 阶段用 threading/asyncio,CPU 阶段用 multiprocessing
```

### 每种方案的"失败场景"(全部亲手验证过)

| 方案 | 用错了会怎样 | 亲测数据 |
|---|---|---|
| asyncio + 同步库 | 阻塞事件循环,退化串行 | `time.sleep` vs `asyncio.sleep` 差 100 倍 |
| threading + CPU 密集 | GIL 导致加速 0 | 加速 1.0x(等于没加速) |
| multiprocessing + 轻任务 | 启动开销远超计算 | 慢 3365 倍 |
| 任何方案 + localhost(Windows) | IPv6 解析拖累 | 慢 12 倍(15s vs 1.2s) |

---

## 四、面试问答模板

### Q1:"multiprocessing 和 threading 的区别?"

> "核心区别是**内存模型**:线程共享内存(需要锁),进程独立内存(需要序列化)。
>
> 线程受 GIL 限制,CPU 密集场景无法加速;进程绕过 GIL,能真正利用多核。但进程的启动和数据传输开销远大于线程。
>
> 选型:I/O 密集用 threading,CPU 密集用 multiprocessing。"

### Q2:"Pool 和 ProcessPoolExecutor 怎么选?"

> "两者底层都是 multiprocessing,性能几乎一样。ProcessPoolExecutor 的 API 跟 ThreadPoolExecutor 统一,错误处理更好,日常开发优先用。Pool 更底层,有 `apply_async` 等灵活接口,面试常考。"

### Q3:"multiprocessing 有什么坑?"

> "三个常见坑:
>
> 第一,pickle 限制——传给进程池的函数必须是模块顶层定义的,lambda 和局部函数不能 pickle。
>
> 第二,Windows 必须用 `if __name__ == '__main__'` 保护,否则会无限递归创建子进程。
>
> 第三,任务太轻反而更慢——我做过实测,100 个极轻任务用多进程反而慢了 3000+ 倍,因为启动和序列化开销远超计算。解决方法是 chunking,把小任务打包成大批次。"

### Q4:"怎么用 pytest 测异步代码?"

> "用 pytest-asyncio 插件。配置 `asyncio_mode = auto` 后,直接写 `async def test_xxx`,pytest 自动用事件循环驱动。
>
> 异步资源(如 aiohttp session)用 async fixture 管理,`yield` 前后分别是 setup 和 teardown。HTTP session 这种无状态资源推荐用 `scope='session'`,整个测试会话共享一个,避免重复创建连接。"

---

## 五、关键代码模板

### 5.1 multiprocessing.Pool 基本用法

```python
from multiprocessing import Pool

def compute(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

if __name__ == '__main__':
    chunks = [25_000_000] * 4
    with Pool(4) as pool:
        results = pool.map(compute, chunks)
    print(results)
```

### 5.2 ProcessPoolExecutor(与 ThreadPoolExecutor 秒切)

```python
from concurrent.futures import ProcessPoolExecutor

# 只需把 ThreadPoolExecutor 改成 ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(compute, chunks))
```

### 5.3 chunking 优化轻任务

```python
def compute_batch(numbers):
    return [n * n for n in numbers]

data = list(range(1_000_000))
chunk_size = len(data) // 4
batches = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

with Pool(4) as pool:
    results = pool.map(compute_batch, batches)
flat = [x for batch in results for x in batch]
```

### 5.4 pytest-asyncio 完整测试套件

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

```python
# conftest.py
import pytest
import aiohttp

@pytest.fixture(scope="session")
async def session():
    async with aiohttp.ClientSession() as s:
        yield s
```

```python
# test_api.py
import asyncio

BASE_URL = "http://127.0.0.1:8000"

async def test_status_code(session):
    async with session.get(f"{BASE_URL}/users/1") as resp:
        assert resp.status == 200

async def test_response_body(session):
    async with session.get(f"{BASE_URL}/users/1") as resp:
        data = await resp.json()
        assert 'id' in data

async def test_concurrent_requests(session):
    urls = [f"{BASE_URL}/users/{i}" for i in range(50)]

    async def fetch(url):
        async with session.get(url) as resp:
            return resp.status

    results = await asyncio.gather(*[fetch(url) for url in urls])
    assert all(status == 200 for status in results)
```

---

## 附录:四份笔记的完整索引

| 笔记 | 核心内容 |
|---|---|
| **Part 1** | asyncio 骨架、Semaphore、gather、GIL、性能测试方法论 |
| **Part 2** | Lock、RLock、Queue、生产者-消费者、毒丸模式 |
| **Part 3** | 任务编排(4 种 API)、协程取消/超时、多线程实战项目、Windows IPv6 大坑 |
| **Part 4** | multiprocessing 实战、pytest-asyncio、并发知识体系总览 |

**四份合在一起 = 测开面试并发方向的完整知识库。**

---
