import importlib
import subprocess as sp
import sys
from os.path import *
from typing import Dict

import click

"""
pymake是一个命令管理工具，目的为解决以下问题：
* 项目中会用到很多小命令，如果每个命令都写成一个单独的文件不利于维护，不利于修改。
* makefile提供了target到命令的映射，但是当使用cmake时，makefile名称跟cmake产生的makefile冲突,所以需要一个独立的命令列表
* pymake可以在项目的任何子目录下执行pymake target来执行项目相关的命令。这是因为pymake能够自动感知项目的根目录

每个cmd应该是一个List[str] 或者是str。如果是str，cmd.split()会将它分隔成若干个部分。
命令中，支持使用宏

makefile.py中可以有一个CWD变量，它是一个字符串集合

在shell模式下，如何实现/bin/bash -e的功能 

TODO：以字典方式定义命令
buildCuda = {
    "cwd": ".",
    "cmd": \"\"\"
cd kmcuda/build
cmake ..
make -j10
ls
\"\"\",
"shell": True
}


"""

WORKSPACE_ROOT = "${WORKSPACE_ROOT}"
CURRENT_DIR = "${CURRENT_DIR}"


def get_workspace_root(now):
    # 根目录的标志:makefile/.vscode/.git/.idea/CMakeLists.txt
    root = abspath(now)
    root_flags = {
        "makefile": 1,
        "Makefile": 1,
        ".vscode": 100,
        ".idea": 100,
        ".git": 100,
        "makefile.py": 100,
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


def rewrite(macros: Dict[str, str], cmd: str):
    for k, v in macros.items():
        if k in cmd:
            cmd = cmd.replace(k, v)
    return cmd


@click.command("pymake", help="一个项目的常用命令集合")
@click.argument("target")
def main(target: str):
    workspace_root = get_workspace_root(abspath("."))
    sys.path = [workspace_root] + sys.path
    if not exists(join(workspace_root, "makefile.py")):
        sys.stderr.write("no makefile.py in workspace root !")
        exit(-1)
    makefile = importlib.import_module("makefile")
    if not hasattr(makefile, target):
        sys.stderr.write(f"找不到名为{target}的target")
        exit(-1)
    cmd = getattr(makefile, target)
    if type(cmd) == str:
        cmd_list = [cmd]
    elif type(cmd) == list:
        cmd_list = cmd
    else:
        assert False, "unkown type %s" % (type(cmd))
    macros = {WORKSPACE_ROOT: workspace_root, CURRENT_DIR: abspath(curdir)}
    for cmd in cmd_list:
        if type(cmd) == str and not exists(cmd):
            cmd = cmd.split()
        if type(cmd) == list:
            cmd = [rewrite(macros, i) for i in cmd]
        print(cmd)
        sp.check_call(cmd, cwd=workspace_root)


if __name__ == "__main__":
    main()
