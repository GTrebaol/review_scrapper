# utils.py

from datetime import datetime
from typing import List
from misc.review import Review
from misc.config import TIME_THRESHOLD

def build_json_result(reviews: List[Review]) -> str:
    message = '{ "reviews" : ['
    for review in reviews:
        message += review.toJSON() + ","
    message = message[:-1]
    message += "]}"
    return message

def check_timestamp(review: Review) -> bool:
    return TIME_THRESHOLD > review.datetime
