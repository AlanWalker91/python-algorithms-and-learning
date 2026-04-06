# Python `@singledispatch` 学习笔记

---

## 一、问题背景：Python 没有方法重载

Java 支持方法重载——可以定义同名但参数类型不同的方法，编译器自动选择匹配版本。

Python **没有**这个机制。传统做法只能用 `if/elif` 写：

```python
def htmlize(obj):
    if isinstance(obj, str):
        # 处理字符串
    elif isinstance(obj, int):
        # 处理整数
    elif isinstance(obj, list):
        # 处理列表
    # ... 类型越多，函数越臃肿
```

**两个明显缺点：**

1. 函数随类型增多越来越臃肿，维护困难
2. 外部用户无法在不修改源码的情况下扩展新类型的处理逻辑

---

## 二、解决方案：`functools.singledispatch`

`@singledispatch` 把臃肿的 `if/elif` 拆成**一组独立的小函数**，通过装饰器注册到一个"泛化函数"上。

**核心概念：**

| 术语 | 含义 |
|------|------|
| 泛化函数（generic function） | 根据第一个参数的类型，以不同方式执行相同操作的一组函数 |
| 单分派（single dispatch） | 只根据**第一个参数**的类型来选择调用哪个函数 |
| 多分派（multiple dispatch） | 根据**多个参数**的类型来选择（Python 标准库不直接支持） |

---

## 三、完整代码示例 + 逐段解析

### 导入依赖

```python
from functools import singledispatch
from collections import abc
import fractions
import decimal
import html
import numbers
```

---

### ❶ 基函数（兜底处理器）

```python
@singledispatch
def htmlize(obj: object) -> str:
    content = html.escape(repr(obj))
    return f'<pre>{content}</pre>'
```

- 用 `@singledispatch` 装饰，成为泛化函数的**入口**
- 参数类型标注为 `object`，表示这是**默认处理器**
- 当传入的对象没有匹配到任何注册类型时，走这里
- 逻辑：用 `repr()` 表示对象 → 转义 HTML 特殊字符 → 包在 `<pre>` 标签里

---

### ❷❸ 注册 `str` 类型

```python
@htmlize.register
def _(text: str) -> str:
    content = html.escape(text).replace('\n', '<br/>\n')
    return f'<p>{content}</p>'
```

- 函数名用 `_`，因为**名字不重要**，调用时始终通过 `htmlize()` 进入
- 分派器根据**类型注解 `str`** 自动路由到这里
- 逻辑：转义 HTML → 换行符变 `<br/>` → 包在 `<p>` 标签里

---

### ❹ 注册 `abc.Sequence` 类型（序列）

```python
@htmlize.register
def _(seq: abc.Sequence) -> str:
    inner = '</li>\n<li>'.join(htmlize(item) for item in seq)
    return '<ul>\n<li>' + inner + '</li>\n</ul>'
```

- 使用抽象基类 `abc.Sequence`，所有序列类型（list、tuple 等）都能匹配
- **递归调用** `htmlize` 处理每个元素 → 生成 HTML 无序列表
- 体现了泛化函数的组合能力：每个元素又会被分派到各自的处理器

---

### ❺ 注册 `numbers.Integral` 类型（整数）

```python
@htmlize.register
def _(n: numbers.Integral) -> str:
    return f'<pre>{n} (0x{n:x})</pre>'
```

- 用 `numbers.Integral` 而不是 `int`，覆盖更广的整数类型
- 同时显示十进制和十六进制两种形式

---

### ❻ 注册 `bool` 类型

```python
@htmlize.register
def _(n: bool) -> str:
    return f'<pre>{n}</pre>'
```

- **为什么要单独注册？** 因为 `bool` 是 `int` 的子类
- 如果不单独注册，`True` 会被当成整数处理，显示为 `1 (0x1)`
- 分派器会**优先选择更具体的类型**

---

### ❼ 显式指定类型的写法

```python
@htmlize.register(fractions.Fraction)
def _(x) -> str:
    frac = fractions.Fraction(x)
    return f'<pre>{frac.numerator}/{frac.denominator}</pre>'
```

- 没有用类型注解，而是**把类型直接传给 `register()` 作为参数**
- 两种注册方式效果完全一样，这种适合类型注解不方便写的场景
- 逻辑：显示分数的分子/分母形式

---

### ❽ 一个函数注册多个类型

```python
@htmlize.register(decimal.Decimal)
@htmlize.register(float)
def _(x) -> str:
    frac = fractions.Fraction(x).limit_denominator()
    return f'<pre>{x} ({frac.numerator}/{frac.denominator})</pre>'
```

- **叠加两个 `@register`**，让 `float` 和 `Decimal` 共用同一个处理逻辑
- 逻辑：显示原始值 + 近似分数表示

---

## 四、两种注册方式对比

| 方式 | 代码 | 适用场景 |
|------|------|----------|
| 类型注解（推荐） | `@htmlize.register` + 参数标注类型 | 大多数情况 |
| 显式传参 | `@htmlize.register(SomeType)` | 类型注解不方便时，或一个函数注册多个类型 |

---

## 五、分派优先级

当类型之间存在继承关系时，分派器选择**最具体的匹配**：

```
bool → ❻ bool 处理器（最具体）
int  → ❺ numbers.Integral 处理器
list → ❹ abc.Sequence 处理器
str  → ❷ str 处理器（注意：str 也是 Sequence，但 str 更具体）
dict → ❶ 基函数（兜底）
```

---

## 六、核心优势总结

| 优势 | 说明 |
|------|------|
| **开放扩展** | 任何人可以在自己的模块中用 `@htmlize.register` 为新类型添加处理逻辑，无需修改源码 |
| **解耦** | 每个类型的处理逻辑独立存在，互不干扰 |
| **支持抽象类型** | 可以注册抽象基类（如 `abc.Sequence`、`numbers.Integral`），一次覆盖整个类型族 |
| **支持第三方类型** | 即使类型来自第三方包、无法编辑，也能为其注册专门的处理函数 |
| **符合开放-封闭原则** | 对扩展开放，对修改封闭 |

---

## 七、快速上手模板

```python
from functools import singledispatch

# 1. 定义基函数
@singledispatch
def process(obj):
    """默认处理"""
    return str(obj)

# 2. 注册具体类型（方式一：类型注解）
@process.register
def _(x: int):
    return f"整数: {x}"

@process.register
def _(x: str):
    return f"字符串: {x}"

# 3. 注册具体类型（方式二：显式传参）
@process.register(float)
def _(x):
    return f"浮点数: {x}"

# 4. 使用——始终通过基函数调用
print(process(42))        # → 整数: 42
print(process("hello"))   # → 字符串: hello
print(process(3.14))      # → 浮点数: 3.14
print(process([1, 2, 3])) # → [1, 2, 3]（走默认处理）
```