# coding=utf-8
from ImageSpider.utils.exceptions import *

MAIN_LOG = 'main.log'
URL_CACHE = 'url_cache'
IMG_CACHE = 'img_cache'
OP_LOG = 'op.log'

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
                   TranslateToAbsoluteURLFailed)
FATAL_EXCEPTIONS = (UnknownPythonVersion,
                    UnsupportedPythonVersion,
                    GetBaseLinkFailed,
                    InitializeFailed)