import os
import re
import subprocess as sp
import sys
from os.path import *
from os.path import abspath, dirname, exists, join

import click
import colorama

"""
python命令运行一个单文件时，这个单文件可能位于某个包下
"""
DEBUG = False
HAS_COLOR = True


def get_window_size():
    # 获取窗口大小，用于打印美观表格
    default_window_size = 80, 40
    try:
        with open("/dev/null", "w") as err:
            window_size = sp.check_output(["stty", "size"], stderr=err).split()
        if len(window_size) == 0:
            return default_window_size
        rows, columns = window_size
        return int(rows), int(columns)
    except Exception as e:
        global HAS_COLOR
        HAS_COLOR = False
        if DEBUG:
            warn(e)
        return default_window_size


def get_caller_info(frame_number):
    # 带行号的打印
    def findCaller():
        f = sys._getframe(frame_number)
        if f is not None:
            f = f.f_back
        co = f.f_code
        return co.co_filename, f.f_lineno, co.co_name

    file, line, func = findCaller()
    file = os.path.relpath(file, os.curdir)
    if func != "<module>":
        info = "%s:%s(%s)" % (file, line, func)
    else:
        info = "%s:%s" % (file, line)
    return info


def warn(*args):
    info = get_caller_info(2) if DEBUG else ""
    print(info, end="")
    print(colorama.Fore.RED, *args, colorama.Style.RESET_ALL, sep="")


def remove_control_chars(s):
    # 去掉字符串s中的颜色控制字符
    return re.sub("\033\[\d+m", "", s)


def line_wrap(s):
    # 将字符串s用=包围起来,让一行充满整个屏幕
    w, h = get_window_size()
    line = "=" * ((h - len(s)) // 2)
    return line + s + line


def pp(s):
    # 控制台输出统一调用此函数
    line_info = get_caller_info(2) if DEBUG else ""
    if not HAS_COLOR:
        s = remove_control_chars(s)
    print(line_info + s, flush=True)


def get_python_root(now: str):
    # 获取python路径
    if isfile(now):
        now = dirname(now)
    while exists(join(now, "__init__.py")):
        # 说明这是一个包
        last = now
        now = dirname(now)
        if now == last:
            break
    return now


def run_python(full_file_name: str, verbose: bool):
    # 首先找到根包
    now = get_python_root(full_file_name)
    if verbose:
        pp(f"root package is {now}")
    # 其次对旧有的PYTHONPATH进行处理
    old_path_list = (
        os.environ["PYTHONPATH"].split(os.pathsep) if "PYTHONPATH" in os.environ else []
    )

    # 路径拼接和去重
    path_list = [now] + old_path_list
    uniq_path_list = []
    for i in path_list:
        if i in uniq_path_list:
            continue
        uniq_path_list.append(i)
    python_path = os.pathsep.join(uniq_path_list)
    if verbose:
        pp(f"PYTHONPATH={python_path}")
    cmd = ["python3", full_file_name]
    env = os.environ
    env["PYTHONPATH"] = python_path
    cmd_string = " ".join(cmd)
    if verbose:
        pp(f"cmd string ={cmd_string}")
    sp.check_call(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, env=env)


@click.command("py", help="run python !")
@click.argument("file-name", nargs=1)
@click.option("--verbose", default=False, is_flag=True, help="是否冗余显示")
def python(file_name: str, verbose: bool):
    get_window_size()  # 使print决定是否输出颜色
    try:
        if verbose:
            pp(f"file_name={file_name}")
        full_file_name = abspath(file_name)
        run_python(full_file_name, verbose)
    except sp.CalledProcessError as e:
        pp(colorama.Fore.RED + line_wrap("FATAL ERROR!"))
        pp(
            f"{colorama.Fore.YELLOW}{e.cmd if type(e.cmd)==str else ' '.join(e.cmd)}{colorama.Fore.RED} exited abnomally with code {e.returncode}{colorama.Fore.RESET}"
        )
        exit(e.returncode)
    except Exception as e:
        if verbose:
            raise e
        print(e)
        print(type(e))


if __name__ == "__main__":
    python()
