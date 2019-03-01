import os
import time
import json
from aws_xray_sdk.core import xray_recorder
os.environ['ENVIRONMENT'] = 'test'
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
import requests

from persona import Persona
from soreness_history import create_body_part_history, persistent2_question, acute_pain_no_question

def login_user(email):
    body = {"password": "Fathom123!", "personal_data": {"email": email}}
    headers = {"Content-Type": "application/json"}
    url = "http://apis.{env}.fathomai.com/users/2_1/user/login".format(env=os.environ['ENVIRONMENT'])
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response.json()['user']['id']

def create_persona_with_two_historic_soreness(days):
    soreness_history = []
    right_knee_persistent2_question = create_body_part_history(persistent2_question(), 7, 2, True)
    soreness_history.append(right_knee_persistent2_question)
    left_knee_acute_pain_no_question = create_body_part_history(acute_pain_no_question(), 7, 1, True)
    soreness_history.append(left_knee_acute_pain_no_question)
    user_id = login_user("dipesh+persona1@fathomai.com")
    print(user_id)
    persona1 = Persona(user_id)
    persona1.soreness_history = soreness_history
    persona1.create_history(days=days)


if __name__ == '__main__':
    start = time.time()
    history_length = 35
    create_persona_with_two_historic_soreness(history_length)
    print(time.time() - start)
#    update_metrics(user_id, event_date)