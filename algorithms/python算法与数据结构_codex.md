# Python 数据结构与算法结构化知识图谱

> 目标：面向 Python 面试准备，系统整理数据结构、算法思想、典型题型与代码模板。  
> 使用方式：先看整体框架，再看“工具映射表”，之后按“数据结构 -> 算法思想 -> 典型题”逐步学习。

---

## 1. 整体框架结构

```text
Python 数据结构与算法
├─ 1. 基础认知
│  ├─ 时间复杂度
│  ├─ 空间复杂度
│  ├─ 常见输入规模与算法选择
│  └─ Python 常用模块
├─ 2. 数据结构
│  ├─ list：动态数组
│  ├─ dict / set：哈希表
│  ├─ deque：双端队列
│  ├─ linked list：链表
│  ├─ heap：堆
│  ├─ tree：树
│  └─ graph：图
├─ 3. 核心算法思想
│  ├─ 双指针
│  ├─ 滑动窗口
│  ├─ 哈希
│  ├─ 二分查找
│  ├─ 递归与分治
│  ├─ 动态规划
│  ├─ 贪心
│  ├─ BFS
│  ├─ DFS
│  └─ 图算法
├─ 4. 高频专题
│  ├─ 子数组 / 子串
│  ├─ TopK
│  ├─ 路径搜索
│  ├─ 连通性
│  ├─ 最短路
│  └─ 依赖关系 / 拓扑排序
└─ 5. 刷题方法论
   ├─ 识别题型
   ├─ 暴力转优化
   ├─ 模板沉淀
   └─ 错题复盘
```

---

## 2. 核心工具与概念映射表

| 问题特征 | 优先想到 | Python 工具 |
|---|---|---|
| 判重、频率统计、映射 | 哈希 | `dict` `set` `Counter` |
| 连续子串、连续子数组 | 滑动窗口 | 双指针 + `dict/set` |
| 有序数组、找边界 | 二分查找 | 手写二分 / `bisect` |
| 从两端逼近、原地覆盖 | 双指针 | 下标访问 |
| 层级扩展、最短步数 | BFS | `collections.deque` |
| 全路径、所有可能性 | DFS / 回溯 | 递归 |
| TopK、优先级弹出 | 堆 | `heapq` |
| 最优子结构、重复子问题 | 动态规划 | `list` / 二维数组 |
| 局部最优可推全局最优 | 贪心 | 排序 / 堆 |
| 依赖关系、入度、是否有环 | 图算法 | 邻接表 + `deque` |

---

## 3. Python 数据结构

### 3.1 `list`

#### 定义与底层实现原理
- `list` 本质上是动态数组。
- 底层是连续内存空间。
- 好处是随机访问很快，因为可以通过下标直接定位。
- 缺点是中间插入、头部删除时，需要整体搬移元素。

#### Python 中的实现方式
- 内置类型，无需额外导入。

#### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 按下标访问 | `nums[i]` | `O(1)` |
| 尾部追加 | `append(x)` | 均摊 `O(1)` |
| 尾部删除 | `pop()` | `O(1)` |
| 头部删除 | `pop(0)` | `O(n)` |
| 中间插入 | `insert(i, x)` | `O(n)` |
| 查找元素 | `x in nums` | `O(n)` |
| 排序 | `sort()` | `O(nlogn)` |

#### 典型应用场景
- 数组题
- 双指针
- 动态规划数组
- 模拟栈

---

### 3.2 `dict`

#### 定义与底层实现原理
- `dict` 是哈希表。
- 通过 key 的哈希值定位存储位置。
- 平均情况下插入、查询、删除都很快。

#### Python 中的实现方式
- 内置类型，无需额外导入。

#### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 查询 | `d[k]` / `get(k)` | 平均 `O(1)` |
| 插入/修改 | `d[k] = v` | 平均 `O(1)` |
| 删除 | `del d[k]` | 平均 `O(1)` |
| 判存在 | `k in d` | 平均 `O(1)` |
| 遍历 | `for k, v in d.items()` | `O(n)` |

#### 典型应用场景
- 频率统计
- 两数之和
- 前缀和计数
- 索引映射

---

### 3.3 `set`

#### 定义与底层实现原理
- `set` 也是哈希表结构，但只保存 key，不保存 value。
- 最大用途是判重和去重。

#### Python 中的实现方式
- 内置类型，无需额外导入。

#### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 添加 | `add(x)` | 平均 `O(1)` |
| 删除 | `remove(x)` / `discard(x)` | 平均 `O(1)` |
| 判存在 | `x in s` | 平均 `O(1)` |

#### 典型应用场景
- 无重复字符子串
- 是否访问过某节点
- 数组去重

---

### 3.4 `deque`

#### 定义与底层实现原理
- `deque` 是双端队列。
- 它适合在头尾两端做插入和删除。
- 比 `list.pop(0)` 更高效。

#### Python 中的实现方式
- 需要导入：`from collections import deque`

#### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 尾部入队 | `append(x)` | `O(1)` |
| 头部入队 | `appendleft(x)` | `O(1)` |
| 尾部出队 | `pop()` | `O(1)` |
| 头部出队 | `popleft()` | `O(1)` |

#### 典型应用场景
- BFS
- 单调队列
- 滑动窗口最大值

---

### 3.5 链表

#### 定义与底层实现原理
- 链表由一个个节点连接而成。
- 每个节点通常保存两个信息：
  - 当前值
  - 下一个节点指针
- 它不要求连续内存。
- 插入删除灵活，但按位置访问慢。

#### Python 中的实现方式
- Python 没有内置面试用链表，一般手写 `ListNode`。

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

#### 典型应用场景
- 反转链表
- 快慢指针
- 合并有序链表

---

### 3.6 堆

#### 定义与底层实现原理
- 堆是用数组实现的完全二叉树。
- Python 的 `heapq` 默认是最小堆。
- 堆顶始终是当前最小值。

#### Python 中的实现方式
- 需要导入：`import heapq`

#### 常用方法与时间复杂度

| 功能 | 方法 | 复杂度 |
|---|---|---|
| 建堆 | `heapify(nums)` | `O(n)` |
| 插入 | `heappush(heap, x)` | `O(logn)` |
| 弹出最小值 | `heappop(heap)` | `O(logn)` |

#### 典型应用场景
- TopK
- 优先队列
- Dijkstra

---

### 3.7 树

#### 定义与底层实现原理
- 树是一种层级结构。
- 二叉树中每个节点最多两个孩子。
- 面试里常见的是：
  - 普通二叉树
  - 二叉搜索树 BST
  - 堆

#### Python 中的实现方式
- 一般手写 `TreeNode`。

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

#### 典型应用场景
- 前中后序遍历
- DFS / BFS
- 路径和
- 最近公共祖先

---

### 3.8 图

#### 定义与底层实现原理
- 图由顶点和边组成。
- 与树不同，图可以有环。
- 可分为有向图、无向图、带权图。

#### Python 中的实现方式
- 常用邻接表表示：

```python
from collections import defaultdict

graph = defaultdict(list)
graph[1].append(2)
graph[1].append(3)
```

#### 典型应用场景
- 连通块
- 拓扑排序
- 最短路径
- 环检测

---

## 4. Python 算法思想

---

## 4.1 双指针

### 核心思想
- 双指针本质上是用两个位置变量配合移动，减少重复遍历。
- 它适合解决“两个位置互相影响”的问题。
- 典型形式有两类：
  - 左右指针：从数组两端往中间收缩
  - 快慢指针：一个负责扫描，一个负责记录结果位置

### 什么时候想到双指针
- 数组已经有序
- 需要原地修改数组
- 需要从两端逼近答案
- 需要维护一个有效区间

### 解题步骤
1. 明确两个指针分别代表什么。
2. 想清楚什么时候移动左指针，什么时候移动右指针。
3. 确保每一步移动都有依据，不要“凭感觉移动”。
4. 注意边界，例如空数组、单元素数组。

### 典型面试题 1：移动零

#### 思路讲解
- 题目要求把所有 `0` 移到数组末尾，同时保持非零元素相对顺序不变。
- 这说明我们不能简单排序，因为排序会打乱原顺序。
- 最自然的办法是用两个指针：
  - `fast`：从左到右扫描整个数组，寻找非零元素
  - `slow`：指向“下一个非零元素应该放的位置”
- 当 `fast` 指向非零元素时，把它交换到 `slow` 位置，然后 `slow += 1`。
- 这样一轮扫描后，前面就都是按原顺序排列好的非零元素，后面自然是零。

```python
def moveZeroes(nums):
    # slow 表示下一个非零元素应该放置的位置
    slow = 0

    # fast 负责遍历整个数组
    for fast in range(len(nums)):
        # 只处理非零元素
        if nums[fast] != 0:
            # 将当前非零元素交换到 slow 位置
            nums[slow], nums[fast] = nums[fast], nums[slow]
            # slow 向后移动，准备放下一个非零元素
            slow += 1
```

### 典型面试题 2：验证回文串

#### 思路讲解
- 回文串是左右对称的。
- 所以最直接的判断方式就是左右两个指针向中间靠拢。
- 但题目通常会要求忽略大小写和非字母数字字符。
- 因此先做预处理，保留有效字符并统一转小写。
- 然后用 `left` 和 `right` 比较。
- 任何一组不相等，就立刻返回 `False`。

```python
def isPalindrome(s):
    # 预处理：只保留字母和数字，并统一转成小写
    filtered = ''.join(ch.lower() for ch in s if ch.isalnum())

    # 左右指针分别从头尾开始
    left, right = 0, len(filtered) - 1

    while left < right:
        # 只要有一对字符不相等，就不是回文
        if filtered[left] != filtered[right]:
            return False

        # 两个指针向中间收缩
        left += 1
        right -= 1

    # 所有位置都对称相等，说明是回文
    return True
```

### 典型面试题 3：两数之和 II（有序数组）

#### 思路讲解
- 题目给的是有序数组，这是关键信号。
- 若当前两数之和太小，就需要增大总和，所以左指针右移。
- 若当前两数之和太大，就需要减小总和，所以右指针左移。
- 因为数组有序，这样移动一定不会错过答案。

```python
def twoSum(numbers, target):
    # 左右指针分别指向数组两端
    left, right = 0, len(numbers) - 1

    while left < right:
        # 计算当前两个数的和
        current_sum = numbers[left] + numbers[right]

        if current_sum == target:
            # 题目一般要求返回 1-based 下标
            return [left + 1, right + 1]
        elif current_sum < target:
            # 和偏小，需要更大的数，所以左指针右移
            left += 1
        else:
            # 和偏大，需要更小的数，所以右指针左移
            right -= 1
```

### 典型面试题 4：盛最多水的容器

#### 思路讲解
- 面积由两部分决定：
  - 宽度：`right - left`
  - 高度：两边短板的高度
- 也就是：`面积 = min(height[left], height[right]) * (right - left)`
- 如果想让面积变大，移动高板没意义，因为短板仍然限制高度。
- 所以每次应移动更短的那一边，才有机会找到更高的短板。

```python
def maxArea(height):
    # 左右指针从两端开始
    left, right = 0, len(height) - 1
    ans = 0

    while left < right:
        # 当前容器面积由短板决定
        current_area = min(height[left], height[right]) * (right - left)
        ans = max(ans, current_area)

        # 移动短板，才有可能得到更大的面积
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return ans
```

### 典型面试题 5：删除排序数组中的重复项

#### 思路讲解
- 数组已经有序，所以重复元素一定挨在一起。
- 我们可以让：
  - `fast` 负责遍历数组
  - `slow` 负责记录“去重后下一个元素该放在哪里”
- 当 `fast` 遇到一个和前一个不同的新元素时，就把它写到 `slow` 位置。
- 最终 `slow` 的值就是去重后的长度。

```python
def removeDuplicates(nums):
    # 空数组直接返回 0
    if not nums:
        return 0

    # slow 指向去重后下一个可写入位置
    slow = 1

    # fast 从第二个元素开始扫描
    for fast in range(1, len(nums)):
        # 当前元素和前一个不同，说明是新元素
        if nums[fast] != nums[fast - 1]:
            nums[slow] = nums[fast]
            slow += 1

    # slow 就是去重后的数组长度
    return slow
```

---

## 4.2 滑动窗口

### 核心思想
- 滑动窗口本质上是在数组或字符串上维护一个连续区间。
- 这个区间通过 `left` 和 `right` 两个指针表示。
- `right` 负责扩大窗口，`left` 负责缩小窗口。
- 目标通常是：
  - 找满足条件的最长区间
  - 找满足条件的最短区间
  - 统计满足条件的区间数量

### 什么时候想到滑动窗口
- 题目中出现“连续子串”“连续子数组”
- 求最长、最短、个数
- 问题与一个连续区间有关

### 解题步骤
1. 明确窗口内要维护什么信息。
2. 先扩张右边界，把新元素纳入窗口。
3. 如果窗口不合法，就收缩左边界。
4. 在合适时机更新答案。

### 典型面试题 1：无重复字符的最长子串

#### 思路讲解
- 我们希望窗口内始终没有重复字符。
- 使用一个 `set` 保存窗口中的字符。
- 每次加入新字符时：
  - 若不重复，直接加入
  - 若重复，就不断移动左指针并删除旧字符，直到重复消失
- 每轮都可以更新当前窗口长度。

```python
def lengthOfLongestSubstring(s):
    # 用集合维护当前窗口中出现过的字符
    seen = set()
    left = 0
    ans = 0

    # right 逐步向右扩张窗口
    for right, ch in enumerate(s):
        # 如果新字符重复，就不断缩小左边界
        while ch in seen:
            seen.remove(s[left])  # 移除左端字符
            left += 1             # 左边界右移

        # 把当前字符加入窗口
        seen.add(ch)

        # 更新最大长度
        ans = max(ans, right - left + 1)

    return ans
```

### 典型面试题 2：长度最小的子数组

#### 思路讲解
- 题目要求找和至少为 `target` 的最短连续子数组。
- 用一个窗口维护当前区间和。
- 当区间和还不够时，继续向右扩张。
- 一旦区间和达到要求，就尽可能缩小左边界，看能不能得到更短区间。

```python
def minSubArrayLen(target, nums):
    left = 0
    current_sum = 0
    ans = float('inf')

    for right, num in enumerate(nums):
        # 扩张窗口：把右边新元素加入当前和
        current_sum += num

        # 当窗口和已经满足要求时，尝试收缩左边界
        while current_sum >= target:
            ans = min(ans, right - left + 1)
            current_sum -= nums[left]
            left += 1

    return 0 if ans == float('inf') else ans
```

### 典型面试题 3：找到字符串中所有字母异位词

#### 思路讲解
- 异位词的本质：字符频次完全相同。
- 因为目标串 `p` 长度固定，所以窗口长度也固定为 `len(p)`。
- 用两个计数器：
  - `need`：目标串频次
  - `window`：当前窗口频次
- 窗口长度超过 `len(p)` 时，就把左边字符移出去。

```python
from collections import Counter


def findAnagrams(s, p):
    # need 记录目标串每个字符的频次
    need = Counter(p)
    # window 记录当前窗口的字符频次
    window = Counter()

    left = 0
    ans = []

    for right, ch in enumerate(s):
        # 将右端字符纳入窗口
        window[ch] += 1

        # 保证窗口长度不超过 len(p)
        if right - left + 1 > len(p):
            left_char = s[left]
            window[left_char] -= 1
            if window[left_char] == 0:
                del window[left_char]
            left += 1

        # 若频次完全相同，则当前 left 是一个答案
        if window == need:
            ans.append(left)

    return ans
```

### 典型面试题 4：最小覆盖子串

#### 思路讲解
- 我们要找到最短的窗口，使得它“覆盖”目标串 `t` 的所有字符及频次。
- 这是典型的“先扩张让窗口合法，再收缩让窗口尽可能短”。
- 用：
  - `need` 记录需求
  - `window` 记录当前窗口
  - `formed` 记录当前已经满足了多少种字符要求
- 当 `formed == required` 时，说明窗口已经合法，可以尝试收缩。

```python
from collections import Counter


def minWindow(s, t):
    need = Counter(t)
    window = Counter()

    required = len(need)  # 需要满足的字符种类数
    formed = 0            # 当前已经满足要求的字符种类数

    left = 0
    start = 0
    min_len = float('inf')

    for right, ch in enumerate(s):
        # 扩张右边界，把字符加入窗口
        window[ch] += 1

        # 若某个字符频次刚好满足需求，则 formed + 1
        if ch in need and window[ch] == need[ch]:
            formed += 1

        # 当窗口已经覆盖 t 时，尝试缩小窗口
        while formed == required:
            # 更新最优答案
            if right - left + 1 < min_len:
                min_len = right - left + 1
                start = left

            # 准备移除左端字符
            left_char = s[left]
            window[left_char] -= 1

            # 如果移除后不再满足需求，则窗口变得不合法
            if left_char in need and window[left_char] < need[left_char]:
                formed -= 1

            left += 1

    return "" if min_len == float('inf') else s[start:start + min_len]
```

### 典型面试题 5：滑动窗口最大值

#### 思路讲解
- 题目要求每个长度为 `k` 的窗口中的最大值。
- 如果每次都扫描窗口找最大值，会超时。
- 更优方法是用“单调队列”：
  - 队列中存下标
  - 队列对应值保持从大到小
- 这样队头永远是当前窗口最大值下标。

```python
from collections import deque


def maxSlidingWindow(nums, k):
    # q 存的是下标，且对应值保持单调递减
    q = deque()
    ans = []

    for i, num in enumerate(nums):
        # 维护单调性：把队尾所有比当前值小的元素弹出
        while q and nums[q[-1]] <= num:
            q.pop()

        # 当前下标入队
        q.append(i)

        # 如果队头已经滑出窗口范围，则移除
        if q[0] <= i - k:
            q.popleft()

        # 当窗口形成后，队头就是当前窗口最大值
        if i >= k - 1:
            ans.append(nums[q[0]])

    return ans
```

---

## 4.3 哈希

### 核心思想
- 哈希的本质是“用空间换时间”。
- 通过建立映射，把原本需要线性查找的问题，优化成平均 `O(1)` 查找。

### 什么时候想到哈希
- 判重
- 频率统计
- 两数配对
- 前缀和计数

### 解题步骤
1. 先思考“我要查什么信息”。
2. 决定 key 是什么，value 存什么。
3. 尝试用哈希表把重复查找优化掉。

### 典型面试题 1：两数之和

#### 思路讲解
- 对每个元素 `x`，我们都想知道是否存在另一个数 `target - x`。
- 如果先把之前见过的数字存到哈希表里，就能在 `O(1)` 时间查到。
- 遍历到当前元素时：
  - 先查补数是否存在
  - 再把当前数加入哈希表

```python
def twoSum(nums, target):
    # 哈希表：key 是数值，value 是下标
    index_map = {}

    for i, num in enumerate(nums):
        complement = target - num

        # 如果补数已经出现过，直接返回答案
        if complement in index_map:
            return [index_map[complement], i]

        # 记录当前数字和下标
        index_map[num] = i
```

### 典型面试题 2：有效的字母异位词

#### 思路讲解
- 两个字符串互为异位词，说明每个字符出现次数完全一样。
- 所以直接统计频次，然后比较是否相等即可。

```python
from collections import Counter


def isAnagram(s, t):
    # Counter 会统计每个字符的出现次数
    return Counter(s) == Counter(t)
```

### 典型面试题 3：最长连续序列

#### 思路讲解
- 如果对每个数都往前往后扩展，会重复很多次。
- 优化关键是：只从“连续序列的起点”开始扩展。
- 若 `x - 1` 不在集合中，说明 `x` 是起点。
- 从起点一路往后找 `x + 1, x + 2 ...` 即可。

```python
def longestConsecutive(nums):
    # 用集合支持 O(1) 判存在
    num_set = set(nums)
    ans = 0

    for num in num_set:
        # 只有当前一个数不存在时，才把它当作序列起点
        if num - 1 not in num_set:
            current = num
            length = 1

            # 不断向后扩展连续序列
            while current + 1 in num_set:
                current += 1
                length += 1

            ans = max(ans, length)

    return ans
```

### 典型面试题 4：和为 K 的子数组

#### 思路讲解
- 子数组和问题常常想到前缀和。
- 若 `prefix[j] - prefix[i] = k`
- 则说明从 `i+1` 到 `j` 的子数组和为 `k`。
- 换句话说，遍历到当前前缀和 `prefix` 时，只要之前出现过 `prefix - k`，就能形成答案。
- 因此我们用哈希表统计“某个前缀和出现过多少次”。

```python
def subarraySum(nums, k):
    # prefix_count[p] 表示前缀和 p 出现过多少次
    prefix_count = {0: 1}

    prefix_sum = 0
    ans = 0

    for num in nums:
        # 更新当前前缀和
        prefix_sum += num

        # 若之前出现过 prefix_sum - k，则这些位置都能组成合法子数组
        ans += prefix_count.get(prefix_sum - k, 0)

        # 记录当前前缀和出现次数
        prefix_count[prefix_sum] = prefix_count.get(prefix_sum, 0) + 1

    return ans
```

### 典型面试题 5：字母异位词分组

#### 思路讲解
- 互为异位词的字符串，排序后一定相同。
- 所以可以把“排序后的字符序列”当作分组 key。
- 每遍历一个字符串，就放到对应的桶里。

```python
from collections import defaultdict


def groupAnagrams(strs):
    # key 是排序后的字符序列，value 是原字符串列表
    groups = defaultdict(list)

    for s in strs:
        # 排序后转换成元组，便于作为哈希表 key
        key = tuple(sorted(s))
        groups[key].append(s)

    return list(groups.values())
```

---

## 4.4 二分查找

### 核心思想
- 二分查找利用“单调性”不断缩小搜索范围。
- 每次比较中间位置，然后排除一半不可能区域。

### 什么时候想到二分
- 数组有序
- 找第一个满足条件的位置
- 找最后一个满足条件的位置
- 题目答案具有单调性

### 解题步骤
1. 明确搜索区间。
2. 明确中间点满足条件时，应该往左缩还是往右缩。
3. 想清楚要找的是“某个值”还是“边界”。

### 典型面试题 1：二分查找

#### 思路讲解
- 在有序数组中找目标值。
- 中间值比目标小，说明目标一定在右边。
- 中间值比目标大，说明目标一定在左边。

```python
def search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
```

### 典型面试题 2：搜索插入位置

#### 思路讲解
- 如果找不到目标值，也要返回它应该插入的位置。
- 实际上就是找“第一个大于等于 target 的位置”。

```python
def searchInsert(nums, target):
    left, right = 0, len(nums) - 1
    ans = len(nums)

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] >= target:
            ans = mid
            right = mid - 1
        else:
            left = mid + 1

    return ans
```

### 典型面试题 3：在排序数组中查找元素的第一个和最后一个位置

#### 思路讲解
- 这题本质不是找一个值，而是找边界。
- 可以写一个通用函数 `lower_bound(x)`：
  - 返回第一个大于等于 `x` 的位置
- 那么：
  - 左边界 = `lower_bound(target)`
  - 右边界 = `lower_bound(target + 1) - 1`

```python
def searchRange(nums, target):
    def lower_bound(x):
        left, right = 0, len(nums) - 1
        ans = len(nums)

        while left <= right:
            mid = (left + right) // 2

            if nums[mid] >= x:
                ans = mid
                right = mid - 1
            else:
                left = mid + 1

        return ans

    left_index = lower_bound(target)
    right_index = lower_bound(target + 1) - 1

    if left_index < len(nums) and nums[left_index] == target:
        return [left_index, right_index]

    return [-1, -1]
```

### 典型面试题 4：x 的平方根

#### 思路讲解
- 不是在数组中二分，而是在“答案范围”上二分。
- 我们要找最大的 `mid`，满足 `mid * mid <= x`。
- 这类题叫“答案二分”。

```python
def mySqrt(x):
    left, right = 0, x
    ans = 0

    while left <= right:
        mid = (left + right) // 2

        if mid * mid <= x:
            ans = mid      # mid 合法，先记录
            left = mid + 1 # 尝试找更大的合法值
        else:
            right = mid - 1

    return ans
```

### 典型面试题 5：搜索旋转排序数组

#### 思路讲解
- 虽然数组被旋转，但每次总有一半是有序的。
- 判断 `nums[left] <= nums[mid]`，若成立，左半边有序。
- 再看目标值是否落在这段有序区间内。
- 如果在，就去这边找；否则去另一边。

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            return mid

        # 如果左半边有序
        if nums[left] <= nums[mid]:
            # 判断目标是否在左半边有序区间中
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # 否则右半边有序
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1
```

---

## 4.5 递归与分治

### 核心思想
- 递归：函数调用自身去解决更小规模的同类问题。
- 分治：把一个大问题拆成若干小问题，分别解决后再合并。

### 什么时候想到递归与分治
- 树结构
- 归并排序、快速幂
- 问题天然可以拆成左右两半

### 写递归时要先想清楚的 3 个问题
1. 函数定义是什么。
2. 递归终止条件是什么。
3. 当前问题如何依赖子问题结果。

### 典型面试题 1：二叉树的最大深度

#### 思路讲解
- 一棵树的最大深度，等于：
  - 左子树最大深度
  - 右子树最大深度
  - 取较大值后再加 1
- 所以它天然适合递归。

```python
def maxDepth(root):
    # 空树深度为 0
    if not root:
        return 0

    # 当前树深度 = 1 + 左右子树最大深度
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```

### 典型面试题 2：翻转二叉树

#### 思路讲解
- 翻转的本质是把每个节点的左右孩子交换。
- 只要递归处理每个节点即可。

```python
def invertTree(root):
    # 空节点直接返回
    if not root:
        return None

    # 递归翻转左右子树，并交换位置
    root.left, root.right = invertTree(root.right), invertTree(root.left)

    return root
```

### 典型面试题 3：合并两个有序链表

#### 思路讲解
- 两个链表头部较小的那个，一定是新链表的当前头节点。
- 然后递归地把“较小节点的 next”和另一个链表继续合并即可。

```python
def mergeTwoLists(list1, list2):
    # 任意一个为空，直接返回另一个
    if not list1:
        return list2
    if not list2:
        return list1

    # 谁小谁作为当前头节点
    if list1.val < list2.val:
        list1.next = mergeTwoLists(list1.next, list2)
        return list1
    else:
        list2.next = mergeTwoLists(list1, list2.next)
        return list2
```

### 典型面试题 4：排序数组（归并排序）

#### 思路讲解
- 把数组不断拆成左右两半，直到只剩一个元素。
- 单个元素天然有序。
- 然后把两个有序数组合并起来。
- 这就是经典分治。

```python
def sortArray(nums):
    # 递归终止：长度为 0 或 1 时已有序
    if len(nums) <= 1:
        return nums

    mid = len(nums) // 2

    # 分治：分别排序左右两半
    left = sortArray(nums[:mid])
    right = sortArray(nums[mid:])

    # 合并两个有序数组
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # 把剩余元素拼接到结果后面
    result.extend(left[i:])
    result.extend(right[j:])

    return result
```

### 典型面试题 5：Pow(x, n)

#### 思路讲解
- 直接计算 `x * x * x ...` 会重复很多次。
- 更优方法是：
  - 先算 `x^(n//2)`
  - 再平方
- 若 `n` 为奇数，再额外乘一个 `x`。
- 这就是快速幂，属于分治。

```python
def myPow(x, n):
    # 任何数的 0 次方都是 1
    if n == 0:
        return 1

    # 处理负指数
    if n < 0:
        return 1 / myPow(x, -n)

    # 先求一半的结果
    half = myPow(x, n // 2)

    # 如果 n 是偶数，结果就是 half * half
    if n % 2 == 0:
        return half * half

    # 如果 n 是奇数，还要再乘一个 x
    return half * half * x
```

---

## 4.6 动态规划

### 核心思想
- 动态规划用于解决“重复子问题 + 最优子结构”问题。
- 它的核心不是背公式，而是定义状态。

### 什么时候想到动态规划
- 求最大值、最小值
- 求方案数
- 判断能不能做到
- 当前位置依赖之前的结果

### 动态规划四问
1. `dp[i]` 或 `dp[i][j]` 表示什么。
2. 状态转移方程是什么。
3. 初始条件是什么。
4. 遍历顺序是什么。

### 典型面试题 1：爬楼梯

#### 思路讲解
- 到达第 `n` 阶，只可能来自：
  - 第 `n-1` 阶走 1 步
  - 第 `n-2` 阶走 2 步
- 所以状态转移是：
  - `dp[n] = dp[n-1] + dp[n-2]`

```python
def climbStairs(n):
    # 前两项单独处理
    if n <= 2:
        return n

    # a 表示 dp[i-2]，b 表示 dp[i-1]
    a, b = 1, 2

    for _ in range(3, n + 1):
        a, b = b, a + b

    return b
```

### 典型面试题 2：打家劫舍

#### 思路讲解
- 对于第 `i` 间房，有两种选择：
  - 不偷它：收益是前一间的最优解
  - 偷它：收益是前两间最优解 + 当前金额
- 所以：
  - `dp[i] = max(dp[i-1], dp[i-2] + nums[i])`

```python
def rob(nums):
    # prev2 表示 dp[i-2]
    # prev1 表示 dp[i-1]
    prev2, prev1 = 0, 0

    for num in nums:
        # 新状态来自“不偷当前房子”和“偷当前房子”两者较大值
        prev2, prev1 = prev1, max(prev1, prev2 + num)

    return prev1
```

### 典型面试题 3：最大子数组和

#### 思路讲解
- 以 `nums[i]` 结尾的最大子数组，要么：
  - 只取自己
  - 接在前面的最大子数组后面
- 所以：
  - `dp[i] = max(nums[i], dp[i-1] + nums[i])`

```python
def maxSubArray(nums):
    # cur 表示以当前位置结尾的最大子数组和
    # ans 表示全局最大值
    cur = ans = nums[0]

    for i in range(1, len(nums)):
        # 决定是从当前重新开始，还是接在前面后面
        cur = max(nums[i], cur + nums[i])
        ans = max(ans, cur)

    return ans
```

### 典型面试题 4：最长公共子序列

#### 思路讲解
- `dp[i][j]` 表示：
  - `text1` 前 `i` 个字符
  - `text2` 前 `j` 个字符
  - 的最长公共子序列长度
- 若当前字符相同，则来自左上角加一。
- 若不同，则取“去掉一个字符后的较优解”。

```python
def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)

    # 多开一行一列，方便处理边界
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                # 当前字符相同，则继承左上角并 +1
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                # 否则从上方或左方取较大值
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]
```

### 典型面试题 5：零钱兑换

#### 思路讲解
- `dp[i]` 表示凑出金额 `i` 的最少硬币数。
- 对每个金额 `i`，尝试最后放入一枚硬币 `coin`。
- 则：
  - `dp[i] = min(dp[i], dp[i-coin] + 1)`

```python
def coinChange(coins, amount):
    # 用一个不可能的大值初始化，表示暂时无法凑出
    dp = [amount + 1] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if i - coin >= 0:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return -1 if dp[amount] == amount + 1 else dp[amount]
```

---

## 4.7 贪心

### 核心思想
- 贪心的核心是：每一步都做局部最优选择。
- 前提是这种局部最优能够推出全局最优。

### 什么时候想到贪心
- 区间选择
- 最少操作次数
- 能否到达终点
- 每一步都有一个“看起来最划算”的选择

### 典型面试题 1：买卖股票的最佳时机 II

#### 思路讲解
- 只要今天比昨天贵，就把这段上涨利润赚到。
- 因为连续上涨的总利润，拆成每天赚也不会损失。

```python
def maxProfit(prices):
    ans = 0

    for i in range(1, len(prices)):
        # 只累加所有上涨差值
        ans += max(0, prices[i] - prices[i - 1])

    return ans
```

### 典型面试题 2：跳跃游戏

#### 思路讲解
- 只要我们不断维护“当前最远可达位置”。
- 如果遍历到某个位置时，它已经超过最远可达位置，说明断掉了。
- 否则就更新更远的可达范围。

```python
def canJump(nums):
    farthest = 0

    for i, num in enumerate(nums):
        # 如果当前位置都到不了，直接失败
        if i > farthest:
            return False

        # 更新最远可达位置
        farthest = max(farthest, i + num)

    return True
```

### 典型面试题 3：跳跃游戏 II

#### 思路讲解
- 这题求最少跳几次。
- 可以把每一次跳跃看作“在当前可达区间内，尽量把下一步覆盖范围扩到最远”。
- 当扫描到当前区间终点时，就必须跳一次，并更新新区间边界。

```python
def jump(nums):
    end = 0       # 当前这一跳能覆盖到的边界
    farthest = 0  # 在当前区间内，下一跳最远能覆盖到哪里
    steps = 0

    for i in range(len(nums) - 1):
        # 更新在当前区间内能达到的最远位置
        farthest = max(farthest, i + nums[i])

        # 到达当前区间边界，说明必须跳一次
        if i == end:
            steps += 1
            end = farthest

    return steps
```

### 典型面试题 4：分发饼干

#### 思路讲解
- 为了让更多孩子满足，应该优先用最小的可行饼干喂胃口最小的孩子。
- 所以先排序，再双指针匹配。

```python
def findContentChildren(g, s):
    # 对孩子胃口和饼干尺寸分别排序
    g.sort()
    s.sort()

    i = j = 0

    while i < len(g) and j < len(s):
        if s[j] >= g[i]:
            # 当前饼干可以满足当前孩子
            i += 1
        # 不管是否满足，当前饼干都已经用掉
        j += 1

    return i
```

### 典型面试题 5：无重叠区间

#### 思路讲解
- 如果想保留尽可能多的区间，就应该优先保留结束时间更早的。
- 因为它更“省空间”，更容易给后面区间留位置。
- 这和活动选择问题是同一个思想。

```python
def eraseOverlapIntervals(intervals):
    # 按结束时间升序排序
    intervals.sort(key=lambda x: x[1])

    end = intervals[0][1]
    remove_count = 0

    for i in range(1, len(intervals)):
        if intervals[i][0] < end:
            # 当前区间和前面保留的区间重叠，只能删除一个
            remove_count += 1
        else:
            # 不重叠，则更新当前保留区间的结束位置
            end = intervals[i][1]

    return remove_count
```

---

## 4.8 BFS

### 核心思想
- BFS 是广度优先搜索。
- 它一层一层向外扩展。
- 因此在无权图中，BFS 非常适合求最短步数。

### 什么时候想到 BFS
- 二叉树层序遍历
- 最短步数
- 状态扩散
- 从一个起点一层一层传播

### 典型面试题 1：二叉树的层序遍历

#### 思路讲解
- 用队列保存当前层节点。
- 每次取出当前层所有节点，然后把下一层节点加入队列。

```python
from collections import deque


def levelOrder(root):
    if not root:
        return []

    q = deque([root])
    ans = []

    while q:
        level = []

        # 当前队列长度就是这一层节点数
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)

            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)

        ans.append(level)

    return ans
```

### 典型面试题 2：岛屿数量

#### 思路讲解
- 每遇到一个陆地 `'1'`，就说明发现了一个新岛屿。
- 然后用 BFS 把和它相连的所有陆地都“淹掉”。
- 这样它们不会被重复统计。

```python
from collections import deque


def numIslands(grid):
    if not grid:
        return 0

    m, n = len(grid), len(grid[0])
    ans = 0

    def bfs(i, j):
        q = deque([(i, j)])
        grid[i][j] = '0'

        while q:
            x, y = q.popleft()

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy

                if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == '1':
                    grid[nx][ny] = '0'
                    q.append((nx, ny))

    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1':
                ans += 1
                bfs(i, j)

    return ans
```

### 典型面试题 3：腐烂的橘子

#### 思路讲解
- 所有腐烂橘子会同时向四周扩散。
- 这种“多源同时扩散”的场景，天然就是 BFS。
- 一层 BFS 就表示过了一分钟。

```python
from collections import deque


def orangesRotting(grid):
    m, n = len(grid), len(grid[0])
    q = deque()
    fresh = 0

    # 先收集所有初始腐烂橘子，并统计新鲜橘子数量
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1

    minutes = 0

    # 只要还有新鲜橘子且队列不空，就继续扩散
    while q and fresh:
        for _ in range(len(q)):
            x, y = q.popleft()

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy

                if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                    grid[nx][ny] = 2
                    fresh -= 1
                    q.append((nx, ny))

        minutes += 1

    return minutes if fresh == 0 else -1
```

### 典型面试题 4：最小基因变化

#### 思路讲解
- 每次只能改动一个字符，且变化后的字符串必须在基因库中。
- 把每个合法基因看成图中的节点。
- 两个基因只差一个字符，就能连边。
- 题目要求最少变化次数，因此用 BFS。

```python
from collections import deque


def minMutation(startGene, endGene, bank):
    bank = set(bank)
    if endGene not in bank:
        return -1

    q = deque([(startGene, 0)])
    visited = {startGene}
    choices = "ACGT"

    while q:
        gene, step = q.popleft()

        if gene == endGene:
            return step

        # 枚举修改每一位得到的新基因
        for i in range(len(gene)):
            for ch in choices:
                next_gene = gene[:i] + ch + gene[i + 1:]

                if next_gene in bank and next_gene not in visited:
                    visited.add(next_gene)
                    q.append((next_gene, step + 1))

    return -1
```

### 典型面试题 5：打开转盘锁

#### 思路讲解
- 每种密码状态都可以看成图中的一个节点。
- 每次转动一个拨轮，会到达一个相邻状态。
- 求最少操作次数，就是标准 BFS 最短路。

```python
from collections import deque


def openLock(deadends, target):
    dead = set(deadends)
    if "0000" in dead:
        return -1

    q = deque([("0000", 0)])
    visited = {"0000"}

    def neighbors(state):
        result = []

        for i, ch in enumerate(state):
            digit = int(ch)

            # 当前位向上拨或向下拨
            for diff in (-1, 1):
                next_digit = (digit + diff) % 10
                next_state = state[:i] + str(next_digit) + state[i + 1:]
                result.append(next_state)

        return result

    while q:
        state, step = q.popleft()

        if state == target:
            return step

        for next_state in neighbors(state):
            if next_state not in dead and next_state not in visited:
                visited.add(next_state)
                q.append((next_state, step + 1))

    return -1
```

---

## 4.9 DFS

### 核心思想
- DFS 是深度优先搜索。
- 它会沿着一条路径一直深入，直到不能再走，再回退。
- 在树、图、回溯问题中非常常见。

### 什么时候想到 DFS
- 求所有路径
- 枚举所有可能
- 连通块问题
- 树的递归遍历

### 典型面试题 1：二叉树前序遍历

#### 思路讲解
- 前序遍历顺序是：
  - 根
  - 左
  - 右
- 这是标准递归 DFS。

```python
def preorderTraversal(root):
    ans = []

    def dfs(node):
        if not node:
            return

        # 前序：先处理根节点
        ans.append(node.val)
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return ans
```

### 典型面试题 2：路径总和

#### 思路讲解
- 从根走到叶子，每经过一个节点，就从目标值里减去当前节点值。
- 走到叶子节点时，如果刚好减到 0，就说明存在这条路径。

```python
def hasPathSum(root, targetSum):
    if not root:
        return False

    # 如果到达叶子节点，检查是否刚好满足路径和
    if not root.left and not root.right:
        return targetSum == root.val

    # 递归检查左子树或右子树
    return hasPathSum(root.left, targetSum - root.val) or \
           hasPathSum(root.right, targetSum - root.val)
```

### 典型面试题 3：岛屿数量（DFS 版）

#### 思路讲解
- 和 BFS 一样，每遇到一个 `'1'` 就代表一个新岛屿。
- 然后通过 DFS 递归把整片陆地都标记掉。

```python
def numIslandsDfs(grid):
    m, n = len(grid), len(grid[0])

    def dfs(i, j):
        # 越界或不是陆地，直接返回
        if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != '1':
            return

        # 标记为已访问
        grid[i][j] = '0'

        # 继续向四个方向搜索
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)

    ans = 0

    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1':
                ans += 1
                dfs(i, j)

    return ans
```

### 典型面试题 4：子集

#### 思路讲解
- 子集问题的关键是：
  - 对每个元素，都有“选”或“不选”两种状态
- 也可以理解为从当前位置开始，不断尝试把后面的元素加入路径。
- 每到一个递归层，当前路径都是一个合法子集。

```python
def subsets(nums):
    ans = []
    path = []

    def dfs(start):
        # 当前路径本身就是一个合法子集
        ans.append(path[:])

        # 从 start 开始尝试选择后续元素
        for i in range(start, len(nums)):
            path.append(nums[i])  # 做选择
            dfs(i + 1)            # 递归进入下一层
            path.pop()            # 撤销选择，回溯

    dfs(0)
    return ans
```

### 典型面试题 5：全排列

#### 思路讲解
- 全排列要求每个位置都尝试放一个还没使用过的数。
- 用 `used` 数组记录哪些元素已经在当前路径里。
- 当路径长度等于原数组长度时，就得到一个完整排列。

```python
def permute(nums):
    ans = []
    path = []
    used = [False] * len(nums)

    def dfs():
        # 路径长度等于数组长度时，说明形成一个完整排列
        if len(path) == len(nums):
            ans.append(path[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue

            used[i] = True
            path.append(nums[i])

            dfs()

            # 回溯：撤销当前选择
            path.pop()
            used[i] = False

    dfs()
    return ans
```

---

## 4.10 图算法

### 核心思想
- 图算法的本质是把问题抽象为“点和边”的关系。
- 常见问题类型：
  - 连通性
  - 是否有环
  - 最短路径
  - 依赖顺序

### 图算法常见专题
- BFS / DFS：图遍历
- 拓扑排序：依赖关系、有向无环图
- 并查集：连通性合并
- Dijkstra：带权最短路径

### 典型面试题 1：课程表

#### 思路讲解
- 若课程存在循环依赖，就无法完成。
- 这是典型拓扑排序问题。
- 思路是：
  - 统计每门课入度
  - 先学入度为 0 的课
  - 学完一门课，就减少它后继课程的入度
- 最终如果所有课程都能被取出，就说明无环。

```python
from collections import defaultdict, deque


def canFinish(numCourses, prerequisites):
    graph = defaultdict(list)
    indegree = [0] * numCourses

    # 建图并统计入度
    for course, pre in prerequisites:
        graph[pre].append(course)
        indegree[course] += 1

    # 所有入度为 0 的课程先入队
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

### 典型面试题 2：课程表 II

#### 思路讲解
- 和上一题一样，仍然是拓扑排序。
- 不同点在于，这次要返回一个合法学习顺序。
- 所以在出队时，把课程加入结果数组即可。

```python
from collections import defaultdict, deque


def findOrder(numCourses, prerequisites):
    graph = defaultdict(list)
    indegree = [0] * numCourses

    for course, pre in prerequisites:
        graph[pre].append(course)
        indegree[course] += 1

    q = deque([i for i in range(numCourses) if indegree[i] == 0])
    order = []

    while q:
        course = q.popleft()
        order.append(course)

        for next_course in graph[course]:
            indegree[next_course] -= 1
            if indegree[next_course] == 0:
                q.append(next_course)

    return order if len(order) == numCourses else []
```

### 典型面试题 3：省份数量（并查集）

#### 思路讲解
- 每个城市一开始属于不同集合。
- 若两个城市相连，就把它们合并到同一个集合。
- 最后集合个数就是省份数量。

```python
def findCircleNum(isConnected):
    n = len(isConnected)
    parent = list(range(n))

    def find(x):
        # 路径压缩：让树更扁平
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        root_x = find(x)
        root_y = find(y)

        if root_x != root_y:
            parent[root_x] = root_y

    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j] == 1:
                union(i, j)

    # 统计根节点个数，就是集合个数
    return sum(1 for i in range(n) if parent[i] == i)
```

### 典型面试题 4：网络延迟时间

#### 思路讲解
- 这是带权图最短路径问题。
- 从起点 `k` 出发，把信号传播到所有点。
- 如果我们知道从 `k` 到每个点的最短时间，那么所有点收到信号的最晚时间，就是答案。
- 使用 Dijkstra：
  - 小根堆每次取当前距离最短的节点
  - 用它去松弛相邻边

```python
import heapq
from collections import defaultdict


def networkDelayTime(times, n, k):
    graph = defaultdict(list)

    # 建图：u -> (v, w)
    for u, v, w in times:
        graph[u].append((v, w))

    # dist[i] 表示从 k 到 i 的当前最短距离
    dist = {i: float('inf') for i in range(1, n + 1)}
    dist[k] = 0

    # 小根堆：按当前距离排序
    heap = [(0, k)]

    while heap:
        current_dist, node = heapq.heappop(heap)

        # 如果弹出的不是最新最短距离，直接跳过
        if current_dist > dist[node]:
            continue

        for next_node, weight in graph[node]:
            new_dist = current_dist + weight

            if new_dist < dist[next_node]:
                dist[next_node] = new_dist
                heapq.heappush(heap, (new_dist, next_node))

    ans = max(dist.values())
    return ans if ans < float('inf') else -1
```

### 典型面试题 5：冗余连接

#### 思路讲解
- 给一棵树多加一条边后，会产生一个环。
- 问哪条边是多余的。
- 用并查集：
  - 若一条边连接的两个点原本就在同一集合中
  - 再连接就会成环
- 这条边就是冗余边。

```python
def findRedundantConnection(edges):
    n = len(edges)
    parent = list(range(n + 1))

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        root_x = find(x)
        root_y = find(y)

        # 如果本来就在一个集合中，说明加这条边会形成环
        if root_x == root_y:
            return False

        parent[root_x] = root_y
        return True

    for u, v in edges:
        if not union(u, v):
            return [u, v]
```

---

## 5. 面试复习建议

### 5.1 推荐学习顺序
1. 先掌握 `list / dict / set / deque / heapq`
2. 再学双指针、滑动窗口、哈希、二分
3. 然后学递归、树、BFS、DFS
4. 最后学动态规划、贪心、图算法

### 5.2 每道题的复盘模板
- 题目类型是什么
- 暴力解法是什么
- 为什么会超时
- 优化思路是什么
- 为什么这个方法正确
- 时间复杂度和空间复杂度是多少
- 下次看到什么特征要想到它

### 5.3 你最该先背熟的模板
- 双指针
- 滑动窗口
- 哈希统计
- 二分边界
- 树的 DFS / BFS
- 回溯
- 一维 DP / 二维 DP
- 拓扑排序
- 并查集
- Dijkstra

---

## 6. 速查模块导入清单

```python
from collections import Counter, defaultdict, deque
import heapq
```

---

## 7. 总结

- 数据结构解决“数据怎么存”。
- 算法思想解决“问题怎么拆、怎么优化”。
- 真正的面试能力，不是记住很多题，而是看到题目后能迅速判断：
  - 这是哪类问题
  - 应该用什么结构
  - 为什么这个方法更优

如果你接下来继续学，最推荐的方式是：
- 一天只学一个专题
- 先看思路，再默写代码
- 第二天重写前一天的题
- 把错题沉淀成自己的模板库

