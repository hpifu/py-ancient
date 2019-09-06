#!/usr/bin/env python3

import json


def main():
    obj = {}
    content = ""
    count = 0
    for line in open("data.txt"):
        if line.startswith("====================================="):
            obj["content"] = content
            if "title" in obj and not obj["title"].startswith("xxxxxxxxxxxxxx"):
                print(json.dumps(obj))
            count = 0
            content = ""
            continue
        count += 1
        if count == 1:
            obj["link"] = line[:-1]
        elif count == 2:
            obj["title"] = line[:-1]
        elif count == 3:
            obj["dynasty"] = line[:-1]
        elif count == 4:
            obj["author"] = line[:-1]
        else:
            content += line


if __name__ == "__main__":
    main()
