# coding=utf-8
from utils.exceptions import *

CRAWLER_DATA_PATH = 'ImageSpider'   # 包名辨识
MAIN_LOG = 'main.log'
URL_CACHE = 'url_cache'
IMG_CACHE = 'img_cache'
TO_DO_URL_CACHE = 'to_do_url_cache'
ALL_CACHE = (URL_CACHE, IMG_CACHE, TO_DO_URL_CACHE)
OP_LOG = 'op.log'
SETTINGS_CONF = 'settings.conf'

NEW_LINE = '\n'

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
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; '
                          'WOW64; Trident/7.0; rv:11.0) like Gecko'
}

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

SPYNNER_WARNING = ('Make sure Spynner is already installed, '
                   'or you can turn off webkit_mode in settings.conf.')