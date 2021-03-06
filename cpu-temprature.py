import glob
import os

import tabulate

"""
linux下查看CPU温度，仅适用于huawei+deepin
"""
files = glob.glob("/sys/class/hwmon/hwmon0/device/hwmon/hwmon0/temp*")

a = [
    (os.path.basename(filename), int(open(filename).read()) / 1000)
    for filename in files
]
print(tabulate.tabulate(a))
