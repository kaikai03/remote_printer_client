from .chrome.webdriver import WebDriver as EDGE  # noqa
from .chrome.options import Options as EDGEOptions  # noqa
from .remote.webdriver import WebDriver as Remote  # noqa
from .common.desired_capabilities import DesiredCapabilities  # noqa
from .common.action_chains import ActionChains  # noqa
from .common.touch_actions import TouchActions  # noqa
from .common.proxy import Proxy  # noqa
from .common.keys import Keys  # noqa

__version__ = '2.0.0'
