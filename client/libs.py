# -*- coding: utf-8 -*-
# @Time    : 2019/4/22 下午1:05
# @Author  : yu_hsuan_chen@trendmicro.com
# @File    : LINES
# @Version : 3.6
import datetime
import re
import sqlite3
from enum import Enum


class DSMSystemPatterns(Enum):
    TIMEFORMAT = "(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?) (?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9]), [1-2][0-9]\d{2} (?:2[0123]|[01]?[0-9]):(?:[0-5][0-9]):(?:(?:[0-5][0-9]|60)(?:[:.,][0-9]+)?) [pP|aA][mM] \[[+-][0-1][0-9]\d+\]"
    JAVACLASS = "(?:[a-zA-Z0-9-]+\.)+[A-Za-z0-9$]+"
    JAVAFUNCTION = "(?:[A-Za-z0-9_.-]+)"
    LOGLEVEL = "([A-a]lert|ALERT|[T|t]race|TRACE|[D|d]ebug|DEBUG|[N|n]otice|NOTICE|[I|i]nfo|INFO|[W|w]arn?(?:ing)?|WARN?(?:ING)?|[E|e]rr?(?:or)?|ERR?(?:OR)?|[C|c]rit?(?:ical)?|CRIT?(?:ICAL)?|[F|f]atal|FATAL|[S|s]evere|SEVERE|EMERG(?:ENCY)?|[Ee]merg(?:ency)?)"
    LOGDATA = ".*"


class ErrorPatterns(Enum):
    HOST_ERROR = "Host Object not found"
    HELLO_ERROR = "Host Object"


class SingleErrorPatterns(object):
    def __init__(self):
        print("init SingleErrorPatterns")
        self.pattern = []

    def get_pattern(self):
        conn = sqlite3.connect('logparser.db')
        db = conn.cursor()
        pattern_rows = db.execute('SELECT id, pattern, priority, log_type, owner FROM single_pattern')
        pattern = {}
        for pattern_row in pattern_rows:
            pattern['id'] = pattern_row[0]
            pattern['pattern'] = pattern_row[1]
            pattern['priority'] = pattern_row[2]
            pattern['log_type'] = pattern_row[3]
            pattern['owner'] = pattern_row[4]
            self.pattern.append(pattern)


class SinglePatternFinder(object):
    # get patterns
    def __init__(self):
        print("init SinglePatternFinder")
        self.patterns = [e.value for e in ErrorPatterns]

    def parse_log(self, raw_log):
        for i in self.patterns:
            res = re.search(i, raw_log)
            if res:
                return res.group()


class LogPage(object):
    def __init__(self, file_name, patterns):
        with open(file_name, 'r') as f:
            raw_logs = f.readlines()
        self.lines = []
        self.total_lines = len(raw_logs)
        self.patterns = patterns
        line_group = 0
        line_number = 1

        for i in raw_logs:
            if re.match(DSMSystemPatterns.TIMEFORMAT.value, i):
                line_group = line_group + 1
            self.__add_line(line_number, i, line_group, self.patterns)
            line_number = line_number + 1
        self.line_group = line_group

    def __add_line(self, line_number, raw_log, line_group, patterns):
        log_line = LogLine(line_number, raw_log, line_group, patterns)
        self.lines.append(log_line)

    def get_group(self, group_number):
        result = []
        for i in range(self.total_lines):
            if self.lines[i].group == group_number:
                result.append(self.lines[i])
            if self.lines[i].group > group_number:
                break
        return result

    def get_group_info(self, group_number, attribute=None):
        result = []
        information = []
        for i in range(self.total_lines):
            if self.lines[i].group == group_number:
                result.append(self.lines[i])
            if self.lines[i].group > group_number:
                break

        for i in result:
            information.append(i.info)
        temp = self.__merge_dicts(information)

        if attribute is None:
            return temp
        else:
            return temp[attribute]

    def __merge_dicts(self, dict_args):
        result = {
            'timestamp': "",
            'class_name': "",
            'class_function': "",
            'group': "",
            'hit_pattern': "",
            'log_level': "",
            'log_data': []
        }

        log_data = []
        hit_pattern = []
        hit_pattern_id = []
        for dictionary in dict_args:
            for key in dictionary.keys():
                if key == "hit_pattern":
                    if dictionary['hit_pattern'] != None:
                        hit_pattern = dictionary['hit_pattern']
                        hit_pattern_id = dictionary['hit_pattern_id']
                if key == "log_data":
                    log_data.append(dictionary[key])
                result[key] = dictionary[key]
        result['hit_pattern'] = hit_pattern
        result['hit_pattern_id'] = hit_pattern_id
        result['log_data'] = '\n'.join(str(e) for e in log_data)
        return result

    def get_parsing_result(self):
        result = []
        for i in range(self.line_group + 1):
            if self.get_group_info(i, 'hit_pattern'):
                result.append(self.get_group_info(i))
        return result


class LogLine(object):
    def __init__(self, line_number, raw_log, group, patterns):
        self.line_number = line_number
        self.raw_log = raw_log
        self.group = group
        self.info = {}
        self.__extract_info()
        self.info['group'] = group
        res = self.__parse_log(raw_log, patterns)

        if res is not None:
            self.info['hit_pattern'] = res[0]
            self.info['hit_pattern_id'] = res[1]

    def __extract_info(self):
        TIMEFORMAT = "(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?) (?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9]), [1-2][0-9]\d{2} (?:2[0123]|[01]?[0-9]):(?:[0-5][0-9]):(?:(?:[0-5][0-9]|60)(?:[:.,][0-9]+)?) [pP|aA][mM] \[[+-][0-1][0-9]\d+\]"
        JAVACLASS = "(?:[a-zA-Z0-9-]+\.)+[A-Za-z0-9$]+"
        JAVAFUNCTION = "(?:[A-Za-z0-9_.-]+)"
        LOGLEVEL = "([A-a]lert|ALERT|[T|t]race|TRACE|[D|d]ebug|DEBUG|[N|n]otice|NOTICE|[I|i]nfo|INFO|[W|w]arn?(?:ing)?|WARN?(?:ING)?|[E|e]rr?(?:or)?|ERR?(?:OR)?|[C|c]rit?(?:ical)?|CRIT?(?:ICAL)?|[F|f]atal|FATAL|[S|s]evere|SEVERE|EMERG(?:ENCY)?|[Ee]merg(?:ency)?)"
        LOGDATA = ".*"
        time_line = re.match("({TIMEFORMAT}) ({JAVACLASS}) ({JAVAFUNCTION})"
                             .format(TIMEFORMAT=TIMEFORMAT, JAVACLASS=JAVACLASS, JAVAFUNCTION=JAVAFUNCTION),
                             self.raw_log)
        log_line_level = re.match("{LOGLEVEL}: ({LOGDATA})".format(LOGLEVEL=LOGLEVEL, LOGDATA=LOGDATA), self.raw_log)
        log_line = re.match("^(?!.*{LOGLEVEL}:){LOGDATA}".format(LOGLEVEL=LOGLEVEL, LOGDATA=LOGDATA), self.raw_log)

        if time_line:
            self.info['timestamp'] = datetime.datetime.strptime(time_line.group(1),
                                                                '%b %d, %Y %I:%M:%S.%f000 %p [%z]').strftime(
                '%Y-%m-%d %H:%M:%S.%f')
            self.info['class_name'] = time_line.group(2)
            self.info['class_function'] = time_line.group(3)
        elif log_line_level:
            self.info['log_level'] = log_line_level.group(1)
            self.info['log_data'] = log_line_level.group(2)
        elif log_line:
            self.info['log_data'] = log_line.group()

    def __parse_log(self, raw_log, patterns):
        patterns_id = patterns['id'].values.tolist()
        patterns = patterns['pattern'].values.tolist()
        patterns_size = len(patterns)

        hit_patterns_id = []
        hit_patterns = []

        for i in range(patterns_size):
            res = re.search(patterns[i], raw_log)
            if res:
                hit_patterns.append(res.group())
                hit_patterns_id.append(patterns_id[i])

        if len(hit_patterns) > 0:
            return hit_patterns, hit_patterns_id
