# -*- coding:utf-8 -*-
__author__ = 'kk'

import sys
import os
import time
import zipfile

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


def packet_log(date_s):
    file_name = date_s + __log_postfix__
    log_f_full = __log_file_path__+date_s+__log_postfix__
    try:
        if os.path.exists(log_f_full):
            log_z = zipfile.ZipFile(__log_file_path__ + date_s + ".zip",'w')
            log_z.write(log_f_full, file_name)
            log_z.close()
            os.remove(log_f_full)
    except Exception as e:
        print(e)
        print('压缩日志失败：', log_f_full)


class Logger(object):
    def __init__(self):
        create_dir_not_exist(__log_file_path__)
        self.terminal = sys.stdout
        self.date_str = get_cur_time()
        self.log = open(__log_file_path__+self.date_str+__log_postfix__, "a")

    def write(self, message):
        if self.date_str != get_cur_time():
            self.log.close()
            packet_log(self.date_str)
            self.date_str = get_cur_time()
            self.log = open(__log_file_path__ + self.date_str + __log_postfix__, "a")

        self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):
        self.log.flush()



