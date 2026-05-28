# Linux 常用命令笔记:测开面试核心增强版

> 学习日期:2025-05-23  
> 优化日期:2026-05-28  
> 主题:测开面试和日常工作的 Linux 核心命令  
> 适用:测试开发工程师面试、接口测试、线上排障、日常运维协作

---

## 目录

- [一、日志排查(最高频)](#一日志排查最高频)
- [二、进程管理](#二进程管理)
- [三、网络排查](#三网络排查)
- [四、文件与磁盘](#四文件与磁盘)
- [五、权限管理](#五权限管理)
- [六、管道与重定向](#六管道与重定向)
- [七、服务管理 systemctl / journalctl](#七服务管理-systemctl--journalctl)
- [八、文本处理进阶 sed / cut / xargs](#八文本处理进阶-sed--cut--xargs)
- [九、环境变量与 Shell 基础](#九环境变量与-shell-基础)
- [十、压缩、传输与备份](#十压缩传输与备份)
- [十一、三大排查场景模型](#十一三大排查场景模型)
- [十二、面试问答模板](#十二面试问答模板)
- [十三、命令速查表](#十三命令速查表)

---

## 一、日志排查(最高频)

日志排查是测开和后端联调时最常用的能力。核心思路是:

1. 先定位错误行。
2. 再看错误上下文。
3. 最后按接口、时间、错误类型做统计。

### 1.1 tail:看文件末尾

```bash
# 看最后 20 行
tail -20 /var/log/app/service.log

# 实时跟踪日志
tail -f /var/log/app/service.log

# 更适合日志轮转场景
tail -F /var/log/app/service.log
```

**`tail -f` 和 `tail -F` 区别**:

- `tail -f`:跟踪当前文件句柄。
- `tail -F`:文件被日志轮转、删除重建后，也会继续跟踪新文件。

测开日常联调用法:

```bash
tail -F service.log
```

然后在另一个终端发接口请求，实时观察有没有异常堆栈。

### 1.2 grep:搜索关键词

```bash
# 基础搜索
grep "ERROR" service.log

# 显示行号
grep -n "ERROR" service.log

# 忽略大小写
grep -i "error" service.log

# 反向过滤:不包含 DEBUG 的行
grep -v "DEBUG" service.log

# 多关键词:ERROR 或 WARN
grep -E "ERROR|WARN" service.log

# 实时看错误日志
tail -f service.log | grep "ERROR"
```

如果发现实时管道输出不及时，可以加 `--line-buffered`:

```bash
tail -f service.log | grep --line-buffered "ERROR"
```

### 1.3 grep 看上下文

排查异常时，只看一行通常不够，需要看前后几行。

```bash
# 显示匹配行前后各 3 行
grep -C 3 "ERROR" service.log

# 显示匹配行后 5 行
grep -A 5 "Exception" service.log

# 显示匹配行前 5 行
grep -B 5 "Exception" service.log
```

参数含义:

| 参数 | 含义 |
|---|---|
| `-C` | context, 前后各 N 行 |
| `-A` | after, 匹配行之后 N 行 |
| `-B` | before, 匹配行之前 N 行 |

### 1.4 查压缩日志 zgrep

线上日志经常会被压缩成 `.gz` 文件，不能直接用普通 `grep` 查。

```bash
# 查压缩日志中的 ERROR
zgrep "ERROR" service.log.2025-05-23.gz

# 查多个压缩日志
zgrep "ERROR" service.log.*.gz

# 显示行号
zgrep -n "timeout" service.log.2025-05-23.gz
```

### 1.5 wc:统计行数

```bash
# 文件总行数
wc -l service.log

# ERROR 出现次数
grep "ERROR" service.log | wc -l
```

### 1.6 awk:按列提取

假设日志格式如下:

```text
2025-05-23 14:32:01 ERROR /api/users 500
   $1         $2      $3     $4      $5
```

```bash
# 提取第 4 列:接口路径
awk '{print $4}' service.log

# 提取日期和接口路径
awk '{print $1, $4}' service.log

# 截取时间到分钟
awk '{print $1, substr($2, 1, 5)}' service.log
```

### 1.7 sort + uniq:排序统计

测开经典一行命令:统计每个接口报错次数。

```bash
grep "ERROR" service.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

拆解:

```text
grep "ERROR" service.log  -> 筛出错误行
awk '{print $4}'          -> 提取接口路径
sort                      -> 排序
uniq -c                   -> 去重并计数
sort -rn                  -> 按数字倒序
```

示例输出:

```text
3 /api/users
1 /api/orders
```

### 1.8 统计每分钟 ERROR 次数

```bash
grep "ERROR" service.log \
  | awk '{print $1, substr($2, 1, 5)}' \
  | sort \
  | uniq -c \
  | sort -rn
```

示例输出:

```text
3 2025-05-23 14:32
1 2025-05-23 14:33
```

这个命令可以判断错误是突发、持续，还是某个时间点集中爆发。

### 1.9 按时间段过滤日志

如果日志时间格式固定，可以用 `awk` 做简单时间过滤。

```bash
# 查看 14:00 到 15:00 之间的日志
awk '$2 >= "14:00:00" && $2 <= "15:00:00"' service.log

# 查看某天某个时间段的 ERROR
awk '$1 == "2025-05-23" && $2 >= "14:00:00" && $2 <= "15:00:00"' service.log \
  | grep "ERROR"
```

注意:这种方式依赖日志时间格式稳定，复杂场景建议使用日志平台或专门脚本。

### 1.10 head + less:查看大文件

```bash
# 看前 10 行
head -10 service.log

# 看后 20 行
tail -20 service.log

# 翻页查看大文件
less service.log
```

`less` 常用快捷键:

| 快捷键 | 含义 |
|---|---|
| `空格` | 下一页 |
| `b` | 上一页 |
| `/keyword` | 搜索关键词 |
| `n` | 下一个匹配 |
| `N` | 上一个匹配 |
| `q` | 退出 |

---

## 二、进程管理

进程排查常用于回答:服务是否启动、进程是否卡死、CPU/内存是否异常、端口被谁占用。

### 2.1 ps:查进程

```bash
# 查所有进程并过滤服务名
ps -ef | grep python
ps -ef | grep nginx
```

输出示例:

```text
UID   PID  PPID  C  STIME  TTY   TIME      CMD
root  1234 1     0  14:00  ?     00:01:23  python app.py
```

字段说明:

| 字段 | 含义 |
|---|---|
| UID | 启动进程的用户 |
| PID | 进程 ID |
| PPID | 父进程 ID |
| STIME | 启动时间 |
| TIME | 占用 CPU 总时间 |
| CMD | 启动命令 |

按资源占用排序:

```bash
# 按内存倒序
ps aux --sort=-%mem | head

# 按 CPU 倒序
ps aux --sort=-%cpu | head
```

### 2.2 pgrep / pkill:按名称查杀进程

```bash
# 查进程 PID 和完整命令
pgrep -fl python

# 按进程名发送终止信号
pkill nginx
```

生产环境谨慎使用 `pkill`，避免误杀同名进程。

### 2.3 top:实时看系统资源

```bash
top
```

关键列:

| 列 | 含义 |
|---|---|
| PID | 进程 ID |
| %CPU | CPU 占用率 |
| %MEM | 内存占用率 |
| COMMAND | 进程名 |

快捷键:

| 快捷键 | 含义 |
|---|---|
| `P` | 按 CPU 排序 |
| `M` | 按内存排序 |
| `q` | 退出 |

### 2.4 free / uptime:看系统整体状态

```bash
# 查看内存
free -h

# 查看系统运行时间和负载
uptime
```

`uptime` 输出里的 load average 表示 1 分钟、5 分钟、15 分钟平均负载。

经验判断:

- 单核机器 load 长期大于 1，说明 CPU 可能繁忙。
- 4 核机器 load 长期大于 4，说明 CPU 可能繁忙。

### 2.5 kill:终止进程

```bash
# 优雅终止:SIGTERM
kill 1234

# 强制杀死:SIGKILL
kill -9 1234
```

面试必背:

> `kill` 默认发送 SIGTERM，进程可以捕获信号并做清理，比如关闭连接、保存数据。  
> `kill -9` 发送 SIGKILL，进程无法捕获，会被操作系统立刻杀死，可能导致数据丢失。  
> 所以优先用 `kill`，`kill -9` 是最后手段。

### 2.6 后台运行 nohup

```bash
# 后台启动服务，并把日志写入 app.log
nohup python app.py > app.log 2>&1 &

# 查看后台任务
jobs
```

符号说明:

| 符号 | 含义 |
|---|---|
| `nohup` | 终端关闭后进程继续运行 |
| `>` | 标准输出重定向 |
| `2>&1` | 标准错误也输出到同一个文件 |
| `&` | 后台运行 |

---

## 三、网络排查

网络排查重点回答:端口是否监听、服务是否可访问、DNS 是否正常、路由是否正确、接口响应是否符合预期。

### 3.1 ss / netstat:查端口监听

```bash
# 查 8080 端口是否被监听
ss -tlnp | grep 8080

# 老系统也可能用 netstat
netstat -tlnp | grep 8080
```

参数说明:

| 参数 | 含义 |
|---|---|
| `-t` | TCP |
| `-l` | 只看监听状态 |
| `-n` | 数字显示，不做 DNS 解析 |
| `-p` | 显示进程 |

优先使用 `ss`，因为很多新系统默认不安装 `netstat`。

### 3.2 lsof:查端口被谁占用

```bash
# 查 8080 端口被哪个进程占用
lsof -i:8080

# 查 TCP 监听
lsof -iTCP -sTCP:LISTEN
```

### 3.3 curl:命令行发 HTTP 请求

```bash
# GET 请求
curl http://127.0.0.1:8080/api/health

# 查看详细过程和响应头
curl -v http://127.0.0.1:8080/api/health

# 只看响应头
curl -I http://127.0.0.1:8080/api/health

# POST JSON
curl -X POST http://127.0.0.1:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 28}'

# 只看状态码
curl -o /dev/null -s -w "%{http_code}" http://127.0.0.1:8080/api/health
```

常用排障参数:

```bash
# 设置连接超时时间
curl --connect-timeout 3 http://127.0.0.1:8080/api/health

# 跳过 HTTPS 证书校验，测试环境常用
curl -k https://test.example.com

# 显示状态码和耗时
curl -o /dev/null -s -w "code=%{http_code} time=%{time_total}\n" http://127.0.0.1:8080/api/health
```

### 3.4 ping:测基础连通性

```bash
ping 127.0.0.1
ping example.com
```

注意:

- `ping` 通不代表 HTTP 一定通。
- `ping` 不通也不一定代表服务不可用，可能是 ICMP 被防火墙禁了。

### 3.5 nc / telnet:测端口连通性

```bash
# 测试目标 IP 的 3306 端口是否能连通
nc -vz 10.0.0.1 3306

# 如果没有 nc，也可以用 telnet
telnet 10.0.0.1 3306
```

常见用途:

- 应用服务器能否连接数据库。
- 测试服务器能否连接 Redis、MQ、ES。
- 判断是服务没启动，还是网络链路不通。

### 3.6 dig / nslookup:排查 DNS

```bash
# 查询域名解析
dig example.com

# 简洁输出 IP
dig +short example.com

# 备用命令
nslookup example.com
```

DNS 排查重点:

- 域名是否能解析。
- 解析到的 IP 是否符合预期。
- 内网环境是否使用了正确 DNS。

### 3.7 traceroute / tracepath:查看网络路径

```bash
traceroute example.com

# 有些系统没有 traceroute，可用 tracepath
tracepath example.com
```

用于判断请求卡在哪一跳，常见于跨机房、跨地域、VPN、代理排查。

### 3.8 ip addr / ip route:查看网卡和路由

```bash
# 查看 IP 地址
ip addr

# 查看路由表
ip route
```

常见判断:

- 机器有没有拿到正确 IP。
- 默认网关是否正确。
- 是否走了预期网卡或路由。

---

## 四、文件与磁盘

### 4.1 常用文件操作

```bash
# 查看目录
ls
ls -lh
ls -la

# 创建目录
mkdir logs
mkdir -p app/logs

# 创建空文件
touch app.log

# 复制
cp source.txt target.txt
cp -r dir1 dir2

# 移动或重命名
mv old.txt new.txt

# 删除文件或目录
rm file.txt
rm -r dir
```

生产环境慎用:

```bash
rm -rf /*
```

不要在不确认路径的情况下使用 `rm -rf`。

### 4.2 find:查找文件

```bash
# 找所有 .log 文件
find . -name "*.log"

# 找最近 1 天修改过的文件
find /var/log -mtime -1

# 找大于 100MB 的文件
find / -size +100M 2>/dev/null

# 找空文件
find . -type f -empty

# 找 7 天前的日志
find /var/log -name "*.log" -mtime +7
```

### 4.3 df:看磁盘空间

```bash
df -h
```

输出示例:

```text
Filesystem  Size  Used  Avail  Use%  Mounted on
/dev/sda1   50G   45G   5G     90%   /
```

### 4.4 du:看目录大小

```bash
# 看当前目录下各子目录大小
du -sh *

# 找最大的 10 个目录或文件
du -sh * | sort -rh | head -10
```

### 4.5 inode 满排查

有时 `df -h` 看磁盘空间没满，但还是无法创建文件，可能是 inode 用完了。

```bash
# 查看 inode 使用情况
df -i

# 统计目录下文件数量
find /path -type f | wc -l
```

常见原因:

- 小文件太多。
- 日志切分过细。
- 临时文件没有清理。
- 缓存目录无限增长。

### 4.6 stat / file:查看文件信息

```bash
# 查看文件详细元信息
stat service.log

# 判断文件类型
file service.log
```

---

## 五、权限管理

Linux 权限排查重点回答:我是谁、文件属于谁、我有没有读写执行权限。

### 5.1 查看当前用户

```bash
# 当前用户
whoami

# 当前用户 ID、组 ID
id

# 当前用户所在用户组
groups
```

### 5.2 chmod:修改权限

```bash
# 给脚本加执行权限
chmod +x deploy.sh

# 数字方式
chmod 755 deploy.sh
chmod 644 file.txt
```

权限数字速记:

```text
r = 4
w = 2
x = 1

755 = rwxr-xr-x
644 = rw-r--r--
```

### 5.3 文件权限和目录权限区别

文件:

- `r`:可以读取文件内容。
- `w`:可以修改文件内容。
- `x`:可以执行文件。

目录:

- `r`:可以列出目录内容。
- `w`:可以在目录内创建、删除、重命名文件。
- `x`:可以进入目录，也可以访问目录下的文件路径。

面试细节:

> 目录没有 `x` 权限时，即使有 `r` 权限，也无法正常进入目录或访问目录内文件。

### 5.4 chown / chgrp:修改所有者和用户组

```bash
# 修改所有者和用户组
chown root:root deploy.sh

# 递归修改目录所有者
chown -R www-data:www-data /var/www/

# 只修改用户组
chgrp developers app.log
```

### 5.5 sudo / su:权限切换

```bash
# 使用管理员权限执行命令
sudo systemctl restart nginx

# 切换用户
su - username
```

### 5.6 umask:默认权限

```bash
umask
```

`umask` 决定新建文件和目录的默认权限。常见默认值是 `022`。

---

## 六、管道与重定向

### 6.1 管道 |

管道把上一个命令的标准输出交给下一个命令处理。

```bash
ps -ef | grep python
grep "ERROR" service.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

### 6.2 重定向

```bash
# 覆盖写入
grep "ERROR" service.log > errors.txt

# 追加写入
echo "$(date) ERROR found" >> alert.log

# 标准错误重定向
command 2> error.log

# 标准输出和标准错误都写入文件
command > all.log 2>&1

# Bash 中也常见
command &> all.log
```

### 6.3 tee:边看输出边写文件

```bash
# 输出到屏幕，同时写入 result.log
command | tee result.log

# 追加写入
command | tee -a result.log
```

### 6.4 /dev/null:丢弃输出

```bash
# 丢弃正常输出，只保留错误输出
command > /dev/null

# 丢弃所有输出
command > /dev/null 2>&1
```

---

## 七、服务管理 systemctl / journalctl

现在大多数 Linux 服务由 systemd 管理。面试和实战都很常见。

### 7.1 systemctl:管理服务

```bash
# 查看服务状态
systemctl status nginx

# 启动服务
systemctl start nginx

# 停止服务
systemctl stop nginx

# 重启服务
systemctl restart nginx

# 重新加载配置
systemctl reload nginx

# 设置开机自启
systemctl enable nginx

# 取消开机自启
systemctl disable nginx
```

### 7.2 journalctl:查看服务日志

```bash
# 查看 nginx 服务日志
journalctl -u nginx

# 查看最近 100 行
journalctl -u nginx -n 100

# 实时跟踪
journalctl -u nginx -f

# 查看今天的日志
journalctl -u nginx --since today

# 查看指定时间后的日志
journalctl -u nginx --since "2025-05-23 14:00:00"
```

### 7.3 服务启动失败排查模型

```text
1. systemctl status 服务名
   看服务是否 failed，错误摘要是什么。

2. journalctl -u 服务名 -n 100
   看最近启动日志和异常堆栈。

3. ss -tlnp | grep 端口
   看端口是否监听。

4. curl -v http://127.0.0.1:端口/health
   看接口是否正常。
```

---

## 八、文本处理进阶 sed / cut / xargs

### 8.1 cut:简单按分隔符取列

```bash
# 按空格取第 4 列
cut -d ' ' -f 4 service.log

# 按冒号取第 1 列
cut -d ':' -f 1 /etc/passwd
```

`cut` 适合简单固定分隔符；复杂文本更推荐 `awk`。

### 8.2 sed:查看、替换、删除

```bash
# 查看第 100 到 120 行
sed -n '100,120p' service.log

# 替换文本，只输出到屏幕，不改文件
sed 's/ERROR/WARN/g' service.log

# 删除空行
sed '/^$/d' service.log
```

谨慎使用 `sed -i`，它会直接修改文件。

```bash
# 直接修改文件中的内容
sed -i 's/old/new/g' config.txt
```

### 8.3 xargs:把输出转成命令参数

```bash
# 查所有日志文件中的 ERROR
find . -name "*.log" | xargs grep "ERROR"

# 删除 7 天前的 .tmp 文件
find /tmp -name "*.tmp" -mtime +7 | xargs rm
```

如果文件名中可能包含空格，使用更安全的写法:

```bash
find . -name "*.log" -print0 | xargs -0 grep "ERROR"
```

---

## 九、环境变量与 Shell 基础

### 9.1 查看命令位置

```bash
# 查看命令路径
which python
which java

# 查看命令更多位置
whereis python
```

### 9.2 查看和设置环境变量

```bash
# 查看 PATH
echo $PATH

# 查看所有环境变量
env

# 设置临时环境变量
export ENV=test

# 查看变量
echo $ENV
```

### 9.3 source:让配置立即生效

```bash
# 修改 ~/.bashrc 后立即生效
source ~/.bashrc
```

### 9.4 查看上一条命令是否成功

```bash
echo $?
```

约定:

- `0`:成功。
- 非 `0`:失败。

### 9.5 Shell 脚本基础

```bash
#!/bin/bash

URL="http://127.0.0.1:8080/health"

code=$(curl -o /dev/null -s -w "%{http_code}" "$URL")

if [ "$code" = "200" ]; then
  echo "service ok"
else
  echo "service failed, code=$code"
fi
```

### 9.6 crontab:定时任务

```bash
# 编辑当前用户定时任务
crontab -e

# 查看当前用户定时任务
crontab -l
```

示例:每 5 分钟执行一次健康检查脚本。

```bash
*/5 * * * * /bin/bash /opt/scripts/health_check.sh >> /var/log/health_check.log 2>&1
```

crontab 时间格式:

```text
分钟 小时 日期 月份 星期 命令
```

---

## 十、压缩、传输与备份

### 10.1 tar:打包和解压

```bash
# 打包并 gzip 压缩
tar -czvf logs.tar.gz logs/

# 解压
tar -xzvf logs.tar.gz

# 查看压缩包内容
tar -tzvf logs.tar.gz
```

参数说明:

| 参数 | 含义 |
|---|---|
| `-c` | create, 创建压缩包 |
| `-x` | extract, 解压 |
| `-z` | gzip |
| `-v` | 显示过程 |
| `-f` | 指定文件名 |

### 10.2 gzip / gunzip

```bash
# 压缩单个文件
gzip service.log

# 解压
gunzip service.log.gz
```

### 10.3 scp:远程拷贝

```bash
# 本地文件传到远程
scp app.log user@10.0.0.1:/tmp/

# 远程文件拉到本地
scp user@10.0.0.1:/tmp/app.log .

# 拷贝目录
scp -r logs/ user@10.0.0.1:/tmp/
```

### 10.4 rsync:增量同步

```bash
rsync -av logs/ user@10.0.0.1:/tmp/logs/
```

`rsync` 适合大量文件或重复同步，比 `scp` 更高效。

### 10.5 ln -s:软链接

```bash
# 创建软链接
ln -s /opt/app/current/logs /var/log/app
```

---

## 十一、三大排查场景模型

### 场景 1:服务不通

三层排查模型:

```text
第 1 层:进程在不在?
  ps -ef | grep 服务名
  pgrep -fl 服务名

第 2 层:端口在不在监听?
  ss -tlnp | grep 端口号
  lsof -i:端口号

第 3 层:接口能不能通?
  curl -v http://127.0.0.1:端口/接口路径
```

如果跨机器访问不通，再继续查:

```bash
ping 目标IP
nc -vz 目标IP 端口
dig 域名
ip route
```

面试表达:

> 排查服务不通，我会先查进程，再查端口，最后查接口。如果本机接口正常但远程不通，再继续排查网络连通性、DNS、防火墙、路由和上游网关。

### 场景 2:磁盘满

```bash
# 第 1 步:看哪个分区满了
df -h

# 第 2 步:进入对应挂载目录，逐层找大目录
du -sh * | sort -rh | head -10

# 第 3 步:找大文件
find / -size +100M 2>/dev/null

# 第 4 步:如果空间没满但无法创建文件，查 inode
df -i
```

常见原因:

- 日志没有轮转。
- 临时文件未清理。
- 大文件上传失败后残留。
- 小文件过多导致 inode 满。

处理方式:

- 清理无用日志。
- 压缩归档旧日志。
- 配置 logrotate。
- 删除临时文件。
- 找业务方确认大文件是否可删。

### 场景 3:接口报 500

```bash
# 实时看错误日志
tail -F service.log | grep --line-buffered "ERROR"

# 搜异常上下文
grep -n -C 5 "Exception" service.log

# 统计错误接口
grep "ERROR" service.log | awk '{print $4}' | sort | uniq -c | sort -rn

# 统计每分钟错误数量
grep "ERROR" service.log \
  | awk '{print $1, substr($2, 1, 5)}' \
  | sort | uniq -c | sort -rn
```

排查顺序:

```text
1. curl 复现接口。
2. tail -F 看实时日志。
3. grep -C 看异常上下文。
4. 统计是否只有某个接口、某个时间段集中报错。
5. 结合数据库、缓存、第三方依赖继续定位。
```

### 场景 4:CPU 飙高

```bash
# 查看整体负载
uptime

# 查看 CPU 占用最高的进程
top
ps aux --sort=-%cpu | head

# 找到 PID 后看进程命令
ps -fp PID
```

常见原因:

- 死循环。
- 瞬时流量过高。
- 大量日志打印。
- 慢 SQL 或批处理任务。
- GC 频繁。

### 场景 5:内存占用高

```bash
# 查看整体内存
free -h

# 查看内存占用最高的进程
ps aux --sort=-%mem | head

# 实时观察
top
```

常见原因:

- 内存泄漏。
- 大对象缓存。
- 批量读取过多数据。
- 连接池没有释放。

---

## 十二、面试问答模板

### Q1:线上服务不通，你怎么排查?

> 我会从下到上查三层。  
> 第一层查进程，用 `ps -ef | grep 服务名` 或 `pgrep -fl 服务名`，确认服务是否启动。  
> 第二层查端口，用 `ss -tlnp | grep 端口` 或 `lsof -i:端口`，确认端口是否监听。  
> 第三层查接口，用 `curl -v http://127.0.0.1:端口/health`，确认应用是否能正常响应。  
> 如果本机正常但远程访问不通，我会继续用 `ping`、`nc -vz`、`dig`、`ip route` 排查网络、DNS 和路由问题。

### Q2:磁盘满了怎么处理?

> 先用 `df -h` 看哪个分区满了，再进入对应目录用 `du -sh * | sort -rh | head -10` 逐层找大目录，然后用 `find / -size +100M 2>/dev/null` 找大文件。  
> 如果磁盘空间没满但无法创建文件，我会用 `df -i` 查 inode 是否用完。  
> 常见原因是日志没有轮转、临时文件未清理、小文件过多。处理前要确认文件是否可删，不能直接删除业务文件。

### Q3:kill 和 kill -9 的区别?

> `kill` 默认发送 SIGTERM，进程可以捕获这个信号并做清理工作，比如关闭连接、保存数据。  
> `kill -9` 发送 SIGKILL，进程无法捕获，会被操作系统强制杀死，可能导致数据丢失。  
> 所以一般优先使用 `kill`，只有进程无响应时才使用 `kill -9`。

### Q4:grep 常用参数有哪些?

> 常用参数有 `-n` 显示行号，`-i` 忽略大小写，`-v` 反向过滤，`-E` 支持扩展正则，`-C/-A/-B` 查看上下文。  
> 日常最常用的是 `tail -F service.log | grep --line-buffered "ERROR"` 实时看错误日志。

### Q5:如何统计日志中某类错误出现次数?

> 可以用 `grep + awk + sort + uniq -c + sort -rn`:

```bash
grep "ERROR" service.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

> 这条命令先筛出错误行，再提取接口路径，然后排序、计数，最后按次数倒序展示。

### Q6:如何查看一个端口被谁占用?

```bash
ss -tlnp | grep 8080
lsof -i:8080
```

> `ss` 可以看监听端口和进程信息，`lsof -i:端口` 可以直接查端口对应的进程。

### Q7:如何排查接口超时?

> 我会先用 `curl -v` 或 `curl -w` 看连接时间和总耗时，再确认服务端端口是否监听、应用日志是否有超时异常。  
> 如果是跨机器访问，还要用 `nc -vz` 测端口连通性，用 `dig` 查域名解析，用 `traceroute` 或 `tracepath` 看网络路径。

```bash
curl -o /dev/null -s -w "code=%{http_code} time=%{time_total}\n" http://example.com/api
nc -vz example.com 443
dig example.com
```

### Q8:systemctl 和 journalctl 怎么用?

> `systemctl` 用来管理服务，比如启动、停止、重启、查看状态。  
> `journalctl` 用来查看 systemd 管理的服务日志。

```bash
systemctl status nginx
systemctl restart nginx
journalctl -u nginx -n 100
journalctl -u nginx -f
```

---

## 十三、命令速查表

### 日志

| 命令 | 用途 |
|---|---|
| `tail -f file` | 实时跟踪日志 |
| `tail -F file` | 跟踪日志，兼容日志轮转 |
| `grep "keyword" file` | 搜关键词 |
| `grep -n` | 显示行号 |
| `grep -i` | 忽略大小写 |
| `grep -v` | 反向过滤 |
| `grep -E "A|B"` | 多关键词 |
| `grep -C 3 keyword file` | 查看匹配行前后 3 行 |
| `zgrep keyword file.gz` | 查压缩日志 |
| `wc -l file` | 数行数 |
| `awk '{print $N}'` | 提取第 N 列 |
| `sort | uniq -c | sort -rn` | 统计频率 |

### 进程

| 命令 | 用途 |
|---|---|
| `ps -ef | grep name` | 查进程 |
| `pgrep -fl name` | 按名称查进程 |
| `top` | 实时资源监控 |
| `free -h` | 查看内存 |
| `uptime` | 查看运行时间和负载 |
| `kill PID` | 优雅终止 |
| `kill -9 PID` | 强制杀死 |
| `nohup cmd > app.log 2>&1 &` | 后台运行 |

### 网络

| 命令 | 用途 |
|---|---|
| `ss -tlnp | grep port` | 查监听端口 |
| `lsof -i:port` | 查端口占用进程 |
| `curl -v URL` | 测接口详情 |
| `curl -I URL` | 只看响应头 |
| `curl -s -o /dev/null -w "%{http_code}" URL` | 只看状态码 |
| `ping host` | 测基础连通性 |
| `nc -vz host port` | 测端口连通性 |
| `dig domain` | 查 DNS |
| `traceroute host` | 查看网络路径 |
| `ip addr` | 查看网卡 IP |
| `ip route` | 查看路由 |

### 磁盘和文件

| 命令 | 用途 |
|---|---|
| `df -h` | 看分区使用率 |
| `df -i` | 看 inode 使用率 |
| `du -sh *` | 看目录大小 |
| `find / -size +100M 2>/dev/null` | 找大文件 |
| `ls -lh` | 查看文件列表 |
| `mkdir -p dir` | 创建目录 |
| `touch file` | 创建空文件 |
| `cp -r src dst` | 复制目录 |
| `mv old new` | 移动或重命名 |
| `stat file` | 查看文件元信息 |
| `file file` | 判断文件类型 |

### 权限

| 命令 | 用途 |
|---|---|
| `whoami` | 查看当前用户 |
| `id` | 查看 UID/GID |
| `groups` | 查看所属用户组 |
| `chmod +x file` | 加执行权限 |
| `chmod 755 file` | 设置权限 |
| `chown user:group file` | 修改所有者和用户组 |
| `sudo command` | 以管理员权限执行 |
| `umask` | 查看默认权限掩码 |

### 服务

| 命令 | 用途 |
|---|---|
| `systemctl status service` | 查看服务状态 |
| `systemctl start service` | 启动服务 |
| `systemctl stop service` | 停止服务 |
| `systemctl restart service` | 重启服务 |
| `systemctl enable service` | 设置开机自启 |
| `journalctl -u service -n 100` | 查看最近服务日志 |
| `journalctl -u service -f` | 实时跟踪服务日志 |

### 文本处理

| 命令 | 用途 |
|---|---|
| `cut -d ':' -f 1 file` | 按分隔符取列 |
| `sed -n '10,20p' file` | 查看第 10 到 20 行 |
| `sed 's/old/new/g' file` | 替换文本并输出 |
| `find . -name "*.log" | xargs grep ERROR` | 批量搜索 |
| `tee result.log` | 边输出边写文件 |

### 环境变量和 Shell

| 命令 | 用途 |
|---|---|
| `which command` | 查看命令路径 |
| `whereis command` | 查看命令相关路径 |
| `echo $PATH` | 查看 PATH |
| `env` | 查看环境变量 |
| `export KEY=value` | 设置临时环境变量 |
| `source ~/.bashrc` | 重新加载配置 |
| `echo $?` | 查看上一条命令退出码 |
| `crontab -e` | 编辑定时任务 |
| `crontab -l` | 查看定时任务 |

### 压缩和传输

| 命令 | 用途 |
|---|---|
| `tar -czvf a.tar.gz dir/` | 打包压缩 |
| `tar -xzvf a.tar.gz` | 解压 |
| `gzip file` | 压缩单个文件 |
| `gunzip file.gz` | 解压 gzip 文件 |
| `scp file user@host:/path/` | 远程复制 |
| `rsync -av src/ user@host:/dst/` | 增量同步 |
| `ln -s source link` | 创建软链接 |

---

## 学习建议

如果用于测开面试，建议按下面顺序掌握:

1. 日志排查:`tail`、`grep`、`awk`、`sort`、`uniq`。
2. 服务排查:`ps`、`ss`、`curl`、`systemctl`、`journalctl`。
3. 网络排查:`ping`、`nc`、`dig`、`ip route`。
4. 磁盘排查:`df -h`、`du -sh`、`find`、`df -i`。
5. 权限排查:`whoami`、`id`、`chmod`、`chown`、`sudo`。
6. Shell 基础:`export`、`source`、`echo $?`、`crontab`。

一句话总结:

> 测开 Linux 能力的核心不是背命令，而是能用命令快速回答:服务在不在、端口通不通、接口对不对、日志错在哪、资源够不够。

