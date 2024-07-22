# android_reviews.py

import googleapiclient.discovery
from google.oauth2 import service_account
import json
import re
from misc.review import Review
from misc.config import config
from typing import List
from misc.utils import check_datetime_treshold, create_datetime_from_timestamp


def get_reviews() -> List[Review]:
    finished = False
    start_index = 0
    reviews = []
    while not finished:
        print("Calling Google services...")
        response_reviews = download_review(start_index=start_index)
        if not 'reviews' in response_reviews or len(response_reviews['reviews']) == 0:
            print('No reviews')
            finished = True
        else:
            for item in response_reviews['reviews']:
                create_review(reviews=reviews, review_raw=item)
            finished = (len(reviews) < config.REVIEWS_FETCH_QUANTITY)
            print(f"Fetched and kept {len(reviews)} reviews.")
            print("We're done here." if finished else "Fetching the next batch.")
            start_index += config.REVIEWS_FETCH_QUANTITY
    return reviews


def download_review(start_index: int) -> dict:
    try:
        json_credentials = json.loads(config.JSON_KEY_DATA)
        credentials = service_account.Credentials.from_service_account_info(json_credentials)
        service = googleapiclient.discovery.build('androidpublisher', 'v3', credentials=credentials)
        return service.reviews().list(packageName=config.REPO_PACKAGE_NAME,
                                      maxResults=config.REVIEWS_FETCH_QUANTITY).execute()
    except Exception as e:
        print(e)
        return {}


def create_review(reviews: List[Review], review_raw: dict):
    comment = review_raw["comments"][0]["userComment"]
    truncated_comment = comment["text"][:99] + "..." if len(comment["text"]) > 100 else comment["text"]
    version = "-"
    version_code = "-"
    phone = "-"
    author_name = "Monsieur Untel"
    if "appVersionName" in comment:
        version = comment["appVersionName"]
    if "deviceMetadata" in comment:
        phone = comment["deviceMetadata"]["productName"]
    if "appVersionCode" in comment:
        version_code = comment["appVersionCode"]
    if "authorName" in review_raw:
        author_name = review_raw["authorName"]
    review = Review(
        os="Android",
        author_name=author_name,
        rating=comment["starRating"],
        truncated_comment=re.sub(r'\t', '', truncated_comment),
        content=re.sub(r'\t', '', comment["text"]),
        datetime=create_datetime_from_timestamp(float(comment["lastModified"]["seconds"])),
        version=version,
        build_version=version_code,
        phone=phone,
        title=""
    )
    if not check_datetime_treshold(review):
        reviews.append(review)
