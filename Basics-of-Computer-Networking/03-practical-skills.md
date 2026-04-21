# 阶段 3：实践能力（1–2 周）

> 理论不落地就是空中楼阁。本阶段目标：用工具验证每一个理论知识点，
> 建立"看到网络现象 → 解释原因 → 提出方案"的完整排查能力。

---

## 一、Wireshark 学习路线

### 学习目标

- [ ] 能用 Wireshark 抓取并过滤指定流量
- [ ] 能识别三次握手、四次挥手的每个报文
- [ ] 能分析 HTTP 请求/响应的完整内容
- [ ] 能从抓包中发现常见问题（重传、RST、超时）

### 1.1 基础操作

```
安装：https://www.wireshark.org/download.html

启动流程：
  ① 选择网卡（Wi-Fi 或 Ethernet）
  ② 开始捕获
  ③ 在浏览器中操作（触发流量）
  ④ 停止捕获
  ⑤ 用过滤器筛选目标流量
```

### 1.2 常用过滤器（必记）

```
# === 基础过滤 ===
ip.addr == 192.168.1.100           # 源或目的IP
ip.src == 192.168.1.100            # 源IP
ip.dst == 93.184.216.34            # 目的IP
tcp.port == 80                     # TCP 端口（源或目的）
tcp.dstport == 443                 # 目的端口
udp.port == 53                     # UDP 端口

# === 协议过滤 ===
http                               # 所有 HTTP 流量
dns                                # 所有 DNS 查询
tcp                                # 所有 TCP 流量
tls                                # 所有 TLS 流量

# === TCP 标志位过滤 ===
tcp.flags.syn == 1                 # SYN 包
tcp.flags.syn == 1 && tcp.flags.ack == 0   # 纯 SYN（握手第一步）
tcp.flags.fin == 1                 # FIN 包
tcp.flags.reset == 1               # RST 包（异常断开）

# === HTTP 过滤 ===
http.request                       # HTTP 请求
http.response                      # HTTP 响应
http.request.method == "POST"      # POST 请求
http.response.code == 404          # 404 响应
http.host == "api.example.com"     # 指定 Host

# === 组合过滤 ===
ip.addr == 93.184.216.34 && tcp.port == 80
tcp.flags.reset == 1 && ip.addr == 10.0.0.1
http && ip.addr == 192.168.1.100

# === 高级过滤 ===
tcp.analysis.retransmission        # TCP 重传
tcp.analysis.duplicate_ack         # 重复 ACK
tcp.analysis.zero_window           # 零窗口（流量控制触发）
tcp.analysis.window_full           # 窗口满
tcp.time_delta > 1                 # 延迟超过 1 秒
```

### 1.3 抓包分析实践

#### 实践 1：分析三次握手

```
步骤：
  1. Wireshark 开始捕获
  2. 浏览器访问 http://httpbin.org
  3. 停止捕获
  4. 过滤：tcp.port == 80 && tcp.flags.syn == 1

找到三个包并记录：
  包1 (SYN):
    - 源端口: _____  目的端口: 80
    - Seq: _____     Ack: 0
    - Flags: SYN
    - Window: _____

  包2 (SYN+ACK):
    - 源端口: 80     目的端口: _____
    - Seq: _____     Ack: _____  (应为包1的Seq+1)
    - Flags: SYN, ACK

  包3 (ACK):
    - Seq: _____     Ack: _____  (应为包2的Seq+1)
    - Flags: ACK
```

#### 实践 2：分析 HTTP 请求/响应

```
步骤：
  1. 过滤：http && ip.addr == [httpbin的IP]
  2. 找到 GET /get 请求
  3. 右键 → Follow → HTTP Stream
  4. 查看完整的请求报文和响应报文

记录：
  请求方法: _____
  请求路径: _____
  Host 头:  _____
  User-Agent: _____
  响应状态码: _____
  Content-Type: _____
  响应体内容: _____
```

#### 实践 3：分析 DNS 查询

```
步骤：
  1. 过滤：dns
  2. 清空浏览器 DNS 缓存（chrome://net-internals/#dns）
  3. 访问一个新网站
  4. 找到 DNS 查询和响应

记录：
  查询类型: A / AAAA
  查询域名: _____
  响应IP:   _____
  查询耗时: _____
```

#### 实践 4：发现异常流量

```
# 查找 TCP 重传
过滤：tcp.analysis.retransmission
思考：为什么会重传？网络丢包？服务端过慢？

# 查找 RST（连接被重置）
过滤：tcp.flags.reset == 1
思考：谁发的 RST？为什么？端口未监听？防火墙？

# 查找零窗口
过滤：tcp.analysis.zero_window
思考：接收方缓冲区满了，为什么？应用处理太慢？
```

### 达成标准

- [ ] 能独立抓取并过滤指定 IP/端口的流量
- [ ] 能在抓包中定位三次握手和四次挥手
- [ ] 能用 Follow Stream 查看完整 HTTP 会话
- [ ] 能识别重传、RST、零窗口等异常情况

---

## 二、tcpdump 学习路线

### 学习目标

- [ ] 能在 Linux 服务器上用 tcpdump 抓包
- [ ] 能过滤特定协议/端口/IP 的流量
- [ ] 能将抓包保存为 .pcap 文件供 Wireshark 分析

### 2.1 基础命令

```bash
# 监听指定网卡
sudo tcpdump -i eth0

# 监听指定端口
sudo tcpdump -i any port 80

# 监听指定 IP
sudo tcpdump -i any host 192.168.1.100

# 监听指定协议
sudo tcpdump -i any tcp
sudo tcpdump -i any udp
sudo tcpdump -i any icmp

# 组合过滤
sudo tcpdump -i any host 10.0.0.1 and port 8080
sudo tcpdump -i any '(port 80 or port 443)'
sudo tcpdump -i any src host 10.0.0.1 and dst port 3306

# 常用参数
-n          # 不解析域名（用IP显示，速度快）
-nn         # 不解析域名和端口名
-v / -vv    # 详细 / 更详细输出
-c 100      # 只抓 100 个包
-A          # 以 ASCII 显示包内容（看 HTTP 文本）
-X          # 以 Hex + ASCII 显示
-w file.pcap  # 保存到文件
-r file.pcap  # 读取文件
```

### 2.2 实践场景

```bash
# 场景 1：抓取三次握手
sudo tcpdump -i any -nn 'tcp[tcpflags] & (tcp-syn) != 0' and port 80 -c 10

# 场景 2：抓取 HTTP 请求内容
sudo tcpdump -i any -A port 80 | grep -E 'GET|POST|HTTP'

# 场景 3：抓取 DNS 查询
sudo tcpdump -i any -nn port 53

# 场景 4：保存抓包供后续分析
sudo tcpdump -i any -w /tmp/capture.pcap port 8080 -c 1000
# 然后用 Wireshark 打开 capture.pcap 分析

# 场景 5：抓取特定服务器的 MySQL 流量
sudo tcpdump -i any dst host 10.0.0.50 and port 3306 -nn

# 场景 6：排查服务端口是否有流量进来
sudo tcpdump -i any port 8080 -nn -c 20
# 然后在另一个终端 curl http://localhost:8080
```

### 达成标准

- [ ] 能在无 GUI 的 Linux 服务器上用 tcpdump 抓包
- [ ] 能用 BPF 过滤器精确过滤目标流量
- [ ] 能将抓包保存为 .pcap 文件并用 Wireshark 打开分析

---

## 三、curl 调试路线

### 学习目标

- [ ] 能用 curl 发送各种 HTTP 请求
- [ ] 能用 curl 调试接口问题（查看完整请求/响应过程）
- [ ] 掌握测试开发中最常用的 curl 用法

### 3.1 核心用法

```bash
# ====== 基础请求 ======
curl https://httpbin.org/get                        # GET
curl -X POST https://httpbin.org/post               # POST（空体）
curl -X PUT https://httpbin.org/put                 # PUT
curl -X DELETE https://httpbin.org/delete            # DELETE

# ====== POST 数据 ======
# JSON（测试开发最常用）
curl -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"name":"test","age":25}'

# 表单
curl -X POST https://httpbin.org/post \
  -d "username=admin&password=123456"

# 文件上传
curl -X POST https://httpbin.org/post \
  -F "file=@/path/to/test.png" \
  -F "name=avatar"

# ====== 请求头 ======
curl -H "Authorization: Bearer token123" \
     -H "Accept: application/json" \
     https://httpbin.org/headers

# ====== 调试选项（最重要） ======
curl -v https://httpbin.org/get          # -v 显示完整通信过程
curl -I https://httpbin.org/get          # -I 只看响应头
curl -o /dev/null -s -w "\
  HTTP Code: %{http_code}\n\
  DNS Time: %{time_namelookup}s\n\
  Connect Time: %{time_connect}s\n\
  TLS Time: %{time_appconnect}s\n\
  Total Time: %{time_total}s\n\
  Speed: %{speed_download} bytes/s\n" \
  https://httpbin.org/get                 # 性能诊断

# ====== Cookie 与 Session ======
curl -c cookies.txt https://httpbin.org/cookies/set/sid/abc123  # 保存Cookie
curl -b cookies.txt https://httpbin.org/cookies                 # 带Cookie请求

# ====== 其他常用 ======
curl -L https://httpbin.org/redirect/3         # 跟随重定向
curl --connect-timeout 5 --max-time 10 URL     # 设置超时
curl -k https://self-signed.example.com        # 忽略证书验证
curl -x http://proxy:8080 https://example.com  # 使用代理
```

### 3.2 curl -v 输出解读

```
$ curl -v https://httpbin.org/get

*   Trying 34.199.75.4:443...          ← DNS 解析后的 IP
* Connected to httpbin.org              ← TCP 连接成功
* ALPN: offers h2,http/1.1              ← 协商 HTTP 版本
* TLSv1.3 (OUT), TLS handshake         ← TLS 握手开始
* Server certificate: httpbin.org       ← 服务器证书
* SSL certificate verify ok            ← 证书验证通过

> GET /get HTTP/2                       ← 发送的请求（> 开头）
> Host: httpbin.org
> User-Agent: curl/8.1.2
> Accept: */*

< HTTP/2 200                            ← 收到的响应（< 开头）
< content-type: application/json
< content-length: 254

{                                       ← 响应体
  "headers": { ... }
}
```

### 达成标准

- [ ] 能用 curl 发送 GET / POST / PUT / DELETE 请求
- [ ] 能用 -v 查看完整的请求/响应过程
- [ ] 能用 -w 选项测量接口性能（DNS时间、连接时间、总耗时）
- [ ] 能在实际工作中用 curl 快速调试接口问题

---

## 四、Python Socket 编程路线

### 学习目标

- [ ] 能用 Python 编写 TCP 客户端和服务端
- [ ] 能用 Python 编写 UDP 客户端和服务端
- [ ] 能实现多客户端并发处理
- [ ] 能实现 TCP 粘包解决方案

### 4.1 TCP 完整示例

```python
"""
tcp_server.py - TCP 回显服务器（多线程版）
"""
import socket
import threading

def handle_client(conn, addr):
    """处理单个客户端"""
    print(f"[+] 新连接: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode('utf-8')
            print(f"[{addr}] 收到: {msg}")
            conn.send(f"Echo: {msg}".encode('utf-8'))
    except ConnectionResetError:
        print(f"[{addr}] 连接被重置")
    finally:
        conn.close()
        print(f"[-] 断开: {addr}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8888))
    server.listen(5)
    print("[*] TCP 服务器启动，监听 0.0.0.0:8888")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n[*] 服务器关闭")
    finally:
        server.close()

if __name__ == '__main__':
    main()
```

```python
"""
tcp_client.py - TCP 客户端
"""
import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))
    print("[*] 已连接到服务器，输入 quit 退出")

    try:
        while True:
            msg = input("发送> ")
            if msg.lower() == 'quit':
                break
            client.send(msg.encode('utf-8'))
            response = client.recv(1024)
            print(f"收到< {response.decode('utf-8')}")
    finally:
        client.close()

if __name__ == '__main__':
    main()
```

### 4.2 带长度前缀的协议实现（解决粘包）

```python
"""
protocol.py - 带长度前缀的消息协议
"""
import struct
import socket
import json

class MessageProtocol:
    """
    消息格式：[4字节长度][JSON消息体]
    """
    HEADER_SIZE = 4

    @staticmethod
    def send(sock: socket.socket, data: dict):
        """发送一条消息"""
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        header = struct.pack('>I', len(body))
        sock.sendall(header + body)

    @staticmethod
    def recv(sock: socket.socket) -> dict | None:
        """接收一条消息"""
        header = MessageProtocol._recv_exact(sock, MessageProtocol.HEADER_SIZE)
        if not header:
            return None
        body_len = struct.unpack('>I', header)[0]
        body = MessageProtocol._recv_exact(sock, body_len)
        if not body:
            return None
        return json.loads(body.decode('utf-8'))

    @staticmethod
    def _recv_exact(sock: socket.socket, n: int) -> bytes | None:
        """精确接收 n 个字节"""
        buf = b''
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf


# 使用示例
# 服务端：
#   msg = MessageProtocol.recv(conn)
#   print(msg)  # {'action': 'hello', 'name': 'test'}
#
# 客户端：
#   MessageProtocol.send(sock, {'action': 'hello', 'name': 'test'})
```

### 4.3 简易 HTTP 服务器

```python
"""
simple_http_server.py - 用 socket 手写 HTTP 服务器
理解 HTTP 协议的本质：它就是 TCP 上的文本协议
"""
import socket
import json
from datetime import datetime

def handle_request(request_text: str) -> str:
    """解析 HTTP 请求并生成响应"""
    lines = request_text.split('\r\n')
    method, path, version = lines[0].split(' ')

    # 路由处理
    if path == '/':
        body = json.dumps({
            "message": "Hello from hand-made HTTP server!",
            "time": datetime.now().isoformat(),
            "method": method
        })
        status = "200 OK"
    elif path == '/health':
        body = json.dumps({"status": "ok"})
        status = "200 OK"
    else:
        body = json.dumps({"error": "Not Found", "path": path})
        status = "404 Not Found"

    response = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{body}"
    )
    return response

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8000))
    server.listen(5)
    print("[*] HTTP 服务器启动: http://localhost:8000")

    while True:
        conn, addr = server.accept()
        try:
            request = conn.recv(4096).decode('utf-8')
            if request:
                print(f"[{addr}] {request.split(chr(13))[0]}")
                response = handle_request(request)
                conn.sendall(response.encode('utf-8'))
        finally:
            conn.close()

if __name__ == '__main__':
    main()

# 测试：
# curl http://localhost:8000/
# curl http://localhost:8000/health
# curl http://localhost:8000/nonexistent
```

### 4.4 异步 Socket（进阶了解）

```python
"""
async_server.py - asyncio 异步 TCP 服务器
面试中如果被问到"高并发怎么处理"可以提到 asyncio
"""
import asyncio

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f"[+] 连接: {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            msg = data.decode()
            print(f"[{addr}] {msg}")
            writer.write(f"Echo: {msg}".encode())
            await writer.drain()
    except ConnectionResetError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"[-] 断开: {addr}")

async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 8888)
    print("[*] Async TCP 服务器启动: 0.0.0.0:8888")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
```

### 实践任务清单

| 序号 | 任务 | 验收标准 |
|------|------|----------|
| 1 | 写 TCP 回显服务器 + 客户端 | 两端能正常收发消息 |
| 2 | 用多线程支持多个客户端同时连接 | 3 个客户端并发通信不互相阻塞 |
| 3 | 实现长度前缀协议 | 快速连发 100 条消息，每条都能正确接收 |
| 4 | 用 socket 手写 HTTP 服务器 | curl 能正常访问并收到 JSON 响应 |
| 5 | 用 Wireshark 抓自己写的服务器的流量 | 能看到握手、数据传输、挥手全过程 |
| 6 | 写 UDP 回显服务 | 对比 TCP 版本，体会无连接的区别 |

---

## 五、常见网络问题排查（测试开发实战）

### 排查工具速查表

| 问题类型 | 首选工具 | 命令/操作 |
|----------|----------|-----------|
| 网络不通 | ping | `ping target_ip` |
| DNS 问题 | dig / nslookup | `dig domain.com` |
| 端口不通 | telnet / nc | `telnet ip port` / `nc -zv ip port` |
| 路由问题 | traceroute | `traceroute target_ip` |
| 端口监听 | ss / netstat | `ss -tlnp` |
| 抓包分析 | tcpdump / Wireshark | `tcpdump -i any port 8080` |
| HTTP 调试 | curl | `curl -v url` |
| 进程端口 | lsof | `lsof -i :8080` |

### 常见问题排查 SOP

```
问题：接口返回超时

排查步骤：
  ① ping 目标服务器 → 网络通不通？延迟多大？
  ② telnet 目标 IP + 端口 → 端口能连上吗？
  ③ curl -v 接口地址 → 卡在哪一步？DNS？连接？等待响应？
  ④ 如果连接正常但响应慢 → 检查服务端日志、慢查询
  ⑤ 如果连接直接失败 → 检查防火墙、安全组、服务是否启动

问题：接口返回 502

排查步骤：
  ① 确认 Nginx/网关正常运行
  ② 检查上游服务是否存活：curl 直接访问上游地址
  ③ 查看 Nginx error log
  ④ 可能原因：上游服务挂了、端口改了、upstream 配置错误

问题：偶发性连接失败

排查步骤：
  ① 检查 TIME_WAIT 数量：ss -tan | grep TIME-WAIT | wc -l
  ② 检查文件描述符限制：ulimit -n
  ③ 检查连接池配置
  ④ 长时间 tcpdump 抓包，看 RST 出现的模式
```
