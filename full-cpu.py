"""
把cpu占满，测试CPU性能，检查cpu是否完好
"""
import multiprocessing as mp


def run():
    for i in range(int(1e9)):
        for j in range(int(1e9)):
            pass


for i in range(mp.cpu_count()):
    mp.Process(target=run).start()
