import requests
import os
import datetime
import json
from utils import format_date, format_datetime
BASE_URL = f"https://apis.{os.getenv('ENVIRONMENT', 'dev')}.fathomai.com"
USERS_API_VERSION = os.getenv('USERS_API_VERSION', '2_2')
PLANS_API_VERSION = os.getenv('PLANS_API_VERSION', '3_1')

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


def get_soreness(body_part, side, pain, severity, movement=None, status="dormant_cleared"):
    return {"body_part": body_part,
            "side": side,
            "pain": pain,
            "severity": severity,
            "movement": movement,
            "status": status}


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


def test_get_plan_readiness_not_completed():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
        reset_user()
    event_date = datetime.datetime.now()
    response1 = get_plan(format_date(event_date), format_datetime(event_date))
    data = response1.json()
    body = {'event_date': format_datetime(event_date + datetime.timedelta(seconds=15))}
    response2 = requests.post(f"{PLANS_URL}/daily_readiness/previous",
                              headers=HEADERS,
                              data=json.dumps(body))
    readiness2 = response2.json()['readiness']

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert len(data['daily_plans']) == 1
    plan = data['daily_plans'][0]
    readiness1 = data['readiness']
    assert not plan['daily_readiness_survey_completed']
    assert len(readiness1) > 0
    assert readiness1 == readiness2
    assert len(readiness1['clear_candidates']) == 1
    assert len(readiness1['hist_sore_status']) == 1


def test_get_plan_one_plan_readiness_completed():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
        reset_user()
    event_date = datetime.datetime.now() - datetime.timedelta(days=2)
    response = get_plan(format_date(event_date), format_datetime(event_date))
    data = response.json()
    readiness = data['readiness']

    assert response.status_code == 200
    assert len(data['daily_plans']) == 1
    plan = data['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert len(readiness) == 0


def test_submit_one_session():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
        reset_user()
    event_date = datetime.datetime.now() - datetime.timedelta(days=2)
    response = submit_session(format_datetime(event_date),
                              sport_name=72,
                              duration=30,
                              rpe=5,
                              soreness=[],
                              clear_candidates=[])

    assert response.status_code == 201
    assert len(response.json()['daily_plans']) == 1
    plan = response.json()['daily_plans'][0]
    assert len(plan['training_sessions']) == 2
    assert plan['post_recovery']['minutes_duration'] == 15


def test_submit_readiness_one_soreness():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
        reset_user()
    event_date = datetime.datetime.now()
    soreness = [get_soreness(body_part=14, side=1, pain=False, severity=2, movement=1)]
    response = submit_readiness(event_date,
                                soreness=soreness,
                                clear_candidates=[],
                                sessions=[])

    assert response.status_code == 201
    plan = response.json()['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert plan['pre_recovery']['minutes_duration'] == 15
    assert plan['landing_screen'] == 0


def test_submit_readiness_max_pain_no_prep():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
        reset_user()
    event_date = datetime.datetime.now() + datetime.timedelta(days=2)
    soreness = [get_soreness(body_part=14, side=1, pain=True, severity=4)]
    response = submit_readiness(event_date,
                                soreness=soreness,
                                clear_candidates=[],
                                sessions=[])

    assert response.status_code == 201
    plan = response.json()['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert plan['pre_recovery']['minutes_duration'] == 15
    assert len(plan['pre_recovery']['inhibit_exercises']) == len(plan['pre_recovery']['lengthen_exercises']) == len(plan['pre_recovery']['activate_exercises']) == 0
    assert plan['landing_screen'] == 0


def test_change_active_time_start_and_complete_recovery():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
        reset_user()
    event_date = datetime.datetime.now() - datetime.timedelta(days=4)
    existing_active_time = get_plan(format_date(event_date), format_datetime(event_date)).json()['daily_plans'][0]['post_recovery']['minutes_duration']

    active_time = 15
    if existing_active_time in [15, 0]:
        active_time = 20
    response = change_active_time(event_date, active_time)
    assert response.status_code == 200
    plan = response.json()['daily_plans'][0]

    assert plan['post_recovery']['minutes_duration'] == active_time
    assert plan['landing_screen'] == 2

    response2 = start_recovery(event_date + datetime.timedelta(minutes=2), recovery_type='post')
    assert response2.status_code == 200

    response3 = complete_recovery(event_date + datetime.timedelta(minutes=12),
                                  completed_exercises=[plan["post_recovery"]["inhibit_exercises"][0]['library_id']],
                                  recovery_type='post')
    assert response3.status_code == 202
    plan = response3.json()["daily_plans"][0]
    assert plan["post_recovery_completed"]
    assert plan["post_recovery"]["completed"]
    assert plan["landing_screen"] == 2
    assert not plan["post_recovery"]["display_exercises"]
