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
