# 第2章：算法分析

> **核心思路**：量化算法的好坏——同样能解决问题的方案，哪个更快、更省空间？建立大O符号作为"通用语言"，贯穿全书。

---

## 2.1 为什么需要算法分析？

同一个问题，可以有多种解法。我们需要一种**客观、可量化**的方式来比较它们。

```python
# 问题：计算前 n 个整数之和

# 方法一：循环累加
def sum_of_n_v1(n):
    total = 0
    for i in range(1, n + 1):
        total += i          # 执行 n 次
    return total

# 方法二：数学公式（高斯求和）
def sum_of_n_v2(n):
    return n * (n + 1) // 2  # 执行 1 次，无论 n 多大

# 两者结果相同，但效率天壤之别！
# n=1000:    v1需要1000次加法，v2只需1次乘法
# n=1000000: v1需要百万次运算，v2仍然只需1次
```

**结论**：光靠"能跑出结果"是不够的，我们需要分析算法随输入规模增长时的行为。

---

## 2.2 大O符号（Big-O Notation）

### ⭐ 核心定义

**大O符号**描述算法运行时间（或空间）随输入规模 `n` 增长的**趋势**。

- 忽略常数系数（`3n` 视为 `n`）
- 忽略低阶项（`n² + n` 视为 `n²`）
- 只保留**增长最快的那一项**

```
T(n) = 5n² + 3n + 100  →  O(n²)
T(n) = 2n + 10000       →  O(n)
T(n) = n·log(n) + n     →  O(n log n)
```

### 常见复杂度等级（从优到劣）

| 符号 | 名称 | 直觉理解 | 举例 |
|------|------|----------|------|
| `O(1)` | 常数 | 无论n多大，时间固定 | 列表按索引访问 |
| `O(log n)` | 对数 | n翻倍，时间只+1 | 二分搜索 |
| `O(n)` | 线性 | 时间与n成正比 | 顺序查找 |
| `O(n log n)` | 线性对数 | 比线性稍慢 | 归并排序 |
| `O(n²)` | 平方 | n翻倍，时间×4 | 冒泡排序 |
| `O(2ⁿ)` | 指数 | n+1，时间×2 | 暴力穷举子集 |
| `O(n!)` | 阶乘 | 增长极快 | 暴力全排列 |

### 复杂度增长速度可视化

```
n=1:    O(1)=1  O(logn)=0  O(n)=1    O(nlogn)=0   O(n²)=1
n=10:   O(1)=1  O(logn)=3  O(n)=10   O(nlogn)=33  O(n²)=100
n=100:  O(1)=1  O(logn)=7  O(n)=100  O(nlogn)=664 O(n²)=10000
n=1000: O(1)=1  O(logn)=10 O(n)=1000 O(nlogn)=10k O(n²)=1000000
```

---

## 2.3 代码分析方法

### 规则：逐行分析，找出主导项

```python
def example(n):
    # 第1行：O(1) —— 赋值一次
    total = 0
    
    # 第2-3行：O(n) —— 循环n次，每次O(1)
    for i in range(n):
        total += i
    
    # 第4-6行：O(n²) —— 嵌套循环，外n次×内n次
    for i in range(n):
        for j in range(n):
            print(i, j)
    
    return total

# 总复杂度：O(1) + O(n) + O(n²) = O(n²)  ← 取最高阶
```

### 三种情况

```python
def search(lst, target):
    """在列表中查找目标值"""
    for i, val in enumerate(lst):
        if val == target:
            return i
    return -1

# 最好情况：O(1)   —— 第一个就找到了
# 平均情况：O(n/2) = O(n) —— 平均在中间找到
# 最坏情况：O(n)   —— 最后一个才找到，或根本没有
# 通常说的复杂度指最坏情况
```

---

## 2.4 Python 内置操作的复杂度

### ⭐ 列表操作复杂度（必须记住！）

```python
lst = [1, 2, 3, 4, 5]

# O(1) 操作 —— 快
lst[2]          # 按索引访问
lst[-1]         # 末尾访问
lst.append(6)   # 末尾追加
lst.pop()       # 末尾删除
len(lst)        # 获取长度

# O(n) 操作 —— 慢
lst.insert(0, 0)   # 头部插入（要移动所有元素）
lst.pop(0)         # 头部删除（要移动所有元素）
lst.remove(3)      # 查找并删除（要先线性查找）
3 in lst           # 成员检查（要逐一比较）
lst.index(3)       # 查找索引（线性扫描）
lst.reverse()      # 翻转（遍历一遍）
```

### ⭐ 字典操作复杂度

```python
d = {'a': 1, 'b': 2}

# O(1) 平均 —— 基于哈希表
d['a']           # 按键访问
d['c'] = 3       # 插入
del d['a']       # 删除
'a' in d         # 成员检查 ← 这是字典比列表快的关键！
```

### 对比实验

```python
import timeit

# 测试：在列表 vs 字典中做成员检查
def test_list_membership():
    lst = list(range(10000))
    return 9999 in lst    # O(n)：最坏情况要比较10000次

def test_dict_membership():
    d = {i: i for i in range(10000)}
    return 9999 in d      # O(1)：哈希直接定位

# timeit 测量（单位：秒）
list_time = timeit.timeit(test_list_membership, number=1000)
dict_time = timeit.timeit(test_dict_membership, number=1000)

print(f"列表成员检查: {list_time:.4f}s")
print(f"字典成员检查: {dict_time:.4f}s")
# 字典通常快 100~1000 倍！
```

---

## 2.5 典型代码的复杂度分析练习

```python
# ---- 示例1：O(log n) —— 折半查找规律 ----
def count_halvings(n):
    """n每次除以2，多少次到1？→ log₂n 次"""
    count = 0
    while n > 1:
        n = n // 2
        count += 1
    return count

# n=8:   8→4→2→1，共3次 = log₂8
# n=1024: 共10次 = log₂1024

# ---- 示例2：O(n²) —— 检查列表是否有重复 ----
def has_duplicate_slow(lst):
    """暴力双重循环"""
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):   # j从i+1开始避免自比
            if lst[i] == lst[j]:
                return True
    return False

def has_duplicate_fast(lst):
    """利用集合 O(n)"""
    return len(lst) != len(set(lst))  # set去重，若长度变小说明有重复

# ---- 示例3：O(n³) 警告 ----
def triple_loop(n):
    count = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):     # 三重循环 = n³，n=100时就是百万次
                count += 1
    return count
```

---

## 2.6 空间复杂度

时间复杂度关注"跑多久"，空间复杂度关注"用多少内存"。

```python
# O(1) 空间：只用固定数量的变量
def sum_inplace(lst):
    total = 0          # 只有这一个额外变量
    for x in lst:
        total += x
    return total

# O(n) 空间：创建与输入等比例的新结构
def double_all(lst):
    result = []        # 新列表，大小与输入相同
    for x in lst:
        result.append(x * 2)
    return result

# 递归的隐式空间：每次调用占用调用栈
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n - 1)  # 递归深度n → O(n) 栈空间
```

---

## 2.7 本章要点总结

| 概念 | 要点 |
|------|------|
| **大O符号** | 描述增长趋势，忽略常数和低阶项 |
| **最坏情况** | 通常用最坏情况作为算法的复杂度标准 |
| **⭐列表vs字典** | 成员检查：列表O(n)，字典O(1)，优先用字典 |
| **嵌套循环** | k层嵌套 = O(nᵏ)，避免不必要的嵌套 |
| **对数复杂度** | 每次把问题规模减半就是O(log n)，非常理想 |

> **给初学者的建议**：
> 1. 看到代码先问："循环嵌套了几层？" 是判断复杂度的第一直觉。
> 2. 背下列表和字典的操作复杂度——这在面试和实际开发中非常高频。
> 3. 第2章是全书的"度量衡"，后续每学一个算法都要问：它的时间复杂度是多少？为什么？
