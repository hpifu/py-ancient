#!/usr/bin/env python3

import argparse
import requests
import sys
import json
import os
import pickle
from pyquery import PyQuery as pq

www = "http://gwx.babihu.com"


def extractLink(url):
    count = 0
    while True:
        try:
            res = requests.get(
                url,
                headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
                }
            )
            d = pq(res.text)
            hrefs = []
            for a in d("a").items():
                hrefs.append(a.attr("href"))
            return hrefs
        except Exception as e:
            count += 1
            if count == 3:
                return []


def dump(obj, filename):
    fp = open(filename, "wb")
    pickle.dump(obj, fp)
    fp.close()


def load(filename, default):
    if not os.path.exists(filename):
        return default
    fp = open(filename, "rb")
    obj = pickle.load(fp)
    fp.close()
    return obj


def travel(filename="stdout", limit=0):
    queue = load(".queue", [www])
    history = load(".history", set())
    if filename == "stdout":
        fp = sys.stdout
    else:
        fp = open(filename, "w")
    count = 0
    num = 0
    while queue:
        url = queue[-1]
        for href in extractLink(url):
            if href in history:
                continue
            history.add(href)
            if href.startswith("/article/view"):
                fp.write("{}\n".format(www+href))
                count += 1
                if limit != 0 and count >= limit:
                    break
            elif href.startswith("/"):
                queue.append(www+href)
        if limit != 0 and count >= limit:
            break
        num += 1
        if num % 100 == 0:
            dump(queue, ".queue")
            dump(history, ".history")
        queue.pop()
        fp.flush()
    fp.close()
    dump(queue, ".queue")
    dump(history, ".history")


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Example:
    python3 link.py --limit 1
""",
    )
    parser.add_argument("-l", "--limit", default=0,
                        type=int, help="limit links")
    parser.add_argument("-o", "--output", default="stdout",
                        help="output filename")
    args = parser.parse_args()
    travel(args.output, args.limit)


if __name__ == "__main__":
    main()
