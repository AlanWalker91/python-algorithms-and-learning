# Python 数据结构与算法结构化知识图谱

> 适用对象：Python 算法基础较弱、想系统准备面试的人  
> 阅读顺序：先看框架和映射表，再看数据结构，再看算法思想，最后刷面试题

---

## 1. 整体框架结构

```text
Python 数据结构与算法
├─ 一、总览层
│  ├─ 核心概念：复杂度、状态、搜索、递归、贪心、最优子结构
│  ├─ 工具映射：题目特征 -> 数据结构 / 算法
│  └─ 模块速查：collections / heapq / bisect
├─ 二、数据结构层
│  ├─ 线性结构：list、deque、linked list、stack、queue
│  ├─ 哈希结构：dict、set、Counter、defaultdict
│  ├─ 树结构：binary tree、BST、heap、trie
│  └─ 图结构：adjacency list、union-find、topological sort
├─ 三、算法思想层
│  ├─ 双指针
│  ├─ 滑动窗口
│  ├─ 哈希
│  ├─ 二分查找
│  ├─ 递归与分治
│  ├─ 动态规划
│  ├─ 贪心
│  ├─ BFS
│  ├─ DFS / 回溯
│  └─ 图算法
├─ 四、应用层
│  ├─ 频率统计
│  ├─ TopK
│  ├─ 子串 / 子数组
│  ├─ 路径搜索
│  ├─ 连通性
│  ├─ 最短路径
│  └─ 依赖关系
└─ 五、面试层
   ├─ 简单题：熟悉模板、训练手感
   ├─ 中等题：理解思路、训练建模
   └─ 复盘：题型识别 + 复杂度 + 易错点
```

---

## 2. 核心概念、常用方法与工具映射表

### 2.1 题目特征 -> 结构 / 算法

| 题目特征 | 优先想到 | 常用 Python 工具 |
|---|---|---|
| 判重、去重、频率统计 | 哈希 | `dict` `set` `Counter` |
| 连续子串、连续子数组 | 滑动窗口 | 双指针 + `dict/set` |
| 数组有序、找边界 | 二分查找 | 手写二分 / `bisect` |
| 两端逼近、原地覆盖 | 双指针 | `list` 下标 |
| 一层一层扩散、最短步数 | BFS | `deque` |
| 搜索所有可能、路径枚举 | DFS / 回溯 | 递归 |
| TopK、优先级出队 | 堆 | `heapq` |
| 最优解、方案数、可行性 | 动态规划 | `list` / 二维数组 |
| 局部最优明显 | 贪心 | 排序、堆 |
| 依赖关系、是否有环 | 图算法 / 拓扑排序 | 邻接表 + `deque` |

### 2.2 常见操作 -> 工具

| 目标 | 首选工具 | 说明 |
|---|---|---|
| 统计词频 / 元素频率 | `Counter` | 比手写字典更快进入状态 |
| 默认值字典 | `defaultdict` | 省去判空代码 |
| 队列 / BFS | `deque` | `popleft()` 是 `O(1)` |
| 最小堆 | `heapq` | Python 默认最小堆 |
| 有序边界查找 | `bisect_left/right` | 适合边界问题 |
| 判重 | `set` | 平均 `O(1)` |
| 键值映射 | `dict` | 平均 `O(1)` |

### 2.3 面试必会模块

```python
from collections import Counter, defaultdict, deque
import heapq
import bisect
```

---

## 3. 相关术语与定义

### 3.1 时间复杂度
- 时间复杂度用于衡量算法随着输入规模 `n` 增大时，运行次数增长有多快。
- 常见级别：
  - `O(1)`：常数时间
  - `O(log n)`：对数时间，常见于二分
  - `O(n)`：线性时间，单次遍历
  - `O(n log n)`：排序常见
  - `O(n^2)`：双重循环常见

### 3.2 空间复杂度
- 空间复杂度表示算法额外使用了多少内存。
- 例如：
  - 使用哈希表通常会增加空间复杂度
  - 原地修改数组通常可以节省空间

### 3.3 状态
- “状态”是动态规划里的核心概念，表示一个子问题结果。
- 例如 `dp[i]` 可能表示“到第 i 个位置时的最优答案”。

### 3.4 状态转移
- 状态转移就是“当前状态如何由更小状态推出”。
- 例如爬楼梯：
  - `dp[i] = dp[i - 1] + dp[i - 2]`

### 3.5 最优子结构
- 大问题的最优解可以由小问题的最优解推出。
- 这是动态规划和贪心常见前提。

### 3.6 重复子问题
- 同一个子问题会被反复计算。
- 这正是动态规划要优化的地方。

### 3.7 递归
- 函数调用自身来解决规模更小的同类问题。
- 关键是：
  - 定义函数含义
  - 写终止条件
  - 写递归关系

### 3.8 分治
- 把一个大问题拆成几个小问题，各自求解后再合并结果。
- 例如归并排序、快速幂。

### 3.9 回溯
- 本质是 DFS 的一种应用。
- 适用于“枚举所有可能解”。
- 核心动作是：
  - 做选择
  - 递归深入
  - 撤销选择

### 3.10 BFS
- 广度优先搜索。
- 一层一层扩散。
- 适用于：
  - 层序遍历
  - 无权图最短路
  - 最少操作次数

### 3.11 DFS
- 深度优先搜索。
- 一条路走到底，再回退。
- 适用于：
  - 树遍历
  - 连通块
  - 路径搜索
  - 回溯

### 3.12 邻接表
- 图的一种表示方式。
- `graph[u] = [v1, v2, ...]`
- 适合稀疏图。

### 3.13 入度
- 在有向图中，指向某个节点的边数。
- 拓扑排序会先处理入度为 `0` 的点。

### 3.14 并查集
- 用来维护“哪些点属于同一个连通块”。
- 核心操作：
  - `find(x)`：找根节点
  - `union(x, y)`：合并集合

---

## 4. Python 数据结构

## 4.1 `list`

### 定义
- `list` 是 Python 的动态数组。
- 动态数组的意思是：长度可以自动扩容，底层仍然按数组方式存储。

### 底层实现原理
- 连续内存
- 支持随机访问
- 扩容时会申请更大的空间并搬移元素

### Python 中的实现方式
- 内置，无需导入

### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 按下标访问 | `nums[i]` | `O(1)` |
| 尾部追加 | `append(x)` | 均摊 `O(1)` |
| 尾部弹出 | `pop()` | `O(1)` |
| 头部弹出 | `pop(0)` | `O(n)` |
| 插入 | `insert(i, x)` | `O(n)` |
| 查找 | `x in nums` | `O(n)` |
| 排序 | `sort()` | `O(nlogn)` |

### 典型应用
- 数组遍历
- 双指针
- 栈
- 动态规划数组

## 4.2 `dict`

### 定义
- `dict` 是键值映射表，底层是哈希表。

### 底层实现原理
- 对 key 计算哈希值
- 快速定位元素存储位置
- 平均查询、插入、删除是 `O(1)`

### Python 中的实现方式
- 内置，无需导入

### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 查询 | `d[k]` / `get(k)` | 平均 `O(1)` |
| 插入 | `d[k] = v` | 平均 `O(1)` |
| 删除 | `del d[k]` | 平均 `O(1)` |
| 判存在 | `k in d` | 平均 `O(1)` |

### 典型应用
- 频率统计
- 补数查找
- 前缀和计数

## 4.3 `set`

### 定义
- `set` 是无重复元素集合，底层也是哈希表。

### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 添加 | `add(x)` | 平均 `O(1)` |
| 删除 | `remove(x)` / `discard(x)` | 平均 `O(1)` |
| 判存在 | `x in s` | 平均 `O(1)` |

### 典型应用
- 判重
- 去重
- 访问标记

## 4.4 `deque`

### 定义
- 双端队列，适合在头尾两端高效插入删除。

### Python 中的实现方式

```python
from collections import deque
```

### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 尾部入队 | `append(x)` | `O(1)` |
| 头部入队 | `appendleft(x)` | `O(1)` |
| 头部出队 | `popleft()` | `O(1)` |
| 尾部出队 | `pop()` | `O(1)` |

### 典型应用
- BFS
- 单调队列

## 4.5 链表

### 定义
- 由节点组成的线性结构。
- 每个节点保存值和下一个节点引用。

### Python 中的实现方式

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

### 典型应用
- 反转链表
- 快慢指针
- 合并链表

## 4.6 堆

### 定义
- 堆是一种特殊的完全二叉树。
- Python 默认提供最小堆。

### Python 中的实现方式

```python
import heapq
```

### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 建堆 | `heapify(nums)` | `O(n)` |
| 插入 | `heappush(heap, x)` | `O(logn)` |
| 弹出堆顶 | `heappop(heap)` | `O(logn)` |

### 典型应用
- TopK
- 优先队列
- 最短路

## 4.7 树

### 定义
- 层级结构。
- 面试高频是二叉树和二叉搜索树 BST。

### Python 中的实现方式

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

### 典型应用
- 递归
- DFS / BFS
- 路径问题

## 4.8 图

### 定义
- 点与边组成的关系结构。
- 可以有环，也可以带方向和权重。

### Python 中的实现方式

```python
from collections import defaultdict

graph = defaultdict(list)
graph[1].append(2)
graph[1].append(3)
```

### 典型应用
- 最短路
- 连通性
- 课程依赖

---

## 5. Python 算法思想

> 这一部分分成两层：
> 1. 先讲核心思想、识别信号、典型应用场景  
> 2. 再给出一个“典型应用代码”，不和后面的面试题重复

## 5.1 双指针

### 核心思想
- 用两个指针协同工作，避免重复遍历。
- 一类是左右夹逼，一类是快慢扫描。

### 识别信号
- 有序数组
- 从两端往中间逼近
- 原地去重、原地覆盖

### 典型应用场景
- 原地移除元素
- 有序数组配对
- 回文判断

### 典型应用代码：移除元素

#### 讲解
- 让 `fast` 扫描整个数组。
- 让 `slow` 记录“保留元素应该写入的位置”。
- 只要 `nums[fast] != val`，就把它写到 `slow`。
- 这是双指针里最典型的“快慢覆盖”模型。

```python
def removeElement(nums, val):
    # slow 指向当前可写入的位置
    slow = 0

    # fast 负责扫描整个数组
    for fast in range(len(nums)):
        # 如果当前元素不是待删除值，就保留下来
        if nums[fast] != val:
            nums[slow] = nums[fast]
            slow += 1

    # 返回新数组长度，前 slow 个元素就是有效部分
    return slow
```

## 5.2 滑动窗口

### 核心思想
- 维护一个连续区间 `[left, right]`。
- 右指针扩张窗口，左指针收缩窗口。
- 常用于最长、最短、计数类连续区间问题。

### 识别信号
- 连续子串、连续子数组
- 最长 / 最短 / 个数
- 需要维护窗口状态

### 典型应用场景
- 最长不重复子串
- 最短满足条件子数组
- 固定长度窗口统计

### 典型应用代码：大小为 K 的子数组平均值

#### 讲解
- 这是最简单的固定窗口模型。
- 先算前 `k` 个元素的和。
- 然后每次窗口右移：
  - 减去左端旧元素
  - 加上右端新元素
- 这样避免了重复求和。

```python
def findMaxAverage(nums, k):
    # 先计算第一个窗口的和
    window_sum = sum(nums[:k])
    max_sum = window_sum

    # 从第 k 个元素开始，窗口不断向右滑动
    for right in range(k, len(nums)):
        # 新窗口 = 旧窗口 - 滑出元素 + 滑入元素
        window_sum += nums[right] - nums[right - k]
        max_sum = max(max_sum, window_sum)

    return max_sum / k
```

## 5.3 哈希

### 核心思想
- 用空间换时间。
- 把线性查找优化成平均 `O(1)` 查询。

### 识别信号
- 判重
- 频率统计
- 配对查找
- 前缀和计数

### 典型应用场景
- 字符频率统计
- 是否出现过
- 数组补数匹配

### 典型应用代码：第一个只出现一次的字符

#### 讲解
- 先统计每个字符出现次数。
- 再按原顺序遍历字符串，找到第一个频次为 1 的字符。
- 这是哈希“统计 + 回查”的标准模型。

```python
from collections import Counter


def firstUniqChar(s):
    # 统计每个字符出现次数
    freq = Counter(s)

    # 按原顺序查找第一个出现次数为 1 的字符
    for i, ch in enumerate(s):
        if freq[ch] == 1:
            return i

    return -1
```

## 5.4 二分查找

### 核心思想
- 利用单调性，每次排除一半答案。

### 识别信号
- 数组有序
- 找边界
- “答案满足某条件，且条件单调”

### 典型应用场景
- 查找目标值
- 查找左边界 / 右边界
- 答案二分

### 典型应用代码：猜数字大小

#### 讲解
- 假设存在一个 `guess(mid)` 接口：
  - 返回 `0` 表示猜中
  - 返回 `-1` 表示猜大了
  - 返回 `1` 表示猜小了
- 这是最纯粹的二分模型。

```python
def guessNumber(n):
    left, right = 1, n

    while left <= right:
        mid = (left + right) // 2
        result = guess(mid)  # 面试平台通常会给这个接口

        if result == 0:
            return mid
        elif result < 0:
            # 猜大了，往左边缩
            right = mid - 1
        else:
            # 猜小了，往右边缩
            left = mid + 1
```

## 5.5 递归与分治

### 核心思想
- 递归：相信子问题已经被解决。
- 分治：把大问题拆开，各自求解，再合并。

### 识别信号
- 树
- 左右子问题
- “定义当前函数返回什么”

### 典型应用场景
- 树深度
- 合并结构
- 快速幂

### 典型应用代码：平衡二叉树

#### 讲解
- 平衡二叉树要求任意节点左右子树高度差不超过 1。
- 可以递归返回“树的高度”。
- 一旦发现某棵子树不平衡，就返回特殊值 `-1`。
- 这是一种“递归返回更多信息”的思路。

```python
def isBalanced(root):
    def height(node):
        # 空树高度为 0
        if not node:
            return 0

        left_height = height(node.left)
        # 左子树不平衡，直接向上返回
        if left_height == -1:
            return -1

        right_height = height(node.right)
        # 右子树不平衡，直接向上返回
        if right_height == -1:
            return -1

        # 当前节点左右高度差超过 1，说明不平衡
        if abs(left_height - right_height) > 1:
            return -1

        # 返回当前树高度
        return 1 + max(left_height, right_height)

    return height(root) != -1
```

## 5.6 动态规划

### 核心思想
- 把重复子问题的结果保存起来。
- 关键是定义状态。

### 识别信号
- 求最值
- 求方案数
- 判断是否可行
- 当前结果依赖过去结果

### 典型应用场景
- 爬楼梯
- 最大子数组和
- 背包问题

### 典型应用代码：使用最小花费爬楼梯

#### 讲解
- 走到第 `i` 阶，可以从 `i-1` 或 `i-2` 过来。
- `dp[i]` 表示到达第 `i` 阶的最小花费。
- 当前状态只依赖前两个状态。

```python
def minCostClimbingStairs(cost):
    n = len(cost)
    dp = [0] * (n + 1)

    # dp[0] 和 dp[1] 都是 0，因为可以从这两个位置出发
    for i in range(2, n + 1):
        # 到 i 可以从 i-1 或 i-2 来
        dp[i] = min(
            dp[i - 1] + cost[i - 1],
            dp[i - 2] + cost[i - 2]
        )

    return dp[n]
```

## 5.7 贪心

### 核心思想
- 每一步都做当前最优选择。
- 前提是局部最优可以推出全局最优。

### 识别信号
- 最少 / 最多操作
- 区间调度
- 每一步都有明显“更优选择”

### 典型应用场景
- 区间问题
- 跳跃覆盖
- 股票买卖

### 典型应用代码：柠檬水找零

#### 讲解
- 收到 10 元时，必须找 5 元。
- 收到 20 元时，优先找 `10 + 5`，因为这样能保留更多 5 元，后续更灵活。
- 这是典型的局部最优策略。

```python
def lemonadeChange(bills):
    five = 0
    ten = 0

    for bill in bills:
        if bill == 5:
            five += 1
        elif bill == 10:
            # 必须找一张 5 元
            if five == 0:
                return False
            five -= 1
            ten += 1
        else:  # bill == 20
            # 优先用 10 + 5 找零
            if ten > 0 and five > 0:
                ten -= 1
                five -= 1
            elif five >= 3:
                five -= 3
            else:
                return False

    return True
```

## 5.8 BFS

### 核心思想
- 从起点开始一层一层向外扩展。
- 最适合无权图最短路径。

### 识别信号
- 最少步数
- 一层一层传播
- 队列模型

### 典型应用场景
- 层序遍历
- 最少操作
- 矩阵扩散

### 典型应用代码：01 矩阵中到最近 0 的距离

#### 讲解
- 所有值为 `0` 的位置同时作为起点。
- 然后做多源 BFS。
- 第一次到达某个位置时，路径一定最短。

```python
from collections import deque


def updateMatrix(mat):
    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]
    q = deque()

    # 所有 0 同时入队，作为多源 BFS 的起点
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                q.append((r, c))

    while q:
        r, c = q.popleft()

        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc

            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))

    return dist
```

## 5.9 DFS / 回溯

### 核心思想
- DFS 先深入，再回退。
- 回溯是在 DFS 过程中维护“当前路径”，并在返回时撤销选择。

### 识别信号
- 搜所有可能
- 树 / 图深度遍历
- 组合、排列、子集

### 典型应用场景
- 子集
- 排列
- 矩阵路径搜索

### 典型应用代码：字母大小写全排列

#### 讲解
- 每遇到一个字母，都有两种选择：
  - 保持小写
  - 变成大写
- 数字没有分支，直接加入路径即可。
- 这是非常标准的回溯树。

```python
def letterCasePermutation(s):
    ans = []
    path = []

    def dfs(index):
        # 走到末尾，得到一个完整结果
        if index == len(s):
            ans.append("".join(path))
            return

        ch = s[index]

        if ch.isalpha():
            # 选择 1：小写
            path.append(ch.lower())
            dfs(index + 1)
            path.pop()

            # 选择 2：大写
            path.append(ch.upper())
            dfs(index + 1)
            path.pop()
        else:
            # 数字只有一种选择
            path.append(ch)
            dfs(index + 1)
            path.pop()

    dfs(0)
    return ans
```

## 5.10 图算法

### 核心思想
- 把问题抽象为点和边。
- 常见关注点是：
  - 是否连通
  - 是否有环
  - 依赖顺序
  - 最短路径

### 识别信号
- 课程依赖
- 城市连通
- 网络传播
- 有向边 / 无向边

### 典型应用场景
- 拓扑排序
- 并查集
- 最短路

### 典型应用代码：查找是否存在路径

#### 讲解
- 给定无向图，判断起点到终点是否可达。
- 用邻接表建图，再用 DFS 或 BFS 搜索。
- 这是图遍历里最基础的一类。

```python
from collections import defaultdict, deque


def validPath(n, edges, source, destination):
    graph = defaultdict(list)

    # 建立无向图
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    q = deque([source])
    visited = {source}

    while q:
        node = q.popleft()

        if node == destination:
            return True

        for nxt in graph[node]:
            if nxt not in visited:
                visited.add(nxt)
                q.append(nxt)

    return False
```

---

## 6. 面试算法题目精选

> 这一部分和上面的“典型应用代码”尽量不重复。  
> 选题以经典、高频、适合面试准备为主，难度以简单和中等为主。

## 6.1 双指针

### 1. 合并两个有序数组
- 难度：简单
- 核心：从后往前双指针，避免覆盖未处理元素

### 2. 反转字符串
- 难度：简单
- 核心：左右指针交换

### 3. 有序数组的平方
- 难度：简单
- 核心：平方后最大值只会在两端

### 4. 接雨水
- 难度：中等
- 核心：维护左右最大高度，决定当前位置能接多少水

### 5. 三数之和
- 难度：中等
- 核心：排序 + 固定一个数 + 双指针

#### 例题详解：有序数组的平方

##### 思路
- 原数组有序，但平方后不一定有序，因为负数平方可能很大。
- 最大平方值一定出现在数组两端。
- 所以用左右指针比较平方大小，把较大值从结果数组末尾开始填入。

```python
def sortedSquares(nums):
    n = len(nums)
    ans = [0] * n

    left, right = 0, n - 1
    pos = n - 1

    while left <= right:
        left_square = nums[left] * nums[left]
        right_square = nums[right] * nums[right]

        if left_square > right_square:
            ans[pos] = left_square
            left += 1
        else:
            ans[pos] = right_square
            right -= 1

        pos -= 1

    return ans
```

## 6.2 滑动窗口

### 1. 长度最小的子数组
- 难度：中等
- 核心：可变窗口，满足条件就收缩

### 2. 无重复字符的最长子串
- 难度：中等
- 核心：窗口内字符不重复

### 3. 至多包含两个不同字符的最长子串
- 难度：中等
- 核心：窗口内维护字符种类数

### 4. 字符串的排列
- 难度：中等
- 核心：固定长度窗口 + 频次比较

### 5. 最大连续 1 的个数 III
- 难度：中等
- 核心：窗口内允许最多 `k` 个 0

#### 例题详解：最大连续 1 的个数 III

##### 思路
- 可以把至多 `k` 个 `0` 翻成 `1`。
- 所以窗口内只要 `0` 的个数不超过 `k`，这个窗口就是合法的。
- 右指针扩张，若 `0` 太多，就移动左指针收缩。

```python
def longestOnes(nums, k):
    left = 0
    zero_count = 0
    ans = 0

    for right, num in enumerate(nums):
        if num == 0:
            zero_count += 1

        while zero_count > k:
            if nums[left] == 0:
                zero_count -= 1
            left += 1

        ans = max(ans, right - left + 1)

    return ans
```

## 6.3 哈希

### 1. 快乐数
- 难度：简单
- 核心：哈希判环

### 2. 同构字符串
- 难度：简单
- 核心：双向映射

### 3. 最长和谐子序列
- 难度：简单
- 核心：频率统计

### 4. 四数相加 II
- 难度：中等
- 核心：分组哈希

### 5. 砖墙
- 难度：中等
- 核心：统计边界位置出现次数

#### 例题详解：同构字符串

##### 思路
- 两个字符串同构，说明一个字符只能映射到另一个固定字符。
- 需要双向约束：
  - `s -> t`
  - `t -> s`
- 否则会出现多个字符映射到同一个字符的问题。

```python
def isIsomorphic(s, t):
    map_st = {}
    map_ts = {}

    for ch1, ch2 in zip(s, t):
        if ch1 in map_st and map_st[ch1] != ch2:
            return False
        if ch2 in map_ts and map_ts[ch2] != ch1:
            return False

        map_st[ch1] = ch2
        map_ts[ch2] = ch1

    return True
```

## 6.4 二分查找

### 1. 搜索插入位置
- 难度：简单

### 2. 有效的完全平方数
- 难度：简单

### 3. 寻找峰值
- 难度：中等

### 4. 爱吃香蕉的珂珂
- 难度：中等

### 5. 在 D 天内送达包裹的能力
- 难度：中等

#### 例题详解：爱吃香蕉的珂珂

##### 思路
- 吃香蕉速度 `k` 越大，所需总时间越少。
- 这说明答案具有单调性，可以二分。
- 我们二分“速度”，检查这个速度是否能在 `h` 小时内吃完。

```python
def minEatingSpeed(piles, h):
    left, right = 1, max(piles)

    def can_finish(speed):
        hours = 0
        for pile in piles:
            # 向上取整：(pile + speed - 1) // speed
            hours += (pile + speed - 1) // speed
        return hours <= h

    while left < right:
        mid = (left + right) // 2

        if can_finish(mid):
            right = mid
        else:
            left = mid + 1

    return left
```

## 6.5 递归与分治

### 1. 对称二叉树
- 难度：简单

### 2. 相同的树
- 难度：简单

### 3. 将有序数组转换为二叉搜索树
- 难度：简单

### 4. 不同的二叉搜索树
- 难度：中等

### 5. 验证二叉搜索树
- 难度：中等

#### 例题详解：对称二叉树

##### 思路
- 对称的本质是“左子树的左边”和“右子树的右边”对应相等，
- 同时“左子树的右边”和“右子树的左边”对应相等。
- 所以递归判断两棵树是否互为镜像。

```python
def isSymmetric(root):
    def is_mirror(left, right):
        if not left and not right:
            return True
        if not left or not right:
            return False
        if left.val != right.val:
            return False

        return is_mirror(left.left, right.right) and \
               is_mirror(left.right, right.left)

    return is_mirror(root.left, root.right)
```

## 6.6 动态规划

### 1. 爬楼梯
- 难度：简单

### 2. 买卖股票的最佳时机
- 难度：简单

### 3. 打家劫舍
- 难度：中等

### 4. 不同路径
- 难度：中等

### 5. 分割等和子集
- 难度：中等

#### 例题详解：不同路径

##### 思路
- 机器人每次只能向右或向下。
- 到达某个格子 `(i, j)` 的方法数，等于：
  - 从上面来
  - 从左边来
- 所以：
  - `dp[i][j] = dp[i-1][j] + dp[i][j-1]`

```python
def uniquePaths(m, n):
    dp = [[1] * n for _ in range(m)]

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

    return dp[m - 1][n - 1]
```

## 6.7 贪心

### 1. 分发饼干
- 难度：简单

### 2. 柠檬水找零
- 难度：简单

### 3. 跳跃游戏
- 难度：中等

### 4. 用最少数量的箭引爆气球
- 难度：中等

### 5. 划分字母区间
- 难度：中等

#### 例题详解：划分字母区间

##### 思路
- 每个字符最后一次出现的位置决定了这个字符最晚必须放在哪个区间里。
- 扫描字符串时，维护当前区间最远右边界。
- 当扫描位置到达右边界时，就可以切分出一个区间。

```python
def partitionLabels(s):
    last_pos = {ch: i for i, ch in enumerate(s)}

    ans = []
    start = 0
    end = 0

    for i, ch in enumerate(s):
        end = max(end, last_pos[ch])

        if i == end:
            ans.append(end - start + 1)
            start = i + 1

    return ans
```

## 6.8 BFS

### 1. 二叉树的层序遍历
- 难度：中等

### 2. 二叉树的右视图
- 难度：中等

### 3. 腐烂的橘子
- 难度：中等

### 4. 钥匙和房间
- 难度：中等

### 5. 单词接龙
- 难度：中等

#### 例题详解：二叉树的右视图

##### 思路
- 每层最右边的节点，就是从右侧看到的节点。
- 做层序遍历时，记录每一层最后出队的节点值即可。

```python
from collections import deque


def rightSideView(root):
    if not root:
        return []

    q = deque([root])
    ans = []

    while q:
        level_size = len(q)

        for i in range(level_size):
            node = q.popleft()

            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)

            # 每层最后一个节点就是右视图看到的节点
            if i == level_size - 1:
                ans.append(node.val)

    return ans
```

## 6.9 DFS / 回溯

### 1. 二叉树的最大深度
- 难度：简单

### 2. 路径总和
- 难度：简单

### 3. 组合
- 难度：中等

### 4. 电话号码的字母组合
- 难度：中等

### 5. 单词搜索
- 难度：中等

#### 例题详解：电话号码的字母组合

##### 思路
- 每个数字对应若干字母。
- 对于每一位数字，都去尝试它映射的所有字母。
- 当前路径长度等于数字串长度时，就得到一个完整组合。

```python
def letterCombinations(digits):
    if not digits:
        return []

    mapping = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
    }

    ans = []
    path = []

    def dfs(index):
        if index == len(digits):
            ans.append("".join(path))
            return

        for ch in mapping[digits[index]]:
            path.append(ch)
            dfs(index + 1)
            path.pop()

    dfs(0)
    return ans
```

## 6.10 图算法

### 1. 查找是否存在路径
- 难度：简单

### 2. 岛屿数量
- 难度：中等

### 3. 课程表
- 难度：中等

### 4. 省份数量
- 难度：中等

### 5. 网络延迟时间
- 难度：中等

#### 例题详解：课程表

##### 思路
- 有依赖关系时，先修课可以看作一条有向边。
- 如果图中有环，就无法修完所有课程。
- 用拓扑排序：
  - 把入度为 0 的节点入队
  - 每弹出一个节点，就减少它后继节点入度
  - 若最终处理节点数等于课程数，则无环

```python
from collections import defaultdict, deque


def canFinish(numCourses, prerequisites):
    graph = defaultdict(list)
    indegree = [0] * numCourses

    for course, pre in prerequisites:
        graph[pre].append(course)
        indegree[course] += 1

    q = deque([i for i in range(numCourses) if indegree[i] == 0])
    visited = 0

    while q:
        course = q.popleft()
        visited += 1

        for next_course in graph[course]:
            indegree[next_course] -= 1
            if indegree[next_course] == 0:
                q.append(next_course)

    return visited == numCourses
```

---

## 7. 面试复习建议

### 7.1 推荐学习顺序
1. `list`、`dict`、`set`、`deque`、`heapq`
2. 双指针、滑动窗口、哈希、二分
3. 树、递归、BFS、DFS
4. 动态规划、贪心、图算法

### 7.2 每道题复盘模板
- 题型是什么
- 暴力解法是什么
- 优化点是什么
- 为什么这种方法成立
- 时间复杂度是多少
- 容易错在哪里

### 7.3 必背模板
- 双指针
- 滑动窗口
- 哈希统计
- 二分边界
- BFS
- DFS / 回溯
- 一维 DP / 二维 DP
- 拓扑排序
- 并查集

---

## 8. 总结

- 数据结构决定“数据怎么存”。
- 算法思想决定“问题怎么拆、怎么优化”。
- 面试里最重要的能力，不是会背多少题，而是看到题目后能快速判断：
  - 它属于哪一类
  - 应该先用什么结构
  - 是否有更优思路

如果继续深化，这份文档最适合配合两件事一起用：
- 一份按天安排的刷题计划
- 一份单独整理的 Python 模板速查表

