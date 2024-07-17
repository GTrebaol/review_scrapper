from apiclient.discovery import build
from datetime import datetime, timedelta, date
from google.oauth2 import service_account
import googleapiclient
import json
import os
import optparse
import re
import requests
from typing import List

"""
This script get the review from a given app for the last 24h
"""

timedelta_hours = 3
time_treshold = datetime.today() - timedelta(hours=timedelta_hours)

class Review:
    def __init__(self, os, author_name, rating, content, timestamp, version, build_version, phone, truncated_comment):
        self.os = os
        self.author_name = author_name
        self.rating = self.set_rating(rating)
        self.content = content
        self.truncated_comment = truncated_comment
        self.datetime = datetime.fromtimestamp(float(timestamp))
        self.version = version
        self.build_version = build_version
        self.phone = phone
    def toJSON(self):
        serializable_object = self
        serializable_object.datetime = str(serializable_object.datetime)
        return json.dumps(
            serializable_object,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )
    def set_rating(self, rating: int) -> str:
        result = ""
        star = "⭐"
        for i in range(int(rating)):
            result = result + star
        return result


def get_ios_reviews(package: str) -> List[Review]:
    """
    Get the reviews from the Apple APIfor a given App using the requests package

    Args:
        review_id (int) - the id of the Apple App ID you want the reviews from
        page_no (int) - data is paginated, so this dermines which page number
        to return
    Returns:
        the response from the api (if status == 200), otherwise None

    """
    #finished = False
    #while not finished:
    url = f'https://api.appstoreconnect.apple.com/v1/apps/{package}/customerReviews'
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        print(json.loads(response.text))
        return response
    elif response is None:
        return None
    else:
        print(f"Error retrieving reviews {response.status_code}")
        return None

def get_android_reviews(package: str, auth_key: str) -> List[Review]:
    finished = False
    startIndex = 0
    reviews = []
    while not finished:
        response_reviews = download_android_review(package=package, auth_key=auth_key, startIndex=startIndex)
        if not 'reviews' in response_reviews or len(response_reviews['reviews']) == 0:
            print('No reviews')
            finished = True
        else:
            review_size = len(reviews)
            for item in response_reviews['reviews']:
                create_review_android(reviews=reviews, review_raw=item)
            finished = (review_size <= len(reviews))
            startIndex += 10
    return reviews

def download_android_review(package: str, auth_key: str, startIndex: int) -> str:
    response = ""
    try:
        json_credentials = json.loads(auth_key)
        credentials = service_account.Credentials.from_service_account_info(json_credentials)
        service = googleapiclient.discovery.build('androidpublisher', 'v3', credentials=credentials)
        response = service.reviews().list(packageName=package, maxResults=10, startIndex=startIndex).execute()
    except Exception as e:
        print(e)
        return
    return response

def get_android_latest_prod_version(package: str, auth_key: str):
    try:
        json_credentials = json.loads(auth_key)
        credentials = service_account.Credentials.from_service_account_info(json_credentials)
        service = googleapiclient.discovery.build('androidpublisher', 'v3', credentials=credentials)
        response_edit_id = service.edits().insert(body={}, packageName=package).execute()
        edit_id = response_edit_id['id']
        response = service.edits().tracks().get(packageName=package, editId=edit_id, track="production").execute()
    except Exception as e:
        print(e)
        return

def create_review_android(reviews: List[Review], review_raw: dict):
    comment = review_raw["comments"][0]["userComment"]
    truncated_comment = ""
    if len(comment["text"]) > 200:
        truncated_comment = comment["text"][0:199] + "..."

    review = Review(
        os="Android",
        author_name=review_raw["authorName"],
        rating=comment["starRating"],
        truncated_comment=re.sub(r'\t', '', truncated_comment),
        content=re.sub(r'\t', '', comment["text"]),
        timestamp=comment["lastModified"]["seconds"],
        version=comment["appVersionName"],
        build_version=comment["appVersionCode"],
        phone=comment["deviceMetadata"]["productName"]
    )
    if check_timestamp(review):
        return
    else:
        reviews.append(review)

def build_json_result(reviews: List[Review]) -> str:
    message = '{ "reviews" : ['
    for review in reviews:
        message +=  review.toJSON() + ","
    message = message[:-1]
    message += "]}"
    return message

def check_timestamp(review: Review) -> bool:
    return time_treshold > review.datetime


if __name__ == "__main__":
    if os.environ.get("http_proxy") != None:
        proxy_settings = {
            "http": os.environ.get("http_proxy"),
            "https": os.environ.get("http_proxy"),
        }

    options = optparse.OptionParser(usage="%prog [options]", description="gSender")

    options.add_option("-i", "--ios", action="store_true", dest="ios", help="scrapping ios review")
    options.add_option("-a", "--android", action="store_false", dest="ios", help="scrapping android review")
    options.add_option("-k", "--key", type="str", default="KEY", help="key needed for google store")
    options.add_option("-p", "--package", type="str", default="com.fortuneo.android", help="package name of the app")
    options.add_option("-f", "--file", type="str", default="reviews.json", help="filename output")
    options.add_option("-t", "--treshold", type="int", default=3, help="fetch reviews from x hours old")

    opts, args = options.parse_args()
    reviews = []
    timedelta_hours = opts.treshold

    if opts.ios:
        reviews = get_ios_reviews(
            package=opts.package
        )
    else:
        reviews = get_android_reviews(
            package=opts.package,
            auth_key=opts.key
        )
    with open(opts.file, 'w') as file:
        file.write(
            build_json_result(
                reviews=reviews
            )
        )
