import math
import os

import click
from PIL import Image

"""
把png转换成icon，这样的网站有很多

* 比特虫：http://www.bitbug.net/
* https://www.easyicon.net/covert/
* https://www.aconvert.com/cn/icon/png-to-ico/
* http://www.faviconico.org/
* https://convertio.co/zh/png-ico/
"""


@click.command()
@click.argument("cin", nargs=1)
@click.option(
    "-o", "cout", default=None, help="The output file name", required=False, type=str
)
@click.option(
    "-s", "size", help="The icon size to be generate", type=int, required=False,
)
def main(cin, cout, size):
    if not os.path.exists(cin):
        print(f"{cin} doesn't exist ! ")
        exit(-1)
    img = Image.open(cin)
    if not size:
        size = min(img.size)
        size = 2 ** int(math.log2(size))
    if not cout:
        parts = os.path.splitext(os.path.basename(cin))
        cout = parts if len(parts) == 1 else parts[0]
        cout = cout + ".ico"
        cout = os.path.join(os.path.dirname(cin), cout)
    print(f"{cin}->{cout} {size}")
    img.save(cout, "ICO", sizes=[(size, size)])


if __name__ == "__main__":
    main()
