import os
import subprocess as sp
from os.path import *

node_path = str(sp.check_output("which node", shell=True), encoding="utf8")
if not node_path:
    raise Exception("cannot find node command")
node_modules = abspath(join(dirname(node_path), "..", "lib", "node_modules"))
des = abspath(join("./node_modules"))
print("src:", node_modules, "\ndes:", des)
os.symlink(node_modules, des)
