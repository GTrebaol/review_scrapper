# android_reviews.py

import json
import logging
import re
from typing import List

import googleapiclient.discovery
from google.oauth2 import service_account

from misc.config import config
from misc.review import Review
from misc.utils import check_datetime_treshold, create_datetime_from_timestamp

logging.basicConfig(level=logging.INFO)


# Table de mappage Android SDK versions et numéros de version Android
android_sdk_mapping = {
    14: "Android 4",
    15: "Android 4.0.3 – 4.0.4",
    16: "Android 4.1",
    17: "Android 4.2",
    18: "Android 4.3",
    19: "Android 4.4",
    20: "Android 4.4W",
    21: "Android 5",
    22: "Android 5.1",
    23: "Android 6",
    24: "Android 7",
    25: "Android 7.1",
    26: "Android 8",
    27: "Android 8.1",
    28: "Android 9",
    29: "Android 10",
    30: "Android 11",
    31: "Android 12",
    32: "Android 12L",
    33: "Android 13",
    34: "Android 14",
    35: "Android 15",
}

# Fonction pour récupérer la version Android à partir d'un numéro de SDK
def get_android_version(sdk_version):
    return android_sdk_mapping.get(sdk_version, f"Version inconnue : {sdk_version} ")

def get_reviews() -> List[Review]:
    finished = False
    start_index = 0
    reviews = []
    while not finished:
        logging.info("Calling Google services...")
        response_reviews = download_review(start_index=start_index)
        if "reviews" not in response_reviews or len(response_reviews["reviews"]) == 0:
            logging.info("No reviews")
            finished = True
        else:
            for item in response_reviews["reviews"]:
                create_review(reviews=reviews, review_raw=item)
            finished = len(reviews) < config.REVIEWS_FETCH_QUANTITY
            logging.info(f"Fetched and kept {len(reviews)} reviews.")
            logging.info("We're done here." if finished else "Fetching the next batch.")
            start_index += config.REVIEWS_FETCH_QUANTITY
    return reviews


def download_review(start_index: int) -> dict:
    try:
        json_credentials = json.loads(config.JSON_KEY_DATA)
        credentials = service_account.Credentials.from_service_account_info(
            json_credentials
        )
        service = googleapiclient.discovery.build(
            "androidpublisher", "v3", credentials=credentials
        )
        return (
            service.reviews()
            .list(
                packageName=config.REPO_PACKAGE_NAME,
                maxResults=config.REVIEWS_FETCH_QUANTITY,
            )
            .execute()
        )
    except Exception as e:
        logging.error(e)
        return {}


def create_review(reviews: List[Review], review_raw: dict):
    comment = review_raw["comments"][0]["userComment"]
    truncated_comment = (
        comment["text"][:99] + "..." if len(comment["text"]) > 100 else comment["text"]
    )
    version = "-"
    version_code = "-"
    phone = "-"
    author_name = "Monsieur Untel"
    version_android = "Version inconnue"
    if "appVersionName" in comment:
        version = comment["appVersionName"]
    if "deviceMetadata" in comment:
        phone = comment["deviceMetadata"]["productName"]
    if "appVersionCode" in comment:
        version_code = comment["appVersionCode"]
    if "authorName" in review_raw:
        author_name = review_raw["authorName"]
    if "androidOsVersion" in comment:
        version_android = get_android_version(comment["androidOsVersion"])

    review = Review(
        os="Android",
        author_name=author_name,
        rating=comment["starRating"],
        truncated_comment=re.sub(r'"', "'", re.sub(r"\t", "", truncated_comment)),
        content=re.sub(r'"', "'", re.sub(r"\t", "", comment["text"])),
        datetime=create_datetime_from_timestamp(
            float(comment["lastModified"]["seconds"])
        ),
        version=version,
        build_version=version_code,
        os_version=version_android,
        phone=phone,
        title="",
    )
    if not check_datetime_treshold(review):
        reviews.append(review)
