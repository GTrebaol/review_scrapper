# token_generator.py

import jwt
import time
from config import KEY_ID, ISSUER_ID

def create_token(private_key: str):
    """
    Create a JWT token required for authenticating with the App Store Connect API.
    """
    header = {
        'alg': 'ES256',
        'kid': KEY_ID,
        'typ': 'JWT'
    }
    payload = {
        'iss': ISSUER_ID,
        'exp': int(time.time()) + 20 * 60,  # Token is valid for 20 minutes
        'aud': 'appstoreconnect-v1'
    }
    token = jwt.encode(payload, private_key, algorithm='ES256', headers=header)
    return token
