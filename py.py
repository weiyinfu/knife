import os
import subprocess as sp
import sys
from os.path import *
from os.path import abspath, dirname, exists, join

"""
python命令运行一个单文件时，这个单文件可能位于某个包下，所以运行之前需要更改PYTHONPATH
"""


def get_python_root(now: str):
    # 获取python路径，一直向上级目录寻找，直到找不到__init__文件为止
    if isfile(now):
        now = dirname(now)
    while exists(join(now, "__init__.py")):
        # 说明这是一个包
        last = now
        now = dirname(now)
        if now == last:
            break
    return now


if len(sys.argv) == 1:
    print(f"using {sys.executable} as python")
    print("请指明参数名称")
    exit(-1)
file_name = sys.argv[1]
full_file_name = abspath(file_name)
now = get_python_root(full_file_name)
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
cmd = sys.argv
cmd[0] = sys.executable
env = os.environ
env["PYTHONPATH"] = python_path
# 如果抛出异常，不要进一步打印异常
sp.check_call(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, env=env)
