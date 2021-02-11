"""
一个命令把若干个文件转成utf编码
"""
import os
import sys

import chardet
from tqdm.autonotebook import tqdm

bad = []  # 转换失败的
transformed = []  # 转换成功的
skip = []  # 无需转换的


def transform(filepath: str, encoding: str):
    if not os.path.exists(filepath):
        bad.append(f"{filepath} not exists ! ")
        return
    det_info = chardet.detect(open(filepath, "rb").read())
    print(f"{filepath} encoding={det_info}")
    if det_info["confidence"] < 0.9:
        bad.append(f"{filepath} cannot detect encoding")
        return
    det_encoding = det_info["encoding"]
    if det_encoding == "utf8":
        print(f"{filepath} don't need transform ! ")
        skip.append(filepath)
    else:
        encoding = encoding or det_encoding
        content = open(filepath, encoding=encoding, errors="ignore").read()
        open(filepath, encoding="utf8", mode="w").write(content)
        print(f"transform {filepath} over ! ")
        transformed.append(f"transform {filepath} {encoding}->utf8 !")


if len(sys.argv) == 1:
    print(f"""please input filename list !
用法：{__file__[:-3]} gbk xxx.txt xx.md gb2312  *.js none haha.java
""")
    exit(0)
encoding_list = ['gbk', 'gb2312', 'none']
last_encoding = None
for file in tqdm(sys.argv[1:]):
    if file in encoding_list:
        last_encoding = file if file != 'none' else None
        continue
    transform(file, last_encoding)
if len(skip):
    print(f"跳过{len(skip)}个文件")
    print(" ".join(skip))
if len(transformed):
    print(f"成功转换{len(transformed)}个文件")
    print(" ".join(transformed))
if len(bad):
    print(f"失败{len(bad)}个文件")
    print(" ".join(bad))
