# 第1章：引言

> **核心思路**：建立"抽象"的思维方式——把数据与操作分离，关注"做什么"而非"怎么做"。本章是整本书的哲学基础。

---

## 1.1 什么是计算机科学

计算机科学不只是写代码，它的本质是**研究问题、寻找解决方案、并表达这些方案的过程**。

```
问题 → 抽象建模 → 设计算法 → 编写程序 → 验证结果
```

### ⭐ 核心概念：抽象（Abstraction）

**抽象**是将复杂事物简化为只关注其本质特征的过程。

- **过程抽象**：调用函数时，我们只需知道"函数做什么"，不需要了解内部实现
- **数据抽象**：使用数据时，只关心数据支持哪些操作，不关心底层如何存储

```python
# 例子：math.sqrt() 就是一种过程抽象
import math

result = math.sqrt(16)   # 我们只需知道"它求平方根"
print(result)            # 4.0
# 不需要关心它内部用的是哪种数值算法
```

---

## 1.2 什么是编程

编程是将**算法**（解决问题的步骤）用计算机能理解的语言表达出来。

> **算法**：解决某类问题的有限步骤序列，每一步都必须明确且可执行。

---

## 1.3 Python 基础回顾

### 1.3.1 内置原子数据类型

```python
# ---- 数值类型 ----
x = 42          # int  整数
y = 3.14        # float 浮点数
z = 2 + 3j      # complex 复数

# ---- 布尔类型 ----
flag = True     # bool，只有 True 和 False

# ---- 常用运算符 ----
print(10 // 3)  # 3    整除
print(10 % 3)   # 1    取余
print(2 ** 10)  # 1024 幂运算
```

### 1.3.2 内置集合数据类型

Python 内置了四种集合类型，理解它们的特点是数据结构学习的起点：

| 类型 | 有序 | 可重复 | 可变 | 典型用途 |
|------|------|--------|------|----------|
| `list` 列表 | ✅ | ✅ | ✅ | 通用序列 |
| `tuple` 元组 | ✅ | ✅ | ❌ | 不可变序列 |
| `set` 集合 | ❌ | ❌ | ✅ | 去重、集合运算 |
| `dict` 字典 | ❌（3.7+有序）| ❌(key) | ✅ | 键值映射 |

```python
# ---- 列表 list ----
nums = [1, 2, 3, 4, 5]
nums.append(6)          # 末尾追加：[1,2,3,4,5,6]
nums.insert(0, 0)       # 指定位置插入：[0,1,2,3,4,5,6]
nums.pop()              # 移除并返回末尾元素：6
print(nums[1:4])        # 切片：[1, 2, 3]

# ---- 字典 dict ----
student = {
    'name': 'Alice',
    'score': 95,
    'grade': 'A'
}
student['age'] = 20          # 新增键值对
print(student.get('age', 0)) # 安全获取，默认值为0
for key, val in student.items():  # 遍历键值对
    print(f"{key}: {val}")

# ---- 集合 set ----
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(a & b)   # 交集：{3, 4}
print(a | b)   # 并集：{1, 2, 3, 4, 5, 6}
print(a - b)   # 差集：{1, 2}

# ---- 元组 tuple ----
point = (3, 4)           # 不可变，常用于坐标、返回值
x, y = point             # 元组解包
```

### 1.3.3 控制结构

```python
# ---- 条件语句 ----
score = 85
if score >= 90:
    grade = 'A'
elif score >= 80:
    grade = 'B'
else:
    grade = 'C'

# ---- 循环 ----
# for 循环：已知次数或遍历集合
for i in range(5):        # range(5) = 0,1,2,3,4
    print(i)

# while 循环：条件驱动
n = 10
while n > 0:
    n -= 1

# 列表推导式（List Comprehension）—— Python 特色语法
squares = [x**2 for x in range(10)]           # [0,1,4,9,...,81]
evens   = [x for x in range(20) if x % 2 == 0] # 偶数列表
```

### 1.3.4 函数

```python
def gcd(m, n):
    """
    求最大公约数（辗转相除法）
    
    核心思想：gcd(m, n) = gcd(n, m%n)，直到余数为0
    """
    while n != 0:
        m, n = n, m % n   # 同时赋值，优雅交换
    return m

print(gcd(48, 18))  # 6
```

---

## 1.4 面向对象编程（OOP）初步

### ⭐ 为什么需要类和对象？

当数据和操作紧密相关时，把它们封装在一起更合理。

**例子：用类实现分数（Fraction）**

```python
class Fraction:
    """
    分数类：演示封装、运算符重载
    
    设计思路：
    1. 分数由分子(numerator)和分母(denominator)组成
    2. 始终保持最简形式（约分）
    3. 支持加减乘除和比较运算
    """
    
    def __init__(self, top, bottom):
        """初始化：自动约分"""
        # 处理负号：让分母始终为正
        if bottom < 0:
            top, bottom = -top, -bottom
        
        # 求最大公约数，进行约分
        common = self._gcd(abs(top), bottom)
        self.num = top // common        # 分子
        self.den = bottom // common     # 分母
    
    def _gcd(self, m, n):
        """私有方法：辗转相除法求最大公约数"""
        while n != 0:
            m, n = n, m % n
        return m
    
    def __str__(self):
        """控制 print() 的输出格式"""
        if self.den == 1:
            return str(self.num)
        return f"{self.num}/{self.den}"
    
    def __repr__(self):
        """控制在交互式环境中的显示"""
        return f"Fraction({self.num}, {self.den})"
    
    def __add__(self, other):
        """重载 + 运算符"""
        # a/b + c/d = (a*d + b*c) / (b*d)
        new_num = self.num * other.den + self.den * other.num
        new_den = self.den * other.den
        return Fraction(new_num, new_den)  # 构造函数会自动约分
    
    def __mul__(self, other):
        """重载 * 运算符"""
        return Fraction(self.num * other.num, self.den * other.den)
    
    def __eq__(self, other):
        """重载 == 运算符（交叉相乘比较）"""
        return self.num * other.den == other.num * self.den
    
    def __lt__(self, other):
        """重载 < 运算符"""
        return self.num * other.den < other.num * self.den


# 使用示例
f1 = Fraction(1, 2)   # 1/2
f2 = Fraction(1, 3)   # 1/3
f3 = Fraction(2, 4)   # 自动约分 → 1/2

print(f1 + f2)         # 5/6
print(f1 * f2)         # 1/6
print(f1 == f3)        # True（1/2 == 2/4）
print(sorted([f2, f1, Fraction(1,4)]))  # 利用 __lt__ 排序
```

---

## 1.5 本章要点总结

| 概念 | 要点 |
|------|------|
| **抽象** | 关注"做什么"，隐藏"怎么做"的细节 |
| **ADT** | 抽象数据类型：定义数据 + 可执行操作的契约 |
| **类与对象** | 数据与操作的封装单元 |
| **运算符重载** | 让自定义类像内置类型一样使用 |

> **给初学者的建议**：本章的分数类例子值得反复研究。它展示了从"需求→设计→实现→测试"的完整过程，是整本书方法论的缩影。
