# Linux 常用命令笔记:测开面试核心

> 学习日期:2025-05-23
> 主题:测开面试和日常工作的 Linux 核心命令
> 适用:测试开发工程师面试 & 实战

---

## 目录

- [一、日志排查(最高频)](#一日志排查最高频)
- [二、进程管理](#二进程管理)
- [三、网络排查](#三网络排查)
- [四、文件与磁盘](#四文件与磁盘)
- [五、权限管理](#五权限管理)
- [六、管道与重定向](#六管道与重定向)
- [七、三大排查场景模型](#七三大排查场景模型)
- [八、面试问答模板](#八面试问答模板)
- [九、命令速查表](#九命令速查表)

---

## 一、日志排查(最高频)

### 1.1 tail:看文件末尾

```bash
# 看最后 20 行
tail -20 /var/log/app/service.log

# ⭐ 实时跟踪(服务还在跑时用这个)
tail -f /var/log/app/service.log
# Ctrl+C 退出
```

**测开每天用**:发请求的同时开一个终端 `tail -f` 盯日志,实时看有没有报错。

### 1.2 grep:搜关键词

```bash
# 基础搜索
grep "ERROR" service.log

# 显示行号
grep -n "ERROR" service.log

# 忽略大小写
grep -i "error" service.log

# 反向过滤(不包含 DEBUG 的行)
grep -v "DEBUG" service.log

# 多关键词(或)
grep -E "ERROR|WARN" service.log

# ⭐ 组合:实时看错误日志
tail -f service.log | grep "ERROR"
```

### 1.3 wc:数行数

```bash
# 数文件总行数
wc -l service.log

# ⭐ 数 ERROR 出现几次
grep "ERROR" service.log | wc -l
```

### 1.4 awk:按列提取

日志通常是空格分隔的多列:

```
2025-05-23 14:32:01 ERROR /api/users 500
   $1         $2      $3     $4      $5
```

```bash
# 提取第 4 列(接口路径)
awk '{print $4}' service.log

# 提取多列
awk '{print $1, $4}' service.log

# 截取字符串:取第 2 列时间的前 5 位(精确到分钟)
awk '{print $1, substr($2, 1, 5)}' service.log
# "14:32:01" → "14:32"
```

### 1.5 sort + uniq:排序统计

```bash
# ⭐ 测开经典一行命令:统计每个接口报错几次
grep "ERROR" service.log | awk '{print $4}' | sort | uniq -c | sort -rn

# 拆解:
# grep "ERROR" service.log  → 筛出错误行
# awk '{print $4}'           → 提取路径列
# sort                       → 排序(uniq 要求有序输入)
# uniq -c                    → 去重并计数
# sort -rn                   → 按数字降序

# 输出:
#       3 /api/users
#       1 /api/orders
```

**`-rn` 参数说明**:`-r` 降序,`-n` 按数字排(不是字母序)。

### 1.6 统计每分钟 ERROR 次数

```bash
grep 'ERROR' service.log \
  | awk '{print $1, substr($2, 1, 5)}' \
  | sort \
  | uniq -c \
  | sort -rn

# 输出:
#       3 2025-05-23 14:32
#       1 2025-05-23 14:33
```

**关键点**:`substr($2, 1, 5)` 把时间截断到分钟,不然每秒都是不同的组。

### 1.7 head + less:查看大文件

```bash
# 看前 10 行
head -10 service.log

# 翻页查看(大文件用这个,不用 cat)
less service.log
# 空格:下一页  b:上一页  /:搜索  q:退出
```

---

## 二、进程管理

### 2.1 ps:查进程

```bash
# 查所有进程,找特定服务
ps -ef | grep python
ps -ef | grep nginx
ps -ef | grep 8080
```

**输出解读**:

```
UID   PID  PPID  C  STIME  TTY   TIME    CMD
root  1234  1    0  14:00  ?   00:01:23  python app.py
 ↑     ↑    ↑                              ↑
用户  进程ID 父进程ID                     具体命令
```

### 2.2 top:实时看系统资源

```bash
top
```

**关键列**:

| 列 | 含义 |
|---|---|
| PID | 进程 ID |
| %CPU | CPU 占用率 |
| %MEM | 内存占用率 |
| COMMAND | 进程名 |

**快捷键**:
- `P` → 按 CPU 排序
- `M` → 按内存排序
- `q` → 退出

### 2.3 kill:终止进程

```bash
# 优雅终止(SIGTERM,让进程自己清理)
kill 1234

# 强制杀死(SIGKILL,立刻死,无法捕获)
kill -9 1234
```

> **面试必背**:"`kill` 发 SIGTERM,进程可以捕获信号做清理(关连接、保存数据)再退出。`kill -9` 发 SIGKILL,进程**无法捕获**,立刻被杀,可能丢数据。优先用 `kill`,`kill -9` 是最后手段。"
>
> **类比**:这和 asyncio 的 `cancel()`(协作式)vs 操作系统强杀进程(强制式)是同一个思想。

---

## 三、网络排查

### 3.1 ss / netstat:查端口占用

```bash
# 查 8080 端口被哪个进程占用
ss -tlnp | grep 8080
netstat -tlnp | grep 8080

# 参数含义:
# -t  TCP
# -l  只看监听状态(LISTEN)
# -n  数字显示端口(不做 DNS 解析)
# -p  显示进程名
```

### 3.2 curl:命令行发 HTTP 请求

```bash
# GET 请求
curl http://127.0.0.1:8080/api/health

# 查看详细响应头(排查问题用)
curl -v http://127.0.0.1:8080/api/health

# POST 请求,带 JSON
curl -X POST http://127.0.0.1:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 28}'

# ⭐ 只看状态码(健康检查脚本常用)
curl -o /dev/null -s -w "%{http_code}" http://127.0.0.1:8080/api/health
```

### 3.3 ping:测连通性

```bash
ping 127.0.0.1
ping google.com
# Ctrl+C 停止
```

---

## 四、文件与磁盘

### 4.1 find:找文件

```bash
# 找所有 .log 文件
find . -name "*.log"

# 找最近 1 天内修改过的文件
find /var/log -mtime -1

# 找大于 100MB 的文件
find / -size +100M
```

### 4.2 df:看磁盘空间

```bash
df -h
# -h 表示 human readable(显示 GB/MB)
```

**输出**:

```
Filesystem  Size  Used  Avail  Use%  Mounted on
/dev/sda1   50G   45G   5G     90%   /
```

### 4.3 du:看目录大小

```bash
# 看当前目录下各子目录大小
du -sh *

# 找最大的 10 个目录
du -sh * | sort -rh | head -10
```

---

## 五、权限管理

### 5.1 chmod:改权限

```bash
# 给脚本加执行权限
chmod +x deploy.sh

# 数字方式
chmod 755 deploy.sh   # rwxr-xr-x
chmod 644 file.txt    # rw-r--r--
```

**权限数字速记**:

```
r(读)=4  w(写)=2  x(执行)=1

755 = 7(rwx) 5(r-x) 5(r-x) = 所有者全权限,其他人只读+执行
644 = 6(rw-) 4(r--) 4(r--) = 所有者读写,其他人只读
```

### 5.2 chown:改所有者

```bash
chown root:root deploy.sh
chown -R www-data:www-data /var/www/  # -R 递归
```

---

## 六、管道与重定向

### 6.1 管道 `|`:串联命令

```bash
ps -ef | grep python
grep "ERROR" log | awk '{print $4}' | sort | uniq -c | sort -rn
```

**管道是 Linux 的灵魂**——把简单命令组合成强大的数据处理流水线。

### 6.2 重定向

```bash
# > 覆盖写入文件
grep "ERROR" service.log > errors.txt

# >> 追加写入文件
echo "$(date) ERROR found" >> alert.log

# 2> 重定向错误输出
command 2> error.log

# &> 同时重定向标准输出和错误输出
command &> all.log
```

### 6.3 常用文件查看

```bash
cat file.txt          # 查看全部内容
head -10 file.txt     # 看前 10 行
tail -20 file.txt     # 看后 20 行
tail -f file.txt      # 实时跟踪
less file.txt         # 翻页查看
wc -l file.txt        # 数行数
```

---

## 七、三大排查场景模型

### 场景 1:服务不通——三层排查模型

```
第 1 层:进程在不在?
  ps -ef | grep 服务名
  → 没有 → 重启服务

第 2 层:端口在不在监听?
  ss -tlnp | grep 端口号
  → 没有 → 服务启动失败,看启动日志

第 3 层:接口能不能通?
  curl -v http://127.0.0.1:端口/接口路径
  → 报错 → 看应用日志找原因
```

**面试金句**:"排查服务不通,我会从下往上查三层:进程 → 端口 → 接口。`ps` 查进程、`ss` 查端口、`curl` 查接口,能快速定位是哪一层的问题。"

### 场景 2:磁盘满——三步排查模型

```bash
# 第 1 步:看哪个分区满了
df -h

# 第 2 步:逐层找最大目录
du -sh *             # 在满了的分区目录里执行,逐层缩小

# 第 3 步:找大文件
find / -size +100M

# 常见原因:日志没做 rotate,无限增长
```

### 场景 3:接口报 500——日志分析模型

```bash
# 实时看日志
tail -f service.log | grep "ERROR"

# 统计最高频的错误接口
grep "ERROR" service.log | awk '{print $4}' | sort | uniq -c | sort -rn

# 统计每分钟错误次数(看错误是持续的还是突发的)
grep 'ERROR' service.log \
  | awk '{print $1, substr($2, 1, 5)}' \
  | sort | uniq -c | sort -rn
```

---

## 八、面试问答模板

### Q1:"线上服务不通,你怎么排查?"

> "我会从下往上查三层:
> 1. `ps -ef | grep 服务名` —— 确认进程在不在
> 2. `ss -tlnp | grep 端口` —— 确认端口在不在监听
> 3. `curl -v http://127.0.0.1:端口/接口` —— 确认接口能不能通
>
> 每一层对应不同的问题:进程没了就重启;进程在但端口没开说明启动失败要看启动日志;端口通但接口报错就要看应用日志找具体原因。"

### Q2:"磁盘满了怎么处理?"

> "先 `df -h` 看哪个分区满了,再 `du -sh *` 逐层找最大的目录,最后 `find / -size +100M` 找大文件。
>
> 最常见的原因是日志没做 rotate(日志轮转),日志文件无限增长。处理方法是清理旧日志、配置 logrotate 定期压缩归档。"

### Q3:"kill 和 kill -9 的区别?"

> "`kill` 发 SIGTERM 信号,进程可以捕获这个信号做清理工作(关闭数据库连接、保存数据)再退出。`kill -9` 发 SIGKILL 信号,进程无法捕获,被操作系统立刻杀死,可能丢失数据。
>
> 应该优先用 `kill`,给进程机会优雅退出。`kill -9` 是进程卡死无法响应时的最后手段。"

### Q4:"grep 常用参数?"

> "`-n` 显示行号,`-i` 忽略大小写,`-v` 反向过滤,`-E` 支持正则/多关键词。
>
> 最常用的组合是 `tail -f service.log | grep 'ERROR'`——实时监控错误日志。"

### Q5:"统计日志中某类错误出现的次数?"

> "用 `grep + awk + sort + uniq -c + sort -rn` 的组合:
>
> ```bash
> grep "ERROR" service.log | awk '{print $4}' | sort | uniq -c | sort -rn
> ```
>
> 这是一个标准的日志统计流水线:grep 筛行、awk 提列、sort 排序、uniq -c 计数、sort -rn 按频率降序。"

---

## 九、命令速查表

### 日志

| 命令 | 用途 |
|---|---|
| `tail -f file` | 实时跟踪日志 |
| `grep "keyword" file` | 搜关键词 |
| `grep -n` | 显示行号 |
| `grep -v` | 反向过滤 |
| `grep -E "A\|B"` | 多关键词 |
| `wc -l file` | 数行数 |
| `awk '{print $N}'` | 提取第 N 列 |
| `sort \| uniq -c \| sort -rn` | 统计频率 |

### 进程

| 命令 | 用途 |
|---|---|
| `ps -ef \| grep name` | 查进程 |
| `top` | 实时资源监控 |
| `kill PID` | 优雅终止 |
| `kill -9 PID` | 强制杀死 |

### 网络

| 命令 | 用途 |
|---|---|
| `ss -tlnp \| grep port` | 查端口 |
| `curl -v URL` | 测接口 |
| `curl -s -o /dev/null -w "%{http_code}" URL` | 只看状态码 |
| `ping host` | 测连通性 |

### 磁盘

| 命令 | 用途 |
|---|---|
| `df -h` | 看分区使用率 |
| `du -sh *` | 看目录大小 |
| `find / -size +100M` | 找大文件 |

### 文件

| 命令 | 用途 |
|---|---|
| `cat file` | 查看文件 |
| `head -N file` | 看前 N 行 |
| `tail -N file` | 看后 N 行 |
| `less file` | 翻页查看 |
| `chmod +x file` | 加执行权限 |
| `chmod 755 file` | 设权限 |

### 管道与重定向

| 符号 | 用途 |
|---|---|
| `cmd1 \| cmd2` | 管道:上一个输出给下一个 |
| `> file` | 覆盖写入 |
| `>> file` | 追加写入 |
| `2> file` | 重定向错误输出 |

---

*Linux 常用命令:测开面试核心 20 条 + 三大排查场景模型 —— 完结。*
