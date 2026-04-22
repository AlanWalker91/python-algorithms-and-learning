# Python 数据结构与算法 · 结构化知识图谱

> 适用场景：测试开发 / 后端工程师面试备战  
> 覆盖范围：数据结构原理 · 算法思想 · 面试真题解析 · 整体框架

---

# 第一部分：Python 数据结构

## 1.1 列表 `list`

### 底层实现
- **动态数组（Dynamic Array）**：底层是一块连续内存，存储指向对象的指针
- 扩容策略：容量不足时按约 1.125 倍增长（过分配机制），避免频繁 realloc
- 内存布局：`[ptr0][ptr1][ptr2]...` 每个槽位固定 8 字节（64 位系统指针）

### Python 实现
```python
lst = []                    # 内置，无需导入
lst = list(range(10))       # 从可迭代对象构建
lst = [x**2 for x in range(5)]  # 列表推导式
```

### 常用方法与时间复杂度

| 操作 | 方法 | 时间复杂度 | 说明 |
|------|------|-----------|------|
| 末尾追加 | `append(x)` | O(1) 均摊 | 扩容时 O(n) |
| 末尾弹出 | `pop()` | O(1) | |
| 任意位置插入 | `insert(i, x)` | O(n) | 需要移动元素 |
| 任意位置删除 | `pop(i)` / `del lst[i]` | O(n) | |
| 查找 | `index(x)` / `in` | O(n) | 线性扫描 |
| 随机访问 | `lst[i]` | O(1) | 指针偏移 |
| 切片 | `lst[a:b]` | O(k) | k=切片长度 |
| 排序 | `sort()` | O(n log n) | Timsort |
| 反转 | `reverse()` | O(n) | |
| 长度 | `len(lst)` | O(1) | 缓存在对象头 |
| 扩展 | `extend(iterable)` | O(k) | k=新元素数量 |

### 典型应用场景
- **栈**：`append()` + `pop()` 模拟 LIFO
- **滑动窗口**：双指针 + 切片维护窗口
- **前缀和**：预处理数组加速区间查询
- **单调栈**：维护递增/递减序列处理"下一个更大元素"

---

## 1.2 元组 `tuple`

### 底层实现
- **静态数组**：创建后长度固定，内存连续，不可变
- CPython 有元组缓存池（长度 ≤ 20），小元组复用对象

### Python 实现
```python
t = (1, 2, 3)
t = tuple([1, 2, 3])
single = (1,)   # 单元素必须有逗号
```

### 常用操作与时间复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 索引访问 `t[i]` | O(1) | |
| 切片 `t[a:b]` | O(k) | |
| 查找 `in` | O(n) | |
| 解包 `a, b = t` | O(n) | |

### 典型应用场景
- **函数多返回值**：`return x, y`
- **字典键**：不可变故可哈希，作为复合键 `dict[(x,y)]`
- **命名元组**：`collections.namedtuple` 增强可读性

---

## 1.3 字典 `dict`

### 底层实现
- **哈希表（Hash Table）**：开放寻址法（Python 3.6+ 用紧凑哈希表）
- Python 3.7+ 字典**保证插入顺序**
- 哈希冲突：伪随机探测（`j = (5*j + 1 + perturb) % size`）
- 装载因子超过 2/3 时触发扩容（扩为原来 4 倍）

```
内部结构（简化）:
indices: [-, 0, -, 2, 1, -, ...]   # 哈希槽，存条目索引
entries: [(hash, key, val), ...]    # 紧凑条目数组
```

### Python 实现
```python
d = {}
d = dict(a=1, b=2)
d = {k: v for k, v in pairs}       # 字典推导式
d = dict.fromkeys(['a','b'], 0)     # 批量初始化
```

### 常用方法与时间复杂度

| 操作 | 方法 | 时间复杂度 | 说明 |
|------|------|-----------|------|
| 查找 | `d[key]` / `get(k, default)` | O(1) 均摊 | 哈希冲突时退化 |
| 插入/更新 | `d[key] = val` | O(1) 均摊 | |
| 删除 | `del d[key]` / `pop(key)` | O(1) 均摊 | |
| 存在判断 | `key in d` | O(1) | |
| 遍历键 | `d.keys()` | O(1) 返回视图 | 遍历 O(n) |
| 遍历值 | `d.values()` | O(1) 返回视图 | |
| 遍历键值 | `d.items()` | O(1) 返回视图 | |
| 合并 | `d.update(other)` / `d1\|d2` | O(k) | |
| 默认值 | `setdefault(k, default)` | O(1) | |

### 典型应用场景
- **频率统计**：`Counter` / 手写 `freq[c] = freq.get(c,0)+1`
- **缓存/记忆化**：动态规划 memo 表
- **图的邻接表**：`graph = defaultdict(list)`
- **两数之和**：哈希表存补数 O(n) 解决

---

## 1.4 集合 `set` / `frozenset`

### 底层实现
- **哈希表**（无值部分），只存 key
- 与 dict 共享大部分实现逻辑
- `frozenset` 不可变，可作为字典键

### Python 实现
```python
s = {1, 2, 3}
s = set([1, 2, 2, 3])   # 自动去重
fs = frozenset([1, 2])
```

### 常用方法与时间复杂度

| 操作 | 方法 | 时间复杂度 |
|------|------|-----------|
| 添加 | `add(x)` | O(1) |
| 删除 | `remove(x)` / `discard(x)` | O(1) |
| 查找 | `x in s` | O(1) |
| 并集 | `s1 \| s2` / `union()` | O(m+n) |
| 交集 | `s1 & s2` / `intersection()` | O(min(m,n)) |
| 差集 | `s1 - s2` / `difference()` | O(m) |
| 对称差 | `s1 ^ s2` | O(m+n) |

### 典型应用场景
- **去重**：`list(set(arr))`
- **成员测试**：O(1) 代替列表的 O(n)
- **图遍历 visited**：`visited = set()`
- **求公共元素**：`set(a) & set(b)`

---

## 1.5 双端队列 `collections.deque`

### 底层实现
- **双向链表（由固定大小块组成）**：非单链表，而是块状双向链表
- 块大小约 64 字节，减少指针开销
- 两端 append/pop 均为 O(1)，中间操作 O(n)

### Python 实现
```python
from collections import deque
dq = deque()
dq = deque([1, 2, 3], maxlen=5)  # 有界队列，满后自动丢弃
```

### 常用方法与时间复杂度

| 操作 | 方法 | 时间复杂度 |
|------|------|-----------|
| 右端追加 | `append(x)` | O(1) |
| 左端追加 | `appendleft(x)` | O(1) |
| 右端弹出 | `pop()` | O(1) |
| 左端弹出 | `popleft()` | O(1) |
| 旋转 | `rotate(n)` | O(k) |
| 随机访问 | `dq[i]` | O(n) ⚠️ |

### 典型应用场景
- **BFS 队列**：`popleft()` 保证先进先出
- **滑动窗口最大值**：单调队列
- **LRU Cache**：配合字典实现 O(1) 操作
- **栈 + 队列**：双端特性兼顾两种结构

---

## 1.6 堆 `heapq`

### 底层实现
- **最小堆（Min-Heap）**：完全二叉树，用数组表示
- 父节点 `i`，左子 `2i+1`，右子 `2i+2`
- `heapq` 模块基于 list 实现，始终是**最小堆**
- 若需最大堆：存负数或用 `(-val, val)` 技巧

```
堆数组: [1, 3, 2, 7, 4, 5, 6]
对应树:
        1
      /   \
     3     2
    / \   / \
   7   4 5   6
```

### Python 实现
```python
import heapq
h = []
heapq.heappush(h, val)          # 入堆
heapq.heappop(h)                # 出堆（最小值）
heapq.heapify(lst)              # 原地建堆 O(n)
heapq.nlargest(k, iterable)     # TopK 最大
heapq.nsmallest(k, iterable)    # TopK 最小
heapq.heappushpop(h, x)        # 入堆后立即出堆，高效
```

### 时间复杂度

| 操作 | 复杂度 |
|------|--------|
| heappush | O(log n) |
| heappop | O(log n) |
| heapify | O(n) |
| 查看堆顶 `h[0]` | O(1) |
| nlargest/nsmallest | O(n log k) |

### 典型应用场景
- **TopK 问题**：维护大小为 K 的堆
- **合并 K 个有序列表**：多路归并
- **Dijkstra 最短路**：优先队列
- **任务调度**：按优先级处理

---

## 1.7 有序字典 `collections.OrderedDict`

### 底层实现
- Python 3.7+ 普通 dict 已保证插入顺序
- `OrderedDict` 额外支持 `move_to_end()` 和顺序敏感的 `==`

### 典型应用场景
- **LRU Cache 手写**：`move_to_end()` + `popitem(last=False)`

---

## 1.8 计数器 `collections.Counter`

```python
from collections import Counter
c = Counter("abracadabra")
# Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
c.most_common(3)   # 前3个最频繁元素
c1 + c2            # 合并计数
c1 - c2            # 差集计数
c1 & c2            # 取最小
c1 | c2            # 取最大
```

### 典型应用场景
- **字母异位词**：`Counter(s1) == Counter(s2)`
- **频率统计**：单词计数、字符分析
- **滑动窗口字符匹配**

---

## 1.9 默认字典 `collections.defaultdict`

```python
from collections import defaultdict
graph = defaultdict(list)          # 图的邻接表
freq = defaultdict(int)            # 计数
nested = defaultdict(lambda: defaultdict(int))  # 嵌套
```

---

## 1.10 链表（手动实现）

Python 无内置链表，面试中需手写：

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# 构建链表: 1 -> 2 -> 3
head = ListNode(1, ListNode(2, ListNode(3)))
```

### 时间复杂度

| 操作 | 单链表 | 双向链表 |
|------|--------|---------|
| 头部插入/删除 | O(1) | O(1) |
| 尾部插入 | O(n) | O(1)（有尾指针） |
| 中间插入（已知节点） | O(1) | O(1) |
| 查找 | O(n) | O(n) |
| 随机访问 | O(n) | O(n) |

### 典型应用场景
- **反转链表**、**合并有序链表**
- **环检测**：快慢指针
- **LRU Cache 底层**

---

## 1.11 栈与队列（对比）

| 特性 | 栈 (Stack) | 队列 (Queue) |
|------|-----------|-------------|
| 原则 | LIFO（后进先出）| FIFO（先进先出）|
| Python 实现 | `list` append/pop | `deque` append/popleft |
| 典型场景 | DFS、括号匹配、表达式求值 | BFS、任务队列 |

---

## 1.12 数据结构选型速查

| 需求 | 推荐结构 |
|------|---------|
| 有序序列，频繁末尾增删 | `list` |
| 频繁两端增删 | `deque` |
| 键值映射，快速查找 | `dict` |
| 去重 / 集合运算 | `set` |
| 频率统计 | `Counter` |
| 按优先级处理 | `heapq` |
| 需要 TopK | `heapq.nlargest/nsmallest` |
| 图邻接表 | `defaultdict(list)` |
| 不可变序列 | `tuple` |
| LRU 缓存 | `OrderedDict` 或 `functools.lru_cache` |


---

# 第二部分：算法思想

---

## 2.1 双指针（Two Pointers）

### 核心思想
用两个指针在数组/链表上协同移动，**将 O(n²) 的暴力枚举降至 O(n)**。

### 三种模式

```
① 对撞指针（Collision）：左右向中间收缩
   [l] --------> <-------- [r]
   适用：有序数组两数之和、三数之和、盛水容器

② 快慢指针（Fast-Slow）：同向不同速
   [slow] -> [fast] ->->->
   适用：链表环检测、链表中点、删除倒数第N个节点

③ 同向双指针（Sliding Window 的基础形式）：
   [l] -> [r]->->
   适用：无重复字符的最长子串（可归入滑动窗口）
```

### 前提条件
- 对撞指针：数组**有序**或有单调性
- 快慢指针：链表问题，或判断循环
- 问题结构满足"两端逼近"的单调性

### 时间 / 空间复杂度
- 时间：O(n)，每个元素最多被访问常数次
- 空间：O(1)，只用额外的两个指针

---

## 2.2 滑动窗口（Sliding Window）

### 核心思想
维护一个**可变长度的窗口**（子数组/子串），窗口随条件**右扩左缩**，避免重复计算。

```
窗口状态转移：
right 持续右移（扩大窗口）
    -> 条件不满足时 left 右移（缩小窗口）
    -> 每一步记录/更新答案

[left ............. right]
        valid window
```

### 两类问题
1. **定长窗口**：窗口大小固定为 k，整体右滑
2. **变长窗口**：窗口大小动态调整（最常见）

### 框架模板
```python
def sliding_window(s):
    left, right = 0, 0
    window = {}          # 窗口内的状态
    result = 0

    while right < len(s):
        c = s[right]
        right += 1
        # 更新窗口状态（扩大）
        window[c] = window.get(c, 0) + 1

        # 判断是否需要收缩
        while 窗口不合法:
            d = s[left]
            left += 1
            # 更新窗口状态（缩小）
            window[d] -= 1
            if window[d] == 0:
                del window[d]

        # 更新答案
        result = max(result, right - left)

    return result
```

### 典型场景
- 最长无重复字符子串
- 找所有字母异位词
- 最小覆盖子串
- 定长窗口最大平均值

---

## 2.3 哈希（Hash）

### 核心思想
通过哈希函数将 key 映射到固定位置，实现 **O(1) 查找/插入/删除**，以空间换时间。

### 关键机制
```
哈希函数：hash(key) -> index
冲突解决：
  - 链地址法（Separate Chaining）：槽位存链表
  - 开放寻址法（Open Addressing）：Python dict 使用

装载因子（load factor）= 元素数 / 槽位数
  > 临界值时扩容（Python: 2/3）
```

### 哈希在算法中的作用
| 场景 | 技巧 |
|------|------|
| 两数之和 | 存已遍历元素，查补数 |
| 子数组和为 K | 前缀和 + 哈希表 |
| 最长连续序列 | set 存所有元素，跳过非起点 |
| 字母异位词分组 | 排序后的字符串作 key |
| 频率统计 | Counter / defaultdict(int) |
| 去重 | set |

### 哈希碰撞与安全
- Python 对字符串哈希加入随机 seed（PYTHONHASHSEED），防止哈希洪泛攻击

---

## 2.4 二分查找（Binary Search）

### 核心思想
在**有序**或**单调**区间上，每次排除一半搜索空间，O(log n) 找到目标。

### 三种经典写法

```python
# ① 精确查找
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2   # 防溢出写法
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# ② 查找左边界（第一个 >= target 的位置）
def left_bound(nums, target):
    left, right = 0, len(nums)   # 注意：right = len(nums)
    while left < right:          # 注意：< 不是 <=
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left

# ③ 查找右边界（最后一个 <= target 的位置）
def right_bound(nums, target):
    left, right = 0, len(nums)
    while left < right:
        mid = (left + right) // 2
        if nums[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left - 1
```

### 二分的本质：**在答案空间上二分**
不仅限于有序数组，只要满足**单调性**即可：
- 在结果范围 [lo, hi] 上二分
- `check(mid)` 判断 mid 是否可行
- 找最小可行 / 最大可行答案

### 典型场景
- 有序数组查找 / 边界
- 搜索旋转排序数组
- 寻找峰值
- 在答案上二分：最小化最大值、切割木头、分配香蕉

---

## 2.5 递归与分治（Recursion & Divide and Conquer）

### 核心思想
**递归**：函数调用自身，将大问题分解为同类小问题  
**分治**：将问题分成若干**独立子问题**，分别求解后合并

```
分治三步骤：
① Divide   — 将问题分解为规模更小的子问题
② Conquer  — 递归求解子问题
③ Combine  — 合并子问题的结果
```

### 递归关键要素
```python
def recursion(args):
    # 1. 终止条件（Base Case）—— 必须有！
    if base_case:
        return base_result
    
    # 2. 递归调用（缩小规模）
    sub_result = recursion(smaller_args)
    
    # 3. 处理当前层逻辑
    return process(sub_result)
```

### 递归 vs 迭代
| | 递归 | 迭代 |
|--|------|------|
| 代码简洁性 | 高 | 中 |
| 空间 | O(深度) 调用栈 | O(1) 或 O(n) 显式栈 |
| 风险 | 栈溢出 | 无 |
| 尾递归优化 | Python 不支持 | — |

### 经典分治算法

| 算法 | 时间复杂度 | 思路 |
|------|-----------|------|
| 归并排序 | O(n log n) | 分两半，各自排序，合并 |
| 快速排序 | O(n log n) 均摊 | partition 后递归两侧 |
| 二叉树遍历 | O(n) | 递归左右子树 |
| 快速幂 | O(log n) | 奇偶分治 |
| 最大子数组（跨中点） | O(n log n) | 分治合并 |

---

## 2.6 动态规划（Dynamic Programming）

### 核心思想
将原问题拆解为**有重叠的子问题**，存储子问题结果（记忆化/DP 表），避免重复计算。

```
DP 四要素：
① 状态定义：dp[i] 表示什么？
② 状态转移方程：dp[i] = f(dp[i-1], dp[i-2], ...)
③ 初始化：base case
④ 遍历顺序：确保计算 dp[i] 时子问题已解
```

### DP vs 递归+记忆化
两者等价，区别在于：
- **自顶向下**（记忆化递归）：更直觉，易写
- **自底向上**（迭代DP）：无栈溢出，可优化空间

### 常见 DP 类型

| 类型 | 代表题 | 状态特征 |
|------|--------|---------|
| 线性 DP | 爬楼梯、最大子数组和 | dp[i] 依赖前若干项 |
| 背包 DP | 0/1背包、完全背包 | dp[i][w] 二维状态 |
| 区间 DP | 戳气球、矩阵链乘 | dp[l][r] 区间状态 |
| 树形 DP | 打家劫舍 III | 在树上递归 |
| 状态压缩 DP | 旅行商、棋盘覆盖 | 用位掩码表示状态集合 |
| 序列 DP | LCS、LIS、编辑距离 | 两序列的二维 dp |

### 空间优化
很多 DP 只依赖前一行/前几项 → 滚动数组压缩到 O(1) 或 O(n)

---

## 2.7 贪心（Greedy）

### 核心思想
每一步都做**局部最优选择**，期望全局也最优。无需枚举所有可能，效率极高。

### 贪心成立的条件
1. **贪心选择性**：局部最优能推导出全局最优
2. **最优子结构**：子问题的最优解构成整体最优解

> ⚠️ 贪心不像 DP 有通用框架，需要**证明**贪心策略的正确性（交换论证法）

### 常见贪心模型

| 场景 | 策略 |
|------|------|
| 区间调度（最多不重叠区间）| 按结束时间排序，贪心选最早结束 |
| 跳跃游戏 | 维护最远可达位置 |
| 分发糖果 | 两次遍历（左→右、右→左）取 max |
| 买卖股票（可多次）| 只要明天涨今天就买 |
| Huffman 编码 | 最小堆贪心合并 |

---

## 2.8 广度优先搜索（BFS）

### 核心思想
从起点出发，**逐层扩展**，先访问距离近的节点。天然求**最短路径**（无权图）。

### 框架模板
```python
from collections import deque

def bfs(graph, start, target):
    queue = deque([start])
    visited = {start}
    step = 0              # 记录层数（距离）

    while queue:
        size = len(queue)           # 当前层的节点数
        for _ in range(size):       # 逐层处理
            node = queue.popleft()
            if node == target:
                return step
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        step += 1

    return -1  # 未找到
```

### BFS vs DFS 选型

| | BFS | DFS |
|--|-----|-----|
| 数据结构 | 队列 | 栈（或递归） |
| 空间复杂度 | O(宽度) | O(深度) |
| 最短路 | ✅ 天然保证 | ❌ 需要额外处理 |
| 路径回溯 | 不直接支持 | 自然支持 |
| 适合场景 | 最短路、层序遍历 | 路径枚举、连通性、拓扑 |

### 典型场景
- 迷宫最短路、二叉树层序遍历
- 单词接龙、最小基因变化
- 多源 BFS（腐烂的橘子）
- 双向 BFS（优化搜索空间）

---

## 2.9 深度优先搜索（DFS）

### 核心思想
沿一条路走到底（或到终止条件），然后**回溯**，尝试其他分支。

### 回溯模板（排列/组合/子集）
```python
def backtrack(path, choices):
    # 终止条件
    if 满足条件:
        result.append(path[:])  # 注意要复制
        return

    for choice in choices:
        # 做选择
        path.append(choice)
        visited.add(choice)

        # 递归
        backtrack(path, next_choices)

        # 撤销选择（回溯）
        path.pop()
        visited.remove(choice)
```

### 剪枝策略
- **去重剪枝**：排序后跳过重复元素
- **路径长度剪枝**：超过目标提前返回
- **可行性剪枝**：当前状态不可能得到有效解时直接返回

### 典型场景
- 全排列、组合、子集
- N 皇后、数独
- 岛屿数量（图的连通性）
- 路径总和（二叉树路径）

---

## 2.10 图算法

### 图的表示

```python
# 邻接表（推荐，稀疏图）
graph = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['D', 'E'],
}

# 邻接矩阵（稠密图）
matrix = [[0]*n for _ in range(n)]
matrix[u][v] = weight

# 带权邻接表
graph = defaultdict(list)
graph[u].append((v, weight))
```

### 拓扑排序（Topological Sort）

```python
# Kahn 算法（BFS）
def topological_sort(n, edges):
    in_degree = [0] * n
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque([i for i in range(n) if in_degree[i] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []  # 空则有环
```

### Dijkstra 最短路

```python
import heapq

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]   # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue     # 过时的记录，跳过
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    return dist
```

**时间复杂度**：O((V + E) log V)  
**限制**：不能有负权边（负权用 Bellman-Ford）

### 并查集（Union-Find）

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # 路径压缩
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        # 按秩合并
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
```

### 常见图算法复杂度汇总

| 算法 | 时间复杂度 | 空间复杂度 | 适用 |
|------|-----------|-----------|------|
| BFS/DFS | O(V+E) | O(V) | 连通性、路径 |
| Dijkstra（堆） | O((V+E)logV) | O(V+E) | 非负权最短路 |
| Bellman-Ford | O(VE) | O(V) | 含负权最短路 |
| Floyd-Warshall | O(V³) | O(V²) | 全对最短路 |
| Kahn（拓扑排序） | O(V+E) | O(V+E) | DAG 排序/判环 |
| Kruskal（最小生成树）| O(E log E) | O(V) | MST |
| Prim（最小生成树）| O((V+E)logV) | O(V) | MST |
| 并查集（路径压缩）| O(α(n)) ≈ O(1) | O(n) | 连通分量 |


---

# 第三部分：算法面试题精讲（每类4题）

---

## 3.1 双指针专题

### 题目1：两数之和 II（有序数组）｜ LeetCode 167

**思路**：对撞指针，利用数组有序性，大了左移右指针，小了右移左指针

```python
def twoSum(numbers: list[int], target: int) -> list[int]:
    left, right = 0, len(numbers) - 1
    
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]   # 题目返回 1-indexed
        elif s < target:
            left += 1    # 和太小，左指针右移增大和
        else:
            right -= 1   # 和太大，右指针左移减小和
    
    return []  # 题目保证有解，实际不会到这里
```
**时间 O(n)，空间 O(1)**

---

### 题目2：盛最多水的容器｜ LeetCode 11

**思路**：对撞指针。容积 = min(height[l], height[r]) × (r - l)。  
移动较矮的一边，才有机会找到更大的容积（移动较高的一边只会变小）。

```python
def maxArea(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_water = 0
    
    while left < right:
        # 当前面积 = 短板高度 × 宽度
        h = min(height[left], height[right])
        w = right - left
        max_water = max(max_water, h * w)
        
        # 移动较矮的指针，才有可能增大面积
        # 若移动较高的指针，宽度减小且高度只能相等或减小，面积一定减小
        if height[left] <= height[right]:
            left += 1
        else:
            right -= 1
    
    return max_water
```
**时间 O(n)，空间 O(1)**

---

### 题目3：三数之和｜ LeetCode 15

**思路**：排序 + 对撞指针。固定一个数，在剩余区间用对撞指针找两数之和。  
关键：去重处理，跳过重复元素。

```python
def threeSum(nums: list[int]) -> list[list[int]]:
    nums.sort()          # 先排序，保证有序性
    result = []
    n = len(nums)
    
    for i in range(n - 2):
        # 最小数都大于0，不可能三数之和为0
        if nums[i] > 0:
            break
        
        # 跳过重复的第一个数
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        
        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                # 跳过重复的第二、三个数
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    
    return result
```
**时间 O(n²)，空间 O(1)（不计返回值）**

---

### 题目4：链表中倒数第 K 个节点｜ LeetCode 19 变体

**思路**：快慢指针。fast 先走 k 步，然后 fast 和 slow 同步走，fast 到尾时 slow 在倒数第 k 个。

```python
def removeNthFromEnd(head, n: int):
    # 哑节点，处理删除头节点的边界情况
    dummy = ListNode(0, head)
    fast = dummy
    slow = dummy
    
    # fast 先走 n+1 步（多走1步是为了让 slow 停在待删节点的前一个）
    for _ in range(n + 1):
        fast = fast.next
    
    # fast 和 slow 同步移动，直到 fast 为 None
    while fast is not None:
        fast = fast.next
        slow = slow.next
    
    # slow.next 就是要删除的节点
    slow.next = slow.next.next
    
    return dummy.next
```
**时间 O(n)，空间 O(1)**

---

## 3.2 滑动窗口专题

### 题目1：无重复字符的最长子串｜ LeetCode 3

**思路**：变长滑动窗口，用 set 维护窗口内字符，right 右移，有重复则 left 右移缩小窗口。

```python
def lengthOfLongestSubstring(s: str) -> int:
    window = set()     # 窗口内的字符集合
    left = 0
    max_len = 0
    
    for right in range(len(s)):
        # 如果右边字符已在窗口内，缩小窗口直到无重复
        while s[right] in window:
            window.remove(s[left])
            left += 1
        
        # 将右边字符加入窗口
        window.add(s[right])
        # 更新最大长度
        max_len = max(max_len, right - left + 1)
    
    return max_len
```
**时间 O(n)，空间 O(min(m,n))，m 为字符集大小**

---

### 题目2：找所有字母异位词｜ LeetCode 438

**思路**：定长滑动窗口（窗口大小 = p 的长度），用 Counter 比较窗口状态。

```python
from collections import Counter

def findAnagrams(s: str, p: str) -> list[int]:
    if len(s) < len(p):
        return []
    
    p_count = Counter(p)             # 目标字符频次
    window = Counter(s[:len(p)])     # 初始窗口
    result = []
    
    # 先检查第一个窗口
    if window == p_count:
        result.append(0)
    
    # 滑动窗口
    for i in range(1, len(s) - len(p) + 1):
        # 加入新字符（窗口右端）
        new_char = s[i + len(p) - 1]
        window[new_char] += 1
        
        # 移出旧字符（窗口左端）
        old_char = s[i - 1]
        window[old_char] -= 1
        if window[old_char] == 0:
            del window[old_char]   # 保持 Counter 干净
        
        # 检查当前窗口是否是异位词
        if window == p_count:
            result.append(i)
    
    return result
```
**时间 O(n)，空间 O(1)（字符集有限）**

---

### 题目3：最小覆盖子串｜ LeetCode 76 ⭐（Hard）

**思路**：变长滑动窗口，维护 need（需要的字符频次）和 window（已有的），  
用 valid 计数满足条件的字符数量，valid == len(need) 时记录并尝试缩小。

```python
from collections import defaultdict

def minWindow(s: str, t: str) -> str:
    need = defaultdict(int)
    for c in t:
        need[c] += 1
    
    window = defaultdict(int)
    left, right = 0, 0
    valid = 0              # 已满足条件的字符种类数
    min_len = float('inf')
    start = 0             # 最小窗口的起始位置
    
    while right < len(s):
        c = s[right]
        right += 1
        
        # 更新窗口
        if c in need:
            window[c] += 1
            if window[c] == need[c]:   # 该字符数量刚好满足
                valid += 1
        
        # 当所有字符都满足时，尝试缩小窗口
        while valid == len(need):
            # 更新最小覆盖子串
            if right - left < min_len:
                min_len = right - left
                start = left
            
            d = s[left]
            left += 1
            if d in need:
                if window[d] == need[d]:  # 移除后该字符不满足了
                    valid -= 1
                window[d] -= 1
    
    return s[start:start + min_len] if min_len != float('inf') else ""
```
**时间 O(n)，空间 O(k)，k 为字符集大小**

---

### 题目4：滑动窗口最大值｜ LeetCode 239 ⭐（Hard）

**思路**：单调队列（deque 维护递减序列），队首始终是当前窗口最大值。  
新元素入队前，清除所有比它小的元素（它们永远不会是最大值）。

```python
from collections import deque

def maxSlidingWindow(nums: list[int], k: int) -> list[int]:
    dq = deque()    # 存下标，队首对应最大值
    result = []
    
    for i, num in enumerate(nums):
        # 移除不在窗口内的队首元素
        if dq and dq[0] < i - k + 1:
            dq.popleft()
        
        # 维护单调递减：清除所有比当前元素小的队尾元素
        # 这些元素不可能成为窗口最大值（当前元素更大且更靠右）
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        
        dq.append(i)
        
        # 窗口大小满足 k 时开始记录结果
        if i >= k - 1:
            result.append(nums[dq[0]])   # 队首是最大值
    
    return result
```
**时间 O(n)，空间 O(k)**

---

## 3.3 哈希专题

### 题目1：两数之和｜ LeetCode 1

**思路**：遍历时用哈希表存已见过的数及其下标，查找补数是否存在。

```python
def twoSum(nums: list[int], target: int) -> list[int]:
    seen = {}    # {数值: 下标}
    
    for i, num in enumerate(nums):
        complement = target - num    # 需要的另一个数
        
        if complement in seen:
            return [seen[complement], i]   # 找到了
        
        seen[num] = i   # 存入当前数
    
    return []
```
**时间 O(n)，空间 O(n)**

---

### 题目2：字母异位词分组｜ LeetCode 49

**思路**：将每个单词排序后作为 key，相同 key 的单词是异位词组。

```python
from collections import defaultdict

def groupAnagrams(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    
    for s in strs:
        # 排序后的字符串作为哈希 key（异位词排序后相同）
        key = tuple(sorted(s))    # 用 tuple 保证可哈希
        groups[key].append(s)
    
    return list(groups.values())

# 进阶：用字符频次元组作为 key，避免排序，O(n*k) 而非 O(n*k*log k)
def groupAnagrams_v2(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for c in s:
            count[ord(c) - ord('a')] += 1
        groups[tuple(count)].append(s)
    return list(groups.values())
```
**时间 O(n·k·log k)，空间 O(n·k)**

---

### 题目3：最长连续序列｜ LeetCode 128

**思路**：用 set 存所有元素。对每个元素，若 x-1 不在 set 中，说明它是序列起点，  
然后向右延伸计数。关键：只从起点开始计，避免 O(n²)。

```python
def longestConsecutive(nums: list[int]) -> int:
    num_set = set(nums)    # O(1) 查找
    max_len = 0
    
    for num in num_set:
        # 只有序列起点才开始计数（避免重复计算）
        if num - 1 not in num_set:
            current = num
            length = 1
            
            # 向右延伸
            while current + 1 in num_set:
                current += 1
                length += 1
            
            max_len = max(max_len, length)
    
    return max_len
```
**时间 O(n)（每个元素最多被访问两次），空间 O(n)**

---

### 题目4：和为 K 的子数组｜ LeetCode 560

**思路**：前缀和 + 哈希表。`sum[i] - sum[j] = k` 等价于 `sum[j] = sum[i] - k`。  
遍历时用哈希表查找已经出现过的前缀和。

```python
from collections import defaultdict

def subarraySum(nums: list[int], k: int) -> int:
    # prefix_count[s] = 前缀和为 s 的次数
    prefix_count = defaultdict(int)
    prefix_count[0] = 1    # 前缀和为0的情况（空子数组）
    
    prefix_sum = 0
    count = 0
    
    for num in nums:
        prefix_sum += num
        
        # 查找有多少个 j 使得 prefix_sum[j] = prefix_sum - k
        # 即 [j+1, i] 这段子数组的和为 k
        count += prefix_count[prefix_sum - k]
        
        # 记录当前前缀和
        prefix_count[prefix_sum] += 1
    
    return count
```
**时间 O(n)，空间 O(n)**

---

## 3.4 二分查找专题

### 题目1：搜索旋转排序数组｜ LeetCode 33

**思路**：旋转后有一半是有序的，每次判断哪半是有序的，再决定在哪半搜索。

```python
def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        
        # 判断左半 [left, mid] 是否有序
        if nums[left] <= nums[mid]:
            # 左半有序，判断 target 是否在左半
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # 右半 [mid, right] 有序，判断 target 是否在右半
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1
```
**时间 O(log n)，空间 O(1)**

---

### 题目2：寻找旋转排序数组中的最小值｜ LeetCode 153

**思路**：最小值在旋转点右边。若 nums[mid] > nums[right]，最小值在右半；否则在左半（含 mid）。

```python
def findMin(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = (left + right) // 2
        
        if nums[mid] > nums[right]:
            # mid 在旋转点左侧，最小值在右半
            left = mid + 1
        else:
            # mid 在旋转点右侧（含旋转点），最小值在左半（含 mid）
            right = mid
    
    return nums[left]
```
**时间 O(log n)，空间 O(1)**

---

### 题目3：在排序数组中查找元素的第一个和最后一个位置｜ LeetCode 34

**思路**：两次二分分别找左边界和右边界。

```python
def searchRange(nums: list[int], target: int) -> list[int]:
    def find_left(nums, target):
        left, right = 0, len(nums)
        while left < right:
            mid = (left + right) // 2
            if nums[mid] < target:
                left = mid + 1
            else:
                right = mid     # 收缩右边，找最左
        return left
    
    def find_right(nums, target):
        left, right = 0, len(nums)
        while left < right:
            mid = (left + right) // 2
            if nums[mid] <= target:
                left = mid + 1  # 收缩左边，找最右
            else:
                right = mid
        return left - 1
    
    l = find_left(nums, target)
    
    # 先检查是否存在
    if l == len(nums) or nums[l] != target:
        return [-1, -1]
    
    r = find_right(nums, target)
    return [l, r]
```
**时间 O(log n)，空间 O(1)**

---

### 题目4：在答案上二分——爱吃香蕉的珂珂｜ LeetCode 875

**思路**：二分速度 k（答案空间），check 函数验证速度 k 能否在 h 小时内吃完。

```python
import math

def minEatingSpeed(piles: list[int], h: int) -> int:
    def canFinish(speed: int) -> bool:
        """以 speed 的速度能否在 h 小时内吃完"""
        hours = sum(math.ceil(p / speed) for p in piles)
        return hours <= h
    
    # 答案范围：[1, max(piles)]
    left, right = 1, max(piles)
    
    while left < right:
        mid = (left + right) // 2
        
        if canFinish(mid):
            right = mid      # 可以完成，尝试更小的速度
        else:
            left = mid + 1   # 不能完成，需要更大的速度
    
    return left   # 找到满足条件的最小速度
```
**时间 O(n log m)，m = max(piles)，空间 O(1)**

---

## 3.5 递归与分治专题

### 题目1：归并排序（手写）

**思路**：分治。分两半各自排序，再合并两个有序数组。

```python
def merge_sort(nums: list[int]) -> list[int]:
    # Base case：单个或空数组已有序
    if len(nums) <= 1:
        return nums
    
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])   # 递归排序左半
    right = merge_sort(nums[mid:])  # 递归排序右半
    
    return merge(left, right)

def merge(left: list[int], right: list[int]) -> list[int]:
    """合并两个有序数组"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # 将剩余部分追加
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```
**时间 O(n log n)，空间 O(n)**

---

### 题目2：快速幂｜ LeetCode 50

**思路**：分治。`x^n = x^(n/2) * x^(n/2)` 若 n 偶数；`x^(n/2) * x^(n/2) * x` 若 n 奇数。

```python
def myPow(x: float, n: int) -> float:
    def fast_pow(base, exp):
        if exp == 0:
            return 1.0
        
        # 递归求一半的幂（分治核心）
        half = fast_pow(base, exp // 2)
        
        if exp % 2 == 0:
            return half * half              # 偶数
        else:
            return half * half * base       # 奇数多乘一个 base
    
    if n < 0:
        x = 1 / x
        n = -n
    
    return fast_pow(x, n)
```
**时间 O(log n)，空间 O(log n) 递归栈**

---

### 题目3：二叉树的最大深度｜ LeetCode 104

**思路**：递归。左右子树各自求最大深度，取较大值加1（当前根节点贡献1层）。

```python
def maxDepth(root) -> int:
    # Base case：空节点深度为0
    if root is None:
        return 0
    
    # 递归求左右子树深度
    left_depth = maxDepth(root.left)
    right_depth = maxDepth(root.right)
    
    # 当前节点深度 = 较深子树 + 1（自身）
    return max(left_depth, right_depth) + 1
```
**时间 O(n)，空间 O(h)，h 为树的高度**

---

### 题目4：数组中的第 K 个最大元素｜ LeetCode 215（快选）

**思路**：快速选择（Quickselect）。基于快速排序的 partition，每次只递归一侧。

```python
import random

def findKthLargest(nums: list[int], k: int) -> int:
    # 第 k 大 = 第 (n-k) 小，转为找第 target 个（0-indexed）
    target = len(nums) - k
    
    def partition(left, right):
        # 随机选 pivot，避免最坏情况
        pivot_idx = random.randint(left, right)
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]
        pivot = nums[right]
        
        store = left    # store 指向下一个小于 pivot 的位置
        for i in range(left, right):
            if nums[i] <= pivot:
                nums[store], nums[i] = nums[i], nums[store]
                store += 1
        
        nums[store], nums[right] = nums[right], nums[store]
        return store
    
    left, right = 0, len(nums) - 1
    while left <= right:
        pivot_pos = partition(left, right)
        
        if pivot_pos == target:
            return nums[pivot_pos]
        elif pivot_pos < target:
            left = pivot_pos + 1   # 目标在右侧
        else:
            right = pivot_pos - 1  # 目标在左侧
    
    return -1
```
**时间 O(n) 均摊，空间 O(1)**

---

## 3.6 动态规划专题

### 题目1：最长递增子序列（LIS）｜ LeetCode 300

**思路①（DP O(n²)）**：`dp[i]` = 以 nums[i] 结尾的最长递增子序列长度。

```python
def lengthOfLIS_dp(nums: list[int]) -> int:
    n = len(nums)
    dp = [1] * n    # 每个元素单独构成长度为1的子序列
    
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:  # nums[i] 可以接在 nums[j] 后面
                dp[i] = max(dp[i], dp[j] + 1)
    
    return max(dp)

# 思路②（贪心+二分 O(n log n)）
def lengthOfLIS(nums: list[int]) -> int:
    import bisect
    tails = []  # tails[i] = 长度为 i+1 的递增子序列末尾最小值
    
    for num in nums:
        pos = bisect.bisect_left(tails, num)  # 找插入位置
        if pos == len(tails):
            tails.append(num)     # 可以延伸最长子序列
        else:
            tails[pos] = num      # 替换，保持末尾最小
    
    return len(tails)
```

---

### 题目2：编辑距离｜ LeetCode 72 ⭐

**思路**：`dp[i][j]` = word1 前 i 个字符转换为 word2 前 j 个字符所需最少操作数。

```python
def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    
    # dp[i][j]: word1[:i] -> word2[:j] 的最少编辑次数
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # 初始化：将任意字符串变为空字符串
    for i in range(m + 1):
        dp[i][0] = i   # 删除 i 个字符
    for j in range(n + 1):
        dp[0][j] = j   # 插入 j 个字符
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                # 字符相同，不需要操作
                dp[i][j] = dp[i-1][j-1]
            else:
                # 三种操作取最小：
                # dp[i-1][j] + 1   → 删除 word1[i-1]
                # dp[i][j-1] + 1   → 插入 word2[j-1]
                # dp[i-1][j-1] + 1 → 替换 word1[i-1] 为 word2[j-1]
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
    
    return dp[m][n]
```
**时间 O(mn)，空间 O(mn)（可优化为 O(n)）**

---

### 题目3：0/1 背包｜经典模板

**思路**：`dp[j]` = 容量为 j 的背包能装的最大价值。

```python
def knapsack_01(weights: list[int], values: list[int], capacity: int) -> int:
    n = len(weights)
    # dp[j] = 容量为 j 时的最大价值
    dp = [0] * (capacity + 1)
    
    for i in range(n):          # 遍历每件物品
        # 注意：从后往前遍历！防止同一物品被多次使用
        for j in range(capacity, weights[i] - 1, -1):
            # 选或不选第 i 件物品
            dp[j] = max(dp[j],                          # 不选
                        dp[j - weights[i]] + values[i]) # 选
    
    return dp[capacity]

# 完全背包（每件物品可选无限次）：只需改为正向遍历
def knapsack_complete(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        for j in range(weights[i], capacity + 1):  # 正向！
            dp[j] = max(dp[j], dp[j - weights[i]] + values[i])
    return dp[capacity]
```

---

### 题目4：打家劫舍 III（树形 DP）｜ LeetCode 337

**思路**：树形 DP。每个节点有"偷"和"不偷"两个状态，后序遍历（左右子 → 根）。

```python
def rob(root) -> int:
    def dp(node):
        """返回 (不偷当前节点的最大值, 偷当前节点的最大值)"""
        if node is None:
            return (0, 0)
        
        left_skip, left_rob = dp(node.left)
        right_skip, right_rob = dp(node.right)
        
        # 偷当前节点：左右子节点都不能偷
        rob_cur = node.val + left_skip + right_skip
        
        # 不偷当前节点：左右子节点可偷可不偷，取各自最大
        skip_cur = max(left_rob, left_skip) + max(right_rob, right_skip)
        
        return (skip_cur, rob_cur)
    
    skip, rob_root = dp(root)
    return max(skip, rob_root)
```
**时间 O(n)，空间 O(h)**

---

## 3.7 贪心专题

### 题目1：跳跃游戏｜ LeetCode 55

**思路**：维护当前能到达的最远位置，若某点超出最远位置则无法到达。

```python
def canJump(nums: list[int]) -> bool:
    max_reach = 0    # 当前能到达的最远下标
    
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False    # 当前位置无法到达
        
        max_reach = max(max_reach, i + jump)  # 更新最远可达位置
    
    return True
```
**时间 O(n)，空间 O(1)**

---

### 题目2：区间调度最大化｜ LeetCode 435（最少移除区间）

**思路**：贪心。按**结束时间**排序，优先选结束早的区间，最多不重叠区间数 = n - 需删除数。

```python
def eraseOverlapIntervals(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0
    
    # 按结束时间排序（贪心核心）
    intervals.sort(key=lambda x: x[1])
    
    count = 0           # 需要删除的区间数
    end = float('-inf') # 上一个选中区间的结束时间
    
    for start, finish in intervals:
        if start >= end:
            # 不重叠，选择这个区间
            end = finish
        else:
            # 重叠，必须删除一个（删结束时间较晚的，即不选当前）
            count += 1
    
    return count
```
**时间 O(n log n)，空间 O(1)**

---

### 题目3：分发糖果｜ LeetCode 135

**思路**：两次贪心扫描。左→右保证"右比左高则多一颗"；右→左保证"左比右高则多一颗"。

```python
def candy(ratings: list[int]) -> int:
    n = len(ratings)
    candies = [1] * n   # 每人至少1颗
    
    # 从左到右：若右边评分更高，右边糖果 = 左边 + 1
    for i in range(1, n):
        if ratings[i] > ratings[i-1]:
            candies[i] = candies[i-1] + 1
    
    # 从右到左：若左边评分更高，左边糖果取当前值和右边+1的较大值
    for i in range(n-2, -1, -1):
        if ratings[i] > ratings[i+1]:
            candies[i] = max(candies[i], candies[i+1] + 1)
    
    return sum(candies)
```
**时间 O(n)，空间 O(n)**

---

### 题目4：买卖股票的最佳时机 II｜ LeetCode 122

**思路**：贪心。只要明天比今天涨，就今天买明天卖（累积所有上涨收益）。

```python
def maxProfit(prices: list[int]) -> int:
    profit = 0
    
    for i in range(1, len(prices)):
        # 只要有上涨就累积利润（等价于在所有上涨区间都操作）
        if prices[i] > prices[i-1]:
            profit += prices[i] - prices[i-1]
    
    return profit
```
**时间 O(n)，空间 O(1)**

---

## 3.8 BFS 专题

### 题目1：二叉树的层序遍历｜ LeetCode 102

```python
from collections import deque

def levelOrder(root) -> list[list[int]]:
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)    # 当前层的节点数
        level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(level)
    
    return result
```
**时间 O(n)，空间 O(w)，w 为最大宽度**

---

### 题目2：单词接龙｜ LeetCode 127

**思路**：BFS 求最短路（无权图）。每一步改变一个字母，看能否到达目标单词。

```python
from collections import deque

def ladderLength(beginWord: str, endWord: str, wordList: list[str]) -> int:
    word_set = set(wordList)
    if endWord not in word_set:
        return 0
    
    queue = deque([(beginWord, 1)])  # (当前单词, 步数)
    visited = {beginWord}
    
    while queue:
        word, steps = queue.popleft()
        
        # 尝试改变每一个字符位置
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                new_word = word[:i] + c + word[i+1:]
                
                if new_word == endWord:
                    return steps + 1
                
                if new_word in word_set and new_word not in visited:
                    visited.add(new_word)
                    queue.append((new_word, steps + 1))
    
    return 0
```
**时间 O(M² × N)，M=单词长度，N=单词数量**

---

### 题目3：腐烂的橘子（多源 BFS）｜ LeetCode 994

**思路**：多源 BFS，所有烂橘子同时作为起点开始扩散。

```python
from collections import deque

def orangesRotting(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    
    # 初始化：找所有烂橘子和新鲜橘子
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))  # (行, 列, 时间)
            elif grid[r][c] == 1:
                fresh += 1
    
    max_time = 0
    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    
    while queue:
        r, c, time = queue.popleft()
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2        # 标记为腐烂
                fresh -= 1
                max_time = max(max_time, time + 1)
                queue.append((nr, nc, time + 1))
    
    return max_time if fresh == 0 else -1
```
**时间 O(m×n)，空间 O(m×n)**

---

### 题目4：岛屿数量（BFS 版）｜ LeetCode 200

```python
from collections import deque

def numIslands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    count = 0
    
    def bfs(r, c):
        queue = deque([(r, c)])
        grid[r][c] = '0'     # 标记已访问
        
        while queue:
            row, col = queue.popleft()
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                    grid[nr][nc] = '0'   # 标记
                    queue.append((nr, nc))
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                bfs(r, c)        # 扩散整个岛屿
                count += 1
    
    return count
```
**时间 O(m×n)，空间 O(min(m,n))（队列最大大小）**

---

## 3.9 DFS / 回溯专题

### 题目1：全排列｜ LeetCode 46

```python
def permute(nums: list[int]) -> list[list[int]]:
    result = []
    
    def backtrack(path, remaining):
        if not remaining:               # 没有剩余元素，路径完成
            result.append(path[:])      # 必须复制！
            return
        
        for i, num in enumerate(remaining):
            path.append(num)                         # 做选择
            backtrack(path, remaining[:i] + remaining[i+1:])  # 递归
            path.pop()                               # 撤销选择
    
    backtrack([], nums)
    return result
```
**时间 O(n × n!)，空间 O(n)**

---

### 题目2：组合总和｜ LeetCode 39

**思路**：回溯 + 剪枝。元素可重复使用，按序枚举避免重复组合。

```python
def combinationSum(candidates: list[int], target: int) -> list[list[int]]:
    result = []
    candidates.sort()   # 排序后便于剪枝
    
    def backtrack(start, path, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        
        for i in range(start, len(candidates)):
            # 剪枝：当前数已超过剩余目标，后面更大的数也不用尝试
            if candidates[i] > remaining:
                break
            
            path.append(candidates[i])
            # 注意：i 不是 i+1，因为可以重复使用同一元素
            backtrack(i, path, remaining - candidates[i])
            path.pop()
    
    backtrack(0, [], target)
    return result
```

---

### 题目3：N 皇后｜ LeetCode 51

**思路**：逐行放置，DFS + 回溯。用三个集合记录哪些列、哪些斜线已被占用。

```python
def solveNQueens(n: int) -> list[list[str]]:
    result = []
    queens = []          # queens[i] = 第 i 行皇后所在列
    cols = set()         # 已被占用的列
    diag1 = set()        # 已被占用的主对角线（行-列）
    diag2 = set()        # 已被占用的副对角线（行+列）
    
    def backtrack(row):
        if row == n:
            # 所有行都放好了，生成棋盘
            board = []
            for q in queens:
                board.append('.' * q + 'Q' + '.' * (n - q - 1))
            result.append(board)
            return
        
        for col in range(n):
            # 检查当前位置是否冲突
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            
            # 放置皇后
            queens.append(col)
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            
            backtrack(row + 1)
            
            # 撤销
            queens.pop()
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
    
    backtrack(0)
    return result
```
**时间 O(n!)，空间 O(n)**

---

### 题目4：岛屿的最大面积（DFS）｜ LeetCode 695

```python
def maxAreaOfIsland(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    
    def dfs(r, c) -> int:
        # 越界或是水/已访问，返回0
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] == 0:
            return 0
        
        grid[r][c] = 0    # 标记已访问（原地修改）
        
        # 四个方向递归，累计面积
        return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)
    
    max_area = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                max_area = max(max_area, dfs(r, c))
    
    return max_area
```
**时间 O(m×n)，空间 O(m×n) 递归栈**

---

## 3.10 图算法专题

### 题目1：课程表（拓扑排序判环）｜ LeetCode 207

```python
from collections import defaultdict, deque

def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    graph = defaultdict(list)
    in_degree = [0] * numCourses
    
    for course, pre in prerequisites:
        graph[pre].append(course)
        in_degree[course] += 1
    
    # 将所有入度为0的节点加入队列
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    completed = 0
    
    while queue:
        course = queue.popleft()
        completed += 1
        
        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)
    
    # 若所有课程都能完成，则无环
    return completed == numCourses
```

---

### 题目2：网络延迟时间（Dijkstra）｜ LeetCode 743

```python
import heapq
from collections import defaultdict

def networkDelayTime(times: list[list[int]], n: int, k: int) -> int:
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    
    dist = {i: float('inf') for i in range(1, n+1)}
    dist[k] = 0
    heap = [(0, k)]    # (距离, 节点)
    
    while heap:
        d, u = heapq.heappop(heap)
        
        if d > dist[u]:
            continue    # 过时记录
        
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    
    max_dist = max(dist.values())
    return max_dist if max_dist < float('inf') else -1
```

---

### 题目3：冗余连接（并查集）｜ LeetCode 684

**思路**：依次添加边，若两端点已连通（find 返回相同根），此边即为冗余。

```python
def findRedundantConnection(edges: list[list[int]]) -> list[int]:
    n = len(edges)
    parent = list(range(n + 1))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])   # 路径压缩
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False   # 已经连通，添加此边会成环
        parent[px] = py
        return True
    
    for u, v in edges:
        if not union(u, v):
            return [u, v]   # 这条边是冗余的
    
    return []
```

---

### 题目4：被围绕的区域（DFS 染色）｜ LeetCode 130

**思路**：从边界的 'O' 出发 DFS，标记为临时 '#'（不会被围绕），最后翻转剩余 'O' 为 'X'，'#' 恢复为 'O'。

```python
def solve(board: list[list[str]]) -> None:
    if not board:
        return
    
    rows, cols = len(board), len(board[0])
    
    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != 'O':
            return
        board[r][c] = '#'   # 临时标记：与边界相连，不会被翻转
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            dfs(r + dr, c + dc)
    
    # 第一步：从边界出发标记所有安全的 'O'
    for r in range(rows):
        for c in range(cols):
            if (r in (0, rows-1) or c in (0, cols-1)) and board[r][c] == 'O':
                dfs(r, c)
    
    # 第二步：翻转
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 'O':
                board[r][c] = 'X'    # 被围绕，翻转
            elif board[r][c] == '#':
                board[r][c] = 'O'    # 恢复安全区域
```


---

# 第四部分：整体框架结构

---

## 4.1 知识全景图

```
Python 数据结构与算法
│
├── 【数据结构层】─────────────────────────────────────────────
│   │
│   ├── 线性结构
│   │   ├── list          → 动态数组        → 栈 / 滑动窗口 / 前缀和
│   │   ├── tuple         → 静态数组        → 不可变序列 / 复合键
│   │   ├── deque         → 块状双向链表    → 队列 / 单调队列 / BFS
│   │   └── 手写 ListNode → 指针链表        → 链表题 / LRU
│   │
│   ├── 哈希结构
│   │   ├── dict          → 哈希表（有序）  → 映射 / 记忆化 / 图
│   │   ├── set           → 哈希表（无值）  → 去重 / visited
│   │   ├── Counter       → dict 子类       → 频率统计 / 异位词
│   │   └── defaultdict   → dict 子类       → 邻接表 / 分组
│   │
│   ├── 树形结构
│   │   ├── heapq         → 二叉堆（最小）  → TopK / Dijkstra / 优先队列
│   │   └── 手写 TreeNode → 二叉树          → 递归 / 树形 DP
│   │
│   └── 图结构
│       ├── 邻接表         → defaultdict(list) + 边列表
│       └── 并查集         → 数组模拟        → 连通分量 / 环检测
│
├── 【算法思想层】─────────────────────────────────────────────
│   │
│   ├── 双指针            → 对撞 / 快慢 / 同向
│   │   └── 前提：有序或有单调性
│   │
│   ├── 滑动窗口          → 定长 / 变长
│   │   └── 核心：右扩左缩，维护窗口状态
│   │
│   ├── 哈希              → 空间换时间，O(1) 查找
│   │   └── 常配合：前缀和 / 计数
│   │
│   ├── 二分查找          → 有序/单调 → O(log n)
│   │   └── 三种写法：精确 / 左边界 / 右边界 / 答案上二分
│   │
│   ├── 递归与分治        → 大问题 → 同类小问题 → 合并
│   │   └── 代表：归并排序 / 快速幂 / 树遍历
│   │
│   ├── 动态规划          → 重叠子问题 + 最优子结构
│   │   ├── 线性 DP / 背包 DP / 区间 DP
│   │   └── 树形 DP / 序列 DP / 状态压缩 DP
│   │
│   ├── 贪心              → 局部最优 → 全局最优
│   │   └── 需证明正确性（交换论证）
│   │
│   ├── BFS               → 队列 + visited → 最短路（无权）
│   │   └── 多源 BFS / 双向 BFS
│   │
│   ├── DFS / 回溯        → 栈/递归 + 路径记录 + 撤销
│   │   └── 剪枝：去重 / 可行性 / 路径长度
│   │
│   └── 图算法
│       ├── 拓扑排序（Kahn / DFS）
│       ├── 最短路（Dijkstra / Bellman-Ford / Floyd）
│       ├── 最小生成树（Kruskal / Prim）
│       └── 并查集（路径压缩 + 按秩合并）
│
└── 【应用场景层】─────────────────────────────────────────────
    │
    ├── 查找类     → 二分 / 哈希 / BFS
    ├── 排序类     → 归并 / 快速 / 堆排序 / Timsort
    ├── 路径类     → BFS（最短）/ DFS（所有路径）/ Dijkstra（带权）
    ├── 最优化类   → DP / 贪心
    ├── 枚举类     → 回溯 + 剪枝
    ├── 连通性     → BFS / DFS / 并查集
    └── 调度类     → 堆（优先队列）/ 拓扑排序
```

---

## 4.2 算法选择决策树

```
面对一道题，按以下流程思考：

                    ┌─ 是否涉及数组/字符串的连续子段？
                    │   ├─ 是 → 滑动窗口 / 前缀和
                    │   └─ 否 ↓
                    │
                    ├─ 是否需要最优解（最大/最小/最多）？
                    │   ├─ 有重叠子问题 → 动态规划
                    │   ├─ 贪心可证明 → 贪心
                    │   └─ 否 ↓
                    │
                    ├─ 是否需要遍历所有可能（排列/组合/路径）？
                    │   └─ 是 → DFS + 回溯 + 剪枝
                    │
                    ├─ 是否是图/树的连通/路径问题？
                    │   ├─ 最短路（无权）→ BFS
                    │   ├─ 最短路（有权）→ Dijkstra
                    │   ├─ 连通分量/环  → 并查集 / DFS
                    │   └─ 依赖顺序    → 拓扑排序
                    │
                    ├─ 是否是有序数组的查找问题？
                    │   └─ 是 → 二分查找
                    │
                    ├─ 是否需要快速查找/去重/频率？
                    │   └─ 是 → 哈希表（dict / set / Counter）
                    │
                    └─ 是否有两个指针可以协同优化？
                        └─ 是 → 双指针
```

---

## 4.3 时间复杂度速查表

| 复杂度 | 名称 | 代表算法 | n=10⁶ 时约 |
|--------|------|---------|-----------|
| O(1) | 常数 | 哈希表操作 | 瞬时 |
| O(log n) | 对数 | 二分查找、堆操作 | ~20 次 |
| O(n) | 线性 | 线性扫描、BFS/DFS | 10⁶ 次 |
| O(n log n) | 线性对数 | 排序、归并 | ~2×10⁷ |
| O(n²) | 平方 | 暴力双循环 | 10¹² ⚠️ |
| O(n³) | 立方 | Floyd、区间 DP | 10¹⁸ ❌ |
| O(2ⁿ) | 指数 | 子集枚举、暴力回溯 | 极大 ❌ |
| O(n!) | 阶乘 | 全排列暴力 | 极大 ❌ |

> 面试中，n ≤ 10⁵ 基本要求 O(n log n) 以内；n ≤ 10³ 可接受 O(n²)

---

## 4.4 常见数据结构操作复杂度汇总

| 结构 | 查找 | 插入 | 删除 | 有序 | 备注 |
|------|------|------|------|------|------|
| list | O(n) | O(1)末尾/O(n)中间 | O(n) | 可以 | 随机访问O(1) |
| dict | O(1) | O(1) | O(1) | 插入序 | 哈希 |
| set | O(1) | O(1) | O(1) | 否 | 哈希 |
| deque | O(n) | O(1)两端 | O(1)两端 | 否 | 双端队列 |
| heapq | O(1)堆顶 | O(log n) | O(log n) | 堆序 | 最小堆 |
| 链表 | O(n) | O(1)已知位置 | O(1)已知位置 | 否 | |
| 二叉搜索树 | O(log n) | O(log n) | O(log n) | 是 | 平衡时 |

---

## 4.5 30 天备战学习路线

```
Week 1：基础打牢
  Day 1-2   数据结构原理（本文第一部分）
  Day 3-4   双指针 + 滑动窗口（10题）
  Day 5-6   哈希表（10题）
  Day 7     二分查找（8题）

Week 2：核心算法
  Day 8-9   递归 + 分治（树相关题）
  Day 10-11 BFS + DFS 基础（图遍历、岛屿）
  Day 12-13 回溯（排列、组合、子集）
  Day 14    综合复习 + 错题整理

Week 3：进阶突破
  Day 15-16 动态规划 基础（线性DP、背包）
  Day 17-18 动态规划 进阶（序列DP、区间DP）
  Day 19-20 贪心（区间调度、跳跃游戏）
  Day 21    图算法（Dijkstra、拓扑排序、并查集）

Week 4：冲刺模拟
  Day 22-24 LeetCode 热题 100 查漏补缺
  Day 25-26 模拟面试（限时做题 + 讲解思路）
  Day 27-28 Python 语言特性巩固（生成器/装饰器/并发）
  Day 29    测试框架（pytest 测试数据结构实现）
  Day 30    全面复盘 + 知识图谱再梳理
```

---

## 4.6 面试解题话术框架

```
1. 理解题目（1-2 min）
   "这道题要求我在...条件下找到...，输入是...，输出是..."
   → 确认输入范围、边界条件（空数组、重复元素、负数）

2. 分析思路（2-3 min）
   "暴力解法是...，时间复杂度 O(...)，可以用...优化到 O(...)"
   → 说出至少两种思路，再选最优

3. 编写代码（10-15 min）
   → 先写主干，再处理边界
   → 变量命名清晰，适当注释

4. 测试验证（2-3 min）
   → 正常用例、边界用例（空/单元素/极大值）
   → 如有时间，分析时间/空间复杂度

5. 可能的优化（加分项）
   "如果空间有限制，可以...；如果需要并发，可以..."
```

---

## 4.7 Python 刷题常用技巧速查

```python
# ============ 初始化 ============
INF = float('inf')
from collections import defaultdict, deque, Counter
from functools import lru_cache
import heapq, bisect, itertools

# ============ 二维数组 ============
grid = [[0]*cols for _ in range(rows)]   # ✅ 正确
grid = [[0]*cols] * rows                  # ❌ 浅拷贝陷阱

# ============ 四个方向 ============
dirs = [(0,1),(0,-1),(1,0),(-1,0)]

# ============ 记忆化递归 ============
@lru_cache(maxsize=None)
def dp(i, j):
    ...

# ============ 堆（最大堆技巧）============
heapq.heappush(h, (-val, val))   # 负数模拟最大堆

# ============ 二分 ============
import bisect
bisect.bisect_left(arr, x)    # 左边界（第一个 >= x）
bisect.bisect_right(arr, x)   # 右边界（第一个 > x）
bisect.insort(arr, x)         # 插入保持有序

# ============ 字符处理 ============
ord('a')           # 97
chr(97)            # 'a'
ord(c) - ord('a')  # 字母转 0-25 的索引

# ============ 列表操作 ============
sorted(lst, key=lambda x: x[1])   # 按第二元素排序
lst.sort(reverse=True)             # 降序
zip(a, b)                          # 并行遍历
enumerate(lst)                     # 带下标遍历
any() / all()                      # 任一/全部

# ============ 字符串 ============
s.split()          # 按空白分割
' '.join(lst)      # 列表转字符串
s[::-1]            # 反转字符串
s.count('a')       # 计数

# ============ 数学 ============
import math
math.ceil(x)       # 向上取整
math.floor(x)      # 向下取整
math.gcd(a, b)     # 最大公约数
math.inf           # 无穷大
```

---

*文档版本：v1.0 | 覆盖算法：10类 | 面试题：40题 | 适用：测试开发 / Python 后端工程师面试备战*
