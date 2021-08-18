# -*- coding:utf-8 -*-
__author__ = 'kk'

import websocket
import time
import printer

__server_host__ = "ws://192.168.1.21:11303/"
__base_flag__ = '#//'
__ping_flag__ = 'ping#//'

__print_flag__ = 'printOrder#//'

__return_flag__ = 'return#//'
__print_success_base__ = (__return_flag__ + 'PrintSuccess_%s')
__print_error_base__ = (__return_flag__ + 'PrintError_%s')
__pong_base__ = __return_flag__ + 'Pong_%s'

reconnect_count = 0


def pong(ws, msg):
    ws.send(__pong_base__ % msg)


def flag_clean(msg):
    return msg.split(__base_flag__)[1]


def ws_connection(ws_protocol_addr):
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
        printer.print_report(addr)
        pass

    if __ping_flag__ in msg:
        pong(ws, flag_clean(msg))


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
            type(error) == ConnectionResetError:
        print('正在尝试第%d次重连' % reconnect_count)
        reconnect_count += 1
        if reconnect_count < 65535:
            if reconnect_count<5:
                time.sleep(2)
            else:
                time.sleep(10)
            ws_connection(__server_host__)

    else:
        print('其他error!，中止服务')


def on_close(ws, code, msg):
    print("### closed ###", code, msg)


def on_open(ws):
    ws.send('login#//%s' % '193.QQ')
    global reconnect_count
    reconnect_count = 0


if __name__ == "__main__":
    if not printer.printer_check():
        raise Exception('启动失败')

    ws_connection(__server_host__)
