import multiprocessing as mp

"""
把cpu占满，测试CPU性能，检查cpu是否完好
"""


def run():
    for i in range(int(1e9)):
        for j in range(int(1e9)):
            pass


for i in range(mp.cpu_count()):
    mp.Process(target=run).start()
