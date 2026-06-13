# 数据库学习笔记:SQL + 索引优化 + 事务 + 连接池增强版

> 学习日期:2025-05-23`r`n> 优化日期:2026-05-28`r`n> 主题:测开面试数据库核心知识 + SQL 实战 + 索引优化 + 事务隔离 + 慢 SQL 排查`r`n> 适用:测试开发工程师面试、接口自动化、测试数据管理、性能排查与后端联调

---

## 目录

- [一、SQL 核心语法](#一sql-核心语法)
- [二、索引原理与优化](#二索引原理与优化)
- [三、连接池](#三连接池)
- [四、事务 ACID 与隔离级别](#四事务-acid-与隔离级别)
- [五、MVCC 与锁机制](#五mvcc-与锁机制)
- [六、SQL 注入与参数化查询](#六sql-注入与参数化查询)
- [七、表结构、数据类型与约束](#七表结构数据类型与约束)
- [八、EXPLAIN 深入与慢 SQL 排查](#八explain-深入与慢-sql-排查)
- [九、联合索引、覆盖索引与分页优化](#九联合索引覆盖索引与分页优化)
- [十、SQL 高频面试题](#十sql-高频面试题)
- [十一、测试数据管理与 pytest 事务回滚](#十一测试数据管理与-pytest-事务回滚)
- [十二、主从复制、读写分离与主从延迟](#十二主从复制读写分离与主从延迟)
- [十三、备份恢复基础](#十三备份恢复基础)
- [十四、连接池常见问题与排查](#十四连接池常见问题与排查)
- [十五、面试问答模板](#十五面试问答模板)
- [十六、关键代码模板](#十六关键代码模板)
- [十七、命令速查表](#十七命令速查表)
---

## 一、SQL 核心语法

### 1.1 SQL 语句骨架(必背)

```sql
SELECT 列
FROM 表
JOIN 另一张表 ON 配对条件
WHERE 行级筛选
GROUP BY 分组
HAVING 组级筛选
ORDER BY 排序
LIMIT 数量;
```

**口诀**:选(SELECT) 从(FROM) 拼(JOIN) 筛(WHERE) 分(GROUP BY) 再筛(HAVING) 排(ORDER BY) 取(LIMIT)

**铁律**:这个顺序不能乱,每个子句各管各的事。

### 1.2 基础 CRUD

```sql
-- 查(最常考)
SELECT name, salary FROM employees WHERE age > 30;

-- 增
INSERT INTO employees (name, age, dept_id, salary) VALUES ('Grace', 29, 1, 17000);

-- 改
UPDATE employees SET salary = 25000 WHERE name = 'Bob';

-- 删
DELETE FROM employees WHERE id = 6;
```

### 1.3 条件与排序

```sql
-- 多条件
SELECT * FROM employees WHERE dept_id = 1 AND salary > 13000;

-- 排序(DESC 降序,ASC 升序/默认)
SELECT name, salary FROM employees ORDER BY salary DESC;

-- 取前 N 条
SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3;
```

### 1.4 NULL 的特殊规则

```sql
-- ❌ 错:NULL 不能用 = 比较
WHERE dept_id = NULL

-- ✅ 对:必须用 IS NULL / IS NOT NULL
WHERE dept_id IS NULL
WHERE dept_id IS NOT NULL
```

> **原因**:SQL 里 NULL 表示"未知"。`NULL = NULL` 的结果是 NULL(未知),不是 TRUE。

### 1.5 JOIN:把两张表拼起来

#### 心智模型:配对

```
左表(employees):              右表(departments):
Alice  dept_id=1              id=1  QA
Bob    dept_id=2              id=2  Dev
Frank  dept_id=NULL           id=3  PM
```

JOIN 就是按 `dept_id = id` 给每行找配对。

#### INNER JOIN vs LEFT JOIN

| | INNER JOIN | LEFT JOIN |
|---|---|---|
| 配上对的行 | ✅ 保留 | ✅ 保留 |
| 左表配不上的行 | ❌ 丢掉 | ✅ 保留(右边填 NULL) |
| 一句话 | **只要交集** | **左边全要** |

```sql
-- INNER JOIN:只要能配对的(Frank 消失)
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.id;

-- LEFT JOIN:左边全要(Frank 保留,部门名为 NULL)
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.id;
```

#### 经典面试题:找没有关联数据的记录

```sql
-- 找没有部门的员工
SELECT e.name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.id
WHERE d.dept_name IS NULL;
```

**思路**:LEFT JOIN 保留所有员工 → 没部门的右边是 NULL → WHERE IS NULL 筛出来。

### 1.6 GROUP BY:分组聚合

#### 常用聚合函数

| 函数 | 作用 |
|---|---|
| `COUNT(*)` | 数行数 |
| `SUM(salary)` | 求和 |
| `AVG(salary)` | 平均值 |
| `MAX(salary)` | 最大值 |
| `MIN(salary)` | 最小值 |

#### 基本用法

```sql
-- 每个部门的平均薪资
SELECT dept_id, AVG(salary) AS 平均薪资
FROM employees
GROUP BY dept_id;

-- 每个部门的最高薪资,按最高薪资降序
SELECT dept_id, MAX(salary) AS 最高薪资
FROM employees
GROUP BY dept_id
ORDER BY MAX(salary) DESC;
```

#### WHERE vs HAVING

| | WHERE | HAVING |
|---|---|---|
| 位置 | GROUP BY **之前** | GROUP BY **之后** |
| 作用 | 筛选**行** | 筛选**组** |
| 能用聚合函数吗 | ❌ 不能 | ✅ 能 |

```sql
-- 平均薪资大于 15000 的部门
SELECT dept_id, AVG(salary) AS 平均薪资
FROM employees
GROUP BY dept_id
HAVING AVG(salary) > 15000;
```

#### 综合题:JOIN + GROUP BY

```sql
-- 每个部门名称对应的员工人数
SELECT d.dept_name, COUNT(*) AS 员工人数
FROM employees e
INNER JOIN departments d ON e.dept_id = d.id
GROUP BY d.dept_name;

-- 每个部门平均薪资 > 15000 的部门名称,按平均薪资降序
SELECT d.dept_name, AVG(e.salary) AS 平均薪资
FROM employees e
INNER JOIN departments d ON e.dept_id = d.id
GROUP BY d.dept_name
HAVING AVG(e.salary) > 15000
ORDER BY AVG(e.salary) DESC;
```

---

## 二、索引原理与优化

### 2.1 心智模型:字典的目录

```
没索引:从第 1 页翻到最后一页找"python" → 最坏翻 1000 页
有索引:查目录"P 在第 650 页" → 直接跳过去 → 翻 3-4 页
```

### 2.2 底层:B+ 树

> 索引用 B+ 树把 O(n) 的全表扫描变成 O(log n) 的树查找。

| 数据量 | 全表扫描次数 | B+ 树查找次数 |
|---|---|---|
| 1,000 | 1,000 | ~3 |
| 100 万 | 1,000,000 | ~4 |
| 1 亿 | 100,000,000 | ~5 |

### 2.3 怎么创建索引

```sql
-- 单列索引
CREATE INDEX idx_email ON employees(email);

-- 联合索引(多列)
CREATE INDEX idx_dept_salary ON employees(dept_id, salary);
```

**命名惯例**:`idx_表名_列名` 或 `idx_列名`。

### 2.4 什么时候该加索引

| 场景 | 该不该加 | 原因 |
|---|---|---|
| WHERE 经常按某列查 | ✅ 加 | 加速查找 |
| JOIN 的 ON 条件列 | ✅ 加 | 加速配对 |
| ORDER BY 的列 | ✅ 考虑加 | 避免排序 |
| 很少被查询的列 | ❌ 不加 | 浪费空间 |
| 经常被更新的列 | ⚠️ 谨慎 | 每次更新也要更新索引 |
| 数据量很小(< 1000 行) | ❌ 不加 | 全表扫描也很快 |
| 写多读少(如日志表) | ❌ 不加 | 拖慢写入速度 |

### 2.5 索引的代价

1. **占磁盘空间** —— 每个索引是一棵额外的 B+ 树
2. **写入变慢** —— INSERT/UPDATE/DELETE 要同时更新索引
3. **维护成本** —— 太多索引反而拖慢写操作

> **金句**:"索引是**用写入性能换读取性能**。读多写少多建索引;写多读少少建索引。"

### 2.6 EXPLAIN:看查询有没有走索引

```sql
EXPLAIN SELECT * FROM employees WHERE name = 'Alice';
```

**关键看两列**:

| 字段 | 好的值 | 坏的值 |
|---|---|---|
| `type` | `ref` / `const` / `eq_ref` | **`ALL`**(全表扫描!) |
| `key` | 索引名(如 `idx_name`) | **`NULL`**(没用索引!) |

> **排查慢查询第一步**:`EXPLAIN` 看 type 是不是 ALL、key 是不是 NULL。

### 2.7 索引失效的三大场景(面试必考陷阱)

#### 陷阱 1:对索引列做函数运算

```sql
-- ❌ 索引失效:函数包裹了列
WHERE YEAR(create_time) = 2024

-- ✅ 改成范围查询
WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01'
```

#### 陷阱 2:LIKE 前导通配符

```sql
-- ❌ 索引失效:% 在前面
WHERE name LIKE '%lice'

-- ✅ 索引有效:% 在后面
WHERE name LIKE 'Ali%'
```

#### 陷阱 3:隐式类型转换

```sql
-- ❌ 索引失效:name 是 VARCHAR,传了数字
WHERE name = 123

-- ✅ 类型一致
WHERE name = '123'
```

> **金句**:"索引失效三大场景:函数运算、LIKE 前导通配符、隐式类型转换。排查用 EXPLAIN。"

---

## 三、连接池

### 3.1 心智模型:提前开好的门

```
没有连接池:
  每次请求: 开门(TCP+认证 ~7ms) → 点单(SQL ~0.1ms) → 关门(~1ms)
  连接开销是查询本身的 70 倍!

有连接池:
  程序启动: 一次性开 10 扇门
  每次请求: 走进已开的门 → 点单 → 走出来(门不关!)
  请求结束: 门还回池子,下个请求复用
```

### 3.2 与并发概念的对应

| 并发概念 | 连接池对应 |
|---|---|
| `Semaphore(10)` | 池子里 10 个连接 |
| `async with semaphore:` | 从池子借一个连接 |
| 出 `async with` | 还回池子 |
| 队列排队 | 连接都被借走了,新请求等待 |

### 3.3 三种方案

#### 方案 1:pymysql + DBUtils(同步,测开最常用)

```python
from dbutils.pooled_db import PooledDB
import pymysql

pool = PooledDB(
    creator=pymysql,
    maxconnections=10,
    host='127.0.0.1',
    port=3306,
    user='root',
    password='123456',
    database='test_db',
    charset='utf8mb4',
)

def query_user(user_id):
    conn = pool.connection()            # 从池子借
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()                    # 不是真关闭!是还回池子
```

#### 方案 2:SQLAlchemy(ORM,大项目用)

```python
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:123456@127.0.0.1:3306/test_db",
    pool_size=10,
    max_overflow=5,
)

with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users WHERE id = 1")
```

#### 方案 3:aiomysql(异步,配合 asyncio)

```python
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306,
        user='root', password='123456',
        db='test_db', maxsize=10,
    )
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users WHERE id = %s", (1,))
            result = await cur.fetchone()
    
    pool.close()
    await pool.wait_closed()
```

### 3.4 核心参数

| 参数 | 含义 | 推荐值 |
|---|---|---|
| `pool_size` / `maxconnections` | 池子大小 | 5-20 |
| `max_overflow` | 允许超出的临时连接 | 5-10 |
| `pool_timeout` | 借不到连接等多久 | 30 秒 |
| `pool_recycle` | 连接存活多久后强制重建 | 3600 秒 |

> **池子太小** → 请求排队,响应慢
> **池子太大** → 数据库被撑爆

> **经验公式**:池子大小 = CPU 核数 × 2 + 磁盘数,通常 10-20 就够。

### 3.5 反直觉的 close()

```python
conn = pool.connection()    # 从池子借
conn.close()                # ← 不是断开!是还回池子!
```

连接池重写了 close 方法,让"关闭"变成"归还"。**不 close 会导致连接泄漏**——池子里的连接用光了没人还,后续请求全部卡住。

### 3.6 pytest 里使用连接池

```python
# conftest.py
import pytest
from dbutils.pooled_db import PooledDB
import pymysql

@pytest.fixture(scope="session")
def db_pool():
    """整个测试会话共享一个连接池"""
    pool = PooledDB(
        creator=pymysql,
        maxconnections=5,
        host='127.0.0.1',
        user='root',
        password='123456',
        database='test_db',
    )
    yield pool

@pytest.fixture
def db(db_pool):
    """每个测试函数独立借还连接"""
    conn = db_pool.connection()
    yield conn
    conn.close()

# test_user.py
def test_query_user(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = 1")
    result = cursor.fetchone()
    assert result is not None
```

**scope 设计要点**:
- `db_pool` 用 `scope="session"` —— 连接池只创建一次
- `db` 用 `scope="function"` —— 每个测试独立借还,保证隔离

---

## 四、事务 ACID 与隔离级别

事务用于保证一组 SQL 要么全部成功,要么全部失败。测开在造测试数据、验证转账类接口、做用例隔离时经常会用到事务。

### 4.1 事务基本语法

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
-- 如果出错:
-- ROLLBACK;
```

常用命令:

| 命令 | 含义 |
|---|---|
| `START TRANSACTION` | 开启事务 |
| `COMMIT` | 提交事务 |
| `ROLLBACK` | 回滚事务 |
| `SAVEPOINT sp1` | 创建保存点 |
| `ROLLBACK TO sp1` | 回滚到保存点 |

### 4.2 ACID 四大特性

| 特性 | 含义 | 例子 |
|---|---|---|
| Atomicity 原子性 | 要么全部成功,要么全部失败 | 转账扣款和加款必须一起成功 |
| Consistency 一致性 | 事务前后数据满足约束 | 账户总金额不应凭空变化 |
| Isolation 隔离性 | 并发事务之间尽量互不干扰 | 两个事务同时改数据不会乱 |
| Durability 持久性 | 提交后数据不会丢 | COMMIT 后宕机也应能恢复 |

### 4.3 并发事务的三个问题

| 问题 | 含义 |
|---|---|
| 脏读 | 读到其他事务未提交的数据 |
| 不可重复读 | 同一事务内两次读同一行,结果不同 |
| 幻读 | 同一事务内两次范围查询,行数不同 |

举例:

```text
脏读:事务 A 修改余额但未提交,事务 B 读到了这个未提交余额。
不可重复读:事务 A 第一次读余额 100,事务 B 提交修改为 200,事务 A 第二次读变成 200。
幻读:事务 A 查询 age > 18 有 10 行,事务 B 插入一条 age=20 并提交,事务 A 再查变成 11 行。
```

### 4.4 四种隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---|---|---|---|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 避免 | 可能 | 可能 |
| REPEATABLE READ | 避免 | 避免 | MySQL InnoDB 通常可避免 |
| SERIALIZABLE | 避免 | 避免 | 避免 |

MySQL InnoDB 默认隔离级别是 `REPEATABLE READ`。

查看隔离级别:

```sql
SELECT @@transaction_isolation;
```

设置当前会话隔离级别:

```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

### 4.5 面试表达

> 事务 ACID 是原子性、一致性、隔离性、持久性。并发事务常见问题有脏读、不可重复读、幻读。MySQL InnoDB 默认隔离级别是 REPEATABLE READ,通过 MVCC 和锁机制提升并发并保证一致性。

---

## 五、MVCC 与锁机制

### 5.1 MVCC 是什么

MVCC 是 Multi-Version Concurrency Control,多版本并发控制。

核心思想:

```text
写操作生成新版本。
读操作读取某个时间点的一致性快照。
读写尽量不互相阻塞。
```

面试表达:

> MVCC 让普通 SELECT 不需要加锁,而是通过版本链和 Read View 读取一致性快照,从而提高数据库并发性能。

### 5.2 快照读和当前读

| 类型 | 示例 | 特点 |
|---|---|---|
| 快照读 | `SELECT * FROM users WHERE id = 1` | 读一致性快照,通常不加锁 |
| 当前读 | `SELECT ... FOR UPDATE` | 读最新数据,并加锁 |

当前读示例:

```sql
START TRANSACTION;
SELECT * FROM orders WHERE id = 1 FOR UPDATE;
UPDATE orders SET status = 'paid' WHERE id = 1;
COMMIT;
```

### 5.3 常见锁类型

| 锁 | 含义 |
|---|---|
| 共享锁 S 锁 | 读锁,多个事务可以同时持有 |
| 排他锁 X 锁 | 写锁,同一时间只能一个事务持有 |
| 行锁 | 锁住命中的行 |
| 表锁 | 锁住整张表 |
| 间隙锁 Gap Lock | 锁住索引记录之间的间隙 |
| Next-Key Lock | 行锁 + 间隙锁 |

### 5.4 行锁和索引的关系

重要结论:

> InnoDB 通常在命中索引时加行锁;如果查询条件没有走索引,可能扫描并锁住更多记录,导致锁冲突扩大。

示例:

```sql
-- id 是主键,通常只锁一行
SELECT * FROM orders WHERE id = 100 FOR UPDATE;

-- status 没有索引时,可能扫描很多行,锁范围变大
SELECT * FROM orders WHERE status = 'created' FOR UPDATE;
```

### 5.5 死锁排查

查看 InnoDB 状态:

```sql
SHOW ENGINE INNODB STATUS;
```

常见死锁原因:

- 多个事务以不同顺序更新同一批数据。
- 长事务长期持有锁。
- 查询没走索引导致锁范围过大。
- 批量更新太多数据。

降低死锁概率:

- 保持固定的加锁顺序。
- 事务尽量短。
- WHERE 条件命中索引。
- 批量任务分批提交。

---

## 六、SQL 注入与参数化查询

### 6.1 什么是 SQL 注入

SQL 注入是把用户输入拼进 SQL 字符串后,用户输入被数据库当作 SQL 执行。

错误写法:

```python
name = request.args.get("name")
sql = f"SELECT * FROM users WHERE name = '{name}'"
cursor.execute(sql)
```

如果用户传入:

```text
' OR '1'='1
```

最终 SQL 可能变成:

```sql
SELECT * FROM users WHERE name = '' OR '1'='1'
```

这会绕过原本的查询条件。

### 6.2 正确做法:参数化查询

```python
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

参数化查询的核心:

```text
SQL 模板和用户输入分离。
用户输入只作为参数值,不会被当成 SQL 语法执行。
```

### 6.3 测开关注点

测试接口时可以关注:

- 登录、搜索、筛选接口是否存在 SQL 注入风险。
- 后端是否使用参数化查询。
- 错误响应中是否暴露 SQL 报错细节。
- 是否有统一输入校验和权限控制。

---

## 七、表结构、数据类型与约束

### 7.1 SQL 分类

| 类型 | 命令 | 作用 |
|---|---|---|
| DQL | `SELECT` | 查询数据 |
| DML | `INSERT` / `UPDATE` / `DELETE` | 增删改数据 |
| DDL | `CREATE` / `ALTER` / `DROP` | 定义表结构 |
| DCL | `GRANT` / `REVOKE` | 权限控制 |
| TCL | `COMMIT` / `ROLLBACK` | 事务控制 |

### 7.2 常用数据类型

| 类型 | 适合场景 | 注意点 |
|---|---|---|
| `INT` | 普通整数 | 用户数、年龄、状态码 |
| `BIGINT` | 大整数 | 雪花 ID、大数量计数 |
| `DECIMAL(10,2)` | 金额 | 金额不要用 FLOAT/DOUBLE |
| `VARCHAR(n)` | 短文本 | 用户名、手机号、邮箱 |
| `TEXT` | 长文本 | 文章内容、备注 |
| `DATETIME` | 日期时间 | 常用于业务时间 |
| `TIMESTAMP` | 时间戳 | 常用于创建/更新时间 |
| `TINYINT` | 小整数/布尔 | `0/1` 表示 false/true |
| `JSON` | 半结构化数据 | 不适合替代规范表设计 |

### 7.3 常见约束

| 约束 | 含义 |
|---|---|
| `PRIMARY KEY` | 主键,唯一且非空 |
| `UNIQUE` | 唯一约束 |
| `NOT NULL` | 不能为空 |
| `DEFAULT` | 默认值 |
| `FOREIGN KEY` | 外键约束 |
| `CHECK` | 检查约束 |
| `AUTO_INCREMENT` | 自增 |

建表示例:

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    age INT DEFAULT 0,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 7.4 COUNT 和 DISTINCT

```sql
-- 统计所有行
SELECT COUNT(*) FROM users;

-- 不统计 NULL
SELECT COUNT(email) FROM users;

-- 去重统计
SELECT COUNT(DISTINCT dept_id) FROM employees;
```

区别:

- `COUNT(*)` 统计所有行。
- `COUNT(column)` 不统计该列为 NULL 的行。
- `DISTINCT` 用于去重。

---

## 八、EXPLAIN 深入与慢 SQL 排查

原文已经讲了 `type` 和 `key`,这里补完整的慢 SQL 排查视角。

### 8.1 EXPLAIN 常看字段

```sql
EXPLAIN SELECT * FROM employees WHERE email = 'alice@test.com';
```

| 字段 | 关注点 |
|---|---|
| `id` | 查询执行层级,id 越大优先级越高 |
| `select_type` | 查询类型,如 SIMPLE、PRIMARY、SUBQUERY |
| `table` | 当前访问的表 |
| `type` | 访问类型,是否全表扫描 |
| `possible_keys` | 可能用到的索引 |
| `key` | 实际使用的索引 |
| `rows` | 预估扫描行数 |
| `Extra` | 额外信息,如 Using filesort、Using temporary |

### 8.2 type 从好到坏

常见顺序:

```text
system > const > eq_ref > ref > range > index > ALL
```

重点:

- `const`:通过主键或唯一索引查一行,很好。
- `ref`:普通索引等值查询,常见且不错。
- `range`:范围查询。
- `index`:扫描整个索引。
- `ALL`:全表扫描,需要重点关注。

### 8.3 Extra 常见危险信号

| Extra | 含义 |
|---|---|
| `Using filesort` | 需要额外排序,可能慢 |
| `Using temporary` | 使用临时表,常见于复杂 GROUP BY |
| `Using index` | 覆盖索引,通常是好事 |
| `Using where` | 使用 WHERE 过滤 |

### 8.4 慢 SQL 排查流程

```text
1. 定位慢接口或慢 SQL。
2. 用 EXPLAIN 看 type、key、rows、Extra。
3. 判断是否全表扫描、索引失效、扫描行数过多。
4. 检查 WHERE、JOIN、ORDER BY、GROUP BY 是否能利用索引。
5. 优化 SQL 或增加合适索引。
6. 再次 EXPLAIN 验证。
```

常用命令:

```sql
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
SHOW PROCESSLIST;
EXPLAIN SELECT ...;
EXPLAIN ANALYZE SELECT ...;
```

说明:

- `SHOW PROCESSLIST` 可以看当前正在执行的 SQL。
- `EXPLAIN ANALYZE` 会实际执行 SQL 并输出真实执行信息,生产谨慎使用。

---

## 九、联合索引、覆盖索引与分页优化

### 9.1 最左前缀原则

联合索引示例:

```sql
CREATE INDEX idx_a_b_c ON t(a, b, c);
```

可以较好使用索引:

```sql
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3
```

不能充分使用该联合索引:

```sql
WHERE b = 2
WHERE c = 3
```

面试金句:

> 联合索引从最左列开始连续匹配,跳过最左列通常无法利用该联合索引。

### 9.2 范围查询后的列可能用不上

```sql
CREATE INDEX idx_a_b_c ON t(a, b, c);

WHERE a = 1 AND b > 10 AND c = 3
```

通常可以利用 `a` 和 `b`,但 `c` 可能无法继续用于索引过滤。

### 9.3 覆盖索引

```sql
CREATE INDEX idx_name_age ON users(name, age);

SELECT name, age FROM users WHERE name = 'Alice';
```

如果查询字段都在索引里,数据库可以直接从索引返回结果,不需要再回表查询完整行,这叫覆盖索引。

### 9.4 回表

在 InnoDB 中,二级索引叶子节点保存的是主键值。通过二级索引找到主键后,再去聚簇索引查完整行,这个过程叫回表。

面试表达:

> 回表是通过二级索引找到主键后,再去聚簇索引查询完整数据行。覆盖索引可以避免回表,提升查询性能。

### 9.5 深分页问题

普通分页:

```sql
SELECT * FROM orders ORDER BY id LIMIT 100000, 20;
```

问题:

```text
数据库需要先扫描并丢弃前 100000 行,再返回 20 行。
偏移量越大,越慢。
```

优化方式 1:基于游标/上一页最大 id

```sql
SELECT * FROM orders
WHERE id > 100000
ORDER BY id
LIMIT 20;
```

优化方式 2:先查 id 再回表

```sql
SELECT o.*
FROM orders o
JOIN (
    SELECT id FROM orders ORDER BY id LIMIT 100000, 20
) t ON o.id = t.id;
```

---

## 十、SQL 高频面试题

### 10.1 查每个部门工资最高的员工

```sql
SELECT e.*
FROM employees e
JOIN (
    SELECT dept_id, MAX(salary) AS max_salary
    FROM employees
    GROUP BY dept_id
) t ON e.dept_id = t.dept_id AND e.salary = t.max_salary;
```

### 10.2 查每个部门薪资前三

使用窗口函数:

```sql
SELECT *
FROM (
    SELECT
        name,
        dept_id,
        salary,
        RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk
    FROM employees
) t
WHERE t.rnk <= 3;
```

窗口函数说明:

| 函数 | 含义 |
|---|---|
| `ROW_NUMBER()` | 连续排名,不并列 |
| `RANK()` | 并列排名,会跳号 |
| `DENSE_RANK()` | 并列排名,不跳号 |

### 10.3 查重复邮箱

```sql
SELECT email, COUNT(*) AS cnt
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

### 10.4 删除重复数据,保留最小 id

```sql
DELETE u1
FROM users u1
JOIN users u2
  ON u1.email = u2.email
 AND u1.id > u2.id;
```

执行删除前,建议先 SELECT 确认:

```sql
SELECT u1.*
FROM users u1
JOIN users u2
  ON u1.email = u2.email
 AND u1.id > u2.id;
```

### 10.5 查没有订单的用户

```sql
SELECT u.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

### 10.6 查每个用户最近一笔订单

```sql
SELECT *
FROM (
    SELECT
        o.*,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM orders o
) t
WHERE t.rn = 1;
```

### 10.7 查询第 N 高薪资

以第 3 高为例:

```sql
SELECT DISTINCT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 2;
```

### 10.8 连续登录 3 天用户

思路:用窗口函数给日期排序,把登录日期减去排名,连续日期会得到同一个分组值。

```sql
SELECT user_id
FROM (
    SELECT
        user_id,
        login_date,
        DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (
            PARTITION BY user_id ORDER BY login_date
        ) DAY) AS grp
    FROM user_login
) t
GROUP BY user_id, grp
HAVING COUNT(*) >= 3;
```

---

## 十一、测试数据管理与 pytest 事务回滚

测开经常需要准备数据、调用接口、验证数据库状态、清理数据。核心目标是:用例之间互不污染。

### 11.1 测试数据管理原则

- 每个用例准备自己的数据。
- 用例结束后清理或回滚。
- 不依赖线上真实数据。
- 避免用固定手机号、固定用户名导致重复冲突。
- 测试数据命名带明显前缀,如 `autotest_`。
- 删除数据前先确认范围。

### 11.2 用事务回滚隔离测试数据

```python
import pytest

@pytest.fixture
def db_conn(db_pool):
    conn = db_pool.connection()
    try:
        conn.begin()
        yield conn
        conn.rollback()
    finally:
        conn.close()
```

注意:

- 如果接口内部使用另一个连接并提交事务,测试侧 rollback 不一定能回滚接口写入的数据。
- 对接口自动化,更常见做法是测试前造数、测试后按唯一标识清理。

### 11.3 测试前造数,测试后清理

```python
@pytest.fixture
def test_user(db):
    email = "autotest_user_001@example.com"
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users(email, name) VALUES(%s, %s)",
        (email, "autotest_user")
    )
    db.commit()

    yield email

    cursor.execute("DELETE FROM users WHERE email = %s", (email,))
    db.commit()
```

### 11.4 验证数据库状态

```python
def test_create_order(api_client, db, test_user):
    resp = api_client.post("/orders", json={"email": test_user, "sku": "A001"})
    assert resp.status_code == 200

    cursor = db.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_email = %s", (test_user,))
    order = cursor.fetchone()
    assert order is not None
```

---

## 十二、主从复制、读写分离与主从延迟

### 12.1 主从复制

常见架构:

```text
应用写入 -> MySQL 主库
应用读取 -> MySQL 从库
主库数据 -> 异步复制到从库
```

作用:

- 主库负责写。
- 从库承担读请求。
- 提升读性能。
- 提供数据备份能力。

### 12.2 读写分离

读写分离可以降低主库压力,但会带来一致性问题。

典型问题:

```text
刚写入主库,马上从从库查询。
如果复制有延迟,从库可能还查不到最新数据。
```

### 12.3 主从延迟对测试的影响

测试中常见现象:

- 创建接口返回成功,立刻查列表查不到。
- 修改接口成功,立刻查详情还是旧值。
- 删除接口成功,立刻查询仍然存在。

处理方式:

- 强一致读取走主库。
- 测试断言加短暂重试。
- 明确接口读的是主库还是从库。
- 监控主从延迟。

示例重试断言:

```python
import time

def wait_until_found(query_func, timeout=3):
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = query_func()
        if result:
            return result
        time.sleep(0.2)
    return None
```

### 12.4 面试表达

> 主从复制用于读扩展和备份,读写分离可以降低主库压力。但主从复制通常存在延迟,所以刚写完马上读从库可能读不到最新数据。强一致场景应该读主库,测试自动化可以用短暂重试降低偶发失败。

---

## 十三、备份恢复基础

### 13.1 mysqldump 备份

```bash
mysqldump -h 127.0.0.1 -u root -p test_db > backup.sql
```

备份指定表:

```bash
mysqldump -h 127.0.0.1 -u root -p test_db users orders > tables.sql
```

### 13.2 恢复数据

```bash
mysql -h 127.0.0.1 -u root -p test_db < backup.sql
```

### 13.3 测开使用场景

- 测试环境重置前备份数据。
- 复现问题前保存现场。
- 导出小批量数据给开发定位。
- 恢复测试基线数据。

注意:

- 生产数据导出要脱敏。
- 不要把包含密码、手机号、身份证的数据直接放到代码仓库。
- 恢复前确认目标库,避免导错环境。

---

## 十四、连接池常见问题与排查

原文已经讲了连接池模型,这里补常见坑。

### 14.1 连接泄漏

现象:

```text
请求越来越慢。
连接池连接被借光。
后续请求一直等待连接。
```

常见原因:

- 借了连接没有 close。
- 异常分支没有归还连接。
- cursor 或事务未正确结束。

建议:

```python
conn = pool.connection()
try:
    ...
finally:
    conn.close()
```

### 14.2 连接池耗尽

可能原因:

- `maxconnections` 太小。
- 慢 SQL 占用连接太久。
- 连接泄漏。
- 并发量超过数据库承载能力。

排查思路:

- 看应用连接池日志。
- 看 MySQL 当前连接数。
- 用 `SHOW PROCESSLIST` 看是否有大量慢 SQL。
- 检查代码是否所有路径都归还连接。

### 14.3 wait_timeout 和 pool_recycle

MySQL 会关闭长时间空闲连接。应用连接池如果继续拿这个旧连接,可能报连接失效。

解决:

- 配置 `pool_recycle`,让连接定期重建。
- 借出连接前做连接有效性检查。

SQLAlchemy 示例:

```python
engine = create_engine(
    "mysql+pymysql://root:123456@127.0.0.1:3306/test_db",
    pool_size=10,
    max_overflow=5,
    pool_recycle=3600,
    pool_pre_ping=True,
)
```

### 14.4 池子不是越大越好

连接池太小会排队,太大会把数据库打满。

压测时要观察:

- 应用响应时间。
- 数据库 CPU。
- 数据库连接数。
- 慢 SQL 数量。
- 锁等待情况。

---

## 十五、面试问答模板

### Q1:"写一条复杂 SQL"(JOIN + GROUP BY + HAVING + ORDER BY)

> "查每个部门平均薪资大于 15000 的部门名称和平均薪资,按降序排列":
>
> ```sql
> SELECT d.dept_name, AVG(e.salary) AS avg_salary
> FROM employees e
> INNER JOIN departments d ON e.dept_id = d.id
> GROUP BY d.dept_name
> HAVING AVG(e.salary) > 15000
> ORDER BY AVG(e.salary) DESC;
> ```

### Q2:"索引为什么能加速?有什么缺点?什么时候不该加?"

> "索引用 B+ 树把 O(n) 的全表扫描变成 O(log n) 的树查找。100 万行数据,没索引扫 100 万次,有索引约 4 次。
>
> 缺点:占磁盘空间、拖慢写入(INSERT/UPDATE/DELETE 要同时更新索引)。本质是**用写入性能换读取性能**。
>
> 不该加的场景:写多读少的表(如日志)、数据量小于 1000 行、很少出现在 WHERE/JOIN 条件里的列。"

### Q3:"索引失效的常见场景?"

> "三大场景:
> 1. 对索引列做函数运算(如 `YEAR(create_time) = 2024`,应改成范围查询)
> 2. LIKE 前导通配符(如 `LIKE '%lice'`,应改成 `LIKE 'Ali%'`)
> 3. 隐式类型转换(如 VARCHAR 列用数字查)
>
> 排查方法:用 `EXPLAIN` 看 type 是否为 ALL(全表扫描)、key 是否为 NULL(没走索引)。"

### Q4:"为什么需要连接池?"

> "建立一次数据库连接要 TCP 握手 + 认证,约 5-7ms,而执行一条简单 SQL 只要 0.1ms。不用连接池,连接开销是查询本身的 **70 倍**。
>
> 连接池提前创建好一批连接,用的时候借、用完还,避免重复的握手和认证。本质上跟并发里的 Semaphore 是同一个模型——有限资源的排队复用。"

### Q5:"INNER JOIN 和 LEFT JOIN 的区别?"

> "INNER JOIN 只保留两张表能配对上的行(交集)。LEFT JOIN 保留左表所有行,配不上的右边填 NULL。
>
> 经典用法:用 LEFT JOIN + WHERE IS NULL 找'没有关联数据的记录',比如找没有部门的员工。"

### Q6:"WHERE 和 HAVING 的区别?"

> "WHERE 在 GROUP BY 之前,筛选行;HAVING 在 GROUP BY 之后,筛选组。HAVING 能用聚合函数(如 AVG、COUNT),WHERE 不能。"

### Q7:"事务的 ACID 是什么?"

> "ACID 是原子性、一致性、隔离性、持久性。原子性保证一组操作要么全成功要么全失败;一致性保证事务前后数据满足约束;隔离性保证并发事务之间互不干扰;持久性保证提交后的数据不会丢。"

### Q8:"脏读、不可重复读、幻读是什么?"

> "脏读是读到其他事务未提交的数据;不可重复读是同一事务内两次读取同一行结果不同;幻读是同一事务内两次范围查询行数不同。MySQL InnoDB 默认隔离级别是 REPEATABLE READ。"

### Q9:"MVCC 是什么?"

> "MVCC 是多版本并发控制。它通过版本链和 Read View 让普通 SELECT 读取某个时间点的一致性快照,避免读写互相阻塞,提升并发性能。"

### Q10:"联合索引的最左前缀原则是什么?"

> "联合索引从最左列开始连续匹配。比如索引 `(a,b,c)`,条件有 `a`、`a,b`、`a,b,c` 可以较好利用索引;如果只有 `b` 或 `c`,通常无法充分利用这个联合索引。"

### Q11:"什么是覆盖索引和回表?"

> "通过二级索引找到主键后,再去聚簇索引查完整行,这个过程叫回表。如果查询需要的字段都在索引里,数据库可以直接从索引返回结果,不需要回表,这叫覆盖索引。"

### Q12:"深分页为什么慢,怎么优化?"

> "`LIMIT 100000,20` 慢是因为数据库需要扫描并丢弃前 100000 行。优化方式可以用游标分页,比如 `WHERE id > last_id ORDER BY id LIMIT 20`,或者先查 ID 再回表。"

### Q13:"如何排查慢 SQL?"

> "先定位慢 SQL,再用 EXPLAIN 看 type、key、rows、Extra。重点关注是否全表扫描、是否没走索引、扫描行数是否过多、是否出现 Using filesort 或 Using temporary。优化后再用 EXPLAIN 验证。"

### Q14:"SQL 注入怎么防?"

> "不要把用户输入直接拼进 SQL,要使用参数化查询。参数化查询会把 SQL 模板和参数值分离,用户输入不会被当成 SQL 语法执行。"

### Q15:"主从延迟会导致什么测试问题?"

> "如果系统写主库、读从库,刚写完马上读从库可能读不到最新数据,导致接口自动化偶发失败。强一致场景应读主库,测试断言可以加短暂重试,同时确认接口读写链路。"
---

## 十六、关键代码模板

### 5.1 SQL 骨架

```sql
SELECT 列
FROM 表
JOIN 另一张表 ON 配对条件
WHERE 行级筛选
GROUP BY 分组
HAVING 组级筛选
ORDER BY 排序
LIMIT 数量;
```

### 5.2 建索引

```sql
CREATE INDEX idx_email ON employees(email);
CREATE INDEX idx_dept_salary ON employees(dept_id, salary);
```

### 5.3 查看是否走索引

```sql
EXPLAIN SELECT * FROM employees WHERE email = 'alice@test.com';
-- 看 type 和 key 两列
```

### 5.4 pymysql + 连接池

```python
from dbutils.pooled_db import PooledDB
import pymysql

pool = PooledDB(
    creator=pymysql,
    maxconnections=10,
    host='127.0.0.1',
    port=3306,
    user='root',
    password='123456',
    database='test_db',
    charset='utf8mb4',
)

def query(sql, params=None):
    conn = pool.connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        conn.close()    # 还回池子,不是真关闭
```

### 5.5 pytest + 连接池 fixture

```python
# conftest.py
@pytest.fixture(scope="session")
def db_pool():
    pool = PooledDB(creator=pymysql, maxconnections=5, ...)
    yield pool

@pytest.fixture
def db(db_pool):
    conn = db_pool.connection()
    yield conn
    conn.close()
```

### 16.6 事务模板

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
-- ROLLBACK;
```

### 16.7 参数化查询

```python
cursor.execute(
    "SELECT * FROM users WHERE email = %s AND status = %s",
    (email, status)
)
```

### 16.8 窗口函数:分组 Top N

```sql
SELECT *
FROM (
    SELECT
        name,
        dept_id,
        salary,
        ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn
    FROM employees
) t
WHERE t.rn <= 3;
```

### 16.9 深分页优化

```sql
SELECT * FROM orders
WHERE id > 100000
ORDER BY id
LIMIT 20;
```

### 16.10 pytest 测试数据清理

```python
@pytest.fixture
def test_user(db):
    email = "autotest_user@example.com"
    cursor = db.cursor()
    cursor.execute("INSERT INTO users(email, name) VALUES(%s, %s)", (email, "autotest"))
    db.commit()

    yield email

    cursor.execute("DELETE FROM users WHERE email = %s", (email,))
    db.commit()
```
---

## 十七、命令速查表

### SQL 分类

| 类型 | 命令 | 用途 |
|---|---|---|
| DQL | SELECT | 查询 |
| DML | INSERT / UPDATE / DELETE | 增删改 |
| DDL | CREATE / ALTER / DROP | 表结构 |
| DCL | GRANT / REVOKE | 权限 |
| TCL | COMMIT / ROLLBACK | 事务 |

### 事务与锁

| 命令 | 用途 |
|---|---|
| START TRANSACTION | 开启事务 |
| COMMIT | 提交事务 |
| ROLLBACK | 回滚事务 |
| SELECT ... FOR UPDATE | 当前读并加排他锁 |
| SHOW ENGINE INNODB STATUS | 查看 InnoDB 状态和死锁信息 |

### 索引与慢 SQL

| 命令 | 用途 |
|---|---|
| CREATE INDEX idx_col ON table(col) | 创建索引 |
| EXPLAIN SELECT ... | 查看执行计划 |
| EXPLAIN ANALYZE SELECT ... | 查看实际执行计划 |
| SHOW PROCESSLIST | 查看当前连接和执行 SQL |
| SHOW VARIABLES LIKE 'slow_query_log' | 查看慢查询日志是否开启 |
| SHOW VARIABLES LIKE 'long_query_time' | 查看慢查询阈值 |

### 备份恢复

| 命令 | 用途 |
|---|---|
| mysqldump -h host -u user -p db > backup.sql | 备份数据库 |
| mysql -h host -u user -p db < backup.sql | 恢复数据库 |

---

## 附录:数据库知识在测开工作中的应用场景

| 场景 | 用到的知识 |
|---|---|
| 写接口自动化:验证数据库状态 | SQL 查询 + pytest fixture |
| 造测试数据 | INSERT + 事务回滚 |
| 排查线上慢接口 | EXPLAIN + 索引优化 |
| 框架里管理数据库连接 | 连接池 + scope 设计 |
| 压测时数据库成为瓶颈 | 连接池参数调优 |
| 面试手写 SQL | JOIN + GROUP BY + HAVING 组合 |

---

*数据库核心知识:SQL + 索引 + 事务 + 连接池增强版 —— 完结。*

