# Python 高阶函数、闭包与装饰器 — 完整学习笔记

---

## 一、代码执行流程分析

### 原始代码

```python
registry = []

def register(func):
    print(f'running register({func})')
    registry.append(func)
    return func

@register
def f1():
    print('running f1()')

print('running main()')
print('registry ->', registry)
f1()
```

### 执行顺序（逐步拆解）

```
第1步：registry = []                    → 创建空列表
第2步：def register(func): ...          → 定义 register 函数（仅定义，不执行）
第3步：@register 装饰 f1               → 立刻执行 register(f1)
       ├── 打印 "running register(<function f1 at 0x...>)"
       ├── 把 f1 添加到 registry
       └── 返回 f1（f1 还是原来的 f1）
第4步：print('running main()')          → 打印 "running main()"
第5步：print('registry ->', registry)   → 打印 "registry -> [<function f1 at 0x...>]"
第6步：f1()                             → 调用 f1()，打印 "running f1()"
```

### 输出结果

```
running register(<function f1 at 0x...>)
running main()
registry -> [<function f1 at 0x...>]
running f1()
```

### 核心发现

`register(f1)` 在**模块加载时**就执行了，比 `print('running main()')` 还早。
这就是装饰器的本质——**导入时运行（import time）**，而不是调用时运行（runtime）。

### 这段代码想表达什么

它演示了一个**注册模式**：用装饰器自动把函数收集到一个列表里。

实际应用中非常常见，比如 Web 框架的路由注册：

```python
# Flask 的 @app.route 本质上就是类似的注册机制
@app.route('/login')
def login():
    ...
```

函数定义时自动注册，框架后续就知道哪个 URL 对应哪个函数。

---

## 二、高阶函数

### 定义

高阶函数就是**以函数作为参数**或**以函数作为返回值**的函数。

### 经典例子 1：函数作为参数

```python
# Python 内置的高阶函数

# sorted 的 key 参数接收一个函数
fruits = ['strawberry', 'fig', 'apple', 'cherry', 'banana']
sorted(fruits, key=len)
# → ['fig', 'apple', 'cherry', 'banana', 'strawberry']

# map：对每个元素应用函数
list(map(abs, [-5, -3, 0, 2, 7]))
# → [5, 3, 0, 2, 7]

# filter：用函数筛选元素
list(filter(lambda x: x > 0, [-5, -3, 0, 2, 7]))
# → [2, 7]
```

### 经典例子 2：函数作为返回值

```python
def make_adder(n):
    """返回一个加 n 的函数"""
    def adder(x):
        return x + n
    return adder       # 返回函数，不是调用函数

add_5 = make_adder(5)  # add_5 现在是一个函数
add_5(10)               # → 15
add_5(20)               # → 25
```

### 经典例子 3：同时接收和返回函数

```python
def register(func):       # 接收函数作为参数
    registry.append(func)
    return func            # 返回函数作为返回值
```

---

## 三、闭包

### 定义

闭包是指**一个内层函数记住了它定义时所在外层作用域的变量**，即使外层函数已经执行完毕。

### 闭包的三个条件

1. 存在函数嵌套（外层函数内定义内层函数）
2. 内层函数引用了外层函数的变量
3. 外层函数返回内层函数

### 经典例子 1：计数器

```python
def make_counter():
    count = 0                     # 外层变量

    def counter():
        nonlocal count            # 声明修改外层变量
        count += 1
        return count

    return counter

c = make_counter()
print(c())    # → 1
print(c())    # → 2
print(c())    # → 3
# make_counter 早已执行完毕，但 count 依然存活在闭包中
```

### 经典例子 2：计算移动平均值

```python
def make_averager():
    series = []                   # 外层变量（被闭包记住）

    def averager(new_value):
        series.append(new_value)  # 引用外层变量
        total = sum(series)
        return total / len(series)

    return averager

avg = make_averager()
print(avg(10))    # → 10.0
print(avg(11))    # → 10.5
print(avg(12))    # → 11.0
```

### 经典例子 3：乘法器工厂

```python
def make_multiplier(factor):
    def multiplier(x):
        return x * factor         # factor 被闭包记住
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # → 10
print(triple(5))   # → 15
```

### 查看闭包变量

```python
avg = make_averager()
avg(10)
avg(11)

# 查看闭包捕获的自由变量
print(avg.__code__.co_freevars)   # → ('series',)
print(avg.__closure__[0].cell_contents)  # → [10, 11]
```

### `nonlocal` 关键字

如果闭包需要**修改**（而非仅读取）外层变量，必须用 `nonlocal` 声明：

```python
def make_counter():
    count = 0

    def counter():
        nonlocal count    # 没有这行，count += 1 会报错
        count += 1        # 因为 Python 会把 count 当作局部变量
        return count

    return counter
```

---

## 四、装饰器

### 定义

装饰器是高阶函数的一种**语法糖**，本质是：**把被装饰的函数传给装饰器函数，用返回值替换原函数**。

### 语法糖等价关系

```python
# 写法一：用 @ 语法
@register
def f1():
    print('running f1()')

# 写法二：手动调用（完全等价）
def f1():
    print('running f1()')
f1 = register(f1)
```

---

### 经典例子 1：计时装饰器

```python
import time

def clock(func):
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)        # 调用原函数
        elapsed = time.perf_counter() - t0
        print(f'{func.__name__} 耗时: {elapsed:.4f}s')
        return result
    return wrapper

@clock
def slow_function():
    time.sleep(1)
    return 'done'

slow_function()
# 输出: slow_function 耗时: 1.0012s
```

### 经典例子 2：日志装饰器

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f'调用 {func.__name__}，参数: args={args}, kwargs={kwargs}')
        result = func(*args, **kwargs)
        print(f'{func.__name__} 返回: {result}')
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(3, 5)
# 输出:
# 调用 add，参数: args=(3, 5), kwargs={}
# add 返回: 8
```

### 经典例子 3：权限检查装饰器

```python
current_user = {'name': 'Alice', 'role': 'admin'}

def require_admin(func):
    def wrapper(*args, **kwargs):
        if current_user.get('role') != 'admin':
            raise PermissionError('需要管理员权限')
        return func(*args, **kwargs)
    return wrapper

@require_admin
def delete_user(user_id):
    print(f'删除用户 {user_id}')

delete_user(42)    # 正常执行
# → 删除用户 42
```

### 经典例子 4：缓存装饰器（记忆化）

```python
def cache(func):
    memo = {}                          # 闭包变量，存储缓存

    def wrapper(*args):
        if args not in memo:
            memo[args] = func(*args)   # 未缓存则计算并存储
        return memo[args]

    return wrapper

@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(30))   # → 832040（瞬间完成，无缓存会非常慢）
```

> Python 标准库提供了现成的 `functools.lru_cache`，效果类似。

### 经典例子 5：重试装饰器

```python
import time

def retry(max_attempts=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f'第 {attempt} 次失败: {e}')
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise Exception(f'{func.__name__} 在 {max_attempts} 次尝试后仍然失败')
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unstable_api_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError('连接超时')
    return '成功'
```

---

## 五、带参数的装饰器（三层嵌套）

普通装饰器是两层（装饰器函数 + wrapper），带参数的装饰器需要**三层**：

```
最外层：接收装饰器参数 → 返回真正的装饰器
中间层：接收被装饰的函数 → 返回 wrapper
最内层：wrapper，替换原函数
```

### 经典例子：可配置的日志装饰器

```python
def log(level='INFO'):                    # 第1层：接收参数
    def decorator(func):                  # 第2层：接收函数
        def wrapper(*args, **kwargs):     # 第3层：替换原函数
            print(f'[{level}] 调用 {func.__name__}')
            return func(*args, **kwargs)
        return wrapper
    return decorator

@log(level='DEBUG')       # 先调用 log('DEBUG') → 返回 decorator
def greet(name):          # 再用 decorator 装饰 greet
    print(f'Hello {name}')

greet('Alice')
# 输出:
# [DEBUG] 调用 greet
# Hello Alice
```

### 执行流程拆解

```python
# @log(level='DEBUG') 等价于：
decorator = log(level='DEBUG')   # 第1步：调用外层，得到 decorator
greet = decorator(greet)         # 第2步：用 decorator 装饰 greet
```

---

## 六、`functools.wraps` — 保留原函数信息

装饰器替换函数后，原函数的 `__name__`、`__doc__` 等属性会丢失。
用 `@functools.wraps` 解决：

```python
import functools

def log_calls(func):
    @functools.wraps(func)        # 把 func 的属性复制到 wrapper
    def wrapper(*args, **kwargs):
        print(f'调用 {func.__name__}')
        return func(*args, **kwargs)
    return wrapper

@log_calls
def add(a, b):
    """两数相加"""
    return a + b

# 没有 @wraps 时：
# add.__name__ → 'wrapper'     （丢失了）
# add.__doc__  → None           （丢失了）

# 有 @wraps 时：
# add.__name__ → 'add'          （保留了）
# add.__doc__  → '两数相加'      （保留了）
```

---

## 七、三者的关系总结

```
高阶函数（基础能力）
│  函数可以作为参数传递和返回
│
├── 闭包（记忆机制）
│     内层函数记住外层作用域的变量
│     即使外层函数已执行完毕
│
└── 装饰器（应用模式）
      = 高阶函数 + 闭包 + @ 语法糖
```

| 概念 | 一句话定义 | 核心能力 |
|------|-----------|---------|
| 高阶函数 | 接收函数或返回函数的函数 | 让函数可以像数据一样传递 |
| 闭包 | 记住外层作用域变量的内层函数 | 让函数拥有"记忆" |
| 装饰器 | 在不修改原函数的前提下增强其功能 | 优雅地扩展函数行为 |

不是所有装饰器都用闭包（比如本文开头的 `register` 就没用），但大多数实用的装饰器都会用闭包来包装原函数。

---

## 八、实用速查表

### 装饰器模板

```python
import functools

# 不带参数的装饰器
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 前置逻辑
        result = func(*args, **kwargs)
        # 后置逻辑
        return result
    return wrapper

# 带参数的装饰器
def my_decorator(param1, param2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 可以使用 param1, param2
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
```

### 常用内置装饰器

| 装饰器 | 来源 | 用途 |
|--------|------|------|
| `@property` | 内置 | 把方法变成属性访问 |
| `@staticmethod` | 内置 | 定义静态方法 |
| `@classmethod` | 内置 | 定义类方法 |
| `@functools.wraps` | functools | 保留被装饰函数的元信息 |
| `@functools.lru_cache` | functools | 自动缓存函数结果 |
| `@functools.singledispatch` | functools | 根据参数类型分派（泛化函数） |
| `@dataclasses.dataclass` | dataclasses | 自动生成 `__init__` 等方法 |
| `@abc.abstractmethod` | abc | 定义抽象方法 |

### 多个装饰器的叠加顺序

```python
@decorator_a
@decorator_b
@decorator_c
def my_func():
    pass

# 等价于：
my_func = decorator_a(decorator_b(decorator_c(my_func)))

# 执行顺序：从下往上装饰，从上往下执行
```