# config.py

import os


class Config:
    def __init__(self):
        # KEY_ID, ISSUER_ID, PRIVATE_KEY are for ios
        # JSON_KEY_DATA is for google
        self.KEY_ID = os.getenv('KEY_ID', 'DEFAULT_KEY_ID')
        self.ISSUER_ID = os.getenv('ISSUER_ID', 'DEFAULT_ISSUER_ID')
        self.PRIVATE_KEY = os.getenv('PRIVATE_KEY', 'DEFAULT_PRIVATE_KEY')
        self.JSON_KEY_DATA = os.getenv('JSON_KEY_DATA', 'JSON_KEY_DATA')
        self.REPO_PACKAGE_NAME = os.getenv('REPO_PACKAGE_NAME', 'DEFAULT_APP_PACKAGE_ID')
        self.OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'reviews.json')
        self.TIMEDELTA_HOURS = int(os.getenv('TIMEDELTA_HOURS', 72))
        self.REVIEWS_FETCH_QUANTITY = 50
        self.DATETIME_FORMAT = "%d/%m/%y %H:%M:%S"


config = Config()
