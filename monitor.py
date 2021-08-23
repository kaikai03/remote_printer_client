# coding: utf-8
__author__ = 'kk'

import psutil
import time
# import pynvml
import platform
# from publisher import Publisher
# import json
# import threading

# 最终间隔还需要加上大约3秒的时间（cpu统计和网络统计耗时等）
__publish_report_interval_default__ = 3
__publish_report_interval_max__ = 20

class Monitor:
    """ 速度单位为 bytes/s"""
    def __init__(self, worker=None, interval=1):
        self.worker = worker
        self.cpu_count = Monitor.get_cpu_count()
        self.interval = interval
        self.publish_report_interval = __publish_report_interval_default__
        self.system = platform.system()
        self.platform = platform.platform()
        self.architecture = platform.architecture()
        self.memory_total = psutil.virtual_memory().total
        self.user = psutil.users()[0].name
        self.cpu_name = None
        self.sys_caption = None
        self.sys_path = None
        self.sys_serial = None
        self.disk_caption = None
        self.fan_status = None
        if self.system == 'Windows':
            try:
                import wmi
                w = wmi.WMI()
                self.user = w.Win32_ComputerSystem()[0].UserName
                self.cpu_name = w.Win32_Processor()[0].Name
                self.sys_caption = w.Win32_OperatingSystem()[0].Caption
                self.sys_path = w.Win32_OperatingSystem()[0].WindowsDirectory
                self.sys_serial = w.Win32_OperatingSystem()[0].SerialNumber
                self.disk_caption = w.Win32_DiskDrive()[0].Caption
                self.fan_status = w.Win32_Fan()[0].status
            except Exception as e:
                print(e)

        # if self.worker is None:
        #     self.worker = self.user
        # self.publish = Publisher(self.worker)
        # self.publish_timer = None


    @staticmethod
    def get_cpu_count():
        return psutil.cpu_count()

    def get_cpu_used(self):
        used = psutil.cpu_percent(self.interval, True)
        return {'average': round(sum(used) / self.cpu_count, 2), 'per': used}

    @staticmethod
    def get_memory_used():
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        return {'virtual': Monitor.usage_to_dic(vm),
                'swap': Monitor.usage_to_dic(sm)}

    @staticmethod
    def usage_to_dic(usage):
        ordered_dict = usage._asdict()
        return {key: ordered_dict[key] for key in list(ordered_dict)}

    @staticmethod
    def get_disk_used(device_all=False):
        # false 只监控项目盘
        if device_all:
            return [{i.device: Monitor.usage_to_dic(psutil.disk_usage(i.device))} for i in psutil.disk_partitions(True)]
        else:
            return Monitor.usage_to_dic(psutil.disk_usage("/"))

    def get_disk_io(self, device_all=False):
        # device_all 为 false 时，返回最大的读写速度
        def get_io():
            infos = psutil.disk_io_counters(1).items()
            return [(item[0], item[1].read_bytes, item[1].write_bytes) for item in infos]

        start = get_io()
        time.sleep(self.interval)
        end = get_io()
        results = [{'device_name': item[0], 'read_speed': (item[1] - start[index][1]) / self.interval,
                    'write_speed': (item[2] - start[index][2]) / self.interval} for index, item in enumerate(end)]
        if device_all:
            return results
        else:
            speed_max, index_max = 0, 0
            for index, item in enumerate(results):
                speed = item['read_speed'] + item['write_speed']
                if speed > speed_max:
                    index_max = index
            results_filted = results[index_max]
            del results_filted['device_name']
            return results_filted

    def get_net_io(self):
        def get_io():
            infos = psutil.net_io_counters()
            return infos.bytes_sent, infos.bytes_recv

        start = get_io()
        time.sleep(self.interval)
        end = get_io()
        return {'sent_speed': (end[0] - start[0]) / self.interval,
                'recv_speed': (end[1] - start[1]) / self.interval}

    # @staticmethod
    # def get_gpu_info():
    #     try:
    #         pynvml.nvmlInit()
    #         handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # 这里的0是GPU id
    #         meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
    #         print(meminfo.total)  # 第二块显卡总的显存大小
    #         print(meminfo.used)  # 这里是字节bytes，所以要想得到以兆M为单位就需要除以1024**2
    #         print(meminfo.free)  # 第二块显卡剩余显存大小
    #         print(pynvml.nvmlDeviceGetCount())  # 显示有几块GPU
    #     except Exception as e:
    #         print(e)

    def get_report(self):
        # 未启用线程时，禁止频繁调用
        return {'cpu': self.get_cpu_used(),
                'memory': self.get_memory_used(),
                'disk_used': self.get_disk_used(device_all=False),
                'disk_io': self.get_disk_io(device_all=False),
                'net_io': self.get_net_io(),
                # 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'time': int(round(time.time()*1000))
                }

    def get_base_info(self):
        infos = {'system': self.system,
                 'platform': self.platform,
                 'architecture': self.architecture,
                 'cpu_cores': self.cpu_count,
                 'memory_total': self.memory_total,
                 }
        if self.system == 'Windows' and (self.cpu_name is not None):
            infos['user'] = self.user
            infos['cpu_name'] = self.cpu_name
            infos['sys_caption'] = self.sys_caption
            infos['sys_path'] = self.sys_path
            infos['sys_serial'] = self.sys_serial
            infos['disk_caption'] = self.disk_caption
            infos['fan_status'] = self.fan_status
        return infos

    # def publish_report_start(self):
    #     report = json.dumps(self.get_report())
    #     self.publish.publish_long(report)
    #     self.publish_timer = threading.Timer(self.publish_report_interval,
    #                                          self.publish_report_start)
    #     self.publish_timer.start()
    #     print("send")

    # def publish_report_stop(self):
    #     while self.publish_timer.is_alive():
    #         self.publish_timer.cancel()
    #         self.publish_timer.cancel()

    # TODO:补充动态publish间隔的功能，websock做完后
    #  （因为这个类会独立出去，放到celery的工程中，所以
    #  后台需要多加个有活跃访问的接口来实现动态推送，同时这个接口也可以作为celery在线的心跳）


# m = Monitor()
# m.publish_report_start()
#
# m.publish_report_stop()
# m.publish.conn_close()
#
# m.publish.publish_temp(json.dumps(m.get_base_info()))
# m.publish.publish_long("111")
#
# m.publish_timer.is_alive()

# json.dumps(m.get_base_info())
# m.get_report()