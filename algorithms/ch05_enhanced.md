# 第5章：排序与搜索

> **本章导读**：排序和搜索是算法世界的"基础设施"，几乎所有复杂算法的内部都依赖它们。本章的学习重点不是死记算法代码，而是理解每种算法**背后的思维模式**：顺序搜索的线性扫描、二分搜索的折半排除、哈希的直接映射、归并的分治合并、快排的分区策略……理解了模式，面对变体题目才能举一反三。
>
> **学习路径**：搜索（顺序→二分→哈希）→ 简单排序（冒泡→选择→插入）→ 高效排序（归并→快速）→ 算法对比与选择
>
> **核心问题**：为什么需要这么多种排序算法？——因为没有"万能最优"的排序，不同场景（数据规模、是否几乎有序、是否需要稳定性、内存是否受限）有不同的最优选择。

---

## 5.0 关键术语速查

| 术语 | 英文 | 定义 |
|------|------|------|
| 顺序搜索 | Sequential Search | 从头到尾逐个比较，直到找到目标或遍历完毕 |
| 二分搜索 | Binary Search | 在有序序列中每次排除一半搜索范围，O(log n) |
| 哈希 | Hashing | 用哈希函数把键直接映射到存储位置，实现 O(1) 查找 |
| 哈希函数 | Hash Function | 将任意键转换为固定范围整数（槽位索引）的函数 |
| 哈希冲突 | Hash Collision | 两个不同的键被哈希函数映射到同一槽位 |
| 线性探测 | Linear Probing | 冲突时顺序向后查找下一个空槽 |
| 链地址法 | Chaining | 冲突时在同一槽位用链表存储多个元素 |
| 装载因子 | Load Factor | 已存元素数 / 槽位总数，影响哈希表性能 |
| 稳定排序 | Stable Sort | 排序后相等元素的相对顺序与排序前保持一致 |
| 原地排序 | In-place Sort | 排序过程中只使用 O(1) 额外空间 |
| 冒泡排序 | Bubble Sort | 相邻元素两两比较交换，最大值"冒泡"到末尾 |
| 选择排序 | Selection Sort | 每轮从未排序部分选出最小值放到正确位置 |
| 插入排序 | Insertion Sort | 将元素逐个插入已排序部分的正确位置 |
| 归并排序 | Merge Sort | 分治思想：分成两半分别排序，再合并 |
| 快速排序 | Quick Sort | 选基准（pivot）分区，递归排两侧 |
| 基准值 | Pivot | 快速排序中用于分区的参考元素 |
| 分区 | Partition | 快速排序中将数组分为"小于pivot"和"大于pivot"两部分 |
| Timsort | Timsort | Python 内置的混合排序（归并+插入），O(n log n) |

---

## 5.1 搜索算法：从 O(n) 到 O(1)

### 5.1.1 顺序搜索——最直觉的方案

```
场景：在一堆乱序的书里找某本书
方案：从第一本开始翻，一本一本看，直到找到
代价：最坏情况要翻所有的书 → O(n)
```

```python
def sequential_search(lst, target):
    """
    顺序搜索（线性搜索）
    
    适用场景：
    ✅ 数据无序时（没有更好的选择）
    ✅ 数据量很小时（简单直接）
    ❌ 数据量大且需要频繁查找时（太慢）
    
    时间复杂度：
    - 最好：O(1)   第一个就找到
    - 平均：O(n/2) ≈ O(n)  平均要比较一半
    - 最坏：O(n)   最后一个才找到，或根本不存在
    空间复杂度：O(1)
    """
    for i in range(len(lst)):
        if lst[i] == target:
            return i     # 找到，返回索引
    return -1            # 未找到，返回-1（约定俗成）


# 小优化：如果列表已排序，可以提前退出
def sequential_search_sorted(lst, target):
    """
    有序列表的顺序搜索：遇到比 target 大的就停止
    最坏仍是 O(n)，但平均情况更快（不需要遍历到末尾）
    """
    for i in range(len(lst)):
        if lst[i] == target:
            return i
        if lst[i] > target:    # 有序：后面的只会更大，目标不存在
            return -1
    return -1
```

---

### 5.1.2 ⭐ 二分搜索——每次排除一半

#### 为什么二分这么快？

```
假设有 1024 个有序元素：

顺序搜索：最坏需要比较 1024 次
二分搜索：每次排除一半
  第1次比较后：512 个候选
  第2次比较后：256 个候选
  第3次比较后：128 个候选
  ...
  第10次比较后：1 个候选  → log₂(1024) = 10 次！

数据量翻倍（2048个），顺序搜索多1024次，二分搜索只多1次！
这就是 O(log n) 的威力。
```

#### 核心思路与边界分析

```
维护搜索区间 [left, right]（闭区间）

每次取中间位置 mid = (left + right) // 2：
  - lst[mid] == target → 找到！返回 mid
  - lst[mid] < target  → 目标在右半，left = mid + 1
  - lst[mid] > target  → 目标在左半，right = mid - 1

循环终止条件：left > right（区间为空，目标不存在）

⚠️ 关键边界：
  - left <= right（注意有等号，left==right时区间还有一个元素）
  - left = mid + 1（不是 mid，否则死循环）
  - right = mid - 1（不是 mid，否则死循环）
```

```python
def binary_search(lst, target):
    """
    二分搜索（迭代版，推荐）
    
    前提：lst 必须已排序（升序）
    时间：O(log n)
    空间：O(1)
    
    执行流程示例（lst=[2,5,8,12,16,23,38,56,72,91], target=23）：
    
    初始：left=0, right=9
    
    第1轮：mid=(0+9)//2=4, lst[4]=16 < 23  → 目标在右半，left=5
    第2轮：mid=(5+9)//2=7, lst[7]=56 > 23  → 目标在左半，right=6
    第3轮：mid=(5+6)//2=5, lst[5]=23 == 23 → 找到！返回5
    
    共3次比较，比顺序搜索的6次少一半。
    """
    left, right = 0, len(lst) - 1
    
    while left <= right:             # 区间非空时继续
        mid = (left + right) // 2    # 取中间位置（向下取整）
        
        if lst[mid] == target:
            return mid               # 命中，返回索引
        elif lst[mid] < target:
            left = mid + 1           # 目标在右半，左边界右移
        else:
            right = mid - 1          # 目标在左半，右边界左移
    
    return -1   # left > right，区间为空，目标不存在


def binary_search_recursive(lst, target, left=0, right=None):
    """
    二分搜索（递归版）
    更清晰地体现"每次把问题规模减半"的分治思想
    
    时间：O(log n)
    空间：O(log n)（递归调用栈深度）
    """
    if right is None:
        right = len(lst) - 1
    
    # 基本情况：区间为空，未找到
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    if lst[mid] == target:
        return mid
    elif lst[mid] < target:
        return binary_search_recursive(lst, target, mid + 1, right)
    else:
        return binary_search_recursive(lst, target, left, mid - 1)


# 测试
data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(binary_search(data, 23))    # 5
print(binary_search(data, 50))    # -1（不存在）
print(binary_search(data, 2))     # 0（第一个）
print(binary_search(data, 91))    # 9（最后一个）
```

---

### 5.1.3 ⭐⭐ 哈希搜索——O(1) 的秘密

#### 为什么哈希能做到 O(1)？

二分搜索通过"比较"缩小范围，本质上还是在搜索。
哈希的思路完全不同：**不搜索，直接定位**。

```
类比：图书馆的借书系统

二分搜索 ≈ 在书架上按字母顺序找书：
  先找到中间，比较，缩小范围……最终找到，O(log n)

哈希搜索 ≈ 图书馆系统直接告诉你"这本书在3楼B区22号架"：
  直接走过去取，O(1)

哈希函数 = 图书馆的查询系统（把书名映射到精确位置）
```

#### 哈希函数：键到槽位的映射

```python
# 最简单的哈希函数：取余法
def hash_func(key, table_size):
    return key % table_size

# 示例：table_size = 11，插入以下键
keys = [54, 26, 93, 17, 77, 31]
table_size = 11

print("键 → 槽位：")
for k in keys:
    slot = hash_func(k, table_size)
    print(f"  {k} → {slot}")
# 54 → 10
# 26 → 4
# 93 → 5
# 17 → 6
# 77 → 0
# 31 → 9
#
# 哈希表：
# 槽位:  0   1   2   3   4   5   6   7   8   9   10
# 值  : [77][  ][  ][  ][26][93][17][  ][  ][31][54]
#
# 查找 93：hash(93, 11) = 5，直接访问槽位5，O(1)！
```

#### 哈希冲突：不可避免的问题

```python
# 当两个键映射到同一槽位时，就发生了冲突
# 例：44 % 11 = 0，77 % 11 = 0  → 两者都想放槽位0！

# ── 解决方案1：线性探测（开放地址法）──────────────────────
# 冲突时，顺序向后找下一个空槽
# 缺点：会产生"聚集"（连续占用），影响性能

class HashTableLinearProbing:
    """
    开放地址法（线性探测）哈希表
    
    冲突处理：目标槽位被占 → 依次尝试 +1, +2, +3... 直到找到空槽
    
    装载因子 λ = 已存元素数 / 表大小
    λ 越低 → 冲突越少 → 性能越接近 O(1)
    λ > 0.7 时应扩容（Python dict 在 2/3 时自动扩容）
    """
    def __init__(self, size=11):
        self.size = size
        self.slots = [None] * size    # 存储键
        self.data  = [None] * size    # 存储值（与slots一一对应）
    
    def _hash(self, key):
        """主哈希函数：取余"""
        return hash(key) % self.size
    
    def _rehash(self, old_slot):
        """线性探测：向右移一位（循环）"""
        return (old_slot + 1) % self.size
    
    def put(self, key, value):
        """
        插入键值对
        
        执行流程：
        1. 计算目标槽位 slot = hash(key)
        2. 若槽位为空 → 直接放入
        3. 若槽位是同一个键 → 更新值
        4. 若槽位被其他键占用（冲突）→ 线性探测找下一个空槽
        """
        slot = self._hash(key)
        
        if self.slots[slot] is None:
            # 槽位为空，直接放入
            self.slots[slot] = key
            self.data[slot]  = value
        elif self.slots[slot] == key:
            # 键已存在，更新值
            self.data[slot] = value
        else:
            # 冲突：线性探测
            next_slot = self._rehash(slot)
            while self.slots[next_slot] is not None and \
                  self.slots[next_slot] != key:
                next_slot = self._rehash(next_slot)
            self.slots[next_slot] = key
            self.data[next_slot]  = value
    
    def get(self, key):
        """
        查找键对应的值
        
        执行流程（与 put 镜像对称）：
        1. 计算槽位 slot = hash(key)
        2. 若 slots[slot] == key → 命中，返回 data[slot]
        3. 若 slots[slot] 为空 → 键不存在
        4. 若 slots[slot] 是其他键 → 线性探测继续找
        """
        slot = self._hash(key)
        start = slot   # 记录起点，防止绕一圈回来死循环
        
        while self.slots[slot] is not None:
            if self.slots[slot] == key:
                return self.data[slot]   # 找到
            slot = self._rehash(slot)
            if slot == start:            # 绕了一圈，没找到
                break
        return None   # 不存在

    def __setitem__(self, key, value): self.put(key, value)
    def __getitem__(self, key):        return self.get(key)


# ── 解决方案2：链地址法（拉链法）──────────────────────────
# 冲突时，同一槽位用链表（或列表）存储多个元素
# Python 的 dict 实际采用的是类似方案

class HashTableChaining:
    """
    链地址法哈希表
    
    每个槽位存储一个列表（桶），
    冲突元素都追加到同一个桶里
    查找时在桶内线性搜索
    
    平均查找：O(1 + λ)，λ为装载因子
    """
    def __init__(self, size=11):
        self.size = size
        self.buckets = [[] for _ in range(size)]   # 每个槽位是一个列表
    
    def _hash(self, key):
        return hash(key) % self.size
    
    def put(self, key, value):
        slot = self._hash(key)
        bucket = self.buckets[slot]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)   # 键存在，更新
                return
        bucket.append((key, value))         # 键不存在，追加
    
    def get(self, key):
        slot = self._hash(key)
        for k, v in self.buckets[slot]:
            if k == key:
                return v
        return None


# ── Python 内置 dict 是最好的哈希表 ─────────────────────────
d = {}
d['apple'] = 1      # O(1) 插入
d['banana'] = 2
print(d['apple'])   # O(1) 查找
print('apple' in d) # O(1) 成员检查  ← 比列表快得多！
```

#### 为什么字典的成员检查比列表快？

```python
import time

n = 1_000_000
data_list = list(range(n))
data_dict = {i: True for i in range(n)}
target = n - 1   # 最坏情况：查最后一个

# 列表：O(n) 线性扫描
start = time.time()
for _ in range(100):
    _ = target in data_list
print(f"列表查找100次: {time.time()-start:.4f}s")

# 字典：O(1) 哈希定位
start = time.time()
for _ in range(100):
    _ = target in data_dict
print(f"字典查找100次: {time.time()-start:.6f}s")

# 典型结果：列表约 3s，字典约 0.00001s，差距约 300000 倍！
```

---

## 5.2 简单排序：O(n²) 的三兄弟

### 5.2.1 为什么先学 O(n²) 的排序？

O(n²) 的排序在大数据量时太慢，但它们：
1. **思路直觉**，是学习高效排序的基础
2. **对几乎有序的数据**（如插入排序），性能可以退化到 O(n)，Python 的 Timsort 内部就用到了插入排序
3. **代码量小**，面试手写可以快速完成

### 5.2.2 冒泡排序（Bubble Sort）

```
直觉：相邻元素两两比较，大的向后"冒泡"
每轮结束：当轮最大的元素到达它最终的位置

[5, 3, 1, 4, 2]  第1轮冒泡：
比较(5,3)→交换 [3, 5, 1, 4, 2]
比较(5,1)→交换 [3, 1, 5, 4, 2]
比较(5,4)→交换 [3, 1, 4, 5, 2]
比较(5,2)→交换 [3, 1, 4, 2, 5] ← 5 已到正确位置
第2轮范围缩小1……
```

```python
def bubble_sort(lst):
    """
    冒泡排序
    
    时间：O(n²) 最坏/平均；O(n) 最好（已有序时提前退出）
    空间：O(1)（原地排序）
    稳定性：稳定（相等元素不交换，相对顺序不变）
    
    优化点：加 swapped 标志，若某轮无交换说明已有序，提前退出
    """
    n = len(lst)
    for i in range(n - 1):            # 共需 n-1 轮
        swapped = False
        
        for j in range(n - 1 - i):   # 每轮比较次数递减（末尾已排好）
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]   # 交换
                swapped = True
        
        # 优化：如果本轮一次交换都没有，说明已经有序，提前退出
        if not swapped:
            break
    
    return lst

# 最坏情况：完全逆序 [5,4,3,2,1] → 需要 4+3+2+1=10 次比较
# 最好情况：已有序 [1,2,3,4,5] → 只需1轮（swapped=False），O(n)
```

### 5.2.3 选择排序（Selection Sort）

```
直觉：每轮从未排序部分选出最小值，放到已排序部分末尾
与冒泡的区别：冒泡每轮"多次交换"，选择每轮"最多1次交换"

[5, 3, 1, 4, 2]
第1轮：找最小值1，与位置0交换  → [1, 3, 5, 4, 2]
第2轮：从位置1开始找最小值2，与位置1交换 → [1, 2, 5, 4, 3]
第3轮：找最小值3，与位置2交换 → [1, 2, 3, 4, 5]
...
```

```python
def selection_sort(lst):
    """
    选择排序
    
    时间：O(n²) 所有情况（无法提前退出，总要找完剩余最小值）
    空间：O(1)
    稳定性：不稳定（交换可能改变相等元素的相对顺序）
    
    优点：交换次数少（最多 n-1 次），适合交换代价大的场景
    缺点：无法利用数据已有的有序性，最好最坏都是 O(n²)
    """
    n = len(lst)
    for i in range(n - 1):              # i：已排序部分的末尾
        min_idx = i                     # 假设当前位置是最小值
        
        for j in range(i + 1, n):      # 在未排序部分找真正的最小值
            if lst[j] < lst[min_idx]:
                min_idx = j
        
        # 把最小值放到正确位置（如果不在当前位置）
        if min_idx != i:
            lst[i], lst[min_idx] = lst[min_idx], lst[i]
    
    return lst
```

### 5.2.4 ⭐ 插入排序（Insertion Sort）

```
直觉：打牌时整理手牌——抓到一张新牌，从右向左找到它的正确位置插入
已有手牌始终保持有序

[5, 3, 1, 4, 2]
初始"已排序"部分：[5]

抓3：3<5，5向右移，插入3 → [3, 5, 1, 4, 2]
抓1：1<5移，1<3移，插入1 → [1, 3, 5, 4, 2]
抓4：4<5移，4>3，插入4   → [1, 3, 4, 5, 2]
抓2：2<5,4,3移，2>1，插入→ [1, 2, 3, 4, 5]
```

```python
def insertion_sort(lst):
    """
    插入排序
    
    时间：O(n²) 最坏（完全逆序）；O(n) 最好（已有序，每次无需移动）
    空间：O(1)
    稳定性：稳定
    
    ⭐ 关键优势：对"几乎有序"的数据非常高效
    Timsort（Python 内置）在小数组段用插入排序，正是利用这一点
    """
    for i in range(1, len(lst)):
        current = lst[i]     # 当前要插入的元素（新抓的牌）
        j = i - 1
        
        # 从右向左扫描已排序部分，把比 current 大的元素向右移
        while j >= 0 and lst[j] > current:
            lst[j + 1] = lst[j]   # 向右移（不是交换！只有最后才赋值）
            j -= 1
        
        lst[j + 1] = current     # 找到正确位置，插入
    
    return lst

# 注意：插入排序用"移动"而不是"交换"
# 交换需要3次赋值，移动只需要1次，效率更高
```

---

## 5.3 ⭐ 高效排序：O(n log n) 的分治思想

### 从 O(n²) 到 O(n log n)——为什么能更快？

```
简单排序：每次操作只确定1个元素的位置，需要 n 轮 → O(n²)
高效排序：利用"分治"，每次操作让"一半的数据"都向正确方向移动
          → 每层 O(n)，共 O(log n) 层 → O(n log n)
```

### 5.3.1 ⭐⭐ 归并排序（Merge Sort）

#### 核心思想：分治

```
分治三步：
1. 分（Divide）  ：把列表从中间一分为二
2. 治（Conquer） ：递归排好左半和右半
3. 合（Combine） ：把两个有序的半段合并成一个有序列表

关键洞察：合并两个有序列表只需 O(n) 时间（双指针）
         分的层数是 O(log n)（每次减半）
         总时间 = O(log n) 层 × O(n) 合并 = O(n log n)
```

#### 执行流程可视化

```
merge_sort([5, 3, 1, 4, 2])

                [5, 3, 1, 4, 2]
               分↙               ↘分
         [5, 3, 1]               [4, 2]
        分↙       ↘分           分↙    ↘分
      [5, 3]       [1]         [4]      [2]
     分↙    ↘分    ↑             ↑        ↑
    [5]      [3]  基本情况      基本情况  基本情况
     ↑         ↑
  基本情况   基本情况

              开始合并（回溯）

    [5] + [3] → merge → [3, 5]
    [3, 5] + [1] → merge → [1, 3, 5]
    [4] + [2] → merge → [2, 4]
    [1, 3, 5] + [2, 4] → merge → [1, 2, 3, 4, 5]  ✅
```

```python
def merge_sort(lst):
    """
    归并排序
    
    时间：O(n log n) 所有情况（最好最坏相同，非常稳定）
    空间：O(n) 额外空间（合并时需要临时数组）
    稳定性：稳定
    
    ⭐ 特点：
    - 性能非常稳定，不受数据分布影响
    - 适合大数据集、需要稳定排序的场景
    - 是归并外排序（超大文件排序）的基础
    """
    # 基本情况：0或1个元素，已经有序
    if len(lst) <= 1:
        return lst
    
    # 分：从中间切开
    mid = len(lst) // 2
    left  = merge_sort(lst[:mid])    # 递归排序左半
    right = merge_sort(lst[mid:])    # 递归排序右半
    
    # 合：合并两个有序列表
    return _merge(left, right)


def _merge(left, right):
    """
    合并两个有序列表（双指针）
    
    执行流程（left=[1,3,5], right=[2,4]）：
    
    i=0, j=0：left[0]=1 < right[0]=2  → 取1，i=1    result=[1]
    i=1, j=0：left[1]=3 > right[0]=2  → 取2，j=1    result=[1,2]
    i=1, j=1：left[1]=3 < right[1]=4  → 取3，i=2    result=[1,2,3]
    i=2, j=1：left[2]=5 > right[1]=4  → 取4，j=2    result=[1,2,3,4]
    j超出right范围，把left剩余部分[5]直接追加
    result=[1,2,3,4,5]  ✅
    
    时间：O(len(left) + len(right)) = O(n)
    """
    result = []
    i = j = 0
    
    # 双指针：比较两边当前最小值，取较小的放入结果
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:      # 注意：等于时取left，保证稳定性
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # 把剩余部分直接追加（必定有序，且都比已放入的大）
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# 测试
print(merge_sort([5, 3, 1, 4, 2]))    # [1, 2, 3, 4, 5]
print(merge_sort([1]))                 # [1]
print(merge_sort([]))                  # []
```

### 5.3.2 ⭐⭐ 快速排序（Quick Sort）

#### 核心思想：分区（Partition）

```
选一个"基准值"（pivot），把数组分成两部分：
    左边：所有 < pivot 的元素
    右边：所有 > pivot 的元素
    中间：pivot 本身（已在最终位置！）

然后对左右两部分递归快排。

与归并的区别：
  归并：先"平均"地分，合并时做排序工作
  快排：分的时候就做排序工作（分区），合并不需要额外操作
```

#### pivot 选取的重要性

```
极端情况：选到最大或最小值作为 pivot
  [1, 2, 3, 4, 5]，每次选末尾元素
  第1轮：pivot=5，左边[1,2,3,4]，右边[]，pivot在位置4
  第2轮：pivot=4，左边[1,2,3]，右边[]……
  退化成 O(n²)！（每次只排好1个元素）

解决方案：选中间位置或随机位置作为 pivot，
         "三数取中法"（取首、中、尾的中位数）更稳定
```

```python
def quick_sort(lst):
    """
    快速排序（简洁版，适合理解原理）
    
    时间：O(n log n) 平均；O(n²) 最坏（pivot选得差时退化）
    空间：O(log n) 平均（递归调用栈）
    稳定性：不稳定
    
    ⭐ 实践中通常比归并排序快：
    - 常数因子更小（原地操作，缓存友好）
    - 平均情况下表现极好
    - Python 的 sorted() 背后是 Timsort，但 C 实现的 qsort 是快排
    """
    if len(lst) <= 1:
        return lst
    
    pivot = lst[len(lst) // 2]   # 选中间元素为 pivot（避免有序数据退化）
    
    left   = [x for x in lst if x < pivot]    # 小于 pivot 的
    middle = [x for x in lst if x == pivot]   # 等于 pivot 的
    right  = [x for x in lst if x > pivot]    # 大于 pivot 的
    
    # 对左右递归，中间的 pivot 已在正确位置，直接拼接
    return quick_sort(left) + middle + quick_sort(right)


def quick_sort_inplace(lst, low=0, high=None):
    """
    快速排序（原地版，面试常考）
    
    原地分区：不创建新列表，通过交换在原数组内完成分区
    空间：O(log n) 平均（只有递归栈，无额外数组）
    
    分区过程（Lomuto 分区方案）：
    选 lst[high] 为 pivot，i 指向"小于区末尾"
    j 遍历 [low, high-1]：
      lst[j] < pivot → i++，交换 lst[i] 和 lst[j]
    最后交换 lst[i+1] 和 lst[high]（pivot 归位）
    """
    if high is None:
        high = len(lst) - 1
    
    if low >= high:        # 基本情况：区间只有0或1个元素
        return
    
    # 分区：让 pivot 归位，返回其最终位置
    pivot_idx = _partition(lst, low, high)
    
    quick_sort_inplace(lst, low, pivot_idx - 1)    # 排左边
    quick_sort_inplace(lst, pivot_idx + 1, high)   # 排右边


def _partition(lst, low, high):
    """
    Lomuto 分区：选 lst[high] 为 pivot
    
    执行流程（lst=[3,6,8,10,1,2,1], low=0, high=6）：
    pivot = lst[6] = 1
    i = low-1 = -1
    
    j=0: lst[0]=3 >= pivot，跳过
    j=1: lst[1]=6 >= pivot，跳过
    ...
    j=4: lst[4]=1 == pivot（不严格小于），跳过
    j=5: lst[5]=2 >= pivot，跳过
    
    循环结束，交换 lst[i+1]=lst[0] 和 lst[6]=1
    结果：[1, 6, 8, 10, 1, 2, 3]  pivot=1 在索引0 ✅
    """
    pivot = lst[high]
    i = low - 1    # i：小于 pivot 的区域末尾（初始为空区域）
    
    for j in range(low, high):
        if lst[j] < pivot:
            i += 1
            lst[i], lst[j] = lst[j], lst[i]   # 把小的换到左边
    
    # pivot 归位：插到小于区和大于区之间
    lst[i + 1], lst[high] = lst[high], lst[i + 1]
    return i + 1   # 返回 pivot 的最终索引


# 测试
arr = [5, 3, 1, 4, 2]
quick_sort_inplace(arr)
print(arr)   # [1, 2, 3, 4, 5]
```

---

## 5.4 排序算法全面对比

| 算法 | 最好 | 平均 | 最坏 | 空间 | 稳定 | 特点 |
|------|------|------|------|------|------|------|
| 冒泡排序 | O(n) | O(n²) | O(n²) | O(1) | ✅ | 有优化提前退出 |
| 选择排序 | O(n²) | O(n²) | O(n²) | O(1) | ❌ | 交换次数最少 |
| 插入排序 | **O(n)** | O(n²) | O(n²) | O(1) | ✅ | 几乎有序时很快 |
| 归并排序 | O(n log n) | O(n log n) | **O(n log n)** | O(n) | ✅ | 稳定，性能稳定 |
| 快速排序 | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ | 实践最快 |
| **Timsort** | **O(n)** | O(n log n) | O(n log n) | O(n) | ✅ | Python 内置，综合最优 |

> **Python 实际使用**：`sorted()` 和 `list.sort()` 使用 **Timsort**
> = 归并排序 + 插入排序的混合体，利用了插入排序在几乎有序数据上的 O(n) 优势。
> **面试中直接用 `sorted()` 即可，不要手写排序（除非题目明确要求）。**

### 如何选择排序算法？

```
数据量 < 20？
  → 插入排序（常数因子小，对小数组很快）

需要稳定排序（如多字段排序）？
  → 归并排序（稳定且 O(n log n) 有保证）

内存受限（只能 O(1) 额外空间）？
  → 堆排序（O(n log n)，O(1)空间，但常数因子大）

追求平均性能（通用场景）？
  → 快速排序（平均最快，但有退化风险）

数据几乎有序？
  → 插入排序或 Timsort

直接用 Python？
  → 永远用 sorted() / list.sort()，底层 Timsort 已经是最优
```

---

## 5.5 ⭐【面试题实战】

### 面试题1：二分查找（LeetCode 704，Easy）

**题目**：在升序数组中查找目标值，找到返回索引，找不到返回 -1。

```python
def search(nums, target):
    """
    标准二分查找模板
    
    关键点：
    1. 循环条件：left <= right（等号不能丢）
    2. mid 计算：(left + right) // 2（Python无整数溢出，不用担心）
    3. 边界更新：left = mid + 1，right = mid - 1（不含mid，防死循环）
    
    时间：O(log n)，空间：O(1)
    """
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

print(search([-1, 0, 3, 5, 9, 12], 9))   # 4
print(search([-1, 0, 3, 5, 9, 12], 2))   # -1
```

---

### 面试题2：搜索插入位置（LeetCode 35，Easy）

**题目**：在排序数组中找目标值，找到返回索引；未找到，返回其应该插入的位置。

**关键洞察**：二分搜索结束后，`left` 指针恰好停在"第一个 ≥ target 的位置"，这就是插入位置。

```python
def search_insert(nums, target):
    """
    搜索插入位置
    
    核心洞察：
    当 left > right 时循环退出。
    此时 left 恰好是第一个大于 target 的位置，
    即 target 应该插入的位置。
    
    执行流程（nums=[1,3,5,6], target=2）：
    初始：left=0, right=3
    mid=1, nums[1]=3 > 2 → right=0
    mid=0, nums[0]=1 < 2 → left=1
    left(1) > right(0)，退出
    返回 left=1  （target=2 应插入索引1，即[1,2,3,5,6]）✅
    
    执行流程（target=7，比所有元素大）：
    最终 left=4，即末尾位置 ✅
    
    时间：O(log n)，空间：O(1)
    """
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid              # 找到，直接返回
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return left   # 未找到，left 就是插入位置

print(search_insert([1, 3, 5, 6], 5))   # 2（找到）
print(search_insert([1, 3, 5, 6], 2))   # 1（插在3前面）
print(search_insert([1, 3, 5, 6], 7))   # 4（插在末尾）
print(search_insert([1, 3, 5, 6], 0))   # 0（插在开头）
```

> **⚠️ 面试注意点**：这道题考察对二分搜索边界的理解。`left` 在循环结束后的语义是"第一个不小于 target 的位置"，记住这个规律能解决一类"二分查找变体"题目。

---

### 面试题3：合并两个有序数组（LeetCode 88，Easy）

**题目**：两个有序数组 `nums1`（长度 m+n，后 n 位为0）和 `nums2`（长度 n），将 `nums2` 合并到 `nums1`，结果有序。

**暴力**：直接合并后排序 → O((m+n)log(m+n))，没有利用"已有序"的特性。

**优化**：从后往前填（逆向双指针），避免覆盖 nums1 中还未使用的元素。

```python
def merge_sorted_arrays(nums1, m, nums2, n):
    """
    逆向双指针合并有序数组
    
    关键洞察：从大到小填入 nums1 的末尾
    nums1 末尾是空位（0占位），不会覆盖有效元素
    
    执行流程（nums1=[1,2,3,0,0,0], m=3, nums2=[2,5,6], n=3）：
    
    p1=2(nums1[2]=3), p2=2(nums2[2]=6), tail=5
    3 < 6 → 填6到tail=5，p2=1, tail=4   nums1=[1,2,3,0,0,6]
    3 < 5 → 填5到tail=4，p2=0, tail=3   nums1=[1,2,3,0,5,6]
    3 > 2 → 填3到tail=3，p1=1, tail=2   nums1=[1,2,3,3,5,6]（注意这里nums1[3]=3）
    2 == 2→ 填2(nums2)到tail=2，p2=-1  nums1=[1,2,2,3,5,6]
    p2<0，退出
    
    最终：[1,2,2,3,5,6] ✅
    
    时间：O(m+n)，空间：O(1)（原地操作）
    """
    p1 = m - 1      # nums1 有效部分末尾
    p2 = n - 1      # nums2 末尾
    tail = m + n - 1  # 填入位置（从末尾开始）
    
    while p1 >= 0 and p2 >= 0:
        if nums1[p1] > nums2[p2]:
            nums1[tail] = nums1[p1]
            p1 -= 1
        else:
            nums1[tail] = nums2[p2]
            p2 -= 1
        tail -= 1
    
    # 若 nums2 还有剩余，直接填入（nums1 有效部分若有剩余，本就在正确位置）
    while p2 >= 0:
        nums1[tail] = nums2[p2]
        p2 -= 1
        tail -= 1

nums1 = [1, 2, 3, 0, 0, 0]
merge_sorted_arrays(nums1, 3, [2, 5, 6], 3)
print(nums1)   # [1, 2, 2, 3, 5, 6]
```

---

### 面试题4：颜色分类（LeetCode 75，Medium）

**题目**：数组只含 0、1、2，排序使 0 在前，1 在中，2 在后。不能使用内置排序函数，只能一次遍历。

**暴力**：计数排序，两次遍历。O(n) 时间，O(1) 空间，但遍历了两次。

**优化**：三路分区（荷兰国旗问题），一次遍历，O(1) 空间。

```python
def sort_colors(nums):
    """
    荷兰国旗问题（三路快速排序分区思想）
    
    三指针将数组分为四个区域：
    [0, low)     → 全是 0（已排好）
    [low, mid)   → 全是 1（已排好）
    [mid, high]  → 待处理（未探索）
    (high, n-1]  → 全是 2（已排好）
    
    初始：low=0, mid=0, high=n-1（待处理区 = 整个数组）
    
    处理 nums[mid]：
    - nums[mid] == 0 → 与 nums[low] 交换，low++, mid++（0 并入左区）
    - nums[mid] == 1 → mid++（1 并入中区，mid 前进）
    - nums[mid] == 2 → 与 nums[high] 交换，high--（2 并入右区，mid 不动因为换来的未知）
    
    执行流程（[2,0,2,1,1,0]）：
    
    初始：low=0, mid=0, high=5
    nums[0]=2 → 与nums[5]交换 → [0,0,2,1,1,2]，high=4
    nums[0]=0 → 与nums[0]交换（自交换）→ low=1,mid=1
    nums[1]=0 → 与nums[1]交换 → low=2,mid=2
    nums[2]=2 → 与nums[4]交换 → [0,0,1,1,2,2]，high=3
    nums[2]=1 → mid=3
    nums[3]=1 → mid=4
    mid(4) > high(3)，退出
    
    结果：[0,0,1,1,2,2] ✅
    
    时间：O(n)，空间：O(1)，一次遍历
    """
    low, mid, high = 0, 0, len(nums) - 1
    
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:  # nums[mid] == 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
            # 注意：mid 不递增！换来的 nums[mid] 还未处理

nums = [2, 0, 2, 1, 1, 0]
sort_colors(nums)
print(nums)   # [0, 0, 1, 1, 2, 2]
```

> **⚠️ 面试注意点**：处理 `nums[mid] == 2` 时，`mid` 不能递增，因为从 `high` 换来的元素还未经过检查，需要在下一轮处理。这是最容易出错的地方。

---

### 面试题5：数组中的第K个最大元素（LeetCode 215，Medium）

**题目**：找数组中第 k 个最大元素（不是第 k 个不同的元素）。

**思路演进**：

```python
# 暴力：排序后直接取，O(n log n)
def find_kth_largest_v1(nums, k):
    return sorted(nums, reverse=True)[k - 1]

# 优化方案1：最小堆，维护大小为 k 的堆
# 时间 O(n log k)，空间 O(k)
import heapq

def find_kth_largest_v2(nums, k):
    """
    最小堆法：维护一个大小为 k 的最小堆
    
    思路：
    - 堆里始终保留当前见过的最大 k 个数
    - 堆顶是这 k 个数中最小的，即"第 k 大"
    
    执行流程（nums=[3,2,1,5,6,4], k=2）：
    
    插入3：堆=[3]
    插入2：堆=[2,3]（size=k=2，停止增大）
    插入1：1 < 堆顶2，忽略
    插入5：5 > 堆顶2，弹出2，插入5 → 堆=[3,5]
    插入6：6 > 堆顶3，弹出3，插入6 → 堆=[5,6]
    插入4：4 < 堆顶5，忽略
    
    返回堆顶 5 ✅（第2大）
    
    时间：O(n log k)，空间：O(k)
    """
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)   # 弹出最小的，堆里始终是最大的k个
    return heap[0]   # 堆顶是k个最大数里最小的，即第k大


# 优化方案2：快速选择，平均 O(n)
def find_kth_largest_v3(nums, k):
    """
    快速选择算法（快排的变体）
    
    思路：
    快排分区后，pivot 落在最终位置，
    若 pivot 的位置正好是"第k大"的位置，就找到了！
    否则只需递归处理一侧（不像快排两侧都处理）
    
    把"第k大"转化为"降序数组的第k-1个位置"
    即"升序数组的第 n-k 个位置"
    
    时间：O(n) 平均，O(n²) 最坏
    空间：O(1)（原地）
    """
    target_idx = len(nums) - k   # 在升序数组中的目标索引
    
    def partition(left, right):
        pivot = nums[right]
        i = left - 1
        for j in range(left, right):
            if nums[j] <= pivot:
                i += 1
                nums[i], nums[j] = nums[j], nums[i]
        nums[i + 1], nums[right] = nums[right], nums[i + 1]
        return i + 1
    
    def quickselect(left, right):
        if left == right:
            return nums[left]
        pivot_idx = partition(left, right)
        if pivot_idx == target_idx:
            return nums[pivot_idx]          # 恰好是目标位置！
        elif pivot_idx < target_idx:
            return quickselect(pivot_idx + 1, right)  # 只递归右边
        else:
            return quickselect(left, pivot_idx - 1)   # 只递归左边
    
    return quickselect(0, len(nums) - 1)


# 测试
print(find_kth_largest_v2([3, 2, 1, 5, 6, 4], 2))   # 5
print(find_kth_largest_v2([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))   # 4
```

> **⚠️ 面试策略**：
> - 直接排序（O(n log n)）可以作为初始解，先说出来表示理解题意
> - 然后说"可以用最小堆优化到 O(n log k)"
> - 如果面试官追问"能不能更快"，再提快速选择 O(n)
> - 实际面试中，最小堆方案通常就足够了

---

## 5.6 本章要点总结

### 核心概念映射表

| 概念 | 定义 | 时间复杂度 | 适用场景 |
|------|------|-----------|---------|
| **顺序搜索** | 从头到尾逐个比较 | O(n) | 数据无序，数据量小 |
| **二分搜索** | 每次排除一半搜索范围 | O(log n) | 数据有序，高频查找 |
| **哈希搜索** | 直接映射到存储位置 | O(1) 平均 | 键值查找，去重判断 |
| **冒泡排序** | 相邻比较，大值冒泡 | O(n²) | 教学理解 |
| **选择排序** | 每轮选最小值 | O(n²) | 交换代价大的场景 |
| **插入排序** | 逐个插入已排序部分 | O(n²)/O(n) | 几乎有序的数据 |
| **归并排序** | 分治：分半排序后合并 | O(n log n) | 需要稳定排序，大数据 |
| **快速排序** | 分区：pivot 归位后递归 | O(n log n) | 通用场景，实践最快 |

### 搜索算法选择指南

```
数据无序？
  → 只能用顺序搜索 O(n)，或先排序再二分

数据有序，单次查找？
  → 二分搜索 O(log n)

数据无序，但会频繁查找？
  → 先 O(n log n) 排一次序，之后每次 O(log n)，均摊更优

需要 O(1) 查找（键值对）？
  → 直接用 Python dict（哈希表）
```

### 排序算法关键对比

| 维度 | 最优选择 | 说明 |
|------|---------|------|
| 综合最优 | Timsort（`sorted()`）| Python 内置，无需手写 |
| 最稳定性能 | 归并排序 | 所有情况 O(n log n) |
| 最快实践 | 快速排序 | 常数因子小，缓存友好 |
| 几乎有序 | 插入排序 | 最好情况 O(n) |
| 内存受限 | 堆排序 | O(1) 额外空间 + O(n log n) |

### 面试高频考点

| 题目 | 核心思路 | 时间 | 空间 | 难度 |
|------|---------|------|------|------|
| 二分查找 LC704 | 标准模板，left≤right，mid±1 | O(log n) | O(1) | Easy |
| 搜索插入位置 LC35 | 二分结束后 left = 插入位置 | O(log n) | O(1) | Easy |
| 合并有序数组 LC88 | 逆向双指针，从末尾往前填 | O(m+n) | O(1) | Easy |
| 颜色分类 LC75 | 三路分区（荷兰国旗），三指针 | O(n) | O(1) | Medium |
| 第K大元素 LC215 | 最小堆 O(n log k) 或快速选择 O(n) | O(n log k) | O(k) | Medium |

### 二分搜索模板（务必背会）

```python
def binary_search_template(nums, target):
    left, right = 0, len(nums) - 1   # ① 闭区间
    
    while left <= right:              # ② 等号不能丢
        mid = (left + right) // 2     # ③ 向下取整
        
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1            # ④ +1 不能省
        else:
            right = mid - 1           # ⑤ -1 不能省
    
    return -1   # 或 return left（搜索插入位置变体）
```

### 常见陷阱（坑点）

| 陷阱 | 说明 | 解决方法 |
|------|------|---------|
| 二分循环条件漏等号 | `left < right` 会遗漏单元素情况 | 用 `left <= right` |
| 二分边界不含mid | `left = mid`/`right = mid` 可能死循环 | 必须 `mid+1` 和 `mid-1` |
| 哈希表装载因子过高 | 冲突增多，性能下降 | 控制 λ < 0.7，及时扩容 |
| 快排 pivot 选取不当 | 有序数据退化 O(n²) | 选中间位置或随机 pivot |
| 颜色分类 mid 不后移 | 交换来的元素未检查 | nums[mid]==2 时 mid 不递增 |
| 合并数组从前往后 | 会覆盖 nums1 未使用的元素 | 从后往前（逆向双指针）|

---

> **给初学者的学习建议**：
> 1. **二分搜索的模板必须背熟**，每次写完后用边界用例验证：空数组、只有1个元素、target在第一个/最后一个/不存在。
> 2. **排序算法的代码不需要全部背**，理解归并和快排的核心思想（分治 + 合并 / 分区），面试能讲清楚思路和复杂度更重要。
> 3. **哈希表是实战中最常用的结构**：遇到"查找"、"去重"、"计数"类问题，第一反应就是用 dict 或 set。
> 4. **面试写排序**时：说明"Python 有内置 sorted()"→ 对方如要手写，先写归并（思路清晰，模板固定）。
