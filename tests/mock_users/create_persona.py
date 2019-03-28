import os
import time
import json
import requests
from aws_xray_sdk.core import xray_recorder
os.environ['ENVIRONMENT'] = 'dev'
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from persona import Persona
import soreness_history as sh
def login_user(email):
    body = {"password": "Fathom123!", "personal_data": {"email": email}}
    headers = {"Content-Type": "application/json"}
    url = "http://apis.{env}.fathomai.com/users/2_1/user/login".format(env=os.environ['ENVIRONMENT'])
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response.json()['user']['id']

def create_persona_with_two_historic_soreness(days):
    soreness_history = []
    right_knee_persistent2_question = sh.create_body_part_history(sh.persistent2_question(), 7, 2, True)
    soreness_history.append(right_knee_persistent2_question)
    left_knee_acute_pain_no_question = sh.create_body_part_history(sh.acute_pain_no_question(), 7, 1, True)
    soreness_history.append(left_knee_acute_pain_no_question)
    user_id = login_user("dipesh+persona1@fathomai.com")
    print(user_id)
    persona1 = Persona(user_id)
    persona1.soreness_history = soreness_history
    persona1.create_history(days=days)

def create_persona_with_eight_historic_soreness(days):
    soreness_history = []
    right_knee_persistent2_question = sh.create_body_part_history(sh.persistent2_question(), 7, 2, True)
    left_knee_acute_pain_no_question = sh.create_body_part_history(sh.acute_pain_no_question(), 7, 1, True)
    lower_back_acute_pain_question = sh.create_body_part_history(sh.acute_pain_question(), 12, 0, True)
    right_shin_persistent2_no_question = sh.create_body_part_history(sh.persistent2_no_question(), 8, 2, True)
    left_glutes_persistent_soreness_question = sh.create_body_part_history(sh.persistent_soreness_question(), 14, 1, False)
    right_glutes_persistent_soreness_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question(), 14, 2, False)
    left_groin_persistent_pain_question = sh.create_body_part_history(sh.persistent_pain_question(), 5, 1, True)
    right_groin_persistent_pain_no_question = sh.create_body_part_history(sh.persistent_pain_no_question(), 5, 2, True)


    soreness_history.append(right_knee_persistent2_question)
    soreness_history.append(left_knee_acute_pain_no_question)
    soreness_history.append(lower_back_acute_pain_question)
    soreness_history.append(right_shin_persistent2_no_question)
    soreness_history.append(left_glutes_persistent_soreness_question)
    soreness_history.append(right_glutes_persistent_soreness_no_question)
    soreness_history.append(left_groin_persistent_pain_question)
    soreness_history.append(right_groin_persistent_pain_no_question)
    user_id = login_user("dipesh+persona2@fathomai.com")
    print(user_id)
    persona2 = Persona(user_id)
    persona2.soreness_history = soreness_history
    persona2.create_history(days=days)

if __name__ == '__main__':
    start = time.time()
    history_length = 35
    create_persona_with_two_historic_soreness(history_length)
    create_persona_with_eight_historic_soreness(history_length)
    print(time.time() - start)
#    update_metrics(user_id, event_date)