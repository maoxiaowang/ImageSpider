# coding=utf-8
import re
import sys
import time
from ImageSpider.utils.exceptions import *


def get_py_version():
    return sys.version_info[0]


def mprint(string, *args):
    ver = get_py_version()
    if args:
        for item in args:
            string += ' %s' % item
    if ver == 2:
        print string
    elif ver == 3:
        print(string)
    else:
        raise UnknownPythonVersion


def try_iter(s):
    # assert (isinstance(s, (str, unicode, list, tuple)),
    #         'str, list or tuple is needed')
    res = list()
    if type(s) in (str, unicode):
        res = [s]
    elif type(s) in (tuple, list):
        res = s
    return res


def add_protocol(sites):
    processed_sites = list()
    sites = try_iter(sites)
    for site in sites:
        assert isinstance(site, (str, unicode))
        site = site.strip(r'/')
        if not site.startswith('http'):
            processed_sites.append(r'http://' + site)
        else:
            processed_sites.append(site)
    return processed_sites


def get_domain(site_link):
    assert isinstance(site_link, (str, unicode))
    if site_link.startswith('http'):
        for item in (r'http://', r'https://'):
            site_link = site_link.replace(item, '')
    site_url = site_link.split('/')[0]
    if not '.' in site_url:
        raise GetBaseLinkFailed

    domain = '.'.join((site_url.split('.')[-2], site_url.split('.')[-1]))
    return domain


def get_images_from_url(url_content, base_link):
    """
    从URL内容中获取所有img标签的src属性
    :param url_content: 页面内容
    :param base_link: 基础链接，比如http://www.baidu.com
    :return: 图片绝对URL的列表
    """
    # TODO: lazyload
    res = re.findall(r'<img.*?src="(.*?)".*?>', url_content)
    result = list()
    for item in res:
        if item.startswith(r'/'):
            result.append(base_link + item)
        elif item.startswith('http'):
            result.append(item)
        else:
            continue
    return result


def replace_html_symbol(content):
    return content.replace('&#47;', r'/')


class Log(object):
    def __init__(self):
        self.NEW_LINE = '\n'

    @property
    def __date_str(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def write(self, content, log_file_path):
        with open(log_file_path, mode='a+') as f:
            f.write('%s %s%s' % (self.__date_str, content, self.NEW_LINE))

    def cache(self, content, cache_file_path):
        cached = False
        with open(cache_file_path, mode='a+') as f:
            lines = f.readlines()
            for line in lines:
                if line == content:
                    cached = True
                    break
            if not cached:
                f.write(content + self.NEW_LINE)

    @staticmethod
    def is_cached(url, cache_file_path):
        with open(cache_file_path, mode='a+') as f:
            lines = f.readlines()
            for line in lines:
                if url == line.strip():
                    return True
        return False

    @staticmethod
    def load_cache(cache_file_path):
        cache = list()
        try:
            with open(cache_file_path, mode='a+') as f:
                lines = f.readlines()
                for line in lines:
                    cache.append(line.strip())
        except Exception:
            raise LoadCacheFailed
        return cache

    @staticmethod
    def clear_cache(cache_file_path):
        try:
            with open(cache_file_path, mode='w') as f:
                f.write('')
        except Exception:
            raise ClearCacheFailed
