# -*- coding:utf-8 -*-
__author__ = 'kk'

from selenium import webdriver
import time
import os.path
import requests


def printer_check():
    try:
        driver_path = r"./driver.exe"
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(driver_path, options=options)
        driver.maximize_window()
        driver.set_page_load_timeout(10)
        driver.set_script_timeout(10)
        driver.implicitly_wait(10)
        driver.quit()
    except Exception as e:
        print("驱动检查失败，考虑chrome浏览器未安装，或当前文件夹内驱动程序（driver.exe）丢失")
        print(e)
        return False
    return True


def print_report(report_addr):
    try:
        response = requests.get(report_addr)
    except Exception as e:
        print('打印地址访问失败：', e)
        return -1

    if response.status_code != 200:
        return response.status_code * -1

    print("打印进程%d已启动" % os.getpid())

    retry_count = 0

    driver_path = r"./driver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(driver_path, options=options)
    driver.maximize_window()

    driver.set_page_load_timeout(10)
    driver.set_script_timeout(10)
    driver.implicitly_wait(10)

    try:
        driver.get(report_addr)
    except Exception as e:
        print(e)
        driver.quit()
        return -1

    while driver.execute_script("return document.getElementById('complete')?false:true"):
        print('wait complete')
        time.sleep(0.5)
        retry_count +=1
        if retry_count > 150:
            print('打印页面加载超时')
            driver.quit()
            return -2

    retry_count = 0
    print(driver.execute_script("printScale()"))

    while driver.execute_script("return document.getElementById('completeTwo')?false:true"):
        print('wait completeTwo')
        time.sleep(0.5)
        retry_count += 1
        if retry_count > 150:
            print('打印iframe加载超时')
            driver.quit()
            return -3

    time.sleep(3)
    driver.quit()
    print('打印完成')
    return 1


if __name__ == '__main__':
    print_report(
        'https://test.drims1.cn/view/preciousBaby/scale/rd_print.jsp?&tableName=rd_scale_physical&tableDesc=体格生长&itemId=309&detailId=4313&printReporter=吕&printReporterId=3&printSign=8b3de1aa14e8453284f96b8333e01c9c&sendId=2119&visNo=A368&isprint=undefined&growPrint=true')

