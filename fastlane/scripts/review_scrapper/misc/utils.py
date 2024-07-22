# utils.py

from datetime import datetime, timedelta
from typing import List
from misc.review import Review
from misc.config import config


def build_json_result(reviews: List[Review]) -> str:
    message = '{ "reviews" : ['
    for review in reviews:
        message += review.to_json() + ","
    message = message[:-1]
    message += "]}"
    return message


def check_datetime_treshold(review: Review) -> bool:
    return get_time_treshold(config.TIMEDELTA_HOURS) > review.datetime


def get_time_treshold(delta: int):
    return datetime.today() - timedelta(hours=delta)


def create_datetime_from_iso8601(date_str):
    # Utilisation de strptime pour analyser la date ISO 8601 en objet datetime
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
    dt = dt.replace(tzinfo=None)
    return dt


def create_datetime_from_timestamp(timestamp):
    # Utilisation de fromtimestamp pour convertir le timestamp en objet datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt
