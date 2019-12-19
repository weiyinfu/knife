"""
一个命令把若干个文件转成utf编码
"""
import os
import sys

import chardet
from tqdm import tqdm

bad = []  # 转换失败的
transformed = []  # 转换成功的
skip = []  # 无需转换的


def transform(filepath: str):
    if not os.path.exists(filepath):
        bad.append(f"{filepath} not exists ! ")
        return
    encoding = chardet.detect(open(filepath, "rb").read())
    print(f"{filepath} encoding={encoding}")
    if encoding["confidence"] < 0.9:
        bad.append(f"{filepath} cannot detect encoding")
        return
    encoding = encoding["encoding"]
    if encoding == "utf8":
        print(f"{filepath} don't need transform ! ")
        skip.append(filepath)
    else:
        content = open(filepath, encoding=encoding, errors="ignore").read()
        open(filepath, encoding="utf8", mode="w").write(content)
        print(f"transform {filepath} over ! ")
        transformed.append(f"transform {filepath} {encoding}->utf8 !")


if len(sys.argv) == 1:
    print(f"please input filename list !")
    exit(0)
for file in tqdm(sys.argv[1:]):
    transform(file)
if len(skip):
    print(f"跳过{len(skip)}个文件")
    print(" ".join(skip))
if len(transformed):
    print(f"成功转换{len(transformed)}个文件")
    print(" ".join(transformed))
if len(bad):
    print(f"失败{len(bad)}个文件")
    print(" ".join(bad))
