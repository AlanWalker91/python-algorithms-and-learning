# Shell 脚本笔记:测开工作常用脚本汇总

## 目录

- [一、Shell 基础语法](#一shell-基础语法)
- [二、脚本稳定性和规范写法](#二脚本稳定性和规范写法)
- [三、常见坑和铁律](#三常见坑和铁律)
- [四、测开常用实战脚本](#四测开常用实战脚本)
- [五、命令速查](#五命令速查)
- [六、学习建议](#六学习建议)

---

## 一、Shell 基础语法

### 1.1 标准脚本头

```bash
#!/usr/bin/env bash

set -Eeuo pipefail

trap 'echo "[ERROR] line $LINENO command failed: $BASH_COMMAND" >&2' ERR
```

含义:

| 写法 | 含义 |
|---|---|
| `#!/usr/bin/env bash` | 使用环境变量中的 bash,可移植性比 `/bin/bash` 更好 |
| `set -e` | 任意命令失败时退出脚本 |
| `set -u` | 使用未定义变量时报错 |
| `set -o pipefail` | 管道中任意命令失败,整个管道都算失败 |
| `set -E` | 让 `ERR trap` 在函数、子 Shell 中也生效 |
| `trap ... ERR` | 捕获错误并打印出错行号和命令 |

> 学习阶段可以先不用 `set -Eeuo pipefail`,但正式脚本建议加上。

### 1.2 变量

```bash
# 定义变量:等号两边不能有空格
name="Alice"
port=8080

# 使用变量
echo "$name"
echo "${port}"      # 花括号用于边界不清晰时

# 参数默认值
LOG_FILE=${1:-"service.log"}    # 没传参数就用默认值

# 必填参数
ENV_NAME=${1:?"请传入环境名称,例如: dev/test/prod"}
```

常见参数展开:

| 写法 | 含义 |
|---|---|
| `${var}` | 读取变量 |
| `${var:-default}` | 变量为空或未定义时使用默认值 |
| `${var:=default}` | 变量为空或未定义时赋默认值 |
| `${var:?message}` | 变量为空或未定义时报错退出 |
| `${var:+value}` | 变量非空时返回 value |

### 1.3 if 判断

```bash
if [ 条件 ]; then
    echo "条件为真"
elif [ 另一个条件 ]; then
    echo "另一个条件为真"
else
    echo "都不满足"
fi
```

常用条件:

| 条件 | 含义 |
|---|---|
| `[ "$a" = "$b" ]` | 字符串相等 |
| `[ "$a" != "$b" ]` | 字符串不等 |
| `[ -n "$a" ]` | 字符串非空 |
| `[ -z "$a" ]` | 字符串为空 |
| `[ "$n" -eq 0 ]` | 数字等于 0 |
| `[ "$n" -ne 0 ]` | 数字不等于 0 |
| `[ "$n" -gt 100 ]` | 数字大于 100 |
| `[ "$n" -lt 5 ]` | 数字小于 5 |
| `[ -f "/path" ]` | 文件存在且是普通文件 |
| `[ -d "/path" ]` | 目录存在 |
| `[ -x "/path" ]` | 文件存在且可执行 |

推荐字符串判断使用 `[[ ... ]]`:

```bash
if [[ "$env" == "prod" ]]; then
    echo "生产环境"
fi

if [[ "$file" == *.log ]]; then
    echo "日志文件"
fi
```

### 1.4 循环

```bash
# while 无限循环
while true; do
    echo "running..."
    sleep 30
done

# for 遍历列表
for item in a b c; do
    echo "$item"
done

# C 风格 for 循环
for (( i=0; i<10; i++ )); do
    echo "$i"
done

# 遍历数组
SERVICES=("user" "order" "pay")
for service in "${SERVICES[@]}"; do
    echo "$service"
done
```

### 1.5 函数

```bash
my_function() {
    local param1=$1
    local param2=$2
    echo "参数: $param1 $param2"
}

my_function "Alice" "28"
```

注意:

- 函数参数也是 `$1`、`$2`、`$@`
- `local` 声明局部变量,不加就是全局变量
- 函数返回值通常用 `echo` 输出,状态用 `return 0/1`

```bash
is_file_exists() {
    local file=$1
    [[ -f "$file" ]]
}

if is_file_exists "service.log"; then
    echo "文件存在"
fi
```

### 1.6 数组

```bash
names=("Alice" "Bob" "Cindy")

echo "${names[0]}"       # 第一个元素
echo "${names[@]}"       # 所有元素
echo "${#names[@]}"      # 数组长度

names+=("David")         # 追加元素
```

每次取两个元素:

```bash
SERVICES=(
    "用户服务" "http://127.0.0.1:8080/health"
    "订单服务" "http://127.0.0.1:8081/health"
)

for (( i=0; i<${#SERVICES[@]}; i+=2 )); do
    name=${SERVICES[$i]}
    url=${SERVICES[$i+1]}
    echo "$name -> $url"
done
```

### 1.7 数学运算

```bash
count=0
count=$((count + 1))
total=$((pass + fail))

if (( total > 10 )); then
    echo "total 大于 10"
fi
```

错误写法:

```bash
count = count + 1    # 错误
```

### 1.8 退出码

```bash
curl -s http://127.0.0.1:8080/health
echo $?    # 打印上一条命令的退出码

if [ $? -ne 0 ]; then
    echo "命令执行失败"
    exit 1
fi

exit 0    # 成功,CI/CD 显示绿色
exit 1    # 失败,CI/CD 显示红色
```

更推荐直接在 `if` 中判断:

```bash
if curl -fsS http://127.0.0.1:8080/health; then
    echo "服务正常"
else
    echo "服务异常"
    exit 1
fi
```

### 1.9 颜色输出

```bash
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
RESET="\033[0m"

echo -e "${RED}失败${RESET}"
echo -e "${GREEN}成功${RESET}"
echo -e "${YELLOW}警告${RESET}"
```

`\033[0m` 必须加,否则后续输出都会继承颜色。

### 1.10 后台运行

```bash
nohup python app.py > app.log 2>&1 &

echo "PID: $!"
```

含义:

| 写法 | 含义 |
|---|---|
| `nohup` | 退出 SSH 后进程继续运行 |
| `&` | 后台运行 |
| `2>&1` | stderr 合并到 stdout |
| `$!` | 上一个后台进程 PID |

### 1.11 管道和逐行处理

```bash
grep "ERROR" service.log \
    | awk '{print $4}' \
    | sort \
    | uniq -c \
    | sort -rn \
    | while read -r count path; do
        echo "  $count 次  $path"
    done
```

推荐使用 `read -r`,避免反斜杠被转义。

### 1.12 命令行参数解析

简单参数:

```bash
LOG_FILE=${1:-"service.log"}
THRESHOLD=${2:-100}
```

正式脚本推荐 `getopts`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

LOG_FILE="service.log"
THRESHOLD=100

usage() {
    echo "Usage: $0 -f <log_file> -t <threshold>"
    echo "Example: $0 -f service.log -t 100"
}

while getopts "f:t:h" opt; do
    case "$opt" in
        f) LOG_FILE="$OPTARG" ;;
        t) THRESHOLD="$OPTARG" ;;
        h) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
done

echo "LOG_FILE=$LOG_FILE"
echo "THRESHOLD=$THRESHOLD"
```

---

## 二、脚本稳定性和规范写法

### 2.1 日志函数

```bash
log_info() {
    echo "[$(date '+%F %T')] [INFO] $*"
}

log_warn() {
    echo "[$(date '+%F %T')] [WARN] $*" >&2
}

log_error() {
    echo "[$(date '+%F %T')] [ERROR] $*" >&2
}
```

`>&2` 表示输出到 stderr,适合错误日志。

### 2.2 输入校验

```bash
require_file() {
    local file=$1
    [[ -f "$file" ]] || { echo "文件不存在: $file" >&2; exit 1; }
}

require_dir() {
    local dir=$1
    [[ -d "$dir" ]] || { echo "目录不存在: $dir" >&2; exit 1; }
}

require_command() {
    local cmd=$1
    command -v "$cmd" >/dev/null 2>&1 || {
        echo "缺少命令: $cmd" >&2
        exit 1
    }
}

require_file "service.log"
require_command "curl"
```

### 2.3 curl 超时、重试和失败处理

```bash
http_code=$(curl -sS \
    --connect-timeout 3 \
    --max-time 10 \
    --retry 2 \
    -o /dev/null \
    -w "%{http_code}" \
    "$url")
```

建议:

- `--connect-timeout 3`:连接超时 3 秒
- `--max-time 10`:整个请求最多 10 秒
- `--retry 2`:失败重试 2 次
- `-sS`:静默但保留错误信息

### 2.4 临时文件和清理

```bash
tmp_file=$(mktemp)

cleanup() {
    rm -f "$tmp_file"
}

trap cleanup EXIT

echo "hello" > "$tmp_file"
cat "$tmp_file"
```

`trap cleanup EXIT` 可以保证脚本退出时清理临时文件。

### 2.5 敏感信息处理

不要把密码写死在脚本里:

```bash
DB_PASS="123456"    # 不推荐
```

推荐使用环境变量:

```bash
DB_PASS="${DB_PASS:?请先设置 DB_PASS 环境变量}"
```

运行:

```bash
export DB_PASS="your-password"
./backup_mysql.sh
```

### 2.6 ShellCheck 静态检查

安装后执行:

```bash
shellcheck script.sh
```

它可以发现:

- 变量未加引号
- 未使用变量
- 不安全的命令替换
- 管道失败未处理
- Bash/sh 兼容性问题

### 2.7 crontab 定时任务

查看定时任务:

```bash
crontab -l
```

编辑定时任务:

```bash
crontab -e
```

示例:

```bash
# 每 5 分钟执行一次健康检查
*/5 * * * * /bin/bash /opt/scripts/health_check.sh >> /var/log/health_cron.log 2>&1

# 每天凌晨 2 点备份数据库
0 2 * * * /bin/bash /opt/scripts/backup_mysql.sh >> /var/log/backup_mysql.log 2>&1
```

---

## 三、常见坑和铁律

### 铁律 1:用变量必须加 `$`

```bash
name="Alice"
echo name      # 错误:打印字符串 name
echo "$name"   # 正确:打印 Alice
```

### 铁律 2:等号两边不能有空格

```bash
name = "Alice"   # 错误
name="Alice"     # 正确
```

### 铁律 3:数字运算用 `$((...))`

```bash
count = count + 1        # 错误
count=$((count + 1))     # 正确
```

### 铁律 4:Shell 大小写严格

```bash
while True; do    # 错误
while true; do    # 正确
```

### 铁律 5:变量和文件名尽量加双引号

```bash
cat $LOG_FILE          # 不推荐,路径有空格会出错
cat "$LOG_FILE"        # 推荐
```

### 铁律 6:不要用 `grep -v grep` 查进程

可以用:

```bash
pgrep -f "myapp"
```

或者:

```bash
ps -ef | grep "[m]yapp"
```

### 铁律 7:用了 `set -e` 后要处理允许失败的命令

`grep` 找不到内容时退出码是 `1`,如果脚本开了 `set -e`,会直接退出。

```bash
errors=$(grep -c "ERROR" "$LOG_FILE" || true)
```

### 铁律 8:危险命令先预览再执行

```bash
# 先预览
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -print

# 确认无误后再删除
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
```

---

## 四、测开常用实战脚本

### 脚本 1:健康检查 + Webhook 报警

适用:定时检查服务是否存活,异常时写日志并发送钉钉/企业微信/飞书等 Webhook。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

LOG_FILE="/var/log/health_check.log"
CHECK_INTERVAL=30
WEBHOOK_URL="${WEBHOOK_URL:-}"

SERVICES=(
    "用户服务" "http://127.0.0.1:8080/health"
    "订单服务" "http://127.0.0.1:8081/health"
    "支付服务" "http://127.0.0.1:8082/health"
)

log_info() {
    echo "[$(date '+%F %T')] [INFO] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%F %T')] [ERROR] $*" | tee -a "$LOG_FILE" >&2
}

send_alert() {
    local msg=$1

    if [[ -z "$WEBHOOK_URL" ]]; then
        return 0
    fi

    curl -sS --connect-timeout 3 --max-time 10 \
        -H "Content-Type: application/json" \
        -d "{\"msgtype\":\"text\",\"text\":{\"content\":\"$msg\"}}" \
        "$WEBHOOK_URL" >/dev/null || true
}

check_service() {
    local name=$1
    local url=$2
    local http_code

    http_code=$(curl -sS \
        --connect-timeout 3 \
        --max-time 10 \
        --retry 2 \
        -o /dev/null \
        -w "%{http_code}" \
        "$url" || echo "000")

    if [[ "$http_code" == "200" ]]; then
        log_info "$name 正常 HTTP $http_code"
    else
        local msg="$name 异常 HTTP $http_code URL: $url"
        log_error "$msg"
        send_alert "$msg"
    fi
}

mkdir -p "$(dirname "$LOG_FILE")"
log_info "健康检查启动,每 ${CHECK_INTERVAL}s 检查一次"

while true; do
    for (( i=0; i<${#SERVICES[@]}; i+=2 )); do
        check_service "${SERVICES[$i]}" "${SERVICES[$i+1]}"
    done
    sleep "$CHECK_INTERVAL"
done
```

运行:

```bash
export WEBHOOK_URL="https://example.com/webhook"
bash health_check.sh
```

核心点:

- `curl --connect-timeout --max-time --retry` 防止请求卡死
- `WEBHOOK_URL` 用环境变量传入,避免写死
- `|| echo "000"` 把请求失败统一当成 HTTP 000

### 脚本 2:日志分析报告

适用:统计错误数量、Top 接口、每小时错误分布、最近错误。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

LOG_FILE=${1:-"service.log"}
THRESHOLD=${2:-100}

[[ -f "$LOG_FILE" ]] || { echo "日志文件不存在: $LOG_FILE" >&2; exit 1; }

echo "========================================"
echo "  日志分析报告 - $(date '+%F')"
echo "========================================"

total=$(wc -l < "$LOG_FILE")
errors=$(grep -c "ERROR" "$LOG_FILE" || true)
warns=$(grep -c "WARN" "$LOG_FILE" || true)

echo "【基本统计】"
echo "  总行数: $total  ERROR: $errors  WARN: $warns"

echo ""
echo "【错误最多的接口 Top 5】"
grep "ERROR" "$LOG_FILE" \
    | awk '{print $4}' \
    | sort \
    | uniq -c \
    | sort -rn \
    | head -5 \
    | while read -r count path; do
        echo "  $count 次  $path"
    done || true

echo ""
echo "【每小时错误分布】"
grep "ERROR" "$LOG_FILE" \
    | awk '{print substr($2, 1, 2)}' \
    | sort \
    | uniq -c \
    | while read -r count hour; do
        echo "  ${hour}:00  $count 次"
    done || true

echo ""
echo "【最近 10 条错误】"
grep "ERROR" "$LOG_FILE" | tail -10 || true

if (( errors > THRESHOLD )); then
    echo ""
    echo -e "\033[31m警告:错误数量($errors)超过阈值($THRESHOLD),请立即排查!\033[0m"
fi

echo ""
echo "报告生成完毕: $(date '+%F %T')"
```

运行:

```bash
bash log_report.sh service.log 100
```

### 脚本 3:批量接口冒烟测试

适用:CI/CD 发布后跑一组关键接口,失败时退出码为 `1`。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8080}"
PASS=0
FAIL=0
FAIL_LIST=()

test_api() {
    local method=$1
    local path=$2
    local data=$3
    local expected=$4
    local actual

    if [[ "$method" == "GET" ]]; then
        actual=$(curl -sS --connect-timeout 3 --max-time 10 \
            -o /dev/null -w "%{http_code}" \
            "$BASE_URL$path" || echo "000")
    else
        actual=$(curl -sS --connect-timeout 3 --max-time 10 \
            -o /dev/null -w "%{http_code}" \
            -X "$method" "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data" || echo "000")
    fi

    if [[ "$actual" == "$expected" ]]; then
        echo "  PASS  $method $path"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $method $path 期望:$expected 实际:$actual"
        FAIL=$((FAIL + 1))
        FAIL_LIST+=("$method $path 期望:$expected 实际:$actual")
    fi
}

echo "========================================"
echo "  接口冒烟测试  $(date '+%T')"
echo "========================================"

test_api "GET"  "/api/health"    ""                         "200"
test_api "GET"  "/api/users/1"   ""                         "200"
test_api "GET"  "/api/users/999" ""                         "404"
test_api "POST" "/api/users"     '{"name":"Test","age":20}' "201"

total=$((PASS + FAIL))
echo ""
echo "总数: $total  通过: $PASS  失败: $FAIL"

if (( FAIL > 0 )); then
    echo ""
    echo "失败用例:"
    printf '  %s\n' "${FAIL_LIST[@]}"
    exit 1
fi

echo "所有用例通过"
```

运行:

```bash
BASE_URL="http://test.example.com" bash smoke_api.sh
```

### 脚本 4:自动部署服务

适用:小型服务部署。正式生产更推荐使用 CI/CD、systemd、Docker 或 Kubernetes。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="myapp"
APP_DIR="/opt/$APP_NAME"
PORT=8080
LOG_FILE="/var/log/deploy.log"
APP_LOG="/var/log/$APP_NAME.log"

log() {
    echo "[$(date '+%F %T')] $*" | tee -a "$LOG_FILE"
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        log "缺少命令: $1"
        exit 1
    }
}

require_command git
require_command python
require_command curl

[[ -d "$APP_DIR" ]] || { log "目录不存在: $APP_DIR"; exit 1; }

log "========== 开始部署 $APP_NAME =========="

cd "$APP_DIR"

log "拉取代码"
git pull origin main

log "安装依赖"
pip install -r requirements.txt -q

old_pid=$(pgrep -f "$APP_DIR/app.py" || true)
if [[ -n "$old_pid" ]]; then
    log "停止旧服务 PID: $old_pid"
    kill "$old_pid"
    sleep 2
fi

log "启动新服务"
nohup python "$APP_DIR/app.py" > "$APP_LOG" 2>&1 &
new_pid=$!
log "新服务 PID: $new_pid"

sleep 3

http_code=$(curl -sS --connect-timeout 3 --max-time 10 \
    -o /dev/null -w "%{http_code}" \
    "http://127.0.0.1:$PORT/health" || echo "000")

if [[ "$http_code" == "200" ]]; then
    log "部署成功"
else
    log "部署失败 HTTP $http_code,查看日志: $APP_LOG"
    exit 1
fi
```

### 脚本 5:MySQL 数据库备份

适用:定时备份 MySQL 数据库,自动清理旧备份。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:?请设置 DB_PASS 环境变量}"
DB_NAME="${DB_NAME:-test_db}"
BACKUP_DIR="${BACKUP_DIR:-/data/backup/mysql}"
KEEP_DAYS="${KEEP_DAYS:-7}"

DATE=$(date "+%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "开始备份数据库: $DB_NAME"

MYSQL_PWD="$DB_PASS" mysqldump \
    -h "$DB_HOST" \
    -u "$DB_USER" \
    --single-transaction \
    --routines \
    --triggers \
    "$DB_NAME" \
    | gzip > "$BACKUP_FILE"

size=$(du -sh "$BACKUP_FILE" | cut -f1)
echo "备份成功: $BACKUP_FILE ($size)"

echo "准备清理 $KEEP_DAYS 天前的备份:"
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +"$KEEP_DAYS" -print
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +"$KEEP_DAYS" -delete

echo "当前备份文件:"
ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || true
```

运行:

```bash
export DB_PASS="your-password"
bash backup_mysql.sh
```

### 脚本 6:批量检查服务端口

适用:检查多个主机端口是否可连通。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

TARGETS=(
    "用户服务" "127.0.0.1" "8080"
    "订单服务" "127.0.0.1" "8081"
    "MySQL"   "127.0.0.1" "3306"
)

check_port() {
    local name=$1
    local host=$2
    local port=$3

    if timeout 3 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
        echo "PASS  $name $host:$port"
    else
        echo "FAIL  $name $host:$port"
        return 1
    fi
}

fail=0

for (( i=0; i<${#TARGETS[@]}; i+=3 )); do
    check_port "${TARGETS[$i]}" "${TARGETS[$i+1]}" "${TARGETS[$i+2]}" || fail=$((fail + 1))
done

if (( fail > 0 )); then
    echo "端口检查失败数量: $fail"
    exit 1
fi

echo "全部端口检查通过"
```

### 脚本 7:接口响应时间统计

适用:快速查看接口状态码、DNS 时间、连接时间、总耗时。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

URLS=(
    "http://127.0.0.1:8080/api/health"
    "http://127.0.0.1:8080/api/users/1"
    "http://127.0.0.1:8080/api/orders/1"
)

printf "%-50s %-8s %-10s %-10s %-10s\n" "URL" "HTTP" "DNS" "CONNECT" "TOTAL"

for url in "${URLS[@]}"; do
    result=$(curl -sS -o /dev/null \
        -w "%{http_code} %{time_namelookup} %{time_connect} %{time_total}" \
        --connect-timeout 3 \
        --max-time 10 \
        "$url" || echo "000 0 0 0")

    read -r code dns connect total <<< "$result"
    printf "%-50s %-8s %-10s %-10s %-10s\n" "$url" "$code" "$dns" "$connect" "$total"
done
```

### 脚本 8:从日志中提取 traceId/requestId

适用:排查链路问题,从日志中快速抽取请求 ID。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

LOG_FILE=${1:-"service.log"}

[[ -f "$LOG_FILE" ]] || { echo "日志文件不存在: $LOG_FILE" >&2; exit 1; }

echo "traceId Top 20:"
grep -Eo 'traceId=[a-zA-Z0-9_-]+' "$LOG_FILE" \
    | cut -d= -f2 \
    | sort \
    | uniq -c \
    | sort -rn \
    | head -20 || true

echo ""
echo "requestId Top 20:"
grep -Eo 'requestId=[a-zA-Z0-9_-]+' "$LOG_FILE" \
    | cut -d= -f2 \
    | sort \
    | uniq -c \
    | sort -rn \
    | head -20 || true
```

运行:

```bash
bash extract_ids.sh service.log
```

### 脚本 9:批量清理测试文件

适用:清理测试环境中的临时文件、历史报告、旧日志。默认先预览,加 `--delete` 才真正删除。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_DIR=${1:-"./tmp"}
KEEP_DAYS=${2:-7}
ACTION=${3:-"--dry-run"}

[[ -d "$TARGET_DIR" ]] || { echo "目录不存在: $TARGET_DIR" >&2; exit 1; }

echo "目标目录: $TARGET_DIR"
echo "保留天数: $KEEP_DAYS"
echo "模式: $ACTION"

if [[ "$ACTION" == "--delete" ]]; then
    echo "开始删除:"
    find "$TARGET_DIR" -type f -mtime +"$KEEP_DAYS" -print -delete
else
    echo "预览将删除的文件:"
    find "$TARGET_DIR" -type f -mtime +"$KEEP_DAYS" -print
    echo ""
    echo "确认无误后执行: bash cleanup_files.sh $TARGET_DIR $KEEP_DAYS --delete"
fi
```

运行:

```bash
bash cleanup_files.sh ./reports 7
bash cleanup_files.sh ./reports 7 --delete
```

### 脚本 10:CI 中运行测试并生成报告

适用:CI/CD 中统一运行测试,保存报告,失败时返回非 0 退出码。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

REPORT_DIR="${REPORT_DIR:-reports}"
REPORT_FILE="$REPORT_DIR/test_result_$(date '+%Y%m%d_%H%M%S').log"

mkdir -p "$REPORT_DIR"

echo "开始执行测试: $(date '+%F %T')" | tee "$REPORT_FILE"

set +e
pytest -q 2>&1 | tee -a "$REPORT_FILE"
test_exit=${PIPESTATUS[0]}
set -e

echo "" | tee -a "$REPORT_FILE"
echo "测试结束: $(date '+%F %T')" | tee -a "$REPORT_FILE"
echo "退出码: $test_exit" | tee -a "$REPORT_FILE"
echo "报告文件: $REPORT_FILE"

exit "$test_exit"
```

核心点:

- `PIPESTATUS[0]` 获取管道中 `pytest` 的退出码
- `tee` 同时输出到屏幕和报告文件
- 最后 `exit "$test_exit"` 让 CI 感知测试失败

### 脚本 11:磁盘、CPU、内存巡检

适用:测试环境机器巡检。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

DISK_THRESHOLD=${DISK_THRESHOLD:-80}
MEM_THRESHOLD=${MEM_THRESHOLD:-80}

echo "========================================"
echo "  系统巡检 $(date '+%F %T')"
echo "========================================"

echo ""
echo "【磁盘使用率】"
df -h

disk_alert=$(df -P | awk -v threshold="$DISK_THRESHOLD" 'NR>1 {gsub("%","",$5); if ($5 > threshold) print $6":"$5"%"}')
if [[ -n "$disk_alert" ]]; then
    echo "磁盘告警:"
    echo "$disk_alert"
fi

echo ""
echo "【内存使用率】"
free -m

mem_used_percent=$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')
if (( mem_used_percent > MEM_THRESHOLD )); then
    echo "内存告警: ${mem_used_percent}%"
fi

echo ""
echo "【CPU Top 5 进程】"
ps -eo pid,ppid,cmd,%cpu,%mem --sort=-%cpu | head -6

echo ""
echo "【内存 Top 5 进程】"
ps -eo pid,ppid,cmd,%cpu,%mem --sort=-%mem | head -6
```

### 脚本 12:Docker 容器日志分析

适用:从容器日志中统计错误、最近异常、关键字。

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

CONTAINER=${1:?"请传入容器名或容器 ID"}
LINES=${2:-1000}

command -v docker >/dev/null 2>&1 || { echo "缺少 docker 命令" >&2; exit 1; }

tmp_log=$(mktemp)
trap 'rm -f "$tmp_log"' EXIT

docker logs --tail "$LINES" "$CONTAINER" > "$tmp_log" 2>&1

echo "容器: $CONTAINER"
echo "分析最近 $LINES 行日志"

errors=$(grep -ciE "error|exception|failed" "$tmp_log" || true)
warns=$(grep -ci "warn" "$tmp_log" || true)

echo "ERROR/EXCEPTION/FAILED: $errors"
echo "WARN: $warns"

echo ""
echo "最近 20 条异常:"
grep -iE "error|exception|failed" "$tmp_log" | tail -20 || true
```

---

## 五、命令速查

| 命令/语法 | 用途 |
|---|---|
| `${1:-"默认值"}` | 参数默认值 |
| `${VAR:?错误信息}` | 必填变量校验 |
| `$(命令)` | 命令替换,把输出赋给变量 |
| `$((表达式))` | 数学运算 |
| `$?` | 上一条命令的退出码 |
| `$!` | 上一个后台进程的 PID |
| `$@` | 所有参数,保留参数边界 |
| `$#` | 参数个数 |
| `${#ARRAY[@]}` | 数组长度 |
| `local var=$1` | 函数局部变量 |
| `tee -a file` | 同时输出到屏幕和追加写文件 |
| `nohup cmd &` | 后台常驻运行 |
| `2>&1` | 错误输出合并到标准输出 |
| `cmd >/dev/null 2>&1` | 丢弃 stdout 和 stderr |
| `grep -c "pattern"` | 输出匹配行数 |
| `grep -E "a|b"` | 扩展正则匹配 |
| `grep -v "pattern"` | 排除匹配行 |
| `awk '{print $1}'` | 提取第一列 |
| `cut -d= -f2` | 按 `=` 分割取第二列 |
| `sort | uniq -c | sort -rn` | 统计频次并倒序 |
| `find . -type f -mtime +7 -print` | 查找 7 天前文件 |
| `find . -type f -mtime +7 -delete` | 删除 7 天前文件 |
| `pgrep -f "name"` | 按命令行查进程 |
| `kill "$pid"` | 停止进程 |
| `curl -o /dev/null -w "%{http_code}"` | 只输出 HTTP 状态码 |
| `curl --connect-timeout 3 --max-time 10` | 设置连接和总超时 |
| `shellcheck script.sh` | Shell 脚本静态检查 |
| `crontab -l` | 查看定时任务 |
| `crontab -e` | 编辑定时任务 |
| `exit 0 / exit 1` | 成功/失败退出,CI/CD 可感知 |

---

## 六、学习建议

### 6.1 建议掌握顺序

1. 变量、if、for、while、函数
2. 文件判断、字符串判断、数字判断
3. `grep`、`awk`、`sed`、`sort`、`uniq`、`find`
4. `curl` 接口检查
5. 退出码和 CI/CD 集成
6. `set -Eeuo pipefail`、`trap`、输入校验
7. ShellCheck 和 crontab

### 6.2 测开面试高频点

- `$?` 是什么
- `2>&1` 是什么
- `set -e` 和 `set -o pipefail` 的作用
- 如何统计日志中 ERROR 数量
- 如何找出错误最多的接口
- 如何判断接口是否健康
- 如何让脚本失败时让 CI/CD 感知
- 如何避免变量未加引号带来的问题
- 如何解析命令行参数
- 如何处理密码等敏感信息

### 6.3 写脚本前的检查清单

- 是否加了脚本头和必要的 `set` 选项
- 是否检查了输入参数
- 文件、目录、命令是否存在
- 变量是否都加了双引号
- 网络请求是否设置超时
- 失败时是否有明确退出码
- 日志是否能定位问题
- 删除操作是否先预览
- 密码是否没有写死
- 是否通过 ShellCheck

---

*Shell 脚本:测开工作常用脚本汇总。建议边复制边改成本公司真实服务名、接口、日志格式和部署方式。*
