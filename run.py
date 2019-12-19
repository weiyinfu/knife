import importlib
import os
import re
import subprocess as sp
import sys
from os.path import *
from os.path import abspath, basename, dirname, exists, join, splitext
from typing import List

import click
import colorama

"""
C++一键运行工具，需要跟根目录下的cpp.py文件配合使用

cpp.py文件编写格式:

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


def warn(*args):
    # 警告信息
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
    if not HAS_COLOR:
        s = remove_control_chars(s)
    print(s, flush=True)


def get_workspace_root(now):
    # 根目录的标志:makefile/.vscode/.git/.idea/CMakeLists.txt，使用加权方式计算每个目录是根目录的概率
    root = abspath(now)
    root_flags = {
        "makefile": 1,
        ".vscode": 100,
        ".idea": 100,
        ".git": 100,
        "CMakeLists.txt": 20,
    }
    ans = None
    max_score = -1
    while dirname(root) != root:
        score = sum(
            weight for flag, weight in root_flags.items() if exists(join(root, flag))
        )
        if score > max_score:
            ans = root
            max_score = score
        root = dirname(root)
    if max_score == 0:
        raise Exception("cannot find workspace")
    return ans


class CppConf:
    def __init__(self):
        self.cxx = None  # 编译器命令
        self.compiler_args = []  # 编译器参数列表
        self.preprocess = []  # 预处理的命令列表
        self.library_name_list = []  # 动态链接库的名字列表
        self.library_path = []  # 加载动态链接库的路径
        self.src_path = []  # 源码地址
        self.include_path = []  # 头文件地址


def flatten(a: List):
    # 把一个列表展平
    b = []
    for i in a:
        if type(i) == list:
            b.extend(flatten(i))
        else:
            b.append(i)
    return b


def load_conf(workspace_root) -> CppConf:
    # 加载cpp.py中的配置,并对配置进行预处理
    if workspace_root not in sys.path:
        sys.path.insert(0, workspace_root)
    cpp_conf = join(workspace_root, "cpp.py")
    assert exists(cpp_conf), f"cannot find {cpp_conf}"
    conf: CppConf = importlib.import_module("cpp")
    conf.library_path = flatten(conf.library_path)
    conf.library_name_list = flatten(conf.library_name_list)
    conf.src_path = flatten(conf.src_path)
    conf.preprocess = conf.preprocess
    conf.include_path = flatten(conf.include_path + conf.src_path)
    conf.library_path = [abspath(join(workspace_root, p)) for p in conf.library_path]
    conf.include_path = [
        abspath(join(workspace_root, header_path)) for header_path in conf.include_path
    ]
    src_path = [abspath(join(workspace_root, p)) for p in conf.src_path]
    conf.src_path = []
    for src_dir in src_path:
        if os.path.isfile(src_dir):
            conf.src_path.append(src_dir)
        else:
            conf.src_path.extend(get_all_cpp(src_dir))
    return conf


def get_newest_time(file_list: List[str]):
    return max(os.stat(f).st_mtime for f in file_list)


def get_all_cpp(dirpath):
    cpp = []
    for father, dirs, files in os.walk(dirpath):
        for f in files:
            if f.endswith(".cpp"):
                cpp.append(join(father, f))
    return cpp


def run_cpp(
    workspace_root: str,
    full_file_name: str,
    verbose: bool,
    dry_run: bool,
    debug: bool,
    single: bool,
    no_compile: bool,
):
    target_path = join(workspace_root, "target")
    conf: CppConf = load_conf(workspace_root)

    if not exists(target_path):
        os.mkdir(target_path)
        if verbose:
            pp(f"creating target path {target_path}")
    for pre_cmd in conf.preprocess:
        sp.check_call(pre_cmd, cwd=workspace_root, shell=True)
    debug_arg = "-g" if debug else ""
    include_arg = [f"-I{header_path}" for header_path in conf.include_path]
    if single:
        cpp_arg = [full_file_name]
    else:
        cpp_arg = [full_file_name] + conf.src_path
    lib_path_arg = [
        f"-L{abspath(join(workspace_root, lib_path))}" for lib_path in conf.library_path
    ]
    lib_name_arg = [f"-l{lib_name}" for lib_name in conf.library_name_list]
    exe_file_arg = join(target_path, splitext(basename(full_file_name))[0] + ".exe")
    if debug:
        conf.cxx = "g++"
    cmd = flatten(
        [
            conf.cxx,
            debug_arg,
            conf.compiler_args,
            include_arg,
            cpp_arg,
            lib_path_arg,
            lib_name_arg,
            f"-o{exe_file_arg}",
        ]
    )
    cmd = [c for c in cmd if c]
    cmd_with_color = flatten(
        [
            conf.cxx,
            debug_arg,
            colorama.Fore.LIGHTBLUE_EX,
            conf.compiler_args,
            colorama.Fore.RESET,
            colorama.Fore.MAGENTA,
            include_arg,
            colorama.Fore.RESET,
            cpp_arg,
            colorama.Fore.LIGHTBLUE_EX,
            lib_path_arg,
            colorama.Fore.MAGENTA,
            lib_name_arg,
            colorama.Fore.RESET,
            f"-o{exe_file_arg}",
        ]
    )
    cmd_string = " ".join(cmd_with_color)
    pp(cmd_string)

    if not dry_run and not no_compile:
        sp.check_call(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    pp(
        colorama.Fore.GREEN
        + line_wrap("compile successfully !".upper())
        + colorama.Fore.RESET
    )
    if not dry_run and not debug:
        sp.check_call(
            exe_file_arg,
            env={"LD_LIBRARY_PATH": ":".join(conf.library_path)},
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        pp(
            "\n"
            + colorama.Fore.GREEN
            + line_wrap("run successfully !".upper())
            + colorama.Fore.RESET
        )


@click.group("run", help="一键运行C++")
def main():
    pass


@main.command("print-library-path", help="打印C++的LIBRARY_PATH")
@click.argument("file-name", nargs=1)
@click.option("--l-join", default=False, is_flag=True, help="使用-L分隔")
@click.option("--colon-join", default=True, is_flag=True, help="使用冒号分隔")
def print_library_path(file_name: str, l_join: bool, colon_join: bool):
    workspace_root = get_workspace_root(abspath(file_name))
    conf = load_conf(workspace_root)
    if l_join:
        print(" ".join(f"-L{p}" for p in conf.library_path))
        return
    if colon_join:
        print(":".join(conf.library_path))
        return
    assert False, "impossible"


@main.command("mm", help="相当于-MM参数查看依赖")
@click.argument("file-name", nargs=1)
@click.option("--show-all", default=False, is_flag=True, help="显示全部依赖")
def print_dependency(file_name: str, show_all: bool):
    workspace_root = get_workspace_root(abspath(file_name))
    conf = load_conf(workspace_root)
    arg = "-M" if show_all else "-MM"
    cmd = flatten(
        [conf.cxx, arg, [f"-I{header}" for header in conf.include_path], file_name]
    )
    sp.check_call(cmd)


@main.command("init", help="生成初始化文件")
def generate_init_file():
    workspace_root = get_workspace_root(abspath("."))
    init_file = join(workspace_root, "cpp.py")
    if exists(init_file):
        print(f"{init_file} already exists !")
        exit(0)
    open(init_file, "w").write(
        """
# 以下配置中，路径列表可以嵌套，加载配置时会自动将路径列表展成一维列表
import os

cc = "g++"  # 编译器名称
compiler_args = ["-std=c++17", "-lpthread"]  # 编译器开关

preprocess = []  # 在运行代码之前需要执行的命令
library_name_list = []
library_path = []
# 源码路径列表,本项目中clusterkit使用CMake进行编译
src_path = []
# include_path
include_path = []

    """
    )


@main.command("print-include-path", help="打印C++的include路径")
@click.argument("file-name", nargs=1)
@click.option("--i-join", default=False, is_flag=True, help="使用-I分隔")
@click.option("--colon-join", default=True, is_flag=True, help="使用冒号分隔")
def print_include_path(file_name: str, i_join: bool, colon_join: bool):
    workspace_root = get_workspace_root(abspath(file_name))
    conf = load_conf(workspace_root)
    if i_join:
        print(" ".join(f"-I{p}" for p in conf.include_path))
        return
    if colon_join:
        print(":".join(conf.include_path))
        return
    assert False, "impossible"


@main.command("cpp", help="run cpp !")
@click.argument("file-name", nargs=1)
@click.option("--workspace-root", help="工作区路径")
@click.option("--verbose", default=False, is_flag=True, help="是否冗余显示")
@click.option("--dry-run", default=False, is_flag=True, help="只打印命令但是不运行")
@click.option("--debug", default=False, is_flag=True, help="调试程序")
@click.option("--single", default=False, is_flag=True, help="当前程序只依赖标准库，是一个独立的程序")
@click.option("--no-compile", default=False, is_flag=True, help="不编译直接运行")
def cpp(
    workspace_root: str,
    file_name: str,
    verbose: bool,
    dry_run,
    debug: bool,
    single: bool,
    no_compile: bool,
):
    get_window_size()  # 使print决定是否输出颜色
    try:
        if verbose:
            pp(f"file_name={file_name}")
        full_file_name = abspath(file_name)
        if workspace_root is None:
            workspace_root = get_workspace_root(full_file_name)
        assert full_file_name.endswith(".cpp") or full_file_name.endswith(
            ".c"
        ), "can only compile cpp file"
        run_cpp(
            workspace_root, full_file_name, verbose, dry_run, debug, single, no_compile
        )
    except sp.CalledProcessError as e:
        pp(colorama.Fore.RED + line_wrap("FATAL ERROR!") + colorama.Fore.RESET)
        pp(
            f"{e.cmd if type(e.cmd) == str else ' '.join(e.cmd)}{colorama.Fore.RED} exited abnomally with code {e.returncode}{colorama.Fore.RESET}"
        )
        exit(e.returncode)
    except Exception as e:
        if verbose:
            raise e
        print(e)
        print(type(e))


if __name__ == "__main__":
    main()

"""
TODO:
* 多进程编译
* 如果文件没有改变,不必编译,直接链接
* 动态链接库
* 自动改写vscode配置，或者生成推荐配置，g++ -v查看头文件，g++确定动态链接库位置
"""
