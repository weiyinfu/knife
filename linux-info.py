"""
一个命令生成linux信息
"""
import math
import re
import subprocess

import click
import psutil
import tabulate


def pack_comand(cmd: str):
    # 运行命令并对结果进行一定的处理
    res = None
    try:
        res = subprocess.check_output(cmd, shell=True)
        res = str(res, encoding="utf8").strip()
        res = res.replace("\\n", "").replace("\\l", "").strip()
        return res
    except:
        return None


# 查看系统信息
uname = [
    ("uname --kernel-name", "内核名称"),
    ("uname --nodename", "主机名称"),
    ("uname --kernel-release", "内核发行号"),
    ("uname --kernel-version", "安装日期"),
    ("uname --machine", "机器硬件名称"),
    ("uname --processor", "处理器类型"),
    ("uname --operating-system", "操作系统"),
    ("uname --hardware-platform", "硬件平台"),
    ("head -n 1 /etc/issue", "操作系统发行版"),
    ("hostname", "计算机名称"),
    ("whoami", "用户名称"),
    ("uptime --since", "开机时间"),
    ("hostname -I", "IP地址"),
]

plain = [(desc, pack_comand(cmd)) for cmd, desc in uname]  # 无需运行，直接展示


def get_screen():
    # 屏幕分辨率
    info = pack_comand("xrandr")
    resolution = re.search("current (\d+ x \d+)", info).group(1)
    screen_size = re.search("\d+mm x \d+mm", info).group(0)
    return resolution, screen_size


resolution, screen_size = get_screen()
plain.extend([("=====", "======"), ("屏幕分辨率", resolution), ("屏幕尺寸", screen_size)])

# psutil系列
plain.extend(
    [
        ("=======", "========"),
        ("物理CPU个数", psutil.cpu_count()),
        ("逻辑CPU个数", psutil.cpu_count(logical=True)),
        ("CPU使用率", psutil.cpu_percent()),
        ("进程数", len(psutil.pids())),
        ("电量",pack_comand("cat `find /sys/devices -name capacity`")+"%")
    ]
)


def human_size(sz):
    x = ["B", "k", "M", "G"]
    ind = int(math.log(sz, 1024))
    return f"{sz / (1024 ** ind):.3f} {x[ind]}"


virtual_memory = psutil.virtual_memory()
plain.extend(
    (
        ("====内存信息", "======="),
        ("总大小", human_size(virtual_memory.total),),
        ("已用", human_size(virtual_memory.used)),
        ("已用百分比", f"{virtual_memory.percent:.1f}%"),
    )
)
net_io = psutil.net_io_counters()
plain.extend(
    (
        ("=====网络", "====="),
        ("已发送", human_size(net_io.bytes_sent)),
        ("已接受", human_size(net_io.bytes_recv)),
    )
)
command_list = [
    ("cat /proc/cpuinfo", "查看CPU信息"),
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
    print(tabulate.tabulate(plain))


if __name__ == "__main__":
    linuxInfo()
