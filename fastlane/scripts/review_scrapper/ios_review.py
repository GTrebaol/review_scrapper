# ios_reviews.py

import logging
import re
from typing import List
import os

import requests

from misc.config import config
from misc.review import Review
from misc.token_generator import create_token
from misc.utils import check_datetime_treshold, create_datetime_from_iso8601

logging.basicConfig(level=logging.INFO)


def get_reviews() -> List[Review]:
    token = create_token()
    finished = False
    reviews = []
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{config.REPO_PACKAGE_NAME}/customerReviews?limit={config.REVIEWS_FETCH_QUANTITY}&sort=-createdDate"
    while not finished:
        logging.info("Calling Apple services...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, proxies=config.PROXIES)
        if response.status_code != 200:
            logging.error(f"Error retrieving reviews {response.status_code}")
            finished = True
        else:
            response_reviews = response.json()
            if "data" not in response_reviews:
                logging.info("No reviews")
            else:
                for item in response_reviews["data"]:
                    check_and_save_review(item, reviews)

                finished = len(reviews) < config.REVIEWS_FETCH_QUANTITY
                logging.info(f"Fetched and kept {len(reviews)} reviews.")
                logging.info(
                    "We're done here." if finished else "Fetching the next batch."
                )
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
        truncated_comment=re.sub(r'"', "'", re.sub(r"[\n\t]", "", truncated_comment)),
        content=re.sub(r'"', "'", re.sub(r"[\n\t]", "", comment)),
        datetime=create_datetime_from_iso8601(review_raw["createdDate"]),
        version="",
        build_version="",
        phone="",
        title=review_raw["title"],
        os_version=""
    )
    reviews.append(review)

def check_and_save_review(review_raw: dict, reviews: List[Review]):
    id = review_raw["id"]
    file_path = "fastlane/scripts/review_scrapper/saved_reviews/" + config.REPO_PACKAGE_NAME + ".txt"
    file_content = ""
    if not check_datetime_treshold("iOs", create_datetime_from_iso8601(review_raw['attributes']["createdDate"])):

        if not os.path.isfile(file_path):
            with open(file_path, "w") as file:
                logging.info("Creating file if it doesn't exist")

        with open(file_path, "r") as file:
            file_content = file.read()

        if id not in file_content:
            string = (f"{{id:{id};date:{review_raw['attributes']['createdDate']}}}\n")
            with open(file_path, "a") as file:
                file.write(string)
                create_review(reviews, review_raw["attributes"])