# -*- coding: utf-8 -*-
# @Time    : 2019/4/30 下午3:11
# @Author  : yu_hsuan_chen@trendmicro.com
# @File    : pattern_handler
# @Version : 3.6
from configparser import ConfigParser

import requests
import sqlite3
import pandas as pd


def load_configuration():
    cfg = ConfigParser()
    cfg.read('system.ini')
    return cfg


def download_db(url):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open('logparser.db', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    # f.flush()


class SingleErrorPatterns(object):
    def __init__(self):
        print("init SingleErrorPatterns")

    def get_pattern(self):
        conn = sqlite3.connect('logparser.db')
        df = pd.read_sql_query("SELECT * FROM simple_pattern WHERE enable = 'true';", conn)
        print("Patterns:\n %s" % df)
        return df
