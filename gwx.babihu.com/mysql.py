#!/usr/bin/env python3

import argparse
import pymysql
import sys
import json

config = {
    "mysqldb": {
        "host": "test-mysql",
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


def insert(input="stdin"):
    if input == "stdin":
        ifp = sys.stdin
    else:
        ifp = open(input)

    for line in ifp:
        obj = json.loads(line[:-1])
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO ancients (id, title, author, dynasty, content)
            VALUES ({id}, '{title}', '{author}', '{dynasty}', '{content}')
            ON DUPLICATE KEY UPDATE id=id
            """.format(**obj))
        conn.commit()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Example:
    python3 mysql.py
""")
    parser.add_argument("-i", "--input", default="stdin",
                        help="input filename")
    args = parser.parse_args()
    insert(args.input)


if __name__ == "__main__":
    main()
