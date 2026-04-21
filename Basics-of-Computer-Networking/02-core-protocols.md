# 阶段 2：核心协议深入（2–3 周）

> 本阶段是面试的核心战场。TCP 和 HTTP 两个协议合计占面试网络题 70% 以上。
> 学习原则：不仅要知道"是什么"，更要能回答"为什么这样设计"。

---

## 一、TCP 协议（最重要，至少投入 1 周）

### 学习目标

- [ ] 理解 TCP 面向连接、可靠传输的核心设计思想
- [ ] 能画出并讲解三次握手和四次挥手的完整过程
- [ ] 理解 TCP 状态机中的关键状态及转换条件
- [ ] 知道滑动窗口和拥塞控制的基本原理
- [ ] 能解释粘包问题及解决方案

### 必学内容

#### 1.1 TCP 报文结构

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          源端口号 (16)        |        目的端口号 (16)        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       序列号 seq (32)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     确认号 ack (32)                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| 偏移 |保留 |U|A|P|R|S|F|        窗口大小 (16)                |
|  (4) | (6) |R|C|S|S|Y|I|                                     |
|      |     |G|K|H|T|N|N|                                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         校验和 (16)           |       紧急指针 (16)           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

关键标志位：
  SYN = 1 → 请求建立连接
  ACK = 1 → 确认号有效
  FIN = 1 → 请求关闭连接
  RST = 1 → 强制重置连接
  PSH = 1 → 接收方应立即将数据推给应用层
  URG = 1 → 紧急指针有效
```

#### 1.2 三次握手（建立连接）

```
    客户端 (Client)                            服务端 (Server)
    状态: CLOSED                               状态: LISTEN
        │                                          │
        │──────── SYN, seq=x ─────────────────────>│
        │         （我想和你建立连接）               │
        │  状态→ SYN_SENT                    状态→ SYN_RCVD
        │                                          │
        │<──── SYN+ACK, seq=y, ack=x+1 ───────────│
        │      （好的，我也想和你连接）              │
        │                                          │
        │──────── ACK, ack=y+1 ───────────────────>│
        │         （收到，连接建立）                  │
        │  状态→ ESTABLISHED               状态→ ESTABLISHED
        │                                          │
        ▼          可以开始传输数据                   ▼
```

**为什么是三次而不是两次？**

> 核心原因：防止**历史重复连接**导致资源浪费。
> 
> 假设只有两次握手：客户端发的一个旧 SYN 在网络中延迟了很久，终于到达服务端。
> 服务端以为是新连接，直接分配资源进入 ESTABLISHED 状态等待数据。
> 但客户端根本不知道这个连接，服务端就白白浪费了资源。
> 
> 三次握手时，服务端回 SYN+ACK 后必须等客户端的 ACK 确认。
> 客户端收到旧连接的 SYN+ACK 会发现序列号对不上，直接发 RST 拒绝，服务端就不会浪费资源。
> 
> 另一个角度：三次握手是确认双方**收发能力**的最少次数。
> 第一次：服务端确认"客户端能发"
> 第二次：客户端确认"服务端能收能发"
> 第三次：服务端确认"客户端能收"

**为什么不是四次？**

> SYN 和 ACK 可以合并在一个报文中（第二步），没必要分开发。

#### 1.3 四次挥手（断开连接）

```
    客户端 (Client)                            服务端 (Server)
    状态: ESTABLISHED                          状态: ESTABLISHED
        │                                          │
        │──────── FIN, seq=u ─────────────────────>│  ① 客户端请求关闭
        │  状态→ FIN_WAIT_1                  状态→ CLOSE_WAIT
        │                                          │
        │<──────── ACK, ack=u+1 ───────────────────│  ② 服务端确认（但可能还有数据要发）
        │  状态→ FIN_WAIT_2                        │
        │                                          │  （服务端继续发送剩余数据...）
        │                                          │
        │<──────── FIN, seq=w ─────────────────────│  ③ 服务端也请求关闭
        │  状态→ TIME_WAIT                   状态→ LAST_ACK
        │                                          │
        │──────── ACK, ack=w+1 ───────────────────>│  ④ 客户端确认
        │                                    状态→ CLOSED
        │  等待 2MSL ...                           │
        │  状态→ CLOSED                            │
```

**为什么挥手是四次不是三次？**

> 握手时服务端的 SYN 和 ACK 可以合并，但挥手时不行。
> 原因：收到客户端 FIN 时，服务端可能还有数据没发完，所以先回 ACK 表示"我知道了"，
> 等数据全发完后再发 FIN 表示"我也准备好关了"。这两步不能合并。

**TIME_WAIT 为什么要等 2MSL？**

> MSL = Maximum Segment Lifetime（报文最大生存时间），通常 30 秒或 2 分钟。
> 
> 原因 1：确保最后一个 ACK 能到达服务端。
> 如果 ACK 丢了，服务端会重发 FIN，客户端在 TIME_WAIT 期间还能响应。
> 
> 原因 2：确保本次连接的所有报文从网络中消失。
> 防止旧连接的残留报文干扰后续新连接（特别是使用相同四元组时）。

#### 1.4 TCP 状态机（关键状态）

```
面试中需要知道的关键状态：

  LISTEN        → 服务端等待连接
  SYN_SENT      → 客户端已发 SYN，等待 SYN+ACK
  SYN_RCVD      → 服务端已收 SYN 并回了 SYN+ACK，等待 ACK
  ESTABLISHED   → 连接已建立，可以传数据
  FIN_WAIT_1    → 主动关闭方已发 FIN，等待 ACK
  FIN_WAIT_2    → 主动关闭方已收到 ACK，等待对方 FIN
  CLOSE_WAIT    → 被动关闭方已收到 FIN，回了 ACK
  LAST_ACK      → 被动关闭方已发 FIN，等待最后的 ACK
  TIME_WAIT     → 主动关闭方已收到 FIN 并回了 ACK，等待 2MSL
  CLOSED        → 连接完全关闭

面试高频点：
  - CLOSE_WAIT 堆积 → 说明服务端代码没有正确 close() 连接
  - TIME_WAIT 堆积 → 高并发短连接场景，端口耗尽
```

#### 1.5 TCP 可靠传输机制

```
TCP 保证可靠传输的 6 个核心机制：

1. 序列号 (Sequence Number)
   → 每个字节都有唯一编号，接收方按序重组

2. 确认应答 (ACK)
   → 接收方告诉发送方"我收到了 xxx 之前的所有数据"
   → 累积确认：ACK=1000 表示 999 及之前的都收到了

3. 超时重传 (Retransmission Timeout)
   → 发送后启动定时器，超时未收到 ACK 就重传
   → RTO 动态计算（基于 RTT 采样）

4. 滑动窗口 (Sliding Window) — 流量控制
   → 接收方通过 window size 字段告诉发送方"我还能接收多少数据"
   → 发送方不能发超过窗口大小的数据
   → 窗口为 0 → 发送方暂停，定期发探测报文

5. 拥塞控制 (Congestion Control)
   → 防止发送方发太快导致网络拥塞
   → 四个算法：慢启动 → 拥塞避免 → 快重传 → 快恢复

6. 校验和 (Checksum)
   → 发送方计算校验和，接收方验证数据完整性
   → 不匹配则丢弃该报文
```

#### 1.6 拥塞控制（四个算法）

```
cwnd = 拥塞窗口，由发送方维护
ssthresh = 慢启动阈值

          cwnd
           ▲
           │          ┌──── 拥塞避免（线性增长）
           │         /
           │        /
           │   ┌───/
 ssthresh ─│──/  ← 到达阈值后，从指数增长变为线性增长
           │ /
           │/  ← 慢启动（指数增长）
           │
           └──────────────────────────> 时间

1. 慢启动 (Slow Start)
   cwnd 从 1 开始，每收到一个 ACK，cwnd 翻倍（指数增长）
   直到 cwnd >= ssthresh

2. 拥塞避免 (Congestion Avoidance)
   cwnd >= ssthresh 后，每个 RTT 只增加 1（线性增长）

3. 快重传 (Fast Retransmit)
   收到 3 个重复 ACK → 立即重传丢失的报文（不等超时）

4. 快恢复 (Fast Recovery)
   快重传后不回到慢启动
   → ssthresh = cwnd/2
   → cwnd = ssthresh + 3
   → 继续拥塞避免
```

#### 1.7 TCP 粘包问题

```
问题本质：TCP 是字节流协议，没有消息边界

  发送方发了两条消息：
    消息1: "Hello"
    消息2: "World"

  接收方可能收到的情况：
    正常：  "Hello" + "World"      （两次 recv）
    粘包：  "HelloWorld"           （一次 recv 收到两条）
    拆包：  "Hel" + "loWorld"      （消息被拆开了）

原因：
  ① Nagle 算法合并小包
  ② 接收方缓冲区积压
  ③ 应用层读取速度 < 到达速度

解决方案（4种）：
  ① 固定长度消息（每条消息固定 N 字节，不足补齐）
  ② 分隔符（每条消息以 \r\n 或特殊字符结尾）
  ③ 长度前缀（消息头部携带 4 字节表示消息体长度）  ← 最常用
  ④ 使用更高层协议（如 HTTP 自带 Content-Length）
```

**Python 长度前缀方案示例：**

```python
import struct
import socket

def send_msg(sock: socket.socket, data: bytes):
    """发送：4字节长度头 + 消息体"""
    length = struct.pack('>I', len(data))   # 大端序 4 字节无符号整数
    sock.sendall(length + data)

def recv_msg(sock: socket.socket) -> bytes:
    """接收：先读 4 字节长度，再读对应长度的消息体"""
    raw_len = recv_all(sock, 4)
    if not raw_len:
        return b''
    msg_len = struct.unpack('>I', raw_len)[0]
    return recv_all(sock, msg_len)

def recv_all(sock: socket.socket, n: int) -> bytes:
    """确保读满 n 个字节"""
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("连接断开")
        data += chunk
    return data
```

### 推荐学习顺序

```
Day 1:   TCP 报文结构 → 标志位含义
Day 2:   三次握手（过程 + 为什么三次）
Day 3:   四次挥手（过程 + TIME_WAIT + 为什么四次）
Day 4:   TCP 状态机（重点：CLOSE_WAIT / TIME_WAIT）
Day 5:   可靠传输（序列号 + ACK + 重传 + 滑动窗口）
Day 6:   拥塞控制（四个算法的触发条件和行为）
Day 7:   粘包问题 + 长度前缀方案编码实践
```

### 实践任务

#### 任务 1：Wireshark 抓三次握手

```
1. 打开 Wireshark，选择网卡
2. 过滤器输入：tcp.port == 80
3. 浏览器访问 http://httpbin.org
4. 找到 SYN → SYN+ACK → ACK 三个包
5. 逐字段记录：源端口、目的端口、seq、ack、标志位、窗口大小
```

#### 任务 2：观察 TIME_WAIT

```bash
# Linux / Mac
# 发起大量短连接后查看 TIME_WAIT 数量
ss -tan | grep TIME-WAIT | wc -l

# 或者用 netstat
netstat -an | grep TIME_WAIT | wc -l
```

#### 任务 3：Python 实现粘包解决方案
用上面的长度前缀代码，写一个 TCP 客户端/服务端，验证多条消息能被正确分割。

### 达成标准

- [ ] 能在白板上画出三次握手和四次挥手的完整时序图
- [ ] 能解释为什么握手三次、挥手四次
- [ ] 能说出 TIME_WAIT 的原因和解决方案
- [ ] 能说出 CLOSE_WAIT 堆积的原因
- [ ] 能列举 TCP 保证可靠传输的 6 个机制
- [ ] 能用自己的话讲清拥塞控制的四个算法
- [ ] 能写出粘包解决方案的代码

---

## 二、UDP 协议

### 核心理解

```
UDP 的核心特点（面试对比 TCP 时用）：

  无连接    → 不需要握手，直接发数据
  不可靠    → 不保证到达、不保证顺序、没有重传
  无拥塞控制 → 不管网络多堵都照发不误
  头部开销小 → 只有 8 字节（TCP 是 20 字节）
  面向数据报 → 每个 UDP 报文是独立的，有消息边界（不会粘包）
```

### TCP vs UDP 对比（面试必背）

| 特性 | TCP | UDP |
|------|-----|-----|
| 连接方式 | 面向连接（三次握手） | 无连接 |
| 可靠性 | 可靠（ACK、重传、有序） | 不可靠 |
| 有序性 | 保证有序 | 不保证 |
| 传输方式 | 字节流（无边界） | 数据报（有边界） |
| 头部大小 | 20 字节 | 8 字节 |
| 拥塞控制 | 有 | 无 |
| 传输效率 | 较低 | 高 |
| 粘包问题 | 有 | 无 |
| 适用场景 | HTTP、文件传输、邮件 | DNS、视频直播、游戏、VoIP |

### 面试加分回答

> "TCP 和 UDP 的选择本质上是**可靠性**和**实时性**的取舍。
> 需要数据完整不丢的场景用 TCP，能容忍少量丢包但要求低延迟的场景用 UDP。
> 现代很多应用会在 UDP 之上自己实现可靠传输（如 QUIC 协议），
> 既保留了 UDP 的灵活性，又实现了需要的可靠性级别。"

### 实践任务

```python
# 写一个 UDP 回显服务，体验 UDP 的"无连接"特性
import socket

# 服务端
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('0.0.0.0', 9999))
print("UDP 服务端启动")
while True:
    data, addr = server.recvfrom(1024)
    print(f"收到来自 {addr}: {data.decode()}")
    server.sendto(f"Echo: {data.decode()}".encode(), addr)
```

---

## 三、HTTP / HTTPS 协议

### 必学内容

#### 3.1 HTTP 请求报文结构

```
请求报文 = 请求行 + 请求头 + 空行 + 请求体

POST /api/users HTTP/1.1              ← 请求行（方法 路径 版本）
Host: api.example.com                 ← 请求头
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJ...
Content-Length: 27
Accept: application/json
User-Agent: python-requests/2.31
                                      ← 空行（CRLF）
{"name":"test","age":25}              ← 请求体
```

#### 3.2 HTTP 响应报文结构

```
响应报文 = 状态行 + 响应头 + 空行 + 响应体

HTTP/1.1 200 OK                       ← 状态行（版本 状态码 描述）
Content-Type: application/json        ← 响应头
Content-Length: 52
Set-Cookie: session=abc123; HttpOnly
Cache-Control: no-cache
                                      ← 空行
{"id":1,"name":"test","age":25}       ← 响应体
```

#### 3.3 HTTP 方法（语义与幂等性）

| 方法 | 语义 | 幂等 | 安全 | 有请求体 | 说明 |
|------|------|------|------|----------|------|
| GET | 获取资源 | ✅ | ✅ | 否 | 查询操作 |
| POST | 创建资源 | ❌ | ❌ | 是 | 提交数据 |
| PUT | 全量更新 | ✅ | ❌ | 是 | 替换整个资源 |
| PATCH | 部分更新 | ❌ | ❌ | 是 | 修改部分字段 |
| DELETE | 删除资源 | ✅ | ❌ | 否 | 删除资源 |
| HEAD | 同 GET 但只返回头 | ✅ | ✅ | 否 | 检查资源存在/大小 |
| OPTIONS | 查询支持的方法 | ✅ | ✅ | 否 | CORS 预检请求 |

**幂等**：同一请求执行多次，效果与执行一次相同。
**安全**：不会修改服务端资源。

#### 3.4 HTTP 状态码（必背清单）

```
2xx 成功：
  200 OK                  → 请求成功
  201 Created             → 资源已创建（POST 成功常用）
  204 No Content          → 成功但无返回体（DELETE 常用）

3xx 重定向：
  301 Moved Permanently   → 永久重定向（URL 已永久变更）
  302 Found               → 临时重定向（URL 临时变更）
  304 Not Modified        → 资源未修改，使用缓存

4xx 客户端错误：
  400 Bad Request         → 请求参数/格式有误
  401 Unauthorized        → 未认证（没有登录/Token 无效）
  403 Forbidden           → 已认证但无权限
  404 Not Found           → 资源不存在
  405 Method Not Allowed  → 请求方法不支持
  408 Request Timeout     → 客户端请求超时
  422 Unprocessable Entity→ 参数格式正确但语义错误
  429 Too Many Requests   → 请求频率超限（限流）

5xx 服务端错误：
  500 Internal Server Error → 服务器内部异常
  502 Bad Gateway           → 网关/代理收到上游无效响应
  503 Service Unavailable   → 服务暂不可用（过载/维护）
  504 Gateway Timeout       → 网关等待上游响应超时
```

**面试重点辨析：**

| 对比 | 区别 |
|------|------|
| 401 vs 403 | 401=没登录/认证失败，403=登录了但没权限 |
| 301 vs 302 | 301=永久搬家（搜索引擎更新URL），302=临时搬家 |
| 500 vs 502 | 500=本服务挂了，502=上游服务挂了 |
| 502 vs 504 | 502=上游返回了错误，504=上游没响应（超时） |

#### 3.5 HTTP 版本演进

```
HTTP/1.0 → HTTP/1.1 → HTTP/2 → HTTP/3

HTTP/1.0:
  每次请求新建 TCP 连接，用完就断
  无 Host 头（一个 IP 只能部署一个网站）

HTTP/1.1（目前仍广泛使用）:
  ✅ 默认 keep-alive（长连接，复用 TCP）
  ✅ 支持 Pipeline（但有队头阻塞 Head-of-line Blocking）
  ✅ 新增 Host 头（虚拟主机，一个 IP 多个网站）
  ✅ 新增 PUT / PATCH / DELETE / OPTIONS
  ✅ 断点续传（Range 头）
  ❌ 队头阻塞：前一个请求的响应没到，后面的请求都得等

HTTP/2:
  ✅ 多路复用（一个连接并行多个请求，解决队头阻塞）
  ✅ 二进制分帧（不再是文本协议）
  ✅ 头部压缩（HPACK 算法）
  ✅ 服务端推送（Server Push）
  ❌ 基于 TCP，TCP 层仍有队头阻塞

HTTP/3:
  ✅ 基于 QUIC（底层用 UDP 而非 TCP）
  ✅ 彻底解决队头阻塞
  ✅ 更快的连接建立（0-RTT）
```

#### 3.6 HTTPS 与 TLS 握手

```
HTTPS = HTTP + TLS/SSL

TLS 握手简化流程：
  客户端                              服务端
    │                                    │
    │── ClientHello ────────────────────>│  (支持的加密套件、随机数A)
    │                                    │
    │<── ServerHello + 证书 ────────────│  (选定加密套件、随机数B、公钥证书)
    │                                    │
    │   验证证书 → 生成预主密钥          │
    │── 用公钥加密预主密钥 ────────────>│
    │                                    │  用私钥解密
    │                                    │
    │   双方用 随机数A+B+预主密钥        │
    │   生成相同的对称密钥               │
    │                                    │
    │<════════ 后续通信用对称加密 ═══════>│

关键点：
  非对称加密（RSA/ECC）用于安全交换密钥
  对称加密（AES）用于实际数据传输（性能好）
  数字证书用于验证服务端身份（防中间人攻击）
```

#### 3.7 Cookie / Session / Token

```
三种身份认证机制对比：

Cookie:
  存储位置：客户端浏览器
  传输方式：每次请求自动携带（Set-Cookie → Cookie 头）
  安全性：  可被 XSS 窃取（需设 HttpOnly）
  跨域：    受同源策略限制

Session:
  存储位置：服务端（内存/Redis）
  传输方式：通过 Cookie 传 Session ID
  状态：    有状态（服务端需存储）
  问题：    分布式环境需共享 Session（Redis/数据库）

Token (JWT):
  存储位置：客户端（localStorage / Cookie）
  传输方式：手动放 Authorization 头（Bearer token）
  状态：    无状态（服务端只需验证签名）
  优势：    天然支持分布式、跨域
  结构：    Header.Payload.Signature（Base64 编码）
```

### 实践任务

#### 任务 1：curl 全方位调试

```bash
# GET 请求
curl -v https://httpbin.org/get

# POST JSON
curl -v -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"name":"test","age":25}'

# 查看响应头
curl -I https://www.baidu.com

# 带 Cookie
curl -b "session=abc123" https://httpbin.org/cookies

# 查看重定向链
curl -vL https://httpbin.org/redirect/3

# 设置超时
curl --connect-timeout 5 --max-time 10 https://httpbin.org/delay/3
```

#### 任务 2：用 Python requests 验证各种场景

```python
import requests

# 验证状态码
print(requests.get('https://httpbin.org/status/404').status_code)  # 404
print(requests.get('https://httpbin.org/status/500').status_code)  # 500

# 验证重定向
resp = requests.get('https://httpbin.org/redirect/2', allow_redirects=False)
print(resp.status_code)  # 302
print(resp.headers['Location'])  # 下一跳 URL

# 验证 Cookie
resp = requests.get('https://httpbin.org/cookies/set/mycookie/myvalue',
                     allow_redirects=True)
print(resp.json())  # 查看 Cookie
```

---

## 四、DNS 协议

### 必学内容

#### 4.1 DNS 解析流程

```
浏览器要访问 www.example.com：

1. 浏览器 DNS 缓存 → 没有
2. 操作系统 DNS 缓存 → 没有
3. 本地 hosts 文件 (/etc/hosts) → 没有
4. 本地 DNS 服务器（递归查询）→ 没有缓存
5. 开始迭代查询：
   本地DNS → 根域名服务器 (.)          "去问 .com 的服务器"
   本地DNS → .com 顶级域服务器         "去问 example.com 的服务器"
   本地DNS → example.com 权威DNS服务器  "www.example.com = 93.184.216.34"
6. 本地 DNS 缓存结果并返回给客户端

递归查询 vs 迭代查询：
  递归：客户端 → 本地DNS（"你帮我查到底"）
  迭代：本地DNS → 各级DNS（"我不知道，你去问他"）
```

#### 4.2 DNS 记录类型

| 记录类型 | 含义 | 示例 |
|----------|------|------|
| A | 域名 → IPv4 地址 | www.example.com → 93.184.216.34 |
| AAAA | 域名 → IPv6 地址 | www.example.com → 2001:db8::1 |
| CNAME | 域名别名 → 另一个域名 | cdn.example.com → d123.cloudfront.net |
| MX | 邮件服务器 | example.com → mail.example.com |
| NS | 域名的权威 DNS 服务器 | example.com → ns1.example.com |
| TXT | 文本信息（SPF、验证等） | "v=spf1 include:..." |

### 实践任务

```bash
# nslookup 基础查询
nslookup www.baidu.com

# dig 详细查询（推荐）
dig www.baidu.com           # A 记录
dig www.baidu.com CNAME     # CNAME 记录
dig +trace www.baidu.com    # 追踪完整解析过程

# Python DNS 查询
python3 -c "
import socket
result = socket.getaddrinfo('www.baidu.com', 80)
for r in result:
    print(f'  {r[0].name}: {r[4]}')
"
```

### 达成标准

- [ ] 能画出 DNS 解析的完整流程（递归 + 迭代）
- [ ] 能说出 A、CNAME、MX、NS 记录的区别
- [ ] 能用 dig 或 nslookup 实际查询并解读结果
