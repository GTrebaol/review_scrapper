# ios_reviews.py

import requests
from misc.review import Review
from misc.token_generator import create_token
from typing import List

def get_ios_reviews(app_id: str, private_key: str) -> List[Review]:
    token = create_token(private_key=private_key)
    url = f'https://api.appstoreconnect.apple.com/v1/apps/{app_id}/customerReviews'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return parse_ios_reviews(response.json())
    else:
        print(f"Error retrieving reviews {response.status_code}")
        return []

def parse_ios_reviews(response: dict) -> List[Review]:
    reviews = []
    for item in response.get('data', []):
        attributes = item['attributes']
        review = Review(
            os="iOS",
            author_name=attributes['userName'],
            rating=attributes['rating'],
            content=attributes['review'],
            timestamp=attributes['date'],
            version=attributes['appVersion'],
            build_version=attributes['buildVersion'],
            phone=attributes['device'],
            truncated_comment=attributes['review'][:200] + '...' if len(attributes['review']) > 200 else attributes['review']
        )
        reviews.append(review)
    return reviews
