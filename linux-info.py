"""
一个命令生成linux信息
"""
import subprocess
from pprint import pprint

import click


def pack_comand(cmd: str):
    res = None
    try:
        res = subprocess.check_output(cmd, shell=True)
        res = str(res, encoding="utf8").strip()
        return res
    except:
        return res


command_list = [
    ("uname -a", "查看内核"),
    ("head -n 1 /etc/issue", "查看操作系统版本"),
    ("cat /proc/cpuinfo", "查看CPU信息"),
    ("hostname", "查看计算机名称"),
    ("du ./ --max-depth=1 -h  2>/dev/null", "家目录大小"),
    ("lspci -tv", "列出全部PCI设备"),
    ("lsusb -tv", "列出全部usb设备"),
    ("lsmod", "列出加载的内核模块"),
    ("env", "查看环境变量"),
    ("free -mh", "查看内存使用两和交换区使用量"),
    ("df -h", "查看各分区使用情况"),
    ("grep MemTotal /proc/meminfo", "查看内存总量"),
    ("grep MemFree /proc/meminfo", "查看空闲内存量"),
    ("uptime", "查看系统运行时间、用户数、负载"),
    ("cat /proc/loadavg", "查看系统负载磁盘和分区"),
    ("mount | column -t", "查看挂接的分区状态"),
    ("fdisk -l 2>/dev/null", "查看所有分区"),
    ("swapon -s", "查看所有交换分区"),
    # ("hdparm -i /dev/hda", "查看磁盘参数"),
    ("dmesg | grep IDE", "查看启动时IDE设备检测状况网络"),
    ("cat /proc/version", "查看内核版本"),
    ("ifconfig", "查看所有网络接口的属性"),
    ("iptables -L", "查看防火墙设置"),
    ("route -n", "查看路由表"),
    ("netstat -lntp", "查看所有监听端口"),
    ("netstat -antp", "查看所有已经建立的连接"),
    ("netstat -s", "查看网络统计信息进程"),
    ("ps -ef", "查看所有进程"),
    ("top", "实时显示进程状态用户"),
    ("w", "查看活动用户"),
    ("id <用户名>", "查看指定用户信息"),
    ("last", "查看用户登录日志"),
    ("cut -d: -f1 /etc/passwd", "查看系统所有用户"),
    ("cut -d: -f1 /etc/group", "查看系统所有组"),
    ("crontab -l", "查看当前用户的计划任务服务"),
    ("chkconfig –list", "列出所有系统服务"),
    ("chkconfig –list | grep on", "列出所有启动的系统服务程序"),
    (
        ' cat /proc/cpuinfo |grep "model name" && cat /proc/cpuinfo |grep "physical id',
        "CPU信息",
    ),
    ("cat /proc/meminfo |grep MemTotal", "内存大小"),
    ("fdisk -l |grep Disk", "硬盘大小"),
    ("ls /proc", "全部进程"),
    ("cat /sys/fs/cgroup/memory/memory.stat", "查看内存"),
]
program = [
    ("which gcc", "默认gcc"),
    ("gcc -v", "gcc版本"),
    ("which java", "java"),
    ("nvidia-smi", "gpu使用情况"),
]
dynamic = [("top", "查看占用CPU高的进程"), ("htop", "系统资源分析")]
redhat = [("rpm -qa", "查看所有安装的软件包)"), ("cat /etc/redhat-release", "查看redhat版本")]


@click.command("linux-info")
def linuxInfo():
    for i, j in command_list:
        print(i)
        print(j)
        print("=" * 20)
        pprint(pack_comand(i))


if __name__ == "__main__":
    linuxInfo()
