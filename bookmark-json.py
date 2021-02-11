"""
chrome书签文件和json互相转换
chrome 书签加载器
把类html形式的书签列表解析为JSON，JSON包括三个字段：label，children，url，其中url和children不能同时存在，有label和url的object表示叶子节点，有label和children的object表示目录节点
把JSON转换成chrome能识别的HTML格式
"""
import json
import os
import sys
import pyquery as pq
import re


def trim(node):
    # 去掉开头的单子结点
    if node["children"] and len(node["children"]) == 1:
        son = node["children"][0]
        if son["children"]:
            return trim(son)
        else:
            return node
    else:
        return node


def json2bookmark(node):
    # 把json转换成chrome书签管理器能识别的html格式
    if type(node) == list:
        assert len(node) == 1, "必须是单根节点"
        node = node[0]
    node = trim(node)  # 去掉多余结点

    def handle(node):
        if not "children" in node:
            # 如果是叶子节点
            if not re.match("^\w+://", node["url"]):
                print(f"url should be absolute path but now is {node['url']}")
                exit(-1)
            return f"<DT><A HREF=\"{node['url']}\">{node['label']}</A>\n"
        s = "".join(map(handle, node["children"]))
        return f"<DT><H3>{node['label']}</H3>\n<DL>\n{s}\n</DL>\n"

    s = "\n".join(map(handle, node["children"]))
    return f"<DL>\n{s}\n</DL>"


def bookmark2json(html_file):
    if not os.path.exists(html_file):
        raise Exception(f"{html_file}不存在")
    lines = open(html_file, encoding="utf8").readlines()
    i = 0
    while not lines[i].strip().startswith("<DL>"):
        i += 1
    stack = [[{"label": "root"}]]
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("<DL>"):
            stack.append([])
        elif line.startswith("<DT>"):
            line = line[len("<DT>"):]
            ele = pq.PyQuery(line)
            it = {"label": ele.text()}
            if "HREF=" in line:
                it["url"] = ele.attr("HREF")
            stack[-1].append(it)
        elif line.startswith("</DL>"):
            sons = stack.pop()
            stack[-1][-1]["children"] = sons  # 上一层的最后一个元素
        else:
            assert False, f"error line {line}"
        i += 1
    return stack[0][0]


def main():
    if len(sys.argv) == 1:
        print("请输入文件名")
        exit(-1)
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(f"{filename} not exists !")
        exit(-1)
    if filename.endswith(".json"):
        data = json.load(open(filename, encoding="utf8"))
        html = json2bookmark(data)
        target_name = os.path.splitext(filename)[0] + ".html"
        if os.path.exists(target_name):
            print(f"{target_name} already exists !")
            exit(-1)
        open(target_name, "w").write(html)
    elif filename.endswith(".html"):
        node = bookmark2json(filename)
        target_name = os.path.splitext(filename)[0] + ".json"
        if os.path.exists(target_name):
            print(f"{target_name} already exits !")
            exit(-1)
        json.dump(
            node, open(target_name, "w", encoding="utf8"), ensure_ascii=False, indent=2
        )
    else:
        print(f"{filename} must be one of .json or .html")
        exit(-1)


if __name__ == "__main__":
    main()
