import os
import re
import sys
from urllib.parse import unquote

import requests
from pyquery import PyQuery
from tqdm.autonotebook import tqdm

"""
从Github上下载文件夹，因为raw github不可用，导致这个工具用途不大
"""


def join(parent: str, son: str):
    if son.startswith("http://") or son.startswith("https://"):
        return son
    else:
        # //如果儿子是根路径，那么parent应该只保留域名
        if son.startswith("/"):
            son = son[1:]
            if '/' in parent:
                parent = parent[:parent.index('/', parent.index('://') + 3)]
        if parent.endswith("/"): parent = parent[:-1]
        return parent + '/' + son


def list_dir(url):
    resp = requests.get(url)
    resp.encoding = 'utf8'
    html = PyQuery(resp.content)
    links = html(".js-navigation-container tr.js-navigation-item")
    a = []
    for ind in range(0, links.length):
        ele = links.eq(ind)
        link = ele("a")
        if link.text() == "..":
            continue
        item_type = ele("svg").attr('aria-label')
        a.append({
            'title': link.text().strip(),
            'url': join(url, link.attr('href')).strip(),
            'type': item_type,
        })
    return a


blob = r"https://github\.com/(.+?)/blob/master/(.+)$"
raw = r"https://raw.githubusercontent.com/(.+?)/master/(.+)$"
tree = r"https://github.com/(.+?)/tree/master/(.+)$"


def to_raw(url: str):
    user_repo, filepath = parse(url)
    return f"https://raw.githubusercontent.com/{user_repo}/master/{filepath}"


def parse(url: str):
    for i in (blob, raw, tree):
        if re.match(i, url):
            res = re.search(i, url)
            user_repo, filepath = res.group(1), res.group(2)
            return user_repo, filepath
    raise Exception("error format of {}".format(url))


def download_file(url, local_path):
    if os.path.exists(local_path): return
    parent = os.path.dirname(local_path)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception("download fail")
    if not os.path.exists(parent):
        os.makedirs(parent)
    open(local_path, 'wb').write(resp.content)


def list_dir_recursive(url):
    a = []
    for i in list_dir(url):
        if i['type'] == 'file':
            a.append(i)
        else:
            i['children'] = list_dir_recursive(i['url'])
    return a


def flatten(folder):
    # 把一个文件夹展平，只显示文件，不显示文件夹
    a = []

    def go(node):
        if type(node) == list:
            for son in node:
                go(son)
        elif node['type'] == 'file':
            a.append(node['url'])
        else:
            for son in node['children']:
                go(son)

    go(folder)
    return a


def build_map(url: str):
    # 给定url建立本地文件到远程文件的映射
    folder = list_dir_recursive(url)
    files = flatten(folder)
    print("list folder over , got {} files ".format(len(folder)))
    root_user_repo, root_file_path = parse(url)
    ma = []
    for file_url in tqdm(files, desc="building map"):
        user_repo, filepath = parse(file_url)
        if not filepath.startswith(root_file_path):
            raise Exception("error")
        ma.append((to_raw(file_url), unquote(os.path.relpath(filepath, os.path.dirname(root_file_path)))))
    return ma


def download_folder(url: str):
    ma = build_map(url)
    for remote_url, local_file in tqdm(ma, desc="downloading file"):
        download_file(remote_url, local_file)


def test():
    tree = "https://github.com/JetBrains/intellij-community/tree/master/platform/platform-resources/src/keymaps"
    blob = "https://github.com/JetBrains/intellij-community/blob/master/platform/platform-resources/src/keymaps/Visual%20Studio.xml"
    print(parse(tree))
    print(parse(blob))
    print(to_raw(blob))


def test2():
    tree = "https://github.com/JetBrains/intellij-community/tree/master/platform/platform-resources/src/keymaps"
    ma = build_map(tree)
    print(ma)


def test3():
    tree = "https://github.com/JetBrains/intellij-community/tree/master/platform/platform-resources/src/keymaps"
    download_folder(tree)


def main():
    url = sys.argv[1]
    url.strip()
    download_folder(url)


if __name__ == '__main__':
    main()
