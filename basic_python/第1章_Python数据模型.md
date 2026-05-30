# 第1章：Python 数据模型

> **核心思想**：Python 的一致性源于数据模型。特殊方法（双下划线方法，又称"魔法方法"）是连接用户自定义对象与 Python 解释器的接口，让自定义类型的行为与内置类型一样自然地融入语言生态。

---

## 目录

1. [知识框架总览](#1-知识框架总览)
2. [什么是 Python 数据模型](#2-什么是-python-数据模型)
3. [案例一：一摞 Python 风格的纸牌](#3-案例一一摞-python-风格的纸牌)
4. [特殊方法是如何使用的](#4-特殊方法是如何使用的)
5. [案例二：模拟数值类型——向量类](#5-案例二模拟数值类型向量类)
6. [`__repr__` vs `__str__`](#6-__repr__-vs-__str__)
7. [自定义类型的布尔值](#7-自定义类型的布尔值)
8. [容器 API：特殊方法与抽象基类](#8-容器-api特殊方法与抽象基类)
9. [特殊方法总览表](#9-特殊方法总览表)
10. [len 为什么不是方法](#10-len-为什么不是方法)
11. [常见误区与陷阱](#11-常见误区与陷阱)

---

## 1. 知识框架总览

```
第1章 Python 数据模型
│
├── 核心概念
│   ├── 特殊方法（双下划线方法 / 魔法方法 / dunder 方法）
│   ├── Python 解释器调用特殊方法，而不是用户直接调用
│   └── 特殊方法让自定义对象融入语言生态（迭代、切片、运算符重载等）
│
├── 最重要的两类特殊方法
│   ├── 表示形式：__repr__、__str__、__format__
│   └── 容器接口：__len__、__getitem__、__contains__
│
├── 数值类型模拟
│   ├── 运算符：__add__、__mul__（正向）
│   ├── 反向运算符：__radd__、__rmul__（交换律）
│   └── 一元运算符：__abs__、__neg__、__bool__
│
├── 容器 ABC 体系
│   ├── Iterable（__iter__）
│   ├── Sized（__len__）
│   ├── Container（__contains__）
│   └── Collection = 以上三者合并（Python 3.6+）
│       ├── Sequence（list、str）
│       ├── Mapping（dict）
│       └── Set（set、frozenset）
│
└── 为什么 len 不是方法
    └── 内置类型直接读取 C 结构体字段，无须方法调用，速度更快
```

---

## 2. 什么是 Python 数据模型

```python
# Python 数据模型（也叫 Python 对象模型）是对语言框架的描述：
# 规范了序列、函数、迭代器、协程、类、上下文管理器等的行为。

# 关键：Python 解释器遇到特殊句法时，会调用对应的特殊方法
# 例如：
obj[key]         # → obj.__getitem__(key)
len(obj)         # → obj.__len__()
obj + other      # → obj.__add__(other)
for item in obj  # → iter(obj) → obj.__iter__() 或 obj.__getitem__(0), [1]...
item in obj      # → obj.__contains__(item)

# 特殊方法的命名规则：
# - 前后都有两个下划线，如 __len__
# - 俗称"双下划线方法"（dunder method）或"魔法方法"（magic method）
# - 用于让自定义类型与 Python 语言特性融合
```

---

## 3. 案例一：一摞 Python 风格的纸牌

> **⚠️ 重点**：仅实现 `__len__` 和 `__getitem__` 两个特殊方法，`FrenchDeck` 就自动支持 `len()`、索引、切片、迭代、`in` 运算符和 `sorted()` 等丰富功能。

```python
import collections

# 使用 namedtuple 创建简单的 Card 类（只有属性，没有方法）
Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck:
    """一摞 52 张扑克牌的实现——只用两个特殊方法。"""

    ranks = [str(n) for n in range(2, 11)] + list('JQKA')  # 点数：2~A
    suits = 'spades diamonds clubs hearts'.split()           # 花色

    def __init__(self):
        # 用列表推导式生成 52 张牌（先按花色，再按点数）
        self._cards = [Card(rank, suit) for suit in self.suits
                       for rank in self.ranks]

    def __len__(self):
        """支持 len(deck)。"""
        return len(self._cards)

    def __getitem__(self, position):
        """支持 deck[0]、deck[-1]、deck[:3]、迭代、in 运算符等。
        
        把操作委托给内部列表 self._cards 的 [] 运算符。
        """
        return self._cards[position]


# ============================================================
# 功能演示（仅 __len__ + __getitem__ 就能实现以下所有功能！）
# ============================================================

deck = FrenchDeck()

# 1. len()
print(len(deck))           # 52

# 2. 索引访问
print(deck[0])             # Card(rank='2', suit='spades')
print(deck[-1])            # Card(rank='A', suit='hearts')

# 3. 切片（委托给 list 的切片）
print(deck[:3])            # 前 3 张
print(deck[12::13])        # 每隔 13 张抽一张（4 张 A）

# 4. 随机选取（无须自己实现，直接用标准库！）
from random import choice
print(choice(deck))        # 随机一张

# 5. 迭代
for card in deck:          # __getitem__ 使其可迭代
    print(card)

# 6. 反向迭代
for card in reversed(deck):
    print(card)

# 7. in 运算符（没有 __contains__ 时，Python 做顺序扫描）
print(Card('Q', 'hearts') in deck)   # True
print(Card('7', 'beasts') in deck)   # False

# 8. 排序（传入自定义排序函数）
suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)

def spades_high(card):
    """扑克牌排序函数：梅花2=0，黑桃A=51。"""
    rank_value = FrenchDeck.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]

for card in sorted(deck, key=spades_high):
    print(card)

# ⚠️ 注意：FrenchDeck 目前是"不可变"的
# 因为没有实现 __setitem__，shuffle(deck) 会报 TypeError
# 解决方案（第13章）：添加 FrenchDeck.__setitem__ = set_card
```

**收获**：
- 通过特殊方法"借用"了 `random.choice`、`reversed`、`sorted` 等标准库函数
- 用户不需要记住 `.size()`、`.length()` 等各种命名，一律使用 `len()`
- `FrenchDeck` 的多数功能来自数据模型和组合模式，而非继承

---

## 4. 特殊方法是如何使用的

### 4.1 解释器调用，而非用户直接调用

```python
# ❌ 不推荐：直接调用特殊方法
my_object.__len__()

# ✅ 推荐：调用对应的内置函数，Python 会调用特殊方法
len(my_object)

# 内置函数除了调用特殊方法，还做了额外的优化：
# - 对内置类型（list、str 等），len() 直接读取 C 结构体中的 ob_size 字段
#   无须方法调用，速度非常快
# - 用户自定义类型才通过 __len__ 方法

# 唯一例外：调用 __init__ 时通常直接调用 super().__init__()
```

### 4.2 特殊方法常由特殊句法隐式触发

```python
# for i in x  →  iter(x) → x.__iter__() 或 x.__getitem__(0), [1]...
# item in x   →  x.__contains__(item)（没有则用迭代）
# x + y       →  x.__add__(y)
# x[i]        →  x.__getitem__(i)
# len(x)      →  x.__len__()
# str(x)      →  x.__str__()
# repr(x)     →  x.__repr__()
# bool(x)     →  x.__bool__()（没有则用 __len__）
```

---

## 5. 案例二：模拟数值类型——向量类

```python
import math


class Vector:
    """简单的二维向量类，演示数值类型特殊方法。

    特殊方法：__repr__、__abs__、__bool__、__add__、__mul__
    """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        """供 repr() 调用，返回开发者友好的表示形式。

        使用 !r 确保区分 Vector(1, 2) 和 Vector('1', '2')。
        格式：Vector(x, y)
        """
        return f'Vector({self.x!r}, {self.y!r})'

    def __abs__(self):
        """支持 abs(v)，计算向量的模（欧几里得长度）。"""
        return math.hypot(self.x, self.y)

    def __bool__(self):
        """支持布尔测试：模为零时为 False，否则为 True。

        用在 if v:、while v:、not v 等布尔上下文中。
        """
        return bool(abs(self))
        # 更高效的写法（不用计算平方根）：
        # return bool(self.x or self.y)

    def __add__(self, other):
        """支持 v1 + v2，返回新向量，不修改操作数。

        中缀运算符的预期行为：创建新对象，不改变运算对象。
        """
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x, y)

    def __mul__(self, scalar):
        """支持 v * 3（标量积），返回新向量。

        注意：不支持 3 * v（需要 __rmul__，见第16章）。
        """
        return Vector(self.x * scalar, self.y * scalar)


# ============================================================
# 测试
# ============================================================

v1 = Vector(2, 4)
v2 = Vector(2, 1)
print(v1 + v2)     # Vector(4, 5)

v = Vector(3, 4)
print(abs(v))      # 5.0  → 调用 __abs__

print(v * 3)       # Vector(9, 12)
print(abs(v * 3))  # 15.0

# 布尔值测试
print(bool(Vector(0, 0)))  # False（模为零）
print(bool(Vector(1, 0)))  # True
if v:
    print('v is truthy')   # 打印出来

# 字符串表示
v3 = Vector(1, 2)
print(repr(v3))    # Vector(1, 2)  → 调用 __repr__
print(str(v3))     # Vector(1, 2)  → 没有 __str__，退而用 __repr__
```

---

## 6. `__repr__` vs `__str__`

> **⚠️ 重点**：如果必须二选一，实现 `__repr__`，因为 Python 在没有 `__str__` 时会用 `__repr__`，反过来则不成立。

```python
class MyObj:
    def __repr__(self):
        return 'MyObj(详细信息，供开发者使用)'

    def __str__(self):
        return 'MyObj(简洁信息，供终端用户使用)'


obj = MyObj()

# __repr__ 的调用场景：
repr(obj)          # 显式调用
f'{obj!r}'         # f-string 中的 !r 转换
'%r' % obj         # 旧式格式化中的 %r

# __str__ 的调用场景：
str(obj)           # 显式调用
print(obj)         # print 内部调用 str()
f'{obj}'           # f-string 中不加 !r

# 关键区别：
# __repr__：返回的字符串应该无歧义，最好与源码保持一致
#            方便通过 eval(repr(obj)) 重新创建对象
# __str__：返回对终端用户友好的字符串，可读性优先
```

---

## 7. 自定义类型的布尔值

```python
# Python 中，任何对象都可以在布尔值上下文中使用
# 调用顺序：先找 __bool__，再找 __len__，最后默认为 True

class MyClass:
    def __bool__(self):
        # 必须返回 True 或 False（Python 要求）
        return True   # 或 False

class SizedClass:
    def __len__(self):
        return 0  # 返回 0 则布尔值为 False，否则为 True

# 没有 __bool__ 和 __len__ 的类，实例始终为 True（真值）
class EmptyClass: pass
print(bool(EmptyClass()))  # True

# 向量示例中的 __bool__：
class Vector:
    def __bool__(self):
        return bool(abs(self))  # 模为零则 False

    # 更简洁的方式（避免浮点计算）：
    # def __bool__(self):
    #     return bool(self.x or self.y)
```

---

## 8. 容器 API：特殊方法与抽象基类

> Python 中基本容器类型的层次结构（`collections.abc` 模块）：

```
Iterable（__iter__）       ← 支持 for 循环和拆包
Sized（__len__）           ← 支持 len()
Container（__contains__）  ← 支持 in 运算符

Collection（Python 3.6+）= Iterable + Sized + Container
    │
    ├── Sequence（有序）
    │   ├── 抽象方法：__getitem__、__len__
    │   ├── 继承得到：__contains__、__iter__、__reversed__、index、count
    │   └── 实现：list、tuple、str、bytes、range
    │
    ├── Mapping（键值对）
    │   └── 实现：dict、collections.OrderedDict 等
    │
    └── Set（集合运算）
        └── 实现：set、frozenset
```

```python
# Python 不强制要求继承这些 ABC（抽象基类）
# 只要实现了对应的特殊方法，就满足接口

# 例如，FrenchDeck 没有继承 Sequence，
# 但只要实现了 __len__ 和 __getitem__，就能被当作序列使用

# 用 isinstance 检查接口（而非具体类型）是更好的做法
from collections.abc import Sequence
isinstance([], Sequence)   # True
isinstance((), Sequence)   # True
isinstance("hi", Sequence) # True
```

---

## 9. 特殊方法总览表

### 表1：非运算符特殊方法（常用部分）

| 分类 | 特殊方法 | 触发场景 |
|------|---------|---------|
| **字符串表示** | `__repr__` | `repr(obj)`、交互式控制台 |
| | `__str__` | `str(obj)`、`print(obj)` |
| | `__format__` | `format(obj, spec)`、f-string |
| **转换为数值** | `__bool__` | `bool(obj)`、if/while 等布尔上下文 |
| | `__int__`、`__float__` | `int(obj)`、`float(obj)` |
| | `__hash__` | `hash(obj)`、用作字典键/集合元素 |
| **容器** | `__len__` | `len(obj)` |
| | `__getitem__` | `obj[key]`、迭代（兜底）、切片 |
| | `__setitem__` | `obj[key] = value` |
| | `__delitem__` | `del obj[key]` |
| | `__contains__` | `item in obj` |
| **迭代** | `__iter__` | `iter(obj)`、for 循环 |
| | `__next__` | `next(obj)` |
| | `__reversed__` | `reversed(obj)` |
| **可调用对象** | `__call__` | `obj(args)` |
| **上下文管理** | `__enter__`、`__exit__` | `with obj:` |
| **对象创建** | `__new__` | 类被调用时，先于 `__init__` |
| | `__init__` | 实例初始化 |
| | `__del__` | 对象销毁时 |
| **属性管理** | `__getattr__` | 常规查找失败后的兜底 |
| | `__setattr__` | `obj.attr = value` |
| | `__getattribute__` | 每次属性访问（慎用）|

### 表2：运算符特殊方法（常用部分）

| 运算符 | 特殊方法 | 反向方法 | 就地方法 |
|--------|---------|---------|---------|
| `+` | `__add__` | `__radd__` | `__iadd__` |
| `-` | `__sub__` | `__rsub__` | `__isub__` |
| `*` | `__mul__` | `__rmul__` | `__imul__` |
| `/` | `__truediv__` | `__rtruediv__` | `__itruediv__` |
| `//` | `__floordiv__` | `__rfloordiv__` | `__ifloordiv__` |
| `%` | `__mod__` | `__rmod__` | `__imod__` |
| `**` | `__pow__` | `__rpow__` | `__ipow__` |
| `@` | `__matmul__` | `__rmatmul__` | `__imatmul__` |
| `&` | `__and__` | `__rand__` | `__iand__` |
| `\|` | `__or__` | `__ror__` | `__ior__` |
| `<` | `__lt__` | — | — |
| `<=` | `__le__` | — | — |
| `==` | `__eq__` | — | — |
| `!=` | `__ne__` | — | — |
| `-`（一元）| `__neg__` | — | — |
| `abs()` | `__abs__` | — | — |

---

## 10. `len` 为什么不是方法

```python
# 问题：为什么是 len(collection) 而不是 collection.len()？

# 答：实用胜过纯粹（出自《Python之禅》）

# 原因1：内置类型的速度优化
# - 对 list、str 等 C 语言实现的内置类型，len() 直接读取 PyVarObject 结构体中
#   的 ob_size 字段，无须方法调用，极快
# - 用户自定义类则通过 __len__ 方法调用

# 原因2：保持语言一致性（"特殊情况不是打破规则的理由"）
# - 借助 __len__，len() 对内置类型和自定义类型都适用
# - 一种句法，两种实现（快速路径 + 通用路径）

# 比较：
class MyList:
    def __len__(self):
        return 42

print(len(MyList()))   # 42  → 通过 __len__
print(len([1, 2, 3]))  # 3   → 直接读 C 结构体，更快
```

---

## 11. 常见误区与陷阱

### ❌ 误区一：认为特殊方法应该直接调用

```python
# ❌ 直接调用特殊方法
my_list.__len__()

# ✅ 通过内置函数调用（内置函数会做额外优化）
len(my_list)
```

### ❌ 误区二：只实现 `__str__` 而不实现 `__repr__`

```python
class Bad:
    def __str__(self):
        return '用户友好的字符串'
    # 没有 __repr__

obj = Bad()
repr(obj)      # '<__main__.Bad object at 0x...>'  ← 毫无信息
f'{obj!r}'     # '<__main__.Bad object at 0x...>'  ← 调试不友好

# ✅ 实现 __repr__（如果只能实现一个，选 __repr__）
class Good:
    def __repr__(self):
        return 'Good(详细描述)'  # 既用于 repr()，也在没有 __str__ 时用于 str()
```

### ❌ 误区三：`__bool__` 忘记返回布尔值

```python
# ❌ 返回了非布尔值
class Bad:
    def __bool__(self):
        return 0  # 返回 int，不是 bool

# ✅ 必须用 bool() 显式转换
class Good:
    def __bool__(self):
        return bool(abs(self))  # ← 用 bool() 转换
```

### ❌ 误区四：以为 `in` 运算符只能通过 `__contains__` 实现

```python
class MySeq:
    def __getitem__(self, i):
        if i < 3: return i
        raise IndexError

s = MySeq()
print(1 in s)   # True！Python 通过顺序扫描 __getitem__ 实现 in
# 有 __contains__ 时用它，没有则用迭代扫描，无须显式实现
```

---

*整理自《流畅的Python（第2版）》第1章 | 知识点覆盖：1.2-1.6*
