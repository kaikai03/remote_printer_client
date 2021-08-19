# -*- coding:utf-8 -*-
__author__ = 'kk'

import sys
import os
import time

stdout_tmp = None
__log_file_path__ = './log_file/'
__log_postfix__ = '.log'

def start_log():
    global stdout_tmp
    stdout_tmp = sys.stdout
    sys.stdout = Logger()


def stop_log():
    global stdout_tmp
    sys.stdout = stdout_tmp

def create_dir_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)

def get_cur_time():
    return time.strftime('%Y%m%d', time.localtime(time.time()))

class Logger(object):
    def __init__(self):
        create_dir_not_exist(__log_file_path__)
        self.terminal = sys.stdout
        self.date_str = get_cur_time()
        self.log = open(__log_file_path__+self.date_str+__log_postfix__, "w")

    def write(self, message):
        if self.date_str != get_cur_time():
            self.log.close()
            self.date_str = get_cur_time()
            self.log = open(__log_file_path__ + self.date_str + __log_postfix__, "w")

        self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):
        self.log.flush()

