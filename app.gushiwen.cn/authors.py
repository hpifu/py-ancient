#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import redis
import random
import argparse
import requests
import logging
import logging.config


config = {
    'redis': {
        'host': os.getenv('REDIS_HOST', '127.0.0.1'),
        'port': int(os.getenv('REDIS_PORT', '6379')),
        "password": os.getenv('REDIS_PASSWORD', ''),
    },
}

rds_cli = redis.Redis(
    host=config['redis']['host'],
    port=config['redis']['port'],
    db=0,
    password=config['redis']['password'],
    decode_responses=True
)


def analyse_response(fp, dynasty, page, authors, data):
    items = data.get('authors', [])
    new_cnt = 0
    exists_cnt = 0
    for item in items:
        s_id = item.get('id', 0)
        if s_id == 0:
            # 对方可能返回的垃圾信息
            logging.warning('unexpect id in {0} page {1}, item {2}'.format(dynasty, page, json.dumps(item)))
            continue

        exists = rds_cli.hget(authors, s_id)
        if exists is not None:
            # 在其它page出现过了
            exists_cnt += 1
            continue

        item['chaodai'] = dynasty
        item['page'] = page
        value = json.dumps(item)
        res = rds_cli.hset(authors, s_id, value)
        if res == 1:
            new_cnt += 1
        else:
            logging.warning('rds set {0} page {1} id {2} failed, item {3}'.format(dynasty, page, s_id, value))
        fp.write('{0}\n'.format(value))
    return new_cnt, exists_cnt


def run(fp):
    # 爬取接口和参数
    url = 'https://app.gushiwen.cn/api/author/Default.aspx'
    token = 'gswapi'
    dynasties = ['先秦', '两汉', '魏晋', '南北朝', '隋代', '唐代',
                 '五代', '宋代', '金朝', '元代', '明代', '清代']
    crawed_set = 'crawed_dynasty_pages'
    author_set = 'author_ids'

    for dynasty in dynasties:
        page = 1
        run_flag = True
        while run_flag:
            # 已经抓取过了
            key = '{0}_{1}'.format(dynasty, page)
            crawed = rds_cli.sismember(crawed_set, key)
            if crawed:
                page += 1
                continue

            # 请求
            logging.info('crawing {0} page {1}'.format(dynasty, page))
            response = requests.get(url, params={'c': dynasty, 'token': token, 'page': page})
            if response.status_code != 200:
                logging.error('crawing page {0} failed, error: {1}'.format(page, response.text))
                run_flag = False
                continue

            # 解析存储
            data = response.json()
            cnt, exists_cnt = analyse_response(fp, dynasty, page, author_set, data)
            if cnt == 0 and exists_cnt == 0:
                run_flag = False
                continue
            else:
                logging.info('crawing {0} page {1} new count {2}, exists cnt {3}'.format(dynasty, page, cnt, exists_cnt))
                rds_cli.sadd(crawed_set, page)
                fp.flush()
                page += 1
            time.sleep(random.uniform(3, 5))


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Example:
        python3 authors.py
    """)
    parser.add_argument('-log', '--logging', help='日志配置', default='logging.conf')
    # parser.add_argument("-i", "--input", default="stdin", help="input filename")
    parser.add_argument("-o", "--output", default="stdout", help="output filename")
    args = parser.parse_args()

    if args.logging:
        os.makedirs('log', exist_ok=True)
        logging.config.fileConfig(args.logging)

    if args.output == 'stdout':
        ofp = sys.stdout
    else:
        ofp = open(args.out, 'w+')

    run(ofp)
    ofp.close()


if __name__ == "__main__":
    main()
