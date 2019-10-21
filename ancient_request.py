#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import redis
import random
import requests
import logging
import logging.config


def analyse_response(rds, page, key, data):
    items = data.get(key, [])
    new_cnt = 0
    exists_cnt = 0
    for item in items:
        s_id = item.get('id', 0)
        if s_id == 0:
            # 对方可能返回的垃圾信息
            logging.warning('unexpect id in page {0}, item {1}'.format(page, json.dumps(item)))
            continue

        exists = rds.exists(s_id)
        if exists == 1:
            # 在其它page出现过了
            exists_cnt += 1
            continue

        value = json.dumps(item)
        res = rds.set(s_id, value)
        if res:
            new_cnt += 1
        else:
            logging.warning('rds set page {0} id {1} failed, item {2}'.format(page, s_id, value))
    return new_cnt, exists_cnt


def main():
    logging_file = os.getenv('LOGGING_CONF', 'conf/logging.conf')
    os.makedirs('log', exist_ok=True)
    logging.config.fileConfig(logging_file)

    # 非必要的信息放在环境变量里
    url = os.getenv('BASE_URL', '')
    token = os.getenv('TOKEN', '')
    json_key = os.getenv('KEY', '')

    redis_host = os.getenv('REDIS_HOST', '127.0.0.1')
    redis_port = int(os.getenv('REDIS_PORT', '6379'))
    redis_password = os.getenv('REDIS_PASSWORD', '')
    rds_cli = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_password, decode_responses=True)

    crawed_pages = 'crawed_pages'
    page = 1
    run_flag = True
    while run_flag:
        # 已经抓取过了
        crawed = rds_cli.sismember(crawed_pages, page)
        if crawed:
            page += 1
            continue

        # 请求
        logging.info('crawing page {0}'.format(page))
        response = requests.post(url, data={'tstr': '', 'token': token, 'page': page})
        if response.status_code != 200:
            logging.error('crawing page {0} failed, error: {1}'.format(page, response.text))
            run_flag = False
            continue

        # 解析存储
        data = response.json()
        cnt, exists_cnt = analyse_response(rds_cli, page, json_key, data)
        if cnt == 0 and exists_cnt == 0:
            run_flag = False
            continue
        else:
            logging.info('crawing page {0} new count {1}, exists cnt {2}'.format(page, cnt, exists_cnt))
            rds_cli.sadd(crawed_pages, page)
            page += 1
        time.sleep(random.uniform(3, 5))


if __name__ == "__main__":
    main()
