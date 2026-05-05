# 第11章：符合 Python 风格的对象

> **核心思想**：实现如此自然的行为，靠的不是继承，而是鸭子类型——只需按照预定行为实现对象所需的方法即可。本章以 `Vector2d` 类为例，系统讲解如何让自定义类型像内置类型一样自然地融入 Python 生态。

---

## 目录

1. [知识框架总览](#1-知识框架总览)
2. [对象表示形式](#2-对象表示形式)
3. [Vector2d 完整实现（逐步演化）](#3-vector2d-完整实现逐步演化)
4. [备选构造函数（@classmethod）](#4-备选构造函数classmethod)
5. [classmethod vs staticmethod](#5-classmethod-vs-staticmethod)
6. [格式化显示（__format__）](#6-格式化显示__format__)
7. [可哈希的 Vector2d（__hash__）](#7-可哈希的-vector2d__hash__)
8. [支持位置模式匹配（__match_args__）](#8-支持位置模式匹配__match_args__)
9. [Python 私有属性和"受保护"的属性](#9-python-私有属性和受保护的属性)
10. [使用 __slots__ 节省内存](#10-使用-__slots__-节省内存)
11. [覆盖类属性](#11-覆盖类属性)
12. [常见误区与陷阱](#12-常见误区与陷阱)

---

## 1. 知识框架总览

```
第11章 符合 Python 风格的对象
│
├── 对象表示形式
│   ├── __repr__：开发者友好（repr/控制台）
│   ├── __str__：用户友好（print/str）
│   ├── __bytes__：字节序列表示
│   └── __format__：格式化微语言
│
├── 备选构造函数
│   └── @classmethod + frombytes()（第一参数是 cls）
│
├── classmethod vs staticmethod
│   ├── classmethod：第一参数是类（cls），常用于备选构造函数
│   └── staticmethod：普通函数，碰巧在类中（不常用）
│
├── 可哈希
│   ├── 同时实现 __hash__ 和 __eq__
│   ├── 基于不可变属性（用 @property 保护）
│   └── 用 hash(tuple(self)) 或 hash(x) ^ hash(y)
│
├── 私有属性
│   ├── __name（双下划线）→ _ClassName__name（名称改写）
│   └── _name（单下划线）→ 约定，不强制
│
└── __slots__
    ├── 节省内存（禁止 __dict__）
    ├── 不适合做继承基类
    └── 每个类都需声明（子类不继承）
```

---

## 2. 对象表示形式

```python
# =============================================
# Python 提供两种字符串表示形式
# =============================================

class Demo:
    def __repr__(self):
        """供 repr()、交互控制台、调试器使用。
        应返回准确无歧义的字符串，最好能 eval() 重建对象。
        """
        return 'Demo()'

    def __str__(self):
        """供 str()、print() 使用。
        应返回用户友好的字符串。
        """
        return '一个 Demo 实例'

obj = Demo()
repr(obj)      # 'Demo()'     → 调用 __repr__
str(obj)       # '一个 Demo 实例' → 调用 __str__
print(obj)     # 一个 Demo 实例  → print 调用 str()
f'{obj!r}'     # 'Demo()'     → !r 强制调用 __repr__
f'{obj}'       # '一个 Demo 实例' → 默认调用 __str__

# ⚠️ 关键原则：
# 如果只能实现一个，选 __repr__！
# 没有 __str__ 时，Python 会用 __repr__
# 反过来则不行（repr 调用 __str__ 没意义）

# 其他表示方法：
# __bytes__：供 bytes() 调用，返回字节序列
# __format__：供 format()、f-string、str.format() 调用
```

---

## 3. Vector2d 完整实现（逐步演化）

```python
from array import array
import math


class Vector2d:
    """二维向量类——完整版（第3版）。

    演示：__repr__、__str__、__bytes__、__eq__、
          __hash__、__bool__、__format__、
          @classmethod frombytes、@property（只读属性）
    """

    typecode = 'd'   # 类属性：用于 __bytes__ 的数组类型码

    def __init__(self, x, y):
        # 用双下划线使 x 和 y 变为私有，防止被子类意外覆盖
        self.__x = float(x)   # ← 名称改写为 _Vector2d__x
        self.__y = float(y)   # ← 名称改写为 _Vector2d__y

    # ---- 只读属性（保护实例变量）----
    @property
    def x(self):
        """x 分量（只读）。"""
        return self.__x

    @property
    def y(self):
        """y 分量（只读）。"""
        return self.__y

    # ---- 支持拆包（让实例可迭代）----
    def __iter__(self):
        return (i for i in (self.x, self.y))

    # ---- 字符串表示 ----
    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self)
        # 等价于：f'{class_name}({self.x!r}, {self.y!r})'

    def __str__(self):
        return str(tuple(self))   # '(3.0, 4.0)'

    # ---- 字节序列 ----
    def __bytes__(self):
        return (bytes([ord(self.typecode)]) +
                bytes(array(self.typecode, self)))

    # ---- 相等性比较 ----
    def __eq__(self, other):
        return tuple(self) == tuple(other)

    # ---- 模（绝对值）----
    def __abs__(self):
        return math.hypot(self.x, self.y)

    # ---- 布尔值 ----
    def __bool__(self):
        return bool(abs(self))

    # ---- 哈希值（可哈希前提：实现 __eq__ + __hash__）----
    def __hash__(self):
        return hash((self.x, self.y))

    # ---- 格式化（见第6节）----
    def __format__(self, fmt_spec=''):
        if fmt_spec.endswith('p'):   # 'p' 后缀：极坐标格式
            fmt_spec = fmt_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{}, {}>'
        else:
            coords = self
            outer_fmt = '({}, {})'
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(*components)

    def angle(self):
        """返回向量角度（弧度）。"""
        return math.atan2(self.y, self.x)

    # ---- 支持位置模式匹配 ----
    __match_args__ = ('x', 'y')

    # ---- 备选构造函数 ----
    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(*memv)


# ---- 使用示例 ----
v1 = Vector2d(3, 4)

# 字符串表示
print(repr(v1))   # Vector2d(3.0, 4.0)
print(str(v1))    # (3.0, 4.0)
print(v1)         # (3.0, 4.0)

# 拆包
x, y = v1
print(x, y)       # 3.0 4.0

# 重建（eval(repr(v)) 应该等于 v）
v1_clone = eval(repr(v1))
print(v1 == v1_clone)   # True

# 字节序列
octets = bytes(v1)
print(octets)     # b'd\x00\x00\x00\x00\x00\x00\x08@\x00\x00...'

# 从字节序列重建
v2 = Vector2d.frombytes(bytes(v1))
print(v2 == v1)   # True

# 格式化
print(format(v1, '.3f'))   # (3.000, 4.000)
print(format(v1, '.3fp'))  # <5.000, 0.927>（极坐标）

# 哈希（可作为字典键）
print(hash(v1))   # 某个整数
d = {v1: '北京'}
print(d[Vector2d(3, 4)])  # '北京'

# 只读属性
print(v1.x)       # 3.0
# v1.x = 0        # AttributeError: can't set attribute
```

---

## 4. 备选构造函数（`@classmethod`）

```python
class Vector2d:
    typecode = 'd'

    # ---- 正常构造函数 ----
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    # ---- 备选构造函数：从字节序列构建 ----
    @classmethod             # ← classmethod 装饰器
    def frombytes(cls, octets):  # ← 第一参数是类（cls），不是实例（self）
        """从字节序列构建 Vector2d 实例。

        @classmethod 的好处：
        - 与正常构造函数签名不同时使用
        - cls 可以是子类，实现多态
        - 标准库中有很多例子：dict.fromkeys()、datetime.fromtimestamp()
        """
        typecode = chr(octets[0])              # 读取类型码
        memv = memoryview(octets[1:]).cast(typecode)  # 转换内存视图
        return cls(*memv)                      # 用 cls 创建实例（而非硬编码 Vector2d）

    def __bytes__(self):
        return (bytes([ord(self.typecode)]) +
                bytes(array(self.typecode, self)))


# 使用示例
v = Vector2d(3, 4)
octets = bytes(v)

# 备选构造函数从字节序列重建对象
v2 = Vector2d.frombytes(octets)
print(v2.x, v2.y)   # 3.0 4.0

# 子类也能用（多态）
class SubVector(Vector2d):
    pass

sub = SubVector.frombytes(octets)
print(type(sub))    # <class '__main__.SubVector'>（而不是 Vector2d！）
```

---

## 5. `classmethod` vs `staticmethod`

```python
class Demo:
    @classmethod
    def klassmeth(*args):
        """类方法：第一个参数始终是类本身（通常命名为 cls）。"""
        return args

    @staticmethod
    def statmeth(*args):
        """静态方法：普通函数，碰巧定义在类中，没有隐式第一参数。"""
        return args


# classmethod 的第一个参数始终是类
print(Demo.klassmeth())           # (<class '__main__.Demo'>,)
print(Demo.klassmeth('spam'))     # (<class '__main__.Demo'>, 'spam')
print(Demo().klassmeth('spam'))   # (<class '__main__.Demo'>, 'spam')（实例调用也一样）

# staticmethod 行为与普通函数完全一样
print(Demo.statmeth())            # ()
print(Demo.statmeth('spam'))      # ('spam',)

# =============================================
# 对比总结
# =============================================
# classmethod：
#   - 第一参数是类（cls）
#   - 主要用途：备选构造函数（fromkeys, frombytes...）
#   - 可以用类名或实例名调用，结果相同
#
# staticmethod：
#   - 没有隐式第一参数
#   - 是普通函数，只是组织在类的命名空间中
#   - 作者观点：不常需要，可用模块级函数替代
```

---

## 6. 格式化显示（`__format__`）

```python
# =============================================
# __format__ 供 format()、f-string、str.format() 调用
# 格式说明符（format_spec）由类自定义解释
# =============================================

# 内置类型的格式化
brl = 1 / 4.82
print(format(brl, '0.4f'))             # '0.2075'
print(f'1 BRL = {1/brl:0.2f} USD')    # '1 BRL = 4.82 USD'
print(format(42, 'b'))                 # '101010'（二进制）
print(format(2/3, '.1%'))              # '66.7%'（百分数）

# 自定义格式微语言
class Vector2d:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __iter__(self):
        return iter((self.x, self.y))

    def angle(self):
        import math
        return math.atan2(self.y, self.x)

    def __abs__(self):
        import math
        return math.hypot(self.x, self.y)

    def __format__(self, fmt_spec=''):
        """自定义格式说明符：
        - 以 'p' 结尾：极坐标格式 <r, θ>
        - 否则：笛卡儿坐标格式 (x, y)，fmt_spec 传给各分量
        """
        if fmt_spec.endswith('p'):
            fmt_spec = fmt_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{}, {}>'
        else:
            coords = self
            outer_fmt = '({}, {})'
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(*components)


v = Vector2d(1, 1)
print(format(v))          # '(1.0, 1.0)'（默认格式）
print(format(v, '.2f'))   # '(1.00, 1.00)'（浮点格式）
print(format(v, '.3e'))   # '(1.000e+00, 1.000e+00)'
print(format(v, 'p'))     # '<1.4142..., 0.7853...>'（极坐标）
print(format(v, '.3fp'))  # '<1.414, 0.785>'
print(f'{v:.2f}')         # '(1.00, 1.00)'（f-string 也走 __format__）
```

---

## 7. 可哈希的 `Vector2d`（`__hash__`）

```python
# =============================================
# 让 Vector2d 可哈希：
# 1. 同时实现 __hash__ 和 __eq__
# 2. 哈希值基于不可变属性
# 3. 把属性变为只读（@property + 私有变量）
# =============================================

class Vector2d:
    def __init__(self, x, y):
        self.__x = float(x)    # 双下划线 → 私有（名称改写）
        self.__y = float(y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __iter__(self):
        return iter((self.x, self.y))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __hash__(self):
        """基于不可变分量的哈希值。
        使用 hash(x) ^ hash(y) 或 hash((x, y))。
        相等的对象必须有相同的哈希值（__eq__ 和 __hash__ 必须一致）。
        """
        return hash((self.x, self.y))
        # 等价写法（对于两个分量）：
        # return hash(self.x) ^ hash(self.y)


v1 = Vector2d(3, 4)
v2 = Vector2d(3, 4)

print(v1 == v2)         # True
print(hash(v1))         # 某个整数
print(hash(v2))         # 与 v1 相同
print(hash(v1) == hash(v2))  # True（相等对象哈希相同）

# 可用作字典键和集合元素
d = {v1: 'point A'}
print(d[v2])            # 'point A'（v2 == v1 且 hash 相同）

s = {v1, v2}
print(len(s))           # 1（相等的对象只存一个）

# ⚠️ 重要规则：
# - 实现了 __eq__ 但没有 __hash__：Python 将 __hash__ 设为 None → 不可哈希
# - 想让对象可哈希：必须同时实现 __hash__ 和 __eq__
# - 哈希值依赖的属性必须是不可变的（否则哈希值变化，作为键时找不到！）
```

---

## 8. 支持位置模式匹配（`__match_args__`）

```python
# =============================================
# __match_args__：为位置类模式匹配指定属性顺序
# Python 3.10+ 新增（但在旧版设置也无害）
# =============================================

class Vector2d:
    __match_args__ = ('x', 'y')   # 位置类模式按此顺序匹配

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


v = Vector2d(1.0, 2.0)

# 位置类模式（依赖 __match_args__）
match v:
    case Vector2d(x, y):           # 按 __match_args__ 顺序：x=1.0, y=2.0
        print(f'x={x}, y={y}')    # x=1.0, y=2.0

# 关键字类模式（不依赖 __match_args__）
match v:
    case Vector2d(x=vx, y=vy):    # 显式指定属性名
        print(f'vx={vx}, vy={vy}')

# 典型用途：在 match/case 中析构自定义对象
vectors = [Vector2d(0, 0), Vector2d(1, 0), Vector2d(0, 1)]
for vec in vectors:
    match vec:
        case Vector2d(0, 0):
            print('原点')
        case Vector2d(x, 0):
            print(f'X 轴上: x={x}')
        case Vector2d(0, y):
            print(f'Y 轴上: y={y}')
        case Vector2d(x, y):
            print(f'普通向量: ({x}, {y})')
```

---

## 9. Python 私有属性和"受保护"的属性

```python
# =============================================
# Python 没有真正的私有属性，但有约定和名称改写机制
# =============================================

class Vector2d:
    def __init__(self, x, y):
        # 双下划线前缀：名称改写（name mangling）
        # __x → _Vector2d__x（防止被子类意外覆盖）
        self.__x = float(x)
        self.__y = float(y)

    @property
    def x(self):
        return self.__x   # 通过属性访问私有变量


v = Vector2d(3, 4)
print(v.x)              # 3.0（通过属性访问）
# v.__x   → AttributeError（在类外直接访问会失败）

# 但可以通过改写后的名称访问（不建议！）
print(v._Vector2d__x)   # 3.0（绕过了保护）

# ---- 名称改写规则 ----
# __name（前缀两个下划线）→ _ClassName__name
# 注意：末尾的双下划线（__name__）不会被改写（这是特殊方法名）


# =============================================
# 单下划线前缀：约定，不强制
# =============================================

class MyClass:
    def __init__(self):
        self._protected = '约定不直接访问，但没有强制'  # 单下划线
        self.__private = '被改写，更难直接访问'          # 双下划线

    def _helper(self):
        """约定为内部方法（但可以从外部调用）。"""
        pass


obj = MyClass()
print(obj._protected)     # 可以访问（只是约定）
# print(obj.__private)    # AttributeError
print(obj._MyClass__private)  # 可以访问（绕过改写）
```

---

## 10. 使用 `__slots__` 节省内存

```python
# =============================================
# __slots__：替代实例的 __dict__，节省内存
# 适用场景：需要创建大量实例，内存严重不足时
# =============================================

class RegularClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class SlottedClass:
    __slots__ = ('x', 'y')   # 声明允许的实例属性

    def __init__(self, x, y):
        self.x = x
        self.y = y


r = RegularClass(1, 2)
s = SlottedClass(1, 2)

# 内存占用对比（一百万个实例）
import tracemalloc
tracemalloc.start()

regular_list = [RegularClass(i, i) for i in range(1_000_000)]
regular_mem = tracemalloc.get_traced_memory()
tracemalloc.reset_peak()

slotted_list = [SlottedClass(i, i) for i in range(1_000_000)]
slotted_mem = tracemalloc.get_traced_memory()

print(f'Regular: {regular_mem[1]/1024/1024:.1f} MB')
print(f'Slotted: {slotted_mem[1]/1024/1024:.1f} MB')
# Regular 通常比 Slotted 多用 30-40% 内存


# ---- __slots__ 的限制 ----
# 1. 不能动态添加未在 __slots__ 中声明的属性
s = SlottedClass(1, 2)
try:
    s.z = 3   # AttributeError：'z' 不在 __slots__ 中
except AttributeError as e:
    print(e)

# 2. 不继承父类的 __slots__（子类默认有 __dict__）
class Parent:
    __slots__ = ('x',)

class Child(Parent):
    pass   # Child 实例仍有 __dict__（因为没有声明 __slots__）

# 3. 含 __slots__ 的类不适合作为基类（原因同上）

# 4. 不能与类的 __weakref__（弱引用支持）同用
#    除非在 __slots__ 中加入 '__weakref__'


# ---- 衡量 __slots__ 节省的内存 ----
import sys

r = RegularClass(1, 2)
s = SlottedClass(1, 2)

# 两者实例大小相近，关键差距在于：
# - regular 有 __dict__，而 dict 本身占用较多内存
# - slotted 直接在对象结构体中存储属性
print(sys.getsizeof(r.__dict__))  # 实例字典的大小
# SlottedClass 实例没有 __dict__
```

---

## 11. 覆盖类属性

```python
# =============================================
# Python 允许通过实例覆盖类属性（创建实例属性）
# 但类属性本身不会改变
# =============================================

class Vector2d:
    typecode = 'd'   # 类属性（所有实例共享）

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __bytes__(self):
        return (bytes([ord(self.typecode)]) +  # 使用 self.typecode
                bytes([int(self.x), int(self.y)]))


v1 = Vector2d(1, 2)
print(v1.typecode)         # 'd'（从类读取）
print(bytes(v1))           # b'd\x01\x02'

# 在实例上覆盖类属性（创建实例属性）
v1.typecode = 'f'          # 只影响 v1 这个实例
print(v1.typecode)         # 'f'（实例属性遮蔽类属性）

v2 = Vector2d(3, 4)
print(v2.typecode)         # 'd'（v2 仍用类属性）

# 修改类属性（影响所有没有实例属性覆盖的实例）
Vector2d.typecode = 'f'
print(v2.typecode)         # 'f'（v2 现在也用 'f' 了）


# ---- 子类继承并覆盖类属性（更 Python 风格的做法）----
class ShortVector2d(Vector2d):
    typecode = 'f'   # 覆盖父类的类属性（单精度浮点）


sv = ShortVector2d(1.0, 1.0)
print(sv.typecode)         # 'f'
print(bytes(sv))           # 字节序列（使用 float 精度）
```

---

## 12. 常见误区与陷阱

### ❌ 误区一：双下划线属性等于"私有"

```python
# ❌ 误区：双下划线属性完全不可访问
class MyClass:
    def __init__(self):
        self.__private = 42

obj = MyClass()
# obj.__private        # AttributeError（看起来私有）
print(obj._MyClass__private)  # 42（实际上可以绕过！）

# 双下划线的真正作用是：防止子类意外覆盖，而不是真正的保密
```

### ❌ 误区二：只实现 `__eq__` 而忘了 `__hash__`

```python
# ❌ 危险：实现了 __eq__ 但没有 __hash__
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    # 没有 __hash__！Python 会自动将 __hash__ 设为 None

p = Point(1, 2)
# hash(p)  → TypeError: unhashable type: 'Point'
# {p}      → TypeError

# ✅ 正确：同时实现两者
class GoodPoint:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))
```

### ❌ 误区三：滥用 `__slots__`

```python
# ❌ 不应该只为了"禁止添加属性"而使用 __slots__
class Rigid:
    __slots__ = ('x', 'y')

# __slots__ 的唯一合理用途是节省内存（大量实例时）
# 否则用 __setattr__ 或 @property 来控制属性访问

# ❌ 误区：以为子类会继承 __slots__ 的限制
class Parent:
    __slots__ = ('x',)

class Child(Parent):
    pass   # 没有声明 __slots__，Child 实例有 __dict__

c = Child()
c.x = 1      # 来自父类的 __slots__
c.z = 99     # 来自自己的 __dict__（不受限制！）
```

### ❌ 误区四：`classmethod` 和 `staticmethod` 混淆

```python
class MyClass:
    count = 0

    @classmethod
    def increment(cls):
        cls.count += 1   # ✅ cls 是类，可以访问类属性

    @staticmethod
    def util():
        # MyClass.count  # 可以，但硬编码了类名
        pass              # 无法通过 cls 动态访问（没有 cls 参数）


# classmethod 是定义备选构造函数的标准方式
# staticmethod 适合组织不依赖类或实例的工具函数
```

---

*整理自《流畅的Python（第2版）》第11章 | 知识点覆盖：11.2-11.13*
