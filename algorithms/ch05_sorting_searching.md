# 第5章：排序与搜索

> **核心思路**：搜索和排序是算法世界的"基础设施"。本章系统对比各种算法的复杂度，重点揭示"哈希"这一把搜索从O(n)降到O(1)的关键思想。

---

## 5.1 搜索算法

### 5.1.1 顺序搜索（Sequential Search）

```python
def sequential_search(lst, target):
    """
    顺序搜索：从头到尾逐一比较
    
    时间复杂度：
    - 最好：O(1)  第一个就找到
    - 平均：O(n/2) = O(n)
    - 最坏：O(n)  最后一个或不存在
    """
    for i, val in enumerate(lst):
        if val == target:
            return i    # 返回索引
    return -1           # 未找到返回-1
```

### ⭐ 5.1.2 二分搜索（Binary Search）

**前提**：列表必须已排序。

**核心思想**：每次排除一半的搜索范围，每比较一次，问题规模减半 → O(log n)。

```python
def binary_search_iterative(lst, target):
    """
    二分搜索（迭代版）
    
    思路：维护搜索范围 [left, right]
    - 计算中间位置 mid
    - 若 lst[mid] == target：找到！
    - 若 lst[mid] < target：目标在右半部分，left = mid + 1
    - 若 lst[mid] > target：目标在左半部分，right = mid - 1
    """
    left, right = 0, len(lst) - 1
    
    while left <= right:
        mid = (left + right) // 2   # 中间位置
        
        if lst[mid] == target:
            return mid              # 命中
        elif lst[mid] < target:
            left = mid + 1          # 目标在右半
        else:
            right = mid - 1         # 目标在左半
    
    return -1

def binary_search_recursive(lst, target, left=0, right=None):
    """
    二分搜索（递归版）—— 更清晰地体现"分治"思想
    """
    if right is None:
        right = len(lst) - 1
    
    # 基本情况：搜索范围为空
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    if lst[mid] == target:
        return mid
    elif lst[mid] < target:
        return binary_search_recursive(lst, target, mid + 1, right)
    else:
        return binary_search_recursive(lst, target, left, mid - 1)

# 演示
data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(binary_search_iterative(data, 23))   # 5（索引）
print(binary_search_iterative(data, 50))   # -1（未找到）

# 复杂度直觉：n=1024 时，最多只需 log₂(1024)=10 次比较！
```

---

## 5.2 ⭐ 哈希搜索（Hashing）

哈希是将搜索从 O(n) 降到 **O(1)** 的关键技术。

### 核心思想

```
目标：给定一个值，能在O(1)时间内直接定位到它的存储位置

方法：用哈希函数 h(key) 把键映射到数组索引
     存储时：index = h(key)，把值放在 table[index]
     查找时：index = h(key)，直接访问 table[index]
```

### 哈希函数

```python
# 最简单的哈希函数：取余法
def hash_function(key, table_size):
    return key % table_size

# 示例：table_size = 11
keys = [54, 26, 93, 17, 77, 31]
for k in keys:
    print(f"{k} → 位置 {hash_function(k, 11)}")
# 54 → 位置 10
# 26 → 位置 4
# 93 → 位置 5
# 17 → 位置 6
# 77 → 位置 0
# 31 → 位置 9
```

### 冲突处理：线性探测

```python
class HashTable:
    """
    开放地址法（线性探测）哈希表
    
    当发生冲突时（目标位置已被占用），
    依次向后探测，直到找到空位
    """
    
    def __init__(self, size=11):
        self.size = size
        self.slots = [None] * size    # 存储键
        self.data  = [None] * size    # 存储值
    
    def _hash(self, key):
        return hash(key) % self.size  # 用内置hash支持任意键类型
    
    def _rehash(self, old_hash):
        """线性探测：向后移一位"""
        return (old_hash + 1) % self.size
    
    def put(self, key, value):
        """插入键值对"""
        idx = self._hash(key)
        
        if self.slots[idx] is None:
            # 空位，直接放入
            self.slots[idx] = key
            self.data[idx]  = value
        else:
            if self.slots[idx] == key:
                # 键已存在，更新值
                self.data[idx] = value
            else:
                # 冲突：线性探测找下一个空位
                next_idx = self._rehash(idx)
                while self.slots[next_idx] is not None and self.slots[next_idx] != key:
                    next_idx = self._rehash(next_idx)
                
                self.slots[next_idx] = key
                self.data[next_idx]  = value
    
    def get(self, key):
        """查找键对应的值"""
        idx = self._hash(key)
        start = idx                  # 记录起始位置，防止死循环
        
        while self.slots[idx] is not None:
            if self.slots[idx] == key:
                return self.data[idx]
            idx = self._rehash(idx)
            if idx == start:         # 转了一圈，没找到
                break
        
        return None
    
    def __setitem__(self, key, value):
        self.put(key, value)
    
    def __getitem__(self, key):
        return self.get(key)

# 测试
ht = HashTable()
ht['cat'] = 'meow'
ht['dog'] = 'woof'
ht['bird'] = 'tweet'
print(ht['cat'])    # meow
print(ht['fish'])   # None（不存在）
```

### 装载因子与性能

```
装载因子 λ = 已存元素数量 / 表的大小

λ 越低 → 冲突越少 → 性能越接近 O(1)
λ 越高 → 冲突越多 → 性能退化

经验法则：λ < 0.7 时性能良好
超过 0.7 时应该扩容（rehashing）

Python 的 dict 在 λ > 2/3 时自动扩容
```

---

## 5.3 排序算法

### ⭐ 5.3.1 冒泡排序（Bubble Sort）

```python
def bubble_sort(lst):
    """
    冒泡排序
    
    思路：每轮比较相邻元素，把最大的"冒泡"到末尾
    n个元素需要 n-1 轮，每轮减少一次比较
    
    时间：O(n²)  空间：O(1)
    """
    n = len(lst)
    for i in range(n - 1):          # n-1 轮
        swapped = False
        for j in range(n - 1 - i):  # 每轮比较次数递减
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]  # 交换
                swapped = True
        
        # 优化：如果本轮没有交换，说明已经有序，提前退出
        if not swapped:
            break
    
    return lst

# [5,3,1,4,2] 第1轮后：[3,1,4,2,5]（5冒到末尾）
```

### 5.3.2 选择排序（Selection Sort）

```python
def selection_sort(lst):
    """
    选择排序
    
    思路：每轮找出最小元素，放到正确位置
    比冒泡少交换次数，但比较次数相同
    
    时间：O(n²)  空间：O(1)
    """
    n = len(lst)
    for i in range(n - 1):
        # 找第 i 轮的最小值索引
        min_idx = i
        for j in range(i + 1, n):
            if lst[j] < lst[min_idx]:
                min_idx = j
        
        # 把最小值放到正确位置
        lst[i], lst[min_idx] = lst[min_idx], lst[i]
    
    return lst
```

### 5.3.3 插入排序（Insertion Sort）

```python
def insertion_sort(lst):
    """
    插入排序
    
    思路：类似打牌时整理手牌——
    维护一个已排序的前半部分，把新元素插入到正确位置
    
    时间：O(n²) 最坏，O(n) 最好（已有序）
    空间：O(1)
    特点：对几乎有序的数据非常高效
    """
    for i in range(1, len(lst)):
        current = lst[i]    # 当前要插入的元素
        j = i - 1
        
        # 向左移动，为 current 找到合适位置
        while j >= 0 and lst[j] > current:
            lst[j + 1] = lst[j]   # 向右移动
            j -= 1
        
        lst[j + 1] = current       # 插入
    
    return lst
```

### ⭐ 5.3.4 归并排序（Merge Sort）

**分治思想的典范**：把问题分成两半，分别解决，再合并。

```python
def merge_sort(lst):
    """
    归并排序
    
    思路（分治）：
    1. 分：把列表从中间分成两半（递归，直到只有1个元素）
    2. 治：每个单元素子列表天然有序
    3. 合：把两个有序子列表合并成一个有序列表
    
    时间：O(n log n)  ← 分治带来的优势
    空间：O(n)        ← 合并时需要额外空间
    """
    # 基本情况：只有0或1个元素，已经有序
    if len(lst) <= 1:
        return lst
    
    # 分：从中间切开
    mid = len(lst) // 2
    left  = merge_sort(lst[:mid])   # 递归排序左半
    right = merge_sort(lst[mid:])   # 递归排序右半
    
    # 合：合并两个有序列表
    return _merge(left, right)

def _merge(left, right):
    """
    合并两个有序列表
    
    双指针技术：各维护一个指针，比较两边当前最小值，
    把较小的放入结果列表
    """
    result = []
    i = j = 0
    
    # 比较双方最小值，较小的先放入结果
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # 把剩余部分直接追加（必定有序）
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# 递归执行过程（[5,3,1,4,2]）：
# 分：[5,3] [1,4,2]
# 分：[5][3] [1][4,2]
# 分：       [4][2]
# 合：[3,5] [1][2,4]
# 合：[3,5] [1,2,4]
# 合：[1,2,3,4,5]
```

### ⭐ 5.3.5 快速排序（Quick Sort）

```python
def quick_sort(lst):
    """
    快速排序
    
    思路（分治）：
    1. 选一个"基准"元素（pivot）
    2. 把比 pivot 小的放左边，大的放右边（分区）
    3. 对左右两边递归快排
    
    时间：O(n log n) 平均，O(n²) 最坏（pivot选得差）
    空间：O(log n) 平均（递归调用栈）
    特点：常数因子小，实践中通常比归并快
    """
    if len(lst) <= 1:
        return lst
    
    pivot = lst[len(lst) // 2]    # 选中间元素为pivot（避免有序列表退化）
    
    left   = [x for x in lst if x < pivot]   # 比pivot小的
    middle = [x for x in lst if x == pivot]  # 等于pivot的
    right  = [x for x in lst if x > pivot]   # 比pivot大的
    
    return quick_sort(left) + middle + quick_sort(right)

# 注意：上面是教学版（简洁但使用额外空间）
# 原地版本通过交换元素实现，空间更优但代码复杂
```

---

## 5.4 排序算法综合对比

| 算法 | 最好 | 平均 | 最坏 | 空间 | 稳定 | 适用场景 |
|------|------|------|------|------|------|----------|
| 冒泡 | O(n) | O(n²) | O(n²) | O(1) | ✅ | 教学，小数据 |
| 选择 | O(n²) | O(n²) | O(n²) | O(1) | ❌ | 交换代价大时 |
| 插入 | O(n) | O(n²) | O(n²) | O(1) | ✅ | 几乎有序的数据 |
| 归并 | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ | 大数据，需稳定 |
| 快速 | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ | 通用，实践最快 |
| 堆排 | O(n log n) | O(n log n) | O(n log n) | O(1) | ❌ | 内存受限 |

> **Python 实际使用**：`sorted()` 和 `list.sort()` 使用 **Timsort**  
> = 归并排序 + 插入排序的混合，O(n log n)，对真实数据极度优化。

---

## 5.5 本章要点总结

| 概念 | 要点 |
|------|------|
| **二分搜索** | 前提是有序；每次排除一半；O(log n) |
| **⭐ 哈希** | 把键直接映射到位置；平均O(1)；冲突是关键问题 |
| **归并排序** | 分治典范；稳定；O(n log n) 有保证 |
| **快速排序** | 实践最快；pivot选择影响性能 |
| **插入排序** | 对几乎有序数据接近O(n)；Timsort的基础 |

> **给初学者的建议**：
> 1. 二分搜索是高频面试题，务必能手写，注意边界条件（`left <= right`）。
> 2. 哈希的思想极为重要——Python 的 dict/set 都是哈希表，理解它才能写出高效代码。
> 3. 排序算法重点理解归并（分治）和快速（分区），能分析它们的复杂度来源。
