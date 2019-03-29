import requests
import os
import datetime
import json
from utils import format_datetime
BASE_URL = f"https://apis.{os.getenv('ENVIRONMENT', 'dev')}.fathomai.com"
USERS_API_VERSION = os.getenv('USERS_API_VERSION', '2_2')
PLANS_API_VERSION = os.getenv('PLANS_API_VERSION', '3_1_1-dev_0')

USERS_URL = f"{BASE_URL}/users/{USERS_API_VERSION}"
PLANS_URL = f"{BASE_URL}/plans/{PLANS_API_VERSION}"
# user:
USER = {'email': "dipesh+persona1@fathomai.com",
        'id': None}
# Headers:
HEADERS = {
    "Authorization": None,
    "Content-Type": "application/json"
  }



def get_soreness(body_part, side, pain, severity, movement=None, status="dormant_cleared"):
    return {"body_part": body_part,
            "side": side,
            "pain": pain,
            "severity": severity,
            "movement": movement,
            "status": status}


def login_user(email):
    body = {"password": "Fathom123!", "personal_data": {"email": email}}
    url = f"{USERS_URL}/user/login"
    response = requests.post(url, data=json.dumps(body), headers=HEADERS).json()
    USER['id'] = response['user']['id']
    print(USER['id'])
    HEADERS['Authorization'] = response['authorization']['jwt']


def reset_user():
    body = {"event_date": format_datetime(datetime.datetime.now()), "copy_all": False}
    url = f"{PLANS_URL}/misc/copy_test_data"
    response = requests.post(url, data=json.dumps(body), headers=HEADERS).json()
    assert response['message'] == 'success'


def get_previous_soreness(event_date):
    body = {'event_date': format_datetime(event_date)}
    response = requests.post(f"{PLANS_URL}/daily_readiness/previous",
                             headers=HEADERS,
                             data=json.dumps(body))
    return response


def get_plan(start_date, event_date):
    body = {'start_date': start_date,
            'event_date': event_date}
    response = requests.post(f"{PLANS_URL}/daily_plan",
                             headers=HEADERS,
                             data=json.dumps(body))
    return response


def submit_readiness(event_date, soreness, clear_candidates, sessions):
    body = {"date_time": format_datetime(event_date),
            "soreness": soreness,
            "clear_candidates": clear_candidates,
            "sessions": sessions}
    response = requests.post(f"{PLANS_URL}/daily_readiness",
                             headers=HEADERS,
                             data=json.dumps(body))
    return response


def change_active_time(event_date, active_time):
    body = {"event_date": format_datetime(event_date),
            "active_time": active_time}
    response = requests.patch(f"{PLANS_URL}/active_recovery/active_time",
                              headers=HEADERS,
                              data=json.dumps(body))
    return response


def start_recovery(event_date, recovery_type="pre"):
    body = {"event_date": format_datetime(event_date),
            "recovery_type": recovery_type}
    response = requests.post(f"{PLANS_URL}/active_recovery",
                             headers=HEADERS,
                             data=json.dumps(body))
    return response


def complete_recovery(event_date, completed_exercises, recovery_type="pre"):
    body = {"event_date": format_datetime(event_date),
            "recovery_type": recovery_type,
            "completed_exercises": completed_exercises}
    response = requests.patch(f"{PLANS_URL}/active_recovery",
                              headers=HEADERS,
                              data=json.dumps(body))
    return response


def submit_session(event_date, sport_name, duration, rpe, soreness, clear_candidates):
    post_session_survey = {"event_date": event_date,
                           "RPE": rpe,
                           "soreness": soreness,
                           "clear_candidates": clear_candidates}
    session = {"event_date": event_date,
               "sport_name": sport_name,
               "session_type": 6,
               "source": 0,
               "duration": duration,
               "post_session_survey": post_session_survey}
    body = {"event_date": event_date,
            "sessions": [session]}
    response = requests.post(f"{PLANS_URL}/session",
                             headers=HEADERS,
                             data=json.dumps(body))
    return response
