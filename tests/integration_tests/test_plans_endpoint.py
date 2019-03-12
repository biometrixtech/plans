import requests, os
import time
import json
os.environ['ENVIRONMENT'] = 'dev'
BASE_URL = os.getenv("BASE_URL", "https://apis.dev.fathomai.com")
# user:
USER = {'email': "integrationtest@fathomai.com",
        'id': None}
# Headers:
HEADERS = {
    "Authorization": None,
    "Content-Type": "application/json"
  }

def login_user(email):
    body = {"password": "Fathom123!", "personal_data": {"email": email}}
    url = "{}/users/2_1/user/login".format(BASE_URL, env=os.getenv('ENVIRONMENT', 'dev'))
    response = requests.post(url, data=json.dumps(body), headers=HEADERS).json()
    USER['id'] = response['user']['id']
    HEADERS['Authorization'] = response['authorization']['jwt']

def get_plan(user_id, start_date, event_date):
    body = {'user_id': user_id,
            'start_date': start_date,
            'event_date': event_date}
    response = requests.post("{}/plans/2_2/daily_plan".format(BASE_URL),
                             headers=HEADERS,
                             data=json.dumps(body))
    return response

def test_get_plan_readiness_not_completed():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
    response1 = get_plan(USER['id'], '2019-01-01', '2019-01-01T13:00:01Z')
    data = response1.json()
    body = {'event_date': '2019-01-01T13:00:01Z'}
    response2 = requests.post("{}/plans/2_2/daily_readiness/previous".format(BASE_URL),
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

def test_get_plan_one_plan_readiness_completed():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
    response = get_plan("test_user", '2018-06-27', '2018-06-27T13:00:01Z')
    data = response.json()
    readiness = data['readiness']

    assert response.status_code == 200
    assert len(data['daily_plans']) == 1
    plan = data['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert len(readiness) == 0

def test_submit_readiness_one_soreness():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
    body = {"date_time": "2018-01-02T13:00:00Z",
            "user_id":USER['id'],
            "soreness":[{
                        "body_part": 14,
                        "severity": 2,
                        "pain": False,
                        "side": 1
                    }],
            "clear_candidates": []}
    response = requests.post("{}/plans/2_2/daily_readiness".format(BASE_URL),
                             headers=HEADERS,
                             data=json.dumps(body))

    assert response.status_code == 201
    plan = response.json()['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert plan['pre_recovery']['minutes_duration'] == 15
    assert plan['landing_screen'] == 0

def test_change_active_time():
    if HEADERS['Authorization'] is None:
        login_user(USER['email'])
    existing_active_time = get_plan(USER['id'], '2018-01-01', "2018-01-01T13:01:00Z").json()['daily_plans'][0]['pre_recovery']['minutes_duration']

    if existing_active_time == 15:
        active_time = 20
    elif existing_active_time == 20:
        active_time = 15
    body = {"event_date": "2018-01-01T13:01:00Z",
            "user_id": USER['id'],
            "active_time": active_time}
    response = requests.patch("{}/plans/2_2/active_recovery/active_time".format(BASE_URL),
                             headers=HEADERS,
                             data=json.dumps(body))
    assert response.status_code == 200
    plan = response.json()['daily_plans'][0]

    assert plan['pre_recovery']['minutes_duration'] == active_time
    assert plan['landing_screen'] == 0


