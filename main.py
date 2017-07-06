# coding=utf-8
"""
Image Spider v1.0
"""

import os
import platform
import urllib
from utils import *
try:
    import spynner
except ImportError:
    spynner = None
if get_py_version() == 2:
    import urllib2
else:
    raise UnsupportedPythonVersion

__author__ = '丐帮'

LOG = Log()

__all__ = ('start', 'settings')


class ImageSpider(object):

    def __init__(self):
        self.headers = DEFAULT_HEADER
        self.cached_urls = list()
        self.cached_images = list()
        self.current_counts = 0
        self.current_domain = str()
        # current_base_link为当前所在页面，如查找当前页面所有链接，或者下载所有图片时
        self.current_base_link = str()
        self.current_abs_dir = str()
        self.current_protocol = 'http'
        self.current_depth = 1
        self.URL_CACHE = str()
        self.IMG_CACHE = str()
        self.MAIN_LOG = str()
        self.OP_LOG = str()
        self.LAST_CACHED_URL = str()

        self.SETTINGS = ConfigParser().settings
        self.SITES = self.SETTINGS.get(SETTINGS_SITES)
        if not self.SITES:
            raise SettingsError(SettingsError.sites_err)
        else:
            self.SITES = try_iter(self.SITES)
            self.SITES = add_protocol(self.SITES, self.current_protocol)
        self.INTERVAL = self.SETTINGS.get(SETTINGS_INTERVAL)
        if self.INTERVAL == 0:
            raise SettingsError(SettingsError.interval_err)
        self.MAX_COUNTS = self.SETTINGS.get(SETTINGS_MAX_COUNTS)
        if self.MAX_COUNTS:
            assert isinstance(self.MAX_COUNTS, int)
        self.MAX_LENGTH = self.SETTINGS.get(SETTINGS_MAX_LENGTH)
        if self.MAX_LENGTH:
            _ = self.MAX_LENGTH
            assert isinstance(self.MAX_LENGTH, (int, float))
            self.MAX_LENGTH = _ * 1024
        else:
            self.MAX_LENGTH = 0
        self.MIN_LENGTH = self.SETTINGS.get(SETTINGS_MIN_LENGTH)
        if self.MIN_LENGTH:
            _ = self.MIN_LENGTH
            assert isinstance(self.MIN_LENGTH, (int, float))
            self.MIN_LENGTH = _ * 1024
        else:
            self.MIN_LENGTH = 0
        self.IMAGE_TYPES = self.SETTINGS.get(SETTINGS_IMAGE_TYPE)
        self.BASE_DIR = self.SETTINGS.get(SETTINGS_BASE_DIR)
        if not self.BASE_DIR:
            plat = platform.platform().lower()
            if 'windows' in plat:  # windows
                self.BASE_DIR = r'C:\\'
            elif 'darwin' in plat or 'linux' in plat:  # unix-like
                # the same following 2 methods.
                # print os.path.expandvars('$HOME')
                # print os.path.expanduser('~、')
                self.BASE_DIR = os.path.join(os.environ['HOME'],CRAWLER_DATA_PATH)
            else:
                # unknown os
                self.BASE_DIR = str(input('未知操作系统，'
                                          '请手动输入保存文件的根路径：'))

        self.LOCAL_SITE = self.SETTINGS.get(SETTINGS_LOCAL_SITE)
        if not isinstance(self.LOCAL_SITE, bool):
            self.LOCAL_SITE = True
        self.CLEAR_CACHE = self.SETTINGS.get(SETTINGS_CLEAR_CACHE)
        if not isinstance(self.CLEAR_CACHE, bool):
            self.CLEAR_CACHE = False
        self.WEBKIT_MODE = self.SETTINGS.get(SETTINGS_WEBKIT_MODE)
        self.CONFIG_NAMES = ((SETTINGS_SITES, self.SITES),
                             (SETTINGS_INTERVAL, self.INTERVAL),
                             (SETTINGS_MAX_COUNTS, self.MAX_COUNTS),
                             (SETTINGS_IMAGE_TYPE, self.IMAGE_TYPES),
                             (SETTINGS_BASE_DIR, self.BASE_DIR),
                             (SETTINGS_LOCAL_SITE, self.LOCAL_SITE),
                             (SETTINGS_CLEAR_CACHE, self.CLEAR_CACHE))

    def settings(self, sites, headers=None, base_dir=None, max_counts=0,
                 interval=5, image_types=None, local_site=True, 
                 clear_cache=False):
        """
        Main process settings
        :param sites: 站点url，可为字符串，列表，元组，必选
        :param headers: 伪装浏览器头部，可选
        :param base_dir: 图片保存根目录，爬虫会在根目录下为每一个站点建立一个子目录
        :param max_counts: 设置爬行最大的url数量，到达后会退出程序，否则会一直执行
        :param interval: 抓取图片间隔
        :param image_types: 图片类型，后缀名
        :param local_site: 如果为True只爬取本站（包括子站），否则会爬取任何看到的链接
        :param clear_cache: 如果为True，会清空日志，忽略已有记录，重新下载已下载过的图片
        :return:
        """
        if headers:
            self.headers = headers
        if base_dir:
            self.BASE_DIR = base_dir
        self.LOCAL_SITE = local_site
        self.SITES = add_protocol(sites, self.current_protocol)
        self.MAX_COUNTS = max_counts
        self.INTERVAL = interval
        self.CLEAR_CACHE = clear_cache
        if image_types:
            self.IMAGE_TYPES = image_types

    def read_html(self, des, times=3):
        assert type(times) == int and times > 0, ('parameter times must be a '
                                                  'integer larger than 0')
        timer = 1
        while True:
            if not self.WEBKIT_MODE:
                try:
                    request = urllib2.Request(des.strip(), headers=self.headers)
                    response = urllib2.urlopen(request)
                    content = response.read()
                    response.close()
                    return content
                except urllib2.HTTPError as e:
                    _ = '%s 打开链接出错：%s' % (LOG.date_str, e.code)
                    mprint(_)
                    LOG.write(_, self.OP_LOG)
                    time.sleep(5)
                    timer += 1
                except urllib2.URLError as e:
                    _ = '%s 连接服务器出错：%s' % (LOG.date_str, e.reason)
                    mprint(_)
                    LOG.write(_, self.OP_LOG)
                    time.sleep(5)
                    timer += 1
                except Exception:
                    raise

            else:
                if not spynner:
                    raise PackageNotInstalled(SPYNNER_WARNING)
                try:
                    browser = spynner.Browser()
                    browser.hide()
                    browser.load(des, self.headers)
                    html_content = browser.html.encode('utf-8')
                    return html_content
                except Exception as e:
                    _ = '%s 读取页面出错(webkit)：%s' % (LOG.date_str, str(e))
                    mprint(_)
                    LOG.write(_, self.OP_LOG)
                    time.sleep(5)
                    timer += 1
            if timer >= times:
                _ = '%s 读取链接失败已经%d次，%s' % (LOG.date_str, timer, des)
                mprint(_)
                LOG.write(_, self.OP_LOG)
                return ''

    def download_images(self, url):
        """
        拿到一个URL中所有图片链接，并下载保存
        :param url: 下载图片的页面
        :return: list
        """

        def __add_image_cache(iu):
            self.cached_images.append(iu)
            LOG.cache(iu, self.IMG_CACHE)

        url_content = self.read_html(url)
        image_urls = get_images_from_url(url_content, self.base_link)

        for img_url in image_urls:
            if img_url in self.cached_images:
                continue
            try:
                path, name = self._get_image_path(img_url)
            except InvalidImageFileName:
                _ = '获取图片文件名失败: %s' % img_url
                __add_image_cache(img_url)
                LOG.write(_, self.MAIN_LOG)
                mprint(_)
                continue
            try:
                self._save_image(img_url, path, name)
            except SaveImageFailed as e:
                _ = '保存图片出错: %s %s' % (img_url, str(e))
                __add_image_cache(img_url)
                LOG.write(_, self.MAIN_LOG)
                mprint(_)
                continue
            # cache save
            __add_image_cache(img_url)
            # log
            log = '%s %s --> %s' % (LOG.date_str, img_url, path)
            mprint(log)
            LOG.write(log, self.MAIN_LOG)
            time.sleep(self.INTERVAL)

    def _get_image_path(self, image_url):
        """
        根据图片链接得到本地储存路径
        :param image_url
        :return: 本地存放绝对路径
        """
        # pat = r'(http[s]?://.*\/(.*?\.(jpg|jpeg|gif|png|bmp)))'
        # # res = re.findall(pat, image_url.lower())
        bare_url = image_url
        try:
            if image_url.startswith('http'):
                for item in (r'http://', r'https://'):
                    bare_url = bare_url.replace(item, '')

            split_list = []
            for item in bare_url.split('/')[1:]:
                if '?' not in item:
                    split_list.append(item)
                else:
                    # 带参数地址处理，遇到问号停止
                    split_list.append(item.split('?')[0])
                    break
            path = '/'.join(split_list[:-1])
            name = split_list[-1]

            _base_link = get_base_link(image_url)

            if not _base_link == self.base_link:
                abs_path = os.path.join(self.BASE_DIR,
                                        get_base_link(image_url, protocol=False))
                if not os.path.exists(abs_path):
                    os.makedirs(abs_path)
            else:
                abs_path = self.current_abs_dir
            for i, p in enumerate(path.split('/')):
                abs_path = os.path.join(abs_path, p)
            # if '?' in name and '=' in name:
            #     # 带参数图片地址处理
            #     if self.IMAGE_TYPES:
            #         _pat = r'^(.*?\.(%s))\?\w+\=.*$' % '|'.join(self.IMAGE_TYPES)
            #         res = re.findall(_pat, name, re.I)
            #         if res:
            #             name = res[0][0]
            #     else:
            #         res = re.findall(r'^(.*?)\?\w+=.*$', name)
            #         if res:
            #             name = res[0]
            #     if not res:
            #         raise InvalidImageFileName

        except Exception:
            raise
        return abs_path, name

    def _save_image(self, img_url, img_path, img_name):
        """从目标URL保存图片到本地"""
        if img_url not in self.cached_images:
            _timer = 0
            while True:
                try:
                    connection = urllib2.build_opener().open(
                        urllib2.Request(img_url))
                    _len = connection.headers.dict.get('content-length')
                    try:
                        _len = int(_len)
                    except ValueError:
                        pass
                    except TypeError:
                        pass
                    if _len and self.MAX_LENGTH and _len > self.MAX_LENGTH:
                        return
                    if _len and self.MIN_LENGTH and _len < self.MIN_LENGTH:
                        return
                    if not os.path.exists(img_path):
                        os.makedirs(img_path)
                    urllib.urlretrieve(img_url,
                                       os.path.join(img_path, img_name), None)
                except Exception:
                    _timer += 1
                    _ = '%s %s 保存图片失败%d次' % (LOG.date_str, img_url, _timer)
                    mprint(_)
                    LOG.write(_, self.OP_LOG)
                    if _timer >= 3:
                        break

                self.current_counts += 1
                self._show_image_counts()
                self._check_max_counts()
                break

    def _show_image_counts(self):
        if self.current_counts % 10 == 0:
            mprint('%s 已保存%d张图片' % (LOG.date_str, self.current_counts))

    def _check_max_counts(self):
        if self.MAX_COUNTS and self.current_counts >= self.MAX_COUNTS:
            exit('已抓够%d张图片，自动退出。' % self.current_counts)

    def _to_abs_url(self, url):
        """把任意URL转为绝对路径"""
        if not url.startswith('http'):
            if url.startswith(r'//'):
                url = '%s://%s' % (self.current_protocol, url.lstrip(r'//'))
            elif url.startswith(r'/'):
                url = '%s://%s/%s' % (self.current_protocol,
                                      self.current_base_link, url.lstrip(r'/'))
            else:
                # 没有/的相对URL
                url = '%s://%s/%s' % (self.current_protocol,
                                      self.current_base_link, url)
        return url

    def get_links(self, url):
        """
        拿到一个URL中所有<a>标签的href（未访问过的）并返回它们的绝对URL
        :param url:
        :return: list
        """
        content = replace_html_symbol(self.read_html(url))
        links = re.findall(r'<a.*?href="(.*?)".*?>', content, re.S)
        links = list(set(links))

        # 首先更新当前页面的base_url
        self.current_base_link = get_base_link(url, protocol=False)
        # filter visited links
        new_links = list()
        for link in links:
            _abs_url = self._to_abs_url(link)
            try:
                _, _domain = get_protocol_domain(_abs_url)
            except InvalidDomain:
                continue
            if self.LOCAL_SITE and not self.current_domain == _domain:
                # 非同域名且local_site为True，不进行任何处理
                continue

            if link not in self.cached_urls:
                # 加入处理后的绝对链接
                new_links.append(_abs_url)

        return new_links

    def _process_links(self, links):
        """
        链接处理
        {'url':'xxx', 'depth':1, ''}
        :param links: abs links
        :return:
        """
        # mprint('当前页面深度：%d' % self.current_depth)
        # next depth links list
        to_do_links = list()
        for link in links:
            # 更新当前页面的base_url
            self.current_base_link = get_base_link(link, protocol=False)

            if link in self.cached_urls:
                # ignore cached links
                continue
            else:
                # all links in next depth
                to_do_links.extend(self.get_links(link))

            # download images on this link one by one
            mprint('%s %s loading...' % (LOG.date_str, link))
            self.download_images(link)
            # cached the URL when images download is done
            self.cached_urls.append(link)
            LOG.cache(link, self.URL_CACHE)

        self.current_depth += 1
        # 拿到页面所有链接，递归
        if to_do_links:
            # 先清空当前深度cache
            LOG.clear_cache(self.TO_DO_URL_CACHE)
            # 将下一个深度的所有url写入到cache
            LOG.cache(NEW_LINE.join(to_do_links), self.TO_DO_URL_CACHE)
            self._process_links(to_do_links)
        else:
            _ = '没有更多的图片了，共保存%d张图片，bye~' % self.current_counts
            for item in ALL_CACHE:
                LOG.clear_cache(item)
            mprint(_)
            LOG.write(_, self.MAIN_LOG)
            return

    def _initialize(self, site):
        try:
            # initialize log and cache position
            self.current_protocol, self.current_domain = (get_protocol_domain
                                                          (link=site))
            self.base_link = get_base_link(site)
            self.base_link_without_protocol = get_base_link(site, protocol=False)

            self.current_abs_dir = os.path.join(self.BASE_DIR,
                                                self.base_link_without_protocol.replace('.','_'))
            print 'cur abs dir',self.current_abs_dir

            if not os.path.exists(self.current_abs_dir):
                os.makedirs(self.current_abs_dir)

            self.URL_CACHE = os.path.join(self.current_abs_dir, URL_CACHE)
            self.IMG_CACHE = os.path.join(self.current_abs_dir, IMG_CACHE)
            self.MAIN_LOG = os.path.join(self.current_abs_dir, MAIN_LOG)
            print 'config OP_LOG', OP_LOG
            self.OP_LOG = os.path.join(self.current_abs_dir, OP_LOG)
            print 'init self.OP_LOG', self.OP_LOG
            self.TO_DO_URL_CACHE = os.path.join(self.current_abs_dir,
                                                TO_DO_URL_CACHE)
            # self.LAST_CACHED_URL = LOG.get_last_cache(self.URL_CACHE)

        except Exception:
            raise InitializeFailed

        if self.CLEAR_CACHE:
            # clear cache
            try:
                LOG.clear_cache(self.URL_CACHE)
                LOG.clear_cache(self.IMG_CACHE)
            except ClearCacheFailed:
                pass
        else:
            # load cache
            try:
                self.cached_urls = LOG.load_cache(self.URL_CACHE)
                self.cached_images = LOG.load_cache(self.IMG_CACHE)
            except LoadCacheFailed:
                pass

    def _show_config(self):
        mprint(TIP_SETTINGS)
        for name, value in self.CONFIG_NAMES:

            mprint('%-15s = %s' % (name, value))
        mprint(TIP_BLANK)

    def start(self):
        # show config info
        self._show_config()
        # start
        if not self.MAX_COUNTS:
            condition = True
        else:
            condition = self.current_counts <= self.MAX_COUNTS
        if not self.SITES:
            raise ParameterNotGiven(ParameterNotGiven.msg)
        mprint(TIP_START)
        while condition:

            for site in self.SITES:
                try:
                    self._initialize(site)
                    do_to_links = LOG.load_cache(self.TO_DO_URL_CACHE)
                    if do_to_links:
                        site = do_to_links
                    # get images from it and all it's sub urls
                    self._process_links(try_iter(site))

                except KeyboardInterrupt:
                    _ = '共保存%d张图片, bye~' % self.current_counts
                    mprint(_)
                    LOG.write(_, self.MAIN_LOG)
                    condition = False
                    break
                except Exception as e:
                    if isinstance(e, WARN_EXCEPTIONS):
                        LOG.write(str(e), self.OP_LOG)
                        continue
                    elif isinstance(e, FATAL_EXCEPTIONS):
                        LOG.write(str(e), self.OP_LOG)
                        raise
                    else:
                        raise
        mprint(TIP_END)
