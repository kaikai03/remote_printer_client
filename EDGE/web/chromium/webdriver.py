
from typing import NoReturn
from EDGE.web.common.options import BaseOptions
from EDGE.web.common.service import Service
from EDGE.web.chrome.options import Options as ChromeOptions
import warnings

from EDGE.web.chromium.remote_connection import ChromiumRemoteConnection
from EDGE.web.remote.webdriver import WebDriver as RemoteWebDriver

DEFAULT_PORT = 0
DEFAULT_SERVICE_LOG_PATH = None
DEFAULT_KEEP_ALIVE = None


class ChromiumDriver(RemoteWebDriver):

    def __init__(self, browser_name, vendor_prefix,
                 port=DEFAULT_PORT, options: BaseOptions = None, service_args=None,
                 desired_capabilities=None, service_log_path=DEFAULT_SERVICE_LOG_PATH,
                 service: Service = None, keep_alive=DEFAULT_KEEP_ALIVE):
       
        if desired_capabilities:
            warnings.warn('desired_capabilities has been deprecated, please pass in a Service object',
                          DeprecationWarning, stacklevel=2)
        if port != DEFAULT_PORT:
            warnings.warn('port has been deprecated, please pass in a Service object',
                          DeprecationWarning, stacklevel=2)
        self.port = port
        if service_log_path != DEFAULT_SERVICE_LOG_PATH:
            warnings.warn('service_log_path has been deprecated, please pass in a Service object',
                          DeprecationWarning, stacklevel=2)
        if keep_alive != DEFAULT_KEEP_ALIVE and type(self) == __class__:
            warnings.warn('keep_alive has been deprecated, please pass in a Service object',
                          DeprecationWarning, stacklevel=2)
        else:
            keep_alive = True

        self.vendor_prefix = vendor_prefix

        _ignore_proxy = None
        if not options:
            options = self.create_options()

        if desired_capabilities:
            for key, value in desired_capabilities.items():
                options.set_capability(key, value)

        if options._ignore_local_proxy:
            _ignore_proxy = options._ignore_local_proxy

        if not service:
            raise AttributeError('service cannot be None')

        self.service = service
        self.service.start()

        try:
            RemoteWebDriver.__init__(
                self,
                command_executor=ChromiumRemoteConnection(
                    remote_server_addr=self.service.service_url,
                    browser_name=browser_name, vendor_prefix=vendor_prefix,
                    keep_alive=keep_alive, ignore_proxy=_ignore_proxy),
                options=options)
        except Exception:
            self.quit()
            raise
        self._is_remote = False

    def launch_app(self, id):
        
        return self.execute("launchApp", {'id': id})

    def get_network_conditions(self):
        
        return self.execute("getNetworkConditions")['value']

    def set_network_conditions(self, **network_conditions) -> NoReturn:
        
        self.execute("setNetworkConditions", {
            'network_conditions': network_conditions
        })

    def execute_cdp_cmd(self, cmd: str, cmd_args: dict):
        
        return self.execute("executeCdpCommand", {'cmd': cmd, 'params': cmd_args})['value']

    def get_sinks(self) -> list:
        
        return self.execute('getSinks')['value']

    def get_issue_message(self):
        
        return self.execute('getIssueMessage')['value']

    def set_sink_to_use(self, sink_name: str) -> str:
        
        return self.execute('setSinkToUse', {'sinkName': sink_name})

    def start_tab_mirroring(self, sink_name: str) -> str:
        
        return self.execute('startTabMirroring', {'sinkName': sink_name})

    def stop_casting(self, sink_name: str) -> str:
        
        return self.execute('stopCasting', {'sinkName': sink_name})

    def quit(self) -> NoReturn:
        
        try:
            RemoteWebDriver.quit(self)
        except Exception:
            # We don't care about the message because something probably has gone wrong
            pass
        finally:
            self.service.stop()

    def create_options(self) -> BaseOptions:
        if self.vendor_prefix == "ms":
            return ChromeOptions()
        else:
            return ChromeOptions()
