# 第7章：图

> **核心思路**：图是树的"再升维"——从层级（一对多，有父子约束）扩展到任意关系（多对多，无限制）。掌握 BFS/DFS 两种遍历，理解 Dijkstra 的贪心策略，理解拓扑排序的应用场景。

---

## 7.1 图的基本概念

### 定义

```
图 G = (V, E)
V（Vertex）：顶点集合
E（Edge）：边集合，每条边连接两个顶点
```

### 核心术语

```
有向图（Digraph）：边有方向，A→B ≠ B→A
无向图：边无方向，A-B = B-A
权重（Weight）：边上的数值（距离、代价等）

路径（Path）：顶点序列 v₁→v₂→...→vₙ，相邻顶点之间有边
环（Cycle）：起点和终点相同的路径
DAG：有向无环图（Directed Acyclic Graph）

度（Degree）：与某顶点相连的边数
  有向图：入度（指向它的边数）+ 出度（它指出的边数）
```

---

## 7.2 图的表示方式

### 邻接矩阵（Adjacency Matrix）

```
用 n×n 矩阵表示 n 个顶点的图
matrix[i][j] = 1（或边权重）表示 i→j 有边

优点：O(1) 判断两点是否相连
缺点：O(V²) 空间，稀疏图浪费严重
```

```python
# 有4个顶点 A(0) B(1) C(2) D(3) 的有向图
# A→B, A→C, B→D, C→D
adj_matrix = [
    #A  B  C  D
    [0, 1, 1, 0],  # A
    [0, 0, 0, 1],  # B
    [0, 0, 0, 1],  # C
    [0, 0, 0, 0],  # D
]
# 判断A→B是否有边：adj_matrix[0][1] == 1 → True，O(1)
```

### ⭐ 邻接表（Adjacency List）

```
每个顶点维护一个列表，存储所有与之相邻的顶点

优点：O(V+E) 空间，稀疏图高效
缺点：O(度数) 判断两点是否相连
```

```python
class Graph:
    """
    用字典实现邻接表的图（支持有向/无向，支持权重）
    
    结构：
    {
      顶点A: [(邻居1, 权重1), (邻居2, 权重2), ...],
      顶点B: [...],
      ...
    }
    """
    
    def __init__(self, directed=True):
        self.adj = {}           # 邻接表：{顶点: [(邻居,权重),...]}
        self.directed = directed
    
    def add_vertex(self, v):
        if v not in self.adj:
            self.adj[v] = []
    
    def add_edge(self, u, v, weight=1):
        """添加边 u→v（有权重）"""
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u].append((v, weight))
        
        if not self.directed:           # 无向图：双向都加
            self.adj[v].append((u, weight))
    
    def get_neighbors(self, v):
        """获取顶点v的所有邻居"""
        return self.adj.get(v, [])
    
    def __str__(self):
        lines = []
        for v, neighbors in self.adj.items():
            nb_str = ', '.join(f"{n}(w={w})" for n, w in neighbors)
            lines.append(f"{v}: [{nb_str}]")
        return '\n'.join(lines)

# 构建示例图
g = Graph(directed=True)
g.add_edge('A', 'B', 4)
g.add_edge('A', 'C', 2)
g.add_edge('B', 'D', 5)
g.add_edge('C', 'B', 1)
g.add_edge('C', 'D', 8)
print(g)
```

---

## 7.3 ⭐ 广度优先搜索（BFS）

### 思想：从起点出发，按距离由近到远逐层探索

```python
from collections import deque

def bfs(graph, start):
    """
    广度优先搜索
    
    用队列实现：先进先出 = 先探索距离近的节点
    
    应用：
    - 求无权图中两点间的最短路径（跳数最少）
    - 层序遍历
    - 找连通分量
    
    时间：O(V + E)  空间：O(V)
    """
    visited = set()          # 记录已访问节点，防止重复访问
    queue = deque([start])   # 队列初始化
    visited.add(start)
    
    order = []               # 记录访问顺序
    
    while queue:
        vertex = queue.popleft()   # 出队（从队头取）
        order.append(vertex)
        
        for neighbor, _ in graph.get_neighbors(vertex):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)  # 入队（加到队尾）
    
    return order

# 执行 bfs(g, 'A')：
# 初始：队列=[A], visited={A}
# 访问A：邻居B,C入队  → 队列=[B,C], visited={A,B,C}
# 访问B：邻居D入队    → 队列=[C,D], visited={A,B,C,D}
# 访问C：邻居B,D已访问 → 队列=[D]
# 访问D：无新邻居     → 队列=[]
# 结果：[A, B, C, D]
```

### ⭐ BFS 求最短路径（无权图）

```python
def bfs_shortest_path(graph, start, end):
    """
    BFS找无权图最短路径
    
    关键：记录每个节点的前驱，反向追踪得到路径
    """
    visited = {start: None}   # {节点: 来自哪个节点}（None表示起点）
    queue = deque([start])
    
    while queue:
        v = queue.popleft()
        
        if v == end:              # 找到终点！
            # 反向追踪路径
            path = []
            while v is not None:
                path.append(v)
                v = visited[v]
            return path[::-1]     # 反转得到正向路径
        
        for neighbor, _ in graph.get_neighbors(v):
            if neighbor not in visited:
                visited[neighbor] = v   # 记录前驱
                queue.append(neighbor)
    
    return None  # 不可达

# 经典应用：词梯问题（FOOL→SAGE，每次改一个字母）
# 把每个单词作为顶点，只差一个字母的单词之间连边
# BFS 求最短变换路径
```

---

## 7.4 ⭐ 深度优先搜索（DFS）

### 思想：沿一条路走到底，走不通再回头

```python
def dfs(graph, start):
    """
    深度优先搜索（递归版）
    
    用系统调用栈模拟栈的行为：先深入，到底后回溯
    
    应用：
    - 检测环
    - 拓扑排序
    - 强连通分量
    - 路径存在性判断
    
    时间：O(V + E)  空间：O(V)（递归栈深度）
    """
    visited = set()
    order = []
    
    def _dfs(v):
        visited.add(v)
        order.append(v)
        for neighbor, _ in graph.get_neighbors(v):
            if neighbor not in visited:
                _dfs(neighbor)         # 深入递归
    
    _dfs(start)
    return order

def dfs_iterative(graph, start):
    """
    DFS（迭代版，用显式栈）
    
    适合递归层次深时（避免Python递归限制）
    """
    visited = set()
    stack = [start]
    order = []
    
    while stack:
        v = stack.pop()          # 从栈顶取（后进先出）
        if v not in visited:
            visited.add(v)
            order.append(v)
            for neighbor, _ in graph.get_neighbors(v):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return order
```

### BFS vs DFS 对比

| | BFS | DFS |
|---|---|---|
| 数据结构 | 队列（FIFO） | 栈（LIFO）/ 递归 |
| 探索顺序 | 按层，由近到远 | 沿路深入，到底回溯 |
| 最短路径 | ✅ 无权图 | ❌ 不保证 |
| 内存占用 | O(宽度) | O(深度) |
| 适用场景 | 最短路径、层序遍历 | 拓扑排序、环检测、迷宫 |

---

## 7.5 ⭐ Dijkstra 最短路径算法

### 适用场景：有权图（非负权重）中的单源最短路径

```python
import heapq

def dijkstra(graph, start):
    """
    Dijkstra 算法
    
    核心思想（贪心）：
    维护一个"已确定最短距离"的集合，
    每次从"候选集"中选距离最小的顶点，
    更新其邻居的距离（松弛操作）
    
    用优先队列（最小堆）高效取最小距离
    
    时间：O((V+E) log V)   空间：O(V)
    
    ⚠️ 不能处理负权边！（负权边用Bellman-Ford）
    """
    # dist[v] = 从start到v的当前已知最短距离
    dist = {v: float('inf') for v in graph.adj}
    dist[start] = 0
    
    # 前驱记录（用于重建路径）
    prev = {v: None for v in graph.adj}
    
    # 优先队列：(距离, 顶点)
    pq = [(0, start)]
    visited = set()
    
    while pq:
        d, u = heapq.heappop(pq)   # 取当前距离最小的顶点
        
        if u in visited:
            continue                # 已确定，跳过
        visited.add(u)
        
        for v, weight in graph.get_neighbors(u):
            new_dist = d + weight   # 经过u到v的距离
            
            # 松弛操作：如果找到更短路径，更新
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))
    
    return dist, prev

def reconstruct_path(prev, start, end):
    """根据前驱字典重建最短路径"""
    path = []
    v = end
    while v is not None:
        path.append(v)
        v = prev[v]
    path.reverse()
    return path if path[0] == start else []

# 测试
g2 = Graph(directed=True)
g2.add_edge('A', 'B', 4)
g2.add_edge('A', 'C', 2)
g2.add_edge('C', 'B', 1)  # A→C→B 总代价=3，比A→B=4更短
g2.add_edge('B', 'D', 5)
g2.add_edge('C', 'D', 8)

dist, prev = dijkstra(g2, 'A')
print(dist)   # {'A':0, 'B':3, 'C':2, 'D':8}
print(reconstruct_path(prev, 'A', 'D'))  # ['A', 'C', 'B', 'D']
```

### Dijkstra 执行过程图解

```
初始：dist = {A:0, B:∞, C:∞, D:∞}，pq = [(0,A)]

步骤1：弹出(0,A)
  → 更新邻居：dist[B]=4, dist[C]=2
  → pq = [(2,C), (4,B)]

步骤2：弹出(2,C)
  → 更新邻居：dist[B]=min(4, 2+1)=3, dist[D]=2+8=10
  → pq = [(3,B), (4,B旧), (10,D)]

步骤3：弹出(3,B)
  → 更新邻居：dist[D]=min(10, 3+5)=8
  → pq = [(4,B旧已访问), (8,D), (10,D旧)]

步骤4：弹出(4,B) → 已访问，跳过

步骤5：弹出(8,D) → 确定！dist[D]=8
```

---

## 7.6 ⭐ 拓扑排序（Topological Sort）

### 适用场景：有向无环图（DAG）中，任务的先后依赖顺序

```python
def topological_sort(graph):
    """
    拓扑排序（Kahn 算法，基于BFS）
    
    思路：
    1. 计算每个顶点的入度
    2. 把所有入度为0的顶点加入队列（无依赖的任务）
    3. 每次取出一个顶点输出，把它的邻居入度-1
    4. 入度变为0的邻居加入队列
    5. 重复直到队列为空
    
    若最终输出的顶点数 < V，说明图中有环（无法拓扑排序）
    
    时间：O(V + E)
    """
    # 计算入度
    in_degree = {v: 0 for v in graph.adj}
    for v in graph.adj:
        for neighbor, _ in graph.get_neighbors(v):
            in_degree[neighbor] += 1
    
    # 入度为0的顶点入队
    queue = deque([v for v, deg in in_degree.items() if deg == 0])
    result = []
    
    while queue:
        v = queue.popleft()
        result.append(v)
        
        for neighbor, _ in graph.get_neighbors(v):
            in_degree[neighbor] -= 1        # 邻居入度-1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)      # 入度变0，加入队列
    
    if len(result) != len(graph.adj):
        raise ValueError("图中存在环，无法拓扑排序！")
    
    return result

# 示例：课程选修依赖
g3 = Graph(directed=True)
g3.add_edge('数学', '线性代数')
g3.add_edge('数学', '概率论')
g3.add_edge('线性代数', '机器学习')
g3.add_edge('概率论', '机器学习')
g3.add_edge('机器学习', '深度学习')

order = topological_sort(g3)
print(order)  # ['数学', '线性代数', '概率论', '机器学习', '深度学习']
# 保证先修课在前，依赖课在后
```

---

## 7.7 最小生成树（Minimum Spanning Tree）

**问题**：连通所有顶点，使得总边权最小。

```python
def prim_mst(graph, start):
    """
    Prim 算法（贪心）
    
    思路：从一个顶点开始，每次贪心选择
    "连接已在树中的顶点 和 不在树中的顶点" 的最短边
    
    时间：O(E log V)（用优先队列）
    """
    in_mst = set()
    # (边权重, 起点, 终点)
    pq = [(0, start, start)]
    mst_edges = []
    total_cost = 0
    
    while pq:
        weight, u, v = heapq.heappop(pq)
        
        if v in in_mst:
            continue                    # 已在树中，跳过
        
        in_mst.add(v)
        if u != v:                      # 不是起始虚边
            mst_edges.append((u, v, weight))
            total_cost += weight
        
        for neighbor, w in graph.get_neighbors(v):
            if neighbor not in in_mst:
                heapq.heappush(pq, (w, v, neighbor))
    
    return mst_edges, total_cost
```

---

## 7.8 本章算法总览

| 算法 | 类型 | 时间复杂度 | 解决问题 |
|------|------|-----------|---------|
| **BFS** | 遍历 | O(V+E) | 无权最短路、层序 |
| **DFS** | 遍历 | O(V+E) | 环检测、拓扑排序 |
| **Dijkstra** | 最短路 | O((V+E)log V) | 有权非负最短路 |
| **Prim** | 最小生成树 | O(E log V) | 连通所有顶点最小代价 |
| **拓扑排序** | DAG排序 | O(V+E) | 任务调度、依赖解析 |

---

## 7.9 本章要点总结

| 概念 | 要点 |
|------|------|
| **邻接表** | 稀疏图首选，O(V+E)空间 |
| **⭐ BFS** | 队列 + visited集合；无权最短路 |
| **⭐ DFS** | 递归/栈；适合拓扑排序、环检测 |
| **⭐ Dijkstra** | 贪心+优先队列；不能有负权边 |
| **拓扑排序** | 仅DAG；实际用于包管理、任务调度 |
| **最小生成树** | Prim/Kruskal；连通图最小代价骨架 |

> **给初学者的建议**：
> 1. BFS 和 DFS 是图算法的基础，务必能手写，理解 `visited` 集合的作用（防止无限循环）。
> 2. Dijkstra 的核心是"松弛操作"——每次用当前最短路径更新邻居，反复练习直到理解。
> 3. 拓扑排序在实际工程中非常常见（如 pip 安装包、Makefile 构建），理解其用途比死背代码更重要。
> 4. 图算法的关键是选对数据结构：稀疏图用邻接表，需要快速判断连接用邻接矩阵。
