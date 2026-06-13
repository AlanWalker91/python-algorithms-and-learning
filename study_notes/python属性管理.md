# Python 属性管理完整体系

> SDET 面试核心知识点 · 从内置函数到描述符协议的统一视角

---

## 全局地图：所有概念一张表

```
属性管理 = 读 + 写 + 删 + 探测
                │
    ┌───────────┼─────────────┬──────────────┐
    │           │             │              │
  内置函数    property      描述符协议    钩子方法
  ─────────   ────────      ──────────    ────────
  getattr()   .getter()     __get__       __getattr__
  setattr()   .setter()     __set__       __setattr__
  hasattr()   .deleter()    __delete__    __delattr__
  delattr()                 __set_name__  __getattribute__
```

| 层次 | 工具 | 触发时机 | 定义位置 |
|------|------|----------|----------|
| 内置函数 | `getattr` / `setattr` / `hasattr` / `delattr` | 主动调用 | 全局函数，无需定义 |
| `property` | `.getter` / `.setter` / `.deleter` | 装饰器语法糖 | 宿主类内部 |
| 描述符协议 | `__get__` / `__set__` / `__delete__` | 属性被访问/赋值/删除 | **属性所在类**上 |
| 属性钩子 | `__getattr__` / `__setattr__` / `__delattr__` | 属性操作时 | **宿主类**上 |
| 底层拦截 | `__getattribute__` | 每次属性访问，无例外 | **宿主类**上 |

---

## 第一部分：内置函数四件套

### 1.1 `getattr(obj, name[, default])`

```python
# 等价于 obj.name，但 name 是字符串，支持动态访问
# 第三个参数：找不到时的默认值，省略则抛 AttributeError

class Config:
    host = "localhost"
    port = 5432

cfg = Config()

# 基础用法
print(getattr(cfg, 'host'))           # → localhost
print(getattr(cfg, 'missing', None))  # → None（有默认值，不报错）
print(getattr(cfg, 'missing'))        # → AttributeError

# 核心价值：name 可以是变量，实现动态分发
fields = ['host', 'port']
for f in fields:
    print(f"{f} = {getattr(cfg, f)}")
# → host = localhost
# → port = 5432

# SDET 场景：动态调用测试方法
class TestSuite:
    def test_login(self): return "login ok"
    def test_logout(self): return "logout ok"

suite = TestSuite()
for method_name in ['test_login', 'test_logout']:
    method = getattr(suite, method_name)
    print(method())
```

### 1.2 `setattr(obj, name, value)`

```python
# 等价于 obj.name = value，name 是字符串

class DataModel:
    pass

m = DataModel()
setattr(m, 'username', 'Alice')   # 动态设置属性
setattr(m, 'age', 30)
print(m.username)   # → Alice
print(m.__dict__)   # → {'username': 'Alice', 'age': 30}

# SDET 场景：从字典批量初始化对象（测试数据工厂核心）
def build_object(cls, data: dict):
    obj = cls.__new__(cls)
    for key, val in data.items():
        setattr(obj, key, val)
    return obj

user = build_object(DataModel, {"name": "Bob", "role": "admin"})
print(user.name, user.role)   # → Bob admin

# 注意：setattr 会触发 __setattr__ 钩子（若存在）
```

### 1.3 `hasattr(obj, name)`

```python
# 本质是：尝试 getattr，若抛 AttributeError 则返回 False
# 源码等价于：
def hasattr(obj, name):
    try:
        getattr(obj, name)
        return True
    except AttributeError:
        return False

class Service:
    def connect(self): pass

svc = Service()
print(hasattr(svc, 'connect'))     # → True
print(hasattr(svc, 'disconnect'))  # → False

# ⚠️ 陷阱：hasattr 会吞掉非 AttributeError 之外的异常（Python 2 时代问题）
# Python 3 中 hasattr 只捕获 AttributeError，其他异常会透传
class Broken:
    @property
    def bad(self):
        raise RuntimeError("数据库挂了")   # 非 AttributeError

b = Broken()
# Python 3 中 hasattr(b, 'bad') 会传播 RuntimeError，不会返回 False
# 所以在 property 内部不要随意抛非 AttributeError 的异常

# SDET 场景：鸭子类型检查，验证对象是否符合接口契约
def assert_has_interface(obj, *method_names):
    for name in method_names:
        assert hasattr(obj, name), f"对象缺少方法: {name}"
        assert callable(getattr(obj, name)), f"{name} 不可调用"

assert_has_interface(svc, 'connect')   # 通过
```

### 1.4 `delattr(obj, name)`

```python
# 等价于 del obj.name，name 是字符串

class Cache:
    def __init__(self):
        self.data = {}
        self.timeout = 60

c = Cache()
print(hasattr(c, 'timeout'))   # → True
delattr(c, 'timeout')
print(hasattr(c, 'timeout'))   # → False

# 删除不存在的属性 → AttributeError
try:
    delattr(c, 'nonexistent')
except AttributeError as e:
    print(e)   # → timeout

# SDET 场景：清理测试对象的缓存属性（配合 LazyProperty）
class PageObject:
    @property
    def title(self):
        return "页面标题"   # 实际场景中从页面抓取

po = PageObject()
# 如果 title 是 cached_property，可用 delattr 强制刷新缓存
# delattr(po, 'title')   # 下次访问重新计算
```

### 1.5 四者关系与对比

```
getattr  ←→  obj.attr          （读）
setattr  ←→  obj.attr = val    （写）
delattr  ←→  del obj.attr      （删）
hasattr  ←→  try getattr ...   （探测）

它们都会经过完整的属性查找链（描述符、__dict__、__getattr__ 等）
即：setattr(obj, 'x', 1)  →  如果类有 __set__ 描述符，会触发它
```

---

## 第二部分：`property` —— 描述符的语法糖

### 2.1 `property` 本质

`property` 是 Python 内置的**数据描述符类**，实现了 `__get__`、`__set__`、`__delete__`，
`@property`、`.getter()`、`.setter()`、`.deleter()` 是它提供的装饰器接口。

```
@property          →  创建只有 fget 的 property 对象（只读属性）
@xxx.getter(func)  →  返回一个新 property，替换 fget
@xxx.setter(func)  →  返回一个新 property，替换 fset
@xxx.deleter(func) →  返回一个新 property，替换 fdel
```

### 2.2 完整用法

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius   # 私有存储，约定用下划线

    # ① 只读属性：只定义 getter
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32

    # ② 读写属性：getter + setter
    @property
    def celsius(self):
        """摄氏度（带校验）"""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError(f"温度不能低于绝对零度: {value}")
        self._celsius = value

    # ③ 支持删除：加 deleter
    @celsius.deleter
    def celsius(self):
        print("重置温度到 0℃")
        self._celsius = 0


t = Temperature(25)
print(t.celsius)      # → 25（触发 getter）
print(t.fahrenheit)   # → 77.0（只读）

t.celsius = 100       # 触发 setter，校验通过
t.celsius = -300      # → ValueError: 温度不能低于绝对零度

del t.celsius         # 触发 deleter → 重置温度到 0℃
print(t.celsius)      # → 0

# 尝试给只读属性赋值
try:
    t.fahrenheit = 100
except AttributeError as e:
    print(e)   # → can't set attribute
```

### 2.3 `.getter()` 的实际用途

`.getter()` 最常用于**子类覆盖父类 property 的读取逻辑**，而保留父类的 setter/deleter：

```python
class Base:
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v


class Child(Base):
    # 只覆盖 getter，保留父类 setter
    @Base.value.getter
    def value(self):
        return f"子类处理: {self._value}"


c = Child()
c.value = 42           # 用父类 setter
print(c.value)         # → 子类处理: 42（用子类 getter）
```

### 2.4 `property` 内部原理（手写实现）

```python
class property_impl:
    """property 的简化手写版，揭示底层描述符机制"""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    # ---- 描述符协议 ----
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self          # 通过类访问，返回 property 对象本身
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    # ---- 链式装饰器 ----
    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)
```

### 2.5 `property` 在 SDET 中的典型场景

```python
# 场景：Page Object 的元素定位（惰性 + 校验）
from selenium.webdriver.common.by import By

class LoginPage:
    def __init__(self, driver):
        self._driver = driver
        self._username_input = None

    @property
    def username_input(self):
        """每次调用都重新查找元素，避免 StaleElementReferenceException"""
        return self._driver.find_element(By.ID, "username")

    @property
    def is_logged_in(self):
        """只读的页面状态，不允许外部直接设置"""
        return "dashboard" in self._driver.current_url

    @property
    def page_title(self):
        return self._driver.title

# page.username_input.send_keys("admin")  → 每次都新鲜定位
# page.is_logged_in = True   → AttributeError（只读保护）
```

---

## 第三部分：描述符协议 `__get__` / `__set__` / `__delete__`

### 3.1 三个方法签名

```python
class Descriptor:
    def __get__(self, obj, objtype=None):
        # obj:     通过实例访问时为实例，通过类访问时为 None
        # objtype: 宿主类（始终存在）
        ...

    def __set__(self, obj, value):
        # obj:   被设置属性的实例
        # value: 赋的值
        ...

    def __delete__(self, obj):
        # obj: 被删除属性的实例
        ...

    def __set_name__(self, owner, name):
        # Python 3.6+ 新增
        # owner: 宿主类
        # name:  该描述符被赋给的属性名
        # 在类定义时自动调用，无需手动传名字
        ...
```

### 3.2 数据描述符 vs 非数据描述符（优先级核心）

```
描述符类型        定义的方法                    优先级
──────────────────────────────────────────────────────
数据描述符        __get__ + __set__/___delete__  > 实例 __dict__
非数据描述符      只有 __get__                   < 实例 __dict__

完整优先级链（从高到低）：
  ① 数据描述符（含 property）
  ② 实例 __dict__
  ③ 非数据描述符 / 普通类属性
  ④ __getattr__ 兜底
```

### 3.3 完整示例：带类型验证和删除的描述符

```python
class Validated:
    """完整实现 __get__ / __set__ / __delete__ 的数据描述符"""

    def __set_name__(self, owner, name):
        self.public_name  = name
        self.private_name = f'_validated_{name}'

    def __init__(self, expected_type, default=None):
        self.expected_type = expected_type
        self.default = default

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # 类访问：返回描述符本身，方便反射
        return getattr(obj, self.private_name, self.default)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"[{self.public_name}] 期望 {self.expected_type.__name__}，"
                f"得到 {type(value).__name__}: {value!r}"
            )
        setattr(obj, self.private_name, value)

    def __delete__(self, obj):
        """删除属性 → 恢复默认值"""
        if hasattr(obj, self.private_name):
            delattr(obj, self.private_name)
            print(f"[{self.public_name}] 已重置为默认值: {self.default}")


class APIConfig:
    host    = Validated(str, default="localhost")
    port    = Validated(int, default=8080)
    timeout = Validated(float, default=30.0)

    def __init__(self, host, port, timeout=30.0):
        self.host    = host
        self.port    = port
        self.timeout = timeout


cfg = APIConfig("example.com", 9000)
print(cfg.host, cfg.port)   # → example.com 9000

# 类型错误
try:
    cfg.port = "nine-thousand"
except TypeError as e:
    print(e)   # → [port] 期望 int，得到 str: 'nine-thousand'

# 删除属性：恢复默认值
del cfg.host
print(cfg.host)   # → localhost（默认值）

# 通过类访问描述符本身
print(APIConfig.port)                  # → <Validated object>
print(APIConfig.port.expected_type)    # → <class 'int'>
```

### 3.4 `__set_name__` 深入：避免多个实例共享描述符状态

```python
# ❌ 错误：把值存在描述符对象上，所有实例共享
class BadDescriptor:
    def __get__(self, obj, objtype=None):
        return self._value          # 所有实例共用同一个 _value

    def __set__(self, obj, value):
        self._value = value         # 会覆盖其他实例的值！


# ✅ 正确：把值存在宿主实例的 __dict__ 上
class GoodDescriptor:
    def __set_name__(self, owner, name):
        self.key = '_desc_' + name  # 每个字段名不同，互不干扰

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get(self.key)

    def __set__(self, obj, value):
        obj.__dict__[self.key] = value   # 存在各自实例的 __dict__


class MyModel:
    x = GoodDescriptor()
    y = GoodDescriptor()

a = MyModel(); a.x = 1; a.y = 2
b = MyModel(); b.x = 10; b.y = 20
print(a.x, b.x)   # → 1 10（互不干扰）
```

### 3.5 非数据描述符：`LazyProperty` / `cached_property`

```python
class cached_property_impl:
    """
    Python 3.8 functools.cached_property 的原理
    非数据描述符：第一次计算后写入实例 __dict__，后续直接命中，跳过描述符
    """
    def __init__(self, func):
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # 写入实例 __dict__，因为是非数据描述符，下次会直接命中 __dict__
        val = self.func(obj)
        obj.__dict__[self.attrname] = val
        return val
    # 注意：没有 __set__，所以是非数据描述符，实例 __dict__ 优先级更高


class HeavyReport:
    def __init__(self, data):
        self.data = data

    @cached_property_impl
    def summary(self):
        print("  [耗时计算...]")
        return {"count": len(self.data), "sum": sum(self.data)}


r = HeavyReport([1, 2, 3, 4, 5])
print(r.summary)   # → [耗时计算...] → {'count': 5, 'sum': 15}
print(r.summary)   # → {'count': 5, 'sum': 15}（从 __dict__ 取，无打印）

# 强制刷新缓存：删除实例属性
del r.__dict__['summary']
print(r.summary)   # → [耗时计算...] → 重新计算
```

---

## 第四部分：属性钩子 `__getattr__` / `__setattr__` / `__delattr__`

### 4.1 三个钩子的触发时机对比

```
__getattr__(self, name)
  触发时机：正常查找链全部失败后（兜底）
  不触发：实例 __dict__ 或类中能找到该属性时

__setattr__(self, name, value)
  触发时机：每次赋值 obj.x = val 都触发（无例外）
  注意：在 __init__ 里 self.x = ... 也会触发！

__delattr__(self, name)
  触发时机：每次 del obj.x 都触发
```

### 4.2 `__setattr__` 详解

```python
class StrictModel:
    """只允许设置预定义的字段，拒绝拼写错误的属性名"""

    _allowed = {'name', 'age', 'email'}

    def __setattr__(self, name, value):
        if name not in self._allowed:
            raise AttributeError(
                f"不允许设置属性 '{name}'，合法字段: {self._allowed}"
            )
        # ⚠️ 必须调用 super().__setattr__，否则死循环
        # 不能用 self.name = value（那会再次触发 __setattr__）
        super().__setattr__(name, value)


m = StrictModel()
m.name = "Alice"    # OK
m.age = 25          # OK
m.nmae = "Alice"    # → AttributeError: 不允许设置属性 'nmae'
```

```python
# __setattr__ 的三种安全赋值方式（避免死循环）

class Safe:
    def __setattr__(self, name, value):
        # ① 推荐：调用父类实现
        super().__setattr__(name, value)

        # ② 直接写 __dict__（绕过 __setattr__）
        # object.__setattr__(self, name, value)

        # ③ 直接操作 __dict__（不触发任何钩子）
        # self.__dict__[name] = value
```

### 4.3 `__delattr__` 详解

```python
class AuditModel:
    """记录所有属性删除操作，用于审计"""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)   # 绕过自定义 __setattr__

    def __delattr__(self, name):
        if not hasattr(self, name):
            raise AttributeError(f"属性不存在: {name}")
        print(f"[审计] 删除属性: {name} = {getattr(self, name)}")
        super().__delattr__(name)   # 实际执行删除


user = AuditModel(name="Alice", role="admin", temp_token="abc123")
del user.temp_token   # → [审计] 删除属性: temp_token = abc123
del user.role         # → [审计] 删除属性: role = admin
print(hasattr(user, 'role'))   # → False
```

### 4.4 三个钩子联合使用：冻结对象

```python
class Frozen:
    """
    初始化后不允许修改或删除任何属性
    类似 namedtuple 的不可变效果，但保留类的其他特性
    """
    _frozen = False

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)
        object.__setattr__(self, '_frozen', True)

    def __setattr__(self, name, value):
        if self._frozen:
            raise AttributeError(f"对象已冻结，不可修改属性 '{name}'")
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if self._frozen:
            raise AttributeError(f"对象已冻结，不可删除属性 '{name}'")
        super().__delattr__(name)


cfg = Frozen(host="localhost", port=5432)
print(cfg.host)       # → localhost

try:
    cfg.host = "other"
except AttributeError as e:
    print(e)   # → 对象已冻结，不可修改属性 'host'

try:
    del cfg.port
except AttributeError as e:
    print(e)   # → 对象已冻结，不可删除属性 'port'
```

### 4.5 `__getattr__` 完整回顾（与钩子族统一视角）

```python
class FlexibleConfig:
    """
    综合示例：
    - __setattr__：记录所有赋值
    - __getattr__：找不到时返回 None（宽容模式）
    - __delattr__：删除时同步清理关联数据
    """

    def __init__(self):
        # 用 object.__setattr__ 初始化内部存储，避免触发自定义 __setattr__
        object.__setattr__(self, '_store', {})
        object.__setattr__(self, '_access_log', [])

    def __setattr__(self, name, value):
        store = object.__getattribute__(self, '_store')
        store[name] = value
        print(f"[SET] {name} = {value!r}")

    def __getattr__(self, name):
        # 只有 _store 中找不到才会走这里（因为 _store 在实例 __dict__ 中）
        store = object.__getattribute__(self, '_store')
        if name in store:
            return store[name]
        return None   # 宽容：未定义属性返回 None

    def __delattr__(self, name):
        store = object.__getattribute__(self, '_store')
        if name in store:
            del store[name]
            print(f"[DEL] {name}")
        else:
            raise AttributeError(f"没有属性: {name}")


fc = FlexibleConfig()
fc.host = "localhost"    # → [SET] host = 'localhost'
fc.port = 5432           # → [SET] port = 5432
print(fc.host)           # → localhost
print(fc.missing)        # → None（不报错）
del fc.port              # → [DEL] port
```

---

## 第五部分：`__getattribute__` —— 最底层的门卫

### 5.1 与 `__getattr__` 的根本区别

```
__getattribute__：每次属性访问必经，是整个查找链的入口
__getattr__：     查找链末端的兜底，只在找不到时调用

调用顺序：
  obj.attr
    → __getattribute__ 执行查找链
        → 找到 → 返回
        → 找不到 → 调用 __getattr__
            → 找到 → 返回
            → AttributeError → 最终报错
```

### 5.2 安全重写示例

```python
class AccessLogger:
    """记录所有属性读取，但不干扰正常行为"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._log = []

    def __getattribute__(self, name):
        # 不记录内部属性，避免日志自身触发循环
        if not name.startswith('_'):
            log = super().__getattribute__('_log')
            log.append(name)
        # 必须调用 super()，否则死循环
        return super().__getattribute__(name)

    def access_report(self):
        return dict.fromkeys(self._log, None)


obj = AccessLogger(1, 2)
_ = obj.x
_ = obj.y
_ = obj.x
print(obj._log)   # → ['x', 'y', 'x']
```

---

## 第六部分：完整属性查找链（终极全景图）

```
obj.attr  （读操作）
    │
    ▼
__getattribute__(obj, 'attr')  ← 每次必经，通常不重写
    │
    ├─① 在 type(obj).__mro__ 中查找 'attr'，是否为数据描述符？
    │      是 → 调用 descriptor.__get__(obj, type(obj))  ✓ 返回
    │
    ├─② 在 obj.__dict__ 中查找 'attr'？
    │      是 → 直接返回 obj.__dict__['attr']             ✓ 返回
    │
    ├─③ 在 type(obj).__mro__ 中查找 'attr'，是否为非数据描述符/普通类属性？
    │      是 → 调用 descriptor.__get__ 或直接返回类属性    ✓ 返回
    │
    └─④ 全部失败 → 调用 __getattr__(obj, 'attr')
               是 → 返回 __getattr__ 的结果              ✓ 返回
               否 → raise AttributeError                 ✗ 报错


obj.attr = value  （写操作）
    │
    ▼
__setattr__(obj, 'attr', value)  ← 每次赋值必经
    │
    ├─① 在 type(obj).__mro__ 中查找 'attr'，是否为数据描述符？
    │      是 → 调用 descriptor.__set__(obj, value)       ✓ 完成
    │
    └─② 否则 → 写入 obj.__dict__['attr'] = value          ✓ 完成


del obj.attr  （删操作）
    │
    ▼
__delattr__(obj, 'attr')  ← 每次删除必经
    │
    ├─① 在 type(obj).__mro__ 中查找 'attr'，是否为数据描述符？
    │      是 → 调用 descriptor.__delete__(obj)           ✓ 完成
    │
    └─② 否则 → del obj.__dict__['attr']                   ✓ 完成
```

---

## 第七部分：综合对比速查表

### 7.1 所有方法一览

| 方法/函数 | 类型 | 定义位置 | 触发条件 | 对应操作 |
|-----------|------|----------|----------|----------|
| `getattr()` | 内置函数 | 无需定义 | 主动调用 | 读 |
| `setattr()` | 内置函数 | 无需定义 | 主动调用 | 写 |
| `hasattr()` | 内置函数 | 无需定义 | 主动调用 | 探测 |
| `delattr()` | 内置函数 | 无需定义 | 主动调用 | 删 |
| `property.getter` | 描述符装饰器 | 宿主类内 | 属性被读取 | 读 |
| `property.setter` | 描述符装饰器 | 宿主类内 | 属性被赋值 | 写 |
| `property.deleter` | 描述符装饰器 | 宿主类内 | 属性被删除 | 删 |
| `__get__` | 描述符协议 | **属性所在类** | 属性被读取 | 读 |
| `__set__` | 描述符协议 | **属性所在类** | 属性被赋值 | 写 |
| `__delete__` | 描述符协议 | **属性所在类** | 属性被删除 | 删 |
| `__set_name__` | 描述符协议 | **属性所在类** | 类定义时 | 初始化 |
| `__getattr__` | 属性钩子 | 宿主类 | 正常查找失败后 | 读（兜底） |
| `__setattr__` | 属性钩子 | 宿主类 | 每次赋值 | 写 |
| `__delattr__` | 属性钩子 | 宿主类 | 每次删除 | 删 |
| `__getattribute__` | 底层钩子 | 宿主类 | 每次属性访问 | 读（门卫） |

### 7.2 选型决策树

```
需要托管属性访问？
    │
    ├── 单个属性，逻辑简单？
    │       → 用 @property + .setter + .deleter
    │
    ├── 多个属性，逻辑相同（如批量类型校验）？
    │       → 自定义描述符类（__get__ + __set__ + __delete__）
    │
    ├── 第一次访问计算，后续缓存？
    │       → 非数据描述符（只有 __get__）或 functools.cached_property
    │
    ├── 动态代理 / 找不到属性时兜底？
    │       → __getattr__
    │
    ├── 拦截所有赋值（如冻结、审计）？
    │       → __setattr__（注意内部用 super() 或 object.__setattr__）
    │
    └── 完全接管属性访问（如 ORM 懒加载）？
            → __getattribute__（高风险，务必 super()）
```

---

## 第八部分：高频面试题精选

### Q1：`property` 和描述符有什么关系？

```
property 本身就是一个内置的数据描述符类。
@property 是把函数包装成 property 实例（描述符），赋给类属性。
property 实现了 __get__、__set__、__delete__，所以属于数据描述符，
优先级高于实例 __dict__。
```

### Q2：`__setattr__` 在 `__init__` 里也会触发吗？如何避免死循环？

```python
class Safe:
    def __init__(self):
        # self.x = 1 会触发 __setattr__！
        # 安全写法一：调用父类
        super().__setattr__('x', 1)
        # 安全写法二：直接操作 __dict__
        self.__dict__['y'] = 2
        # 安全写法三：object.__setattr__
        object.__setattr__(self, 'z', 3)

    def __setattr__(self, name, value):
        print(f"设置 {name}")
        super().__setattr__(name, value)
```

### Q3：为什么 `hasattr` 在某些 property 上可能抛异常？

```python
# Python 3 中 hasattr 只捕获 AttributeError
# 如果 property 的 getter 抛出其他异常，hasattr 不会吞掉

class Risky:
    @property
    def data(self):
        raise RuntimeError("连接失败")   # 不是 AttributeError

r = Risky()
# hasattr(r, 'data')  →  抛出 RuntimeError，而不是返回 False
# 正确写法：在 property 内部只抛 AttributeError
```

### Q4：描述符的值应该存在哪里？

```
❌ 存在描述符对象本身：所有宿主类实例共享同一份数据
✅ 存在宿主类实例的 __dict__：每个实例独立
   → 用 obj.__dict__[self.private_name] = value
   → 用 __set_name__ 生成每个字段唯一的 private_name
```

### Q5：`cached_property` 为什么用非数据描述符？

```
非数据描述符（只有 __get__）的优先级低于实例 __dict__。
第一次访问时，在实例 __dict__ 中写入计算结果。
第二次访问时，Python 先查实例 __dict__（优先级更高），
直接命中缓存，描述符的 __get__ 完全不会再被调用。

如果用数据描述符（有 __set__），则 __get__ 每次都会被调用，缓存机制失效。
```

### Q6：`__getattr__` 与 `__getattribute__` 怎么选？

```
场景                          选择
──────────────────────────────────────────────
动态属性代理/兜底              __getattr__（安全，低风险）
完全接管属性读取逻辑            __getattribute__（高风险，务必 super()）
监控/日志所有属性读取           __getattribute__
MagicMock 的动态属性           __getattr__
```

---

## 快速记忆口诀

```
内置四件套（主动调用）：
  get / set / has / del + attr → 动态操作属性的工具函数

property 三步走（装饰器语法糖）：
  @property 读 → @xxx.setter 写 → @xxx.deleter 删
  本质是描述符，住在宿主类里

描述符三兄弟（属性的类上定义）：
  __get__   → 别人读我
  __set__   → 别人写我  → 有我就是数据描述符，优先级盖过实例 dict
  __delete__ → 别人删我

钩子三兄弟（宿主类上定义）：
  __getattr__   → 找不到才叫我（兜底）
  __setattr__   → 每次写都叫我（拦截）
  __delattr__   → 每次删都叫我（拦截）

门卫（最底层）：
  __getattribute__ → 每次读必经，轻易别重写
```
