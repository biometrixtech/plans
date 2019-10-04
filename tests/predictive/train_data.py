import pytest
import os
from tests.predictive.modeling import Descriptor, DescriptorType, BodyPartDescriptors, BodyPartModel, BodyPartPrediction
from aws_xray_sdk.core import xray_recorder

os.environ["ENVIRONMENT"] = "production"

xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn import feature_selection, metrics, model_selection
import statistics
from collections import namedtuple
from logic.soreness_processing import SorenessCalculator
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from models.post_session_survey import PostSessionSurvey
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus, BodyPartSide
from models.body_parts import BodyPart, BodyPartLocation
from config import get_secret
from utils import parse_date, format_date, format_datetime
from statistics import stdev, mean
from datetime import timedelta
from datastores.predictive_datastore import PredictiveDatastore
from logic.stats_processing import StatsProcessing
import numpy as np


@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):


    config = get_secret('mongo')
    os.environ["MONGO_HOST"] = config['host']
    os.environ["MONGO_REPLICASET"] = config['replicaset']
    os.environ["MONGO_DATABASE"] = config['database']
    os.environ["MONGO_USER"] = config['user']
    os.environ["MONGO_PASSWORD"] = config['password']
    os.environ["MONGO_COLLECTION_DAILYREADINESS"] = config['collection_dailyreadiness']
    os.environ["MONGO_COLLECTION_DAILYPLAN"] = config['collection_dailyplan']
    os.environ["MONGO_COLLECTION_EXERCISELIBRARY"] = config['collection_exerciselibrary']
    os.environ["MONGO_COLLECTION_TRAININGSCHEDULE"] = config['collection_trainingschedule']
    os.environ["MONGO_COLLECTION_ATHLETESEASON"] = config['collection_athleteseason']
    os.environ["MONGO_COLLECTION_ATHLETESTATS"] = config['collection_athletestats']
    os.environ["MONGO_COLLECTION_COMPLETEDEXERCISES"] = config['collection_completedexercises']

def get_dates(start_date, end_date):

    dates = []

    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates

def get_ps_survey_soreness_list(survey_list):

        soreness_list = []

        for c in survey_list:

            for s in c.survey.soreness:
                s.reported_date_time = format_date(c.event_date)
                soreness_list.append(s)

        return soreness_list

def get_readiness_soreness_list(survey_list):

        soreness_list = []

        for c in survey_list:

            for s in c.soreness:
                #s.reported_date_time = format_date(c.event_date)
                s.reported_date_time = c.event_date
                soreness_list.append(s)

        return soreness_list

def merge_soreness_from_surveys(readiness_survey_soreness_list, ps_survey_soreness_list):

        soreness_list = []
        merged_soreness_list = []

        soreness_list.extend(readiness_survey_soreness_list)
        soreness_list.extend(ps_survey_soreness_list)

        grouped_severity = {}
        grouped_movement = {}

        ns = namedtuple("ns", ["location", "is_pain", "side", "reported_date_time"])

        for s in soreness_list:
            ns_new = ns(s.body_part.location, s.pain, s.side, format_date(s.reported_date_time.date()))
            severity = 0
            movement = 0
            if s.severity is not None:
                severity = s.severity
            if s.movement is not None:
                movement = s.movement
            if ns_new in grouped_severity:
                grouped_severity[ns_new] = max(grouped_severity[ns_new], severity)
            else:
                grouped_severity[ns_new] = severity
            if ns_new in grouped_movement:
                grouped_movement[ns_new] = max(grouped_movement[ns_new], movement)
            else:
                grouped_movement[ns_new] = movement

        for r in grouped_severity:

            s = Soreness()
            s.body_part = BodyPart(r.location, None)
            s.side = r.side
            s.reported_date_time = r.reported_date_time
            s.severity = grouped_severity[r]
            s.movement = grouped_movement[r]  # these should be equivalent even though looping through severity
            s.pain = r.is_pain
            merged_soreness_list.append(s)

        return merged_soreness_list


def get_ramp(training_volume_date_dictionary, current_date):

    one_week_ago = current_date - timedelta(days=6)
    two_weeks_ago = current_date - timedelta(days=13)

    current_week_training_volume = 0
    last_week_training_volume = 0

    for dt, tv in training_volume_date_dictionary.items():
        if dt >= one_week_ago:
            current_week_training_volume += tv
        elif two_weeks_ago <= dt < one_week_ago:
            last_week_training_volume += tv

    if last_week_training_volume > 0:
        return round(current_week_training_volume / last_week_training_volume, 2)
    else:
        return 0


def is_high_workout(training_volume_date_dictionary, current_date):

    todays_training_volume = training_volume_date_dictionary[current_date]

    one_week_ago = current_date - timedelta(days=6)

    training_volume_list = []

    for dt, tv in training_volume_date_dictionary.items():
        if dt >= one_week_ago:
            training_volume_list.append(tv)

    if len(training_volume_list) == 2:
        if todays_training_volume > training_volume_list[0]:
            return True
    if len(training_volume_list) > 2:
        mean_volume = mean(training_volume_list)
        if todays_training_volume > mean_volume:
            return True
        return False

    else:
        return False


def get_inflammation_score(tissue_overload_dictionary, soreness_date_dictionary,  current_date, target_body_part):

    three_days_ago = current_date - timedelta(days=2)
    ten_days_ago = current_date - timedelta(days=9)

    is_tissue_overload = False

    for dt, t in tissue_overload_dictionary.items():
        if dt >= three_days_ago:
            if t:
                is_tissue_overload = True
                break

    found_pain = False

    for dt, s in soreness_date_dictionary.items():
        if dt >= ten_days_ago:
            pain_list = [s for s in soreness_date_dictionary[dt] if
                         s.body_part.location.value == target_body_part.body_part_location.value and s.side == target_body_part.side and s.pain]
            if len(pain_list) > 0:
                found_pain = True

    todays_soreness_severity = 0
    todays_soreness = [s for s in soreness_date_dictionary[current_date] if s.body_part.location.value == target_body_part.body_part_location.value and s.side == target_body_part.side]

    if len(todays_soreness) > 0 and is_tissue_overload:
        todays_soreness_severity = todays_soreness[0].severity
        if todays_soreness[0].pain and not found_pain:
            todays_soreness_severity += todays_soreness_severity + 1

    return todays_soreness_severity


def get_muscle_spams_score(inflammation_dictionary, soreness_date_dictionary,  current_date, related_joints):

    four_days_ago = current_date - timedelta(days=3)
    ten_days_ago = current_date - timedelta(days=9)

    is_inflammation = False
    inflammation_count = 0

    for dt, t in inflammation_dictionary.items():
        if dt >= four_days_ago:
            if t:
                is_inflammation = True
                inflammation_count += 1

    found_pain = False
    max_pain_severity = 0
    score = 0

    for dt, s in soreness_date_dictionary.items():
        if dt >= ten_days_ago:
            for r in related_joints:
                #TODO - manage bilateral / non-bilateral linkages
                pain_list = [s for s in soreness_date_dictionary[dt] if
                             s.body_part.location.value == r.body_part_location.value and s.side == r.side and s.pain]
                if len(pain_list) > 0:
                    found_pain = True
                    max_pain_severity = max(max_pain_severity, pain_list[0].severity)

    if found_pain and inflammation_count >= 1:
        score = max_pain_severity

    return score


def find_user_history():
    start_date = parse_date("2019-05-01")
    end_date = parse_date("2019-08-31")

    users = []
    user_names = []

    users.append('e1b09f08-fc83-4957-9321-463001650440')
    user_names.append('becky')

    # users.append('06f2c55d-780c-47cf-9742-a74535bea45f')
    # user_names.append('rachael')
    #
    # users.append('55b040ff-4eab-4469-be30-39ab4574c3b3')
    # user_names.append('gary')
    #
    # users.append('589c625a-cdd6-429f-aa36-3ae66756af3b')
    # user_names.append('cm')
    #
    # users.append('d061ca16-b1e1-4d20-b483-8f9c740064c0')
    # user_names.append('ryan')
    #
    # users.append('e83814ba-3784-4b24-8a23-95cd8d238045')
    # user_names.append('connor')
    #
    # users.append('e9d78b6f-8695-4556-9369-d6a5702c6cc7')
    # user_names.append('matthew')
    #
    # users.append('a8172baf-4ca9-4676-84a6-e64f3cd50b13')
    # user_names.append('doug')

    pred_datastore = PredictiveDatastore()
    athlete_ids = pred_datastore.get()
    user_ids = []
    for a in athlete_ids:
        user_ids.append(a["athlete_id"])
    #user_ids.append(users[0])
    #user_ids.extend(users) - dont need this because we're doing all!

    # users.append("4a40acbd-cdc0-4817-9226-d5181be85bea")
    # users.append("2d68623c-8706-4ce2-a937-8e7ab2ff9af4")
    # users.append("fc8540fd-467a-4fea-a3c5-54557c4b704d")
    # users.append("a97765bb-3d11-42ee-93fc-d4e069efa7fa")
    # users.append("aa14351b-e714-4790-a75f-a3d6f2ed45af")
    # users.append("e3956862-2dbb-47ac-83dd-1ee47259228d")
    # users.append("d1649300-fac5-4147-ae48-b71138474bc1")
    # users.append("723a8085-2700-4690-869a-ebb11a0ebf58")
    # users.append("49bc5521-a70b-45c4-b179-7dd8442e2abd")
    # users.append("e06456d8-544e-47ca-ac94-3191717131ab")
    # users.append("5e49be59-af1b-48c1-9df6-7f9e0c76b8ee")
    # users.append("e28dfbbc-70f1-4dc6-90ea-43d7adfae2ab")
    # users.append("4976c162-d712-4f26-9f7d-055c0c7e6f91")
    # users.append("c4324949-4f44-4ccf-b602-ce64304c0d8c")
    # users.append("1ea753c9-4179-49c2-92ea-e1e6e667c1c0")
    # users.append("2c681bcf-7123-406a-ae82-5f80c94bd806")
    # users.append("0be06602-c74c-4073-8f10-688e95e922ac")
    # users.append("b5f5775b-f484-47a0-87d6-1f06544a232a")
    # users.append("20bd1cd2-7aad-41a1-97ec-5a6bd8f45877")
    # users.append("c4825306-f8fd-4a56-95b3-b728c329e389")
    # users.append("c25a1e90-bf6d-47d4-bac3-5943dfa04da7")

    data = []
    y_data = []
    x_column_names = []
    y_column_names = []

    inflammation_count = 0
    muscle_spasm_count = 0

    #for u in range(0, len(users)):
    for u in range(0, len(user_ids)):
        #user_id = users[u]
        user_id = user_ids[u]
        #user_id = u
        #user_name = user_names[u]
        user_name = ''

        dates = get_dates(start_date, end_date)

        prod_plans_dao = DailyPlanDatastore()
        prod_plans = prod_plans_dao.get(user_id, format_date(start_date), format_date(end_date))
        athlete_stats_dao = AthleteStatsDatastore()
        athlete_stats = athlete_stats_dao.get(user_id)

        all_daily_readiness_surveys = [plan.daily_readiness_survey for plan in prod_plans if
                                       plan.daily_readiness_survey is not None]

        post_session_surveys = []
        training_sessions = []
        for plan in prod_plans:
            post_surveys = \
                [PostSessionSurvey.post_session_survey_from_training_session(session.post_session_survey, user_id, session.id, session.session_type().value, plan.event_date)
                 for session in plan.training_sessions if session is not None]
            post_session_surveys.extend([s for s in post_surveys if s is not None])
            training_sessions.extend(plan.training_sessions)

        descriptor_list = []

        target_body_part = BodyPartSide(BodyPartLocation.quads, 1)
        related_joints = [BodyPartSide(BodyPartLocation.knee, 1),
                          BodyPartSide(BodyPartLocation.hip_flexor, 1),
                          BodyPartSide(BodyPartLocation.lower_back, 0)]

        training_volume_dictionary = {}
        tissue_overload_dictionary = {}
        inflammation_dictionary = {}
        muscle_spasm_ditionary = {}
        soreness_date_dictionary = {}
        #ramp_dictionary = {}

        for d in dates:
            #day_0_start_date = d - timedelta(days=15)
            #date_series = get_dates(day_0_start_date, d - timedelta(days=2))

            #soreness_date_dictionary = dict.fromkeys(date_series, [])
            #training_session_date_dictionary = dict.fromkeys(date_series, [])
            #training_volume_date_dictionary = dict.fromkeys(date_series, [])
            #ramp_dictionary = dict.fromkeys(date_series, [])

            #for s in date_series:
            daily_readiness_surveys = [a for a in all_daily_readiness_surveys if format_date(a.event_date) == format_date(d.date())]
            daily_ps_surveys = [a for a in post_session_surveys if format_date(a.event_date) == format_date(d.date())]

            daily_soreness_list = merge_soreness_from_surveys(get_readiness_soreness_list(daily_readiness_surveys),
                                                    get_ps_survey_soreness_list(daily_ps_surveys))

            training_session_list = [t for t in training_sessions if t.event_date.date() == d.date()]

            soreness_date_dictionary[d] = daily_soreness_list

            training_volume = 0

            for t in training_session_list:
                training_volume += t.training_volume(athlete_stats.load_stats)

            training_volume_dictionary[d] = training_volume
            two_days_ago_ramp = get_ramp(training_volume_dictionary, d)
            #ramp_dictionary[d] = two_days_ago_ramp
            two_days_ago_high_workout = is_high_workout(training_volume_dictionary, d)
            is_tissue_overload = two_days_ago_high_workout
            tissue_overload_dictionary[d] = is_tissue_overload

            # TODO differentiate high volume from high intensity
            # TODO determine what is "high" (right now just using > mean)

            inflammation_score = get_inflammation_score(tissue_overload_dictionary, soreness_date_dictionary, d, target_body_part)
            is_inflammation = (inflammation_score > 0)
            if is_inflammation:
                inflammation_count += 1
            inflammation_dictionary[d] = inflammation_score

            muscle_spams_score = get_muscle_spams_score(inflammation_dictionary, soreness_date_dictionary, d, related_joints)
            is_muscle_spasm = (muscle_spams_score > 0)
            if is_muscle_spasm:
                muscle_spasm_count += 1
            muscle_spasm_ditionary[d] = muscle_spams_score



            # todays_daily_readiness_surveys = [a for a in all_daily_readiness_surveys if format_date(a.event_date) == format_date(two_days_ago.date())]
            # todays_daily_ps_surveys = [a for a in post_session_surveys if format_date(a.event_date) == format_date(d.date())]
            #
            # todays_soreness_list = merge_soreness_from_surveys(get_readiness_soreness_list(todays_daily_readiness_surveys),
            #                                                   get_ps_survey_soreness_list(todays_daily_ps_surveys))


            left_quad = BodyPartSide(BodyPartLocation(6), 1)
            right_quad = BodyPartSide(BodyPartLocation(6), 2)
            left_knee = BodyPartSide(BodyPartLocation(7), 1)
            right_knee = BodyPartSide(BodyPartLocation(7), 2)
            lower_back = BodyPartSide(BodyPartLocation(12), 0)
            left_hip = BodyPartSide(BodyPartLocation(4), 1)
            right_hip = BodyPartSide(BodyPartLocation(4), 2)

            left_hamstring = BodyPartSide(BodyPartLocation(15), 1)
            right_hamstring = BodyPartSide(BodyPartLocation(15), 2)
            left_glute = BodyPartSide(BodyPartLocation(14), 1)
            right_glute = BodyPartSide(BodyPartLocation(14), 2)
            left_it = BodyPartSide(BodyPartLocation(11), 1)
            right_it = BodyPartSide(BodyPartLocation(11), 2)
            left_groin = BodyPartSide(BodyPartLocation(5), 1)
            right_groin = BodyPartSide(BodyPartLocation(5), 2)

            left_quad_prediction = BodyPartPrediction(left_quad)
            #left_quad_prediction.set_predictions(soreness_date_dictionary[two_days_ago], inflammation_dictionary[two_days_ago], muscle_spasm_ditionary[two_days_ago])

            left_quad_descriptors = BodyPartDescriptors(left_quad)
            right_quad_descriptors = BodyPartDescriptors(right_quad)
            left_knee_descriptors = BodyPartDescriptors(left_knee)
            right_knee_descriptors = BodyPartDescriptors(right_knee)
            lower_back_descriptors = BodyPartDescriptors(lower_back)
            left_hip_descriptors = BodyPartDescriptors(left_hip)
            right_hip_descriptors = BodyPartDescriptors(right_hip)

            left_hamstring_descriptors = BodyPartDescriptors(left_hamstring)
            right_hamstring_descriptors = BodyPartDescriptors(right_hamstring)
            left_glute_descriptors = BodyPartDescriptors(left_glute)
            right_glute_descriptors = BodyPartDescriptors(right_glute)
            left_it_descriptors = BodyPartDescriptors(left_it)
            right_it_descriptors = BodyPartDescriptors(right_it)
            left_groin_descriptors = BodyPartDescriptors(left_groin)
            right_groin_descriptors = BodyPartDescriptors(right_groin)

            quad_model = BodyPartModel()
            quad_model.ramp = two_days_ago_ramp
            quad_model.muscle_spasm_score = muscle_spams_score
            quad_model.infammation_score = inflammation_score
            quad_model.is_muscle_spasm = is_muscle_spasm
            quad_model.is_inflammation = is_inflammation
            quad_model.is_tissue_overload = is_tissue_overload
            quad_model.body_part_descriptors.append(left_quad_descriptors)
            quad_model.body_part_descriptors.append(right_quad_descriptors)
            quad_model.body_part_descriptors.append(left_hamstring_descriptors)
            quad_model.body_part_descriptors.append(right_hamstring_descriptors)

            quad_model.body_part_descriptors.append(left_glute_descriptors)
            quad_model.body_part_descriptors.append(right_glute_descriptors)

            quad_model.body_part_descriptors.append(left_it_descriptors)
            quad_model.body_part_descriptors.append(right_it_descriptors)

            quad_model.body_part_descriptors.append(left_groin_descriptors)
            quad_model.body_part_descriptors.append(right_groin_descriptors)

            quad_model.body_part_descriptors.append(left_knee_descriptors)
            quad_model.body_part_descriptors.append(right_knee_descriptors)
            quad_model.body_part_descriptors.append(left_hip_descriptors)
            quad_model.body_part_descriptors.append(right_hip_descriptors)
            quad_model.body_part_descriptors.append(lower_back_descriptors)

            quad_model.body_part_predictors.append(left_quad_prediction)
            quad_model.set_descriptors(soreness_date_dictionary[d])
            descriptor_list.append(quad_model)

        for dr in range(len(dates) - 3):
            two_days_ahead = dates[dr] + timedelta(days=2)
            descriptor_list[dr].body_part_predictors[0].set_predictions(soreness_date_dictionary[two_days_ahead], inflammation_dictionary[two_days_ahead], muscle_spasm_ditionary[two_days_ahead])

        if len(x_column_names) == 0:
            #x_column_names = ["user_id"]
            x_column_names = descriptor_list[0].export_column_names()
            #x_column_names.extend(ex_column_names)

        if len(y_column_names) == 0:
            y_column_names = descriptor_list[0].export_predictor_column_names()

        for d in descriptor_list:
            #data_list = [user_id]
            data_list = d.export_to_list()
            #data_list.extend(data_ex_list)
            y_list = d.export_predictors_to_list()
            data_list.extend(y_list)
            #if not all(v == 0 for v in data_list) or not all(v == 0 for v in y_list):
            if not all(v == 0 for v in data_list):
                data.append(data_list)
                y_data.append(y_list)


        # soreness_list = merge_soreness_from_surveys(get_readiness_soreness_list(all_daily_readiness_surveys),
        #                                             get_ps_survey_soreness_list(post_session_surveys))
        #
        # left_quad_soreness_list = [s for s in soreness_list if s.body_part.location.value == 6 and s.side == 1]
        #
        # right_quad_soreness_list = [s for s in soreness_list if s.body_part.location.value == 6 and s.side == 2]
        #
        # left_knee_pain_list = [s for s in soreness_list if s.body_part.location.value == 7 and s.side == 1 and s.pain]
        #
        # right_knee_pain_list = [s for s in soreness_list if s.body_part.location.value == 7 and s.side == 2 and s.pain]
        #
        # left_hip_pain_list = [s for s in soreness_list if s.body_part.location.value == 4 and s.side == 1 and s.pain]
        #
        # right_hip_pain_list = [s for s in soreness_list if s.body_part.location.value == 4 and s.side == 2 and s.pain]
        #
        # any_hip_list = [s for s in soreness_list if s.body_part.location.value == 4]
        #
        # left_lower_back_pain_list = [s for s in soreness_list if s.body_part.location.value == 12 and s.side == 1 and s.pain]
        #
        # right_lower_back_pain_list = [s for s in soreness_list if s.body_part.location.value == 12 and s.side == 2 and s.pain]
        #
        # any_lower_back_list = [s for s in soreness_list if s.body_part.location.value == 12]

    x_column_names.extend(y_column_names)
    quad_df = pd.DataFrame(data, columns=x_column_names)
    data_series_csv = quad_df.to_csv("left_quad_data_series_ext.csv")
    #quad_df = quad_df.loc[:, (quad_df != 0).any(axis=0)]
    #y_quad_df = pd.DataFrame(y_data, columns=y_column_names)
    #logit_model = sm.Logit(exog=quad_df, endog=y_quad_df)
    #logit_result = logit_model.fit(method='bfgs', maxiter=100)
    #logit_result = logit_model.fit(maxiter=100)
    #print(logit_result.summary2())
    #i=9

def run_regression():
    # quad_df = pd.read_csv("left_quad_data_series_ext.csv", usecols=[#"quads-1-pain_daily",
    #                                                                 #"quads-1-soreness_daily",
    #                                                                 #"quads-1-tightness_daily",
    #                                                                 #"quads-2-pain_daily",
    #                                                                 #"quads-2-soreness_daily",
    #                                                                 #"quads-2-tightness_daily",
    #                                                                 #"hamstrings-1-pain_daily",
    #                                                                 #"hamstrings-1-soreness_daily",
    #                                                                 #"hamstrings-1-tightness_daily",
    #                                                                 #"hamstrings-2-pain_daily",
    #                                                                 #"hamstrings-2-soreness_daily",
    #                                                                 #"hamstrings-2-tightness_daily",
    #                                                                 #"glutes-1-pain_daily",
    #                                                                 #"glutes-1-soreness_daily",
    #                                                                 #"glutes-1-tightness_daily",
    #                                                                 #"glutes-2-pain_daily",
    #                                                                 #"glutes-2-soreness_daily",
    #                                                                 #"glutes-2-tightness_daily",
    #                                                                 #"groin-1-pain_daily",
    #                                                                 #"groin-1-soreness_daily",
    #                                                                 #"groin-1-tightness_daily",
    #                                                                 #"groin-2-pain_daily",
    #                                                                 #"groin-2-soreness_daily",
    #                                                                 #"groin-2-tightness_daily",
    #                                                                 #"outer_thigh-1-pain_daily",
    #                                                                 #"outer_thigh-1-soreness_daily",
    #                                                                 #"outer_thigh-1-tightness_daily",
    #                                                                 #"outer_thigh-2-pain_daily",
    #                                                                 #"outer_thigh-2-soreness_daily",
    #                                                                 #"outer_thigh-2-tightness_daily",
    #                                                                 #"knee-1-pain_daily",
    #                                                                 #"knee-1-soreness_daily",
    #                                                                 #"knee-1-tightness_daily",
    #                                                                 #"knee-2-pain_daily",
    #                                                                 #"knee-2-soreness_daily",
    #                                                                 "knee-2-tightness_daily",
    #                                                                 #"hip_flexor-1-pain_daily",
    #                                                                 #"hip_flexor-1-soreness_daily",
    #                                                                 #"hip_flexor-1-tightness_daily",
    #                                                                 "hip_flexor-2-pain_daily",
    #                                                                 #"hip_flexor-2-soreness_daily",
    #                                                                 #"hip_flexor-2-tightness_daily",
    #                                                                 #"lower_back-0-pain_daily",
    #                                                                 #"lower_back-0-soreness_daily",
    #                                                                 #"lower_back-0-tightness_daily",
    #                                                                 #"ramp",
    #                                                                 #"is_tissue_overload",
    #                                                                 #"is_inflammation",
    #                                                                 #"is_muscle_spasm",
    #                                                                 "inflammation_score",
    #                                                                 #"muscle_spasm_score",
    #                                                             ])
    # #quad_df["high_ramp"] = [1 if x>1.0 else 0 for x in quad_df['ramp']]
    # #quad_df = quad_df.drop(columns=['ramp'])
    # quad_df["const"] = 1  # add constant
    # y_df = pd.read_csv("left_quad_data_series_ext.csv", usecols=["quads-1-muscle_spasm_score"])

    quad_df = pd.read_csv("left_quad_data_series_ext.csv", usecols=["quads-1-pain_daily",
                                                                    "quads-1-soreness_daily",
                                                                    "quads-1-tightness_daily",
                                                                    "quads-2-pain_daily",
                                                                    "quads-2-soreness_daily",
                                                                    "quads-2-tightness_daily",
                                                                    "hamstrings-1-pain_daily",
                                                                    "hamstrings-1-soreness_daily",
                                                                    "hamstrings-1-tightness_daily",
                                                                    "hamstrings-2-pain_daily",
                                                                    "hamstrings-2-soreness_daily",
                                                                    "hamstrings-2-tightness_daily",
                                                                    "glutes-1-pain_daily",
                                                                    "glutes-1-soreness_daily",
                                                                    "glutes-1-tightness_daily",
                                                                    "glutes-2-pain_daily",
                                                                    "glutes-2-soreness_daily",
                                                                    "glutes-2-tightness_daily",
                                                                    "groin-1-pain_daily",
                                                                    "groin-1-soreness_daily",
                                                                    "groin-1-tightness_daily",
                                                                    "groin-2-pain_daily",
                                                                    "groin-2-soreness_daily",
                                                                    "groin-2-tightness_daily",
                                                                    "outer_thigh-1-pain_daily",
                                                                    "outer_thigh-1-soreness_daily",
                                                                    "outer_thigh-1-tightness_daily",
                                                                    "outer_thigh-2-pain_daily",
                                                                    "outer_thigh-2-soreness_daily",
                                                                    "outer_thigh-2-tightness_daily",
                                                                    "knee-1-pain_daily",
                                                                    "knee-1-soreness_daily",
                                                                    "knee-1-tightness_daily",
                                                                    "knee-2-pain_daily",
                                                                    "knee-2-soreness_daily",
                                                                    "knee-2-tightness_daily",
                                                                    "hip_flexor-1-pain_daily",
                                                                    "hip_flexor-1-soreness_daily",
                                                                    "hip_flexor-1-tightness_daily",
                                                                    "hip_flexor-2-pain_daily",
                                                                    "hip_flexor-2-soreness_daily",
                                                                    "hip_flexor-2-tightness_daily",
                                                                    "lower_back-0-pain_daily",
                                                                    "lower_back-0-soreness_daily",
                                                                    "lower_back-0-tightness_daily",
                                                                    "ramp",
                                                                    "is_tissue_overload",
                                                                    "is_inflammation",
                                                                    #"is_muscle_spasm",
                                                                    "inflammation_score",
                                                                    "muscle_spasm_score",
                                                                ])
    quad_df["high_ramp"] = [1 if x>1.0 else 0 for x in quad_df['ramp']]
    quad_df["tissue_overload"] = [1 if x else 0 for x in quad_df['is_tissue_overload']]
    quad_df["inflammation"] = [1 if x else 0 for x in quad_df['is_inflammation']]
    #quad_df["low_ramp"] = [1 if x <= 1.0 else 0 for x in quad_df['ramp']]
    quad_df = quad_df.drop(columns=['ramp'])
    quad_df = quad_df.drop(columns=['is_tissue_overload'])
    quad_df = quad_df.drop(columns=['is_inflammation'])
    quad_df["const"] = 1  # add constant

    # quad_df = pd.read_csv("left_quad_data_series_ext.csv", usecols=[#"quads-1-pain_daily",
    #                                                             #"quads-1-soreness_daily",
    #                                                             #"quads-1-tightness_daily",
    #                                                             #"quads-2-pain_daily",
    #                                                             #"quads-2-soreness_daily",
    #                                                             #"quads-2-tightness_daily",
    #                                                             #"hamstrings-1-pain_daily",
    #                                                             #"hamstrings-1-soreness_daily",
    #                                                             #"hamstrings-1-tightness_daily",
    #                                                             #"hamstrings-2-pain_daily",
    #                                                             #"hamstrings-2-soreness_daily",
    #                                                             #"hamstrings-2-tightness_daily",
    #                                                             #"glutes-1-pain_daily",
    #                                                             #"glutes-1-soreness_daily",
    #                                                             #"glutes-1-tightness_daily",
    #                                                             #"glutes-2-pain_daily",
    #                                                             #"glutes-2-soreness_daily",
    #                                                             #"glutes-2-tightness_daily",
    #                                                             #"groin-1-pain_daily",
    #                                                             #"groin-1-soreness_daily",
    #                                                             #"groin-1-tightness_daily",
    #                                                             #"groin-2-pain_daily",
    #                                                             #"groin-2-soreness_daily",
    #                                                             #"groin-2-tightness_daily",
    #                                                             #"outer_thigh-1-pain_daily",
    #                                                             #"outer_thigh-1-soreness_daily",
    #                                                             #"outer_thigh-1-tightness_daily",
    #                                                             #"outer_thigh-2-pain_daily",
    #                                                             #"outer_thigh-2-soreness_daily",
    #                                                             #"outer_thigh-2-tightness_daily",
    #                                                             #"knee-1-pain_daily",
    #                                                             #"knee-1-soreness_daily",
    #                                                             #"knee-1-tightness_daily",
    #                                                             #"knee-2-pain_daily",
    #                                                             #"knee-2-soreness_daily",
    #                                                             #"knee-2-tightness_daily",
    #                                                             #"hip_flexor-1-pain_daily",
    #                                                             #"hip_flexor-1-soreness_daily",
    #                                                             #"hip_flexor-1-tightness_daily",
    #                                                             #"hip_flexor-2-pain_daily",
    #                                                             #"hip_flexor-2-soreness_daily",
    #                                                             "hip_flexor-2-tightness_daily",
    #                                                             #"lower_back-0-pain_daily",
    #                                                             #"lower_back-0-soreness_daily",
    #                                                             #"lower_back-0-tightness_daily",
    #                                                             "ramp",
    #                                                             #"is_tissue_overload",
    #                                                             #"is_inflammation",
    #                                                             #"is_muscle_spasm",
    #                                                             #"inflammation_score",
    #                                                             #"muscle_spasm_score",
    #                                                             ])
    # #quad_df["high_ramp"] = [1 if x>1.0 else 0 for x in quad_df['ramp']]
    # #quad_df = quad_df.drop(columns=['ramp'])
    # quad_df["const"] = 1  # add constant
    # y_df = pd.read_csv("left_quad_data_series_ext.csv", usecols=["quads-1-inflammation_score"])

    # quad_df = pd.read_csv("left_quad_data_series_ext.csv", usecols=[#"quads-1-pain_daily",
    #                                                             #"quads-1-soreness_daily",
    #                                                             #"quads-1-tightness_daily",
    #                                                             #"quads-2-pain_daily",
    #                                                             #"quads-2-soreness_daily",
    #                                                             #"quads-2-tightness_daily",
    #                                                             #"hamstrings-1-pain_daily",
    #                                                             #"hamstrings-1-soreness_daily",
    #                                                             #"hamstrings-1-tightness_daily",
    #                                                             #"hamstrings-2-pain_daily",
    #                                                             #"hamstrings-2-soreness_daily",
    #                                                             #"hamstrings-2-tightness_daily",
    #                                                             #"glutes-1-pain_daily",
    #                                                             #"glutes-1-soreness_daily",
    #                                                             #"glutes-1-tightness_daily",
    #                                                             #"glutes-2-pain_daily",
    #                                                             #"glutes-2-soreness_daily",
    #                                                             #"glutes-2-tightness_daily",
    #                                                             #"groin-1-pain_daily",
    #                                                             #"groin-1-soreness_daily",
    #                                                             #"groin-1-tightness_daily",
    #                                                             #"groin-2-pain_daily",
    #                                                             #"groin-2-soreness_daily",
    #                                                             #"groin-2-tightness_daily",
    #                                                             #"outer_thigh-1-pain_daily",
    #                                                             #"outer_thigh-1-soreness_daily",
    #                                                             #"outer_thigh-1-tightness_daily",
    #                                                             #"outer_thigh-2-pain_daily",
    #                                                             #"outer_thigh-2-soreness_daily",
    #                                                             #"outer_thigh-2-tightness_daily",
    #                                                             #"knee-1-pain_daily",
    #                                                             #"knee-1-soreness_daily",
    #                                                             #"knee-1-tightness_daily",
    #                                                             #"knee-2-pain_daily",
    #                                                             #"knee-2-soreness_daily",
    #                                                             #"knee-2-tightness_daily",
    #                                                             #"hip_flexor-1-pain_daily",
    #                                                             #"hip_flexor-1-soreness_daily",
    #                                                             #"hip_flexor-1-tightness_daily",
    #                                                             #"hip_flexor-2-pain_daily",
    #                                                             #"hip_flexor-2-soreness_daily",
    #                                                             #"hip_flexor-2-tightness_daily",
    #                                                             #"lower_back-0-pain_daily",
    #                                                             #"lower_back-0-soreness_daily",
    #                                                             #"lower_back-0-tightness_daily",
    #                                                             "ramp",
    #                                                             #"is_tissue_overload",
    #                                                             #"is_inflammation",
    #                                                             #"is_muscle_spasm",
    #                                                             #"inflammation_score",
    #                                                             #"muscle_spasm_score",
    #                                                             ])
    # quad_df["high_ramp"] = [1 if x>1.0 else 0 for x in quad_df['ramp']]
    # #quad_df = quad_df.drop(columns=['ramp'])
    # quad_df["const"] = 1  # add constant
    # y_df = pd.read_csv("left_quad_data_series_ext.csv", usecols=["quads-1-soreness"])

    #logit_model = sm.Logit(exog=quad_df, endog=y_df)
    #logit_result = logit_model.fit(method='bfgs', maxiter=100)
    #print(logit_result.summary2())

    y_column = "quads-1-soreness"
    #quad_df = quad_df.drop(columns=["quads-1-soreness_daily"])
    #y_column = "quads-1-inflammation_score"
    quad_df = quad_df.drop(columns=["inflammation_score"])
    quad_df = quad_df.drop(columns=["muscle_spasm_score"])
    quad_df = quad_df.drop(columns=["tissue_overload"])
    #y_column = "quads-1-muscle_spasm_score"
    #quad_df = quad_df.drop(columns=["muscle_spasm_score"])

    y_df = pd.read_csv("left_quad_data_series_ext.csv", usecols=[y_column])

    output = quad_df.groupby('quads-1-soreness_daily').mean()

    logreg = LogisticRegression()
    np.random.seed(1)

    reduced_x_df = quad_df.copy()

    y_list = y_df[y_column].tolist()
    #x_train, x_test, y_train, y_test = model_selection.train_test_split(quad_df, y_list, test_size=0.3, random_state=0)

    rfe = feature_selection.RFE(logreg, 6)
    rfe = rfe.fit(quad_df, y_df.values.ravel())
    #print(rfe.support_)
    #print(rfe.ranking_)
    rank_list = list(rfe.ranking_)

    for s in range(len(rfe.support_)-1, -1, -1):
        if not rfe.support_[s]:
            reduced_x_df = reduced_x_df.drop(reduced_x_df.columns[s], axis=1)
            del rank_list[s]

    #print(rank_list)

    for j in range(0, 20):
        logit_model_revised = sm.Logit(exog=reduced_x_df, endog=y_df)
        logit_result_revised = logit_model_revised.fit(method='bfgs', maxiter=200)

        # find highest insignicant pvalue and remove
        p_values = logit_result_revised.pvalues
        p_values.sort_values(ascending=False, inplace=True)
        column_removed = False
        if len(p_values) > 0 and p_values[0] > .05:
            column_to_remove = p_values.index[0]
            reduced_x_df = reduced_x_df.drop(columns=[column_to_remove])
            column_removed = True
        if not column_removed:
            break

    print(logit_result_revised.summary2())

    #logreg.fit(x_train, y_train)
    #y_pred = logreg.predict(x_test)
    #print('Accuracy of logistic regression classifier on test set: {:.2f}'.format(logreg.score(x_test, y_test)))
    #confusion_matrix = metrics.confusion_matrix(y_test, y_pred)
    #print(confusion_matrix)
    #probabilities = logreg.predict_proba(x_test)
    g=0

if __name__ == '__main__':
    #find_user_history()
    run_regression()