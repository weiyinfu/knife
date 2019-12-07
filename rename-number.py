import os
import re

d = os.path.abspath(os.path.curdir)
now = 1

file_pattern = "^\d+-.*\.py"
filenames = [i for i in os.listdir(d) if re.match(file_pattern, i)]


def filenum(filename):
    k = filename[: filename.index("-")]
    return int(k)


filenames = sorted(filenames, key=filenum)
for filename in filenames:
    if re.match(file_pattern, filename):
        k = filename[filename.index("-") :]
        newfilename = "%03d" % now + k
        os.rename(os.path.join(d, filename), os.path.join(d, newfilename))
        print(filename, newfilename)
        now += 5
