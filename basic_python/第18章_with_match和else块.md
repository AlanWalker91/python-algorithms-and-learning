# 第18章：with、match 和 else 块

> **核心思想**：`with` 语句保证资源的正确释放；`match/case` 提供强大的结构化模式匹配；`for/while/try` 的 `else` 子句表达"正常结束"的语义，让代码意图更清晰。

---

## 目录

1. [知识框架总览](#1-知识框架总览)
2. [上下文管理器和 with 块](#2-上下文管理器和-with-块)
3. [LookingGlass：自定义上下文管理器](#3-lookingglass自定义上下文管理器)
4. [contextlib 工具包](#4-contextlib-工具包)
5. [@contextmanager 装饰器](#5-contextmanager-装饰器)
6. [案例分析：lis.py 中的模式匹配](#6-案例分析lispy-中的模式匹配)
7. [for/while/try 的 else 块](#7-forwhiletry-的-else-块)
8. [常见误区与陷阱](#8-常见误区与陷阱)

---

## 1. 知识框架总览

```
第18章 with、match 和 else 块
│
├── 上下文管理器（with 语句）
│   ├── 协议：__enter__ + __exit__
│   ├── __enter__：进入 with 块时调用，返回值绑定到 as 子句
│   ├── __exit__：退出 with 块时调用（无论是否发生异常）
│   │   ├── 返回 True → 抑制异常
│   │   └── 返回 False/None → 传播异常
│   └── 嵌套 with（Python 3.10+ 括号风格）
│
├── contextlib 工具
│   ├── @contextmanager  → 用生成器函数创建上下文管理器
│   ├── closing          → 为没有 close 的对象添加 close 方法
│   ├── nullcontext      → 空上下文管理器（测试/条件 with）
│   ├── suppress         → 抑制指定异常
│   ├── AbstractContextManager → 抽象基类
│   └── ExitStack        → 动态组合多个上下文管理器
│
├── 模式匹配（match/case）
│   ├── 字面量模式：case 'quit'
│   ├── 捕获模式：case Point(x, y)
│   ├── 通配符：case _（匹配一切，不绑定）
│   ├── OR 模式：case 'a' | 'b' | 'c'
│   ├── 守卫（guard）：case Point(x, y) if x == y
│   └── 序列/映射/类模式
│
└── for/while/try 的 else 块
    ├── for...else：循环正常结束（没有 break）时执行 else
    ├── while...else：循环正常结束时执行 else
    └── try...else：try 块没有异常时执行 else（应与 except 配合）
```

---

## 2. 上下文管理器和 `with` 块

```python
# =============================================
# 上下文管理器协议：__enter__ 和 __exit__
# =============================================

# ---- with 语句的执行步骤 ----
# 1. 求解 with 表达式，获取上下文管理器对象
# 2. 调用上下文管理器的 __enter__ 方法
# 3. 如果有 as 子句，把 __enter__ 的返回值绑定到 as 变量
# 4. 执行 with 块
# 5. 无论 with 块如何退出（正常/异常），调用 __exit__

# ---- 最常见用法：文件操作 ----

# ❌ 不安全（异常时文件可能不关闭）
f = open('myfile.txt', 'w', encoding='utf-8')
f.write('hello')
f.close()   # 如果 write 抛出异常，close 不会被调用！

# ✅ 安全（with 保证文件一定关闭）
with open('myfile.txt', 'w', encoding='utf-8') as fp:
    fp.write('hello')
# 离开 with 块后，文件自动关闭

# ---- __enter__ 返回值 ----
# as 绑定的是 __enter__ 的返回值，不是上下文管理器本身！
# 对于文件：__enter__ 返回文件对象本身（所以 fp 就是文件）
# 对于某些上下文管理器：__enter__ 返回不同的对象

# ---- __exit__ 参数 ----
# __exit__(self, exc_type, exc_val, exc_tb)
# - exc_type：异常类（无异常则为 None）
# - exc_val：异常实例（无异常则为 None）
# - exc_tb：traceback 对象（无异常则为 None）
# - 返回 True → 抑制异常（with 块外不会看到异常）
# - 返回 False 或 None → 传播异常

# ---- 嵌套 with（Python 3.10+ 支持括号风格）----
with (
    open('input.txt') as fin,
    open('output.txt', 'w') as fout
):
    for line in fin:
        fout.write(line.upper())
```

---

## 3. `LookingGlass`：自定义上下文管理器

```python
import sys


class LookingGlass:
    """自定义上下文管理器示例：在 with 块中把输出反转。

    演示 __enter__/__exit__ 的完整实现。
    """

    def __enter__(self):
        """进入 with 块时调用。

        返回值绑定到 as 子句中的变量。
        """
        self.original_write = sys.stdout.write   # 保存原始的 write 方法

        # 替换 sys.stdout.write 为反转版本
        sys.stdout.write = self.reverse_write
        return 'JABBERWOCKY'   # as 子句的值

    def reverse_write(self, text):
        """反转文本后写入标准输出。"""
        self.original_write(text[::-1])

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出 with 块时调用（无论是否有异常）。

        参数：
            exc_type：异常类型（无异常则为 None）
            exc_val：异常实例（无异常则为 None）
            exc_tb：traceback 对象（无异常则为 None）

        返回：
            True → 抑制异常（with 块外不会看到异常）
            False/None → 传播异常
        """
        sys.stdout.write = self.original_write   # 恢复原始的 write 方法

        if exc_type is ZeroDivisionError:
            print('Please DO NOT divide by zero!')
            return True   # 抑制 ZeroDivisionError

        return False   # 其他异常正常传播


# ---- 使用示例 ----
with LookingGlass() as what:
    print('Alice, Kitty and Snowdrop')   # 输出反转的文本
    print(what)                          # 输出 'YKCOWREBBAJ'

# 离开 with 块后，stdout 恢复正常
print('Back to normal')   # 'Back to normal'（正常输出）

# ---- 验证 as 子句的值 ----
with LookingGlass() as what:
    print(what)              # 'YKCOWREBBAJ'（反转的 'JABBERWOCKY'）
    # what 是 __enter__ 的返回值 'JABBERWOCKY'

monster = 'JABBERWOCKY'
print(monster == 'JABBERWOCKY')   # True（with 块外正常比较）
```

---

## 4. `contextlib` 工具包

```python
import contextlib

# =============================================
# contextlib 提供多种便捷的上下文管理工具
# =============================================

# ---- 1. closing：为没有 close 的对象添加 close 支持 ----
# 适用于实现了 close() 但没有 __enter__/__exit__ 的对象
from contextlib import closing
from urllib.request import urlopen

with closing(urlopen('https://www.python.org')) as page:
    for line in page:
        print(line)
# 无论如何，都会调用 page.close()

# ---- 2. suppress：抑制指定异常 ----
from contextlib import suppress
import os

with suppress(FileNotFoundError):
    os.remove('somefile.tmp')   # 如果文件不存在，不报错

# 等价于：
try:
    os.remove('somefile.tmp')
except FileNotFoundError:
    pass

# ---- 3. nullcontext：空上下文管理器 ----
from contextlib import nullcontext

# 用于条件 with（有时需要上下文管理器，有时不需要）
def process(fp, managed=True):
    ctx = fp if managed else nullcontext(fp)
    with ctx as f:
        return f.read()

# ---- 4. ExitStack：动态组合上下文管理器 ----
from contextlib import ExitStack

# 动态打开不定数量的文件
filenames = ['a.txt', 'b.txt', 'c.txt']
with ExitStack() as stack:
    files = [stack.enter_context(open(fn)) for fn in filenames]
    # 所有文件都在 with 块退出时关闭

# ---- 5. AbstractContextManager：抽象基类 ----
from contextlib import AbstractContextManager

class MyContextManager(AbstractContextManager):
    """只需实现 __enter__，AbstractContextManager 提供默认 __exit__（返回 None）。"""

    def __enter__(self):
        return self
    # 使用默认 __exit__（不抑制异常，直接传播）
```

---

## 5. `@contextmanager` 装饰器

```python
from contextlib import contextmanager

# =============================================
# @contextmanager：用生成器函数创建上下文管理器
# 无须实现 __enter__ 和 __exit__ 方法
# =============================================

@contextmanager
def looking_glass():
    """上下文管理器：在 with 块中把输出反转。

    工作原理：
    - yield 之前的代码 → __enter__（进入 with 块前执行）
    - yield 的值 → as 子句绑定的值
    - yield 之后的代码 → __exit__（退出 with 块后执行）
    """
    import sys
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write    # 进入：替换 write

    try:
        yield 'JABBERWOCKY'             # 产出值给 as 子句，暂停（with 块执行）
    except ZeroDivisionError:
        msg = 'Please DO NOT divide by zero!'
        print(msg)
    finally:
        sys.stdout.write = original_write  # 退出：恢复 write（无论是否异常）


# 使用示例
with looking_glass() as what:
    print('Alice, Kitty and Snowdrop')  # 反转输出
    print(what)                          # 'YKCOWREBBAJ'

print('normal')   # 'normal'（正常输出）


# =============================================
# @contextmanager 的执行机制
# =============================================

# 当 with 语句求解 looking_glass() 时：
# 1. @contextmanager 的 __enter__ 推进生成器到 yield
# 2. yield 的值（'JABBERWOCKY'）绑定到 as 子句
# 3. with 块执行（在 yield 处暂停的生成器等待）
# 4. with 块结束后（不管是否有异常），@contextmanager 的 __exit__ 恢复生成器
#    - 无异常：调用 next(gen)，生成器从 yield 后继续，直到结束
#    - 有异常：调用 gen.throw(exc_type, exc_val, exc_tb)，异常在 yield 处抛出


# ---- 更健壮的实现：始终使用 try/finally ----
@contextmanager
def managed_resource():
    """总是用 try/finally 确保清理代码执行。"""
    resource = acquire_resource()
    try:
        yield resource          # 产出资源给 with 块使用
    finally:
        release_resource(resource)  # 无论如何都释放资源
```

---

## 6. 案例分析：`lis.py` 中的模式匹配

```python
# =============================================
# match/case：结构化模式匹配（Python 3.10+）
# 在 lis.py（Scheme 解释器）中的应用
# =============================================

# ---- 基础：match 表达式 ----
command = 'go north'

match command:
    case 'quit':
        print('退出')
    case 'go north' | 'go south' | 'go east' | 'go west':
        print(f'移动：{command}')
    case _:          # 通配符：匹配一切（必须放最后）
        print(f'未知命令：{command}')


# ---- 序列模式 ----
def evaluate(expr):
    """简化版 Scheme 求值（演示序列模式）。"""
    match expr:
        case ['quote', x]:           # 匹配 ['quote', x] 形式
            return x
        case ['if', test, then, else_]:   # 匹配 4 元素列表
            if evaluate(test):
                return evaluate(then)
            else:
                return evaluate(else_)
        case ['define', str(name), value_expr]:  # 匹配 define，name 必须是 str
            ENVIRONMENT[name] = evaluate(value_expr)
        case [func, *args]:          # 匹配：第一个是函数，其余是参数
            func = evaluate(func)
            args = [evaluate(arg) for arg in args]
            return func(*args)
        case _:
            return expr              # 原子表达式


# ---- 类模式 ----
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

def describe_point(point):
    match point:
        case Point(x=0, y=0):                    # 关键字模式：精确匹配
            print('原点')
        case Point(x=0, y=y_val):                # 关键字 + 捕获
            print(f'Y 轴上，y={y_val}')
        case Point(x=x_val, y=0):
            print(f'X 轴上，x={x_val}')
        case Point(x=x_val, y=y_val):
            print(f'普通点：({x_val}, {y_val})')
        case _:
            print('不是点')


# ---- 守卫（guard）：case 后的 if 条件 ----
def classify_point(point):
    match point:
        case Point(x=x, y=y) if x == y:      # 守卫：x 等于 y
            print(f'在对角线上：({x}, {y})')
        case Point(x=x, y=y) if x > 0 and y > 0:
            print(f'在第一象限：({x}, {y})')
        case Point(x=x, y=y):
            print(f'其他：({x}, {y})')


# ---- OR 模式 ----
def is_valid_direction(direction):
    match direction:
        case 'north' | 'south' | 'east' | 'west':
            return True
        case _:
            return False


# ---- 映射模式 ----
def process_config(config):
    match config:
        case {'action': 'login', 'user': str(username)}:
            print(f'用户 {username} 登录')
        case {'action': 'logout'}:
            print('用户登出')
        case {'action': action, **rest}:   # ** 捕获剩余键
            print(f'未知操作：{action}，其余参数：{rest}')


# ---- lis.py 中的 OR 模式（Scheme 求值）----
def evaluate(exp, env):
    """Scheme 求值函数（使用模式匹配）。"""
    match exp:
        case int(x) | float(x):          # OR 模式：int 或 float
            return x
        case str(var):                    # 变量名（字符串）
            return env[var]
        case ['quote', x]:               # 引用表达式
            return x
        case ['if', test, then, else_]:  # 条件表达式
            if evaluate(test, env):
                return evaluate(then, env)
            else:
                return evaluate(else_, env)
        case ['lambda', [*params], *body]:  # lambda 表达式
            return Procedure(params, body, env)
        case ['define', str(name), value]:  # define 语句
            env[name] = evaluate(value, env)
        case [func, *args]:              # 函数调用
            proc = evaluate(func, env)
            vals = [evaluate(arg, env) for arg in args]
            return proc(*vals)
        case _:
            raise SyntaxError(f'无效的表达式：{exp}')
```

---

## 7. `for`/`while`/`try` 的 `else` 块

```python
# =============================================
# for/while/try 的 else 子句
# 核心语义："正常结束"时执行 else
# 没有 break（for/while）或没有异常（try）才执行
# =============================================

# ---- for...else：未被 break 中断时执行 else ----

# 示例1：在序列中查找元素
def find_in(haystack, needle):
    for item in haystack:
        if item == needle:
            break   # 找到了，不执行 else
    else:
        raise ValueError(f'{needle!r} 不在序列中')
    return item   # 只有 break 后才会执行到这里

# 等价的传统写法（更啰嗦）：
def find_in_old(haystack, needle):
    found = False
    for item in haystack:
        if item == needle:
            found = True
            break
    if not found:
        raise ValueError(f'{needle!r} 不在序列中')
    return item


# 示例2：在序列中搜索（for...else 更清晰地表达意图）
primes = [2, 3, 5, 7, 11, 13]

for n in range(2, 20):
    for p in primes:
        if n % p == 0:    # n 能被 p 整除，不是素数
            break
        if p * p > n:     # p 已经超过 sqrt(n)，n 是素数
            primes.append(n)
            break
    # else: n < p*p 且 n % p != 0 → n 不在此轮检查范围
    # （这里 else 不太直觉，for 循环中通常更常见的是 break 搭配 else）


# ---- while...else：条件变为 False 时执行 else ----
import random

n = 0
while n < 10:
    n = random.randint(0, 20)
    if n == 7:
        print('找到 7，中断')
        break
else:
    print('循环正常结束，没有找到 7')


# ---- try...else：没有异常时执行 else ----

# ✅ 推荐：把可能抛异常的代码放 try，后续处理放 else
# 这样清楚地分离了"可能失败"的操作和"成功后执行"的代码

def process_file(filename):
    try:
        f = open(filename)     # 只有这行可能抛 FileNotFoundError
    except FileNotFoundError:
        print(f'文件不存在：{filename}')
    else:
        # 只有打开成功才执行（没有 FileNotFoundError）
        with f:
            data = f.read()
            print(f'读取了 {len(data)} 字节')
        # 注意：这里的 IOError 不会被 except 捕获！
        # （这正是把处理放在 else 而不是 try 中的好处）

# ❌ 不推荐：把所有代码都放 try 中
def process_file_bad(filename):
    try:
        f = open(filename)         # 可能 FileNotFoundError
        data = f.read()            # 可能 IOError
        print(f'读取了 {len(data)} 字节')
    except FileNotFoundError:
        print(f'文件不存在：{filename}')
        # 问题：如果 f.read() 抛 IOError，也会被这里捕获（不对！）


# ---- else 的语义总结 ----
# for/while...else：没有 break（循环正常结束）→ 执行 else
# try...else：没有异常 → 执行 else
# if/elif/else：这是另一回事（else 的传统含义）

# 助记：把 else 理解为 "no_break" 或 "no_exception"
# for...: ... else: (no_break)...
# while...: ... else: (no_break)...
# try: ... except: ... else: (no_exception)...
```

---

## 8. 常见误区与陷阱

### ❌ 误区一：`as` 子句绑定的是上下文管理器，而不是 `__enter__` 的返回值

```python
# ❌ 误区：with obj as x 中，x 是 obj
with open('file.txt') as f:
    # f 是 open('file.txt').__enter__() 的返回值
    # 对于文件，__enter__ 返回文件对象本身，所以 f 就是文件
    pass

# 但是对于自定义上下文管理器：
class CM:
    def __enter__(self):
        return 'hello'   # __enter__ 返回字符串！

    def __exit__(self, *args):
        pass

with CM() as x:
    print(x)   # 'hello'（不是 CM 实例！）

# ✅ 记住：as 绑定的是 __enter__ 的返回值
# 如果 __enter__ 返回 self，则 as 得到上下文管理器本身
# 如果 __enter__ 返回其他值，则 as 得到那个值
```

### ❌ 误区二：`@contextmanager` 装饰的函数必须只有一个 `yield`

```python
# ❌ 多个 yield 会导致 RuntimeError
from contextlib import contextmanager

@contextmanager
def bad_cm():
    yield 1
    yield 2   # ← 第二个 yield 会引发 RuntimeError

with bad_cm() as x:
    pass   # 离开时：RuntimeError: generator didn't stop

# ✅ @contextmanager 装饰的函数必须恰好有一个 yield
@contextmanager
def good_cm():
    print('进入')
    yield '资源'      # 只有一个 yield
    print('退出')
```

### ❌ 误区三：`__exit__` 返回真值会抑制所有异常

```python
# ❌ 危险：无差别抑制所有异常（连 SystemExit、KeyboardInterrupt 也抑制！）
class DangerousCM:
    def __enter__(self): return self
    def __exit__(self, *args):
        return True   # 抑制所有异常（非常危险！）

with DangerousCM():
    raise SystemExit(1)   # 本应终止程序，但被抑制了！

# ✅ 只抑制特定异常
class SafeCM:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ZeroDivisionError:
            print('捕获：除以零')
            return True   # 只抑制 ZeroDivisionError
        return False      # 其他异常正常传播
```

### ❌ 误区四：`for/while` 的 `else` 含义与 `if/else` 不同

```python
# ⚠️ for...else 的 else 不是"如果循环没有执行"的意思！
# 而是"如果循环没有被 break 中断"

items = []   # 空列表

for item in items:       # 空列表：循环体一次也没执行
    break                # 这个 break 不会执行
else:
    print('else 执行了！')  # 这会执行！（循环正常结束，没有 break）

# 空序列的 for 循环也会执行 else，因为没有 break！
# 如果想检查"循环是否至少执行了一次"，需要用标志变量

found = False
for item in items:
    found = True
    # 处理 item...
if not found:
    print('列表为空')
```

### ❌ 误区五：`try...else` 中的异常不被 `except` 捕获

```python
# ✅ 这正是 else 的优点（有时也是意外陷阱）

try:
    x = int('42')       # 可能 ValueError
except ValueError:
    print('转换失败')
else:
    y = 1 / x           # 如果 x 是 0，会抛 ZeroDivisionError
    # ⚠️ 这里的 ZeroDivisionError 不会被上面的 except ValueError 捕获！
    # 会向上传播，这通常是我们想要的行为

# 如果想捕获 else 中的异常，需要嵌套 try
try:
    x = int('42')
except ValueError:
    print('转换失败')
else:
    try:
        y = 1 / x
    except ZeroDivisionError:
        print('除以零')
```

### ❌ 误区六：`match/case` 的 `case _` 通配符绑定了变量

```python
# ❌ 误区：case _ 会把匹配值绑定到 _ 变量
def process(command):
    match command:
        case 'quit':
            return 'quit'
        case _:
            # _ 是特殊的通配符，匹配一切，但不绑定到变量
            print('未知命令')

# ✅ 如果需要捕获匹配值，用具名变量
def process(command):
    match command:
        case 'quit':
            return 'quit'
        case other:   # 捕获到变量 other（而不是 _）
            print(f'未知命令：{other}')

# 注意：case _ 是通配符（不绑定），case x 是捕获模式（绑定到 x）
```

---

*整理自《流畅的Python（第2版）》第18章 | 知识点覆盖：18.2-18.4*
