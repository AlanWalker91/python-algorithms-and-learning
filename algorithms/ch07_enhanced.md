# 第7章：图

> **本章导读**：图是数据结构的"终极形态"——树是有父子约束的特殊图，链表是退化的线性图，而图可以表达任意的多对多关系。社交网络、地图导航、任务依赖、网页链接……现实世界中最复杂的关系系统都需要用图来建模。
>
> **学习路径**：图的基本概念 → 两种表示方式（矩阵/邻接表）→ BFS（广度优先）→ DFS（深度优先）→ Dijkstra 最短路径 → 拓扑排序 → 最小生成树
>
> **核心问题**：BFS 和 DFS 都能遍历图，它们有什么本质区别？——BFS 用队列按层扩展，天然得到"最短路径"（按跳数）；DFS 用栈深入探索，天然适合"连通性"和"拓扑排序"。理解这个区别，图算法就掌握了一半。

---

## 7.0 关键术语速查

| 术语 | 英文 | 定义 |
|------|------|------|
| 图 | Graph | 由顶点集合 V 和边集合 E 组成，G=(V,E) |
| 顶点 | Vertex / Node | 图中的基本单元，代表实体 |
| 边 | Edge | 连接两个顶点的关系，代表实体间的联系 |
| 有向图 | Directed Graph (Digraph) | 边有方向，A→B 与 B→A 是不同的边 |
| 无向图 | Undirected Graph | 边无方向，A-B 与 B-A 是同一条边 |
| 权重 | Weight | 边上附带的数值（如距离、代价、时间） |
| 路径 | Path | 顶点序列 v₁→v₂→...→vₙ，相邻顶点间有边 |
| 环 | Cycle | 起点和终点相同的路径（自环：v→v） |
| 有向无环图 | DAG | 有向图中不存在任何环，适合建模依赖关系 |
| 度 | Degree | 与某顶点相连的边数；有向图分入度和出度 |
| 入度 | In-degree | 有向图中指向某顶点的边数 |
| 出度 | Out-degree | 有向图中从某顶点出发的边数 |
| 连通 | Connected | 无向图中任意两顶点间都存在路径 |
| 连通分量 | Connected Component | 无向图中极大连通子图 |
| 强连通 | Strongly Connected | 有向图中任意两顶点间互相可达 |
| 邻接矩阵 | Adjacency Matrix | 用 n×n 二维数组表示图，matrix[i][j]=权重 |
| 邻接表 | Adjacency List | 用字典/数组表示图，每个顶点存储邻居列表 |
| BFS | Breadth-First Search | 广度优先搜索，用队列按层扩展 |
| DFS | Depth-First Search | 深度优先搜索，用栈/递归深入探索 |
| 最短路径 | Shortest Path | 两顶点间权重和最小（或跳数最少）的路径 |
| Dijkstra | Dijkstra | 贪心算法，求单源最短路径（不含负权边） |
| 拓扑排序 | Topological Sort | DAG 中将顶点排成线性序列，使依赖项排在前面 |
| 最小生成树 | MST | 连通所有顶点的权重最小的无环子图 |
| Prim | Prim's Algorithm | 从一点出发逐步扩展的 MST 算法 |
| Kruskal | Kruskal's Algorithm | 按边权从小到大贪心选边的 MST 算法 |

---

## 7.1 为什么需要图？

### 树和链表不够用

```
链表：A → B → C → D（一对一，线性）
树  ：A 是 B 和 C 的父节点（一对多，层级）
图  ：A 与 B、C、D 都有关系，B 与 D 也有关系（多对多，任意）

现实问题：
  "从北京到上海，最便宜的机票路线是什么？"
  → 城市=顶点，航线=有向边，票价=权重，求最短路径
  
  "这两个人在社交网络中相差几个朋友圈？"
  → 人=顶点，好友关系=无向边，求最短路径（跳数）
  
  "这批任务有依赖关系，按什么顺序执行？"
  → 任务=顶点，依赖=有向边，求拓扑排序
```

### 图的直观分类

```
按方向：
  无向图：A ─── B（互相可达）
  有向图：A ──▶ B（A能到B，B不一定能到A）

按权重：
  无权图：只关心是否连通（如好友关系）
  带权图：边有数值（如距离、费用）

特殊图：
  DAG（有向无环图）：任务调度、依赖管理
  二分图：两组节点，边只在组间（如用户-商品关系）
  完全图：每两个顶点间都有边，共 n(n-1)/2 条边
```

---

## 7.2 图的两种表示方式

### 7.2.1 邻接矩阵（Adjacency Matrix）

```
用 n×n 的二维数组表示 n 个顶点的图
matrix[i][j] = 权重（或 1）表示 i→j 有边
matrix[i][j] = 0（或 ∞）表示 i→j 无边

示例（有向图：A→B(4), A→C(2), C→B(1), B→D(5)）：

     A    B    C    D
A  [ 0    4    2    0 ]
B  [ 0    0    0    5 ]
C  [ 0    1    0    0 ]
D  [ 0    0    0    0 ]

优点：O(1) 判断两点是否相连，O(1) 更新边权重
缺点：O(V²) 空间，稀疏图（边少）时极度浪费
适用：稠密图（边接近 V² 量级），或需要频繁查询边是否存在
```

### 7.2.2 ⭐ 邻接表（Adjacency List）

```
用字典（或数组）表示，每个顶点对应一个邻居列表

示例（同上有向图）：
{
  'A': [('B', 4), ('C', 2)],
  'B': [('D', 5)],
  'C': [('B', 1)],
  'D': []
}

优点：O(V+E) 空间，稀疏图高效，遍历邻居 O(度)
缺点：判断两点是否相连需要 O(度) 时间
适用：大多数实际场景（现实图通常是稀疏图）
```

```python
from collections import defaultdict, deque

class Graph:
    """
    用邻接表实现图（支持有向/无向，支持权重）
    
    内部结构：
    self.adj = {
        顶点: [(邻居, 权重), (邻居, 权重), ...],
        ...
    }
    """
    
    def __init__(self, directed=True):
        self.adj      = defaultdict(list)   # 邻接表，默认空列表
        self.directed = directed            # True=有向图
    
    def add_vertex(self, v):
        """显式添加顶点（即使没有边）"""
        if v not in self.adj:
            self.adj[v] = []
    
    def add_edge(self, u, v, weight=1):
        """
        添加边 u→v（有向）或 u-v（无向）
        
        无向图：同时添加 u→v 和 v→u
        """
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u].append((v, weight))
        
        if not self.directed:               # 无向图双向添加
            self.adj[v].append((u, weight))
    
    def get_neighbors(self, v):
        """返回 v 的所有邻居 [(neighbor, weight), ...]"""
        return self.adj.get(v, [])
    
    def vertices(self):
        """返回所有顶点"""
        return list(self.adj.keys())
    
    def __str__(self):
        lines = []
        for v in self.adj:
            nb = ', '.join(f"{n}(w={w})" for n, w in self.adj[v])
            lines.append(f"  {v}: [{nb}]")
        return "Graph{\n" + "\n".join(lines) + "\n}"


# ══ 构建示例图 ══
#   A ──4──▶ B
#   │         │
#   2         5
#   ▼         ▼
#   C ──1──▶ B   (C也指向B)
#             │
#             5
#             ▼
#             D

g = Graph(directed=True)
g.add_edge('A', 'B', 4)
g.add_edge('A', 'C', 2)
g.add_edge('C', 'B', 1)
g.add_edge('B', 'D', 5)
g.add_edge('C', 'D', 8)
print(g)
```

---

## 7.3 ⭐ 广度优先搜索（BFS）

### 核心思想

```
从起点出发，先访问距离为1的所有邻居，
再访问距离为2的所有邻居，……
像水波一样向外扩散——"广度"优先。

工具：队列（FIFO）
      先入队的先出队 = 距离近的先处理

关键：必须用 visited 集合记录已访问顶点，防止重复访问（死循环）
```

```
BFS 扩展过程示意（从 A 出发）：

初始：队列=[A]，visited={A}

第1轮：取出A，加入邻居 B,C
  队列=[B,C]，visited={A,B,C}
  ← 这是距离1的所有顶点

第2轮：取出B，加入邻居 D（C已访问）
  队列=[C,D]，visited={A,B,C,D}

第3轮：取出C，邻居D已访问，跳过
  队列=[D]

第4轮：取出D，无未访问邻居
  队列=[]，结束

访问顺序：A → B → C → D
```

```python
def bfs(graph, start):
    """
    广度优先搜索
    
    时间：O(V + E)，每个顶点和每条边都处理一次
    空间：O(V)，visited 集合和队列
    
    适用场景：
    ✅ 无权图中两点间的最短路径（跳数最少）
    ✅ 找所有距离为 k 的顶点
    ✅ 连通分量的探索
    ✅ 二部图检测
    """
    visited = set([start])       # 已访问集合，初始化时就加入起点
    queue   = deque([start])     # 队列，FIFO
    order   = []                 # 记录访问顺序
    
    while queue:
        v = queue.popleft()      # 取队头（最先入队的，距离最近的）
        order.append(v)
        
        for neighbor, _ in graph.get_neighbors(v):
            if neighbor not in visited:
                visited.add(neighbor)      # 入队时就标记，防止重复入队
                queue.append(neighbor)     # 加入队尾
    
    return order


def bfs_shortest_path(graph, start, end):
    """
    BFS 求无权图最短路径（最少跳数）
    
    关键技巧：用字典记录每个顶点的"前驱"
    到达终点后沿前驱反向追踪，即得路径
    
    执行流程（A→D，图：A-B-D, A-C-B）：
    
    dist_from_A:  A=0, B=1(via A), C=1(via A), D=2(via B)
    
    prev:  B←A, C←A, D←B
    
    追踪 D→B→A，反转得 A→B→D
    
    时间：O(V+E)，空间：O(V)
    """
    # prev[v] = v 是从哪个顶点到达的（None 表示起点）
    prev  = {start: None}
    queue = deque([start])
    
    while queue:
        v = queue.popleft()
        
        if v == end:
            # 找到终点，沿前驱链追踪路径
            path = []
            while v is not None:
                path.append(v)
                v = prev[v]
            return path[::-1]   # 反转得到从 start 到 end 的路径
        
        for neighbor, _ in graph.get_neighbors(v):
            if neighbor not in prev:   # 未访问过
                prev[neighbor] = v
                queue.append(neighbor)
    
    return None   # 不可达


# 测试
print(bfs(g, 'A'))                         # ['A', 'B', 'C', 'D']
print(bfs_shortest_path(g, 'A', 'D'))      # ['A', 'B', 'D']
```

---

## 7.4 ⭐ 深度优先搜索（DFS）

### 核心思想

```
从起点出发，沿着一条路一直走到底（无法继续为止），
然后回退（回溯）到上一步，换另一条路继续，
像走迷宫一样——"深度"优先。

工具：递归（系统调用栈）或显式栈

与 BFS 的本质区别：
  BFS：先访问近邻，再访问远邻 → 按距离分层
  DFS：先走到底，再回头     → 按路径深入
```

```python
def dfs_recursive(graph, start, visited=None):
    """
    DFS（递归版）
    
    时间：O(V + E)
    空间：O(V)（visited + 递归调用栈，深度最大 V）
    
    适用场景：
    ✅ 连通性判断
    ✅ 环的检测
    ✅ 拓扑排序
    ✅ 路径存在性问题
    """
    if visited is None:
        visited = set()
    
    visited.add(start)
    order = [start]
    
    for neighbor, _ in graph.get_neighbors(start):
        if neighbor not in visited:
            order.extend(dfs_recursive(graph, neighbor, visited))
    
    return order


def dfs_iterative(graph, start):
    """
    DFS（迭代版，显式栈）
    
    适合递归层次很深时（避免 Python 递归限制）
    
    注意：迭代 DFS 的访问顺序可能与递归 DFS 略有不同
    （因为栈是后进先出，邻居的处理顺序相反）
    """
    visited = set()
    stack   = [start]
    order   = []
    
    while stack:
        v = stack.pop()           # 从栈顶取（LIFO = 深度优先）
        
        if v not in visited:
            visited.add(v)
            order.append(v)
            
            # 注意：逆序压栈，保证处理顺序与递归版一致
            for neighbor, _ in reversed(graph.get_neighbors(v)):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return order


# BFS vs DFS 对比测试（同一张图）
print("BFS:", bfs(g, 'A'))              # 按层：A B C D
print("DFS:", dfs_recursive(g, 'A'))    # 沿路：A B D C
```

### BFS vs DFS 核心对比

| 维度 | BFS | DFS |
|------|-----|-----|
| 数据结构 | 队列（FIFO） | 栈/递归（LIFO） |
| 探索方式 | 按层，由近到远 | 沿路，到底回溯 |
| 空间复杂度 | O(最大层宽) | O(最大深度) |
| 无权最短路 | ✅ 天然最优 | ❌ 不保证 |
| 环检测 | ✅ 可以 | ✅ 更自然 |
| 拓扑排序 | ✅（Kahn算法）| ✅（后序DFS）|
| 典型应用 | 最短路、多源扩散 | 连通分量、回溯搜索 |

---

## 7.5 ⭐ Dijkstra 最短路径算法

### 问题背景

```
BFS 求最短路径：适合无权图（跳数最少）
Dijkstra    ：适合有权图（权重和最小），但要求权重非负

思维实验：
从 A 到 D，有两条路：
  A→B→D：代价 4+5=9
  A→C→B→D：代价 2+1+5=8  ← 更短！

BFS 会走 A→B→D（两跳最短），但忽略了代价
Dijkstra 会走 A→C→B→D（代价最小），这才是正确答案
```

### 贪心策略与执行过程

```
核心思想（贪心）：
每次从"已发现但未确定"的顶点中选择距离最小的，
确定它的最短距离，并更新其邻居的距离。

为什么贪心是正确的？
  一旦选出距离最小的顶点 u，因为所有权重非负，
  以后不可能再找到更短的路径到达 u，
  所以 u 的距离可以确定。

执行流程（图：A→B(4), A→C(2), C→B(1), B→D(5), C→D(8)）：

初始：dist={A:0, B:∞, C:∞, D:∞}，pq=[(0,A)]

步骤1：弹出(0,A)，处理A的邻居
  dist[B] = min(∞, 0+4) = 4
  dist[C] = min(∞, 0+2) = 2
  pq=[(2,C),(4,B)]

步骤2：弹出(2,C)（距离最小），处理C的邻居
  dist[B] = min(4, 2+1) = 3  ← 更新！（经过C到B更短）
  dist[D] = min(∞, 2+8) = 10
  pq=[(3,B),(4,B旧),(10,D)]

步骤3：弹出(3,B)，处理B的邻居
  dist[D] = min(10, 3+5) = 8  ← 更新！
  pq=[(4,B旧),(8,D),(10,D旧)]

步骤4：弹出(4,B旧) → B已确定，跳过

步骤5：弹出(8,D) → 确定！dist[D]=8

最终：dist = {A:0, B:3, C:2, D:8}
      路径 A→D：A→C→B→D，代价=8
```

```python
import heapq

def dijkstra(graph, start):
    """
    Dijkstra 最短路径算法
    
    时间：O((V+E) log V)，优先队列每次操作 O(log V)
    空间：O(V)
    
    ⚠️ 限制：所有边权重必须非负！
    负权边应使用 Bellman-Ford 算法
    """
    # dist[v] = 从 start 到 v 的当前已知最短距离
    dist = {v: float('inf') for v in graph.vertices()}
    dist[start] = 0
    
    # prev[v] = 最短路径上 v 的前驱顶点（用于路径重建）
    prev = {v: None for v in graph.vertices()}
    
    # 优先队列：(距离, 顶点)，最小堆保证每次取距离最小的
    pq = [(0, start)]
    
    # 已确定最短距离的顶点集合
    confirmed = set()
    
    while pq:
        d, u = heapq.heappop(pq)   # 取距离最小的顶点
        
        if u in confirmed:
            continue   # 已确定，跳过（可能是旧的无效条目）
        confirmed.add(u)
        
        # 松弛操作：尝试更新 u 的所有邻居的距离
        for v, weight in graph.get_neighbors(u):
            new_dist = d + weight
            
            if new_dist < dist[v]:        # 找到更短路径
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))
    
    return dist, prev


def reconstruct_path(prev, start, end):
    """
    根据前驱字典重建最短路径
    从终点沿前驱链反向追踪到起点
    """
    path = []
    v = end
    while v is not None:
        path.append(v)
        v = prev[v]
    path.reverse()
    
    # 验证路径确实从 start 开始（否则 start→end 不可达）
    return path if path and path[0] == start else []


# 测试
dist, prev = dijkstra(g, 'A')
print("最短距离:", dist)
# {'A': 0, 'B': 3, 'C': 2, 'D': 8}

print("A→D最短路径:", reconstruct_path(prev, 'A', 'D'))
# ['A', 'C', 'B', 'D']

print("A→D最短距离:", dist['D'])
# 8
```

---

## 7.6 ⭐ 拓扑排序（Topological Sort）

### 问题背景

```
场景：大学课程选修，"数据结构"要先学"编程基础"，
     "算法"要先学"数据结构"……
     问：所有课程应该按什么顺序修？

这就是拓扑排序：
给 DAG（有向无环图）中的顶点排一个线性顺序，
使得对于每条边 u→v，u 都排在 v 前面。

⚠️ 注意：
  - 只有 DAG（有向无环图）才有拓扑排序
  - 若图中有环（如 A→B→A），无法拓扑排序（循环依赖！）
  - 拓扑排序结果不唯一（可能有多个合法顺序）
```

### Kahn 算法（基于 BFS）

```
核心思想：
1. 计算所有顶点的入度
2. 把所有入度为 0 的顶点加入队列（没有依赖的，可以先执行）
3. 每次取一个顶点输出，把它的邻居入度各减 1
4. 若邻居入度变为 0，加入队列
5. 重复直到队列为空

检测环：若最终输出的顶点数 < 总顶点数，说明图中有环
```

```python
def topological_sort_kahn(graph):
    """
    Kahn 算法：基于 BFS 的拓扑排序
    
    时间：O(V + E)
    空间：O(V)
    
    优点：
    - 能检测图中是否有环
    - 直观理解（逐步去掉"无依赖"的顶点）
    """
    # 计算每个顶点的入度
    in_degree = {v: 0 for v in graph.vertices()}
    for v in graph.vertices():
        for neighbor, _ in graph.get_neighbors(v):
            in_degree[neighbor] += 1
    
    # 所有入度为 0 的顶点入队（无前置依赖，可以立即处理）
    queue  = deque([v for v, deg in in_degree.items() if deg == 0])
    result = []
    
    while queue:
        v = queue.popleft()
        result.append(v)
        
        # 把 v 的所有邻居入度减 1（v 处理完后，其依赖解除）
        for neighbor, _ in graph.get_neighbors(v):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)   # 入度变 0，可以处理了
    
    # 检测环：若输出顶点数 < 总顶点数，存在环
    if len(result) != len(graph.vertices()):
        raise ValueError("图中存在环，无法进行拓扑排序！")
    
    return result


def topological_sort_dfs(graph):
    """
    DFS 后序版拓扑排序
    
    原理：DFS 到底（后序）再加入结果，
    最后翻转即为拓扑顺序
    
    与 Kahn 算法等价，但通过 DFS 实现
    """
    visited = set()
    result  = []
    
    def dfs(v):
        visited.add(v)
        for neighbor, _ in graph.get_neighbors(v):
            if neighbor not in visited:
                dfs(neighbor)
        result.append(v)    # 后序：所有后继都处理完后才加入
    
    for v in graph.vertices():
        if v not in visited:
            dfs(v)
    
    return result[::-1]   # 反转得到拓扑顺序


# 测试：课程依赖图
# 数学→线性代数, 数学→概率论, 线代→机器学习, 概率论→机器学习
g_course = Graph(directed=True)
g_course.add_edge('数学',     '线性代数')
g_course.add_edge('数学',     '概率论')
g_course.add_edge('线性代数', '机器学习')
g_course.add_edge('概率论',   '机器学习')
g_course.add_edge('机器学习', '深度学习')

order = topological_sort_kahn(g_course)
print("修课顺序：", order)
# ['数学', '线性代数', '概率论', '机器学习', '深度学习']
# （线性代数和概率论的顺序可能互换，都合法）
```

---

## 7.7 最小生成树（MST）

### 问题背景

```
场景：用最少的线缆连通所有城市（铺设光纤网络）
      城市=顶点，可铺线路=边，线缆成本=权重
      目标：连通所有顶点，总权重最小，且不形成环

MST 性质：
  - n 个顶点，MST 恰好有 n-1 条边
  - MST 不唯一（可能有多个等权重的 MST）
  - 贪心策略：每次选权重最小的安全边
```

### Prim 算法

```python
def prim_mst(graph, start):
    """
    Prim 算法求最小生成树
    
    思路（贪心）：
    从一个顶点开始，每次选择"连接已选集合与未选集合的最小权重边"
    直到所有顶点都被选入
    
    时间：O(E log V)（用优先队列）
    空间：O(V)
    
    执行流程（从 A 出发，图：A-B(4),A-C(2),C-B(1),B-D(5),C-D(8)）：
    
    in_mst={A}，pq=[(2,A,C),(4,A,B)]
    
    弹出(2,A,C)：C不在MST，加入。MST边：A-C
    in_mst={A,C}，加入C的邻居：B(1), D(8)
    pq=[(1,C,B),(4,A,B),(5,B,D),(8,C,D)]
    
    弹出(1,C,B)：B不在MST，加入。MST边：C-B
    in_mst={A,C,B}，加入B的邻居：D(5)
    pq=[(4,A,B旧),(5,B,D),(8,C,D)]
    
    弹出(4,A,B)：B已在MST，跳过
    
    弹出(5,B,D)：D不在MST，加入。MST边：B-D
    in_mst={A,C,B,D}，所有顶点已选
    
    MST边集合：A-C(2), C-B(1), B-D(5)，总代价=8
    """
    in_mst    = set()
    mst_edges = []
    total_cost = 0
    
    # 优先队列：(权重, 起点, 终点)
    # 起始用虚拟边 (0, start, start)
    pq = [(0, start, start)]
    
    while pq:
        weight, u, v = heapq.heappop(pq)
        
        if v in in_mst:
            continue             # v 已在 MST 中，跳过
        
        in_mst.add(v)
        if u != v:               # 排除起始虚拟边
            mst_edges.append((u, v, weight))
            total_cost += weight
        
        # 把 v 的所有到"未选顶点"的边加入候选队列
        for neighbor, w in graph.get_neighbors(v):
            if neighbor not in in_mst:
                heapq.heappush(pq, (w, v, neighbor))
    
    return mst_edges, total_cost


# 用无向图测试
g_undirected = Graph(directed=False)
g_undirected.add_edge('A', 'B', 4)
g_undirected.add_edge('A', 'C', 2)
g_undirected.add_edge('C', 'B', 1)
g_undirected.add_edge('B', 'D', 5)
g_undirected.add_edge('C', 'D', 8)

edges, cost = prim_mst(g_undirected, 'A')
print("MST 边：", edges)     # [('A','C',2), ('C','B',1), ('B','D',5)]
print("总代价：", cost)       # 8
```

---

## 7.8 ⭐【面试题实战】

### 面试题1：岛屿数量（LeetCode 200，Medium）

**题目**：给定二维网格，`'1'` 代表陆地，`'0'` 代表水，计算岛屿的数量（每个岛屿由相邻陆地连接而成）。

**核心思路**：把网格看成图，每个 `'1'` 是一个顶点，上下左右相邻的 `'1'` 之间有边。岛屿数量 = 连通分量数量。

```python
def num_islands(grid):
    """
    DFS 淹没法：每发现一块陆地，用 DFS 把整座岛淹没（标记为'0'）
    
    岛屿数量 = 触发 DFS 的次数
    
    时间：O(m × n)，每个格子最多访问一次
    空间：O(m × n)（最坏情况递归深度）
    
    执行流程（简化示例）：
    
    grid = [['1','1','0'],
            ['0','1','0'],
            ['0','0','1']]
    
    (0,0)='1' → 触发DFS，淹没(0,0),(0,1),(1,1) → count=1
    (0,1)='0'（已淹没）跳过
    (2,2)='1' → 触发DFS，淹没(2,2) → count=2
    
    返回 2
    """
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    count = 0
    
    def dfs(r, c):
        """淹没以(r,c)为起点的整座岛屿"""
        # 越界或不是陆地：停止
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        
        grid[r][c] = '0'    # 标记为已访问（淹没）
        
        # 向四个方向扩展
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':    # 发现新陆地 = 发现新岛屿
                count += 1
                dfs(r, c)            # 淹没整座岛
    
    return count


grid = [
    ['1','1','0','0','0'],
    ['1','1','0','0','0'],
    ['0','0','1','0','0'],
    ['0','0','0','1','1']
]
print(num_islands(grid))    # 3
```

> **⚠️ 面试注意点**：
> 1. 直接修改 grid 值为 `'0'`（淹没），避免额外 visited 集合
> 2. 如果题目不允许修改输入，改用 `visited = set()` 记录坐标
> 3. 可改为 BFS 版本（用队列），逻辑相同，只是换用 deque

---

### 面试题2：课程表（LeetCode 207，Medium）

**题目**：有 n 门课，prerequisites[i]=[a,b] 表示学 a 之前必须学 b。判断是否可以完成所有课程（即课程图中是否存在环）。

**本质**：检测有向图中是否存在环 = 看拓扑排序能否完成。

```python
def can_finish(num_courses, prerequisites):
    """
    拓扑排序判断有向图是否有环
    
    思路：Kahn 算法（BFS 拓扑排序）
    若能排完所有课程（输出 n 个节点），则无环，返回 True
    若中途队列变空但还有课没排，说明有环，返回 False
    
    时间：O(V + E)，空间：O(V + E)
    
    执行流程（n=4, prerequisites=[[1,0],[2,1],[3,1]]）：
    
    建图：0→1, 1→2, 1→3
    入度：{0:0, 1:1, 2:1, 3:1}
    
    队列=[0]（入度0）
    弹出0：邻居1入度变0，入队 → 队列=[1]，count=1
    弹出1：邻居2,3入度变0，入队 → 队列=[2,3]，count=2
    弹出2：count=3
    弹出3：count=4
    count(4)==num_courses(4) → 无环，返回 True ✅
    """
    # 建图（邻接表）和入度统计
    graph     = defaultdict(list)
    in_degree = [0] * num_courses
    
    for course, prereq in prerequisites:
        graph[prereq].append(course)    # prereq → course
        in_degree[course] += 1
    
    # Kahn 算法
    queue = deque([i for i in range(num_courses) if in_degree[i] == 0])
    count = 0   # 已成功处理的课程数
    
    while queue:
        course = queue.popleft()
        count += 1
        
        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)
    
    return count == num_courses   # 全部处理完 = 无环


print(can_finish(2, [[1, 0]]))           # True（0→1，无环）
print(can_finish(2, [[1, 0], [0, 1]]))  # False（0→1→0，有环）
print(can_finish(4, [[1,0],[2,1],[3,1]]))# True
```

---

### 面试题3：腐烂的橘子（LeetCode 994，Medium）

**题目**：网格中 0=空，1=新鲜橘子，2=腐烂橘子。腐烂会向四方蔓延，每分钟新鲜变腐烂。求最少多少分钟后所有橘子腐烂？若不可能返回 -1。

**核心思路**：多源 BFS——把所有腐烂橘子同时作为起点开始 BFS 蔓延。

```python
def oranges_rotting(grid):
    """
    多源 BFS：所有腐烂橘子同时开始向外蔓延
    
    关键洞察：
    单源 BFS = 从1个起点开始，一圈一圈扩展
    多源 BFS = 把所有起点同时放入队列，一起开始扩展
              相当于"虚拟超级源点"连接所有实际起点
    
    每"一圈"扩展 = 1分钟
    BFS 结束时处理的层数 = 最少需要的分钟数
    
    时间：O(m × n)，空间：O(m × n)
    """
    rows, cols  = len(grid), len(grid[0])
    queue       = deque()
    fresh_count = 0   # 新鲜橘子数量
    
    # 初始化：找所有腐烂橘子（多个起点）和新鲜橘子
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))   # (行, 列, 时间)
            elif grid[r][c] == 1:
                fresh_count += 1
    
    if fresh_count == 0:
        return 0   # 没有新鲜橘子，直接返回0
    
    max_time = 0
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    
    while queue:
        r, c, time = queue.popleft()
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2              # 腐烂！
                fresh_count -= 1
                max_time = max(max_time, time + 1)
                queue.append((nr, nc, time + 1))
    
    # 若还有新鲜橘子，说明有孤立的无法到达的橘子
    return max_time if fresh_count == 0 else -1


grid1 = [[2,1,1],[1,1,0],[0,1,1]]
grid2 = [[2,1,1],[0,1,1],[1,0,1]]
print(oranges_rotting(grid1))   # 4
print(oranges_rotting(grid2))   # -1（左下角1被隔离）
```

> **⭐ 多源 BFS 是重要模式**：当有多个起点需要同时扩展时，把所有起点一起放入初始队列，BFS 自动保证层序（按时间/距离分层）。

---

### 面试题4：判断二分图（LeetCode 785，Medium）

**题目**：给定无向图，判断是否是二分图（能否将节点分为两组，使每条边的两端不在同一组）。

**核心思路**：BFS/DFS 染色——尝试用两种颜色交替染色，若出现冲突则不是二分图。

```python
def is_bipartite(graph_adj):
    """
    BFS 二着色法判断二分图
    
    二分图 ⟺ 图中不存在奇数长度的环 ⟺ 可以二着色
    
    思路：对每个节点，给它一种颜色，邻居给另一种颜色
    若发现邻居与自己同色 → 不是二分图
    
    graph_adj：邻接表（列表的列表，索引为节点编号）
    color[i]：0 或 1，表示节点 i 的颜色；-1 表示未染色
    
    时间：O(V + E)，空间：O(V)
    """
    n     = len(graph_adj)
    color = [-1] * n   # -1=未染色，0=颜色A，1=颜色B
    
    for start in range(n):
        if color[start] != -1:
            continue   # 已染色，跳过（可能是其他连通分量已处理）
        
        # BFS 对 start 所在的连通分量染色
        queue = deque([start])
        color[start] = 0   # 起点染颜色A
        
        while queue:
            node = queue.popleft()
            
            for neighbor in graph_adj[node]:
                if color[neighbor] == -1:
                    # 未染色：染成与当前节点相反的颜色
                    color[neighbor] = 1 - color[node]
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:
                    # 邻居与自己同色 → 冲突 → 不是二分图！
                    return False
    
    return True


# 测试
# 二分图：0-1-2-3 构成正方形（偶数环）
adj1 = [[1,3],[0,2],[1,3],[0,2]]
print(is_bipartite(adj1))   # True

# 非二分图：0-1-2 构成三角形（奇数环）
adj2 = [[1,2],[0,2],[0,1]]
print(is_bipartite(adj2))   # False
```

---

### 面试题5：网络延迟时间（LeetCode 743，Medium）

**题目**：n 个节点的网络，times[i]=[u,v,w] 表示 u 到 v 有延迟 w 的有向边。从节点 k 发出信号，问所有节点都收到信号需要多少时间？若无法到达所有节点返回 -1。

**本质**：Dijkstra 求单源最短路径，答案是最长的最短路径。

```python
def network_delay_time(times, n, k):
    """
    Dijkstra 求所有节点的最短路径，取最大值
    
    "所有节点都收到信号" = 信号到达最远节点的时间
    
    时间：O(E log V)，空间：O(V + E)
    
    执行流程（times=[[2,1,1],[2,3,1],[3,4,1]], n=4, k=2）：
    
    建图：2→1(1), 2→3(1), 3→4(1)
    
    dist = {1:∞, 2:0, 3:∞, 4:∞}
    pq = [(0, 2)]
    
    弹出(0,2)：处理邻居1和3
      dist[1]=1, dist[3]=1
    
    弹出(1,1)：无邻居
    弹出(1,3)：处理邻居4
      dist[4]=2
    
    弹出(2,4)：无邻居
    
    dist = {1:1, 2:0, 3:1, 4:2}
    max_dist = 2  → 返回 2 ✅
    """
    # 建图（邻接表）
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    
    # Dijkstra
    dist = {i: float('inf') for i in range(1, n + 1)}
    dist[k] = 0
    pq = [(0, k)]
    
    while pq:
        d, u = heapq.heappop(pq)
        
        if d > dist[u]:        # 过期条目，跳过
            continue
        
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    
    max_dist = max(dist.values())
    return max_dist if max_dist < float('inf') else -1


print(network_delay_time([[2,1,1],[2,3,1],[3,4,1]], 4, 2))   # 2
print(network_delay_time([[1,2,1]], 2, 2))                     # -1（2无法到1）
```

---

## 7.9 本章要点总结

### 核心概念映射表

| 概念 | 定义 | 关键特征 | 主要应用 |
|------|------|----------|---------|
| **有向图** | 边有方向 | A→B ≠ B→A | 任务依赖、网页链接 |
| **无向图** | 边无方向 | A-B = B-A | 社交网络、地图 |
| **邻接矩阵** | n×n 二维数组 | O(1)查边，O(V²)空间 | 稠密图 |
| **邻接表** | 字典+列表 | O(V+E)空间 | 稀疏图（推荐）|
| **BFS** | 队列，按层扩展 | 无权最短路 | 最短跳数、多源扩散 |
| **DFS** | 栈/递归，深入探索 | 连通性、环检测 | 岛屿计数、拓扑排序 |
| **Dijkstra** | 贪心+优先队列 | 有权非负最短路 | 导航、网络延迟 |
| **拓扑排序** | DAG 线性排序 | Kahn(BFS)/DFS后序 | 课程调度、依赖解析 |
| **MST** | 最小权连通生成树 | n-1条边，贪心 | 最小铺线代价 |

### 图算法选择指南

```
问题类型                    → 选用算法
─────────────────────────────────────────────
无权图最短路径（跳数最少）  → BFS
有权图最短路径（非负权重）  → Dijkstra
连通性 / 连通分量           → BFS 或 DFS
环的检测                    → DFS（看 visited 状态）
拓扑排序 / 依赖检测         → Kahn算法（BFS）
最小生成树                  → Prim（稠密图）/ Kruskal（稀疏图）
网格类搜索（岛屿、路径）    → DFS（计数）/ BFS（最短距离）
多起点同时扩展              → 多源 BFS
```

### 面试高频考点

| 题目 | 核心思路 | 时间 | 空间 | 难度 |
|------|---------|------|------|------|
| 岛屿数量 LC200 | DFS 淹没，计触发次数 | O(mn) | O(mn) | Medium |
| 课程表 LC207 | Kahn拓扑排序，检测环 | O(V+E) | O(V+E) | Medium |
| 腐烂橘子 LC994 | 多源 BFS 同时扩展 | O(mn) | O(mn) | Medium |
| 判断二分图 LC785 | BFS 二着色，同色冲突返回False | O(V+E) | O(V) | Medium |
| 网络延迟 LC743 | Dijkstra，取最大最短路 | O(E log V) | O(V+E) | Medium |

### 关键代码模板

```python
# BFS 模板（无权最短路/层序扩展）
from collections import deque
visited = set([start])
queue   = deque([start])
while queue:
    v = queue.popleft()
    for neighbor in get_neighbors(v):
        if neighbor not in visited:
            visited.add(neighbor)
            queue.append(neighbor)

# 多源 BFS 模板
queue = deque()
for source in all_sources:       # 所有起点同时加入
    queue.append(source)
    visited.add(source)
# 后续 BFS 逻辑相同

# DFS 模板（递归）
visited = set()
def dfs(v):
    visited.add(v)
    for neighbor in get_neighbors(v):
        if neighbor not in visited:
            dfs(neighbor)

# Dijkstra 模板
import heapq
dist = {v: float('inf') for v in vertices}
dist[start] = 0
pq = [(0, start)]
while pq:
    d, u = heapq.heappop(pq)
    if d > dist[u]: continue       # 过期条目
    for v, w in get_neighbors(u):
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            heapq.heappush(pq, (dist[v], v))

# Kahn 拓扑排序模板
in_degree = {v: 0 for v in vertices}
for v in vertices:
    for neighbor in get_neighbors(v):
        in_degree[neighbor] += 1
queue = deque([v for v in vertices if in_degree[v] == 0])
result = []
while queue:
    v = queue.popleft()
    result.append(v)
    for neighbor in get_neighbors(v):
        in_degree[neighbor] -= 1
        if in_degree[neighbor] == 0:
            queue.append(neighbor)
```

### 常见陷阱（坑点）

| 陷阱 | 说明 | 解决方法 |
|------|------|---------|
| BFS 未标记已访问 | 同一节点重复入队，死循环或结果错误 | 入队时立即加入 visited，不是出队时 |
| Dijkstra 忽略过期条目 | pq 中可能有同一节点的旧条目 | `if d > dist[u]: continue` |
| Dijkstra 用于负权边 | 贪心策略在负权边时失效 | 负权边改用 Bellman-Ford |
| 拓扑排序未检测环 | 输出节点数 < 总节点数时有环 | `if len(result) != V: 有环` |
| 网格 DFS 不标记访问 | 重复访问，死循环 | 访问时立即修改原值或加 visited |
| 多源 BFS 漏加初始节点 | 部分起点未加入队列 | 初始化时遍历所有起点 |

---

> **给初学者的学习建议**：
> 1. **BFS 和 DFS 模板必须背熟**，并且能用 `visited` 集合、队列/栈手写出来。大多数图题都是这两个模板的变体。
> 2. **网格图是入门图算法的最佳练习场**（LeetCode 200 岛屿系列），它把图的概念可视化了，比抽象的邻接表更直观。
> 3. **Dijkstra 的三个要点**：优先队列取最小、松弛操作、过期条目跳过。代码量不大，但逻辑要非常清楚。
> 4. **拓扑排序 = 检测环 + 排序**，面试中课程表系列（LC207、LC210）非常高频，Kahn 算法（BFS 版）代码整洁，推荐优先掌握。
> 5. **实际面试中**，图的题目通常会给你邻接表（或网格），不需要手写 Graph 类，直接在函数内建 `defaultdict(list)` 即可。
