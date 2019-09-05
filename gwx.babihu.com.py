#!/usr/bin/env python3

import requests
from pyquery import PyQuery as pq

www = "http://gwx.babihu.com"


def extractLink(url):
    res = requests.get(
        url,
        headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        }
    )
    d = pq(res.text)
    pairs = []
    for a in d("a").items():
        pairs.append((a.text(), a.attr("href")))
    return pairs


def travel():
    hrefs = [www]
    hrefset = set(hrefs)
    fp = open("gwx.babihu.com.txt.1", "w")
    while hrefs:
        url = hrefs[-1]
        for pair in extractLink(url):
            text, href = pair
            if href in hrefset:
                continue
            hrefset.add(href)
            if href.startswith("/dynasty"):
                hrefs.append(www+href)
            if href.startswith("/author"):
                hrefs.append(www+href)
            if href.startswith("/article/view"):
                fp.write("{}\t{}\t{}\n".format(text, www+href, url))
        hrefs.pop()
        fp.flush()
    fp.close()


def main():
    travel()


if __name__ == "__main__":
    main()
