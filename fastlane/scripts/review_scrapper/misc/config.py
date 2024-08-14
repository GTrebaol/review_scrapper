# config.py

import os
import httplib2
from urllib.parse import urlparse

class Config:
    def __init__(self):
        # KEY_ID, ISSUER_ID, PRIVATE_KEY are for ios
        # JSON_KEY_DATA is for google
        self.KEY_ID = os.getenv('KEY_ID', 'DEFAULT_KEY_ID')
        self.ISSUER_ID = os.getenv('ISSUER_ID', 'DEFAULT_ISSUER_ID')
        self.PRIVATE_KEY = os.getenv('PRIVATE_KEY', 'DEFAULT_PRIVATE_KEY')
        self.JSON_KEY_DATA = os.getenv('JSON_KEY_DATA', 'DEFAULT_JSON_KEY_DATA')
        self.REPO_PACKAGE_NAME = os.getenv('REPO_PACKAGE_NAME', 'DEFAULT_APP_PACKAGE_ID')
        self.OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'reviews.json')
        self.TIMEDELTA_HOURS_ANDROID = int(os.getenv('TIMEDELTA_HOURS_ANDROID', 1))
        self.TIMEDELTA_HOURS_IOS = int(os.getenv('TIMEDELTA_HOURS_IOS', 24))
        self.REVIEWS_FETCH_QUANTITY = 50
        self.DATETIME_FORMAT = "%d/%m/%y %H:%M:%S"
        self.PROXIES = {
            'http': os.getenv("http_proxy"),
            'https': os.getenv("http_proxy"),
        }
        self.PROXY_GOOGLE_OBJECT = configure_proxy(urlparse(os.getenv("http_proxy")))


def configure_proxy(url_parse):
    http = httplib2.Http()
    proxy_info = httplib2.ProxyInfo(
        proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
        proxy_host=url_parse.hostname,
        proxy_port=url_parse.port,
    )
    http.proxy_info = proxy_info
    return http


config = Config()
