# Redis 笔记:测开面试核心

## 目录

- [一、Redis 是什么](#一redis-是什么)
- [二、五种基础数据类型](#二五种基础数据类型)
- [三、三个重要特性](#三三个重要特性)
- [四、测开常用场景](#四测开常用场景)
- [五、缓存三大问题(面试必考)](#五缓存三大问题面试必考)
- [六、缓存更新策略与一致性](#六缓存更新策略与一致性)
- [七、分布式锁的正确实现](#七分布式锁的正确实现)
- [八、redis-cli 常用排查命令](#八redis-cli-常用排查命令)
- [九、Redis 内存淘汰与过期删除](#九redis-内存淘汰与过期删除)
- [十、Redis 持久化详解](#十redis-持久化详解)
- [十一、Redis 高可用:主从、哨兵、集群](#十一redis-高可用主从哨兵集群)
- [十二、性能排查:慢查询、大 Key、热 Key](#十二性能排查慢查询大-key热-key)
- [十三、事务、Lua 与 Pub/Sub](#十三事务lua-与-pubsub)
- [十四、扩展数据类型](#十四扩展数据类型)
- [十五、生产安全注意事项](#十五生产安全注意事项)
- [十六、面试问答模板](#十六面试问答模板)
- [十七、命令速查表](#十七命令速查表)
---

## 一、Redis 是什么

### 1.1 核心画面

```
没有 Redis:
请求 → 应用 → MySQL(硬盘) → 返回    耗时 10~100ms

有 Redis:
请求 → 应用 → Redis(内存) → 返回    耗时 0.1ms  ← 缓存命中
                  ↓ 没找到
              MySQL → 存入 Redis → 返回
              下次直接从 Redis 拿
```

> **Redis 一句话**:基于内存的键值数据库,读写速度极快(微秒级),主要用于缓存、会话管理、消息队列、排行榜等场景。

### 1.2 Redis vs MySQL

| | Redis | MySQL |
|---|---|---|
| 存储位置 | 内存 | 硬盘 |
| 读写速度 | 微秒级(0.1ms) | 毫秒级(10~100ms) |
| 数据结构 | String/Hash/List/Set/ZSet | 表格 |
| 数据持久性 | 可选(RDB/AOF) | 强持久化 |
| 适合场景 | 高频读、临时数据 | 持久化存储、复杂查询 |

### 1.3 Key 命名惯例

```bash
# 用冒号分隔，表示层级结构
user:1                    # 用户 1 的信息
user:token:abc123         # 用户 token
rate:user_1:202505231430  # 用户限流计数
order:lock:create         # 订单创建分布式锁
```

---

## 二、五种基础数据类型

### 2.1 String(字符串)——最基础最常用

```bash
# 基本操作
SET name "Alice"
GET name                      # → "Alice"
DEL name

# ⭐ 设置过期时间(缓存必用)
SET token "abc123" EX 3600    # 1 小时后自动过期
TTL token                     # 查看剩余秒数

# ⭐ 计数器(原子操作,无并发问题)
SET page_views 0
INCR page_views               # → 1
INCRBY page_views 10          # → 11
```

**适合场景**:缓存用户信息、session、计数器、限流。

### 2.2 Hash(哈希)——存对象

```bash
# 存用户对象
HSET user:1 name "Alice" age 28 email "alice@test.com"

# 取单个字段
HGET user:1 name              # → "Alice"

# 取所有字段
HGETALL user:1

# 只修改某个字段(不影响其他)
HSET user:1 age 29

# 删除某个字段
HDEL user:1 email
```

**为什么用 Hash 而不是 String 存对象?**

String 存整个 JSON,改一个字段要全部取出再存回去。Hash 可以单独修改某个字段,**更高效,更灵活**。

**适合场景**:存用户信息、商品信息等有多个字段的对象。

### 2.3 List(列表)——队列/栈

```bash
# 从左插入
LPUSH messages "消息1"
LPUSH messages "消息2"    # [消息2, 消息1]

# 从右插入
RPUSH messages "消息3"    # [消息2, 消息1, 消息3]

# 从左取出(消费)
LPOP messages             # → "消息2"

# 查看全部
LRANGE messages 0 -1

# ⭐ 阻塞式取出(没数据就等待,消息队列用)
BLPOP messages 30         # 最多等 30 秒
```

**适合场景**:消息队列(LPUSH + BRPOP)、最新 N 条动态。

### 2.4 Set(集合)——去重

```bash
# 添加(自动去重)
SADD online_users "Alice"
SADD online_users "Bob"
SADD online_users "Alice"    # 重复,忽略

# 查看所有
SMEMBERS online_users

# 判断是否存在
SISMEMBER online_users "Alice"    # → 1(是)

# ⭐ 交集(共同好友)
SINTER user1_friends user2_friends

# 并集/差集
SUNION set1 set2
SDIFF set1 set2
```

**适合场景**:在线用户、标签系统、共同好友。

### 2.5 ZSet(有序集合)——排行榜 ⭐ 面试必考

每个元素有一个**分数(score)**,按分数自动排序。

```bash
# 添加元素(分数 + 值)
ZADD leaderboard 100 "Alice"
ZADD leaderboard 200 "Bob"
ZADD leaderboard 150 "Charlie"

# 按分数升序取出
ZRANGE leaderboard 0 -1 WITHSCORES
# → Alice 100, Charlie 150, Bob 200

# ⭐ 按分数降序取出(排行榜)
ZREVRANGE leaderboard 0 -1 WITHSCORES
# → Bob 200, Charlie 150, Alice 100

# 取 Top 3
ZREVRANGE leaderboard 0 2 WITHSCORES

# 增加分数
ZINCRBY leaderboard 50 "Alice"    # Alice: 100 → 150

# 查看某人排名(0 是第一名)
ZREVRANK leaderboard "Bob"        # → 0
```

> **面试金句**:"ZSet 用跳表实现,插入/查询都是 O(log n),是实现实时排行榜最自然的数据结构。"

**适合场景**:游戏排行榜、热搜榜、优先级队列。

---

## 三、三个重要特性

### 3.1 过期时间(TTL)

```bash
SET key value EX 3600     # 存时设置过期(推荐)
EXPIRE key 3600           # 对已有 key 设置过期

TTL key     # 查看剩余秒数
            # -1 = 永不过期
            # -2 = 已过期或不存在

PERSIST key # 取消过期时间(变成永久)
```

### 3.2 原子操作

**Redis 是单线程的**——所有命令串行执行,天然避免并发冲突。

```bash
INCR counter    # 原子自增,多个客户端同时调用不会冲突
```

对比你学过的 Python 并发:
- Python `counter += 1` → 非原子,多线程要加 Lock
- Redis `INCR` → 原子,天然线程安全

### 3.3 持久化

| 方式 | 特点 | 适合 |
|---|---|---|
| **RDB** | 定期快照,文件小,重启快 | 备份,允许少量数据丢失 |
| **AOF** | 记录每条写命令,数据完整 | 数据安全要求高 |
| **混合** | RDB + AOF 结合(推荐) | 生产环境 |

---

## 四、测开常用场景

### 场景 1:Session 管理(你学的第一道题)

```python
import redis
import uuid

r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

def create_session(user_id):
    """用户登录后创建 session"""
    token = str(uuid.uuid4())
    r.set(f"user:token:{token}", user_id, ex=1800)  # 30 分钟过期
    return token

def get_session(token):
    """验证 session"""
    user_id = r.get(f"user:token:{token}")
    if user_id:
        r.expire(f"user:token:{token}", 1800)  # 重置过期时间
    return user_id
```

### 场景 2:接口限流

```python
import time

def check_rate_limit(user_id, limit=100):
    """每分钟最多 100 次请求"""
    key = f"rate:{user_id}:{time.strftime('%Y%m%d%H%M')}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)    # 第一次设置过期
    return count <= limit

# 使用
if not check_rate_limit(user_id):
    return {"error": "请求过于频繁,请稍后重试"}
```

### 场景 3:缓存数据库查询

```python
import json

def get_user(user_id):
    """先查 Redis,没有再查 MySQL"""
    cache_key = f"user:{user_id}"

    # 1. 查 Redis
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)    # 缓存命中

    # 2. 查 MySQL
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    if not user:
        r.set(cache_key, "", ex=60)  # 防止缓存穿透:存空值
        return None

    # 3. 存入 Redis
    r.set(cache_key, json.dumps(user), ex=3600)
    return user
```

### 场景 4:分布式锁(面试高频)

```python
import uuid

LOCK_RELEASE_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""

def acquire_lock(lock_key, expire=10):
    """
    SET key value NX EX 10
    NX = 只有 key 不存在时才设置(原子操作)
    EX = 过期时间,防止程序崩溃导致死锁
    value = 唯一标识,防止误删别人的锁
    """
    lock_value = str(uuid.uuid4())
    ok = r.set(lock_key, lock_value, nx=True, ex=expire)
    return lock_value if ok else None

def release_lock(lock_key, lock_value):
    """释放锁时先判断 value,再删除;Lua 保证判断和删除是原子操作。"""
    return r.eval(LOCK_RELEASE_SCRIPT, 1, lock_key, lock_value)

# 使用
lock_key = "order:create:lock"
lock_value = acquire_lock(lock_key, expire=10)
if lock_value:
    try:
        create_order()
    finally:
        release_lock(lock_key, lock_value)
else:
    return "系统繁忙,请稍后重试"
```

> **金句**:"Redis 分布式锁用 `SET key value NX EX` 获取锁。NX 保证只有一个客户端能设置成功,EX 防止死锁,value 必须是唯一标识。释放锁时要先校验 value 再删除,并用 Lua 保证原子性,避免误删其他客户端的锁。"

### 场景 5:排行榜

```python
def add_score(user_id, score):
    """增加用户分数"""
    r.zincrby("game:leaderboard", score, user_id)

def get_top_10():
    """获取 Top 10"""
    return r.zrevrange("game:leaderboard", 0, 9, withscores=True)

def get_rank(user_id):
    """获取用户排名(从 1 开始)"""
    rank = r.zrevrank("game:leaderboard", user_id)
    return rank + 1 if rank is not None else None
```

---

## 五、缓存三大问题(面试必考)

### 5.1 缓存穿透

```
现象:请求一个数据库里也没有的 key
     → Redis 没有 → 每次都打到 MySQL → MySQL 被打垮

解决:查 MySQL 也没有时,在 Redis 存一个空值
     r.set(key, "", ex=60)    # 存空值,60 秒过期
```

### 5.2 缓存击穿

```
现象:热点 key 过期的一瞬间
     → 大量请求同时打到 MySQL → MySQL 被打垮

解决:
方案 1:热点 key 不设过期时间(手动更新)
方案 2:用分布式锁,只让一个请求去重建缓存
```

### 5.3 缓存雪崩

```
现象:大量 key 同时过期(比如同一时间批量导入的数据)
     → 大量请求同时打到 MySQL → MySQL 被打垮

解决:过期时间加随机值,避免同时过期
     ex = 3600 + random.randint(0, 600)
```

### 一句话总结三个问题

| 问题 | 触发原因 | 解决方案 |
|---|---|---|
| 穿透 | 查询不存在的数据 | 存空值 |
| 击穿 | 热点 key 突然过期 | 不过期 or 分布式锁 |
| 雪崩 | 大量 key 同时过期 | 过期时间加随机值 |

---

## 六、缓存更新策略与一致性

Redis 最常见的工程问题不是“怎么存”,而是“缓存和数据库怎么保持尽量一致”。

### 6.1 Cache Aside Pattern(旁路缓存)

这是业务系统最常用的缓存模式。

读流程:

```text
1. 先查 Redis。
2. Redis 命中,直接返回。
3. Redis 未命中,查 MySQL。
4. MySQL 查到后,写入 Redis。
5. 返回结果。
```

写流程:

```text
1. 先更新 MySQL。
2. 再删除 Redis 缓存。
3. 下次读取时重新从 MySQL 加载到 Redis。
```

典型代码:

```python
def update_user(user_id, data):
    db.update("users", user_id, data)
    r.delete(f"user:{user_id}")
```

### 6.2 为什么通常是删除缓存,不是更新缓存?

因为并发情况下直接更新缓存更容易写入旧值。

常用做法是:

```text
更新数据库 -> 删除缓存
```

这样下一次读请求会重新从数据库加载最新数据。

### 6.3 先删缓存还是先更新数据库?

推荐:

```text
先更新数据库,再删除缓存
```

原因:

- 如果先删缓存,还没更新数据库时来了读请求,会把旧数据重新写回缓存。
- 先更新数据库再删缓存,即使短暂不一致,窗口也更小。

### 6.4 延迟双删

在高并发场景,可以使用延迟双删降低旧数据回写缓存的概率。

```text
1. 删除缓存。
2. 更新数据库。
3. 等待一小段时间。
4. 再删除缓存一次。
```

示例:

```python
def update_user_with_double_delete(user_id, data):
    key = f"user:{user_id}"
    r.delete(key)
    db.update("users", user_id, data)
    time.sleep(0.5)
    r.delete(key)
```

注意:延迟双删不是强一致方案,只是降低并发下脏缓存概率。

### 6.5 面试表达

> 缓存和数据库很难做到绝对强一致。常用方案是 Cache Aside:读时先缓存,未命中再查数据库并写回;写时先更新数据库,再删除缓存。删除缓存比更新缓存更稳,可以避免并发场景下把旧值写回缓存。对一致性要求高的业务,可以配合消息队列、binlog 订阅或延迟双删。

---

## 七、分布式锁的正确实现

前面已经介绍了 `SET key value NX EX seconds`。这里重点补充生产实现细节。

### 7.1 为什么不能直接 DEL 释放锁?

错误写法:

```python
r.set(lock_key, "locked", nx=True, ex=10)
# 执行业务
r.delete(lock_key)
```

风险场景:

```text
1. A 拿到锁,过期时间 10 秒。
2. A 执行业务超过 10 秒,锁自动过期。
3. B 拿到同一个锁。
4. A 执行结束后 DEL lock_key。
5. B 的锁被 A 误删。
```

### 7.2 正确方式:唯一 value + Lua 删除

```python
import uuid

lock_key = "order:create:lock"
lock_value = str(uuid.uuid4())

ok = r.set(lock_key, lock_value, nx=True, ex=10)
```

释放锁:

```python
lua = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""

r.eval(lua, 1, lock_key, lock_value)
```

为什么用 Lua?

```text
GET 判断 value 和 DEL 删除 key 必须是一个原子操作。
如果先 GET 再 DEL,中间锁可能过期并被别人拿到。
Lua 脚本在 Redis 中会作为一个整体执行,可以保证原子性。
```

### 7.3 分布式锁注意点

- 锁必须设置过期时间,防止死锁。
- value 必须唯一,防止误删别人的锁。
- 释放锁必须校验 value。
- 校验和删除要用 Lua 保证原子性。
- 业务执行时间不能长期超过锁过期时间。
- 复杂生产场景可使用 Redisson,支持看门狗自动续期。

### 7.4 面试表达

> Redis 分布式锁核心是 `SET key value NX EX seconds`。NX 保证互斥,EX 防止死锁,value 使用 UUID 防止误删。释放锁时不能直接 DEL,必须先判断 value 是否属于自己,再删除,并用 Lua 保证判断和删除的原子性。

---

## 八、redis-cli 常用排查命令

### 8.1 连接 Redis

```bash
# 本机连接
redis-cli

# 指定 host 和 port
redis-cli -h 127.0.0.1 -p 6379

# 指定密码
redis-cli -h 127.0.0.1 -p 6379 -a password
```

进入后常用命令:

```bash
PING                 # 测试连通性,返回 PONG
AUTH password        # 认证
SELECT 1             # 切换 DB
DBSIZE               # 当前 DB key 数量
INFO                 # 查看 Redis 整体信息
```

### 8.2 通用 key 命令

```bash
EXISTS key           # 判断 key 是否存在
TYPE key             # 查看 key 类型
TTL key              # 查看剩余过期时间
EXPIRE key 60        # 设置 60 秒过期
DEL key              # 删除 key
RENAME old new       # 重命名 key
```

危险命令:

```bash
FLUSHDB              # 清空当前 DB
FLUSHALL             # 清空所有 DB
```

生产环境不要随便执行清空命令。

### 8.3 KEYS 和 SCAN

```bash
KEYS user:*          # 查匹配 key,生产慎用
```

`KEYS` 会一次性扫描整个 key 空间,数据量大时可能阻塞 Redis。

生产推荐使用 `SCAN`:

```bash
SCAN 0 MATCH user:* COUNT 100
```

说明:

- `SCAN` 是渐进式扫描。
- 每次返回一批 key 和下一次 cursor。
- cursor 变成 `0` 表示扫描完成。

### 8.4 查看配置和状态

```bash
INFO memory
INFO clients
INFO stats
INFO replication
CONFIG GET maxmemory
CONFIG GET maxmemory-policy
CLIENT LIST
```

常见用途:

- `INFO memory`:看内存使用。
- `INFO clients`:看客户端连接。
- `INFO replication`:看主从状态。
- `CONFIG GET maxmemory-policy`:看内存淘汰策略。

---

## 九、Redis 内存淘汰与过期删除

### 9.1 Redis 怎么删除过期 key?

Redis 不是 key 一过期就立刻删除,主要有两种策略:

| 策略 | 含义 |
|---|---|
| 惰性删除 | 访问 key 时发现过期,再删除 |
| 定期删除 | Redis 周期性抽样检查部分 key,删除过期 key |

这样做是为了平衡性能。如果每个 key 到期都立刻删除,会造成大量定时任务和额外开销。

### 9.2 内存满了怎么办?

当 Redis 达到 `maxmemory` 限制时,会根据 `maxmemory-policy` 决定是否淘汰 key。

查看配置:

```bash
CONFIG GET maxmemory
CONFIG GET maxmemory-policy
```

### 9.3 常见淘汰策略

| 策略 | 含义 |
|---|---|
| `noeviction` | 不淘汰,key 写入时报错 |
| `allkeys-lru` | 从所有 key 中淘汰最近最少使用的 key |
| `volatile-lru` | 从设置了过期时间的 key 中淘汰最近最少使用的 key |
| `allkeys-random` | 从所有 key 中随机淘汰 |
| `volatile-random` | 从设置了过期时间的 key 中随机淘汰 |
| `volatile-ttl` | 从设置了过期时间的 key 中优先淘汰 TTL 更短的 key |
| `allkeys-lfu` | 从所有 key 中淘汰最少使用的 key |
| `volatile-lfu` | 从设置了过期时间的 key 中淘汰最少使用的 key |

### 9.4 面试表达

> Redis 过期 key 主要靠惰性删除和定期删除。内存不够时,Redis 会根据 maxmemory-policy 执行淘汰策略。缓存场景常用 allkeys-lru 或 allkeys-lfu,前者淘汰最近最少使用,后者淘汰访问频率最低。

---

## 十、Redis 持久化详解

### 10.1 RDB

RDB 是快照持久化,会在某个时间点把内存数据生成一个快照文件。

优点:

- 文件紧凑,适合备份。
- 恢复速度快。
- 对运行时性能影响相对小。

缺点:

- 两次快照之间的数据可能丢失。
- 数据安全性不如 AOF。

适合场景:

- 允许丢失少量数据。
- 做备份和灾难恢复。

### 10.2 AOF

AOF 会记录每条写命令。

优点:

- 数据更完整。
- 可以配置每秒刷盘,最多丢 1 秒数据。

缺点:

- 文件通常比 RDB 大。
- 恢复速度可能更慢。
- 需要 AOF rewrite 压缩文件。

### 10.3 AOF rewrite

AOF 长期记录写命令会越来越大。Redis 会通过 AOF rewrite 重写日志,把多条历史命令压缩成当前数据状态所需的最少命令。

例如:

```text
INCR counter
INCR counter
INCR counter
```

可以重写成:

```text
SET counter 3
```

### 10.4 混合持久化

生产常见配置是 RDB + AOF 混合持久化。

| 方式 | 优点 | 缺点 |
|---|---|---|
| RDB | 恢复快,文件小 | 可能丢较多数据 |
| AOF | 数据更完整 | 文件大,恢复慢 |
| 混合持久化 | 兼顾恢复速度和数据完整性 | 配置和理解成本更高 |

---

## 十一、Redis 高可用:主从、哨兵、集群

### 11.1 主从复制

```text
Master 负责写
Slave 复制 Master 数据,可以承担读请求
```

作用:

- 数据备份。
- 读写分离。
- 提升读性能。

缺点:

- 主节点宕机后,需要故障转移。
- 主从复制可能有延迟。

### 11.2 哨兵 Sentinel

Sentinel 用于监控 Redis 主从节点,并在主节点故障时自动选举新的主节点。

作用:

- 监控主从节点是否存活。
- 主节点宕机时自动故障转移。
- 通知客户端新的主节点地址。

面试表达:

> 主从复制解决数据备份和读扩展,Sentinel 解决主节点故障后的自动切换。

### 11.3 Redis Cluster

Redis Cluster 用于分片存储,解决单机容量和性能上限。

核心点:

- Redis Cluster 有 16384 个 slot。
- 每个 key 会根据 hash 映射到某个 slot。
- 不同节点负责不同 slot。
- Cluster 支持横向扩容。

面试表达:

> Redis Cluster 通过 16384 个槽位做数据分片。key 根据 hash 映射到 slot,slot 分布在不同节点上,从而突破单机内存和性能限制。

### 11.4 三种架构对比

| 架构 | 解决问题 | 说明 |
|---|---|---|
| 单机 | 简单缓存 | 有单点风险 |
| 主从 + Sentinel | 高可用 | 主故障可自动切换 |
| Cluster | 分片 + 高可用 | 适合大容量和高并发 |

---

## 十二、性能排查:慢查询、大 Key、热 Key

### 12.1 慢查询

```bash
# 查看最近 10 条慢查询
SLOWLOG GET 10

# 查看慢查询数量
SLOWLOG LEN

# 清空慢查询日志
SLOWLOG RESET
```

慢查询常见原因:

- 大 key 操作。
- 一次返回太多数据。
- 使用了阻塞命令。
- Redis 所在机器 CPU 或网络异常。

### 12.2 大 Key(Big Key)

Big Key 指 value 很大或集合元素非常多的 key。

风险:

- 网络传输慢。
- 删除可能阻塞。
- 主从同步压力大。
- Cluster 下可能造成数据倾斜。

排查命令:

```bash
MEMORY USAGE key     # 查看 key 占用内存
STRLEN key           # String 长度
LLEN key             # List 长度
HLEN key             # Hash 字段数
SCARD key            # Set 元素数
ZCARD key            # ZSet 元素数
```

处理思路:

- 拆分大 key。
- 控制集合长度。
- 删除大 key 用异步删除 `UNLINK`。
- 避免一次性 `HGETALL`、`SMEMBERS` 拉取超大集合。

### 12.3 热 Key(Hot Key)

Hot Key 指某个 key 被大量请求集中访问。

风险:

- 单个 Redis 节点流量被打满。
- 应用大量等待 Redis 响应。
- Cluster 下某个分片压力过大。

解决思路:

- 本地缓存。
- 热 key 副本拆分,例如 `hot:key:1`、`hot:key:2`。
- 提前预热缓存。
- 限流和降级。

### 12.4 Redis 响应慢排查模型

```text
1. INFO memory 看内存是否接近上限。
2. SLOWLOG GET 看是否有慢命令。
3. CLIENT LIST 看连接数是否异常。
4. 检查是否有 KEYS、HGETALL、SMEMBERS 等大范围命令。
5. 检查网络、CPU、磁盘和主从复制延迟。
```

常用命令:

```bash
INFO memory
INFO clients
INFO stats
SLOWLOG GET 10
CLIENT LIST
CONFIG GET maxmemory-policy
```

---

## 十三、事务、Lua 与 Pub/Sub

### 13.1 Redis 事务

Redis 事务使用 `MULTI`、`EXEC`。

```bash
MULTI
SET a 1
INCR counter
EXEC
```

特点:

- 命令会按顺序执行。
- 执行过程中不会被其他客户端命令插入。
- Redis 事务不支持 MySQL 那种自动回滚。

### 13.2 Lua 脚本

Lua 可以让多条 Redis 命令作为一个整体原子执行。

常见用途:

- 分布式锁释放。
- 限流。
- 库存扣减。
- 多 key 条件判断。

示例:

```bash
EVAL "return redis.call('get', KEYS[1])" 1 name
```

### 13.3 Pub/Sub 发布订阅

订阅:

```bash
SUBSCRIBE channel1
```

发布:

```bash
PUBLISH channel1 "hello"
```

注意:

> Pub/Sub 不持久化消息。消费者不在线时会丢消息。如果需要可靠消息队列,优先考虑 Redis Stream 或专业 MQ。

---

## 十四、扩展数据类型

除了 String、Hash、List、Set、ZSet,Redis 还提供了一些高级数据类型。

| 类型 | 适合场景 | 常用命令 |
|---|---|---|
| Bitmap | 签到、活跃状态、布尔统计 | `SETBIT`、`GETBIT`、`BITCOUNT` |
| HyperLogLog | UV 去重统计 | `PFADD`、`PFCOUNT` |
| Stream | 消息队列 | `XADD`、`XREAD`、`XGROUP` |
| Geo | 附近的人、门店距离 | `GEOADD`、`GEODIST`、`GEOSEARCH` |
| Bitfield | 多位整数状态存储 | `BITFIELD` |

### 14.1 Bitmap:签到

```bash
# 用户 1 第 5 天签到
SETBIT user:sign:1 5 1

# 查看第 5 天是否签到
GETBIT user:sign:1 5

# 统计签到次数
BITCOUNT user:sign:1
```

### 14.2 HyperLogLog:UV 统计

```bash
PFADD uv:20250523 user1 user2 user3
PFCOUNT uv:20250523
```

特点:

- 占用内存很小。
- 适合统计不需要绝对精确的 UV。
- 有一定误差。

### 14.3 Stream:消息队列

```bash
# 写入消息
XADD mq:orders * order_id 1001 status created

# 读取消息
XREAD COUNT 1 STREAMS mq:orders 0
```

Stream 比 List 更适合作为消息队列,支持消息 ID、消费者组、消息确认等能力。

### 14.4 Geo:地理位置

```bash
GEOADD shops 116.397128 39.916527 shop1
GEODIST shops shop1 shop2 km
GEOSEARCH shops FROMMEMBER shop1 BYRADIUS 5 km
```

---

## 十五、生产安全注意事项

### 15.1 不要公网裸奔

Redis 不应该直接暴露在公网。

建议:

- 绑定内网 IP。
- 开启密码认证。
- 使用安全组或防火墙限制访问来源。
- 开启 protected-mode。

查看配置:

```bash
CONFIG GET bind
CONFIG GET protected-mode
CONFIG GET requirepass
```

### 15.2 慎用危险命令

危险命令:

```bash
KEYS *
FLUSHDB
FLUSHALL
CONFIG
EVAL
SHUTDOWN
```

生产建议:

- 避免使用 `KEYS *`,改用 `SCAN`。
- 禁止普通账号执行清库命令。
- 必要时通过配置 rename-command 禁用危险命令。

### 15.3 测开操作 Redis 的注意事项

- 操作前确认环境:本地、测试、预发还是生产。
- 删除 key 前先确认 key 类型和业务含义。
- 不要在生产执行 `FLUSHDB`、`FLUSHALL`。
- 查大范围 key 用 `SCAN`,不要用 `KEYS *`。
- 压测前确认 Redis 容量、连接数和淘汰策略。

---

## 十六、面试问答模板

### Q1:"Redis 和 MySQL 的区别?"

> "Redis 基于内存,读写速度微秒级,适合高频读、临时数据。MySQL 基于硬盘,读写毫秒级,适合持久化存储和复杂查询。实际项目里两者配合使用——MySQL 存全量数据,Redis 缓存热点数据,大幅提升读取性能。"

### Q2:"Redis 有哪些数据类型,分别用在什么场景?"

> "五种:
> - String:缓存、session、计数器
> - Hash:存对象(用户信息、商品信息)
> - List:消息队列、最新动态
> - Set:去重、共同好友
> - ZSet:排行榜(按分数自动排序,O(log n),是实现排行榜最自然的结构)"

### Q3:"缓存穿透、击穿、雪崩的区别?"

> "穿透是查询根本不存在的数据,解决方案是存空值。击穿是热点 key 过期一瞬间大量请求涌入,解决方案是不设过期或用分布式锁。雪崩是大量 key 同时过期,解决方案是过期时间加随机值。三个问题都会导致 MySQL 被打垮,但原因和解法不同。"

### Q4:"Redis 分布式锁怎么实现?"

> "用 `SET key value NX EX seconds`。NX 保证只有 key 不存在时才能设置——这是原子操作,保证同一时间只有一个客户端能拿到锁。EX 设置过期时间,保证程序崩溃后锁自动释放,不会产生死锁。释放锁时直接 `DEL key`。"

### Q5:"Redis 为什么快?"

> "三个原因:基于内存(比硬盘快 1000 倍);单线程模型(避免了线程切换和锁竞争);数据结构简单高效(跳表、哈希表等)。单线程不代表慢,因为瓶颈在 I/O 不在 CPU,单线程反而减少了上下文切换开销。"

### Q6:"生产环境为什么不建议用 KEYS *?"

> "`KEYS *` 会一次性扫描整个 key 空间,如果 Redis 里 key 很多,会阻塞 Redis 主线程,影响线上请求。生产环境应该用 `SCAN` 渐进式扫描,例如 `SCAN 0 MATCH user:* COUNT 100`。"

### Q7:"缓存和数据库如何保持一致?"

> "常用 Cache Aside 模式。读时先查缓存,未命中再查数据库并写回缓存;写时先更新数据库,再删除缓存。删除缓存而不是更新缓存,是为了减少并发场景下旧数据写回缓存的风险。对一致性要求更高的场景,可以结合延迟双删、消息队列或 binlog 订阅。"

### Q8:"Redis 内存满了怎么办?"

> "先用 `INFO memory` 看内存情况,再用 `CONFIG GET maxmemory` 和 `CONFIG GET maxmemory-policy` 看内存上限和淘汰策略。如果是缓存场景,通常配置 `allkeys-lru` 或 `allkeys-lfu`。还要排查是否存在 big key、过期时间缺失、缓存写入过多等问题。"

### Q9:"Redis 的主从、哨兵、集群分别解决什么问题?"

> "主从复制解决数据备份和读扩展;哨兵 Sentinel 解决主节点宕机后的自动故障转移;Redis Cluster 通过 16384 个 slot 做数据分片,解决单机容量和性能上限。"

### Q10:"什么是 Big Key 和 Hot Key?"

> "Big Key 是 value 很大或集合元素很多的 key,会导致网络传输慢、删除阻塞、主从同步压力大。Hot Key 是访问特别集中的 key,可能打满单个 Redis 节点。Big Key 可以拆分或限制集合长度,Hot Key 可以用本地缓存、副本拆分、预热和限流解决。"

### Q11:"Redis 事务支持回滚吗?"

> "Redis 事务用 `MULTI` 和 `EXEC`,能保证命令按顺序执行且中间不被插入,但不支持 MySQL 那种自动回滚。如果需要多步操作的原子性,很多场景会使用 Lua 脚本。"
---

## 十七、命令速查表

### String

| 命令 | 用途 |
|---|---|
| `SET key value EX 秒` | 存值+过期时间 |
| `GET key` | 取值 |
| `DEL key` | 删除 |
| `TTL key` | 查看剩余秒数 |
| `INCR key` | 原子自增 |
| `INCRBY key N` | 自增 N |

### Hash

| 命令 | 用途 |
|---|---|
| `HSET key field value` | 设置字段 |
| `HGET key field` | 取单个字段 |
| `HGETALL key` | 取所有字段 |
| `HDEL key field` | 删除字段 |

### List

| 命令 | 用途 |
|---|---|
| `LPUSH key value` | 从左插入 |
| `RPUSH key value` | 从右插入 |
| `LPOP key` | 从左取出 |
| `LRANGE key 0 -1` | 查看全部 |
| `BLPOP key 秒` | 阻塞取出 |

### Set

| 命令 | 用途 |
|---|---|
| `SADD key member` | 添加元素 |
| `SMEMBERS key` | 查看所有 |
| `SISMEMBER key member` | 判断是否存在 |
| `SINTER key1 key2` | 交集 |

### ZSet

| 命令 | 用途 |
|---|---|
| `ZADD key score member` | 添加元素 |
| `ZREVRANGE key 0 -1 WITHSCORES` | 降序取出 |
| `ZINCRBY key N member` | 增加分数 |
| `ZREVRANK key member` | 查看排名 |

### 通用 Key 命令

| 命令 | 用途 |
|---|---|
| `EXISTS key` | 判断 key 是否存在 |
| `TYPE key` | 查看 key 类型 |
| `EXPIRE key 秒` | 设置过期时间 |
| `RENAME old new` | 重命名 key |
| `SCAN 0 MATCH pattern COUNT 100` | 渐进式扫描 key |
| `DBSIZE` | 查看当前 DB key 数量 |
| `FLUSHDB` | 清空当前 DB,危险 |
| `FLUSHALL` | 清空所有 DB,危险 |

### redis-cli 排查

| 命令 | 用途 |
|---|---|
| `redis-cli -h host -p port` | 连接 Redis |
| `PING` | 测试连通性 |
| `AUTH password` | 密码认证 |
| `SELECT 1` | 切换 DB |
| `INFO memory` | 查看内存 |
| `INFO clients` | 查看连接 |
| `INFO replication` | 查看主从复制 |
| `CLIENT LIST` | 查看客户端连接 |
| `CONFIG GET maxmemory` | 查看内存上限 |
| `CONFIG GET maxmemory-policy` | 查看淘汰策略 |

### 性能排查

| 命令 | 用途 |
|---|---|
| `SLOWLOG GET 10` | 查看最近慢查询 |
| `MEMORY USAGE key` | 查看 key 内存占用 |
| `STRLEN key` | 查看 String 长度 |
| `LLEN key` | 查看 List 长度 |
| `HLEN key` | 查看 Hash 字段数 |
| `SCARD key` | 查看 Set 元素数 |
| `ZCARD key` | 查看 ZSet 元素数 |
| `UNLINK key` | 异步删除 key |

### 扩展数据类型

| 命令 | 用途 |
|---|---|
| `SETBIT key offset 1` | Bitmap 设置位 |
| `GETBIT key offset` | Bitmap 获取位 |
| `BITCOUNT key` | Bitmap 统计 1 的数量 |
| `PFADD key member` | HyperLogLog 添加元素 |
| `PFCOUNT key` | HyperLogLog 估算基数 |
| `XADD stream * field value` | Stream 写入消息 |
| `XREAD STREAMS stream 0` | Stream 读取消息 |
| `GEOADD key lng lat member` | Geo 添加位置 |
| `GEODIST key m1 m2 km` | Geo 计算距离 |

### 事务和发布订阅

| 命令 | 用途 |
|---|---|
| `MULTI` | 开启事务 |
| `EXEC` | 执行事务 |
| `DISCARD` | 放弃事务 |
| `EVAL script numkeys key arg` | 执行 Lua 脚本 |
| `SUBSCRIBE channel` | 订阅频道 |
| `PUBLISH channel message` | 发布消息 |
---

## 学习建议

如果用于测开面试,建议按下面顺序掌握:

1. 基础数据类型:String、Hash、List、Set、ZSet。
2. 缓存三大问题:穿透、击穿、雪崩。
3. 缓存一致性:Cache Aside、更新 DB 后删除缓存。
4. 分布式锁:SET NX EX、唯一 value、Lua 释放。
5. 生产排查:INFO、SLOWLOG、SCAN、大 Key、热 Key。
6. 高可用:主从、哨兵、Cluster。

一句话总结:

> Redis 面试不要只背命令,重点是能讲清楚缓存为什么快、数据怎么过期、缓存和数据库怎么一致、锁怎么避免误删、线上慢了怎么排查。

---

*Redis:测开面试核心增强版 —— 完结。*

