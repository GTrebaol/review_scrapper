# android_reviews.py

import googleapiclient.discovery
from google.oauth2 import service_account
import json
import re
from misc.review import Review
from misc.config import REVIEWS_FETCH_QUANTITY
from typing import List
from misc.utils import check_timestamp

def get_android_reviews(package: str, auth_key: str) -> List[Review]:
    finished = False
    startIndex = 0
    reviews = []
    while not finished:
        print("Calling Google services...")
        response_reviews = download_android_review(package=package, auth_key=auth_key, startIndex=startIndex)
        if not 'reviews' in response_reviews or len(response_reviews['reviews']) == 0:
            print('No reviews')
            finished = True
        else:
            for item in response_reviews['reviews']:
                create_review_android(reviews=reviews, review_raw=item)
            finished = (len(reviews) < REVIEWS_FETCH_QUANTITY)
            print(f"Fetched and kept {len(reviews)} reviews.")
            print("We're done here." if finished else "Fetching the next batch.")
            startIndex += REVIEWS_FETCH_QUANTITY
    return reviews

def download_android_review(package: str, auth_key: str, startIndex: int) -> dict:
    try:
        json_credentials = json.loads(auth_key)
        credentials = service_account.Credentials.from_service_account_info(json_credentials)
        service = googleapiclient.discovery.build('androidpublisher', 'v3', credentials=credentials)
        return service.reviews().list(packageName=package, maxResults=REVIEWS_FETCH_QUANTITY, startIndex=startIndex).execute()
    except Exception as e:
        print(e)
        return {}

def create_review_android(reviews: List[Review], review_raw: dict):
    comment = review_raw["comments"][0]["userComment"]
    truncated_comment = comment["text"][:199] + "..." if len(comment["text"]) > 200 else comment["text"]

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
    if not check_timestamp(review):
        reviews.append(review)
