#!/usr/bin/env python3

import sys
import requests
import json
import argparse
import re
from pyquery import PyQuery as pq
import mmh3


def murmur3_64(text):
    val, _ = mmh3.hash64(text)
    return val if val >= 0 else val + 2**64


def analyst(url):
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
            title = d("div.h_bar h2").text()
            infos = d("div#msg_con p span").text().split(
                "┋")[0].split(":")[-1].strip().split("·")
            dynasty = infos[0]
            author = infos[-1]
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
        except Exception as e:
            count += 1
            if count == 3:
                return None


def serialize(input="stdin", output="stdout", limit=0):
    if input == "stdin":
        ifp = sys.stdin
    else:
        ifp = open(input)
    if output == "stdout":
        ofp = sys.stdout
    else:
        ofp = open(output, "w")
    count = 0
    for url in ifp:
        infos = analyst(url)
        if not infos:
            continue
        title, dynasty, author, content = infos
        content = re.sub('[ \u00a0\u0020\u3000]+', ' ', content)
        content = re.sub('[\n\r]+', '\n', content)
        val = "".join([c for c in content if c not in set(
            [c for c in " \t\n\r，、。；《》“”\"\"''"]
        )])
        ofp.write("{}\n".format(json.dumps({
            "url": url[:-1],
            "id": murmur3_64(val) % (2**63 - 1),
            "title": title,
            "dynasty": dynasty,
            "author": author,
            "content": content,
        })))
        ofp.flush()
        count += 1
        if limit != 0 and count >= limit:
            break
    ofp.close()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Example:
    python3 data.py --limit 1
""")
    parser.add_argument("-l", "--limit", default=0,
                        type=int, help="limit links")
    parser.add_argument("-o", "--output", default="stdout",
                        help="output filename")
    parser.add_argument("-i", "--input", default="stdin",
                        help="input filename")
    args = parser.parse_args()
    serialize(args.input, args.output, args.limit)


if __name__ == "__main__":
    main()
