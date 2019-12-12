import os
import subprocess as sp

import click

# 把可执行文件安装到此目录
target_path = os.path.join(os.path.expanduser("~"), "knife-bin")
"""
把本文件夹下的所有命令一键安装到某个PATH路径下

提供两种安装方式：
* 以bash方式安装
* 以Python方式安装，这种方式的好处是可以修改knife源码
"""

if not os.path.exists(target_path):
    res = input(f"do you like to create folder {target_path}? y/n")
    if res.lower().strip() == "y":
        os.mkdir(target_path)
    else:
        print("do nothing")
        exit(-1)
python3_path = str(sp.check_output(["which", "python3"]), encoding="utf8").strip()


def cmd_iterator():
    """迭代当前目录下所有的可用命令"""
    now_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(now_dir)
    for i in files:
        if i == os.path.basename(__file__):
            continue
        if not i.endswith(".py"):
            continue
        cmd = i[: -len(".py")]
        target = os.path.join(target_path, cmd)
        yield os.path.join(now_dir, i), cmd, target


def install():
    # 以python文件拷贝的方式安装
    for src_path, cmd, target in cmd_iterator():
        src = open(src_path, encoding="utf8").read()
        if not src.startswith("#!"):
            src = f"#!{python3_path}\n{src}"
        open(target, mode="w", encoding="utf8").write(src)
        os.chmod(target, 0o775)


def install_soft():
    # 软链方式安装
    for src_path, cmd, target in cmd_iterator():
        open(target, mode="w", encoding="utf8").write(
            f'#!/bin/bash\n{python3_path} {src_path} "$@"'
        )
        os.chmod(target, 0o775)


@click.command("install")
@click.option("-s", "--soft", is_flag=True, default=False, help="是否使用shell方式安装")
@click.option("--dry-run", is_flag=True, default=False, help="打印可用的工具，并不安装")
def main(soft: bool, dry_run: bool):
    if dry_run:
        for src_path, cmd, target in cmd_iterator():
            print(f"{cmd}:{src_path}->{target}")
        return
    install_soft() if soft else install()


if __name__ == "__main__":
    main()
