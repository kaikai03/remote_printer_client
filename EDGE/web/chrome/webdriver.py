
import warnings
from EDGE.web.chromium.webdriver import ChromiumDriver
from .options import Options
from .service import Service
from EDGE.web.common.desired_capabilities import DesiredCapabilities


DEFAULT_PORT = 0
DEFAULT_SERVICE_LOG_PATH = None
DEFAULT_KEEP_ALIVE = None


class WebDriver(ChromiumDriver):
    def __init__(self, executable_path, port=DEFAULT_PORT,
                 options: Options = None, service_args=None,
                 desired_capabilities=None, service_log_path=DEFAULT_SERVICE_LOG_PATH,
                 service: Service = None):

        keep_alive = True

        if not service:
            service = Service(executable_path, port, service_args, service_log_path)

        super(WebDriver, self).__init__(DesiredCapabilities.MicrosoftEdge['browserName'], "goog",
                                        port, options,
                                        service_args, desired_capabilities,
                                        service_log_path, service, keep_alive)
