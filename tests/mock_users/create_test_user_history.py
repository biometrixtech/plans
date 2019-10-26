import os
import time
import json
import requests
import test_users
from models.athlete_trend import InsightType
from models.styles import VisualizationType
from aws_xray_sdk.core import xray_recorder
os.environ['ENVIRONMENT'] = 'test'
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from persona import Persona
import soreness_history as sh
from utils import format_datetime
from datetime import datetime, timedelta

plans_version = "4_5"


def login_user(email):
    body = {"password": "Fathom123!", "personal_data": {"email": email}}
    headers = {"Content-Type": "application/json"}
    url = "http://apis.{env}.fathomai.com/users/2_3/user/login".format(env=os.environ['ENVIRONMENT'])
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response.json()['user']['id'], response.json()['authorization']['jwt']


def clear_fte_category_view(insight_type, visualization_type, jwt, plan_date_time):
    url = "http://apis.{env}.fathomai.com/plans/{version}/trends/first_time_experience/view".format(env=os.environ['ENVIRONMENT'], version=plans_version)
    body = {
            "event_date": format_datetime(plan_date_time),
            "insight_type": insight_type.value,
            "visualization_type": visualization_type.value}
    headers = {"Content-Type": "application/json", "Authorization": jwt}
    response = requests.post(url, data=json.dumps(body), headers=headers)

    return response


def clear_fte_category(insight_type, jwt, plan_date_time):
    url = "http://apis.{env}.fathomai.com/plans/{version}/trends/first_time_experience/category".format(env=os.environ['ENVIRONMENT'], version=plans_version)
    body = {
            "event_date": format_datetime(plan_date_time),
            "insight_type": insight_type.value}
    headers = {"Content-Type": "application/json", "Authorization": jwt}
    response = requests.post(url, data=json.dumps(body), headers=headers)

    return response


def clear_plan_alerts(insight_type, jwt, plan_date_time):
    url = "http://apis.{env}.fathomai.com/plans/{version}/trends/plan_alerts/clear".format(env=os.environ['ENVIRONMENT'], version=plans_version)
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
    users.extend(test_users.get_merged_users())

    three_sensor_users = test_users.get_three_sensor_test_users()

    for u in three_sensor_users:
        if u in ["tread_a@200.com", "tread_b@200.com", "tread_run@200.com", "run_a@200.com", "sym@200.com",
                 "half_sym@200.com", "run_a_2@200.com", "sym_2@200.com", "long_3s@200.com", "run_a_mazen@200.com","tread_run_2_mazen@200.com","tread_b_mazen@200.com",
                 "run_a_3@200.com", "sym_3@200.com","tread_a_2@200.com", "tread_b_2@200.com", "tread_run_2@200.com", "half_sym_2@200.com", "long_3s_2@200.com"]:
            soreness_history = []
            user_id, jwt = login_user(u)
            print(u + "=" + user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            if u in ["run_a@200.com"]:
                rpes = [5, None, None, 5, None, 3, None,
                        4, None, 6, None, 5, 5, None,
                        None, 4, None, 3, 5, None, None,
                        6, None, 5, None, 4, None, 3,
                        5, None, 6, None, 5, 4, 6]
                persona1.create_history(days=history_length, suffix='', end_today=True, rpes=rpes)
            else:
                persona1.create_history(days=history_length, suffix='')
            print(time.time() - start)

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
            response = clear_fte_category(InsightType.personalized_recovery, jwt, last_plan_date_time)
            response_2 = clear_fte_category_view(InsightType.personalized_recovery, VisualizationType.prevention, jwt, last_plan_date_time)
            print(time.time() - start)
        elif u in ["near_clear@200.com", "near_clear_2@200.com", "nc_long@200.com", "nc_long_2@200.com", "ivonna+demo2@fathomai.com"]:
            soreness_history = []
            abs_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_25_days(), 3, 0, False)
            soreness_history.append(abs_no_question)
            right_quad_31_days_sore_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 6, 2, False)
            soreness_history.append(right_quad_31_days_sore_no_question)
            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            if u in ["nc_long@200.com", "nc_long_2g@200.com", "ivonna+demo2@fathomai.com"]:
                rpes = [5, None, None, 5, None, 3, None,
                        4, None, 6, None, 5, 5, None,
                        None, 4, None, 3, 5, None, None,
                        6, None, 5, None, 4, None, 3,
                        5, None, 6, None, 5, 4, 6]
                last_plan_date_time = persona1.create_history(days=history_length, suffix='', end_today=True, rpes=rpes)
            else:
                last_plan_date_time = persona1.create_history(days=history_length, suffix='')
                clear_fte_category(InsightType.personalized_recovery, jwt, last_plan_date_time)
                clear_fte_category_view(InsightType.personalized_recovery,
                                        VisualizationType.prevention, jwt, last_plan_date_time)
                clear_fte_category_view(InsightType.personalized_recovery,
                                        VisualizationType.personalized_recovery, jwt, last_plan_date_time)
            print(time.time() - start)
        elif u in ["ts_tread@200.com", "ts_tread_2@200.com"]:
            soreness_history = []
            pecs_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_31_days(), 2, 1, False)
            calves_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_31_days(), 16, 2, False)
            soreness_history.append(pecs_no_question)
            soreness_history.append(calves_no_question)

            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            rpes = [5, None, None, 5, None, 3, None,
                    4, None, 6, None, 5, 5, None,
                    None, 4, None, 3, 5, None, None,
                    6, None, 5, None, 4, None, 3,
                    5, 5, 6, None, 5, 4, 6]
            last_plan_date_time = persona1.create_history(days=history_length, suffix='', end_today=True, rpes=rpes)

            print(time.time() - start)
        elif u in ["ts_pain_long@200.com", "ts_pain_long_2@200.com"]:
            soreness_history = []
            groin_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_31_days(), 5, 2, False)
            quad_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_31_days(), 6, 2, False)
            r_achilles_1_day_pain = sh.create_body_part_history(sh.pre_pad_with_nones([2]), 17, 2, True)
            r_hamstring_1_day_pain = sh.create_body_part_history(sh.pre_pad_with_nones([2]), 15, 2, True)
            soreness_history.append(groin_no_question)
            soreness_history.append(quad_no_question)
            soreness_history.append(r_achilles_1_day_pain)
            soreness_history.append(r_hamstring_1_day_pain)

            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            rpes = [5, None, None, 5, None, 3, None,
                    4, None, 6, None, 5, 5, None,
                    None, 4, None, 3, 5, None, None,
                    6, None, 5, None, 4, None, 3,
                    5, 5, 6, None, 5, 4, 6]
            last_plan_date_time = persona1.create_history(days=history_length, suffix='', end_today=True, rpes=rpes)

            print(time.time() - start)
        elif u in ["full_fte_long@200.com", "full_fte_long_2@200.com"]:
            soreness_history = []
            lower_back_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 12, 0, True)
            r_pec_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 2, 2, False)
            lower_back_1_day_pain = sh.create_body_part_history(sh.pre_pad_with_nones([2]), 12, 0, True)
            l_hamstring_1_day_sore = sh.create_body_part_history(sh.pre_pad_with_nones([2]), 15, 1, False)
            l_calves_1_day_sore = sh.create_body_part_history(sh.pre_pad_with_nones([2]), 16, 1, False)
            soreness_history.append(lower_back_no_question)
            soreness_history.append(r_pec_no_question)
            soreness_history.append(lower_back_1_day_pain)
            soreness_history.append(l_hamstring_1_day_sore)
            soreness_history.append(l_calves_1_day_sore)

            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            rpes = [None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4]
            last_plan_date_time = persona1.create_history(days=history_length, suffix='', end_today=True, rpes=rpes)

            print(time.time() - start)
        elif u in ["full_fte_tread@200.com","full_fte_tread_2@200.com"]:
            soreness_history = []
            lower_back_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 12, 0, True)
            r_pec_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 2, 2, False)
            l_quads_1_day_sore = sh.create_body_part_history(sh.pre_pad_with_nones([2]), 6, 1, False)
            soreness_history.append(lower_back_no_question)
            soreness_history.append(r_pec_no_question)
            soreness_history.append(l_quads_1_day_sore)

            user_id, jwt = login_user(u)
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            rpes = [5, None, None, 5, None, 3, None,
                    4, None, 6, None, 5, 5, None,
                    None, 4, None, 3, 5, None, None,
                    6, None, 5, None, 4, None, 3,
                    5, 5, 6, None, 5, 4, 6]
            last_plan_date_time = persona1.create_history(days=history_length, suffix='', end_today=True, rpes=rpes)

            print(time.time() - start)

        elif u in ["nc_sore_tread@200.com", "nc_sore_tread_2@200.com", "ivonna+demo1@fathomai.com"]:
            soreness_history = []
            abs_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_25_days(), 3, 0, False)
            soreness_history.append(abs_no_question)
            right_quad_31_days_sore_no_question = sh.create_body_part_history(sh.persistent_soreness_no_question_29_days(), 6, 2, False)
            left_quad_1_day_sore = sh.create_body_part_history(sh.pre_pad_with_nones([2, 2]), 6, 1, False)
            soreness_history.append(right_quad_31_days_sore_no_question)
            soreness_history.append(left_quad_1_day_sore)
            user_id, jwt = login_user(u)
            rpes = [None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4]
            print(user_id)
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            last_plan_date_time = persona1.create_history(days=history_length, suffix='', end_today=True, rpes=rpes)
            # clear_fte_category(InsightType.personalized_recovery, jwt, last_plan_date_time)
            # clear_fte_category_view(InsightType.personalized_recovery,
            #                         VisualizationType.prevention, jwt, last_plan_date_time)
            # clear_fte_category_view(InsightType.personalized_recovery,
            #                         VisualizationType.personalized_recovery, jwt, last_plan_date_time)
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
            clear_fte_category(InsightType.personalized_recovery, jwt, last_plan_date_time)
            clear_fte_category_view(InsightType.personalized_recovery,
                                    VisualizationType.prevention, jwt, last_plan_date_time)
            clear_fte_category_view(InsightType.personalized_recovery,
                                    VisualizationType.personalized_recovery, jwt, last_plan_date_time)
            print(time.time() - start)

        elif u in ["two_pain_tread@200.com","two_pain_tread_2@200.com"]:
            soreness_history = []
            right_calf_no_question = sh.create_body_part_history(sh.persistent2_no_question(), 16, 2, True)
            soreness_history.append(right_calf_no_question)
            right_it_band_no_question = sh.create_body_part_history(sh.persistent2_no_question(), 11, 2, True)
            soreness_history.append(right_it_band_no_question)
            right_calf_sore_question = sh.create_body_part_history(sh.persistent_soreness_no_question_31_days(), 16, 2, False)
            soreness_history.append(right_calf_sore_question)
            user_id, jwt = login_user(u)
            print(user_id)
            rpes = [None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4,
                    None, None, 6, None, 5, None, 4]
            persona1 = Persona(user_id)
            persona1.soreness_history = soreness_history
            last_plan_date_time = persona1.create_history(days=history_length, suffix='', end_today=True, rpes=rpes)
            # clear_fte_category(InsightType.personalized_recovery, jwt, last_plan_date_time)
            # clear_fte_category_view(InsightType.personalized_recovery,
            #                         VisualizationType.prevention, jwt, last_plan_date_time)
            # clear_fte_category_view(InsightType.personalized_recovery,
            #                         VisualizationType.personalized_recovery, jwt, last_plan_date_time)
            #
        elif u == "pain_sore@200.com" or u == "pain_sore_2@200.com":
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

            response = clear_plan_alerts(InsightType.personalized_recovery, jwt, last_plan_date_time)
            additional_soreness_history = []
            additional_rec_pec_soreness = sh.create_body_part_history(sh.two_days_soreness(), 2, 2, False)
            additional_soreness_history.append(additional_rec_pec_soreness)
            persona1 = Persona(user_id)
            persona1.soreness_history = additional_soreness_history
            last_plan_date_time = persona1.create_history(days=2, suffix='', clear_history=False, start_date_time=datetime.now()+timedelta(days=2))

            print(time.time() - start)
        elif u == "three_pain@200.com" or u == "three_pain_2@200.com":
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
            clear_fte_category(InsightType.personalized_recovery, jwt, last_plan_date_time)
            clear_fte_category_view(InsightType.personalized_recovery,
                                    VisualizationType.prevention, jwt, last_plan_date_time)
            clear_fte_category_view(InsightType.personalized_recovery,
                                    VisualizationType.personalized_recovery, jwt, last_plan_date_time)

            additional_soreness_history = []
            right_calf_no_question = sh.create_body_part_history(sh.new_persistent_pain_no_question(), 16, 2, True)
            additional_soreness_history.append(right_calf_no_question)
            right_it_band_no_question = sh.create_body_part_history(sh.new_persistent_pain_no_question(), 11, 2, True)
            additional_soreness_history.append(right_it_band_no_question)
            additional_soreness_new = sh.create_body_part_history(sh.new_persistent_pain_no_question(), 9, 2, True)
            additional_soreness_history.append(additional_soreness_new)

            persona1 = Persona(user_id)
            persona1.soreness_history = additional_soreness_history
            last_plan_date_time = persona1.create_history(days=20, suffix='', clear_history=False,
                                                          start_date_time=datetime.now() + timedelta(days=20))

            print(time.time() - start)

