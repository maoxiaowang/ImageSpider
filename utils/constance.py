# coding=utf-8
from utils.exceptions import *
import sys

CRAWLER_DATA_PATH = 'ImageSpider'   # 包名辨识
MAIN_LOG = 'main.log'
URL_CACHE = 'url_cache'
IMG_CACHE = 'img_cache'
TO_DO_URL_CACHE = 'to_do_url_cache'
ALL_CACHE = (URL_CACHE, IMG_CACHE, TO_DO_URL_CACHE)
OP_LOG = 'op.log'
SETTINGS_CONF = 'settings.conf'

NEW_LINE = '\n'

if sys.version_info[0] == 2:
    PY_VERSION = 2
    STR = (str, unicode)
else:
    PY_VERSION = 3
    STR = (str, )

SETTINGS_SITES = 'sites'
SETTINGS_INTERVAL = 'interval'
SETTINGS_MAX_COUNTS = 'max_counts'
SETTINGS_MAX_LENGTH = 'max_length'
SETTINGS_MIN_LENGTH = 'min_length'
SETTINGS_IMAGE_TYPE = 'image_types'
SETTINGS_BASE_DIR = 'base_dir'
SETTINGS_LOCAL_SITE = 'is_local_site'
SETTINGS_CLEAR_CACHE = 'clear_cache'
SETTINGS_WEBKIT_MODE = 'webkit_mode'

COMMON_IMAGE_TYPES = ['jpg', 'jpeg', 'gif', 'png', 'bmp']

TIP_SETTINGS = '----------SETTINGS----------'
TIP_BLANK = '----------------------------'
TIP_START = '------------START-----------'
TIP_END = '-------------END------------'

DEFAULT_HEADER = {
    'Connection': 'Keep-Alive',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/48.0.2564.116 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
}

DEFAULT_TIMEOUT = 30

WARN_EXCEPTIONS = (InvalidImageFileName,
                   ClearCacheFailed,
                   LoadCacheFailed,
                   SaveImageFailed,
                   TranslateToAbsoluteURLFailed,
                   InvalidDomain,
                   )
FATAL_EXCEPTIONS = (UnknownPythonVersion,
                    UnsupportedPythonVersion,
                    GetBaseLinkFailed,
                    InitializeFailed,
                    SettingsError,
                    LoadSettingsFileFailed)

PHANTOMJS_PATH = None
PHANTOMJS_LOG = ''

WEBDRIVER_WARNING = ('Make sure selenium is already installed, '
                     'or you can turn off webkit_mode in settings.conf.')