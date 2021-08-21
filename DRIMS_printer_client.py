# -*- coding:utf-8 -*-
__author__ = 'kk'

import websocket
import time
import printer
import configparser
import re
import logger

__version__ = '210820'
__config_version__ = '210819'
__chrome_version__ = '92.0.4515.159'


__base_flag__ = '#//'
__ping_flag__ = 'ping#//'

__print_flag__ = 'printOrder#//'

__return_flag__ = 'return#//'
__print_success_base__ = (__return_flag__ + 'PrintSuccess_%s')
__print_error_base__ = (__return_flag__ + 'PrintError_%s')
__pong_base__ = __return_flag__ + 'Pong_%s'

__ban_flag__ = 'fuckoff#//'


__ini_example__ = """************************************
**config.ini file EXAMPLE:
**   [server]
**   host=192.168.1.21
**   port=11303
**   protocol=ws
**   [client]
**   printerid=1
**   printername=QQQQ
**   hospitalid=1
**   hospitalname=1
**   remoteip=
**   dsc=
*********************************************"""

banned = False
reconnect_count = 0
server_host = None
printer_id = None
printer_name = None
hospital_id = None
hospital_name = None


def flag_clean(msg):
    return msg.split(__base_flag__)[1]


def send_pong(ws, msg):
    ws.send(__pong_base__ % msg)


def send_print_success(ws, msg):
    ws.send(__print_success_base__ % msg)


def send_print_error(ws, code, msg):
    if code == -1:
        # '访问页面链路建立失败'
        ws.send(__print_error_base__ % '访问页面链路建立失败:'+str(msg))
        return

    if code < -100:
        # 'http code 非200错误'
        ws.send(__print_error_base__ % 'http status_code('+str(code)+'):'+str(msg))
        return

    if code == -2:
        # '打印页面内容加载超时'
        ws.send(__print_error_base__ % '打印页面内容加载超时:'+str(msg))
        return

    if code == -3:
        # '打印iframe内容加载超时'
        ws.send(__print_error_base__ % '打印iframe内容加载超时:' + str(msg))
        return

    ws.send(__print_error_base__ % 'unknown error:' + str(msg))


def ws_connection(ws_protocol_addr):
    if banned:
        # 被禁止使用，停止自动重连
        return
    websocket.enableTrace(True)
    host = ws_protocol_addr
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


def on_message(ws, msg):
    print('get msg:', msg)
    if not (__base_flag__ in msg):
        print('command error')
        return

    if __print_flag__ in msg:
        addr = flag_clean(msg)
        print('打印地址:', addr)
        find_send_id = re.compile(r'sendId=\d+').findall(msg)
        send_id = 0
        if len(find_send_id) > 0:
            send_id = find_send_id[0].replace('sendId=', '')

        ret_code = printer.print_report(addr)
        if ret_code == 1:
            # '打印成功'
            send_print_success(ws,send_id)

        if ret_code <= 0:
            # '打印失败'
            send_print_error(ws, ret_code, send_id)

    if __ping_flag__ in msg:
        send_pong(ws, flag_clean(msg))

    if __ban_flag__ in msg:
        global banned
        print(flag_clean(msg))
        banned = True


def on_error(ws, error):
    print(error)
    print(type(error))
    global reconnect_count

    try:
       ws_error_flag = ws._exceptions.WebSocketConnectionClosedException
    except Exception :
        ws_error_flag = None

    if type(error) == ConnectionRefusedError or \
            type(error) == ws_error_flag or \
            type(error) == ConnectionResetError or \
            type(error) == TimeoutError or \
            type(error) == ConnectionAbortedError or \
            type(error) == ConnectionError or \
            type(error) == BrokenPipeError:
        print('正在尝试第%d次重连' % reconnect_count)
        reconnect_count += 1
        if reconnect_count < 65535:
            if reconnect_count < 5:
                time.sleep(2)
            else:
                time.sleep(10)
            ws_connection(server_host)

    else:
        print('其他error!，中止服务')


def on_close(ws, code, msg):
    print("### closed ###", code, msg)


def on_open(ws):
    ws.send('login#//%s' % printer_name)
    global reconnect_count
    reconnect_count = 0


def load_configur():
    cf = configparser.ConfigParser()
    cf.read("./config.ini",encoding='utf-8')
    secs = cf.sections()

    if len(secs) == 0:
        print('请检查./config.ini 存在， 并确保格式正确')
        print(__ini_example__)
        raise Exception('config.ini error')

    protocol = cf.get("server", "protocol")
    if protocol.lower() not in ['websocket','ws']:
        raise Exception('请检查./config.ini的protocol字段, 当前服务仅仅支持websocket协议，example：ws 或 websocket')

    global server_host, printer_id, printer_name, hospital_id, hospital_name

    try:
        server_host = "ws://"+cf.get("server", "host")+':'+cf.get("server", "port")
        printer_id = cf.get("client", "printerid")
        printer_name = cf.get("client", "printername")
        hospital_id = cf.get("client", "hospitalid")
        hospital_name = cf.get("client", "hospitalname")
    except Exception as e:
        print('请检查./config.ini 确保格式正确')
        print(__ini_example__)
        raise Exception('config.ini error')


if __name__ == "__main__":
    logger.start_log()
    if not printer.printer_check():
        raise Exception('启动失败')

    load_configur()

    print('本体版本：', __version__)
    print('配置版本：', __config_version__)
    print('chrome最优版本：', __chrome_version__)

    ws_connection(server_host)

