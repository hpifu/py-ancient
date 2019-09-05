#!/usr/bin/env python3

import requests
from pyquery import PyQuery as pq


www = "https://so.gushiwen.org/shiwen"


def getPage(url):
    res = requests.get(
        url,
        headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        }
    )
    return res.text


def analyst(text):
    d = pq(text)

    shis = []
    sons = d("div.sons")
    for son in sons.items():
        name = son("p b").text()
        if not name:
            continue
        infos = list(son("p.source a").items())
        dynasty = infos[0].text()
        author = infos[1].text()
        content = son("div.contson").text()
        tags = son("div.tag a").text()
        shis.append({
            "name": name,
            "dynasty": dynasty,
            "author": author,
            "tags": tags,
            "content": content,
        })

    next = d("div.pagesright a.amore").attr("href")
    return shis, next


def main():
    print(analyst(getPage(www+"/default_4A111111111111A1.aspx")))


if __name__ == '__main__':
    main()
