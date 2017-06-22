from main import ImageSpider

isp = ImageSpider()
# This method can override settings.conf
# isp.settings(sites=SITES,
#              headers=DEFAULT_HEADER,
#              interval=INTERVAL,
#              max_counts=MAX_COUNTS,
#              image_types=('jpg', 'png'),
#              local_site=True,
#              clear_cache=False)
isp.start()
