#!/usr/bin/env python3

import sys
import requests
from pyquery import PyQuery as pq


def analyst(url):
    res = requests.get(
        url,
        headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        }
    )
    d = pq(res.text)
    title = d("div.h_bar h2").text()
    infos = d("div#msg_con p span a").text().split("·")
    dynasty = infos[0]
    author = infos[1]
    count = 0
    lines = []
    for p in d("div#msg_con p").items():
        count += 1
        if count == 1:
            continue
        if p.attr("class") == "pay_bg":
            break
        lines.append(p.text())
    content = "\n".join(lines)
    return (title, dynasty, author, content)


def main():
    for url in sys.stdin:
        title, dynasty, autor, content = analyst(url)
        print("=====================================")
        print(url[:-1])
        print(title)
        print(dynasty)
        print(autor)
        print(content)


if __name__ == "__main__":
    main()
