"""
查看端口占用情况，打印端口信息
"""
import socket
import subprocess as sp

import click
import psutil


def is_port_open(ip: str, port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        # 利用shutdown()函数使socket双向数据传输变为单向数据传输。shutdown()需要一个单独的参数，
        # 该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写。
        return True
    except:
        return False


def get_process_id_by_port(port: int):
    res = sp.check_output(f"lsof -i:{port}", shell=True)
    lines = res.splitlines()
    assert len(lines) > 0
    pid = lines[1].split()[1]
    return int(pid)


def get_processes_of_port(port: int):
    res = sp.check_output(f"lsof -i:{port}", shell=True)
    lines = res.splitlines()
    pids = [lines[i].split()[1] for i in range(1, len(lines))]
    pids = [int(i) for i in pids]
    return pids


@click.command("seeport")
@click.argument("port", nargs=1, type=int)
def main(port):
    if not is_port_open("127.0.0.1", port):
        print(f"port {port} is down")
        exit(0)
    pid = get_process_id_by_port(port)
    p = psutil.Process(pid)
    print(
        f"""port:{port}
pid:{pid}
cpu:{p.cpu_percent()}
cmd:{" ".join(p.cmdline())}
username:{p.username()}
name:{p.name()}
numthreads:{p.num_threads()}
cwd:{p.cwd()}
num_fds:{p.num_fds()}
"""
    )


if __name__ == "__main__":
    main()
