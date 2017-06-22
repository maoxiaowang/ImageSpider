# coding=utf-8
"""
Image Spider v1.0
"""

import os
import platform
import urllib
from utils import *

if get_py_version() == 2:
    import urllib2
else:
    raise UnsupportedPythonVersion

__author__ = '丐帮'

LOG = Log()

__all__ = ('start', 'settings')


class ImageSpider(object):

    def __init__(self):

        self.SETTINGS = ConfigParser().settings
        self.SITES = try_iter(self.SETTINGS.get(SETTINGS_SITES))
        if not self.SITES:
            raise SettingsError(SettingsError.sites_err)
        self.INTERVAL = self.SETTINGS.get(SETTINGS_INTERVAL)
        if self.INTERVAL == 0:
            raise SettingsError(SettingsError.interval_err)
        self.MAX_COUNTS = self.SETTINGS.get(SETTINGS_MAX_COUNTS)
        if not self.MAX_COUNTS:
            self.MAX_COUNTS = 0
        self.IMAGE_TYPE = self.SETTINGS.get(SETTINGS_IMAGE_TYPE)
        self.BASE_DIR = self.SETTINGS.get(SETTINGS_BASE_DIR)
        if not self.BASE_DIR:
            plat = platform.platform().lower()
            if 'windows' in plat:
                self.BASE_DIR = 'C:\\'
            elif 'linux' in plat:
                self.BASE_DIR = '\\home'
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

        self.CONFIG_NAMES = ((SETTINGS_SITES, self.SITES),
                             (SETTINGS_INTERVAL, self.INTERVAL),
                             (SETTINGS_MAX_COUNTS, self.MAX_COUNTS),
                             (SETTINGS_IMAGE_TYPE, self.IMAGE_TYPE),
                             (SETTINGS_BASE_DIR, self.BASE_DIR),
                             (SETTINGS_LOCAL_SITE, self.LOCAL_SITE),
                             (SETTINGS_CLEAR_CACHE, self.CLEAR_CACHE))
        
        self.headers = DEFAULT_HEADER
        self.cached_urls = list()
        self.cached_images = list()
        self.current_counts = 0
        self.current_domain = str()
        self.current_abs_dir = str()

        self.URL_CACHE = str()
        self.IMG_CACHE = str()
        self.MAIN_LOG = str()
        self.OP_LOG = str()
        self.IMAGE_TYPES = None

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
        :param clear_cache: 如果为True，会清空日志，忽略已爬取的记录，重新下载已下载过的图片
        :return:
        """
        if headers:
            self.headers = headers
            # assert (isinstance(headers, dict),
            #         'parameter headers must be a dictionary')
            # self.headers = headers
        # if clear_cache:
        #     LOG.clear_cache(self.URL_CACHE)
        #     LOG.clear_cache(self.IMG_CACHE)
        if base_dir:
            self.BASE_DIR = base_dir
        self.LOCAL_SITE = local_site
        self.SITES = add_protocol(sites)
        self.MAX_COUNTS = max_counts
        self.INTERVAL = interval
        self.CLEAR_CACHE = clear_cache
        if image_types:
            self.IMAGE_TYPES = image_types

        # if maximum_counts:
        #     assert (isinstance(maximum_counts, int) and maximum_counts > 0,
        #             'a positive integer is needed')
        #     self.MAX_COUNTS = maximum_counts
        # self.INTERVAL = interval
        # assert (isinstance(interval, int) and interval > 0,
        #         'a positive integer is needed')

    def read_html(self, des, times=10):
        assert type(times) == int and times > 0, ('parameter times must be a '
                                                  'integer larger than 0')
        timer = 1
        while True:
            try:
                request = urllib2.Request(des.strip(), headers=self.headers)
                response = urllib2.urlopen(request)
                break
            except urllib2.HTTPError as e:
                _ = '打开链接出错，错误码：%s' %e.code
                mprint(_)
                LOG.write(_, self.OP_LOG)
                time.sleep(10)
                timer += 1
            except urllib2.URLError as e:
                _ = '目标服务器连接出错，错误码：%s' %e.reason
                mprint(_)
                LOG.write(_, self.OP_LOG)
                time.sleep(10)
                timer += 1
            if timer >= times:
                _ = '读取链接失败已经%d次，%s' % (timer, des)
                mprint(_)
                LOG.write(_, self.OP_LOG)
                return ''

        content = response.read()
        response.close()
        return content

    def download_images(self, url):
        """
        拿到一个URL中所有图片链接，并下载保存
        :param url: 下载图片的页面
        :return: list
        """
        url_content = self.read_html(url)
        image_urls = get_images_from_url(url_content, self.current_domain)
        for img_url in image_urls:
            # TODO: 转为绝对路径
            path, name = self._get_image_path(img_url)
            self._save_image(img_url, path, name)
            # cache save
            if img_url not in self.cached_images:
                self.cached_images.append(img_url)
                LOG.cache(img_url, self.IMG_CACHE)
                # log
                log = '%s --> %s' % (img_url, path)
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
        try:
            if image_url.startswith('http'):
                for item in (r'http://', r'https://'):
                    image_url = image_url.replace(item, '')
            path = '/'.join(image_url.split('/')[1:-1])
            name = image_url.split('/')[-1]
            abs_path = self.current_abs_dir
            for i, p in enumerate(path.split('/')):
                abs_path = os.path.join(abs_path, p)
        except Exception:
            raise
        return abs_path, name
        # if res:
        #     path, name = res[0][0], res[0][1]
        #     abs_path = self.current_abs_dir
        #     for i, p in enumerate(path.split('/')):
        #         abs_path = os.path.join(abs_path, p)
        #     return abs_path, name
        # else:
        #     # not a image url
        #     raise InvalidImageFileName
        #     pass

    def _save_image(self, img_url, img_path, img_name):
        """从目标URL保存图片到本地"""
        if img_url not in self.cached_images:
            u_obj = urllib.urlopen(img_url)
            img_data = u_obj.read()
            try:
                if not os.path.exists(img_path):
                    os.makedirs(img_path)
                f = open(os.path.join(img_path, img_name), 'wb')
                f.write(img_data)
                f.close()
            except IOError as e:
                raise e
            except Exception:
                raise SaveImageFailed

            self.current_counts += 1
            self._show_image_counts()
            self._check_exit()

    def _show_image_counts(self):
        if self.current_counts % 10 == 0:
            mprint('已保存%d张图片' % self.current_counts)

    def _check_exit(self):
        if self.MAX_COUNTS and self.current_counts >= self.MAX_COUNTS:
            exit('已抓够%d张图片，自动退出。' % self.current_counts)

    def _remove_non_local_site_links(self, links):
        """移除非本站链接"""
        # result = list()
        for link in links:
            # if self.current_domain in link:
            #     result.append(link)
            if self.current_domain not in link:
                links.remove(link)
        return links

    @staticmethod
    def _to_abs_url(url):
        """把URL转为绝对路径"""
        res = re.findall(r'(http[s]?://.*?)/.*$', url)
        if not res:
            raise TranslateToAbsoluteURLFailed

    def get_links(self, url):
        """
        拿到一个URL中所有a标签的href（未访问过的）
        :param url:
        :return: list
        """
        content = replace_html_symbol(self.read_html(url, times=5))
        links = re.findall(r'<a.*?href="(http.*?)".*?>', content, re.S)
        links = list(set(links))
        # filter visited links
        for link in links:
            if link in self.cached_urls:
                links.remove(link)
            if link.startswith(r'/'):
                # 转为绝对路径
                links.remove(link)
                links.append(self._to_abs_url(link))
        if self.LOCAL_SITE:
            # filter non local links
            links = self._remove_non_local_site_links(links)

        return links

    def _process_links(self, links):
        """
        链接处理
        :param links:
        :return:
        """
        for link in links:
            # first, download images on this link one by one
            self.download_images(link)

            # 缓存地址
            if link not in self.cached_urls:
                mprint(link)
                self.cached_urls.append(link)
                LOG.write(link, self.URL_CACHE)
            else:
                # ignore cached links
                continue

            # TODO: 拿到页面所有链接，递归
            do_to_links = self.get_links(link)
            self._process_links(do_to_links)

    def _process_site(self, site):
        """
        页面处理
        :param site: settings指定的站点URL
        :return:
        """

        # get down images of the the page first
        self.download_images(site)

        # get urls on this page
        base_urls = self.get_links(site)
        
        # LOG
        LOG.write('Start getting images from %s' % site, 
                  os.path.join(self.current_abs_dir, self.MAIN_LOG))

        # process urls
        self._process_links(base_urls)

    def _initialize(self, site):
        try:
            # initialize log and cache position
            self.current_domain = get_domain(site_link=site)
            self.current_abs_dir = os.path.join(self.BASE_DIR,
                                                self.current_domain)
            if not os.path.exists(self.current_abs_dir):
                os.makedirs(self.current_abs_dir)
            self.URL_CACHE = os.path.join(self.current_abs_dir, URL_CACHE)
            self.IMG_CACHE = os.path.join(self.current_abs_dir, IMG_CACHE)
            self.MAIN_LOG = os.path.join(self.current_abs_dir, MAIN_LOG)
            self.OP_LOG = os.path.join(self.current_abs_dir, OP_LOG)
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
        mprint('----------SETTINGS----------')
        for name, value in self.CONFIG_NAMES:

            mprint('%-15s = %s' % (name, value))
        mprint('----------------------------')

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
        while condition:
            for site in self.SITES:
                try:
                    self._initialize(site)
                    # get images from it and all it's sub urls
                    self._process_site(site)
                except KeyboardInterrupt:
                    mprint('本次共保存%d张图片, bye~' % self.current_counts)
                except Exception as e:
                    if isinstance(e, WARN_EXCEPTIONS):
                        LOG.write(str(e), self.OP_LOG)
                        raise
                    elif isinstance(e, FATAL_EXCEPTIONS):
                        LOG.write(str(e), self.OP_LOG)
                        raise
                    else:
                        raise
