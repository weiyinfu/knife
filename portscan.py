import signal
import socket
import sys
import threading
import time

"""
端口扫描工具：判断哪些端口是开放的
线程数动态增加，直到无法带来更多收益为止
每次线程数增加delta个，如果赚了delta加倍；如果赔了，delta减半
"""
socket.setdefaulttimeout(2)  # 设置默认超时时间
stop_flag = False  # 全局停止flag

open_ports = []


def sigint_handler(signum, frame):
    global stop_flag
    stop_flag = True
    print("\ncatch interrupt signal!")


signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)

init_thread_count = 10  # 初始线程数
total_count = 1 << 16  # 扫描的进程范围
a = [False] * total_count  # 端口是否检测过
now_pos = 0  # 当前已经处理了的端口个数
workers = []  # 全部worker集合
ip = "127.0.0.1"
if len(sys.argv) > 1:
    ip = sys.argv[1]
else:
    print("请输入ip地址，如果查看本地端口，请输入ipscan localhost")
    exit()


def check_port(ip, port):
    """
    输入IP和端口号，扫描判断端口是否占用
    """
    global now_pos
    now_pos = max(now_pos, port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((ip, port))
        if result == 0:
            print("{}:{} is open".format(ip, port))
            open_ports.append(port)
    except Exception as ex:
        print("\nscan port error", ex)


class ScanThread(threading.Thread):
    def __init__(self):
        super(ScanThread, self).__init__(target=self.ip_scan)
        self.stop = False

    def ip_scan(self):
        for i in range(len(a)):
            if stop_flag or self.stop:
                break
            if not a[i]:
                a[i] = True
                check_port(ip, i)


def watcher():
    # 监控进程
    global stop_flag, workers
    while not stop_flag:
        all_die = True
        for ind in range(len(workers)):
            i = workers[ind]
            if i.is_alive():
                all_die = False
                i.join()
        if all_die:
            break
    if not stop_flag:
        print("scan over")
        stop_flag = True


def add_thread(thread_count=1):
    for i in range(thread_count):
        th = ScanThread()
        workers.append(th)
        th.start()


def speed_thread():
    # 测速线程
    last_count = now_pos
    last_speed = 0
    while not stop_flag:
        time.sleep(3)
        now_speed = now_pos - last_count
        if now_speed > last_speed:
            add_thread()
        else:
            print("\n增加线程结束，似乎{}个线程最合适".format(len(workers)))
            return
        last_count = now_pos
        last_speed = now_speed


add_thread(init_thread_count)
threading.Thread(target=watcher).start()
threading.Thread(target=speed_thread).start()
while not stop_flag:
    time.sleep(3)
print("\n".join(map(str, open_ports)))
