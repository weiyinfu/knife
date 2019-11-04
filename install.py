import os
import subprocess as sp

target_path = os.path.join(os.path.expanduser("~"), "bin")
"""
把本文件夹下的所有命令一键安装到某个PATH路径下
"""
now_dir = os.path.dirname(os.path.abspath(__file__))
files = os.listdir(now_dir)
python3_path = str(sp.check_output(["which", "python3"]), encoding="utf8").strip()
for i in files:
    if i == os.path.basename(__file__):
        continue
    if not i.endswith(".py"):
        continue
    cmd = i[: -len(".py")]
    src = open(os.path.join(now_dir, i), encoding="utf8").read()
    if not src.startswith("#!"):
        src = f"#!{python3_path}\n{src}"
    target = os.path.join(target_path, cmd)
    open(target, mode="w", encoding="utf8").write(src)
    os.chmod(target, 0o775)
