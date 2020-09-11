import requests
import os
from utils import format_datetime
import datetime, pytz
import json
BASE_URL = f"https://apis.{os.getenv('ENVIRONMENT', 'dev')}.fathomai.com"
USERS_API_VERSION = os.getenv('USERS_API_VERSION', '2_4')
PLANS_API_VERSION = os.getenv('PLANS_API_VERSION', 'latest')

USERS_URL = f"{BASE_URL}/users/{USERS_API_VERSION}"
PLANS_URL = f"{BASE_URL}/plans/{PLANS_API_VERSION}"
# user:
USER = {'email': "dipesh+mvp@fathomai.com",
        'id': None}
# Headers:
HEADERS = {
    "Authorization": None,
    "Content-Type": "application/json"
  }


def login_user(email):
    body = {"password": "Fathom123!", "personal_data": {"email": email}}
    url = f"{USERS_URL}/user/login"
    response = requests.post(url, data=json.dumps(body), headers=HEADERS).json()
    USER['id'] = response['user']['id']
    print(USER['id'])
    HEADERS['Authorization'] = response['authorization']['jwt']


def submit_session_to_get_responsive_recovery(data):
    # body = data
    user_id = USER['id']
    response = requests.post(f"{PLANS_URL}/responsive_recovery/{user_id}",
                             headers=HEADERS,
                             data=json.dumps(data))
    return response