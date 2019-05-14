# -*- coding: utf-8 -*-
# @Time    : 2019/4/19 上午11:28
# @Author  : yu_hsuan_chen@trendmicro.com
# @File    : parser
# @Version : 3.6
from libs import LogPage, SinglePatternFinder
import pattern_handler
import sqlite3
import sys
import os

ERROR_MESSAGE = "Please input correct type and file."


def main():
    if len(sys.argv) == 3:
        execute_type = sys.argv[1]
        execute_file = sys.argv[2]

        if execute_type == "zip":
            if os.path.exists(execute_file):
                if os.path.isfile(execute_file) and "zip" in os.path.basename(execute_file):
                    pass
                else:
                    print(ERROR_MESSAGE)
            else:
                print(ERROR_MESSAGE)
        elif execute_type == "folder":
            if os.path.exists(execute_file):
                pass
            else:
                print(ERROR_MESSAGE)
        elif execute_file == "file":
            if os.path.exists(execute_file):
                pass
            else:
                print(ERROR_MESSAGE)
        else:
            print(ERROR_MESSAGE)
    else:
        print(ERROR_MESSAGE + "\nparser.py [zip/folder/file] [path]")


def sql():
    conn = sqlite3.connect('logparser.db')
    db = conn.cursor()
    res = db.execute('SELECT id, pattern, priority, log_type, owner FROM single_pattern')


def run():
    cfg = pattern_handler.load_configuration()
    pattern_handler.download_db(cfg['Default']['database'])

    # extra patterns
    patterns = pattern_handler.SingleErrorPatterns().get_pattern()
    # load files
    page = LogPage("server1.log", patterns)
    print(page.get_parsing_result())


def run2():
    cfg = pattern_handler.load_configuration()
    pattern_handler.download_db(cfg['Default']['database'])

    # extra patterns
    patterns = pattern_handler.SingleErrorPatterns().get_pattern()
    # load files
    page = LogPage("server0.log", patterns)
    page.line_group
    print(page.line_group)

    for i in range(1,page.line_group+1):
        print(page.get_group_info(i, "log_data"))


if __name__ == "__main__":
    run()
    run2()