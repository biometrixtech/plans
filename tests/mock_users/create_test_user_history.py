import os
import time
import json
import requests
import test_users
from models.athlete_trend import InsightType, VisualizationType
from aws_xray_sdk.core import xray_recorder
os.environ['ENVIRONMENT'] = 'test'
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from persona import Persona
import soreness_history as sh
from utils import format_datetime
from datetime import datetime, timedelta


def login_user(email):
    body = {"password": "Fathom123!", "personal_data": {"email": email}}
    headers = {"Content-Type": "application/json"}
    url = "http://apis.{env}.fathomai.com/users/2_3/user/login".format(env=os.environ['ENVIRONMENT'])
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response.json()['user']['id'], response.json()['authorization']['jwt']


def clear_fte_category_view(insight_type, visualization_type, jwt, plan_date_time):
    url = "http://apis.{env}.fathomai.com/plans/4_2/trends/first_time_experience/view".format(env=os.environ['ENVIRONMENT'])
    body = {
            "event_date": format_datetime(plan_date_time),
            "insight_type": insight_type.value,
            "visualization_type": visualization_type.value}
    headers = {"Content-Type": "application/json", "Authorization": jwt}
    response = requests.post(url, data=json.dumps(body), headers=headers)

    return response


def clear_fte_category(insight_type, jwt, plan_date_time):
    url = "http://apis.{env}.fathomai.com/plans/4_2/trends/first_time_experience/category".format(env=os.environ['ENVIRONMENT'])
    body = {
            "event_date": format_datetime(plan_date_time),
            "insight_type": insight_type.value}
    headers = {"Content-Type": "application/json", "Authorization": jwt}
    response = requests.post(url, data=json.dumps(body), headers=headers)

    return response


def clear_plan_alerts(insight_type, jwt, plan_date_time):
    url = "http://apis.{env}.fathomai.com/plans/4_2/trends/plan_alerts/clear".format(env=os.environ['ENVIRONMENT'])
    body = {
            "event_date": format_datetime(plan_date_time),
            "insight_type": insight_type.value}
    headers = {"Content-Type": "application/json", "Authorization": jwt}
    response = requests.post(url, data=json.dumps(body), headers=headers)

    return response


if __name__ == '__main__':
    start = time.time()
    history_length = 35

    users = test_users.get_test_users()

    for u in users:
        if u == "full_fte@200.com" or u == "full_fte_2@200.com":
            soreness_history = []
            lower_back_no_question = sh.create_body_part_history(sh.persistent2_no_question(), 12, 0, True)
            soreness_history.append(lower_back_no_question)
            right_pec_29_days_sore_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 2, 2, False)
            soreness_history.append(right_pec_29_days_sore_no_question)
            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            persona1.create_history(days=history_length, suffix='')
            print(time.time() - start)
        elif u == "sore_fte@200.com" or u == "sore_fte_2@200.com":
            soreness_history = []
            lower_back_no_question = sh.create_body_part_history(sh.persistent2_no_question(), 12, 0, True)
            soreness_history.append(lower_back_no_question)
            #right_pec_31_days_sore_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_31_days(), 2, 2, False)
            #soreness_history.append(right_pec_31_days_sore_no_question)
            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            last_plan_date_time = persona1.create_history(days=history_length, suffix='')
            response = clear_fte_category(InsightType.movement_dysfunction_compensation, jwt, last_plan_date_time)
            response_2 = clear_fte_category_view(InsightType.movement_dysfunction_compensation, VisualizationType.pain_functional_limitation, jwt, last_plan_date_time)
            print(time.time() - start)
        elif u == "near_clear@200.com" or u == "near_clear_2@200.com":
            soreness_history = []
            abs_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_25_days(), 3, 0, False)
            soreness_history.append(abs_no_question)
            right_quad_31_days_sore_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 6, 2, False)
            soreness_history.append(right_quad_31_days_sore_no_question)
            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            last_plan_date_time = persona1.create_history(days=history_length, suffix='')
            clear_fte_category(InsightType.movement_dysfunction_compensation, jwt, last_plan_date_time)
            clear_fte_category_view(InsightType.movement_dysfunction_compensation,
                                    VisualizationType.pain_functional_limitation, jwt, last_plan_date_time)
            clear_fte_category_view(InsightType.movement_dysfunction_compensation,
                                    VisualizationType.tight_overactice_underactive, jwt, last_plan_date_time)
            print(time.time() - start)
        elif u == "two_pain@200.com" or u == "two_pain_2@200.com":
            soreness_history = []
            right_calf_no_question = sh.create_body_part_history(sh.persistent2_no_question(), 16, 2, True)
            soreness_history.append(right_calf_no_question)
            right_it_band_no_question = sh.create_body_part_history(sh.persistent2_no_question(), 11, 2, True)
            soreness_history.append(right_it_band_no_question)
            # left_bicep_31_days_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_31_days(), 22, 1, False)
            # soreness_history.append(left_bicep_31_days_no_question)
            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            last_plan_date_time = persona1.create_history(days=history_length, suffix='')
            clear_fte_category(InsightType.movement_dysfunction_compensation, jwt, last_plan_date_time)
            clear_fte_category_view(InsightType.movement_dysfunction_compensation,
                                    VisualizationType.pain_functional_limitation, jwt, last_plan_date_time)
            clear_fte_category_view(InsightType.movement_dysfunction_compensation,
                                    VisualizationType.tight_overactice_underactive, jwt, last_plan_date_time)
            print(time.time() - start)
        elif u == "pain_sore@200.com":
            soreness_history = []
            lower_back_no_question = sh.create_body_part_history(sh.persistent2_no_question(), 12, 0, True)
            soreness_history.append(lower_back_no_question)
            right_pec_29_days_sore_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 2, 2, False)
            soreness_history.append(right_pec_29_days_sore_no_question)
            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            last_plan_date_time = persona1.create_history(days=history_length, suffix='')

            response = clear_plan_alerts(InsightType.movement_dysfunction_compensation,jwt, last_plan_date_time)
            additional_soreness_history = []
            additional_rec_pec_soreness = sh.create_body_part_history(sh.two_days_soreness(), 2, 2, False)
            additional_soreness_history.append(additional_rec_pec_soreness)
            persona1 = Persona(user_id)
            persona1.soreness_history = additional_soreness_history
            last_plan_date_time = persona1.create_history(days=2, suffix='', clear_history=False, start_date_time=datetime.now()+timedelta(days=2))

            print(time.time() - start)

