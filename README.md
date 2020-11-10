# 网络编程
## Socket 介绍
Socket套接字<br>
Python中提供socket.py标准库，非常底层的接口库。<br>
Socket是一种通用的网络编程接口，和网络层次没有一一对应的关系。

协议族<br>
AF表示Address Family，用于socket()第一个参数。

| 名称 | 含义 |
| :---: | :---: |
| AF_INET | IPv4 |
| AF_INET6 | IPv6 |
| AF_UNIX | Unix Domain Socket, Windows没有 |

Socket 类型

| 名称 | 含义 |
| :---: | :---: |
| SOCK_STREAM | 面向链接的流套接字。默认值，TCP协议 |
| SOCK_DGRAM | 无连接的数据报文套接字。UDP协议 |

### TCP编程(CS编程)
Socket编程，需要两端，一般来说需要一个服务器，一个客户端称为Server,客户端称为Client

#### TCP服务端
服务端编程步骤
- 创建Socket对象
- 绑定IP地址Address和端口Port,bind()方法
- IPv4地址为一个二元组(IP地址字符串, port)
- 开始监听，将在指定的IP的端口上监听。listen()方法
- 获取用于传送数据的Socket对象<br>
    socked.accept() -> (socket object, address info)<br>
    accept方法阻塞等待客户建立连接，返回一个新的Socket对象和客户端地址的二元组地址是远程客户端的地址，IPv4中它是一个二元组(clientaddr, port)
    - 接收数据<br>
        recv(bufsize[,flags])使用缓冲区接收数据
    - 发送数据
        send(bytes)发送数据

```python
import socket


ipaddr = ("127.0.0.1", 9999)
with socket.socket() as server:
    server.bind(ipaddr)
    server.listen()
    sl, ip = server.accept()
    data = sl.recv(1024)
    sl.send(data)
```

简单实现双向聊天

```python
import socket

ipaddr = ("127.0.0.1", 9999)
with socket.socket() as server:
    server.bind(ipaddr)
    server.listen()
    s, raddr = server.accept()     # 等待对方连接
    with s as se:
        while True:
            try:
                data = s.recv(1024)            # 获取数据 等待数据
                print('已接收到对方数据，信息如下')
                print(data.decode(encoding='gbk'))
                if data.decode('gbk') == 'exit':
                    break
                data = input('回应对方数据:')
                for i in range(2):
                    s.send(bytes(data, encoding='gbk'))                   # 回应数据
            except ConnectionResetError:
                print('对方已断开连接')
                break
```

##### 问题
两次绑定同一个端口会怎么样
```python
import socket


with socket.socket as server:
    server.bind(('127.0.0.1', 9999))
    server.listen()
    s1, info = server.accept()
    with s1:
        data = s1.recv(1024)
        print(data, info)
        s1.send(b'okay1')
    s2, info = server.accept()
    with s2:
        data = s2.recv(1024)
        print(data, info)
        s2.send(b'okay2')
```
上列accept和recv是阻塞的，逐渐从经常被阻塞住而不能工作怎么办

### 练习
写一个群聊程序

需求分析<br>
聊天根据是CS程序，C是每一个客户端，S是服务器端。<br>
服务器应该具有的功能:
- 启动服务，包括绑定地址和端口，监听
- 建立连接，能和多个客户端建立连接
- 接收不同用户的信息
- 分发，将接收的某个用户的信息转发到已连接的所有客户端
- 停止服务
- 记录连接的客户端

服务器对应一个类

```python
import socket
import threading
import logging
import datetime

FORMAT = "%(asctime)s %(threadName)s %(thread)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


# TCP Server
class GlobalChatServer:
    def __init__(self, ip: str = '127.0.0.1', port: int = 9999):
        self.addr = (ip, port)
        self.sock = socket.socket()
        self.clients = {}
        self.event = threading.Event()

    def start(self):
        self.sock.bind(self.addr)
        self.sock.listen()  # 服务启动
        threading.Thread(target=self.accept(), name="accept").start()

    def accept(self):
        while not self.event.is_set():
            s, raddr = self.sock.accept()  # 阻塞
            self.clients[raddr] = s
            logging.info(s)
            logging.info(raddr)
            threading.Thread(target=self.recv, name="recv", args=(s,)).start()

    def recv(self, sock):
        while not self.event.is_set():
            try:
                data = sock.recv(1024)    # 阻塞
            except Exception as e:
                logging.info(e)
                data = b'quit'
            if data == b'quit':
                self.clients.pop(sock.getpeername())
                break
            logging.info(data)
            msg = 'ack{} {} {}'.format(
                sock.getpeername(),
                datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S"),
                data.decode()).encode('gbk')
            for s in self.clients.values():
                s.send(msg)

    def stop(self):
        for i in self.clients.values():
            i.close()
        self.sock.close()
        self.event.set()


cs = GlobalChatServer()
cs.start()


while True:
    cmd = input(">>>")
    if cmd.strip() == 'exit':
        cs.stop()
        threading.Event.wait(3)
    logging.info(threading.enumerate())

```

## 其他方法

| 名称 | 含义 |
| :--- | :--- |
| socket.recv(bufsize[, flags]) | 获取数据，默认是阻塞的方式 |
| socket.recvfrom(bufsize[, flags]) | 获取数据，返回一个二元组(bytes, address) |
| socket.recv_into(buffer)[, nbytes[, flags]] | 获取到nbytes的数据后，存储到buffer中。如果nbytes没有指定或0，将buffer大小的数据存入buffer中。返回接收的字节数。 |
| socket.recvfrom_into(buffer[, nbytes[, flags]]) | 获取数据，返回一个二元组(bytes, address)到buffer中 |
| socket.send(bytes[, flags]) | TCP发送数据 |
| socket.sendall(bytes[, flags]) | TCP发送全部数据，成功返回None |
| socket.sendfile(file, offset=0, count=None) | 发送一个文件直到EOF，使用高性能os.sendfile机制，返回发送的字节数。如果win下不支持sendfile，或者不是普通文件，使用send()发送文件。offset告诉起始位置。3.5版本开始 |

- send：
    - 几个字节一个字节的从IO上读取，再一个字节一个字节发回去
    - IO上读取之后到内核空间，从内核空间到用户空间，再从用户空间再发到内核空间，再从内核空间发送出去
- sendfile:
    - 使用0拷贝机制
    - 在内核空间内读取一次，然后其他打上标记，最后一次性将文件发送出去。

```python
socket.makefile(mode='r', buffering=None, *, encofing=None,  errors=None, newline=None)
```
创建一个与该套接字相关联的文件对象，将recv方法看作读方法，将send方法看作写方法

```python
# 使用makefile
import socket

sockserver = socket.socket()
ip = '127.0.0.1'
port = 9999
addr = (ip, port)
sockserver.bind(addr)
sockserver.listen()
print('-'*30)
s, _ = sockserver.accept()
print('-'*30)
f = s.makefile(mode='rw') # 读发文件

line = f.read(10) # 阻塞等
print('-'*30)
print(line)
f.write('Return your msg:{}'.format(line))
f.flush()
```
上列不能循环消息

```python
import socket
import threading


sockserver = socket.socket()
ip = '127.0.0.1'
port = 9999
addr = (ip, port)
sockserver.bind(addr)
sockserver.listen()
print('-'*30)

event = threading.Event()

def accept(sock: socket.socket, e: threading.Event):
    s, _ =  sock.accept()
    f = s.makefile(mode='rw')
    
    while True:
        line = f.readline()
        print(line)
        if line.strip() == 'quit':  # 注意要发quit\n
            break
        f.write('Return your msg: {}'.format(line))
        f.flush()
    f.close()
    sock.close()
    e.wait(3)

t = threading.Thread(target=accept, args=(sockserver,  event))
t.start()
t.join()
print(sockserver)
```

| 名称 | 含义 |
| :--- | :--- |
| socket.getpeername() | 返回连接套字节的远程地址，返回值通常是元组(ipaddr, port) |
| socket.getsockname() | 返回套接字自己的地址。通常是一个元组(ipaddr, port) |
| socket.setblocking(flag) | 如果flag为0，则将套接字设置为非阻塞模式，否则将套接字设置为阻塞模式(默认值)<br>非阻塞模式下，如果调用recv()没有发现任何数据或send()调用无法立即发送数据，那么将引起socket.error异常 |
| socket.settimeout(value) | 设置套接字的超时期，timeout是一个浮点数，单位是秒。值None表示没有超时期。一般，超时应该在刚创建套接字时设置，因为它们可能用与连接的操作(如connect()) |
| socket.setsockopt(level, optname, value) | 设置套接字选项的值。比如缓冲区大小。更多详细观看相关文档，不同系统，不同版本都不尽相同。 |

### 练习

使用makefile编写群聊

```python
import socket
import threading
import logging
import datetime

FORMAT = "%(asctime)s %(threadName)s %(thread)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


# TCP Server
class GlobalChatServer:
    def __init__(self, ip: str = '127.0.0.1', port: int = 9999):
        self.addr = (ip, port)
        self.sock = socket.socket()
        self.clients = {}
        self.event = threading.Event()

    def start(self):
        self.sock.bind(self.addr)
        self.sock.listen()  # 服务启动
        threading.Thread(target=self.accept(), name="accept").start()

    def accept(self):
        while not self.event.is_set():
            s, raddr = self.sock.accept()  # 阻塞
            f = s.makefile(mode='rw')
            self.clients[raddr] = f
            logging.info(f)
            logging.info(s)
            logging.info(raddr)
            threading.Thread(target=self.recv, name="recv", args=(f, raddr)).start()

    def recv(self, f, raddr):
        while not self.event.is_set():
            try:
                # data = f.recv(1024)    # 阻塞
                data = f.readline()     # string, 会等待换行符\n
                logging.info(data)
            except Exception as e:
                logging.error(e)
                data = b'quit'
            if data == b'quit':
                self.clients.pop(raddr)
                break
            msg = 'ack{} {} {}'.format(
                raddr,
                datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S"),
                data)
            for s in self.clients.values():
                f.write(msg)
                f.flush()

    def stop(self):
        for i in self.clients.values():
            i.close()
        self.sock.close()
        self.event.set()


# cmd = input(">>>")
cs = GlobalChatServer()
cs.start()


while True:
    cmd = input(">>>")
    if cmd.strip() == 'exit':
        cs.stop()
        threading.Event.wait(3)
    logging.info(threading.enumerate())
```
上列完了了基本功能，但是如果客户主动断开或者readline出现异常，就不会从clients中移除作废socket，可以使用异常处理解决这个问题

## GlobalChatServer

注意，这个代码为实验用，代码中的瑕疵还有很多，Socket太底层了，实际开发中很少用这么底层的接口。<br>
新增加一些异常处理
# SocketGlobalChatServer
