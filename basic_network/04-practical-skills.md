# 阶段 3：动手验证——看到的才是你的

## 为什么需要这个阶段？

前两个阶段你已经建立了理论框架。但理论和实践之间有一条鸿沟：

> 你可以背出三次握手的过程，但是如果面试官给你一段 Wireshark 截图让你分析，你能看懂吗？
> 你知道 HTTP 请求报文的格式，但你能用 socket 从零写一个 HTTP 服务器吗？

这个阶段的目标就是**跨越这条鸿沟**。我设计了从简到难的 5 个递进级别：

```
Level 1: 会看（用工具观察网络现象）
Level 2: 会用（熟练使用 curl / Wireshark / tcpdump 调试）
Level 3: 会写（用 socket 编程实现网络通信）
Level 4: 会排查（遇到问题知道怎么定位）
Level 5: 会解释（能把排查过程讲给面试官听）
```

我们按级别递进。

---

# Level 1：学会"看"—— Wireshark 入门

## 为什么先学 Wireshark？

因为它能让你**亲眼看到**阶段 2 学的所有理论：
- 三次握手不再是图上的箭头，而是你能点开的真实数据包
- HTTP 请求不再是书上的文本，而是你能逐字段检查的结构体

**安装**：https://www.wireshark.org/download.html（免费，Windows/Mac/Linux 都有）

## 你的第一次抓包

**目标**：抓到一个完整的 HTTP 请求过程，看到三次握手 → HTTP 请求 → HTTP 响应 → 四次挥手。

```
步骤：
  1. 打开 Wireshark
  2. 选择你正在用的网卡（Wi-Fi 或 Ethernet），双击开始捕获
  3. 在浏览器中访问 http://httpbin.org/get （注意是 http 不是 https）
  4. 回到 Wireshark，点击红色方块停止捕获
  5. 在过滤栏输入：tcp.port == 80
```

**你应该看到的东西**：

```
No.  Time      Source          Destination     Protocol  Info
───────────────────────────────────────────────────────────────
1    0.000     你的IP          httpbin的IP     TCP       SYN         ← 握手第1步
2    0.045     httpbin的IP     你的IP          TCP       SYN, ACK    ← 握手第2步
3    0.046     你的IP          httpbin的IP     TCP       ACK         ← 握手第3步
4    0.047     你的IP          httpbin的IP     HTTP      GET /get    ← HTTP 请求
5    0.120     httpbin的IP     你的IP          HTTP      200 OK      ← HTTP 响应
6    ...       ...             ...             TCP       FIN, ACK    ← 挥手开始
```

**点开第 1 个包（SYN）**，你能看到每一层的详细信息：

```
▸ Frame（物理帧信息）
▸ Ethernet II（数据链路层：源MAC → 目的MAC）
▸ Internet Protocol（网络层：源IP → 目的IP）
▸ Transmission Control Protocol（传输层）
    Source Port: 54321        ← 你的电脑随机分配的端口
    Destination Port: 80     ← HTTP 端口
    Sequence Number: 0       ← 初始序列号（Wireshark 显示为相对值 0）
    Flags: 0x002 (SYN)       ← 这就是 SYN 标志
    Window: 65535            ← 窗口大小
```

看到这里，你在阶段 2 学的"SYN 包、序列号、窗口大小"就全部有了真实的对应。

### 🔧 练习 1：填写握手记录表

抓到三次握手后，填写这个表格来加深理解：

| 步骤 | 方向 | Flags | Seq | Ack | 含义 |
|------|------|-------|-----|-----|------|
| 第1步 | 客户端→服务端 | ? | ? | ? | ? |
| 第2步 | 服务端→客户端 | ? | ? | ? | ? |
| 第3步 | 客户端→服务端 | ? | ? | ? | ? |

## Wireshark 过滤器速查

过滤器是你在大量流量中找到目标的关键。按使用频率排序：

```
====== 你每天都会用的 ======

ip.addr == 192.168.1.100           按 IP 过滤（源或目的）
tcp.port == 80                     按端口过滤
http                               只看 HTTP
dns                                只看 DNS

====== 排查问题时用的 ======

tcp.flags.syn == 1 && tcp.flags.ack == 0    纯 SYN 包（握手第一步）
tcp.flags.reset == 1                        RST 包（连接异常重置）
tcp.flags.fin == 1                          FIN 包（断开连接）

tcp.analysis.retransmission         重传（丢包了！）
tcp.analysis.duplicate_ack          重复 ACK（有包丢了，接收方在催）
tcp.analysis.zero_window            零窗口（接收方处理不过来了）

====== 组合过滤 ======

ip.addr == 10.0.0.1 && tcp.port == 8080
http.request.method == "POST"
http.response.code == 500
```

### 🔧 练习 2：用过滤器找到异常

```
任务：访问一个不存在的页面（比如 http://httpbin.org/nonexistent），
用 Wireshark 过滤出 HTTP 响应，确认状态码是 404。

过滤器：http.response.code == 404
```

---

# Level 2：熟练使用调试工具

## curl：命令行里的万能 HTTP 客户端

curl 是测试开发**最常用**的调试工具，你需要把它用到"肌肉记忆"级别。

### 从简单到复杂的 curl 使用路径

**第 1 步：最基础——发请求看响应**

```bash
curl https://httpbin.org/get
# 输出 JSON 响应体。最简单的 GET 请求。
```

**第 2 步：调试模式——看完整过程（-v 是最重要的参数）**

```bash
curl -v https://httpbin.org/get

# * Trying 3.230.204.70:443...        ← 正在连接
# * Connected                         ← TCP 连接成功
# * TLS handshake                     ← TLS 握手（因为是 HTTPS）
# > GET /get HTTP/2                   ← 你发出的请求（> 开头）
# > Host: httpbin.org
# < HTTP/2 200                        ← 收到的响应（< 开头）
# < content-type: application/json
# { "args": {}, ... }                 ← 响应体
```

**第 3 步：POST 请求——接口测试必备**

```bash
# 发 JSON（最常用）
curl -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"name":"Alan","role":"SDET"}'

# 发表单
curl -X POST https://httpbin.org/post \
  -d "username=admin&password=123"

# 上传文件
curl -X POST https://httpbin.org/post \
  -F "file=@test.png"
```

**第 4 步：性能诊断——接口慢了用这个**

```bash
curl -o /dev/null -s -w "\
  DNS 解析:     %{time_namelookup}s\n\
  TCP 连接:     %{time_connect}s\n\
  TLS 握手:     %{time_appconnect}s\n\
  首字节时间:   %{time_starttransfer}s\n\
  总耗时:       %{time_total}s\n" \
  https://httpbin.org/get

# 输出示例：
#   DNS 解析:     0.015s     ← 如果很慢，DNS 有问题
#   TCP 连接:     0.048s     ← 如果很慢，网络延迟大
#   TLS 握手:     0.120s     ← HTTPS 特有，正常
#   首字节时间:   0.180s     ← 服务端处理时间
#   总耗时:       0.185s     ← 端到端总时间

#这些参数在网络基础中代表什么？
#当你运行这个命令后，你会得到一组时间数据，它们精确对应了 TCP/IP 的不同阶段：

#DNS 解析 (time_namelookup)：
#把 httpbin.org 变成 IP 地址的时间。如果这个时间很长，说明你的 DNS 服务器（如 114.114.114.114）慢。

#TCP 连接 (time_connect)：
#这包含了 三次握手 的耗时。它反映了你和服务器之间的网络延迟（RTT）。

#TLS 握手 (time_appconnect)：
#HTTPS 加密层建立的时间。如果这个值比 TCP 连接大很多，说明加密协议协商比较耗时。

#首字节时间 (time_starttransfer)：
#从发请求到服务器吐出第一个字节的时间。这通常反映了服务器的处理能力（TTFB）。

#总耗时 (time_total)：
#整个流程走完的总时间。

```

**这个命令在实际工作中非常有用**——当有人说"接口慢了"，你跑一下就能定位是 DNS 慢、网络慢、还是服务端处理慢。

### 🔧 练习 3：curl 调试任务

```
任务 1：用 curl -v 访问 https://www.baidu.com，对照阶段 1 学的"URL到页面"流程，
        在输出中找到 DNS 解析、TCP 连接、TLS 握手、HTTP 请求/响应的每个阶段。

任务 2：用 curl 的性能诊断命令测试 3 个不同网站的响应速度，
        对比它们在 DNS、连接、服务端处理上的差异。

任务 3：用 curl 发送一个 POST 请求到 https://httpbin.org/post，
        包含 JSON 数据和 Authorization 头，确认请求是否正确发送。
```

## tcpdump：服务器上的抓包工具

Wireshark 是图形界面的，但你 SSH 到一台 Linux 服务器时没有图形界面。这时候用 tcpdump。

```bash
# 最基本用法：监听指定端口
sudo tcpdump -i any port 8080 -nn

# -i any    = 所有网卡
# -nn       = 不解析域名和端口名（显示数字，更快更清晰）

# 监听并保存为文件（之后用 Wireshark 打开分析）
sudo tcpdump -i any port 8080 -nn -w /tmp/capture.pcap -c 100
# -w = 写入文件    -c 100 = 只抓 100 个包

# 查看 HTTP 请求内容
sudo tcpdump -i any port 80 -A | grep -E 'GET|POST|HTTP'
# -A = 以 ASCII 显示包内容

# 抓特定 IP 的流量
sudo tcpdump -i any host 10.0.0.50 and port 3306 -nn
```

### 🔧 练习 4：tcpdump + Wireshark 联动

```
1. 在终端 A 启动 tcpdump 抓包：
   sudo tcpdump -i any port 80 -nn -w /tmp/test.pcap -c 50

2. 在终端 B 发起请求：
   curl http://httpbin.org/get

3. 终端 A 的 tcpdump 会自动停止（抓够 50 个包）
4. 把 /tmp/test.pcap 用 Wireshark 打开分析
```

---

# Level 3：用 Socket 编程理解协议本质

## 为什么要自己写 Socket？

因为 requests 库、Flask 框架都是 Socket 的"封装"。当你自己用 Socket 写过服务器后，你会理解：
- `sock.listen(5)` 的 5 是什么意思
- 为什么服务端代码需要 `accept()`
- 为什么需要 `setsockopt(SO_REUSEADDR, 1)`
- `recv(1024)` 的 1024 意味着什么

### 渐进式 Socket 编程路线

**项目 1（入门）：回显服务器——收什么就回什么**

```python
"""
echo_server.py
目标：理解 socket 编程的基本流程
      bind → listen → accept → recv → send → close
"""
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 为什么需要这一行？
# 因为服务器关闭后端口进入 TIME_WAIT，短时间内无法重新绑定
# 这行让端口可以被立即复用
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(('0.0.0.0', 8888))   # 绑定地址和端口
server.listen(5)                  # 开始监听，5 = 等待队列最大长度
print("服务器启动，监听 0.0.0.0:8888")

while True:
    # accept() 会阻塞，直到有客户端连接
    conn, addr = server.accept()
    print(f"新连接: {addr}")
    
    data = conn.recv(1024)        # 最多读 1024 字节
    if data:
        print(f"收到: {data.decode()}")
        conn.send(data)            # 回显：原样发回去
    
    conn.close()
```

```python
"""
echo_client.py
"""
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8888))

message = "Hello, Socket!"
client.send(message.encode())

response = client.recv(1024)
print(f"服务器回复: {response.decode()}")

client.close()
```

**验证**：先运行 server，再运行 client。如果看到消息被回显，恭喜你完成了第一个 Socket 程序！

**同时用 Wireshark 抓包**，过滤 `tcp.port == 8888`，你能看到完整的握手→数据传输→挥手。

---

**项目 2（进阶）：多人聊天室——支持多客户端**

项目 1 的问题是一次只能服务一个客户端。真实的服务器需要同时处理多个连接。

```python
"""
chat_server.py
目标：理解多线程处理并发连接
关键知识点：为什么需要线程？因为 accept() 和 recv() 都会阻塞
"""
import socket
import threading

clients = []  # 保存所有已连接的客户端

def handle_client(conn, addr):
    """每个客户端一个线程"""
    print(f"[+] {addr} 加入聊天室")
    clients.append(conn)
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            msg = f"[{addr[1]}] {data.decode()}"
            print(msg)
            
            # 广播给所有其他客户端
            for c in clients:
                if c != conn:
                    try:
                        c.send(msg.encode())
                    except:
                        clients.remove(c)
    except ConnectionResetError:
        pass
    finally:
        clients.remove(conn)
        conn.close()
        print(f"[-] {addr} 离开聊天室")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 8888))
server.listen(5)
print("[*] 聊天室启动: 0.0.0.0:8888")

while True:
    conn, addr = server.accept()
    t = threading.Thread(target=handle_client, args=(conn, addr))
    t.daemon = True
    t.start()
```

**验证**：打开 3 个终端，一个运行 server，另外 2 个用 `nc 127.0.0.1 8888`（或运行 client 脚本）连接。在一个客户端输入消息，另一个客户端应该能收到。

---

**项目 3（挑战）：手写 HTTP 服务器**

这是理解 HTTP 协议本质最好的方式——**HTTP 就是 TCP 上面的一层文本格式约定**。

```python
"""
mini_http_server.py
目标：理解 HTTP 协议就是 TCP 上面的文本协议
你可以用 curl http://localhost:8000/ 来测试
"""
import socket
import json
from datetime import datetime

def parse_request(raw: str) -> dict:
    """解析 HTTP 请求文本 → 结构化数据"""
    lines = raw.split('\r\n')
    method, path, version = lines[0].split(' ')
    
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
        elif line == '':
            break
    
    return {'method': method, 'path': path, 'headers': headers}

def build_response(status: str, body: str) -> str:
    """构造 HTTP 响应文本"""
    return (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{body}"
    )

def handle_request(request: dict) -> str:
    """路由 + 处理逻辑"""
    path = request['path']
    method = request['method']
    
    if path == '/' and method == 'GET':
        body = json.dumps({"message": "Hello from mini HTTP!", "time": str(datetime.now())})
        return build_response("200 OK", body)
    
    elif path == '/health' and method == 'GET':
        body = json.dumps({"status": "healthy"})
        return build_response("200 OK", body)
    
    elif path == '/echo' and method == 'POST':
        body = json.dumps({"echo": "received", "headers": request['headers']})
        return build_response("200 OK", body)
    
    else:
        body = json.dumps({"error": "Not Found", "path": path})
        return build_response("404 Not Found", body)

# 启动服务器
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 8000))
server.listen(5)
print("[*] Mini HTTP Server: http://localhost:8000")

while True:
    conn, addr = server.accept()
    raw = conn.recv(4096).decode()
    if raw:
        request = parse_request(raw)
        print(f"[{addr}] {request['method']} {request['path']}")
        response = handle_request(request)
        conn.sendall(response.encode())
    conn.close()
```

**验证**：

```bash
# 测试各种路由
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/nonexistent    # 应该返回 404
curl -X POST http://localhost:8000/echo   # POST 请求

# 用 -v 看完整的请求/响应过程
curl -v http://localhost:8000/
# 你会发现：你自己构造的 HTTP 响应，curl 完全能正确解析！
```

**这个项目的意义**：当你亲手解析过 `GET / HTTP/1.1\r\nHost: ...` 这样的原始文本，你就彻底理解了"HTTP 就是一个文本协议"。requests 库、Flask、Django 做的事情，本质上就是帮你处理这些文本格式。

---

# Level 4：问题排查 SOP

## 测试开发常见网络问题排查手册

实际工作中你会遇到各种网络问题。这里给你一个排查清单，每个问题都有"先做什么、再做什么"的标准流程：

### 问题 1：接口完全不通（Connection Refused / Timeout）

```
排查路线：从底层到上层

① 网络层：能 ping 通吗？
   ping target_ip
   → ping 不通 → 网络不通 / 防火墙 / IP 错误

② 传输层：端口开着吗？
   telnet target_ip 8080
   或 nc -zv target_ip 8080
   → 连不上 → 服务没启动 / 端口错误 / 防火墙拦截端口

③ 应用层：服务正常吗？
   curl -v http://target_ip:8080/health
   → 能连但返回错误 → 应用层问题，看错误码和日志
```

### 问题 2：接口返回 502 Bad Gateway

```
502 = 网关（通常是 Nginx）收到了上游的无效响应

排查路线：
  ① Nginx 本身正常吗？
     systemctl status nginx    → 看 Nginx 是否在运行

  ② 直接访问上游服务：
     curl http://upstream_ip:port/health
     → 如果也失败 → 上游服务挂了（看服务日志、是否 OOM）
     → 如果正常 → Nginx 配置问题

  ③ 看 Nginx 错误日志：
     tail -f /var/log/nginx/error.log
     "connect() failed" → 上游没启动 / 端口不对
     "upstream timed out" → 上游太慢（可能是 504 而非 502）
```

### 问题 3：接口偶发超时

```
"偶发"是最难排查的，因为问题不稳定复现。

排查思路：
  ① 用 curl -w 多次测试，统计各阶段耗时
     → DNS 时间不稳定？ → DNS 服务器问题，/etc/hosts 绑定 IP
     → 连接时间不稳定？ → 网络抖动，检查路由
     → 服务端处理时间不稳定？ → 看慢查询日志、是否有定时任务干扰

  ② 长时间 tcpdump 抓包
     → 看有没有重传（tcp.analysis.retransmission）
     → 看有没有 RST（连接被异常断开）

  ③ 检查连接数
     → ss -tan | wc -l  → 连接数是否接近上限？
     → TIME_WAIT 是否大量堆积？
```

### 排查工具总结

| 我想排查... | 用什么工具 | 具体命令 |
|-------------|-----------|---------|
| 网络是否通 | ping | `ping target_ip` |
| 端口是否开 | telnet / nc | `nc -zv ip port` |
| DNS 是否正常 | dig / nslookup | `dig domain.com` |
| 路由是否通 | traceroute | `traceroute target_ip` |
| 哪些端口在监听 | ss / netstat | `ss -tlnp` |
| HTTP 接口详情 | curl | `curl -v url` |
| 接口性能分解 | curl | `curl -w "..." url` |
| 抓包分析 | tcpdump + Wireshark | `tcpdump -i any port 8080 -w out.pcap` |
| 哪个进程占端口 | lsof | `lsof -i :8080` |
| TCP 连接状态 | ss | `ss -tan \| grep TIME-WAIT` |

---

## 阶段 3 达成标准

### Level 1-2 验证

- [ ] 能用 Wireshark 抓取 HTTP 流量并定位三次握手的三个包
- [ ] 能用 Wireshark 过滤器找到重传和 RST 包
- [ ] 能用 curl -v 查看完整的 HTTP 请求/响应过程
- [ ] 能用 curl -w 分析接口的各阶段耗时
- [ ] 能用 tcpdump 抓包并保存为 .pcap 文件

### Level 3 验证

- [ ] 完成了回显服务器（项目 1）并成功通信
- [ ] 完成了多人聊天室（项目 2）并支持多客户端
- [ ] 完成了手写 HTTP 服务器（项目 3）并通过 curl 测试

### Level 4 验证

- [ ] 能说出"接口 502"的排查流程
- [ ] 能说出"接口偶发超时"的排查思路
- [ ] 知道至少 8 个排查工具及其用途
