from jose import jwt
import datetime
import os
os.environ['ENVIRONMENT'] = 'soflete-test'
from tests.mock_users.aws_jwt import get_secret


def get_jwt():
    rs256_key = get_secret('service_jwt_key')
    print(f'Got RS256 key')

    if os.environ['ENVIRONMENT'] == 'dev':
        delta = datetime.timedelta(days=1)
    else:
        delta = datetime.timedelta(days=1)

    # Generate the JWT
    payload = {
        'iss': 'soflete',
        'aud': 'fathom',
        'exp': datetime.datetime.utcnow() + delta,
        'iat': datetime.datetime.utcnow(),
        'sub': '6a91a0cb-2c90-4b93-94d2-a943c6284af7',
        'scope': 'fathom.plans:read'

    }

    print(rs256_key)
    print(f'About to compile token')
    ret = {'token': jwt.encode(payload, rs256_key, headers={'kid': 'soflete_001'}, algorithm='RS256')}  # soflete_001 is for test environment
    print('Encoded token')
    return ret


test_jwt = get_jwt()
print(test_jwt["token"])
