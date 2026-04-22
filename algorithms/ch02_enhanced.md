# 第2章：算法分析

> **本章导读**：这是全书的"度量衡"章节。学完本章你会拥有一把尺子——大O符号，用它可以衡量任意算法的好坏。后续每学一种数据结构或算法，第一个要问的问题都是：它的时间复杂度是多少？为什么？
>
> **学习路径**：为什么需要分析 → 大O的直觉 → 大O的数学规则 → 如何分析代码 → Python内置操作复杂度 → 空间复杂度 → 均摊分析
>
> **核心问题**：两段代码都能得出正确答案，怎么判断哪个更好？答案不是"跑一下看谁快"——因为同一台机器、不同数据量、不同时刻的测量结果会不同。我们需要一种**与机器、数据无关的客观度量**。

---

## 2.0 关键术语速查

| 术语 | 英文 | 定义 |
|------|------|------|
| 算法分析 | Algorithm Analysis | 在不运行代码的前提下，预测算法的资源消耗 |
| 时间复杂度 | Time Complexity | 算法执行时间随输入规模 n 增长的变化趋势 |
| 空间复杂度 | Space Complexity | 算法运行时所需额外内存随 n 增长的变化趋势 |
| 大O符号 | Big-O Notation | 描述函数增长上界的数学符号，用于表示最坏情况 |
| 大Ω符号 | Big-Omega | 描述增长下界，表示最好情况 |
| 大Θ符号 | Big-Theta | 同时是上界和下界，表示增长的精确阶 |
| 输入规模 | Input Size (n) | 衡量输入大小的量（如列表长度、字符串长度、节点数） |
| 基本操作 | Basic Operation | 算法中被重复执行的核心操作，用于计数 |
| 最好情况 | Best Case | 输入使算法执行最少操作的情形 |
| 平均情况 | Average Case | 所有可能输入的平均执行操作数 |
| 最坏情况 | Worst Case | 输入使算法执行最多操作的情形（通常用此评估）|
| 常数复杂度 | O(1) | 与输入规模无关，执行时间固定 |
| 对数复杂度 | O(log n) | 每次把问题规模减半（二分的特征）|
| 线性复杂度 | O(n) | 执行时间与输入规模成正比 |
| 线性对数 | O(n log n) | 归并/快速排序的典型复杂度 |
| 平方复杂度 | O(n²) | 双重嵌套循环的典型复杂度 |
| 指数复杂度 | O(2ⁿ) | 穷举所有子集的复杂度，实际不可用 |
| 均摊分析 | Amortized Analysis | 将偶发的高代价操作均摊到多次操作上的分析方法 |
| 前缀和 | Prefix Sum | 预计算数组前缀的累计和，用于 O(1) 区间求和 |
| 滑动窗口 | Sliding Window | 维护一个可变窗口在数组上滑动的优化技巧 |

---

## 2.1 为什么需要算法分析？

### 从一个问题出发

```python
# 问题：判断一个数 n 是否是素数（质数）

# 方案A：暴力枚举，从2试到n-1
def is_prime_v1(n):
    if n < 2:
        return False
    for i in range(2, n):       # 试除次数：n-2 次
        if n % i == 0:
            return False
    return True

# 方案B：只试到 √n（数学优化）
def is_prime_v2(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):   # 试除次数：√n 次
        if n % i == 0:
            return False
    return True

# 两者都能正确判断，但性能差距悬殊：
# n=1_000_000：v1 需要约 100万次除法，v2 只需约 1000次
# n=10^14：   v1 需要约 10^14 次，v2 只需约 10^7 次
```

**直觉上我们知道 v2 更好，但如何精确量化"好多少"？**

这就是算法分析要解决的问题：用一套**标准化的语言**，精确描述算法性能随输入规模变化的规律，让不同算法可以公平比较。

---

### 为什么不直接计时？

```python
import time

def benchmark(func, n):
    start = time.time()
    func(n)
    return time.time() - start

# 直接计时的问题：
# 1. 不同机器结果不同（老电脑慢，新电脑快）
# 2. 同一机器，系统负载不同结果也不同
# 3. 无法预测"n=10^18 时要跑多久"
# 4. 小数据量差距不明显，大数据量可能要等几天

# 我们需要的是：
# ✅ 与机器无关
# ✅ 与实现语言无关
# ✅ 能预测大规模输入的行为
# ✅ 能数学证明的精确描述
```

---

## 2.2 ⭐ 大O符号——衡量增长趋势

### 核心思想

大O符号描述的不是"精确的运行时间"，而是**运行时间随输入规模 n 增长的趋势**。

```
关键规则：
  1. 忽略常数系数：3n 和 100n 都是 O(n)
     （系数只影响速度快慢，不影响增长趋势）
  
  2. 忽略低阶项：n² + n + 100 是 O(n²)
     （当 n 足够大，低阶项可以忽略不计）
  
  3. 只保留最高阶的那一项
```

**为什么可以忽略常数和低阶项？**

```
设 T(n) = 100n + 1000

n=10:   T(10) = 2000   其中 1000n = 100*10 = 1000，占 50%
n=100:  T(100) = 11000  其中 1000   占 9%
n=1000: T(1000) = 101000  其中 1000  占 1%
n=∞:   低阶项的占比趋近于 0%

当 n 足够大，决定性能的只有最高阶项。
```

```python
# 大O化简练习
T = lambda n: 5*n**2 + 3*n + 100     # → O(n²)
T = lambda n: 2*n + 10000             # → O(n)
T = lambda n: n * (n-1) / 2           # = 0.5n² - 0.5n → O(n²)
T = lambda n: 3                       # 常数 → O(1)
T = lambda n: n**3 + n**2 + n + 1    # → O(n³)
```

---

### 常见复杂度等级（从优到劣）

```
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)
最优                                                        最差
```

| 符号 | 名称 | 核心特征 | 典型例子 | n=1000时的操作数（约） |
|------|------|----------|---------|----------------------|
| `O(1)` | 常数 | 与 n 完全无关 | 数组按索引访问、字典查找 | **1** |
| `O(log n)` | 对数 | 每次问题减半 | 二分搜索 | **10** |
| `O(n)` | 线性 | 遍历一次 | 线性搜索、前缀和 | **1,000** |
| `O(n log n)` | 线性对数 | 分治+合并 | 归并排序、快速排序 | **10,000** |
| `O(n²)` | 平方 | 双重嵌套循环 | 冒泡排序、暴力两数之和 | **1,000,000** |
| `O(2ⁿ)` | 指数 | 穷举所有子集 | 暴力背包问题 | **10^301**（不可用）|
| `O(n!)` | 阶乘 | 穷举所有排列 | 暴力旅行商问题 | **10^2568**（不可用）|

### 数量级感受（直观理解）

```
假设计算机每秒执行 10^8 次基本操作（1亿次）：

n = 100：
  O(n)       = 100次       → 瞬间完成 ✅
  O(n²)      = 10,000次    → 瞬间完成 ✅
  O(2ⁿ)      = 10^30次     → 宇宙年龄都不够 ❌

n = 10,000：
  O(n)       = 10^4次      → 瞬间完成 ✅
  O(n log n) = 10^5次      → 瞬间完成 ✅
  O(n²)      = 10^8次      → 约1秒 ⚠️
  O(n³)      = 10^12次     → 约3小时 ❌

n = 10^6（百万）：
  O(n)       = 10^6次      → 约0.01秒 ✅
  O(n log n) = 2×10^7次    → 约0.2秒 ✅
  O(n²)      = 10^12次     → 约3小时 ❌

结论：O(n²) 在 n > 10^4 时通常已经太慢；
     O(n log n) 在绝大多数实际场景都是可接受的。
```

---

## 2.3 ⭐ 如何分析代码的复杂度

### 分析步骤

```
第1步：确定输入规模 n（通常是列表长度、字符串长度等）
第2步：找出"基本操作"（循环体内被重复执行的操作）
第3步：数基本操作执行了多少次（用 n 表示）
第4步：化简为大O形式（去常数、去低阶项）
```

### 规则1：顺序语句相加，取最大

```python
def analyze_sequential(lst):
    n = len(lst)
    
    # 段1：O(1) —— 固定操作
    total = 0
    max_val = lst[0]
    
    # 段2：O(n) —— 单层循环，执行 n 次
    for x in lst:
        total += x
    
    # 段3：O(n²) —— 双重嵌套，外n次 × 内n次
    for i in range(n):
        for j in range(i + 1, n):
            if lst[i] > lst[j]:
                lst[i], lst[j] = lst[j], lst[i]
    
    # 总计：O(1) + O(n) + O(n²) = O(n²) ← 取最高阶
    return total
```

### 规则2：嵌套循环相乘

```python
# 单层循环：O(n)
for i in range(n):            # 执行 n 次
    print(i)                  # 每次 O(1)
# 总计：n × 1 = O(n)

# 双层嵌套：O(n²)
for i in range(n):            # 外层 n 次
    for j in range(n):        # 内层每次 n 次
        print(i, j)           # 每次 O(1)
# 总计：n × n × 1 = O(n²)

# 内层不从0开始：仍是 O(n²)
for i in range(n):
    for j in range(i + 1, n): # 内层执行 n-1, n-2, ..., 1 次
        pass                  # 总计 n(n-1)/2 次 → O(n²)
```

### 规则3：问题规模减半 → O(log n)

```python
# 每次循环把 n 减半：O(log n)
def log_example(n):
    count = 0
    while n > 1:
        n = n // 2    # 每次减半！
        count += 1
    return count

# 执行追踪（n=16）：
# n=16 → n=8 → n=4 → n=2 → n=1，共 4 次 = log₂(16)
# n=1024 需要 log₂(1024) = 10 次
# n 翻倍，只多执行1次 ← 这就是对数增长的本质
```

### 规则4：函数调用要展开分析

```python
def process(lst):
    sorted_lst = sorted(lst)   # ← sorted() 是 O(n log n)，不是 O(1)！
    return sorted_lst[0]       # O(1)
# 总复杂度：O(n log n)，而不是 O(1)

# 常见陷阱：把内置函数当成 O(1)
def bad_analysis(lst, target):
    return target in lst        # ← list 的 in 是 O(n)，不是 O(1)！
```

### 经典案例分析

```python
# 案例1：找出最大值
def find_max(lst):
    max_val = lst[0]      # O(1)
    for x in lst[1:]:     # O(n)
        if x > max_val:   # O(1) 每次
            max_val = x
    return max_val        # O(1)
# 总：O(n)


# 案例2：判断是否有重复元素（暴力 vs 哈希）
def has_duplicate_brute(lst):
    n = len(lst)
    for i in range(n):              # 外层 n 次
        for j in range(i + 1, n):  # 内层约 n 次
            if lst[i] == lst[j]:
                return True
    return False
# 总：O(n²)

def has_duplicate_hash(lst):
    seen = set()
    for x in lst:             # O(n)
        if x in seen:         # O(1) 平均
            return True
        seen.add(x)           # O(1) 平均
    return False
# 总：O(n)，用 O(n) 额外空间换来 O(n) 时间提升


# 案例3：矩阵乘法（理解 O(n³)）
def matrix_multiply(A, B, n):
    """n×n 矩阵相乘"""
    C = [[0] * n for _ in range(n)]
    for i in range(n):            # 外层 n 次
        for j in range(n):        # 中层 n 次
            for k in range(n):    # 内层 n 次
                C[i][j] += A[i][k] * B[k][j]
    return C
# 总：O(n³)  n=100时是100万次，n=1000时是10亿次！


# 案例4：递归的复杂度（斐波那契）
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n-1) + fib_naive(n-2)
# 每次调用产生2个子调用，深度为n
# 调用总次数约 2^n → O(2ⁿ)
# n=40 时约 10亿次调用，需要几秒
# n=100 时根本跑不完
```

---

## 2.4 三种情况：最好、平均、最坏

```python
def linear_search(lst, target):
    """在无序列表中查找目标值"""
    for i in range(len(lst)):
        if lst[i] == target:
            return i
    return -1

# ── 最好情况（Best Case）——————————————————————————
# target 恰好在第一个位置
# 执行1次比较 → O(1)
# 用 Big-Ω 表示：Ω(1)

# ── 平均情况（Average Case）——————————————————————
# target 随机分布在列表中
# 平均需要 n/2 次比较 → O(n)
# 通常需要概率分析

# ── 最坏情况（Worst Case）—————————————————————————
# target 在最后一个位置，或根本不存在
# 执行 n 次比较 → O(n)
# 用 Big-O 表示：O(n)

# 通常说的复杂度 = 最坏情况
# 理由：最坏情况是算法性能的"保证上限"
#       知道最坏情况，就知道算法"最差能坏到什么程度"
```

### 为什么通常关注最坏情况？

```
理由1：工程保证
  数据库查询可能没有缓存命中 → 需要知道最坏有多慢
  操作系统调度需要保证响应时间 → 最坏情况决定可靠性

理由2：平均情况难以分析
  平均情况需要对输入的概率分布做假设
  现实中输入的分布往往未知

理由3：悲观但安全
  "最坏不过如此"让系统设计有依据
```

---

## 2.5 ⭐ Python 内置操作的复杂度

**这部分是面试高频考点，必须背熟！**

### 列表（list）操作复杂度

```python
lst = [1, 2, 3, 4, 5]

# ═══ O(1) 操作（快）═══════════════════════════════

lst[2]              # 按索引访问（随机访问，直接计算内存地址）
lst[-1]             # 末尾访问（等价于 lst[len-1]）
lst.append(6)       # 末尾追加（均摊 O(1)，偶尔扩容 O(n)）
lst.pop()           # 末尾删除（移除最后一个，不需要移动其他元素）
len(lst)            # 获取长度（Python 在对象头部存储了 size 字段）

# ═══ O(n) 操作（慢）═══════════════════════════════

lst.insert(0, 0)   # 头部插入
                   # ← 必须把所有现有元素向右移动一格，O(n)

lst.pop(0)         # 头部删除
                   # ← 必须把所有后续元素向左移动一格，O(n)

lst.remove(3)      # 按值删除
                   # ← 先线性扫描找到元素，再移动后续元素，O(n)

3 in lst           # 成员检查
                   # ← 从头到尾逐个比较，最坏 O(n)

lst.index(3)       # 查找索引（同上，线性扫描）

lst.reverse()      # 原地翻转（需要遍历一半元素做交换）

lst.copy()         # 浅拷贝（需要复制所有元素）

sorted(lst)        # 排序（Timsort：O(n log n)）
lst.sort()         # 原地排序（Timsort：O(n log n)）


# ═══ 为什么 append 是 O(1) 而不是 O(n)？（均摊分析）═══
# Python list 是动态数组，初始分配一定容量
# 当容量满时，扩容为 2 倍并把所有元素复制过去（O(n)）
# 
# 分析 n 次 append 的总代价：
# 拷贝次数 = 1+2+4+...+n/2 ≈ n（等比数列求和）
# n 次 append 总代价 = O(n)，平均每次 = O(1)
# 这就是"均摊 O(1)"的含义
```

### 字典（dict）/ 集合（set）操作复杂度

```python
d = {'a': 1, 'b': 2}

# ═══ O(1) 平均（基于哈希表）═══════════════════════

d['a']           # 按键访问   ← 哈希计算直接定位，O(1)
d['c'] = 3       # 插入/更新  ← 哈希计算定位槽位，O(1)
del d['a']       # 删除       ← 哈希计算定位，O(1)
'a' in d         # 成员检查   ← 哈希计算，O(1)！ 比 list 快得多
d.get('a', 0)    # 安全访问

# 集合操作
s = {1, 2, 3}
s.add(4)         # O(1)
4 in s           # O(1)  ← 与 dict 同样的哈希机制
s.remove(2)      # O(1)

# ═══ O(n) 操作 ═══════════════════════════════════
list(d.keys())   # 转为列表，O(n)
list(d.values()) # 转为列表，O(n)


# ⚠️ 最坏情况：O(n)（哈希冲突严重时）
# 但精心设计的哈希函数极少触发最坏情况
# Python 的 dict 做了很多工程优化，实践中几乎总是 O(1)
```

### 关键对比：列表 vs 字典的成员检查

```python
import timeit, random

n = 100_000
data = list(range(n))
random.shuffle(data)

lst  = data[:]
d    = {x: True for x in data}
s    = set(data)
target = n - 1   # 查找最坏情况：最后一个元素

# 列表：O(n)
t1 = timeit.timeit(lambda: target in lst, number=1000)

# 字典：O(1)
t2 = timeit.timeit(lambda: target in d, number=1000)

# 集合：O(1)
t3 = timeit.timeit(lambda: target in s, number=1000)

print(f"列表成员检查（O(n)）: {t1:.4f}s")
print(f"字典成员检查（O(1)）: {t2:.6f}s")
print(f"集合成员检查（O(1)）: {t3:.6f}s")
# 典型结果：列表约2s，字典/集合约0.00005s
# 差距：约 40000 倍！

# 结论：
# ✅ 需要频繁查找？→ 用 dict 或 set
# ✅ 需要按顺序访问？→ 用 list
# ❌ 不要对 list 做频繁的 in 检查（数据量大时极慢）
```

### 字符串操作复杂度

```python
s = "hello world"

# O(1)
len(s)           # 长度
s[2]             # 索引访问

# O(n)
s.find('world')  # 查找子串
s.count('l')     # 计数
s.replace('l','L') # 替换（创建新字符串）

# O(n) —— 字符串拼接的陷阱！
# ❌ 低效方式（每次拼接创建新字符串）：
result = ""
for i in range(n):
    result += str(i)    # n 次拼接，总代价 O(n²)！

# ✅ 高效方式：
result = "".join(str(i) for i in range(n))   # O(n)
```

---

## 2.6 ⭐ 空间复杂度

空间复杂度衡量的是算法运行所需的**额外内存**（不包括输入本身）。

### 常见空间复杂度

```python
# ═══ O(1) 额外空间（原地操作）══════════════════════

def find_max(lst):
    """
    只用固定数量的变量（max_val, x），
    无论 lst 有多长，额外内存固定不变
    """
    max_val = lst[0]     # 1个变量
    for x in lst:        # 循环变量不计入额外空间
        if x > max_val:
            max_val = x
    return max_val       # 额外空间：O(1)


def reverse_inplace(lst):
    """双指针原地翻转，O(1) 额外空间"""
    left, right = 0, len(lst) - 1
    while left < right:
        lst[left], lst[right] = lst[right], lst[left]
        left  += 1
        right -= 1
    # 额外变量：left, right（2个），O(1)


# ═══ O(n) 额外空间══════════════════════════════════

def get_double(lst):
    """
    创建与输入等大小的新列表
    额外空间 = n 个元素 → O(n)
    """
    return [x * 2 for x in lst]   # 新列表，O(n) 空间


def prefix_sum(lst):
    """
    前缀和数组，大小为 n+1
    额外空间：O(n)
    """
    n = len(lst)
    pre = [0] * (n + 1)           # O(n) 额外数组
    for i in range(n):
        pre[i + 1] = pre[i] + lst[i]
    return pre


# ═══ O(n) 隐式空间（递归调用栈）══════════════════════

def factorial(n):
    """
    递归深度 = n 层
    每层占一个栈帧 → O(n) 栈空间
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def merge_sort(lst):
    """
    空间：O(n) ← 合并时需要临时数组
    注意：O(n log n) 时间，O(n) 空间（不是 O(log n)）
    """
    if len(lst) <= 1:
        return lst
    mid = len(lst) // 2
    left  = merge_sort(lst[:mid])   # 递归：O(log n) 调用栈
    right = merge_sort(lst[mid:])
    # 合并时临时数组最大 O(n)
    return _merge(left, right)      # O(n) 合并空间
```

### 时间与空间的权衡

```
在算法设计中，时间和空间通常是可以互相换的：

用空间换时间（典型例子）：
  哈希表：O(n) 额外空间 → 查找从 O(n) 降到 O(1)
  记忆化：O(n) 缓存空间 → 递归从 O(2ⁿ) 降到 O(n)
  前缀和：O(n) 预计算 → 区间求和从 O(n) 降到 O(1)

用时间换空间（典型例子）：
  不用前缀和，每次区间求和重新计算 → O(1) 空间，O(n) 查询
  不用记忆化，每次重新递归 → O(1) 空间，O(2ⁿ) 时间

实际工程中：
  内存通常比时间更充裕（1GB内存可以存 2.5亿个整数）
  因此通常优先优化时间复杂度
```

---

## 2.7 均摊分析（Amortized Analysis）

### 概念

均摊分析用于分析**偶发昂贵操作**的实际代价：
把偶尔出现的高代价操作，均摊到每次调用上，得到每次操作的"平均"代价。

### 典型案例：动态数组的 append

```python
# Python list 的 append 实现原理：

# 底层是"动态数组"：
# - 初始分配一定容量（如4个槽位）
# - 满了就扩容（变为原来2倍），并复制所有元素
# - 然后再追加新元素

# 模拟16次 append 的代价：
# 
# 追加1: 不满，代价=1
# 追加2: 不满，代价=1
# 追加3: 不满，代价=1
# 追加4: 不满，代价=1
# 追加5: 满了！扩容（复制4个）+追加，代价=4+1=5
# 追加6~8: 代价各=1
# 追加9: 满了！扩容（复制8个）+追加，代价=8+1=9
# 追加10~16: 代价各=1
# 追加17: 满了！扩容（复制16个）+追加，代价=16+1=17
#
# 前16次 append 总代价 = 1+1+1+1+5+1+1+1+9+1+1+1+1+1+1+1 = 27
# 均摊每次代价 = 27/16 ≈ 1.7 = O(1)
#
# 数学分析：n 次 append，拷贝总次数 = 1+2+4+...+n ≈ 2n
# 均摊每次代价 = 2n/n = 2 = O(1)

# 结论：虽然偶尔会有 O(n) 的扩容操作，
#       但均摊下来每次 append 是 O(1)
```

---

## 2.8 ⭐【面试题实战】

### 面试题1：两数之和（LeetCode 1，Easy）

**题目**：给定整数数组 `nums` 和目标值 `target`，找出两个数的索引使其和等于 `target`，每个输入只有唯一解。

#### 暴力 → 哈希的完整演进

```python
# ── 方案1：暴力双重循环，O(n²) 时间 O(1) 空间 ────────────────
def two_sum_brute(nums, target):
    """
    枚举所有两数对
    
    执行流程（nums=[2,7,11,15], target=9）：
    i=0(2), j=1(7):  2+7=9  ✅ 返回 [0,1]
    
    最坏情况：答案在最后，需要枚举所有 n(n-1)/2 对 → O(n²)
    """
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):       # j 从 i+1 开始，避免重复和自配
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


# ── 方案2：哈希表，O(n) 时间 O(n) 空间 ──────────────────────
def two_sum_hash(nums, target):
    """
    哈希表存储"已见过的数"
    
    关键洞察：
    找 nums[i] + nums[j] == target
    等价于：对每个 nums[i]，找是否存在 target - nums[i]
    
    如果把已见过的数存入哈希表，查找 O(1) 而不是 O(n)！
    
    执行流程（nums=[2,7,11,15], target=9）：
    
    i=0, num=2:
      need = 9-2 = 7
      7 不在 seen 里  →  seen={2:0}
    
    i=1, num=7:
      need = 9-7 = 2
      2 在 seen 里！seen[2]=0  →  返回 [seen[2], i] = [0, 1] ✅
    
    时间：O(n)，每个元素只处理一次
    空间：O(n)，最坏情况哈希表存 n 个元素
    """
    seen = {}    # {数值: 索引}
    
    for i, num in enumerate(nums):
        need = target - num      # 需要找到的配对数
        
        if need in seen:         # O(1) 查找！
            return [seen[need], i]
        
        seen[num] = i            # 记录当前数的索引
    
    return []


# 测试
print(two_sum_hash([2, 7, 11, 15], 9))    # [0, 1]
print(two_sum_hash([3, 2, 4], 6))          # [1, 2]
print(two_sum_hash([3, 3], 6))             # [0, 1]

# 性能对比（n=10000）：
# 暴力：约 5000万次操作
# 哈希：约 1万次操作
# 提升约 5000 倍！
```

> **⚠️ 面试注意点**：
> 1. 先说暴力 O(n²) 方案，表明理解了问题
> 2. 指出优化方向："需要 O(1) 查找配对数" → 哈希表
> 3. 注意 `seen[num] = i` 放在查找之后，避免 `[3,3],6` 时用同一个元素两次

---

### 面试题2：寻找数组的中心下标（LeetCode 724，Easy）

**题目**：找一个下标 `i`，使得 `i` 左边所有数之和 = `i` 右边所有数之和。

**核心技术：前缀和**——O(n²) 暴力 → O(n) 前缀和优化。

```python
# ── 方案1：暴力，O(n²) ────────────────────────────────────────
def pivot_index_brute(nums):
    """
    对每个位置，重新计算左和右的和
    O(n) 的位置 × O(n) 的求和 = O(n²)
    """
    n = len(nums)
    for i in range(n):
        left_sum  = sum(nums[:i])      # O(i) 计算左和
        right_sum = sum(nums[i+1:])    # O(n-i) 计算右和
        if left_sum == right_sum:
            return i
    return -1


# ── 方案2：前缀和，O(n) 时间 O(n) 空间 ──────────────────────
def pivot_index_prefix(nums):
    """
    预计算前缀和，O(1) 得到任意区间的和
    
    前缀和定义：pre[i] = nums[0] + nums[1] + ... + nums[i-1]
    pre[0] = 0（空前缀）
    
    执行流程（nums=[1, 7, 3, 6, 5, 6]）：
    pre = [0, 1, 8, 11, 17, 22, 28]
    
    检查 i=3（值=6）：
    左和 = pre[3] = 11
    右和 = pre[6] - pre[4] = 28 - 17 = 11
    11 == 11 ✅ 返回 3
    """
    n = len(nums)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + nums[i]
    
    total = pre[n]
    for i in range(n):
        left_sum  = pre[i]            # O(1) 查表
        right_sum = total - pre[i+1] # O(1) 查表
        if left_sum == right_sum:
            return i
    return -1


# ── 方案3：O(n) 时间 O(1) 空间（最优）──────────────────────
def pivot_index_optimal(nums):
    """
    只用两个变量：left_sum 和 right_sum
    
    初始：left_sum=0，right_sum=总和-nums[0]
    每次右移：left_sum += nums[i-1]，right_sum -= nums[i]
    
    执行流程（nums=[1,7,3,6,5,6]，total=28）：
    
    i=0: left=0,  right=28-1=27,  0≠27
    i=1: left=1,  right=27-7=20,  1≠20
    i=2: left=8,  right=20-3=17,  8≠17
    i=3: left=11, right=17-6=11,  11==11 ✅ 返回3
    """
    total    = sum(nums)
    left_sum = 0
    
    for i, num in enumerate(nums):
        right_sum = total - left_sum - num
        if left_sum == right_sum:
            return i
        left_sum += num
    
    return -1


print(pivot_index_optimal([1, 7, 3, 6, 5, 6]))   # 3
print(pivot_index_optimal([1, 2, 3]))              # -1
print(pivot_index_optimal([2, 1, -1]))             # 0
```

> **⭐ 前缀和是高频优化技巧**：任何"区间求和"操作，都可以用前缀和从 O(n) 降到 O(1)，代价是 O(n) 额外空间。

---

### 面试题3：无重复字符的最长子串（LeetCode 3，Medium）

**题目**：给定字符串 `s`，找出不含重复字符的最长子串的长度。

**核心技术：滑动窗口**——O(n²) 暴力 → O(n) 滑动窗口优化。

```python
# ── 方案1：暴力，O(n²) 或 O(n³) ────────────────────────────
def length_of_longest_v1(s):
    """
    枚举所有子串，检查是否无重复
    O(n²) 枚举 × O(n) 检查 = O(n³)
    （如果用集合，可以做到 O(n²)）
    """
    n = len(s)
    max_len = 0
    for i in range(n):
        seen = set()
        for j in range(i, n):
            if s[j] in seen:     # 发现重复，停止
                break
            seen.add(s[j])
            max_len = max(max_len, j - i + 1)
    return max_len


# ── 方案2：滑动窗口 + 哈希表，O(n) ──────────────────────────
def length_of_longest_v2(s):
    """
    滑动窗口：维护一个无重复字符的窗口 [left, right]
    right 不断右移扩大窗口，遇到重复字符则 left 右移缩小窗口
    
    核心洞察：
    遇到重复字符 s[right] 时，不需要从头重新开始，
    只需把 left 跳到"上次 s[right] 出现位置的下一位"
    
    执行流程（s="abcabcbb"）：
    
    char_idx = {}（记录每个字符最后出现的索引）
    left=0, max_len=0
    
    right=0, s[0]='a': 未见过，char_idx={'a':0}, 窗口[0,0], len=1
    right=1, s[1]='b': 未见过，char_idx={'a':0,'b':1}, 窗口[0,1], len=2
    right=2, s[2]='c': 未见过，char_idx={..,'c':2}, 窗口[0,2], len=3
    
    right=3, s[3]='a': 见过！'a'上次在索引0，left=max(0, 0+1)=1
    char_idx={'a':3,'b':1,'c':2}, 窗口[1,3], len=3
    
    right=4, s[4]='b': 见过！'b'上次在索引1，left=max(1, 1+1)=2
    窗口[2,4], len=3
    
    right=5, s[5]='c': 见过！'c'上次在索引2，left=max(2, 2+1)=3
    窗口[3,5], len=3
    
    right=6, s[6]='b': 见过！'b'上次在索引4，left=max(3, 4+1)=5
    窗口[5,6], len=2
    
    right=7, s[7]='b': 见过！'b'上次在索引6，left=max(5, 6+1)=7
    窗口[7,7], len=1
    
    返回 max_len=3（对应子串"abc"）
    
    时间：O(n)，right 和 left 各最多移动 n 次
    空间：O(min(n, 字符集大小))，哈希表大小
    """
    char_idx = {}   # {字符: 最后出现的索引}
    left    = 0
    max_len = 0
    
    for right, char in enumerate(s):
        if char in char_idx and char_idx[char] >= left:
            # 重复字符在当前窗口内：left 跳过它
            left = char_idx[char] + 1
        
        char_idx[char] = right                    # 更新最新位置
        max_len = max(max_len, right - left + 1)  # 更新最大窗口
    
    return max_len


print(length_of_longest_v2("abcabcbb"))   # 3（"abc"）
print(length_of_longest_v2("bbbbb"))      # 1（"b"）
print(length_of_longest_v2("pwwkew"))     # 3（"wke"）
print(length_of_longest_v2(""))           # 0
```

> **⭐ 滑动窗口模式**：适用于"连续子数组/子串"类问题。核心是维护一个满足条件的窗口 `[left, right]`，right 右移扩展，left 右移收缩，两个指针各走 O(n) 步，总体 O(n)。

---

### 面试题4：移动零（LeetCode 283，Easy）

**题目**：将数组中所有 `0` 移到末尾，非零元素相对顺序不变，原地操作。

**核心技术：双指针**

```python
def move_zeroes(nums):
    """
    双指针：slow 指向下一个非零元素应该放置的位置
    
    思路：
    slow 指针：指向"已处理好部分的末尾"
    fast 指针：扫描整个数组
    
    遇到非零：放到 slow 位置，slow 右移
    遇到零  ：跳过（fast 继续，slow 不动）
    最后把 slow 之后全置零
    
    执行流程（nums=[0,1,0,3,12]）：
    
    slow=0
    fast=0: nums[0]=0，跳过
    fast=1: nums[1]=1≠0，nums[slow(0)]=1，slow=1   → [1,1,0,3,12]
    fast=2: nums[2]=0，跳过
    fast=3: nums[3]=3≠0，nums[slow(1)]=3，slow=2   → [1,3,0,3,12]
    fast=4: nums[4]=12≠0，nums[slow(2)]=12，slow=3  → [1,3,12,3,12]
    
    把 slow(3) 到末尾全置0          → [1,3,12,0,0] ✅
    
    时间：O(n)，空间：O(1)
    """
    slow = 0   # 下一个非零元素应放置的位置
    
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow] = nums[fast]
            slow += 1
    
    # slow 之后的位置全部置零
    for i in range(slow, len(nums)):
        nums[i] = 0

nums = [0, 1, 0, 3, 12]
move_zeroes(nums)
print(nums)   # [1, 3, 12, 0, 0]
```

---

### 面试题5：复杂度陷阱题（代码分析）

**这类题在面试中很常见：给你一段代码，说出其时间复杂度。**

```python
# ── 陷阱1：看似 O(n) 实则 O(n²) ─────────────────────────────
def trap1(lst):
    result = ""
    for x in lst:
        result += str(x)   # ❌ 字符串 += 每次创建新字符串，O(n) 每次
    return result
# 时间复杂度：O(n²)！不是 O(n)
# 正确写法：''.join(str(x) for x in lst)  → O(n)


# ── 陷阱2：内层循环不依赖外层 ──────────────────────────────
def trap2(m, n):
    for i in range(m):       # 外层 m 次
        for j in range(n):   # 内层 n 次（与 m 无关！）
            pass
# 时间复杂度：O(m × n)，而不是 O(n²)！
# 若 m 和 n 相同量级才是 O(n²)


# ── 陷阱3：函数调用隐藏复杂度 ─────────────────────────────
def trap3(lst):
    for i in range(len(lst)):           # O(n)
        if lst[i] in lst[i+1:]:         # list 切片是 O(n)，in 是 O(n)
            return True                 # 这里是 O(n) 操作！
    return False
# 时间复杂度：O(n) × O(n) = O(n²)


# ── 陷阱4：两个变量的情况 ─────────────────────────────────
def trap4(m, n):
    i = m
    while i > 0:
        j = n
        while j > 0:
            j //= 2     # j 每次减半！
        i -= 1
# 外层：O(m)；内层：O(log n)（j 每次减半）
# 时间复杂度：O(m log n)


# ── 陷阱5：递归复杂度 ──────────────────────────────────────
def trap5(n):
    if n <= 0:
        return
    for i in range(n):   # O(n)
        print(i)
    trap5(n // 2)        # 递归，规模减半
    trap5(n // 2)        # 又一次递归

# 设 T(n) = 执行总次数
# T(n) = n + 2 × T(n/2)
# 展开：n + 2×(n/2 + 2×T(n/4))
#       = n + n + 4×T(n/4)
#       = n + n + n + 8×T(n/8)
#       = n × log(n)（共 log n 层，每层 O(n) 工作）
# 时间复杂度：O(n log n)


# ── 测试你的分析 ────────────────────────────────────────────
# 下面这段代码的复杂度是多少？
def mystery(n):
    count = 0
    i = 1
    while i < n:
        j = 0
        while j < i:
            count += 1
            j += 1
        i *= 2        # i 翻倍！
    return count

# 分析：
# i 的值序列：1, 2, 4, 8, ..., n/2
# 共 log(n) 轮
# 第 k 轮（i=2^(k-1)）：内层执行 2^(k-1) 次
# 总次数 = 1 + 2 + 4 + ... + n/2 = n - 1 ≈ O(n)
# 时间复杂度：O(n)（不是 O(n log n)！）
```

---

## 2.9 本章要点总结

### 核心概念映射表

| 概念 | 定义 | 如何判断 | 典型场景 |
|------|------|---------|---------|
| **O(1)** | 与输入规模无关 | 没有循环，直接计算 | 数组按索引访问、哈希查找 |
| **O(log n)** | 每次问题规模减半 | `while n > 0: n //= 2` | 二分搜索、AVL树操作 |
| **O(n)** | 遍历一遍 | 单层 for/while 循环 | 线性搜索、前缀和构建 |
| **O(n log n)** | 分治后合并 | 递归+线性合并 | 归并/快速排序 |
| **O(n²)** | 双重嵌套 | 两层嵌套循环 | 冒泡排序、暴力两数之和 |
| **O(2ⁿ)** | 每步两个分支 | 递归有两个子调用 | 暴力斐波那契 |

### 大O化简规则

```
规则1：系数无关     O(3n) = O(n)，O(100) = O(1)
规则2：取最高阶     O(n² + n) = O(n²)，O(n + log n) = O(n)
规则3：相乘不相加   嵌套循环：O(m) × O(n) = O(mn)
规则4：顺序取最大   O(n) + O(n²) = O(n²)
```

### Python 关键操作复杂度速查

| 操作 | list | dict / set |
|------|------|-----------|
| 按索引/键访问 | **O(1)** | **O(1)** |
| 末尾追加/插入 | **O(1)** 均摊 | **O(1)** 均摊 |
| 头部插入 | O(n) ❌ | — |
| 成员检查 `in` | O(n) ❌ | **O(1)** ✅ |
| 按值删除 | O(n) | **O(1)** |
| 排序 | O(n log n) | — |
| 切片 `lst[a:b]` | O(b-a) | — |

### 优化技术与复杂度改进

| 技术 | 改进 | 代价 | 适用场景 |
|------|------|------|---------|
| **哈希表** | 查找 O(n)→O(1) | O(n) 额外空间 | 频繁查找、去重 |
| **前缀和** | 区间和 O(n)→O(1) | O(n) 额外空间 | 多次区间查询 |
| **滑动窗口** | O(n²)→O(n) | O(1) 额外空间 | 连续子数组/子串问题 |
| **双指针** | O(n²)→O(n) | O(1) 额外空间 | 有序数组、原地操作 |
| **记忆化** | O(2ⁿ)→O(n) | O(n) 额外空间 | 重叠子问题的递归 |
| **分治** | O(n²)→O(n log n) | O(log n) 栈空间 | 排序、数组问题 |

### 面试高频考点

| 题目 | 暴力复杂度 | 优化复杂度 | 关键技术 | 难度 |
|------|----------|-----------|---------|------|
| 两数之和 LC1 | O(n²) | O(n) | 哈希表 | Easy |
| 中心下标 LC724 | O(n²) | O(n) | 前缀和 | Easy |
| 无重复最长子串 LC3 | O(n²) | O(n) | 滑动窗口 | Medium |
| 移动零 LC283 | O(n²) | O(n) | 双指针 | Easy |
| 复杂度分析 | — | — | 逐段分析 | — |

### 分析代码复杂度的步骤

```
第1步：确认 n 是什么（列表长度？字符串长度？矩阵维度？）
第2步：找循环层数（1层→O(n)，2层→O(n²)，以此类推）
第3步：检查内层循环是否依赖外层（是→相乘，否→相加）
第4步：检查每次循环 n 的变化（减1→O(n)，减半→O(log n)）
第5步：展开所有函数调用（不要把 sorted() 当 O(1)）
第6步：保留最高阶，去掉系数
```

### 常见陷阱（坑点）

| 陷阱 | 错误认知 | 正确答案 |
|------|---------|---------|
| 字符串 `+=` 拼接 | 以为是 O(1) | 实际 O(n)，n 次拼接共 O(n²) |
| `list` 的 `in` | 以为是 O(1) | 实际 O(n)！用 `set` 或 `dict` |
| `sorted()` / `list.sort()` | 以为是 O(n) | 实际 O(n log n) |
| `list.insert(0, x)` | 以为是 O(1) | 实际 O(n)，需移动所有元素 |
| 列表切片 `lst[a:b]` | 以为是 O(1) | 实际 O(b-a)，会复制元素 |
| 递归深度 | 忽略调用栈空间 | 每层递归占 O(1) 栈帧，深度 d→O(d) 空间 |

---

> **给初学者的学习建议**：
> 1. **看到代码，先数循环层数**——这是判断复杂度最快的第一直觉。单层=O(n)，双层嵌套=O(n²)，然后再检查有没有减半/跳跃等特殊情况。
> 2. **背熟列表和字典的操作复杂度**——尤其是"列表的 `in` 是 O(n)，字典的 `in` 是 O(1)"，这个差异在面试和实际开发中非常高频。
> 3. **学会三个优化利器**：哈希表（降低查找代价）、前缀和（降低区间查询代价）、滑动窗口（降低连续子数组问题代价），这三个技巧能解决 60% 以上的初中级算法题。
> 4. **本章是全书的工具**——后面每学一个新算法（排序、树、图……），都要回来问：它的时间复杂度是多少？为什么？有没有更好的算法？
