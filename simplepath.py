#!/usr/bin/python
"""
简化path环境变量
用法：export PATH=`simplepath`
"""
import os
import platform

p = os.environ['PATH']
sysstr = platform.system().lower()
sep = ';' if sysstr == 'windows' else ':'
a = p.split(sep)
b = set()
c = []
for i in a:
    if i not in b:
        b.add(i)
        c.append(i)
print(':'.join(c))
