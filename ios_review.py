# ios_reviews.py

import requests
import re
from misc.review import Review
from misc.utils import check_datetime_treshold, create_datetime_from_iso8601
from misc.config import config
from misc.token_generator import create_token
from typing import List


def get_reviews() -> List[Review]:
    token = create_token()
    finished = False
    reviews = []
    url = f'https://api.appstoreconnect.apple.com/v1/apps/{config.REPO_PACKAGE_NAME}/customerReviews?limit={config.REVIEWS_FETCH_QUANTITY}&sort=-createdDate'
    while not finished:
        print("Calling Apple services...")
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error retrieving reviews {response.status_code}")
        else:
            response_reviews = response.json()
            print(response_reviews)
            for item in response_reviews['data']:
                create_review(reviews=reviews, review_raw=item["attributes"])
            finished = (len(reviews) < config.REVIEWS_FETCH_QUANTITY)
            print(f"Fetched and kept {len(reviews)} reviews.")
            print("We're done here." if finished else "Fetching the next batch.")
            if not finished:
                url = response_reviews["links"]["next"]
    return reviews


def create_review(reviews: List[Review], review_raw: dict):
    comment = review_raw["body"]
    truncated_comment = comment[:99] + "..." if len(comment) > 100 else comment
    review = Review(
        os="iOs",
        author_name=review_raw["reviewerNickname"],
        rating=review_raw["rating"],
        truncated_comment=re.sub(r'[\n\t]', '', truncated_comment),
        content=re.sub(r'[\n\t]', '', comment),
        datetime=create_datetime_from_iso8601(review_raw["createdDate"]),
        version="",
        build_version="",
        phone="",
        title=review_raw["title"]
    )
    if not check_datetime_treshold(review):
        reviews.append(review)
