#!/usr/bin/env python3

import argparse
import pymysql
import sys
import json

config = {
    "mysqldb": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "hatlonely",
        "password": "keaiduo1",
        "db": "hads"
    },
}

conn = pymysql.connect(
    host=config["mysqldb"]["host"],
    user=config["mysqldb"]["user"],
    port=config["mysqldb"]["port"],
    password=config["mysqldb"]["password"],
    db=config["mysqldb"]["db"],
    charset="utf8",
    cursorclass=pymysql.cursors.DictCursor
)


def insert(output="stdout"):
    if output == "stdout":
        ofp = sys.stdout
    else:
        ofp = open(output, "w")

    limit = 1000
    offset = 0
    with conn.cursor() as cursor:
        while True:
            cursor.execute("""SELECT * FROM ancients LIMIT {} OFFSET {}""".format(
                limit, offset
            ))
            objs = cursor.fetchall()
            for obj in objs:
                ofp.write("{}\n".format(json.dumps(obj)))
            if len(objs) == 0:
                break
            offset += limit
            ofp.flush()
    ofp.close()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Example:
    python3 dump.py
""")
    parser.add_argument("-o", "--output", default="stdout",
                        help="output filename")
    args = parser.parse_args()
    insert(args.output)


if __name__ == "__main__":
    main()
