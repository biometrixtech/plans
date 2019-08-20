from jose import jwt
import datetime
import calendar
import time
import cryptography
import os
os.environ['ENVIRONMENT'] = 'dev'
from tests.mock_users.aws_jwt import get_secret


key = {
  "kty": "RSA",
  "d": "dkJZ8z86o22WUk6MbJ0WZtPe0uAutdgorOSaHireaB0z0qdJHQtDq__EANDQSvl83-W_rbzGpX7nA9Pe0ISSyDlQWMneM5Sj8-m2cUeKBHoZbwhsm8dCBpXyMTPWOhJy1yw2WmQaulLPgjKS8jGCdk3W4xLTqm491G-UyepddcEnSxCu_V966iu40T7ymDxSA5Paj8gE44-B_oYzDFo0MRJZ_Xpu9U0LVIYsxMUEJt4u-y1PRY5UZEjq7mW2H9_hhcRVl0fYMnZHtJsSDpEGyytv8rZrlN-zg1wsAN2KkydPnM3Q1CrOZN32CTrZtqlSZsbQPCE_tB6DNn4py2Q6UQ",
  "e": "AQAB",
  "use": "sig",
  "kid": "full_fte_test",
  "alg": "RS256",
  "n": "iYW-shRLlKKcNw8GeB5uGZpD53v8HvAr_nrCo6bJ2op_5_5YcYJLgGiV-hI9DxWk6V4htj3OfQG5Uo3o4W5R3jaqq4-dXL9YS2T3lAaAamvpF8nMMINSac_qvMRb_A9phj-XqYXEZ5yVLebr8s-MZwGlLpc_2_WpmvRhojGzbHEsdx7MP8cG_MOX900uvhj83XK24aKJRZiKBPfjYCmBDCaUQLt4IghBidUy7BNn_T6z7q_PsxulgwkpBvGgDgRNC-806H0vTixo1V4C20YdL_V9kD5xuLL1mFiHOluIXEHKTnIP0PlgiUatHHrQ2-KSifxFs-ANZXxf-l5fIzuhCQ"
}


'''
def service_handler(event, _):
    rs256_key = get_secret('service_jwt_key')
    print(f'Got RS256 key')

    if os.environ['ENVIRONMENT'] == 'dev':
        delta = datetime.timedelta(days=1)
    else:
        delta = datetime.timedelta(days=1)

    token = {
        "auth_time": 1538835893,
        "cognito:username": "00000000-0000-4000-8000-000000000000",
        "custom:role": "service",
        "event_id": str(uuid.uuid4()),
        "iss": os.environ['AWS_LAMBDA_FUNCTION_NAME'],
        "token_use": "id",
        'exp': datetime.datetime.utcnow() + delta,
        'iat': datetime.datetime.utcnow(),
        'sub': '00000000-0000-4000-8000-000000000000',
    }

    print(f'About to compile token')
    ret = {'token': jwt.encode(token, rs256_key, headers={'kid': rs256_key['kid']}, algorithm='RS256')}
    print('Encoded token')
    return ret
'''


def get_jwt():
    rs256_key = get_secret('service_jwt_key')
    print(f'Got RS256 key')

    if os.environ['ENVIRONMENT'] == 'dev':
        delta = datetime.timedelta(days=1)
    else:
        delta = datetime.timedelta(days=1)

    # Generate the JWT
    payload = {
        'iss': 'full_fte',
        'aud': 'fathom_test',
        'exp': datetime.datetime.utcnow() + delta,
        'iat': datetime.datetime.utcnow(),
        'sub': '6a91a0cb-2c90-4b93-94d2-a943c6284af7',
        'scope': 'fathom.plans:read'

    }

    print(rs256_key)
    print(f'About to compile token')
    #ret = {'token': jwt.encode(payload, rs256_key, headers={'kid': rs256_key['kid']}, algorithm='RS256')}
    ret = {'token': jwt.encode(payload, rs256_key, headers={'kid': 'example_001'}, algorithm='RS256')}
    print('Encoded token')
    return ret


test_jwt = get_jwt()
print(test_jwt["token"])