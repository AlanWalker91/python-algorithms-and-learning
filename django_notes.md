# Django 学习笔记:测开平台开发核心

> 学习日期:2025-05-23
> 主题:Django 核心概念 + DRF + 测开平台开发
> 深度:中等(能写完整 CRUD 接口、能讲清面试题)

---

## 目录

- [一、Web 应用 & MVT 模式](#一web-应用--mvt-模式)
- [二、URL 路由](#二url-路由)
- [三、View 视图](#三view-视图)
- [四、Model 与 ORM](#四model-与-orm)
- [五、DRF(Django REST Framework)](#五drfdjango-rest-framework)
- [六、中间件 Middleware](#六中间件-middleware)
- [七、认证 Authentication](#七认证-authentication)
- [八、信号 Signals](#八信号-signals)
- [九、面试问答模板](#九面试问答模板)
- [十、完整项目骨架](#十完整项目骨架)

---

## 一、Web 应用 & MVT 模式

### 1.1 Web 应用的本质

```
浏览器 → HTTP 请求 → Web 服务器 → 应用框架(Django) → 数据库
                                       ↓
浏览器 ← HTTP 响应 ← Web 服务器 ← 处理逻辑
```

**核心**:请求(Request)进来,响应(Response)出去。

### 1.2 Django 的 MVT 模式

| 角色 | Django 里 | 干什么 |
|---|---|---|
| **M** Model | models.py | 跟数据库打交道 |
| **V** View | views.py | 处理业务逻辑 |
| **T** Template | templates/ | 生成 HTML(前后端分离时用不到) |
| URL | urls.py | 决定哪个请求给哪个 View |

```
请求来了
  ↓
URL 路由(urls.py)── "这个请求该谁处理?"
  ↓
View(views.py)── 处理逻辑
  ↓             ↓
  ↓        Model(models.py)── 操作数据库
  ↓             ↑
  ↓
Template(templates/)或 JSON── 生成响应
  ↓
响应返回浏览器
```

### 1.3 项目结构

```
test_platform/
├── manage.py              ← 命令行入口
├── test_platform/         ← 项目主目录
│   ├── settings.py        ← 配置文件
│   ├── urls.py            ← 项目级 URL 路由
│   ├── wsgi.py / asgi.py
│   └── ...
└── api/                   ← 一个 app
    ├── views.py
    ├── models.py
    ├── urls.py            ← app 级 URL(需手动创建)
    ├── serializers.py     ← DRF 序列化器(需手动创建)
    └── ...
```

### 1.4 启动命令

```bash
# 安装
pip install django djangorestframework

# 创建项目
django-admin startproject test_platform

# 创建 app
python manage.py startapp api

# 数据库迁移(Model 变化后)
python manage.py makemigrations    # 生成迁移文件
python manage.py migrate           # 执行迁移

# 启动开发服务器
python manage.py runserver

# 创建超级用户
python manage.py createsuperuser

# Django shell(交互式调试)
python manage.py shell
```

---

## 二、URL 路由

### 2.1 两层路由设计

```python
# test_platform/urls.py(项目级,总路由)
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),       # 把 api 的 URL 接进来
]
```

```python
# api/urls.py(app 级,需手动创建)
from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello),
    path('testcases/<int:id>/', views.get_testcase),
]
```

### 2.2 分层的两个核心收益

1. **可维护性**:每个 app 的路由自治,改某模块的 URL 不用翻整个项目
2. **协作友好**:多人开发不同 app 时,不会因为改同一个 urls.py 产生 Git 冲突

### 2.3 URL 参数

```python
path('users/<int:user_id>/', views.get_user)
# <int:user_id> = 整数参数,会传给 view 函数
# 类型:<str:>, <int:>, <slug:>, <uuid:>
```

---

## 三、View 视图

### 3.1 函数视图(基础写法)

```python
from django.http import HttpResponse, JsonResponse

def hello(request):
    return HttpResponse("Hello")

def get_user(request, user_id):
    return JsonResponse({"id": user_id, "name": "Alice"})
```

### 3.2 HttpResponse vs JsonResponse

| | HttpResponse | JsonResponse |
|---|---|---|
| Content-Type | text/html | application/json |
| 浏览器显示 | HTML 渲染 | 原始 JSON 文本 |
| 自动序列化 | ❌ | ✅ dict → JSON |

`JsonResponse(data)` 本质上 = `HttpResponse(json.dumps(data), content_type='application/json')`。

### 3.3 RESTful 设计原则

| HTTP 方法 | 用途 | 幂等性 |
|---|---|---|
| GET | 查询 | ✅ |
| POST | 创建 | ❌ |
| PUT | 完整更新 | ✅ |
| PATCH | 部分更新 | - |
| DELETE | 删除 | ✅ |

**核心**:URL 表示资源(名词),HTTP 方法表示操作(动词)。

- ✅ `DELETE /testcases/1/`
- ❌ `GET /testcases/delete?id=1`

---

## 四、Model 与 ORM

### 4.1 定义 Model

```python
# api/models.py
from django.db import models

class TestCase(models.Model):
    title = models.CharField(max_length=200)
    api_url = models.CharField(max_length=500)
    method = models.CharField(max_length=10, default='GET')
    expected_status = models.IntegerField(default=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)    # ⭐ 软删除
    
    creator = models.ForeignKey(           # 外键到 User
        'auth.User',
        on_delete=models.CASCADE,
        related_name='testcases',
        null=True
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'api_testcase'           # 自定义表名(可选)
        ordering = ['-created_at']          # 默认排序
```

### 4.2 常用字段类型

| 字段类型 | 对应 |
|---|---|
| `CharField(max_length=N)` | VARCHAR(N) |
| `TextField()` | TEXT |
| `IntegerField()` | INT |
| `FloatField()` | FLOAT |
| `BooleanField()` | BOOLEAN |
| `DateTimeField()` | DATETIME |
| `DateField()` | DATE |
| `ForeignKey()` | 外键 |
| `ManyToManyField()` | 多对多 |

### 4.3 ORM 增删改查

```python
# ===== 增 =====
TestCase.objects.create(title="登录测试", api_url="/api/login")

# ===== 查 =====
TestCase.objects.all()                       # SELECT *
TestCase.objects.get(id=1)                   # WHERE id=1(不存在抛异常)
TestCase.objects.filter(method="POST")       # WHERE method='POST'
TestCase.objects.filter(method="POST", expected_status=200)
TestCase.objects.filter(expected_status__gt=200)         # WHERE > 200
TestCase.objects.filter(title__contains="登录")           # LIKE '%登录%'
TestCase.objects.exclude(method="DELETE")     # WHERE NOT method='DELETE'
TestCase.objects.order_by('-created_at')      # ORDER BY DESC
TestCase.objects.all()[:5]                    # LIMIT 5

# ===== 改 =====
case = TestCase.objects.get(id=1)
case.title = "新标题"
case.save()

# 批量更新
TestCase.objects.filter(method="GET").update(expected_status=200)

# ===== 删 =====
case = TestCase.objects.get(id=1)
case.delete()                                 # ⚠️ 物理删除

# 软删除(推荐)
case.is_deleted = True
case.save()
```

### 4.4 ORM 过滤操作符速记

| 写法 | SQL |
|---|---|
| `field=值` | `= 值` |
| `field__gt=值` | `> 值` |
| `field__lt=值` | `< 值` |
| `field__gte=值` | `>= 值` |
| `field__lte=值` | `<= 值` |
| `field__contains="x"` | `LIKE '%x%'` |
| `field__startswith="x"` | `LIKE 'x%'` |
| `field__in=[1,2,3]` | `IN (1,2,3)` |
| `field__isnull=True` | `IS NULL` |

**记法**:`字段__操作符=值`,**双下划线** `__` 是 ORM 语法标识。

### 4.5 默认表名规则

```
Model 类名:TestCase
App 名:api
默认表名:api_testcase    (app名_类名小写)
```

### 4.6 物理删除 vs 软删除

| | 物理删除 | 软删除 |
|---|---|---|
| 操作 | `case.delete()` | `case.is_deleted = True; case.save()` |
| 数据 | 真的从表里消失 | 数据还在,只是标记 |
| 可恢复 | ❌ | ✅ |
| 生产推荐 | 仅测试数据清理 | ⭐ 99% 的场景 |

---

## 五、DRF(Django REST Framework)

### 5.1 为什么需要 DRF

手写 view 拼 JSON,代码冗长。DRF 提供了一套 RESTful API 的标准实现。

### 5.2 三大组件

| 组件 | 作用 |
|---|---|
| **Serializer** | Model ↔ JSON 自动转换 + 字段校验 |
| **ViewSet** | 自动实现 CRUD 视图函数 |
| **Router** | 自动生成 RESTful URL |

### 5.3 完整骨架

```python
# api/serializers.py
from rest_framework import serializers
from .models import TestCase

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'        # 所有字段
        # 或指定字段:fields = ['id', 'title', 'api_url']
        # 或排除字段:exclude = ['is_deleted']
```

```python
# api/views.py
from rest_framework import viewsets
from .models import TestCase
from .serializers import TestCaseSerializer

class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.filter(is_deleted=False)
    serializer_class = TestCaseSerializer
```

```python
# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'testcases', views.TestCaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

### 5.4 自动生成的 5 个接口

| HTTP 方法 | URL | 作用 | ViewSet 方法 |
|---|---|---|---|
| GET | `/testcases/` | 列表 | list |
| POST | `/testcases/` | 创建 | create |
| GET | `/testcases/1/` | 详情 | retrieve |
| PUT | `/testcases/1/` | 完整更新 | update |
| PATCH | `/testcases/1/` | 部分更新 | partial_update |
| DELETE | `/testcases/1/` | 删除 | destroy |

**3 行 ViewSet + 3 行 Router = 完整 CRUD**——这就是 DRF 的核心威力。

### 5.5 数据权限隔离(用户只看自己的数据)

```python
class TestCaseViewSet(viewsets.ModelViewSet):
    serializer_class = TestCaseSerializer
    
    def get_queryset(self):
        # 动态生成 queryset,根据当前用户过滤
        return TestCase.objects.filter(
            creator=self.request.user,
            is_deleted=False
        )
```

**两种方式对比**:
- `queryset = ...` :静态,所有人看到一样的数据
- `get_queryset()` :动态,可以根据 request 过滤

### 5.6 自定义 Serializer 字段

```python
class TestCaseSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    # 加一个外键关联的字段
    
    method = serializers.ChoiceField(
        choices=['GET', 'POST', 'PUT', 'DELETE']
    )    # 自定义校验
    
    class Meta:
        model = TestCase
        fields = ['id', 'title', 'api_url', 'method', 'creator_name']
```

---

## 六、中间件 Middleware

### 6.1 核心画面

```
请求 → 中间件1 → 中间件2 → 中间件3 → View → 响应
         (日志)    (认证)    (限流)
```

**中间件 = 请求/响应的全局钩子**,处理跨多个 view 的横切关注点。

### 6.2 写一个自定义中间件

```python
# api/middleware.py
import time
import logging

logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 请求到达 View 之前
        start_time = time.time()
        
        # 调用下一站(下一个中间件或 View)
        response = self.get_response(request)
        
        # View 返回响应之后
        duration = (time.time() - start_time) * 1000
        logger.info(f"{request.method} {request.path} - {duration:.2f}ms")
        
        return response
```

注册:

```python
# settings.py
MIDDLEWARE = [
    # ... Django 自带的中间件
    'api.middleware.RequestTimingMiddleware',    # 加在末尾
]
```

### 6.3 常用场景

- 请求日志
- 用户认证
- API 限流
- CORS 跨域
- 性能监控
- 异常统一处理

---

## 七、认证 Authentication

### 7.1 Token 认证(前后端分离标配)

```
1. 用户登录(POST /login/ 用户名密码)
   ↓
2. 后端验证,生成 Token 返回
   ↓
3. 前端保存 Token
   ↓
4. 每个请求带上 Token:Authorization: Token abc123...
   ↓
5. 后端验证 Token,识别用户
```

### 7.2 DRF Token 认证配置

```python
# settings.py
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',     # ⭐ DRF 自带的 Token 应用
    'api',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

```python
# urls.py
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('login/', obtain_auth_token),   # 用户名密码 → Token
    # ...
]
```

```bash
# 数据库迁移
python manage.py migrate
python manage.py createsuperuser

# 登录拿 Token
curl -X POST http://127.0.0.1:8000/login/ -d "username=alice&password=xxx"
# 返回:{"token":"abc123..."}

# 带 Token 访问
curl http://127.0.0.1:8000/testcases/ -H "Authorization: Token abc123..."
```

### 7.3 在 View 里取当前用户

```python
def my_view(request):
    user = request.user        # 当前登录的 User 对象
    username = user.username
```

### 7.4 权限控制

```python
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class TestCaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]    # 必须登录
    # 或 [IsAdminUser]    # 必须是管理员
```

---

## 八、信号 Signals

### 8.1 核心思想

**让数据变化自动触发附加操作,不污染业务代码**。

```
没有信号:
def create_user_view(request):
    user = User.objects.create(...)
    send_welcome_email(user)       # 业务代码塞各种附加操作
    create_audit_log(user)
    notify_other_system(user)

有信号:
def create_user_view(request):
    user = User.objects.create(...)   # 业务代码保持干净
    # 信号自动触发邮件、日志、通知
```

### 8.2 常用信号

| 信号 | 触发时机 |
|---|---|
| `pre_save` | Model 保存前 |
| `post_save` | Model 保存后 |
| `pre_delete` | Model 删除前 |
| `post_delete` | Model 删除后 |

### 8.3 写一个信号

```python
# api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TestCase

@receiver(post_save, sender=TestCase)
def log_testcase_change(sender, instance, created, **kwargs):
    if created:
        print(f"新用例创建:{instance.title}")
    else:
        print(f"用例更新:{instance.title}")
```

```python
# api/apps.py
from django.apps import AppConfig

class ApiConfig(AppConfig):
    name = 'api'
    
    def ready(self):
        import api.signals    # ⭐ 注册信号
```

---

## 九、面试问答模板

### Q1:"Django 的 MVT 模式?和 MVC 的区别?"

> "MVT 是 Django 的设计模式:Model 管数据库,View 管业务逻辑,Template 管 HTML。和经典 MVC 的区别——Django 的 View 相当于 MVC 的 Controller(业务逻辑),Django 的 Template 相当于 MVC 的 View(展示层)。本质相同,只是命名不同。"

### Q2:"Django ORM 是什么?有什么优缺点?"

> "ORM(对象关系映射)让你用 Python 类操作数据库,不用写 SQL。
> 
> 优点:开发快、避免 SQL 注入、跨数据库迁移容易(MySQL → PostgreSQL 改一行配置)。
> 
> 缺点:复杂查询写起来不直观、有性能损耗、容易写出低效查询(比如 N+1 问题)——复杂场景仍然需要写原生 SQL 或用 `.select_related()`、`.prefetch_related()` 优化。"

### Q3:"DRF 的核心组件?"

> "三大组件:
> - Serializer:Model 和 JSON 互转 + 字段校验
> - ViewSet:封装 CRUD 视图逻辑(list/create/retrieve/update/destroy)
> - Router:根据 ViewSet 自动生成 RESTful URL
> 
> 三者配合,几行代码就能生成完整的 CRUD 接口。"

### Q4:"RESTful 风格的核心是什么?"

> "核心是 URL 表示资源(名词),HTTP 方法表示操作(动词)。
> - GET 查询(幂等)
> - POST 创建(非幂等)
> - PUT 完整更新(幂等)
> - DELETE 删除(幂等)
> 
> 反例:`GET /api/deleteUser?id=1` 把动词放 URL 里,违反 RESTful 语义。正确写法:`DELETE /api/users/1/`。"

### Q5:"中间件的作用?"

> "中间件是 Django 处理请求/响应的全局钩子,用于处理跨多个 view 的横切关注点。常见场景:日志、认证、限流、CORS、性能监控。设计上避免在每个 view 里重复写这些逻辑。"

### Q6:"Token 认证 vs Session 认证?"

> "Session 认证:服务器记录登录状态,客户端存 cookie——有状态,适合传统 Web 应用。
> 
> Token 认证:服务器不记状态,客户端每次请求带 Token——无状态,适合前后端分离、移动端、微服务。
> 
> 测开平台前后端分离,选 Token。"

### Q7:"信号(Signals)是什么?什么时候用?"

> "Django 信号是观察者模式实现,用于解耦业务逻辑和附加操作。
> 
> 比如用户注册后要发邮件、写日志、通知第三方——直接在注册 view 里写会让代码臃肿,用信号让发邮件模块监听'用户已创建'信号,各自处理,降低耦合。
> 
> 不过信号也有坑:执行顺序不明确、调试困难——简单场景直接调用函数就行,不用过度使用。"

### Q8:"物理删除 vs 软删除?"

> "物理删除是真的从数据库删除,不可恢复;软删除是加 is_deleted 标记,数据保留。
> 
> 生产环境 99% 用软删除,因为:可恢复(防止误删)、可审计(谁什么时候删的)、不破坏外键关系。物理删除只在测试数据清理等场景才用。"

---

## 十、完整项目骨架

```
test_platform/
├── manage.py
├── requirements.txt           # django, djangorestframework
├── test_platform/
│   ├── settings.py            # INSTALLED_APPS, MIDDLEWARE, DRF配置
│   └── urls.py                # 项目级 URL + login URL
└── api/
    ├── apps.py                # ready() 中注册信号
    ├── models.py              # TestCase Model + 软删除字段
    ├── serializers.py         # DRF Serializer
    ├── views.py               # ViewSet + get_queryset 数据权限
    ├── urls.py                # Router 注册
    ├── middleware.py          # 请求耗时中间件
    └── signals.py             # 创建审计日志
```

**典型工作流**:

```
1. 改 Model → makemigrations + migrate
2. 写 Serializer → 暴露哪些字段
3. 写 ViewSet → 业务逻辑 / 权限控制
4. 注册到 Router → URL 自动生成
5. 测试:浏览器访问 DRF 调试界面 / curl 调用
```

---

## 附录:学习路径建议

Django 是个大框架,不可能一次学完。建议路径:

1. ✅ 当前掌握:URL/View/Model/ORM/DRF/中间件/认证/信号
2. 下一步:**亲手把测试用例 CRUD 项目从零写一遍**(不看笔记)
3. 进阶:Django Admin、缓存、Celery 异步任务、N+1 查询优化
4. 高级:Django 源码阅读、自定义认证后端、自定义 ORM 字段

**Django 必须动手才能真正学会**——光看笔记下次写还是会忘。

---

*Django 中等深度学习笔记 —— 完结。*
