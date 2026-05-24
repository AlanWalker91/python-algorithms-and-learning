# Shell 脚本笔记:测开工作常用脚本

> 学习日期:2025-05-23
> 主题:Shell 脚本语法 + 5 个测开常用脚本
> 适用:测试开发工程师面试 & 实战

---

## 目录

- [一、Shell 基础语法](#一shell-基础语法)
- [二、5 个常用脚本](#二5-个常用脚本)
- [三、常见坑和铁律](#三常见坑和铁律)
- [四、命令速查](#四命令速查)

---

## 一、Shell 基础语法

### 1.1 变量

```bash
# 定义(等号两边不能有空格!)
name="Alice"
port=8080

# 使用
echo "$name"
echo "${port}"      # 花括号用于边界不清晰时

# 参数默认值
LOG_FILE=${1:-"service.log"}    # 没传参数就用默认值
```

### 1.2 if 判断

```bash
if [ 条件 ]; then
    # 条件为真
elif [ 另一个条件 ]; then
    # 另一个条件
else
    # 都不满足
fi
```

**常用条件**:

| 条件 | 含义 |
|---|---|
| `[ "$a" = "$b" ]` | 字符串相等 |
| `[ "$a" != "$b" ]` | 字符串不等 |
| `[ -n "$a" ]` | 字符串非空 |
| `[ $n -eq 0 ]` | 数字等于 0 |
| `[ $n -gt 100 ]` | 数字大于 100 |
| `[ $n -lt 5 ]` | 数字小于 5 |
| `[ -f "/path" ]` | 文件存在 |
| `[ -d "/path" ]` | 目录存在 |

### 1.3 循环

```bash
# while 无限循环
while true; do
    # 做事情
    sleep 30
done

# for 遍历列表
for item in a b c; do
    echo "$item"
done

# for 遍历数组(每次取两个)
for (( i=0; i<${#ARRAY[@]}; i+=2 )); do
    name=${ARRAY[$i]}
    url=${ARRAY[$i+1]}
done
```

### 1.4 函数

```bash
# 定义
my_function() {
    local param1=$1    # $1 是第一个参数
    local param2=$2    # $2 是第二个参数
    echo "参数: $param1 $param2"
}

# 调用
my_function "Alice" "28"
```

**`local` 声明局部变量**——不加 local 是全局变量,可能污染其他函数。

### 1.5 数学运算

```bash
# 必须用 $(()) 
count=0
count=$((count + 1))
total=$((pass + fail))

# ❌ 错误写法:
count = count + 1    # 报错
```

### 1.6 退出码

```bash
# 每个命令执行后都有退出码
# 0 = 成功,非 0 = 失败
curl -s http://127.0.0.1:8080/health
echo $?    # 打印上一条命令的退出码

# 用退出码做判断
if [ $? -ne 0 ]; then
    echo "命令执行失败"
    exit 1
fi

# 脚本主动退出
exit 0    # 成功(CI/CD 显示绿色)
exit 1    # 失败(CI/CD 显示红色、发报警)
```

### 1.7 颜色输出

```bash
echo -e "\033[31m 红色(失败) \033[0m"
echo -e "\033[32m 绿色(成功) \033[0m"
echo -e "\033[33m 黄色(警告) \033[0m"
# \033[0m = 重置颜色,必须加,否则后续输出都是该颜色
```

### 1.8 后台运行

```bash
nohup python app.py > app.log 2>&1 &
# nohup  = 退出 SSH 也继续跑
# &      = 后台运行
# 2>&1   = 错误输出合并到标准输出
# $!     = 刚启动的后台进程的 PID
```

### 1.9 while read:逐行处理管道输出

```bash
grep "ERROR" service.log \
    | awk '{print $4}' \
    | sort | uniq -c \
    | while read count path; do
        echo "  $count 次  $path"    # 自由格式化输出
    done
```

---

## 二、5 个常用脚本

### 脚本 1:健康检查 + 自动报警

```bash
#!/bin/bash

LOG_FILE="/var/log/health_check.log"
CHECK_INTERVAL=30

SERVICES=(
    "用户服务"    "http://127.0.0.1:8080/health"
    "订单服务"    "http://127.0.0.1:8081/health"
    "支付服务"    "http://127.0.0.1:8082/health"
)

check_service() {
    local name=$1
    local url=$2
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$http_code" = "200" ]; then
        echo "[$timestamp] ✅ $name 正常 (HTTP $http_code)"
    else
        local msg="[$timestamp] ❌ $name 异常! HTTP $http_code URL: $url"
        echo "$msg"
        echo "$msg" >> "$LOG_FILE"
    fi
}

echo "健康检查启动,每 ${CHECK_INTERVAL}s 检查一次"

while true; do
    echo "--- $(date '+%H:%M:%S') 开始检查 ---"
    for (( i=0; i<${#SERVICES[@]}; i+=2 )); do
        check_service "${SERVICES[$i]}" "${SERVICES[$i+1]}"
    done
    sleep $CHECK_INTERVAL
done
```

**核心点**:
- `while true` + `sleep` = 定时轮询
- `curl -w "%{http_code}"` = 只取状态码
- `>> "$LOG_FILE"` = 异常才写日志

### 脚本 2:日志分析报告

```bash
#!/bin/bash

LOG_FILE=${1:-"service.log"}
DATE=$(date "+%Y-%m-%d")
THRESHOLD=100

echo "========================================"
echo "  日志分析报告 - $DATE"
echo "========================================"

total=$(wc -l < "$LOG_FILE")
errors=$(grep -c "ERROR" "$LOG_FILE")
warns=$(grep -c "WARN" "$LOG_FILE")

echo "【基本统计】"
echo "  总行数: $total  ERROR: $errors  WARN: $warns"

echo ""
echo "【错误最多的接口 Top 5】"
grep "ERROR" "$LOG_FILE" \
    | awk '{print $4}' \
    | sort | uniq -c | sort -rn \
    | head -5 \
    | while read count path; do
        echo "  $count 次  $path"
    done

echo ""
echo "【每小时错误分布】"
grep "ERROR" "$LOG_FILE" \
    | awk '{print substr($2, 1, 2)}' \
    | sort | uniq -c \
    | while read count hour; do
        echo "  ${hour}:00  $count 次"
    done

echo ""
echo "【最近 10 条错误】"
grep "ERROR" "$LOG_FILE" | tail -10

# 阈值报警
if [ "$errors" -gt "$THRESHOLD" ]; then
    echo ""
    echo -e "\033[31m⚠️  警告:错误数量($errors)超过阈值($THRESHOLD),请立即排查!\033[0m"
fi

echo ""
echo "报告生成完毕: $(date '+%Y-%m-%d %H:%M:%S')"
```

**核心点**:
- `${1:-"默认值"}` = 参数默认值
- `grep -c` = 直接输出匹配行数
- `substr($2, 1, 5)` = 截取时间到分钟精度

### 脚本 3:批量接口测试

```bash
#!/bin/bash

BASE_URL="http://127.0.0.1:8080"
PASS=0
FAIL=0
FAIL_LIST=""

test_api() {
    local method=$1
    local path=$2
    local data=$3
    local expected=$4

    if [ "$method" = "GET" ]; then
        actual=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$path")
    else
        actual=$(curl -s -o /dev/null -w "%{http_code}" \
            -X POST "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    if [ "$actual" = "$expected" ]; then
        echo "  ✅ PASS  $method $path"
        PASS=$((PASS + 1))
    else
        echo "  ❌ FAIL  $method $path (期望 $expected,实际 $actual)"
        FAIL=$((FAIL + 1))
        FAIL_LIST="$FAIL_LIST\n  $method $path"
    fi
}

echo "========================================"
echo "  接口冒烟测试  $(date '+%H:%M:%S')"
echo "========================================"

test_api "GET"  "/api/health"    ""                         "200"
test_api "GET"  "/api/users/1"   ""                         "200"
test_api "GET"  "/api/users/999" ""                         "404"
test_api "POST" "/api/users"     '{"name":"Test","age":20}' "201"

total=$((PASS + FAIL))
echo ""
echo "总数: $total  通过: $PASS  失败: $FAIL"

if [ $FAIL -gt 0 ]; then
    echo -e "\033[31m失败的用例:\033[0m"
    echo -e "$FAIL_LIST"
    exit 1
else
    echo -e "\033[32m所有用例通过!\033[0m"
    exit 0
fi
```

**核心点**:
- `exit 1` = CI/CD 能感知测试失败
- `$((PASS + 1))` = Shell 数学运算
- 颜色区分通过/失败

### 脚本 4:自动部署服务

```bash
#!/bin/bash

APP_NAME="myapp"
APP_DIR="/opt/$APP_NAME"
PORT=8080
LOG_FILE="/var/log/deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_result() {
    if [ $? -ne 0 ]; then
        log "❌ 失败: $1"
        exit 1
    fi
    log "✅ 成功: $1"
}

log "========== 开始部署 $APP_NAME =========="

# 1. 拉代码
cd "$APP_DIR" && git pull origin main
check_result "拉取代码"

# 2. 安装依赖
pip install -r requirements.txt -q
check_result "安装依赖"

# 3. 停止旧服务
old_pid=$(ps -ef | grep "$APP_NAME" | grep -v grep | awk '{print $2}')
if [ -n "$old_pid" ]; then
    kill "$old_pid"
    sleep 2
fi

# 4. 启动新服务
nohup python "$APP_DIR/app.py" > /var/log/$APP_NAME.log 2>&1 &
sleep 3

# 5. 健康检查
http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/health")
if [ "$http_code" = "200" ]; then
    log "✅ 部署成功!"
else
    log "❌ 部署失败! HTTP $http_code"
    exit 1
fi
```

**核心点**:
- `tee -a` = 同时输出到屏幕和文件
- `$?` = 上一条命令退出码
- `grep -v grep` = 过滤掉 grep 自身进程
- `nohup ... &` = 后台常驻运行

### 脚本 5:数据库备份

```bash
#!/bin/bash

DB_HOST="127.0.0.1"
DB_USER="root"
DB_PASS="123456"
DB_NAME="test_db"
BACKUP_DIR="/data/backup/mysql"
KEEP_DAYS=7

DATE=$(date "+%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz"

mkdir -p "$BACKUP_DIR"

# 备份 + 压缩
mysqldump -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" \
    | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    size=$(du -sh "$BACKUP_FILE" | cut -f1)
    echo "✅ 备份成功: $BACKUP_FILE ($size)"
else
    echo "❌ 备份失败!"
    exit 1
fi

# 清理 7 天前的旧备份
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$KEEP_DAYS -delete
echo "已清理 $KEEP_DAYS 天前的备份"

ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null
```

**核心点**:
- `mysqldump | gzip` = 边备份边压缩,节省空间
- `find -mtime +7 -delete` = 自动清理旧文件
- `cut -f1` = 提取第一列

---

## 三、常见坑和铁律

### 铁律 1:用变量必须加 `$`

```bash
name="Alice"
echo name      # ❌ 打印字符串"name"
echo "$name"   # ✅ 打印"Alice"
```

### 铁律 2:等号两边不能有空格

```bash
name = "Alice"   # ❌ 报错
name="Alice"     # ✅
```

### 铁律 3:数字运算用 `$(())`

```bash
count = count + 1        # ❌ 报错
count=$((count + 1))     # ✅
```

### 铁律 4:Shell 大小写严格

```bash
while True; do    # ❌ True 不存在
while true; do    # ✅
```

### 铁律 5:文件名/变量名加引号防空格

```bash
cat $LOG_FILE          # ❌ 如果路径有空格会报错
cat "$LOG_FILE"        # ✅ 加引号防空格
```

### 铁律 6:grep 要过滤自身

```bash
ps -ef | grep "myapp"              # ❌ 会多出 grep 自身那行
ps -ef | grep "myapp" | grep -v grep  # ✅
```

---

## 四、命令速查

| 命令/语法 | 用途 |
|---|---|
| `${1:-"默认值"}` | 参数默认值 |
| `$(命令)` | 命令替换,把输出赋给变量 |
| `$((表达式))` | 数学运算 |
| `$?` | 上一条命令的退出码 |
| `$!` | 上一个后台进程的 PID |
| `${#ARRAY[@]}` | 数组长度 |
| `local var=$1` | 函数局部变量 |
| `tee -a file` | 同时输出到屏幕和文件 |
| `nohup cmd &` | 后台常驻运行 |
| `2>&1` | 错误输出合并到标准输出 |
| `grep -c "pattern"` | 直接输出匹配行数 |
| `grep -v grep` | 过滤掉 grep 自身 |
| `cut -f1` | 提取第一列 |
| `find -mtime +7 -delete` | 删除 7 天前的文件 |
| `exit 0 / exit 1` | 成功/失败退出(CI/CD 感知) |

---

*Shell 脚本:测开工作 5 大常用场景 —— 完结。*
