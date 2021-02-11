import os
import subprocess as sp
from os.path import *

"""
根据node命令找到node所在的目录，把node_modules软链接到当前目录
在mac下把nodemodules软链接到当前目录可能有问题
"""
node_path = str(sp.check_output("which node", shell=True), encoding="utf8")
if not node_path:
    raise Exception("cannot find node command")
node_modules = abspath(join(dirname(node_path), "..", "lib", "node_modules"))
des = abspath(join("./node_modules"))
print("src:", node_modules, "\ndes:", des)
os.symlink(node_modules, des)
