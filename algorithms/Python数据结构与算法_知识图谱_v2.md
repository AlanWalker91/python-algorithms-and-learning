# Python 数据结构与算法 · 结构化知识图谱

> 适用场景：测试开发 / Python 后端工程师面试备战  
> 覆盖范围：整体框架 · 数据结构原理 · 算法思想 · 面试题精讲

---

# 第一部分：整体框架结构

## 1.1 知识全景图

```
Python 数据结构与算法
│
├── 【数据结构层】
│   │
│   ├── 线性结构
│   │   ├── list          动态数组        → 栈 / 滑动窗口 / 前缀和 / 单调栈
│   │   ├── tuple         静态数组        → 不可变序列 / 复合键 / 函数返回值
│   │   ├── deque         块状双向链表    → 队列 / 单调队列 / BFS
│   │   └── ListNode      手写指针链表    → 链表反转 / 环检测 / LRU
│   │
│   ├── 哈希结构
│   │   ├── dict          哈希表（有序）  → 映射 / 记忆化 / 图邻接表
│   │   ├── set           哈希集合        → 去重 / visited / 成员判断
│   │   ├── Counter       计数哈希        → 频率统计 / 异位词 / TopK
│   │   └── defaultdict   默认值哈希      → 邻接表 / 分组 / 计数
│   │
│   ├── 树形结构
│   │   ├── heapq         二叉堆（最小）  → TopK / Dijkstra / 优先队列
│   │   └── TreeNode      手写二叉树      → 遍历 / 递归 / 树形DP
│   │
│   └── 图结构
│       ├── 邻接表         defaultdict(list) + 边权列表
│       └── 并查集         数组模拟       → 连通分量 / 环检测 / Kruskal
│
├── 【算法思想层】
│   │
│   ├── 双指针            对撞指针 / 快慢指针 / 同向指针
│   ├── 滑动窗口          定长窗口 / 变长窗口（右扩左缩）
│   ├── 哈希              空间换时间，O(1) 查找补数/频次
│   ├── 二分查找          有序/单调区间 → O(log n)
│   ├── 递归与分治        Divide → Conquer → Combine
│   ├── 动态规划          重叠子问题 + 最优子结构
│   ├── 贪心              局部最优 → 全局最优（需证明）
│   ├── BFS               队列逐层扩展 → 最短路（无权）
│   ├── DFS / 回溯        深度遍历 + 路径记录 + 撤销
│   └── 图算法            拓扑 / Dijkstra / 并查集 / MST
│
└── 【场景应用层】
    │
    ├── 查找类     二分 / 哈希 / BFS
    ├── 排序类     归并(nlogn) / 快排(nlogn) / 堆排(nlogn)
    ├── 最短路类   BFS(无权) / Dijkstra(非负权) / Bellman-Ford(负权)
    ├── 最优化类   DP（子问题有重叠）/ 贪心（可证明局部最优）
    ├── 枚举类     回溯 + 剪枝（排列/组合/子集/棋盘）
    ├── 连通性类   BFS / DFS / 并查集
    └── 调度类     堆（优先队列）/ 拓扑排序（依赖关系）
```

---

## 1.2 核心术语定义速查

| 术语 | 英文 | 定义 |
|------|------|------|
| 时间复杂度 | Time Complexity | 算法执行时间随输入规模 n 增长的趋势，用大 O 表示 |
| 空间复杂度 | Space Complexity | 算法运行所需额外内存随 n 的增长趋势 |
| 均摊复杂度 | Amortized Complexity | 多次操作的总代价平均到每次，如 list.append() 均摊 O(1) |
| 原地操作 | In-place | 不使用额外空间（或 O(1) 额外空间）直接在原数据上操作 |
| 稳定排序 | Stable Sort | 排序后相同 key 的元素保持原有相对顺序（如归并排序）|
| 装载因子 | Load Factor | 哈希表中元素数量 / 槽位总数，超阈值触发扩容 |
| 哈希冲突 | Hash Collision | 不同 key 映射到相同哈希槽位 |
| 开放寻址 | Open Addressing | 冲突时在表内探测空槽（Python dict 使用） |
| 链地址法 | Separate Chaining | 冲突时槽位存链表，挂载多个元素 |
| 路径压缩 | Path Compression | 并查集优化：find 时将节点直接挂到根，降低树高 |
| 按秩合并 | Union by Rank | 并查集优化：将矮树挂到高树下，控制树高 |
| 记忆化 | Memoization | 自顶向下 DP：将已计算结果缓存，避免重复递归 |
| 制表法 | Tabulation | 自底向上 DP：按顺序填 dp 数组 |
| 最优子结构 | Optimal Substructure | 全局最优解可由子问题最优解构成（DP/贪心前提） |
| 重叠子问题 | Overlapping Subproblems | 递归求解时同一子问题被多次计算（DP 核心特征） |
| 贪心选择性 | Greedy Choice Property | 局部最优选择不影响后续子问题的最优性 |
| 拓扑序 | Topological Order | 有向无环图中，若有边 u→v 则 u 在 v 之前的线性排列 |
| 入度 | In-degree | 有向图中指向某节点的边数 |
| 出度 | Out-degree | 有向图中从某节点出发的边数 |
| 连通分量 | Connected Component | 无向图中极大连通子图 |
| 强连通分量 | Strongly Connected Component | 有向图中任意两点互达的极大子图 |
| 前缀和 | Prefix Sum | `pre[i]` = 数组前 i 个元素之和，加速区间查询 |
| 差分数组 | Difference Array | `diff[i] = arr[i] - arr[i-1]`，加速区间批量修改 |
| 单调栈 | Monotonic Stack | 栈内元素保持单调递增/递减，处理"下一个更大/更小元素" |
| 单调队列 | Monotonic Deque | 队内元素保持单调性，处理滑动窗口最大/最小值 |

---

## 1.3 数据结构选型速查

| 需求描述 | 推荐结构 | 理由 |
|---------|---------|------|
| 有序序列，频繁末尾增删 | `list` | 动态数组末尾操作 O(1) 均摊 |
| 频繁两端增删（队列/栈）| `deque` | 两端均 O(1) |
| 键值映射，快速查找 | `dict` | 哈希查找 O(1) 均摊 |
| 快速去重 / 成员判断 | `set` | 哈希 O(1) |
| 字符/元素频率统计 | `Counter` | 直接建立计数映射 |
| 图的邻接表 / 分组聚合 | `defaultdict(list)` | 无需手动初始化键 |
| 按优先级处理 / TopK | `heapq` | 堆操作 O(log n) |
| 不可变序列 / 复合键 | `tuple` | 可哈希，内存高效 |
| LRU 缓存 | `OrderedDict` + `move_to_end` | 维护访问顺序 |
| 连通性 / 动态合并集合 | `UnionFind`（手写）| 近似 O(1) 的 find/union |
| 区间最大/最小（窗口）| `deque`（单调队列）| O(n) 总复杂度 |

---

## 1.4 常见操作时间复杂度汇总

| 结构 | 随机访问 | 查找 | 头部增删 | 尾部增删 | 中间增删 | 有序？ |
|------|---------|------|---------|---------|---------|--------|
| `list` | O(1) | O(n) | O(n) | O(1)均摊 | O(n) | 手动 |
| `deque` | O(n) | O(n) | O(1) | O(1) | O(n) | 手动 |
| `dict` | — | O(1) | — | O(1) | — | 插入序 |
| `set` | — | O(1) | — | O(1) | — | 否 |
| `heapq` | O(1)堆顶 | — | — | O(log n) | — | 堆序 |
| 单链表 | O(n) | O(n) | O(1) | O(n) | O(1)知位置 | 手动 |
| 双链表 | O(n) | O(n) | O(1) | O(1) | O(1)知位置 | 手动 |

---

## 1.5 Python 刷题常用技巧速查

```python
# ===== 导入 =====
from collections import defaultdict, deque, Counter, OrderedDict
from functools import lru_cache
import heapq, bisect, math, itertools

# ===== 常量 =====
INF = float('inf')
NEG_INF = float('-inf')

# ===== 二维数组（正确初始化）=====
grid = [[0] * cols for _ in range(rows)]  # ✅ 每行独立
# grid = [[0]*cols] * rows               # ❌ 浅拷贝，所有行共享同一列表

# ===== 四方向 / 八方向 =====
dirs4 = [(0,1),(0,-1),(1,0),(-1,0)]
dirs8 = [(dr,dc) for dr in [-1,0,1] for dc in [-1,0,1] if (dr,dc)!=(0,0)]

# ===== 堆（最大堆技巧）=====
heapq.heappush(h, (-val, item))    # 存负数模拟最大堆
top = -heapq.heappop(h)[0]        # 取出时取反还原

# ===== 二分模块 =====
bisect.bisect_left(arr, x)         # 第一个 >= x 的位置（左边界）
bisect.bisect_right(arr, x)        # 第一个 > x 的位置（右边界）
bisect.insort_left(arr, x)         # 插入保持有序

# ===== 字符处理 =====
ord(c) - ord('a')                  # 字母 → 0~25 索引
chr(idx + ord('a'))                # 索引 → 字母
Counter(s)                         # 字符串字符频次

# ===== 记忆化递归 =====
@lru_cache(maxsize=None)
def dp(i, j, state):
    ...

# ===== 排序技巧 =====
sorted(lst, key=lambda x: (x[1], -x[0]))  # 多级排序
lst.sort(key=lambda x: x[1], reverse=True)

# ===== 其他 =====
any(cond for x in lst)    # 任一满足
all(cond for x in lst)    # 全部满足
zip(*matrix)              # 矩阵转置（解包）
[*map(int, input().split())]  # 快速读入整数列表
```


---

# 第二部分：Python 数据结构

---

## 2.1 列表 `list` — 动态数组

### 核心术语
| 术语 | 定义 |
|------|------|
| 动态数组 | 容量可自动扩展的数组，底层仍是连续内存块 |
| 过分配（Over-allocation）| 扩容时申请比实际需要更多的空间，减少频繁扩容次数 |
| 均摊 O(1) | 单次 append 可能触发 O(n) 扩容，但 n 次 append 总代价 O(n)，平均每次 O(1) |
| 指针数组 | list 底层存储的不是对象本身，而是指向对象的指针（8 字节/槽位） |

### 底层实现原理
```
内存布局（64位系统）：
┌──────────────────────────────────────────┐
│  ob_size: 当前元素数    (int)             │
│  allocated: 已分配槽位  (int)             │
│  ob_item:  ┌──┬──┬──┬──┬──┬──┐          │
│            │p0│p1│p2│p3│  │  │  ← 指针数组│
│            └──┴──┴──┴──┴──┴──┘          │
│              ↓  ↓  ↓  ↓                  │
│             obj obj obj obj               │
└──────────────────────────────────────────┘

扩容规律（近似 1.125 倍）：
容量: 0→4→8→16→25→35→46→58→72→88...
```

### Python 用法
```python
lst = []
lst = [1, 2, 3]
lst = list(range(10))
lst = [x**2 for x in range(5)]        # 列表推导式
lst = [0] * n                          # 初始化长度为 n 的列表
```

### 常用方法与时间复杂度

| 操作 | 方法 | 时间复杂度 | 备注 |
|------|------|-----------|------|
| 末尾追加 | `append(x)` | O(1) 均摊 | 扩容时 O(n)，均摊后 O(1) |
| 末尾弹出 | `pop()` | O(1) | |
| 指定位置插入 | `insert(i, x)` | O(n) | i 之后元素全部右移 |
| 指定位置删除 | `pop(i)` | O(n) | i 之后元素全部左移 |
| 按值删除 | `remove(x)` | O(n) | 先线性查找再删除 |
| 随机访问 | `lst[i]` | O(1) | 指针偏移：ob_item + i * 8 |
| 切片 | `lst[a:b]` | O(k) | k = b - a，创建新列表 |
| 查找（线性）| `index(x)` / `x in lst` | O(n) | |
| 排序 | `sort()` / `sorted()` | O(n log n) | Timsort（稳定排序） |
| 反转 | `reverse()` | O(n) | 原地操作 |
| 长度 | `len(lst)` | O(1) | 缓存在对象头部 |
| 拼接 | `lst1 + lst2` | O(m+n) | 创建新列表 |
| 扩展 | `extend(iterable)` | O(k) | k = 新增元素数 |
| 清空 | `clear()` | O(n) | 需要解引用每个元素 |

### 典型应用场景（含代码）

**① 用 list 模拟栈（LIFO）**
```python
# 栈：后进先出，括号匹配经典应用
def isValid(s: str) -> bool:
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}

    for ch in s:
        if ch in '({[':
            stack.append(ch)          # 左括号入栈
        elif ch in ')}]':
            if not stack or stack[-1] != mapping[ch]:
                return False          # 栈空或不匹配
            stack.pop()               # 匹配成功，出栈
    return not stack                  # 栈空说明全部匹配
```

**② 前缀和（区间求和 O(1)）**
```python
# 预处理 O(n)，之后每次区间查询 O(1)
def build_prefix(nums):
    n = len(nums)
    pre = [0] * (n + 1)             # pre[0] = 0（哨兵）
    for i in range(n):
        pre[i+1] = pre[i] + nums[i]
    return pre

# 查询 nums[l..r] 的区间和（闭区间）
def range_sum(pre, l, r):
    return pre[r+1] - pre[l]        # 前 r+1 个 - 前 l 个

# 示例
nums = [1, 2, 3, 4, 5]
pre  = build_prefix(nums)           # [0, 1, 3, 6, 10, 15]
print(range_sum(pre, 1, 3))         # 2+3+4 = 9
```

**③ 单调栈（下一个更大元素）**
```python
# 单调栈：栈内保持递减顺序，用于求每个元素右边第一个更大的数
def nextGreaterElement(nums):
    n = len(nums)
    result = [-1] * n               # 默认没有更大元素
    stack = []                      # 存下标，栈内对应值单调递减

    for i in range(n):
        # 当前元素比栈顶大，说明找到了栈顶元素的"下一个更大值"
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]   # 记录答案
        stack.append(i)

    return result

# 示例：[2,1,2,4,3] → [4,2,4,-1,-1]
```

---

## 2.2 元组 `tuple` — 静态数组

### 核心术语
| 术语 | 定义 |
|------|------|
| 不可变（Immutable）| 创建后不能增删改元素，内存地址和内容均固定 |
| 可哈希（Hashable）| 对象有稳定的哈希值，可作为 dict 的键或 set 的元素 |
| 元组缓存池 | CPython 对长度 ≤ 20 的小元组复用对象，减少内存分配 |

### 典型应用
```python
# ① 函数多返回值（本质是返回 tuple）
def divmod_custom(a, b):
    return a // b, a % b            # 等价于 return (a//b, a%b)

q, r = divmod_custom(17, 5)        # 解包赋值

# ② 作为字典复合键（list 不可哈希，tuple 可以）
visited = {}
visited[(row, col)] = True         # 二维坐标作为键

# ③ 命名元组（增强可读性）
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(3, 4)
print(p.x, p.y)                    # 3 4，比 p[0] p[1] 更清晰
```

---

## 2.3 字典 `dict` — 有序哈希表

### 核心术语
| 术语 | 定义 |
|------|------|
| 哈希函数 | 将任意 key 映射为固定范围整数（槽位索引）的函数 |
| 哈希碰撞 | 不同 key 映射到相同槽位，Python 用伪随机探测解决 |
| 伪随机探测 | `j = (5*j + 1 + perturb) % size`，探测下一个候选槽位 |
| 紧凑哈希表 | Python 3.6+ 的 dict 结构：indices 数组 + entries 紧凑数组，节省内存并保留插入序 |

### 底层结构（Python 3.6+）
```
indices 数组（槽位 → 条目索引）：
[ -, 0, -, 2, 1, -, -, 3 ]
  ↑              ↑
  空槽           哈希(key)%size 对应位置

entries 紧凑数组（顺序存储所有键值对）：
[ (hash0, key0, val0),
  (hash1, key1, val1),
  (hash2, key2, val2),
  ... ]

优点：
- 保留插入顺序（Python 3.7+ 官方保证）
- 内存占用比旧版减少约 20-25%
```

### 常用方法与时间复杂度

| 操作 | 方法 | 复杂度 | 备注 |
|------|------|--------|------|
| 查找 | `d[k]` | O(1) 均摊 | key 不存在抛 KeyError |
| 安全查找 | `d.get(k, default)` | O(1) 均摊 | 不存在返回默认值 |
| 插入/更新 | `d[k] = v` | O(1) 均摊 | |
| 删除 | `del d[k]` / `pop(k)` | O(1) 均摊 | |
| 存在判断 | `k in d` | O(1) | |
| 遍历 | `.items()` / `.keys()` | O(1) 返回视图，O(n) 遍历 | 视图对象，非拷贝 |
| 合并（Python 3.9+）| `d1 \| d2` | O(n) | |
| 默认值 | `setdefault(k, v)` | O(1) | 不存在时才设置 |
| 批量初始化 | `fromkeys(keys, val)` | O(n) | |

### 典型应用场景（含代码）

**① 频率统计**
```python
from collections import Counter, defaultdict

# 方法一：Counter（推荐）
freq = Counter("abracadabra")
print(freq.most_common(3))          # [('a', 5), ('b', 2), ('r', 2)]

# 方法二：defaultdict
freq2 = defaultdict(int)
for c in "abracadabra":
    freq2[c] += 1

# 方法三：手写（理解原理）
freq3 = {}
for c in "abracadabra":
    freq3[c] = freq3.get(c, 0) + 1
```

**② 两数之和（哈希 + 补数查找）**
```python
def twoSum(nums, target):
    seen = {}                        # {数值: 下标}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:       # O(1) 查找
            return [seen[complement], i]
        seen[num] = i
```

**③ 图的邻接表**
```python
from collections import defaultdict

# 构建有向图
graph = defaultdict(list)
edges = [(0,1),(0,2),(1,3),(2,3)]
for u, v in edges:
    graph[u].append(v)
# graph: {0:[1,2], 1:[3], 2:[3]}

# 带权邻接表
weighted = defaultdict(list)
for u, v, w in [(0,1,5),(0,2,3),(1,3,2)]:
    weighted[u].append((v, w))
```

---

## 2.4 集合 `set` — 哈希集合

### 核心术语
| 术语 | 定义 |
|------|------|
| 哈希集合 | 只存 key（无 value）的哈希表，查找/插入/删除均 O(1) |
| frozenset | 不可变集合，可哈希，可作为 dict 键 |
| 集合运算 | 并集 `\|`，交集 `&`，差集 `-`，对称差 `^` |

### 典型应用场景（含代码）

**① BFS/DFS 的 visited 集合**
```python
from collections import deque

def bfs(graph, start):
    visited = set()                  # 用 set 而非 list，O(1) 查找
    queue = deque([start])
    visited.add(start)

    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:  # O(1) 判断，若用 list 则 O(n)
                visited.add(neighbor)
                queue.append(neighbor)
```

**② 求两个列表的公共元素**
```python
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]

# 集合交集：O(min(m,n))
common = set(a) & set(b)            # {3, 4, 5}

# 在 a 中不在 b 中
only_a = set(a) - set(b)            # {1, 2}
```

---

## 2.5 双端队列 `collections.deque` — 块状双向链表

### 核心术语
| 术语 | 定义 |
|------|------|
| 双向链表 | 每个节点有前驱和后继指针，两端均可 O(1) 增删 |
| 块状链表 | deque 的实际实现：由固定大小内存块（约 64 字节）组成的双向链表，平衡了链表灵活性和数组缓存友好性 |
| maxlen | 指定最大长度，超出后自动从另一端丢弃，实现有界环形缓冲区 |
| 单调队列 | deque 内元素保持单调性（递增/递减），用于 O(n) 求滑动窗口极值 |

### 底层结构
```
deque 由若干固定大小的"块"组成，块间用双向链表连接：
←→ [block0: e0,e1,...,e7] ←→ [block1: e8,...,e15] ←→ ...
    ↑ leftblock/leftindex        ↑ rightblock/rightindex

两端操作只需移动 leftindex / rightindex，不涉及数据移动 → O(1)
```

### 常用方法与时间复杂度

| 操作 | 方法 | 复杂度 |
|------|------|--------|
| 右端追加 | `append(x)` | O(1) |
| 左端追加 | `appendleft(x)` | O(1) |
| 右端弹出 | `pop()` | O(1) |
| 左端弹出 | `popleft()` | O(1) |
| 随机访问 | `dq[i]` | O(n) ⚠️ 非连续内存 |
| 旋转 | `rotate(n)` | O(k) |
| 查找 | `x in dq` | O(n) |

### 典型应用场景（含代码）

**① BFS 标准队列**
```python
from collections import deque

def bfs_shortest_path(graph, start, end):
    """BFS 求无权图最短路径长度"""
    queue = deque([(start, 0)])      # (节点, 距离)
    visited = {start}

    while queue:
        node, dist = queue.popleft() # 从左端取出（FIFO）
        if node == end:
            return dist

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))  # 从右端加入
    return -1
```

**② 单调队列（滑动窗口最大值）**
```python
from collections import deque

def sliding_window_max(nums, k):
    """O(n) 求每个大小为 k 的窗口内的最大值"""
    dq = deque()    # 存下标，对应值单调递减（队首最大）
    result = []

    for i, num in enumerate(nums):
        # ① 移除不在窗口内的队首（过期元素）
        if dq and dq[0] < i - k + 1:
            dq.popleft()

        # ② 维护单调递减：移除所有比当前值小的队尾
        #    （它们比 num 更早入队且更小，永远不可能是窗口最大值）
        while dq and nums[dq[-1]] < num:
            dq.pop()

        dq.append(i)

        # ③ 窗口形成后记录答案（队首下标对应值就是当前窗口最大值）
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
```

---

## 2.6 堆 `heapq` — 最小二叉堆

### 核心术语
| 术语 | 定义 |
|------|------|
| 完全二叉树 | 除最后一层外都填满，最后一层从左至右填充的二叉树 |
| 堆性质（小根堆）| 每个节点的值 ≤ 其左右子节点的值，因此根节点是全局最小值 |
| 堆化（Heapify）| 将任意数组调整为满足堆性质的过程，O(n)（非 O(n log n)）|
| 上浮（Sift Up）| 新元素插入堆尾，不断与父节点比较上移，维护堆性质 |
| 下沉（Sift Down）| 删除堆顶后将末尾元素放到顶部，不断与子节点比较下移 |
| 优先队列 | 基于堆实现的抽象数据结构，每次出队优先级最高（最小/最大）的元素 |

### 底层结构
```
堆用数组表示完全二叉树：
数组: [1, 3, 2, 7, 4, 5, 6]
       0  1  2  3  4  5  6

对应树:
        1        ← index 0
      /   \
     3     2     ← index 1, 2
    / \   / \
   7   4 5   6   ← index 3,4,5,6

父节点 i → 左子 2i+1，右子 2i+2
子节点 j → 父节点 (j-1)//2
```

### 常用操作

```python
import heapq

# 建堆（原地，O(n)）
nums = [5, 3, 8, 1, 9]
heapq.heapify(nums)             # 原地变为小根堆：[1,3,8,5,9]

# 入堆（O(log n)）
heapq.heappush(nums, 2)

# 出堆（返回最小值，O(log n)）
smallest = heapq.heappop(nums)

# 查看堆顶（O(1)，不弹出）
top = nums[0]

# 最大堆：存负数技巧
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -1)
max_val = -heapq.heappop(max_heap)   # 1 是最大值

# 带优先级的元素（元组比较按字典序）
heapq.heappush(h, (priority, item))
```

### 典型应用场景（含代码）

**① TopK 最大元素（维护大小 K 的小根堆）**
```python
import heapq

def topK_largest(nums, k):
    """
    维护一个大小为 k 的小根堆。
    堆顶是当前 k 个最大值里最小的。
    若新元素比堆顶大，替换堆顶，保证堆始终是最大的 k 个元素。
    """
    heap = nums[:k]
    heapq.heapify(heap)             # O(k) 建堆

    for num in nums[k:]:
        if num > heap[0]:           # 比当前 k 个最大值中最小的还大
            heapq.heapreplace(heap, num)   # 替换堆顶，O(log k)

    return sorted(heap, reverse=True)

# 示例：[3,1,5,12,2,11] 中 Top3 最大 → [12, 11, 5]
```

**② 合并 K 个有序列表**
```python
import heapq

def mergeKLists(lists):
    """
    多路归并：用小根堆维护每个列表当前最小元素。
    每次取出全局最小，推入其下一个元素。
    """
    heap = []
    result = []

    # 初始化：每个列表的第一个元素入堆
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))   # (值, 列表索引, 元素索引)

    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        # 推入同列表下一个元素
        if elem_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))

    return result
```

---

## 2.7 `Counter` — 计数哈希

```python
from collections import Counter

# 构建
c = Counter("abracadabra")          # 字符计数
c = Counter([1,1,2,3,3,3])         # 列表元素计数
c = Counter({'a': 3, 'b': 2})      # 从字典构建

# 常用操作
c.most_common(3)                    # 前3高频元素：[('a',5),('b',2),('r',2)]
c['z']                              # 不存在的键返回 0（不抛 KeyError）
c.total()                           # 所有计数之和（Python 3.10+）
+c                                  # 删除计数 <= 0 的键

# 集合运算
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
c1 + c2   # Counter({'a':4,'b':3})  合并
c1 - c2   # Counter({'a':2})        差集（只保留正数）
c1 & c2   # Counter({'a':1,'b':1}) 各键取最小
c1 | c2   # Counter({'a':3,'b':2}) 各键取最大
```

### 典型应用：字母异位词判断
```python
# 判断两个字符串是否互为字母异位词
def isAnagram(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)   # O(n)，比排序 O(n log n) 更优
```

---

## 2.8 手写链表 `ListNode`

### 核心术语
| 术语 | 定义 |
|------|------|
| 哨兵节点（Dummy Node）| 在链表头前增加一个虚拟节点，统一处理头节点的边界情况 |
| 快慢指针 | 两个指针速度不同（fast 走两步，slow 走一步），用于找中点/检测环 |
| Floyd 判圈算法 | 快慢指针检测链表是否有环：若有环，fast 和 slow 必然相遇 |

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# 构建链表：1 → 2 → 3 → None
def build_list(vals):
    dummy = ListNode(0)
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

# 转为列表（用于调试）
def to_list(head):
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result
```

### 典型应用场景（含代码）

**① 哨兵节点简化头部操作**
```python
def removeElements(head, val):
    """删除所有值为 val 的节点"""
    dummy = ListNode(0, head)    # 哨兵节点
    cur = dummy
    while cur.next:
        if cur.next.val == val:
            cur.next = cur.next.next   # 跳过该节点
        else:
            cur = cur.next
    return dummy.next            # 返回真实头节点

# 优点：无需单独处理 head 被删除的情况
```

**② 快慢指针找链表中点**
```python
def findMiddle(head):
    """快慢指针：fast 走两步，slow 走一步，fast 到尾时 slow 在中点"""
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next   # fast 速度是 slow 的两倍
    return slow                 # slow 停在中点（偶数长度取后中点）
```

**③ Floyd 判圈（环检测）**
```python
def hasCycle(head):
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:        # 指针相遇 → 有环
            return True
    return False                # fast 到 None → 无环
```

---

## 2.9 并查集 `UnionFind` — 手写

### 核心术语
| 术语 | 定义 |
|------|------|
| 路径压缩 | find 操作时将沿途所有节点直接挂到根节点，降低后续操作复杂度 |
| 按秩合并 | union 时将较矮树挂到较高树下，防止退化为链表 |
| α(n) | 阿克曼函数的反函数，路径压缩+按秩合并后 find/union 的均摊复杂度，实际场景中视为 O(1) |

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))    # 初始时每个节点的父节点是自己
        self.rank = [0] * n             # 树高（按秩合并用）
        self.count = n                  # 连通分量数

    def find(self, x):
        """查找 x 的根节点（路径压缩）"""
        if self.parent[x] != x:
            # 递归压缩：将 x 直接挂到根节点
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """合并 x 和 y 所在集合（按秩合并）"""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False            # 已在同一集合，加此边会成环
        # 矮树挂到高树下，防止退化
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.count -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)
```

### 典型应用：动态连通性
```python
# 判断图中有多少连通分量
def countComponents(n, edges):
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count
```


---

# 第三部分：算法思想

---

## 3.1 双指针（Two Pointers）

### 核心术语
| 术语 | 定义 |
|------|------|
| 对撞指针 | left 从头、right 从尾，向中间移动，利用有序性每步排除一侧不可能的答案 |
| 快慢指针 | 同向出发，fast 速度更快（走两步），用于找中点、检测环、删除倒数第 K 个 |
| 同向指针 | 两指针同向移动，速度可相同或不同，通常是滑动窗口的基础形式 |
| 单调性 | 对撞指针有效的前提：问题在某个维度上具有单调性，移动某端能明确缩小搜索空间 |

### 核心思想
```
暴力两层循环 O(n²) → 双指针 O(n)
前提：有序数组 或 问题具有单调性

对撞指针示意：
[l] → → →     ← ← ← [r]
      相遇停止

快慢指针示意（链表）：
slow → → →
fast → → → → → →
slow 走1步，fast 走2步，fast 到尾时 slow 在中点
```

### 三种模式代码模板

```python
# ① 对撞指针（有序数组，两数之和）
def two_pointer_collision(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return [left, right]
        elif s < target:
            left += 1      # 和太小，增大左端
        else:
            right -= 1     # 和太大，减小右端

# ② 快慢指针（链表中点）
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow

# ③ 同向双指针（删除有序数组重复项）
def remove_duplicates(nums):
    slow = 0                           # slow 指向下一个写入位置
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:   # 发现新元素
            slow += 1
            nums[slow] = nums[fast]    # 写入新位置
    return slow + 1
```

### 典型应用场景（含代码）

**① 有序数组两数之和**
```python
def twoSum_sorted(numbers, target):
    """
    利用数组有序性：
    - 两数之和 < target → 需要更大的数 → left 右移
    - 两数之和 > target → 需要更小的数 → right 左移
    时间 O(n)，空间 O(1)
    """
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:   return [l+1, r+1]
        elif s < target:  l += 1
        else:             r -= 1
```

**② 判断链表是否有环（Floyd 判圈）**
```python
def hasCycle(head):
    """
    快慢指针：若有环，fast 终将追上 slow（类比操场跑圈）
    若无环，fast 会先到达 None
    """
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:   # 相遇 → 有环
            return True
    return False
```

**③ 盛最多水（对撞指针 + 单调性证明）**
```python
def maxArea(height):
    """
    容积 = min(h[l], h[r]) × (r - l)
    移动较矮的一边：宽度必然减小，但有机会遇到更高的板
    移动较高的一边：宽度减小且高度不会增大，面积必然不增
    → 贪心地移动较矮端，才有可能找到更大面积
    """
    l, r = 0, len(height) - 1
    ans = 0
    while l < r:
        ans = max(ans, min(height[l], height[r]) * (r - l))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return ans
```

---

## 3.2 滑动窗口（Sliding Window）

### 核心术语
| 术语 | 定义 |
|------|------|
| 窗口（Window）| [left, right) 区间内的子数组/子串，是当前考察的连续段 |
| 右扩（Expand）| right 指针右移，将新元素纳入窗口 |
| 左缩（Shrink）| left 指针右移，将旧元素移出窗口，恢复合法状态 |
| 窗口状态 | 描述当前窗口内内容的数据结构（如字符计数的 dict） |
| 定长窗口 | 窗口大小固定为 k，整体平移；每步移除最左加入最右 |
| 变长窗口 | 窗口大小随合法性条件动态调整，是更通用的形式 |

### 核心思想
```
关键洞察：子数组是连续的 → 相邻子数组只有两端元素变化
          → 可以在 O(1) 内从旧窗口状态推导新窗口状态
          → 避免重复计算，将 O(n²) 降至 O(n)

变长窗口标准流程：
right 持续向右扩展
  → 窗口不满足条件：left 向右收缩，直到合法
  → 每步更新答案
```

### 通用模板
```python
def sliding_window_template(s):
    window = {}                          # 窗口内状态（字符计数等）
    left = right = 0
    ans = 0

    while right < len(s):
        # ① 扩大窗口，纳入 s[right]
        c = s[right]
        right += 1
        window[c] = window.get(c, 0) + 1

        # ② 判断窗口是否需要收缩
        while 窗口不合法的条件:
            d = s[left]
            left += 1
            # 更新窗口状态（移除 s[left]）
            window[d] -= 1
            if window[d] == 0:
                del window[d]

        # ③ 更新答案（此时窗口合法）
        ans = max(ans, right - left)

    return ans
```

### 典型应用场景（含代码）

**① 最长无重复字符子串**
```python
def lengthOfLongestSubstring(s):
    """
    窗口内维护字符集合（set），保证无重复。
    right 右移加入新字符，若重复则 left 右移直到无重复。
    """
    window = set()
    left = 0
    ans = 0

    for right in range(len(s)):
        # 有重复，收缩左端直到移除重复字符
        while s[right] in window:
            window.remove(s[left])
            left += 1
        window.add(s[right])
        ans = max(ans, right - left + 1)

    return ans
# 时间 O(n)，空间 O(字符集大小)
```

**② 定长窗口：子数组最大平均值**
```python
def findMaxAverage(nums, k):
    """
    定长窗口：初始计算前 k 个元素之和，之后每步加右减左滑动。
    避免每次重新求和（O(k) → O(1) 的增量更新）
    """
    window_sum = sum(nums[:k])       # 初始窗口
    max_sum = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # 加入右端，移除左端
        max_sum = max(max_sum, window_sum)

    return max_sum / k
```

**③ 变长窗口：最小覆盖子串**
```python
from collections import defaultdict

def minWindow(s, t):
    """
    需要找包含 t 所有字符的最短子串。
    维护 need（目标计数）和 window（当前计数），
    valid 记录已满足的字符种类数，valid == len(need) 表示窗口合法。
    合法时收缩左端，记录更小的合法窗口。
    """
    need = defaultdict(int)
    for c in t: need[c] += 1

    window = defaultdict(int)
    left = right = 0
    valid = 0           # 已满足数量要求的字符种类数
    start, min_len = 0, float('inf')

    while right < len(s):
        c = s[right]; right += 1
        if c in need:
            window[c] += 1
            if window[c] == need[c]:   # 该字符数量刚好满足
                valid += 1

        while valid == len(need):      # 窗口合法，尝试收缩
            if right - left < min_len:
                min_len = right - left; start = left
            d = s[left]; left += 1
            if d in need:
                if window[d] == need[d]:  # 收缩后该字符不再满足
                    valid -= 1
                window[d] -= 1

    return s[start:start+min_len] if min_len != float('inf') else ""
```

---

## 3.3 哈希（Hashing）

### 核心术语
| 术语 | 定义 |
|------|------|
| 哈希函数 | key → index 的映射函数，理想情况下均匀分布，计算 O(1) |
| 哈希碰撞 | 两个不同 key 映射到相同 index，需要冲突解决策略 |
| 开放寻址 | 碰撞时在表内找下一个空槽（Python dict 使用），缓存友好但删除复杂 |
| 链地址法 | 碰撞时槽位挂链表（Java HashMap），实现简单但有额外指针开销 |
| 装载因子 | 元素数/槽位数，Python dict 超过 2/3 时扩容（约 4 倍），保证操作均摊 O(1) |
| 哈希攻击 | 故意构造大量碰撞，使哈希表退化为 O(n)，Python 引入随机种子防御 |
| 前缀和+哈希 | 将子数组和问题转化为两个前缀和之差，结合哈希表 O(1) 查找 |

### 核心思想
```
目的：以 O(1) 均摊时间完成"我之前见过 X 吗？" 或 "X 出现了多少次？"

常见范式：
① 计数    → Counter / defaultdict(int)
② 存补数  → seen[target - num] 是否存在（两数之和）
③ 存前缀  → prefix_count[prefix_sum - k] 是否存在（子数组和）
④ 存分组  → groups[normalized_key].append(item)（字母异位词分组）
```

### 典型应用场景（含代码）

**① 前缀和 + 哈希（子数组和为 K）**
```python
from collections import defaultdict

def subarraySum(nums, k):
    """
    核心公式：sum(l..r) = prefix[r+1] - prefix[l]
    若 prefix[r+1] - prefix[l] = k，则 prefix[l] = prefix[r+1] - k
    → 遍历时用哈希表存已有的前缀和出现次数，O(1) 查找 prefix[l]

    注意：prefix_count[0]=1 是哨兵，处理子数组从下标0开始的情况
    """
    prefix_count = defaultdict(int)
    prefix_count[0] = 1     # 前缀和为0，出现1次（空前缀）
    prefix_sum = 0
    count = 0

    for num in nums:
        prefix_sum += num
        # 查找有多少个前缀和等于 prefix_sum - k
        count += prefix_count[prefix_sum - k]
        prefix_count[prefix_sum] += 1

    return count
```

**② 字符串哈希（字母异位词分组）**
```python
from collections import defaultdict

def groupAnagrams(strs):
    """
    异位词排序后相同 → 用排序后的字符串作哈希键
    进阶：用字符计数元组作键，O(k) 而非 O(k log k)
    """
    groups = defaultdict(list)
    for s in strs:
        # 字符计数元组作为键（26个字母的频次）
        count = [0] * 26
        for c in s: count[ord(c) - ord('a')] += 1
        groups[tuple(count)].append(s)
    return list(groups.values())
```

**③ 最长连续序列（哈希集合）**
```python
def longestConsecutive(nums):
    """
    核心思想：只从序列起点（num-1 不在集合中）开始向右延伸计数。
    每个元素最多被访问两次（一次判断是否起点，一次延伸时经过）→ O(n)
    """
    num_set = set(nums)
    ans = 0

    for num in num_set:
        if num - 1 not in num_set:      # num 是序列起点
            cur, length = num, 1
            while cur + 1 in num_set:   # 向右延伸
                cur += 1; length += 1
            ans = max(ans, length)

    return ans
```

---

## 3.4 二分查找（Binary Search）

### 核心术语
| 术语 | 定义 |
|------|------|
| 单调性 | 二分的本质前提：在某个维度上，答案一侧满足条件，另一侧不满足，具有明确的"分界线" |
| 左边界 | 满足条件的**最左**位置（第一个 >= target 的下标） |
| 右边界 | 满足条件的**最右**位置（最后一个 <= target 的下标） |
| 答案二分 | 不是在数组下标上二分，而是在**答案的可能值范围**上二分，用 check(mid) 验证 |
| 开/闭区间 | 搜索区间的写法影响终止条件和边界更新：`[l,r]` 闭区间用 `l<=r`；`[l,r)` 半开用 `l<r` |

### 三种经典写法
```python
# ① 精确查找（闭区间 [left, right]）
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:                      # 区间非空
        mid = left + (right - left) // 2      # 防溢出
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# ② 左边界（第一个 >= target 的位置）半开区间 [left, right)
def left_bound(nums, target):
    left, right = 0, len(nums)            # right 是开区间端点
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid                   # mid 可能是答案，保留
    return left                           # left == right 时退出

# ③ 右边界（最后一个 <= target 的位置）
def right_bound(nums, target):
    left, right = 0, len(nums)
    while left < right:
        mid = (left + right) // 2
        if nums[mid] <= target:
            left = mid + 1                # mid 的值符合，但试图找更右的
        else:
            right = mid
    return left - 1                       # 最后一个符合条件的位置
```

### 典型应用场景（含代码）

**① 在答案上二分（最小化最大值）**
```python
def shipWithinDays(weights, days):
    """
    船的最小承重能力二分搜索。
    答案范围：[max(weights), sum(weights)]
    check(cap)：以承重 cap 能否在 days 天内运完？
    找满足 check 的最小 cap。
    """
    def can_ship(capacity):
        day_used, load = 1, 0
        for w in weights:
            if load + w > capacity:   # 装不下，开新的一天
                day_used += 1; load = 0
            load += w
        return day_used <= days

    left, right = max(weights), sum(weights)
    while left < right:
        mid = (left + right) // 2
        if can_ship(mid):
            right = mid               # 能完成，试试更小
        else:
            left = mid + 1            # 不能完成，需要更大
    return left
```

**② bisect 模块（有序插入/查找）**
```python
import bisect

# 维护有序数组，查询 >= target 的位置
arr = [1, 3, 5, 7, 9]
pos = bisect.bisect_left(arr, 6)    # 4（第一个>=6的位置是下标4）
bisect.insort(arr, 6)               # 插入后仍有序：[1,3,5,6,7,9]

# LIS（最长递增子序列）O(n log n) 解法用到 bisect
def lengthOfLIS(nums):
    tails = []                       # tails[i] = 长度i+1的递增子序列末尾最小值
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)        # 可以延伸最长子序列
        else:
            tails[pos] = num         # 替换，让末尾尽量小（贪心）
    return len(tails)
```

---

## 3.5 递归与分治（Recursion & Divide and Conquer）

### 核心术语
| 术语 | 定义 |
|------|------|
| 递归 | 函数调用自身，将问题规模缩小，直到触达 base case |
| Base Case（基础情况）| 递归的终止条件，直接返回结果，不再调用自身 |
| 递归栈（Call Stack）| 每次函数调用占用一帧栈内存，深度过大导致 Stack Overflow |
| 分治（Divide & Conquer）| 将问题分为若干**相互独立**的子问题，分别求解后合并结果 |
| 尾递归 | 递归调用是函数最后一步（Python 不优化尾递归，仍可能溢出）|
| 记忆化 | 用字典缓存 `(参数) → 结果`，避免相同子问题重复计算（动态规划的自顶向下形式）|

### 核心思想
```
分治三步骤：
① Divide  — 将 problem(n) 拆为若干 problem(n/k)
② Conquer — 递归求解各子问题
③ Combine — 合并子问题结果

关键：子问题必须相互独立（否则用 DP）
时间复杂度由主定理分析
```

### 典型应用场景（含代码）

**① 归并排序（分治 + 合并）**
```python
def merge_sort(nums):
    """
    分：每次对半拆分
    治：递归排序左右两半
    合：合并两个有序数组（O(n) 的 merge 操作）
    T(n) = 2T(n/2) + O(n) → O(n log n)
    """
    if len(nums) <= 1:
        return nums

    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])

    # 合并两个有序数组
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result
```

**② 二叉树后序遍历（分治思维）**
```python
def maxPathSum(root):
    """
    二叉树中最大路径和（路径可不经过根）
    分治：对每个节点，计算经过它的最大路径（左贡献 + 节点 + 右贡献）
    子问题：left_gain = 左子树能提供的最大正贡献值
    """
    ans = float('-inf')

    def dfs(node):
        nonlocal ans
        if not node: return 0

        # 只有正贡献才纳入（负贡献不如不选）
        left_gain = max(dfs(node.left), 0)
        right_gain = max(dfs(node.right), 0)

        # 经过当前节点的最大路径
        ans = max(ans, node.val + left_gain + right_gain)

        # 向父节点返回：只能选左或右（路径不能分叉）
        return node.val + max(left_gain, right_gain)

    dfs(root)
    return ans
```

**③ 记忆化递归（斐波那契 → 展示优化思路）**
```python
from functools import lru_cache

@lru_cache(maxsize=None)         # 自动记忆化，等价于 memo = {}
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)  # 子问题有重叠 → 记忆化后 O(n)

# 不加缓存：O(2^n)（大量重复计算）
# 加缓存后：每个 fib(k) 只计算一次 → O(n)
```

---

## 3.6 动态规划（Dynamic Programming）

### 核心术语
| 术语 | 定义 |
|------|------|
| 状态（State）| 描述子问题的参数，如 `dp[i]`、`dp[i][j]`，需完整刻画子问题 |
| 状态转移方程 | 当前状态如何由之前状态推导，是 DP 的核心 |
| 初始化（Base Case）| dp 数组的边界值，对应最小规模子问题的答案 |
| 遍历顺序 | 保证计算 `dp[i]` 时所依赖的子状态已经计算好 |
| 滚动数组 | 空间优化技术：若 dp[i] 只依赖 dp[i-1]，可用两行（或一行）交替使用 |
| 推导方向 | 有时需要从后往前遍历（如 0/1 背包的一维压缩），防止同一物品被用多次 |

### DP 设计四步骤
```
① 定义状态：dp[i] 或 dp[i][j] 表示什么？（通常是题目要求的目标量）
② 写转移方程：dp[i] 与哪些之前状态有关？关系式是什么？
③ 确定初始化：base case 是什么？
④ 确定遍历顺序：外层循环遍历什么？内层遍历什么？
```

### 典型应用场景（含代码）

**① 线性 DP：最大子数组和（Kadane 算法）**
```python
def maxSubArray(nums):
    """
    dp[i] = 以 nums[i] 结尾的最大子数组和
    转移：dp[i] = nums[i] + max(dp[i-1], 0)
    含义：若前面的子数组和为负，不如丢弃重新开始

    空间优化：dp[i] 只依赖 dp[i-1]，用变量代替数组
    """
    cur_max = nums[0]   # dp[i]，以 nums[i] 结尾的最大和
    global_max = nums[0]

    for num in nums[1:]:
        # 若 cur_max < 0，加上它只会变小，不如重新从 num 开始
        cur_max = num + max(cur_max, 0)
        global_max = max(global_max, cur_max)

    return global_max
```

**② 背包 DP（0/1背包）**
```python
def knapsack01(weights, values, capacity):
    """
    dp[j] = 容量为 j 的背包能装的最大价值
    关键：内层循环从后往前（capacity → weight[i]）
    原因：防止同一物品被选多次
    （从后往前时，dp[j-w] 还是上一轮的值，即不含第 i 件物品时的状态）
    """
    dp = [0] * (capacity + 1)

    for i in range(len(weights)):
        w, v = weights[i], values[i]
        for j in range(capacity, w - 1, -1):  # 从后往前！
            # 选或不选第 i 件物品
            dp[j] = max(dp[j], dp[j - w] + v)

    return dp[capacity]

# 完全背包（每件物品无限次）：内层正向遍历
def knapsack_complete(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        w, v = weights[i], values[i]
        for j in range(w, capacity + 1):       # 正向！允许重复选
            dp[j] = max(dp[j], dp[j - w] + v)
    return dp[capacity]
```

**③ 序列 DP：编辑距离**
```python
def minDistance(word1, word2):
    """
    dp[i][j] = word1[:i] 变为 word2[:j] 的最少操作数
    转移：
      若 word1[i-1] == word2[j-1]：dp[i][j] = dp[i-1][j-1]（不需操作）
      否则取三种操作的最小值 + 1：
        dp[i-1][j]   → 删除 word1[i-1]
        dp[i][j-1]   → 插入 word2[j-1]
        dp[i-1][j-1] → 替换 word1[i-1] 为 word2[j-1]
    """
    m, n = len(word1), len(word2)
    dp = [[0]*(n+1) for _ in range(m+1)]

    for i in range(m+1): dp[i][0] = i   # word1 变为空串：删 i 次
    for j in range(n+1): dp[0][j] = j   # 空串变为 word2：插 j 次

    for i in range(1, m+1):
        for j in range(1, n+1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1

    return dp[m][n]
```

---

## 3.7 贪心（Greedy）

### 核心术语
| 术语 | 定义 |
|------|------|
| 贪心选择性 | 每步选局部最优不影响后续的最优性，即不会"后悔" |
| 最优子结构 | 全局最优解包含子问题的最优解 |
| 交换论证 | 证明贪心正确性的常用方法：假设最优解不使用贪心策略，将其"交换"为贪心选择后证明不变差 |
| 反例驱动 | 贪心策略错误时，构造一个反例即可推翻；证明正确需要严格证明 |

### 典型应用场景（含代码）

**① 区间调度（按结束时间贪心）**
```python
def eraseOverlapIntervals(intervals):
    """
    最少移除区间数 = 总数 - 最多不重叠区间数
    贪心策略：按结束时间排序，优先选结束早的区间。
    直觉：结束早的区间"占用时间"少，给后续区间留更多空间。
    证明（交换论证）：若最优解不选某个结束最早的区间 A，
                      而选了和 A 重叠且结束更晚的区间 B，
                      将 B 换成 A 后重叠数不增 → 贪心不差。
    """
    intervals.sort(key=lambda x: x[1])   # 按结束时间排序
    ans = 0
    end = float('-inf')

    for start, finish in intervals:
        if start >= end:           # 不重叠，选择此区间
            end = finish
        else:
            ans += 1               # 重叠，删除（不选当前）

    return ans
```

**② 跳跃游戏（维护最远可达）**
```python
def canJump(nums):
    """
    贪心：遍历每个位置，维护从该位置出发能到达的最远下标。
    若当前位置 i > max_reach，说明无法到达 i，返回 False。
    """
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False               # 当前位置已无法到达
        max_reach = max(max_reach, i + jump)
    return True
```

---

## 3.8 广度优先搜索（BFS）

### 核心术语
| 术语 | 定义 |
|------|------|
| 层序扩展 | BFS 按"距离起点的步数"逐层访问，第 k 层所有节点距起点恰好 k 步 |
| 最短路保证 | 无权图中，BFS 首次到达某节点时的步数，就是最短路长度 |
| visited 集合 | 记录已访问节点，防止重复入队（否则可能死循环或重复计算）|
| 多源 BFS | 将多个起点同时加入初始队列，等价于新建一个超级源点连向所有起点 |
| 双向 BFS | 从起点和终点同时 BFS，两侧相遇时停止，搜索空间从 O(b^d) 降至 O(2b^(d/2)) |

### 标准框架
```python
from collections import deque

def bfs(graph, start, target):
    queue = deque([(start, 0)])    # (节点, 距离)
    visited = {start}

    while queue:
        # 写法一：整层处理（需要知道层数）
        for _ in range(len(queue)):
            node, dist = queue.popleft()
            if node == target: return dist
            for nb in graph[node]:
                if nb not in visited:
                    visited.add(nb)
                    queue.append((nb, dist+1))
```

### 典型应用场景（含代码）

**① 网格 BFS（最短路）**
```python
from collections import deque

def shortestPath(grid):
    """
    在 0/1 网格中，从左上到右下的最短路径（只经过 0）。
    BFS 保证第一次到达终点时的步数就是最短。
    """
    n = len(grid)
    if grid[0][0] == 1 or grid[n-1][n-1] == 1:
        return -1

    queue = deque([(0, 0, 1)])    # (行, 列, 步数)
    visited = {(0, 0)}
    dirs = [(dr,dc) for dr in [-1,0,1] for dc in [-1,0,1] if (dr,dc)!=(0,0)]

    while queue:
        r, c, steps = queue.popleft()
        if r == n-1 and c == n-1:
            return steps
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if 0<=nr<n and 0<=nc<n and grid[nr][nc]==0 and (nr,nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc, steps+1))
    return -1
```

**② 多源 BFS（腐烂的橘子）**
```python
from collections import deque

def orangesRotting(grid):
    """
    所有烂橘子同时作为起点（多源），向四周扩散。
    多源 BFS：初始将所有源点入队，之后按层扩展。
    等价于：建立超级源点连向所有烂橘子，BFS 从超级源点出发（但不实际建立）。
    """
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2: queue.append((r, c, 0))
            elif grid[r][c] == 1: fresh += 1

    max_time = 0
    for r, c, t in queue:                  # 注意：遍历 queue 本身（边追加边遍历）
        pass
    # 改用标准 while 循环
    queue = deque()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2: queue.append((r, c, 0))

    while queue:
        r, c, time = queue.popleft()
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==1:
                grid[nr][nc] = 2
                fresh -= 1
                max_time = max(max_time, time+1)
                queue.append((nr, nc, time+1))

    return max_time if fresh == 0 else -1
```

---

## 3.9 深度优先搜索 / 回溯（DFS / Backtracking）

### 核心术语
| 术语 | 定义 |
|------|------|
| 状态树（State Tree）| 回溯过程形成的树形结构，每条从根到叶的路径对应一个候选解 |
| 剪枝（Pruning）| 在搜索过程中提前判断当前分支不可能产生有效解，直接跳过 |
| 做选择 / 撤销选择 | 回溯的核心操作：进入分支前修改状态，退出分支后恢复状态 |
| 去重（去除重复分支）| 有重复元素时，排序后跳过相同元素，避免产生重复结果 |
| 可行性剪枝 | 当前选择已导致问题无解（如剩余容量不足），立即剪枝 |
| 最优性剪枝 | 当前路径的代价已超过已知最优解，立即剪枝 |

### 回溯通用模板
```python
def backtrack(path, start, choices):
    # ① 终止条件（找到一个解）
    if 满足结束条件:
        result.append(path[:])   # 必须复制！path 是引用
        return

    for i in range(start, len(choices)):
        # ② 剪枝
        if 当前选择无效: continue

        # ③ 做选择
        path.append(choices[i])

        # ④ 递归（缩小规模）
        backtrack(path, i+1, choices)   # i+1 避免重复使用

        # ⑤ 撤销选择（回溯）
        path.pop()
```

### 典型应用场景（含代码）

**① 子集枚举**
```python
def subsets(nums):
    """
    每个元素有"选"和"不选"两种状态 → 2^n 个子集
    用 start 控制从哪个位置开始选，保证子集不重复（如不出现[2,1]和[1,2]）
    """
    result, path = [], []

    def backtrack(start):
        result.append(path[:])          # 每个状态都是一个合法子集
        for i in range(start, len(nums)):
            path.append(nums[i])        # 选 nums[i]
            backtrack(i + 1)            # 下一个元素从 i+1 开始（不重复）
            path.pop()                  # 撤销

    backtrack(0)
    return result
```

**② 组合（含剪枝）**
```python
def combinationSum3(k, n):
    """
    从 1-9 中选 k 个不重复数字，使其和为 n。
    剪枝：当前和已超过 n，或剩余数字不够 k 个，直接返回。
    """
    result, path = [], []

    def backtrack(start, remaining):
        if len(path) == k and remaining == 0:
            result.append(path[:])
            return
        for i in range(start, 10):
            if i > remaining: break    # 剪枝：后面的数更大，不可能满足
            if len(path) + (10-i) < k: break  # 剩余数字不够 k 个
            path.append(i)
            backtrack(i + 1, remaining - i)
            path.pop()

    backtrack(1, n)
    return result
```

---

## 3.10 图算法

### 核心术语
| 术语 | 定义 |
|------|------|
| 有向图（Digraph）| 边有方向，u→v 不等于 v→u |
| 无向图 | 边无方向，u-v 表示双向可达 |
| 有向无环图（DAG）| 有向图且无环，可进行拓扑排序 |
| 权重（Weight）| 边上的数值，表示距离/代价/时间等 |
| 最短路 | 两点间边权之和最小的路径 |
| 生成树 | 包含图中所有顶点、无环、连通的子图（n个顶点，n-1条边）|
| 最小生成树（MST）| 边权总和最小的生成树 |
| 松弛操作（Relax）| Dijkstra 的核心步骤：若经过中转点 u 到 v 的代价更小，更新 dist[v] |
| Kahn 算法 | BFS 实现拓扑排序：每次将入度为 0 的节点加入队列，BFS 扩展 |

### 典型应用场景（含代码）

**① 拓扑排序（课程依赖）**
```python
from collections import defaultdict, deque

def topological_sort(n, edges):
    """
    Kahn 算法：BFS 拓扑排序
    每次将入度为 0 的节点加入队列（无前置依赖，可直接处理）
    处理完后更新其后继节点的入度
    若最终处理了 n 个节点 → 无环（DAG）；否则有环
    """
    graph = defaultdict(list)
    in_degree = [0] * n

    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque([i for i in range(n) if in_degree[i] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for nb in graph[node]:
            in_degree[nb] -= 1
            if in_degree[nb] == 0:
                queue.append(nb)

    return order if len(order) == n else []   # 空列表表示有环
```

**② Dijkstra 最短路**
```python
import heapq
from collections import defaultdict

def dijkstra(graph, start, n):
    """
    graph[u] = [(v, w), ...]  有向带权图
    核心：小根堆保证每次取出当前已知距离最小的节点（贪心）
    松弛操作：若 dist[u] + w < dist[v]，更新 dist[v] 并入堆
    注意：同一节点可能多次入堆，出堆时需检查是否过时
    时间复杂度：O((V+E) log V)
    限制：不能有负权边
    """
    dist = [float('inf')] * n
    dist[start] = 0
    heap = [(0, start)]             # (距离, 节点)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]: continue   # 过时记录，跳过
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    return dist
```

**③ 并查集（连通分量 + 判环）**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n              # 连通分量数

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # 路径压缩
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py: return False   # 已连通，加边成环
        if self.rank[px] < self.rank[py]: px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]: self.rank[px] += 1
        self.count -= 1
        return True

# 应用：Kruskal 最小生成树
def kruskal(n, edges):
    """
    按边权从小到大排序，贪心加入不成环的边，直到选了 n-1 条。
    用并查集高效判断是否成环。
    """
    edges.sort(key=lambda e: e[2])   # 按权重排序
    uf = UnionFind(n)
    mst_weight = 0

    for u, v, w in edges:
        if uf.union(u, v):           # 加入不成环的边
            mst_weight += w
            if uf.count == 1:        # 所有节点已连通
                break

    return mst_weight if uf.count == 1 else -1   # -1 表示图不连通
```


---

# 第四部分：面试题精讲

> 难度标注：🟢 简单（Easy）· 🟡 中等（Medium）  
> 原则：经典高频题，覆盖常考场景，与第三部分不重复

---

## 4.1 双指针专题

### 🟢 题1：移动零（LeetCode 283）

**题意**：将数组中所有 0 移到末尾，保持非零元素的相对顺序，要求原地操作。

**思路**：同向双指针。`slow` 指向下一个写入位置，`fast` 扫描非零元素。

```python
def moveZeroes(nums: list[int]) -> None:
    """
    slow：下一个非零元素应该写入的位置
    fast：遍历整个数组

    当 fast 找到非零元素时，写到 slow 位置，slow 前进。
    最后 slow 之后的所有位置填 0。
    """
    slow = 0   # slow 左边都是已处理的非零元素

    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow] = nums[fast]   # 将非零元素移到前面
            slow += 1

    # slow 之后的位置填 0
    for i in range(slow, len(nums)):
        nums[i] = 0

# 示例：[0,1,0,3,12] → [1,3,12,0,0]
# 时间 O(n)，空间 O(1)
```

---

### 🟢 题2：反转字符串（LeetCode 344）

**题意**：原地反转字符数组。

**思路**：对撞指针交换两端，向中间收敛。

```python
def reverseString(s: list[str]) -> None:
    """
    对撞指针：l 从左、r 从右，两两交换，直到相遇。
    每次交换 s[l] 和 s[r]，然后 l++，r--。
    """
    l, r = 0, len(s) - 1
    while l < r:
        s[l], s[r] = s[r], s[l]   # Python 优雅交换
        l += 1
        r -= 1

# 时间 O(n)，空间 O(1)
```

---

### 🟡 题3：颜色分类（LeetCode 75，荷兰国旗问题）

**题意**：数组只含 0、1、2，原地排序，使 0 在前、1 在中、2 在后。要求一趟扫描。

**思路**：三指针。`low` 维护 0 区右边界，`high` 维护 2 区左边界，`mid` 为当前扫描位置。

```python
def sortColors(nums: list[int]) -> None:
    """
    三个区域：
    [0, low)   → 全是 0（已处理）
    [low, mid) → 全是 1（已处理）
    [mid, high] → 待处理
    (high, n)  → 全是 2（已处理）

    mid 扫描到 high 时结束。
    """
    low, mid, high = 0, 0, len(nums) - 1

    while mid <= high:
        if nums[mid] == 0:
            # 0 应该在左区，与 low 交换，两个指针都前进
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1             # 1 已在正确位置，mid 前进
        else:
            # 2 应该在右区，与 high 交换，high 后退
            # 注意：从 high 换来的数还未检查，mid 不前进
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1

# 示例：[2,0,2,1,1,0] → [0,0,1,1,2,2]
# 时间 O(n)，空间 O(1)，一趟扫描
```

---

### 🟡 题4：接雨水（LeetCode 42）⭐ 经典

**题意**：给定高度数组，计算能接多少雨水。

**思路**：对撞指针。每个位置能接的雨水量 = `min(左侧最高, 右侧最高) - 自身高度`。  
用左右指针维护左/右侧最大值，每次处理较矮一侧（其对应的 min 已确定）。

```python
def trap(height: list[int]) -> int:
    """
    关键洞察：对于位置 i，接水量 = min(max_left, max_right) - height[i]
    对撞指针：
    - left_max = height[0..l] 的最大值
    - right_max = height[r..n-1] 的最大值
    - 若 left_max <= right_max：位置 l 的接水量由 left_max 决定
      （right_max >= left_max，min 一定是 left_max），处理 l，l++
    - 否则对称处理 r，r--
    """
    l, r = 0, len(height) - 1
    left_max = right_max = 0
    ans = 0

    while l < r:
        left_max = max(left_max, height[l])
        right_max = max(right_max, height[r])

        if left_max <= right_max:
            # l 位置的接水量已确定（短板是 left_max）
            ans += left_max - height[l]
            l += 1
        else:
            # r 位置的接水量已确定（短板是 right_max）
            ans += right_max - height[r]
            r -= 1

    return ans

# 示例：[0,1,0,2,1,0,1,3,2,1,2,1] → 6
# 时间 O(n)，空间 O(1)
```

---

## 4.2 滑动窗口专题

### 🟢 题1：大小为 K 且平均值大于等于阈值的子数组数目（LeetCode 1343）

**题意**：统计长度为 k、平均值 >= threshold 的子数组个数。

**思路**：定长滑动窗口，维护窗口和，等价于判断窗口和是否 >= k * threshold。

```python
def numOfSubarrays(arr: list[int], k: int, threshold: int) -> int:
    """
    定长滑动窗口：固定大小 k，计算窗口和。
    窗口右移：加入新右端元素，减去旧左端元素（增量更新）。
    """
    target = k * threshold
    window_sum = sum(arr[:k])          # 初始窗口
    count = 1 if window_sum >= target else 0

    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]   # 滑动：+右端 -左端
        if window_sum >= target:
            count += 1

    return count

# 时间 O(n)，空间 O(1)
```

---

### 🟡 题2：水果成篮（LeetCode 904）

**题意**：从任意位置开始，每个篮子只能装一种水果，最多两个篮子，能摘多少水果（最长子数组，最多包含两种不同数字）。

**思路**：变长滑动窗口，用 Counter 维护窗口内水果种类数。

```python
from collections import defaultdict

def totalFruit(fruits: list[int]) -> int:
    """
    转化：找最长子数组，其中不同元素最多 2 种。
    变长窗口：window 记录当前窗口内各水果数量。
    当种类数 > 2，收缩左端直到种类数 <= 2。
    """
    window = defaultdict(int)
    left = 0
    ans = 0

    for right, fruit in enumerate(fruits):
        window[fruit] += 1               # 纳入右端水果

        while len(window) > 2:           # 超过 2 种，收缩
            left_fruit = fruits[left]
            window[left_fruit] -= 1
            if window[left_fruit] == 0:
                del window[left_fruit]   # 从窗口移除该种类
            left += 1

        ans = max(ans, right - left + 1) # 当前合法窗口长度

    return ans

# 示例：[1,2,1,2,3] → 4（子数组[1,2,1,2]）
# 时间 O(n)，空间 O(1)（窗口最多3种水果）
```

---

### 🟡 题3：乘积小于 K 的子数组（LeetCode 713）

**题意**：统计乘积严格小于 k 的连续子数组个数。

**思路**：变长滑动窗口。以 right 结尾的合法子数组数量 = `right - left + 1`（固定右端，左端可在 [left, right] 任意位置）。

```python
def numSubarrayProductLessThanK(nums: list[int], k: int) -> int:
    """
    以 right 结尾的合法子数组：[left..right], [left+1..right], ..., [right..right]
    共 right - left + 1 个。
    窗口乘积 >= k 时，left 右移缩小窗口。

    注意：k <= 1 时无任何乘积 < k 的非空子数组（元素均为正整数）。
    """
    if k <= 1:
        return 0

    prod = 1
    left = 0
    ans = 0

    for right in range(len(nums)):
        prod *= nums[right]

        while prod >= k:          # 窗口乘积过大，收缩左端
            prod //= nums[left]
            left += 1

        # 以 right 结尾的合法子数组数量
        ans += right - left + 1

    return ans

# 示例：[10,5,2,6], k=100 → 8
# 时间 O(n)，空间 O(1)
```

---

### 🟡 题4：字符串的排列（LeetCode 567）

**题意**：判断 s2 中是否包含 s1 的某个排列（即 s2 的某个子串是 s1 的字母异位词）。

**思路**：定长滑动窗口（窗口长度 = len(s1)），用两个 Counter 比较。

```python
from collections import Counter

def checkInclusion(s1: str, s2: str) -> bool:
    """
    滑动窗口大小固定为 len(s1)。
    维护窗口字符计数 window，若 window == need，返回 True。

    优化：不直接比较 Counter（O(26)），而是维护"满足条件的字符数" valid。
    """
    if len(s1) > len(s2): return False

    need = Counter(s1)
    window = Counter(s2[:len(s1)])         # 初始窗口
    valid = sum(1 for c in need if window[c] == need[c])
    total = len(need)

    if valid == total: return True

    for i in range(len(s1), len(s2)):
        # 加入右端字符
        in_c = s2[i]
        if in_c in need:
            if window[in_c] == need[in_c]: valid -= 1   # 加入前刚好满足
            window[in_c] += 1
            if window[in_c] == need[in_c]: valid += 1   # 加入后刚好满足

        # 移出左端字符
        out_c = s2[i - len(s1)]
        if out_c in need:
            if window[out_c] == need[out_c]: valid -= 1
            window[out_c] -= 1
            if window[out_c] == need[out_c]: valid += 1

        if valid == total: return True

    return False

# 时间 O(n)，空间 O(1)（字母表大小固定）
```

---

## 4.3 哈希专题

### 🟢 题1：有效的字母异位词（LeetCode 242）

**题意**：判断 t 是否是 s 的字母异位词（字符相同，顺序不同）。

**思路**：统计字符频次，比较两个字符串的字符计数数组。

```python
def isAnagram(s: str, t: str) -> bool:
    """
    方法一：Counter 直接比较（简洁）
    方法二：用长度26的数组计数（更省空间，理解底层）
    """
    if len(s) != len(t): return False

    # 方法二：数组计数
    count = [0] * 26
    for c in s: count[ord(c) - ord('a')] += 1   # s 的字符 +1
    for c in t: count[ord(c) - ord('a')] -= 1   # t 的字符 -1

    # 若所有计数为 0，说明字符完全相同
    return all(x == 0 for x in count)

# 时间 O(n)，空间 O(1)（26个字符固定空间）
```

---

### 🟢 题2：快乐数（LeetCode 202）

**题意**：对一个数反复做"各位数字的平方和"，若最终得到 1 则为快乐数，否则会进入循环。

**思路**：用 set 记录见过的数，若出现重复说明进入循环（不是快乐数）。

```python
def isHappy(n: int) -> bool:
    """
    哈希集合检测循环：若不是快乐数，数字序列必然进入循环。
    用 seen 存访问过的数，重复出现 → 有环 → 不是快乐数。

    进阶：也可用快慢指针（Floyd判圈）替代哈希集合，节省空间。
    """
    def get_next(num):
        total = 0
        while num > 0:
            digit = num % 10        # 取末位数字
            total += digit ** 2
            num //= 10
        return total

    seen = set()
    while n != 1:
        if n in seen: return False  # 出现循环
        seen.add(n)
        n = get_next(n)
    return True

# 时间 O(log n)（每个数字的位数约 log n），空间 O(log n)
```

---

### 🟡 题3：四数相加 II（LeetCode 454）

**题意**：四个长度为 n 的数组 A/B/C/D，统计满足 `a+b+c+d=0` 的四元组数目。

**思路**：将 O(n⁴) 暴力拆分为两个 O(n²)：先统计 A+B 的所有组合，再查 -(C+D) 是否在哈希表中。

```python
from collections import defaultdict

def fourSumCount(nums1, nums2, nums3, nums4) -> int:
    """
    分治 + 哈希：
    ① 枚举 A、B 所有组合，存 ab_sum 的频次到哈希表（O(n²)）
    ② 枚举 C、D 所有组合，查 -(c+d) 在哈希表中的频次（O(n²)）
    总时间 O(n²)，比暴力 O(n⁴) 快很多。
    """
    ab_count = defaultdict(int)
    for a in nums1:
        for b in nums2:
            ab_count[a + b] += 1        # 统计所有 A+B 的和

    count = 0
    for c in nums3:
        for d in nums4:
            target = -(c + d)           # 需要 A+B = -(C+D)
            count += ab_count[target]   # 查哈希表（O(1)）

    return count

# 时间 O(n²)，空间 O(n²)
```

---

### 🟡 题4：找到字符串中所有字母异位词（LeetCode 438）

**题意**：在 s 中找出所有 p 的字母异位词起始下标。

**思路**：定长滑动窗口 + 字符计数差值维护，避免每步 O(26) 的 Counter 比较。

```python
def findAnagrams(s: str, p: str) -> list[int]:
    """
    维护差值数组 diff：diff[c] = window中c的数量 - need中c的数量
    维护 differ（不满足条件的字符种类数）
    differ == 0 时窗口是异位词

    优化：不用 Counter == Counter（每次O(26)），改为维护 differ 计数
    """
    if len(s) < len(p): return []

    diff = {}                        # 字符的"多出"量（正数多了，负数少了）
    for c in p:   diff[c] = diff.get(c, 0) - 1   # need
    for c in s[:len(p)]: diff[c] = diff.get(c, 0) + 1  # window 初始

    differ = sum(1 for v in diff.values() if v != 0)   # 不满足的字符种类数
    result = [0] if differ == 0 else []

    for i in range(len(p), len(s)):
        in_c = s[i]                              # 进入窗口的字符
        out_c = s[i - len(p)]                    # 离开窗口的字符

        # 处理进入的字符
        diff[in_c] = diff.get(in_c, 0) + 1
        if diff[in_c] == 0: differ -= 1
        elif diff[in_c] == 1: differ += 1        # 从0变1，新增不满足

        # 处理离开的字符
        diff[out_c] = diff.get(out_c, 0) - 1
        if diff[out_c] == 0: differ -= 1
        elif diff[out_c] == -1: differ += 1      # 从0变-1，新增不满足

        if differ == 0:
            result.append(i - len(p) + 1)

    return result

# 时间 O(n)，空间 O(1)
```

---

## 4.4 二分查找专题

### 🟢 题1：第一个错误的版本（LeetCode 278）

**题意**：1~n 个版本，从某个版本开始全部是错误的，找到第一个错误版本。API：`isBadVersion(n)`。

**思路**：典型左边界二分，找第一个满足 `isBadVersion(mid) == True` 的位置。

```python
def firstBadVersion(n: int) -> int:
    """
    性质：[good, good, ..., bad, bad, ..., bad]，具有单调性。
    找第一个 bad（左边界二分）。
    mid 是 bad → 答案在左侧（含 mid），right = mid
    mid 是 good → 答案在右侧，left = mid + 1
    """
    left, right = 1, n
    while left < right:
        mid = left + (right - left) // 2    # 防溢出
        if isBadVersion(mid):
            right = mid                     # mid 可能是答案，保留
        else:
            left = mid + 1                  # mid 是好版本，排除
    return left   # left == right，就是第一个坏版本

# 时间 O(log n)，空间 O(1)
```

---

### 🟢 题2：猜数字大小（LeetCode 374）

**题意**：1~n 猜数字，API `guess(num)` 返回 -1（猜大了）、1（猜小了）、0（正确）。

```python
def guessNumber(n: int) -> int:
    """
    标准二分查找框架，根据 guess() 的返回值决定搜索方向。
    """
    left, right = 1, n
    while left <= right:
        mid = left + (right - left) // 2
        result = guess(mid)
        if result == 0:
            return mid
        elif result == 1:         # 猜小了，目标在右侧
            left = mid + 1
        else:                     # 猜大了，目标在左侧
            right = mid - 1
    return -1

# 时间 O(log n)，空间 O(1)
```

---

### 🟡 题3：有序矩阵中第 K 小的元素（LeetCode 378）

**题意**：n×n 矩阵，每行每列均升序，找第 k 小的元素。

**思路**：在答案范围 [matrix[0][0], matrix[n-1][n-1]] 上二分。`check(mid)`：矩阵中 <= mid 的元素个数是否 >= k。

```python
def kthSmallest(matrix: list[list[int]], k: int) -> int:
    """
    答案一定在 [matrix[0][0], matrix[n-1][n-1]] 范围内。
    对答案值二分：check(mid) = 矩阵中有多少元素 <= mid？
    若 count >= k，说明第 k 小 <= mid，right = mid。
    否则 left = mid + 1。

    count(mid) 的计算：利用行有序性，从左下角出发
    - 当前列元素 <= mid → 整列前 row+1 个都 <= mid，列右移
    - 否则行上移
    时间 O(n)。
    """
    n = len(matrix)

    def count_le(mid):
        """统计矩阵中 <= mid 的元素个数"""
        count = 0
        row, col = n - 1, 0              # 从左下角开始
        while row >= 0 and col < n:
            if matrix[row][col] <= mid:
                count += row + 1         # 该列从 0 到 row 都 <= mid
                col += 1                 # 列右移
            else:
                row -= 1                 # 行上移
        return count

    left, right = matrix[0][0], matrix[n-1][n-1]
    while left < right:
        mid = (left + right) // 2
        if count_le(mid) >= k:
            right = mid                  # 第 k 小 <= mid，收缩右端
        else:
            left = mid + 1

    return left

# 时间 O(n log(max-min))，空间 O(1)
```

---

### 🟡 题4：山脉数组的峰顶索引（LeetCode 852）

**题意**：满足山脉性质的数组（先升后降），找峰顶下标。

**思路**：二分。若 `nums[mid] < nums[mid+1]`，峰顶在右侧；否则在左侧（含 mid）。

```python
def peakIndexInMountainArray(arr: list[int]) -> int:
    """
    山脉数组单调性：
    峰顶左侧：arr[i] < arr[i+1]（上升段）
    峰顶右侧：arr[i] > arr[i+1]（下降段）

    二分找第一个满足 arr[mid] > arr[mid+1] 的位置（即峰顶或右侧开始下降的位置）。
    """
    left, right = 0, len(arr) - 1
    while left < right:
        mid = (left + right) // 2
        if arr[mid] < arr[mid + 1]:
            left = mid + 1          # 还在上升段，峰顶在右侧
        else:
            right = mid             # 已到下降段或峰顶，向左收缩（保留 mid）
    return left

# 时间 O(log n)，空间 O(1)
```

---

## 4.5 递归与分治专题

### 🟢 题1：翻转二叉树（LeetCode 226）

**题意**：翻转一棵二叉树（左右镜像）。

**思路**：递归后序遍历，先翻转子树，再交换左右子节点。

```python
def invertTree(root):
    """
    分治：对每个节点，翻转其左右子树，然后交换左右子节点。
    后序遍历（先处理子问题，再处理当前节点）。
    """
    if root is None:
        return None

    # 先递归翻转左右子树（分治）
    left = invertTree(root.left)
    right = invertTree(root.right)

    # 交换左右子节点（合并）
    root.left = right
    root.right = left

    return root

# 时间 O(n)，空间 O(h)（h = 树高，递归栈深度）
```

---

### 🟢 题2：对称二叉树（LeetCode 101）

**题意**：判断一棵二叉树是否轴对称。

**思路**：递归地比较"镜像对称"的两个节点：一个走左子树，另一个走右子树。

```python
def isSymmetric(root) -> bool:
    """
    对称 = 左子树和右子树互为镜像。
    定义 isMirror(l, r)：l 和 r 是否互为镜像。
    条件：
    ① l 和 r 都为 None：对称
    ② 一个 None 一个非 None：不对称
    ③ 值不同：不对称
    ④ 值相同：递归比较 (l.left, r.right) 和 (l.right, r.left)
    """
    def isMirror(l, r):
        if l is None and r is None: return True
        if l is None or r is None: return False
        if l.val != r.val: return False
        # 外侧对比：l.left vs r.right
        # 内侧对比：l.right vs r.left
        return isMirror(l.left, r.right) and isMirror(l.right, r.left)

    return isMirror(root.left, root.right)

# 时间 O(n)，空间 O(h)
```

---

### 🟡 题3：验证二叉搜索树（LeetCode 98）

**题意**：判断一棵二叉树是否是有效的二叉搜索树（BST）。

**思路**：递归传递上下界。每个节点的值必须在 `(min_val, max_val)` 范围内。

```python
def isValidBST(root) -> bool:
    """
    BST 性质：左子树所有节点 < 根 < 右子树所有节点（不是仅左右子节点）。
    递归时传递合法范围 (lo, hi)：
    - 根节点：lo = -inf, hi = +inf
    - 进入左子树：hi 更新为当前节点值（左子树所有值必须 < 当前值）
    - 进入右子树：lo 更新为当前节点值（右子树所有值必须 > 当前值）
    """
    def validate(node, lo, hi):
        if node is None: return True
        if not (lo < node.val < hi): return False   # 不在合法范围内
        return (validate(node.left, lo, node.val) and    # 左子树：上界收紧
                validate(node.right, node.val, hi))      # 右子树：下界收紧

    return validate(root, float('-inf'), float('inf'))

# 时间 O(n)，空间 O(h)
```

---

### 🟡 题4：从前序与中序遍历序列构造二叉树（LeetCode 105）

**题意**：给定前序遍历和中序遍历序列，重构二叉树。

**思路**：前序第一个元素是根，在中序中找到根的位置，左边是左子树，右边是右子树，递归构建。

```python
def buildTree(preorder: list[int], inorder: list[int]):
    """
    前序：[根, 左子树..., 右子树...]
    中序：[左子树..., 根, 右子树...]

    ① 前序第一个元素 = 根节点值
    ② 在中序中找根的位置 idx
    ③ 左子树节点数 = idx（中序中根左边的元素数）
    ④ 递归构建左右子树

    优化：用哈希表预存中序中每个值的位置，O(1) 查找
    """
    idx_map = {val: i for i, val in enumerate(inorder)}   # {值: 中序位置}

    def build(pre_l, pre_r, in_l, in_r):
        """
        preorder[pre_l:pre_r+1] 和 inorder[in_l:in_r+1] 对应同一棵子树
        """
        if pre_l > pre_r: return None

        root_val = preorder[pre_l]                # 前序第一个是根
        root = TreeNode(root_val)

        mid = idx_map[root_val]                   # 根在中序中的位置
        left_size = mid - in_l                    # 左子树节点数

        # 左子树：前序 [pre_l+1, pre_l+left_size]，中序 [in_l, mid-1]
        root.left = build(pre_l+1, pre_l+left_size, in_l, mid-1)
        # 右子树：前序 [pre_l+left_size+1, pre_r]，中序 [mid+1, in_r]
        root.right = build(pre_l+left_size+1, pre_r, mid+1, in_r)

        return root

    return build(0, len(preorder)-1, 0, len(inorder)-1)

# 时间 O(n)，空间 O(n)
```

---

## 4.6 动态规划专题

### 🟢 题1：爬楼梯（LeetCode 70）

**题意**：每次可以爬 1 或 2 个台阶，爬到 n 阶有多少种方法？

**思路**：`dp[i] = dp[i-1] + dp[i-2]`，即斐波那契数列。

```python
def climbStairs(n: int) -> int:
    """
    dp[i] = 到达第 i 阶的方法数
    转移：到 i 阶 = 从 i-1 阶爬1步 + 从 i-2 阶爬2步
    空间优化：只需保留前两个状态
    """
    if n <= 2: return n
    a, b = 1, 2          # dp[1]=1, dp[2]=2
    for _ in range(3, n+1):
        a, b = b, a + b  # 滚动更新
    return b

# 时间 O(n)，空间 O(1)
```

---

### 🟢 题2：使用最小花费爬楼梯（LeetCode 746）

**题意**：`cost[i]` 是从第 i 阶出发的花费，可以选择爬 1 或 2 步，找到到达楼顶的最小花费。

```python
def minCostClimbingStairs(cost: list[int]) -> int:
    """
    dp[i] = 到达第 i 阶的最小花费（到达不需要花费，起跳才花费）
    dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])
    目标：dp[n]（楼顶在 n，超过数组末尾）

    理解：dp[i] 表示站在第 i 个台阶上，已花费的总代价。
    """
    n = len(cost)
    a, b = 0, 0    # dp[0] = dp[1] = 0（起点不花费）

    for i in range(2, n + 1):
        a, b = b, min(b + cost[i-1], a + cost[i-2])

    return b

# 示例：cost = [10,15,20] → 15（从下标1出发，爬2步到顶）
# 时间 O(n)，空间 O(1)
```

---

### 🟡 题3：打家劫舍（LeetCode 198）

**题意**：不能偷相邻的房子，最多能偷多少钱？

```python
def rob(nums: list[int]) -> int:
    """
    dp[i] = 考虑前 i 个房子能偷到的最大金额
    转移：
    - 偷第 i 个：dp[i-2] + nums[i]（上一个不能偷）
    - 不偷第 i 个：dp[i-1]
    dp[i] = max(dp[i-1], dp[i-2] + nums[i])

    空间优化：只需 prev2 和 prev1 两个变量
    """
    if len(nums) == 1: return nums[0]

    prev2, prev1 = 0, 0    # prev2=dp[i-2], prev1=dp[i-1]
    for num in nums:
        cur = max(prev1, prev2 + num)   # 当前最优
        prev2, prev1 = prev1, cur

    return prev1

# 时间 O(n)，空间 O(1)
```

---

### 🟡 题4：不同路径（LeetCode 62）

**题意**：m×n 网格，从左上角到右下角，只能向右或向下移动，有多少种路径？

```python
def uniquePaths(m: int, n: int) -> int:
    """
    dp[i][j] = 到达 (i,j) 的路径数
    转移：dp[i][j] = dp[i-1][j] + dp[i][j-1]（从上面来 + 从左边来）
    初始：第一行和第一列都只有 1 条路径

    空间优化：dp[i][j] 只依赖上一行，用一维数组滚动更新
    """
    dp = [1] * n                       # 初始化：第一行全为 1
    for i in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j-1]           # dp[j] = 上方（旧dp[j]）+ 左方（dp[j-1]）

    return dp[n-1]

# 时间 O(mn)，空间 O(n)
```

---

## 4.7 贪心专题

### 🟢 题1：柠檬水找零（LeetCode 860）

**题意**：每位顾客给 5/10/20 美元买 5 元柠檬水，判断是否总能正确找零。

**思路**：贪心。收到 20 时优先用 10+5（保留更多 5 元，5 元用途更广）。

```python
def lemonadeChange(bills: list[int]) -> bool:
    """
    贪心：收到大额时，优先用大面额找零，保留小面额（5元）以备更多用途。
    收20时：优先用10+5（而非3个5），因为10元只能找零20元用，但5元更通用。
    """
    five = ten = 0   # 手头 5 元和 10 元的数量

    for bill in bills:
        if bill == 5:
            five += 1                     # 直接收下
        elif bill == 10:
            if five == 0: return False    # 没有5元找零
            five -= 1; ten += 1
        else:   # bill == 20
            if ten > 0 and five > 0:      # 优先10+5
                ten -= 1; five -= 1
            elif five >= 3:               # 没有10，用3个5
                five -= 3
            else:
                return False              # 无法找零

    return True

# 时间 O(n)，空间 O(1)
```

---

### 🟢 题2：买卖股票的最佳时机（LeetCode 121）

**题意**：只能买卖一次，找最大利润。

```python
def maxProfit(prices: list[int]) -> int:
    """
    贪心：遍历时记录历史最低价，当前价格减去历史最低价就是当前最大利润。
    min_price：截至当前的最低买入价
    """
    min_price = float('inf')
    max_profit = 0

    for price in prices:
        min_price = min(min_price, price)          # 更新历史最低
        max_profit = max(max_profit, price - min_price)  # 今天卖出的利润

    return max_profit

# 时间 O(n)，空间 O(1)
```

---

### 🟡 题3：任务调度器（LeetCode 621）

**题意**：CPU 执行任务，相同任务必须间隔 n 个时间单位，求完成所有任务的最短时间。

**思路**：贪心。让出现最频繁的任务来"主导"时间框架，填满冷却时间。

```python
from collections import Counter

def leastInterval(tasks: list[str], n: int) -> int:
    """
    设最高频次为 max_count，有 max_count_tasks 个任务具有该频次。
    构建框架：(max_count-1) 个"桶"，每桶有 (n+1) 个时间槽，加上最后一行。
    最短时间 = max((max_count-1)*(n+1) + max_count_tasks, len(tasks))
    解释：
    - 当任务种类多，能填满所有冷却时间：答案是 len(tasks)
    - 否则：以最高频任务为框架，其他任务填空闲槽
    """
    freq = Counter(tasks)
    max_count = max(freq.values())
    max_count_tasks = sum(1 for v in freq.values() if v == max_count)

    return max((max_count - 1) * (n + 1) + max_count_tasks, len(tasks))

# 示例：tasks=["A","A","A","B","B","B"], n=2 → 8
# 框架：A B _ | A B _ | A B（_可放其他任务或idle）
# 时间 O(n)，空间 O(1)（字母表固定大小）
```

---

### 🟡 题4：根据身高重建队列（LeetCode 406）

**题意**：每人属性 [h, k]，h 为身高，k 为前面身高 >= h 的人数，重建队列。

**思路**：贪心。先按身高降序排（高个子先放），再按 k 值插入（插入时低个子不影响高个子的 k）。

```python
def reconstructQueue(people: list[list[int]]) -> list[list[int]]:
    """
    贪心策略：
    ① 按身高降序排（相同身高按 k 升序）
    ② 依次将每个人插入到下标 k 处

    正确性：高个子先确定位置，后来的矮个子插入时不会影响高个子的 k 值
    （矮个子对高个子"透明"，不被高个子计入 k）
    """
    # 身高降序，相同身高按 k 升序
    people.sort(key=lambda x: (-x[0], x[1]))

    result = []
    for p in people:
        result.insert(p[1], p)   # 在下标 k 处插入

    return result

# 示例：[[7,0],[4,4],[7,1],[5,0],[6,1],[5,2]]
# → [[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]]
# 时间 O(n²)（insert 是 O(n)），空间 O(n)
```

---

## 4.8 BFS 专题

### 🟢 题1：二叉树的最小深度（LeetCode 111）

**题意**：找从根节点到最近叶子节点的最短路径长度。

**思路**：BFS 层序遍历，第一次遇到叶子节点时返回当前层数（即最小深度）。

```python
from collections import deque

def minDepth(root) -> int:
    """
    BFS 天然按层扩展，第一次遇到叶子节点时的层数就是最小深度。
    比 DFS 更高效（不需要遍历整棵树），找到即返回。
    """
    if not root: return 0

    queue = deque([(root, 1)])      # (节点, 深度)

    while queue:
        node, depth = queue.popleft()

        # 叶子节点：左右子节点都为 None
        if not node.left and not node.right:
            return depth            # BFS 保证这是最短路径

        if node.left:
            queue.append((node.left, depth + 1))
        if node.right:
            queue.append((node.right, depth + 1))

    return 0

# 时间 O(n) 最坏，空间 O(w)（w 为最大宽度）
```

---

### 🟡 题2：01 矩阵（LeetCode 542）

**题意**：给定只含 0 和 1 的矩阵，计算每个格子到最近 0 的距离。

**思路**：多源 BFS，将所有 0 同时作为起点，向外 BFS 扩展（反向思维：不是从 1 找 0，而是从所有 0 同时向外扩散）。

```python
from collections import deque

def updateMatrix(mat: list[list[int]]) -> list[list[int]]:
    """
    多源 BFS：所有 0 同时入队（距离=0），BFS 逐层扩散。
    到达每个 1 格时的层数，就是它到最近 0 的距离。

    类比：把所有 0 看成一个超级源点，BFS 到每个 1 的距离即所求。
    """
    rows, cols = len(mat), len(mat[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    queue = deque()

    # 所有 0 的位置入队，距离设为 0
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                queue.append((r, c))

    while queue:
        r, c = queue.popleft()
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<rows and 0<=nc<cols:
                # 若通过当前格能更新邻格距离
                if dist[nr][nc] > dist[r][c] + 1:
                    dist[nr][nc] = dist[r][c] + 1
                    queue.append((nr, nc))

    return dist

# 时间 O(mn)，空间 O(mn)
```

---

### 🟡 题3：完全平方数（LeetCode 279）

**题意**：给定正整数 n，找最少需要几个完全平方数使其和等于 n。

**思路**：BFS 按层搜索，每层表示用了 k 个完全平方数。第一次到达 0（n 减完）时的层数就是答案。

```python
from collections import deque
import math

def numSquares(n: int) -> int:
    """
    将问题建模为无权图的最短路：
    - 节点：0 到 n 的整数
    - 边：节点 x 到 x - 完全平方数（代表选一个完全平方数）
    - 求从 n 到 0 的最短路（或等价，从 0 到 n）

    BFS 按层扩展，层数即"最少使用的完全平方数个数"。
    """
    squares = [i*i for i in range(1, int(math.sqrt(n))+1)]
    queue = deque([n])
    visited = {n}
    steps = 0

    while queue:
        steps += 1
        for _ in range(len(queue)):
            num = queue.popleft()
            for sq in squares:
                next_num = num - sq
                if next_num == 0: return steps
                if next_num > 0 and next_num not in visited:
                    visited.add(next_num)
                    queue.append(next_num)

    return steps

# 时间 O(n√n)，空间 O(n)
```

---

### 🟡 题4：打开转盘锁（LeetCode 752）

**题意**：拨号锁从 "0000" 出发，每次转动一个拨轮一格（+1 或 -1，循环），避开死亡组合，找到 target 的最少步数。

```python
from collections import deque

def openLock(deadends: list[str], target: str) -> int:
    """
    BFS 最短路：每个状态是4位字符串，相邻状态是转动一个拨轮一格的结果。
    从 "0000" 出发，避开 deadends，找到 target 的最少步数。
    """
    dead = set(deadends)
    start = "0000"
    if start in dead: return -1
    if start == target: return 0

    queue = deque([(start, 0)])     # (状态, 步数)
    visited = {start}

    while queue:
        state, steps = queue.popleft()

        # 生成所有相邻状态（8种：每个拨轮±1）
        for i in range(4):
            digit = int(state[i])
            for delta in [1, -1]:
                new_digit = (digit + delta) % 10    # 循环：9+1=0，0-1=9
                new_state = state[:i] + str(new_digit) + state[i+1:]

                if new_state == target: return steps + 1
                if new_state not in dead and new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, steps + 1))

    return -1

# 时间 O(10^4 × 4 × 2) = O(1)（状态空间固定），空间 O(10^4)
```

---

## 4.9 DFS / 回溯专题

### 🟢 题1：路径总和（LeetCode 112）

**题意**：判断二叉树中是否存在从根到叶子节点的路径，使路径上所有节点值之和等于 target。

```python
def hasPathSum(root, targetSum: int) -> bool:
    """
    DFS：每向下走一步，目标减少当前节点值。
    到达叶子节点时，若剩余目标恰好为 0，说明找到了满足条件的路径。
    """
    if root is None: return False

    # 到达叶子节点，判断剩余值是否恰好被消耗完
    if root.left is None and root.right is None:
        return root.val == targetSum

    # 递归左右子树，有一个满足即可
    remaining = targetSum - root.val
    return hasPathSum(root.left, remaining) or hasPathSum(root.right, remaining)

# 时间 O(n)，空间 O(h)
```

---

### 🟢 题2：二叉树的所有路径（LeetCode 257）

**题意**：返回所有从根节点到叶子节点的路径。

```python
def binaryTreePaths(root) -> list[str]:
    """
    DFS 回溯：path 记录当前路径，到达叶子时记录结果。
    用列表维护路径，回溯时弹出最后一个节点（撤销选择）。
    """
    result = []

    def dfs(node, path):
        if node is None: return
        path.append(str(node.val))    # 做选择

        if not node.left and not node.right:
            result.append('->'.join(path))   # 到达叶子，记录路径
        else:
            dfs(node.left, path)
            dfs(node.right, path)

        path.pop()    # 撤销选择（回溯）

    dfs(root, [])
    return result

# 时间 O(n²)（字符串拼接），空间 O(n)
```

---

### 🟡 题3：电话号码的字母组合（LeetCode 17）

**题意**：给定数字字符串，返回数字键盘上对应字母的所有组合。

```python
def letterCombinations(digits: str) -> list[str]:
    """
    回溯：逐个数字，枚举该数字对应的所有字母，递归处理下一个数字。
    状态树：每层对应一个数字，每个分支对应该数字的一个字母。
    """
    if not digits: return []

    phone = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }
    result = []

    def backtrack(index, path):
        if index == len(digits):      # 所有数字都处理完，记录结果
            result.append(''.join(path))
            return
        for letter in phone[digits[index]]:
            path.append(letter)       # 做选择
            backtrack(index + 1, path)  # 处理下一个数字
            path.pop()                # 撤销选择

    backtrack(0, [])
    return result

# 时间 O(4^n × n)，空间 O(n)（n = digits 长度）
```

---

### 🟡 题4：单词搜索（LeetCode 79）

**题意**：在字母网格中，判断是否存在一条路径能拼出给定单词（每个格子只能用一次）。

```python
def exist(board: list[list[str]], word: str) -> bool:
    """
    DFS + 回溯：从每个格子出发，尝试匹配 word 的每个字符。
    - 做选择：将当前格子标记为已访问（临时修改为特殊符号）
    - 递归匹配下一个字符
    - 撤销选择：恢复格子原来的字符

    剪枝：当前字符不匹配，立即返回 False
    """
    rows, cols = len(board), len(board[0])

    def dfs(r, c, idx):
        if idx == len(word): return True       # 所有字符都匹配成功

        # 越界 / 当前字符不匹配
        if not (0<=r<rows and 0<=c<cols) or board[r][c] != word[idx]:
            return False

        temp = board[r][c]
        board[r][c] = '#'                      # 标记已访问（避免重复使用）

        # 四个方向递归匹配下一个字符
        found = any(dfs(r+dr, c+dc, idx+1)
                    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)])

        board[r][c] = temp                     # 回溯：恢复格子
        return found

    # 枚举所有起点
    return any(dfs(r, c, 0)
               for r in range(rows)
               for c in range(cols))

# 时间 O(mn × 4^L)，L = word 长度；空间 O(L)
```

---

## 4.10 图算法专题

### 🟢 题1：找到小镇的法官（LeetCode 997）

**题意**：n 个人，法官不信任任何人，其他所有人都信任法官，找到法官。

**思路**：入度 - 出度 == n-1 的节点就是法官。

```python
def findJudge(n: int, trust: list[list[int]]) -> int:
    """
    法官特征：
    - 出度 = 0（不信任任何人）
    - 入度 = n-1（其他所有人都信任他）
    用 in_degree - out_degree 的差值，差值为 n-1 的就是法官。
    """
    score = [0] * (n + 1)    # score[i] = in_degree[i] - out_degree[i]

    for a, b in trust:
        score[a] -= 1        # a 信任别人，出度+1
        score[b] += 1        # b 被信任，入度+1

    for i in range(1, n + 1):
        if score[i] == n - 1:
            return i

    return -1

# 时间 O(V+E)，空间 O(V)
```

---

### 🟢 题2：克隆图（LeetCode 133）

**题意**：给定一个连通无向图的节点，返回该图的深拷贝。

```python
def cloneGraph(node):
    """
    DFS + 哈希表：
    visited 字典存 {原节点: 克隆节点}，防止重复克隆和处理环。
    对每个节点，先创建克隆，再递归克隆其邻居。
    """
    if not node: return None
    visited = {}

    def dfs(n):
        if n in visited: return visited[n]   # 已克隆，直接返回

        clone = Node(n.val)                  # 创建克隆节点
        visited[n] = clone                   # 先存入（处理环！）

        for nb in n.neighbors:
            clone.neighbors.append(dfs(nb))  # 递归克隆邻居

        return clone

    return dfs(node)

# 时间 O(V+E)，空间 O(V)
```

---

### 🟡 题3：钥匙和房间（LeetCode 841）

**题意**：n 个房间，房间 0 开始，每个房间有若干钥匙，判断是否能开所有房间。

```python
def canVisitAllRooms(rooms: list[list[int]]) -> bool:
    """
    图连通性问题：节点是房间，边是钥匙（从 i 房间拿到 j 号钥匙 = i→j 的边）。
    从节点 0 出发 DFS/BFS，看能否到达所有节点。
    用 visited 集合记录已进入的房间。
    """
    visited = set()
    stack = [0]                          # DFS 栈，从 0 号房间开始

    while stack:
        room = stack.pop()
        if room in visited: continue     # 已访问，跳过
        visited.add(room)
        for key in rooms[room]:          # 收集当前房间的所有钥匙
            if key not in visited:
                stack.append(key)        # 把新钥匙对应的房间加入待访问

    return len(visited) == len(rooms)   # 是否访问了全部房间

# 时间 O(V+E)，空间 O(V)
```

---

### 🟡 题4：省份数量（LeetCode 547）

**题意**：n 个城市，`isConnected[i][j]=1` 表示 i 和 j 直接相连，求省份数量（连通分量数）。

```python
def findCircleNum(isConnected: list[list[int]]) -> int:
    """
    方法一：并查集（推荐）
    遍历所有边，合并相连的城市，最终连通分量数即省份数。
    """
    n = len(isConnected)
    parent = list(range(n))
    count = n

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])   # 路径压缩
        return parent[x]

    def union(x, y):
        nonlocal count
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
            count -= 1

    for i in range(n):
        for j in range(i+1, n):
            if isConnected[i][j] == 1:
                union(i, j)

    return count

    """
    方法二：DFS 标记连通分量
    visited = [False] * n
    count = 0
    def dfs(i):
        visited[i] = True
        for j in range(n):
            if isConnected[i][j] == 1 and not visited[j]:
                dfs(j)
    for i in range(n):
        if not visited[i]:
            dfs(i); count += 1
    return count
    """

# 时间 O(n²)，空间 O(n)
```

