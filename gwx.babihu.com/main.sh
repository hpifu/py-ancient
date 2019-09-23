#!/usr/bin/env bash

python3 link.py | python3 data.py | python3 mysql.py | python3 es.py > data.txt
