from ImageSpider.main import ImageSpider

SITES = 'http://www.nipic.com/index.html'
INTERVAL = 3
MAX_COUNTS = 10
BASE_DIR = 'E:\\'


isp = ImageSpider()
isp.settings(sites=SITES,
             base_dir=BASE_DIR,
             interval=INTERVAL,
             maximum_counts=MAX_COUNTS)
isp.start()