# coding=utf-8
import re
import sys
import time
from constance import *


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
    """
    turn value to iterable
    :param s: str, tuple, list
    :return: list
    """
    res = list()
    if type(s) in (str, unicode):
        res = [s]
    elif type(s) in (tuple, list):
        res = s
    return res


def add_protocol(sites, protocol):
    processed_sites = list()
    sites = try_iter(sites)
    for site in sites:
        assert isinstance(site, (str, unicode))
        site = site.strip(r'/')
        if not site.startswith('http'):
            processed_sites.append(r'%s://' % protocol + site)
        else:
            processed_sites.append(site)
    return processed_sites


def get_base_link(site, protocol=True):
    """http://s1.image.abc.com/hello.html的base_link为s1.image.abc.com"""
    pat = r'(http[s]?://[^/]+)/?' if protocol else r'http[s]?://([^/]+)/?'
    res = re.findall(pat, site)
    if not res:
        raise GetBaseLinkFailed
    _base_link = res[0]
    if not protocol and ':' in _base_link:
        # 有端口的情况
        return _base_link.split(':')[0]
    else:
        return _base_link

def getHostnameOfUrl(url):
    # (?xi)\A
    # [a - z][a - z0 - 9 +\-.] *: //  # Scheme
    # ([a - z0 - 9\-._
    # ~ %!$ & '()*+,;=]+@)?           # User
    # ([a - z0 - 9\-._
    # ~ %]+                           # Named or IPv4 host
    # | \[[a - z0 - 9\-._
    # ~ %!$ & '()*+,;=:]+\])          # IPv6+ host
    reobj = re.compile(r"(?xi)\A[a-z][a-z0-9+\-.]*://([a-z0-9\-._~%!$&'()*+,;=]+@)?([a-z0-9\-._~%]+|[a−z0−9\-.])")
    return reobj.search(url).group(2)

def get_protocol_domain(link):
    """
    link必须为绝对URL，比如http://www.baidu.com/...这种形式
    :param link:
    :return:
    """
    assert isinstance(link, (str, unicode))
    if link.startswith('https'):
        site_link = link.replace(r'https://', '')
        protocol = 'https'
    else:
        site_link = link.replace(r'http://', '')
        protocol = 'http'

    site_url = site_link.split('/')[0]
    if '.' not in site_url:
        raise InvalidDomain

    double_suffix = ('com', 'net', 'gov', 'org', 'edu', 'top')
    domain = '.'.join((site_url.split('.')[-2:]))
    for item in double_suffix:
        # 分为两部分的域名后缀，如com.cn
        if re.match(r'^%s\.[a-z]{2}$' % item, domain):
            domain = '.'.join((site_url.split('.')[-3:]))
    return protocol, domain


def get_images_from_url(url_content, base_link):
    """
    从URL内容中获取所有img标签的src属性，并返回src列表
    :param url_content: 页面内容
    :param base_link: 基本链接，如https://www.baidu.com
    :return: 图片绝对URL的列表
    """
    # TODO: lazyload
    res = re.findall(r'<img.*?src="(.*?)".*?>', url_content)
    res = list(set(res))
    result = list()
    for item in res:
        if item.startswith(r'//'):
            result.append('%s%s' % ('http://', item.strip(r'//')))
        elif item.startswith(r'/'):
            result.append('%s/%s' % (base_link, item.strip(r'/')))
        elif item.startswith('http'):
            result.append(item)
        else:
            continue
    return result


def replace_html_symbol(content):
    for item in ('&#x2F;', '&#47;', '&#x2f;'):
        content = content.replace(item, r'/')
    return content


class Log(object):
    def __init__(self):
        pass

    @property
    def date_str(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def write(self, content, log_file_path):
        with open(log_file_path, mode='a+') as f:
            f.write('%s %s%s' % (self.date_str, content, NEW_LINE))

    @staticmethod
    def cache(content, cache_file_path):
        cached = False
        with open(cache_file_path, mode='a+') as f:
            lines = f.readlines()
            for line in lines:
                if line == content:
                    cached = True
                    break
            if not cached:
                f.write(content + NEW_LINE)

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

    @staticmethod
    def get_last_cache(cache_file_path):
        try:
            with open(cache_file_path, mode='a+') as f:
                lines = f.readlines()
                lines.reverse()
                for line in lines:
                    if line.strip():
                        return line.strip()
        except Exception:
            raise LoadCacheFailed


class ConfigParser(object):

    def __init__(self):
        self._settings = dict()
        try:
            with open(SETTINGS_CONF) as f:
                lines = f.readlines()
                for line in lines:
                    if line and not line.startswith('#') and '=' in line:
                        l = line.split('=')
                        if len(l) == 2:
                            name, value = l
                        elif len(l) > 2:
                            name, value = l[0], '='.join(l[1:])
                        else:
                            raise LoadSettingsFileFailed
                        name, value = name.strip(), value.strip()
                        self._settings[name] = self._trans(value)
        except Exception:
            raise LoadSettingsFileFailed

    @staticmethod
    def _trans_single(v):
        if v.replace('.', '').isdigit():
            if '.' in v:
                v = float(v)
            else:
                v = int(v)
        elif v.lower() == 'true':
            v = True
        elif v.lower() == 'false':
            v = False
        return v

    def _trans(self, value):
        if ',' in value:
            # for multiple value, return a list
            value = [i.strip() for i in value.split(',') if i]
            return [self._trans_single(i) for i in value]
        else:
            return self._trans_single(value)

    def get(self, name):
        # 返回value
        return self._trans(self._settings.get(name))

    @property
    def settings(self):
        # 读取所有配置项，并返回对应value
        return self._settings
