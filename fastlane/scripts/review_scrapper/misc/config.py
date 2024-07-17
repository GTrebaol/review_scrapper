# config.py
from datetime import datetime, timedelta

KEY_ID = '539Y9B38ZP'
ISSUER_ID = '69a6de70-bb8a-47e3-e053-5b8c7c11a4d1'
IOS_PACKAGE_NAME = 'com.fortuneo.ios'
ANDROID_PACKAGE_NAME = 'com.fortuneo.android'
OUTPUT_FILE = 'reviews.json'
TIMEDELTA_HOURS = 3
REVIEWS_FETCH_QUANTITY = 10
TIME_THRESHOLD = datetime.today() - timedelta(hours=TIMEDELTA_HOURS)