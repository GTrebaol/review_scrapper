# token_generator.py

import jwt
import time
from misc.config import config


def create_token():
    """
    Create a JWT token required for authenticating with the App Store Connect API.
    """
    header = {
        'alg': 'ES256',
        'kid': config.KEY_ID,
        'typ': 'JWT'
    }
    payload = {
        'iss': config.ISSUER_ID,
        'exp': int(time.time()) + 20 * 60,  # Token is valid for 20 minutes
        'aud': 'appstoreconnect-v1'
    }
    token = jwt.encode(payload, config.PRIVATE_KEY, algorithm='ES256', headers=header)
    return token
