# 图论学习笔记（Python · 面试导向）

> 五课体系：**建图 → DFS/BFS → 拓扑排序 → 并查集 → Dijkstra**
> 一句话总纲：**图论所有算法，剥到最里面都是 DFS 和 BFS 两条腿。换个"邻居"的定义，就是一道新题。**

---

## 目录

1. [第一课：图的概念与存储](#第一课图的概念与存储)
2. [第二课：DFS 与 BFS](#第二课dfs-与-bfs)
3. [第三课：拓扑排序](#第三课拓扑排序)
4. [第四课：并查集](#第四课并查集)
5. [第五课：Dijkstra 最短路](#第五课dijkstra-最短路)
6. [总复习：地图 · 决策树 · 陷阱清单](#总复习)
7. [刷题路线](#刷题路线)

---

## 第一课：图的概念与存储

### 1.1 图的本质

一句话：**一堆顶点（vertex），加上顶点之间的连线（边 edge）。**

三组核心区分：

| 区分 | 说明 | 例子 |
|---|---|---|
| **有向 / 无向** | 边是否单向 | 无向=微信好友；有向=微博关注 |
| **带权 / 无权** | 边上有没有数字 | 无权=通不通；带权=距离/费用/时间 |
| **度** | 一个点连了几条边 | 有向图分**入度**（指向我的）和**出度**（我指向的） |

> 面试里 90% 的题是 **有向/无向 + 无权**，用 BFS/DFS 就能打穿。

### 1.2 三种存储方式

以这个无向图为例：

```
0 --- 1
|     |
2 --- 3
```

**① 邻接矩阵** —— `M[i][j] = 1` 表示 i、j 有边

```python
M = [
    [0, 1, 1, 0],   # 0 连了 1 和 2
    [1, 0, 0, 1],   # 1 连了 0 和 3
    [1, 0, 0, 1],   # 2 连了 0 和 3
    [0, 1, 1, 0],   # 3 连了 1 和 2
]
```
- 查 i、j 是否有边：**O(1)**
- 空间：**O(V²)**，点多会爆炸
- 无向图矩阵一定沿对角线**对称**（可用来检查存错没）

**② 邻接表** —— 每个点存一个"邻居列表"（**面试 99% 用这个**）

```python
from collections import defaultdict

graph = defaultdict(list)
edges = [(0,1), (0,2), (1,3), (2,3)]
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)   # 无向图加两次！有向图只加一次
# graph = {0:[1,2], 1:[0,3], 2:[0,3], 3:[1,2]}
```
- 空间：**O(V + E)**，稀疏图省太多
- 遍历一个点的邻居：**O(度数)**

**③ 边列表** —— 就是 `[(0,1), (0,2), ...]`，并查集和 Kruskal 直接吃这个格式。

### 1.3 选哪个

| | 邻接矩阵 | 邻接表 |
|---|---|---|
| 空间 | O(V²) | O(V+E) |
| 查 u→v 是否有边 | O(1) | O(度) |
| 遍历 u 的邻居 | O(V) | O(度) |
| 适合 | 稠密图、点少 | **稀疏图、绝大多数题** |

> **建图肌肉记忆**：LeetCode 通常给你 `edges = [[0,1],[1,2]]`，第一步永远是**转成邻接表**。

### 1.4 ⚠️ 陷阱：孤立顶点

`graph` 从 `edges` 长出来，**没出现在任何边里的顶点不会进 dict**。而 `defaultdict` 更阴险：`graph[5]` 一查就悄悄创建空列表。

**正解**：需要遍历所有顶点时，用 `range(n)`，别用 `for v in graph`。更稳的建图写法：

```python
graph = [[] for _ in range(n)]   # 直接开好 n 个槽，杜绝孤立点问题（面试推荐）
```

> 图**不一定连通**，可能有互不相连的"孤岛"。凡是遍历所有顶点，用 `range(n)`。

---

## 第二课：DFS 与 BFS

### 2.1 两种走法的直觉

想象在迷宫里找出口：

- **DFS（深度优先）**：一条路走到黑，撞墙再退回岔路口 → **递归 / 栈**
- **BFS（广度优先）**：像水波纹一圈圈扩散，先看一步能到的，再看两步的 → **队列**

> **极其重要的结论**：
> - **BFS 在无权图上，第一次到达某点走的一定是最短路径**（按层扩散，第 k 层 = 距起点 k 步）
> - **DFS 不保证最短**，只保证"能到"
>
> 看到「最少步数 / 最短路径 / 最少操作」→ **无脑 BFS**

### 2.2 核心区别：visited

树的遍历不需要 visited（无环）；**图有环，不标记就死循环**。

> **图的遍历 = 树的遍历 + visited 集合。** 就这一个区别。

### 2.3 DFS 代码

```python
# 递归版 —— 面试首选
def dfs(u):
    visited.add(u)
    # 访问 u（业务逻辑放这）
    for v in graph[u]:
        if v not in visited:
            dfs(v)

visited = set()
dfs(0)
```

```python
# 迭代版 —— 数据量大怕爆栈时用（Python 递归深度默认 1000）
def dfs_iter(start):
    visited = set()
    stack = [start]
    while stack:
        u = stack.pop()              # pop() 从尾部弹 = 栈
        if u in visited:
            continue
        visited.add(u)               # ⚠️ 弹出时标记
        for v in graph[u]:
            if v not in visited:
                stack.append(v)
```

> 迭代版 `visited.add` 放在**弹出时**——同一点可能被多次压栈，靠 `if u in visited: continue` 兜底。

### 2.4 BFS 代码（背下来）

```python
from collections import deque

def bfs(start):
    visited = {start}                # ⚠️ 入队时就标记
    q = deque([start])
    while q:
        u = q.popleft()              # popleft() 从头部弹 = 队列
        for v in graph[u]:
            if v not in visited:
                visited.add(v)       # ⚠️ 在这里标记，不是出队时
                q.append(v)
```

> **致命细节**：BFS 必须在**入队时**标记 visited，不能出队时标记。否则一个点被多个邻居同时塞进队列，复杂度退化。
> （DFS 迭代版可以出栈时标记，因为有 continue 兜底；**BFS 绝对不行**。）

### 2.5 BFS 分层写法（求最短距离必用）

```python
def bfs_shortest(start, target):
    visited = {start}
    q = deque([start])
    step = 0
    while q:
        size = len(q)                # 🔑 先固定当前层的点数（循环里 len 会变）
        for _ in range(size):        # 🔑 把这一层全处理完
            u = q.popleft()
            if u == target:
                return step
            for v in graph[u]:
                if v not in visited:
                    visited.add(v)
                    q.append(v)
        step += 1                    # 🔑 一层处理完，步数 +1
    return -1
```

> `size = len(q)` 是灵魂：**必须先存下当前长度**，因为循环里会往队尾加新点。

### 2.6 网格题：隐式图

网格就是一张图——**每个格子是顶点，上下左右是邻居**，不用真的建邻接表。

**网格 DFS 三件套**：

```python
def dfs(r, c):
    # ① 守卫放在函数入口：越界 or 非目标 → 立刻 return
    if r < 0 or r >= m or c < 0 or c >= n or grid[r][c] != 1:
        return 0
    grid[r][c] = 0                   # ② 原地标记（沉岛法，复用 grid 当 visited）
    # ③ 四方向递归
    return 1 + dfs(r-1,c) + dfs(r+1,c) + dfs(r,c-1) + dfs(r,c+1)
```

- **方向数组** `[(-1,0),(1,0),(0,-1),(0,1)]`：网格题标配，见到条件反射
- **原地标记**：走过的 `1` 改成 `0`，省掉 visited 集合
- **主循环**触发几次 DFS = 有几个连通块（每次 DFS 会把整块"染色"）

### 2.7 DFS vs BFS 对照表

| | DFS | BFS |
|---|---|---|
| 容器 | 系统调用栈（隐式） | `deque` 队列（显式手搓） |
| 守卫位置 | 函数入口（进门再查） | 入队之前（门口就查） |
| 主循环要不要 `if` | 不用（有入口守卫） | **必须要**（无守卫） |
| 标记时机 | 走到就标记 | **入队就标记**（非出队） |
| 计数方式 | 返回值向上汇总（"回来数"） | 入队时当场 +1（"进去数"） |
| 代码长度 | 短 | 长 |
| 栈溢出 | 有风险（深度 >1000 爆） | 无风险（深度恒为 1） |
| 求最短路 | ❌ 不保证 | ✅ 保证 |

> 面试追问"网格 10⁶ 格怎么办？"→ 标准答案：**改用 BFS**（避免递归爆栈）。

### 2.8 复杂度

两者均为 **时间 O(V + E)，空间 O(V)**。每点进出一次，每边看一次。

### 2.9 多源 BFS（994 腐烂橘子）

**所有起点一次性全塞进队列**，其余不变。分钟数 = BFS 层数。

```python
from collections import deque

def orangesRotting(grid):
    m, n = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    # ① 所有腐烂橘子入队 + 统计新鲜橘子
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                q.append((r, c))     # 多源起点
            elif grid[r][c] == 1:
                fresh += 1
    if fresh == 0:                   # ② 边界：本来没有新鲜橘子 → 0 分钟
        return 0
    minutes = 0
    # ③ 分层 BFS
    while q:
        size = len(q)
        for _ in range(size):
            r, c = q.popleft()
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                    grid[nr][nc] = 2 # 传染 = 标记 visited
                    fresh -= 1
                    q.append((nr, nc))
        minutes += 1
    # ④ 还有新鲜的没烂完 → 传染不到
    return minutes - 1 if fresh == 0 else -1
```

> **为什么 `minutes - 1`**：最后一批腐烂橘子出队时四周已无新鲜橘子，那一轮空转仍 `+= 1`，需减掉。
> 替代写法避免减 1：`while q and fresh > 0:`（新鲜的没了就停）。

---

## 第三课：拓扑排序

### 3.1 解决什么

> **一堆事情有先后依赖，能不能排出合法执行顺序？** 同时**检测有没有环**（成环则无解）。

`B → A` 表示"B 完成后才能做 A"（B 是 A 的前置）。选课、编译依赖、任务调度都是它。

### 3.2 直觉：剥洋葱（Kahn 算法）

**入度 = 还没满足的前置条件数量。**

1. 找所有**入度为 0** 的点（无前置，可立刻执行）
2. 执行并"删掉"它们
3. 它们指向的邻居入度 **-1**，可能产生新的入度为 0 的点
4. 循环，直到没有入度为 0 的点

> **本质就是 BFS**，队列里放"入度为 0 的点"。
> **排出的点数 < 总点数 → 有环**（成环的点入度永远减不到 0）。

### 3.3 代码模板（背下来）

```python
from collections import deque

def topo_sort(n, edges):
    # edges = [[u, v], ...] 表示 u → v
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    # ① 建图 + 统计入度
    for u, v in edges:
        graph[u].append(v)           # 有向图只加一次
        indegree[v] += 1
    # ② 入度为 0 的点入队（多源起点）
    q = deque(i for i in range(n) if indegree[i] == 0)
    order = []
    # ③ BFS 剥洋葱
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:     # ⚠️ 减到 0 才入队
                q.append(v)
    # ④ 校验
    return order if len(order) == n else []   # 空列表 = 有环
```

### 3.4 三个必看的坑

1. **有向图只 `append` 一次**（写两次就变无向图了）
2. **方向别搞反**：LeetCode 207 给 `[a, b]` = "学 a 前先学 b" = `b → a`
   ```python
   for a, b in prerequisites:
       graph[b].append(a)      # b → a
       indegree[a] += 1
   ```
3. **减到 0 才入队**，不是减一次就入队（`if indegree[v] == 0`）

### 3.5 DFS 版（三色标记法，面试可能追问）

```python
def canFinish(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]
    for u, v in prerequisites:
        graph[v].append(u)
    # 0=没访问 1=正在访问(在当前递归路径上) 2=已完成
    state = [0] * numCourses
    def dfs(u):
        if state[u] == 1:            # 🔑 撞见"正在访问"→ 转回来了 → 有环
            return False
        if state[u] == 2:            # 已确认安全，剪枝
            return True
        state[u] = 1                 # 进入递归路径
        for v in graph[u]:
            if not dfs(v):
                return False
        state[u] = 2                 # 这条路走完，安全
        return True
    return all(dfs(i) for i in range(numCourses))
```

> **灰色(1) 是灵魂**：表示"还在当前递归栈里"。撞见灰点 = 绕一圈回到自己 = 环。
> 撞见黑色(2) 只是"以前走过"，**不是环**（新手最易混）。
> 面试建议：默认写 Kahn（直观、不爆栈、能输出顺序），DFS 版能讲原理即可。

### 3.6 与 BFS 的同构

| | 994 腐烂橘子 | 拓扑排序 |
|---|---|---|
| 多源起点 | 所有 `2` 入队 | 所有 `indegree==0` 入队 |
| 出队后 | 传染邻居 | 邻居 `indegree -= 1` |
| 邻居何时入队 | `grid==1` | `indegree==0` |
| 最后校验 | `fresh == 0`? | `len(order)==n`? |

> **"入度减到 0" 就是拓扑排序版的 visited。** 复杂度 O(V + E)。

---

## 第四课：并查集

### 4.1 解决什么

> **这两个点是不是在同一个连通块里？** 尤其是**动态加边**场景。

BFS/DFS 也能判连通，但**每加一条边就重跑一次 O(V+E)** 太慢。并查集能做到近似 **O(1)**。

### 4.2 直觉：认老大

每个连通块是一个帮派，有一个老大（代表元）。

- `find(x)`：查 x 的老大（一路往上问，直到自己是自己老大）
- `union(x, y)`：让两个帮派的老大合并
- **x、y 连通 ⟺ `find(x) == find(y)`**

用 `parent` 数组存"上级是谁"，初始 `parent[i] = i`（各自为王）。

### 4.3 两个优化（必须会）

**① 路径压缩** —— 找老大路上顺手把每个人直接挂到老大底下（**灵魂一行**）

```python
def find(self, x):
    if self.parent[x] != x:
        self.parent[x] = self.find(self.parent[x])   # 递归 + 直接改指向
    return self.parent[x]
```

**② 按秩合并** —— 矮树挂到高树下，防止树长高

两个优化都上 → **O(α(n))**，α 是反阿克曼函数，实践中就是 O(1)。

### 4.4 完整模板（面试直接默写）

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n                       # 连通块数量

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # 路径压缩
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False                     # 已连通（这条边会成环）
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx                  # 保证 rx 更高
        self.parent[ry] = rx                 # 矮的挂高的下面
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.count -= 1                      # 🔑 合并一次，连通块 -1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)
```

> **`self.count` 很有用**："数连通块个数"直接 `return uf.count`。

### 4.5 两大用法（所有并查集题都是这俩的变体）

| | 看什么 | 核心逻辑 | 代表题 |
|---|---|---|---|
| **数连通块** | `uf.count` | 合并成功 → count -= 1 | 547 省份数量 |
| **判无向环** | `union` 返回值 | 返回 False → 就是成环边 | 684 冗余连接 |

**547 省份数量**（数连通块）：

```python
def findCircleNum(isConnected):
    n = len(isConnected)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):    # 只扫上三角（矩阵对称）
            if isConnected[i][j] == 1:
                uf.union(i, j)
    return uf.count
```

**684 冗余连接**（判环）：

```python
def findRedundantConnection(edges):
    n = len(edges)
    uf = UnionFind(n + 1)            # ⚠️ 节点从 1 开始 → 开 n+1
    for u, v in edges:
        if not uf.union(u, v):       # union 失败 = 已连通 = 成环
            return [u, v]
    return []
```

> **成环判定**：x、y 已连通（本来就有路能互达），再加一条直连边 → 两条路 → 环。

### 4.6 选并查集还是 DFS/BFS

| 场景 | 用什么 |
|---|---|
| 静态图，一次性数连通块 | 都行 |
| **动态加边** + 反复查连通 | **并查集**（DFS 会超时） |
| **判无向图的环** | **并查集** |
| 最小生成树 Kruskal | **并查集**（核心组件） |
| 需要**路径**（不只连不连通） | **BFS/DFS**（并查集不记路径） |

> ⚠️ 并查集**只能判无向图的环**。**有向图判环必须用拓扑排序或 DFS 三色法**，别混。

---

## 第五课：Dijkstra 最短路

### 5.1 为什么 BFS 不够

BFS 求最短路的前提是**每条边长度都是 1**。边有权重时，"步数少 ≠ 权重小"：

```
   A→C 一步(权10)   vs   A→B→C 两步(权 1+1=2，更短)
```

### 5.2 直觉：贪心 + 优先队列

把 BFS 的普通队列换成**最小堆**，每次弹出**当前距起点最近**的点。

> **贪心核心**：已确定的最近点，其最短距离不可能再被改进（**前提：边权非负**）。
> ⚠️ 有负权边必须用 Bellman-Ford / SPFA。

### 5.3 代码模板

```python
import heapq
from collections import defaultdict

def dijkstra(n, edges, start):
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
        # 无向图再加：graph[v].append((u, w))
    dist = [float('inf')] * n
    dist[start] = 0
    heap = [(0, start)]              # (距离, 节点)，距离放前面才能按它排序
    while heap:
        d, u = heapq.heappop(heap)   # 弹出当前最近的点
        if d > dist[u]:              # 🔑 过期数据（懒删除），跳过
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:         # 🔑 松弛：找到更短的路
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
```

### 5.4 三个关键点

1. **`if d > dist[u]: continue`（懒删除）**：同一点可能被多次 push，弹出过期旧数据时直接跳过
2. **元组顺序必须是 `(距离, 节点)`**：`heapq` 按第一个元素排序，反了就错
3. **Dijkstra = 加权版 BFS**：`deque` → `heapq`，"最早入队" → "距离最近"

**复杂度**：O((V + E) log V)

### 5.5 变体：改的只是"怎么算 nd"

| 题 | nd 的算法 |
|---|---|
| 743 网络延迟时间 | `nd = d + w`，答案 `max(dist)` |
| 1631 最小体力消耗 | `nd = max(d, w)`（路径最大值，非求和） |
| 787 K 站中转最便宜 | 状态多一维：堆放 `(费用, 节点, 剩余站数)` |

> 骨架完全不动，只改 nd 的计算方式。

---

## 总复习

### 算法地图

```
                    建图（edges → 邻接表）
                    无向加两次 / 有向加一次
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
      DFS                 BFS               并查集
     递归/栈             队列/deque          parent 数组
        │                  │                  │
   连通块/染色         最短步数(无权)       动态连通性
   所有路径            层序/多源BFS         判无向环
   三色法判环             │               数连通块
                     拓扑排序(BFS+入度)
                     有向图判环/依赖顺序
                          │
                     Dijkstra(BFS+堆)
                     非负权最短路
```

### 决策树（看题选算法）

| 题目关键词 | 用什么 |
|---|---|
| 岛屿 / 连通块 / 染色 / 区域 | **DFS**（代码最短） |
| **最少**步数 / 最短路径（无权） | **BFS** |
| 网格 + "同时"扩散（腐烂/传染） | **多源 BFS** |
| 课程 / 依赖 / 先后顺序 | **拓扑排序** |
| **有向图**判环 | **拓扑排序**（`len(order) < n`） |
| **无向图**判环 | **并查集**（`union` 返回 False） |
| 动态加边 + 反复查连通 | **并查集** |
| 边**有权重** + 最短 | **Dijkstra** |
| 有**负权边** | Bellman-Ford（进阶） |
| 最小生成树 | Kruskal（并查集）/ Prim（堆） |

### ⚠️ 高频陷阱清单

1. 无向图 `append` **两次**，有向图**一次** ← 最常见低级错
2. BFS **入队时**标记 visited，不是出队时
3. BFS 分层：`size = len(q)` 必须**先存下来**
4. 拓扑排序**方向别搞反**（`[a,b]` = 学 a 前先学 b = `b → a`）
5. 并查集节点从 1 开始 → 开 **`n+1`**
6. Dijkstra 堆里放 **`(距离, 节点)`**，顺序不能反
7. 遍历所有点用 **`range(n)`**，别用 `for v in graph`（漏孤立点）
8. 多源 BFS 分层计数最后常**多走一层空转**，注意 `-1`

### 复杂度速查

| 算法 | 时间 | 空间 |
|---|---|---|
| DFS / BFS | O(V + E) | O(V) |
| 拓扑排序 | O(V + E) | O(V + E) |
| 并查集（双优化） | O(α(n)) ≈ O(1) 每次操作 | O(V) |
| Dijkstra | O((V + E) log V) | O(V + E) |

---

## 刷题路线

### 巩固（模板题，限时重做）
- 200 岛屿数量
- 547 省份数量
- 207 / 210 课程表

### 进阶（本周做完）
- 130 被围绕的区域 —— 反向 DFS
- 417 太平洋大西洋水流 —— 双向 DFS
- 1091 二进制矩阵最短路 —— BFS + 八方向
- **127 单词接龙 —— 隐式图 BFS（重点：建图思维）**
- 743 网络延迟时间 —— Dijkstra 模板
- 684 冗余连接 —— 并查集判环
- 990 等式方程可满足性 —— 并查集

### 必刷（面试真·高频）
- 133 克隆图
- 399 除法求值 —— 带权并查集 / DFS
- 787 K 站中转 —— Dijkstra 变体
- 1584 连接所有点的最小费用 —— Kruskal 最小生成树

> **建议先拿下 127 单词接龙**——它逼你完成从"给了图"到"自己发现图（隐式图）"的思维跃迁，那才是图论真正的门槛。

---

*四大件：DFS / BFS / 拓扑排序 / 并查集。掌握后 LeetCode 上约 80% 的图题都能打。*
