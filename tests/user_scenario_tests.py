import pytest
import logic.training as training
import datetime
import logic.training_plan_management as training_plan_management
from aws_xray_sdk.core import xray_recorder
import athlete_data_access_mocks
#import datastores.exercise_datastore as exercise_datastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_schedule_datastore import DailyScheduleDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore as PostSessionSurveyDataStore
from models.daily_readiness import DailyReadiness
from models.post_session_survey import PostSurvey, PostSessionSurvey
import models.session as session
from soreness_and_injury import DailySoreness, BodyPart, BodyPartLocation
import os
import json


@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):
    xray_recorder.begin_segment(name='test')


@pytest.fixture(scope="module")
def body_part_location(location_enum):
    location = BodyPartLocation(location_enum)

    return location

def get_post_survey(RPE, soreness_list):

    survey = {
        "RPE" : RPE,
        "soreness": soreness_list
    }

    return  survey

def body_part_soreness(location_enum, severity):
    # soreness = DailySoreness()
    # body_part = BodyPart(body_part_location(location_enum), 0)
    # soreness.body_part = body_part
    # soreness.severity = severity

    soreness = {
        "body_part": location_enum,
        "severity": severity
    }

    return soreness


def write_file(file_name, daily_plan):
    directory = os.path.expanduser("~/test_plan_output/")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file = open(directory + file_name + ".json", "w")
    json_string = json.dumps(daily_plan.json_serialise(), indent=4)
    file.write(json_string)
    file.close()

def generate_plan(user_id, survey, plan_date, file_name, plan_letter):

    plan_datastore = DailyPlanDatastore()
    readiness_store = DailyReadinessDatastore()
    post_session_store = PostSessionSurveyDataStore()

    if plan_letter == "a":

        readiness_store.put([survey])

    else:
        post_session_store.put([survey])


    manager = training_plan_management.TrainingPlanManager(user_id,
                                                           readiness_store,
                                                           DailyScheduleDatastore(),
                                                           PostSessionSurveyDataStore(),
                                                           plan_datastore)
    success = manager.create_daily_plan()

    if success:

        plan = plan_datastore.get(user_id, plan_date, plan_date)

        write_file(file_name + plan_date.replace('-', '') + plan_letter, plan[0])

    return success


# Ryan Robbins


def test_robbins_create_daily_july_12():

    user_id = "rrobbins@fakemail.com"

    file_user_id = "ryanrobbins"

    july_12_soreness_list = [body_part_soreness(12, 1)]

    july_12_survey = DailyReadiness(datetime.datetime(2018, 7, 12, 11, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id,
                                    july_12_soreness_list, 7, 9)

    success = generate_plan(user_id, july_12_survey, "2018-07-12", file_user_id, "a")

    assert True is success

    july_12_soreness_list = [body_part_soreness(12, 1)]

    july_12_post_survey = get_post_survey(4, july_12_soreness_list)
    july_12_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 12, 17, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          1, july_12_post_survey)

    success = generate_plan(user_id, july_12_post_session_survey, "2018-07-12", file_user_id, "b")

    assert True is success


def test_robbins_create_daily_july_13():

    user_id = "rrobbins@fakemail.com"

    file_user_id = "ryanrobbins"

    july_13_soreness_list = [body_part_soreness(12, 1), body_part_soreness(9, 2)]

    july_13_survey = DailyReadiness(datetime.datetime(2018, 7, 13, 8, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_13_soreness_list, 6, 7)

    success = generate_plan(user_id, july_13_survey, "2018-07-13", file_user_id, "a")

    assert True is success

    july_13_soreness_list = [body_part_soreness(9, 2)]

    july_13_post_survey = get_post_survey(3, july_13_soreness_list)
    july_13_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 13, 17, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_13_post_survey)

    success = generate_plan(user_id, july_13_post_session_survey, "2018-07-13", file_user_id, "b")

    assert True is success


def test_robbins_create_daily_july_14():

    user_id = "rrobbins@fakemail.com"

    file_user_id = "ryanrobbins"

    july_14_soreness_list = [body_part_soreness(9, 1), body_part_soreness(7, 2)]

    july_14_survey = DailyReadiness(datetime.datetime(2018, 7, 14, 14, 15, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_14_soreness_list, 3, 1)

    success = generate_plan(user_id, july_14_survey, "2018-07-14", file_user_id, "a")

    assert True is success

    july_14_soreness_list = [body_part_soreness(7, 3)]

    july_14_post_survey = get_post_survey(8, july_14_soreness_list)
    july_14_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 14, 17, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          2, july_14_post_survey)

    success = generate_plan(user_id, july_14_post_session_survey, "2018-07-14", file_user_id, "b")

    assert True is success


def test_robbins_create_daily_july_15():

    user_id = "rrobbins@fakemail.com"

    file_user_id = "ryanrobbins"

    july_15_soreness_list = [body_part_soreness(7, 2)]

    july_15_survey = DailyReadiness(datetime.datetime(2018, 7, 15, 7, 20, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_15_soreness_list, 6, 6)

    success = generate_plan(user_id, july_15_survey, "2018-07-15", file_user_id, "a")

    assert True is success

    july_15_soreness_list = [body_part_soreness(7, 3)]

    july_15_post_survey = get_post_survey(6, july_15_soreness_list)
    july_15_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 15, 16, 20, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          2, july_15_post_survey)

    success = generate_plan(user_id, july_15_post_session_survey, "2018-07-15", file_user_id, "b")

    assert True is success

def test_robbins_create_daily_july_16():

    user_id = "rrobbins@fakemail.com"

    file_user_id = "ryanrobbins"

    july_16_soreness_list = [body_part_soreness(7, 3)]

    july_16_survey = DailyReadiness(datetime.datetime(2018, 7, 16, 6, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_16_soreness_list, 4, 3)

    success = generate_plan(user_id, july_16_survey, "2018-07-16", file_user_id, "a")

    assert True is success

    july_16_soreness_list = [body_part_soreness(7, 4)]

    july_16_post_survey = get_post_survey(7, july_16_soreness_list)
    july_16_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 16, 19, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_16_post_survey)

    success = generate_plan(user_id, july_16_post_session_survey, "2018-07-16", file_user_id, "b")

    assert True is success


def test_robbins_create_daily_july_17():

    user_id = "rrobbins@fakemail.com"

    file_user_id = "ryanrobbins"

    july_17_soreness_list = [body_part_soreness(7, 4)]

    july_17_survey = DailyReadiness(datetime.datetime(2018, 7, 17, 6, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_17_soreness_list, 4, 5)

    success = generate_plan(user_id, july_17_survey, "2018-07-17", file_user_id, "a")

    assert True is success

    july_17_soreness_list = [body_part_soreness(7, 4)]

    july_17_post_survey = get_post_survey(8, july_17_soreness_list)
    july_17_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 17, 19, 4, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          1, july_17_post_survey)

    success = generate_plan(user_id, july_17_post_session_survey, "2018-07-17", file_user_id, "b")

    assert True is success


def test_robbins_create_daily_july_18():

    user_id = "rrobbins@fakemail.com"

    file_user_id = "ryanrobbins"

    july_18_soreness_list = [body_part_soreness(7, 2), body_part_soreness(11, 1)]

    july_18_survey = DailyReadiness(datetime.datetime(2018, 7, 18, 12, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_18_soreness_list, 4, 2)

    success = generate_plan(user_id, july_18_survey, "2018-07-18", file_user_id, "a")

    assert True is success

    july_18_soreness_list = [body_part_soreness(7, 2), body_part_soreness(11, 2)]

    july_18_post_survey = get_post_survey(5, july_18_soreness_list)
    july_18_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 18, 20, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_18_post_survey)

    success = generate_plan(user_id, july_18_post_session_survey, "2018-07-18", file_user_id, "b")

    assert True is success

# Julie Jones


def test_jones_create_daily_july_12():

    user_id = "jjones@email.com"

    file_user_id = "juliejones"

    july_12_soreness_list = [body_part_soreness(5, 2)]

    july_12_survey = DailyReadiness(datetime.datetime(2018, 7, 12, 11, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id,
                                    july_12_soreness_list, 6, 7)

    success = generate_plan(user_id, july_12_survey, "2018-07-12", file_user_id, "a")

    assert True is success

    july_12_soreness_list = [body_part_soreness(5, 2)]

    july_12_post_survey = get_post_survey(4, july_12_soreness_list)
    july_12_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 12, 13, 54, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_12_post_survey)

    success = generate_plan(user_id, july_12_post_session_survey, "2018-07-12", file_user_id, "b")

    assert True is success


def test_jones_create_daily_july_13():

    user_id = "jjones@email.com"

    file_user_id = "juliejones"

    july_13_soreness_list = [body_part_soreness(5, 2)]

    july_13_survey = DailyReadiness(datetime.datetime(2018, 7, 13, 8, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_13_soreness_list, 4, 4)

    success = generate_plan(user_id, july_13_survey, "2018-07-13", file_user_id, "a")

    assert True is success

    july_13_soreness_list = [body_part_soreness(5, 3)]

    july_13_post_survey = get_post_survey(7, july_13_soreness_list)
    july_13_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 13, 13, 51, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_13_post_survey)

    success = generate_plan(user_id, july_13_post_session_survey, "2018-07-13", file_user_id, "b")

    assert True is success


def test_jones_create_daily_july_14():

    user_id = "jjones@email.com"

    file_user_id = "juliejones"

    july_14_soreness_list = [body_part_soreness(5, 2), body_part_soreness(12, 2)]

    july_14_survey = DailyReadiness(datetime.datetime(2018, 7, 14, 14, 15, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_14_soreness_list, 9, 7)

    success = generate_plan(user_id, july_14_survey, "2018-07-14", file_user_id, "a")

    assert True is success

    july_14_soreness_list = [body_part_soreness(5, 2), body_part_soreness(12, 1)]

    july_14_post_survey = get_post_survey(4, july_14_soreness_list)
    july_14_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 14, 14, 2, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_14_post_survey)

    success = generate_plan(user_id, july_14_post_session_survey, "2018-07-14", file_user_id, "b")

    assert True is success


def test_jones_create_daily_july_15():

    user_id = "jjones@email.com"

    file_user_id = "juliejones"

    july_15_soreness_list = [body_part_soreness(5, 3), body_part_soreness(12, 1)]

    july_15_survey = DailyReadiness(datetime.datetime(2018, 7, 15, 11, 1, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_15_soreness_list, 8, 9)

    success = generate_plan(user_id, july_15_survey, "2018-07-15", file_user_id, "a")

    assert True is success

    july_15_soreness_list = [body_part_soreness(5, 3)]

    july_15_post_survey = get_post_survey(1, july_15_soreness_list)
    july_15_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 15, 13, 47, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_15_post_survey)

    success = generate_plan(user_id, july_15_post_session_survey, "2018-07-15", file_user_id, "b")

    assert True is success


def test_jones_create_daily_july_16():

    user_id = "jjones@email.com"

    file_user_id = "juliejones"

    july_16_soreness_list = [body_part_soreness(5, 2)]

    july_16_survey = DailyReadiness(datetime.datetime(2018, 7, 16, 10, 27, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_16_soreness_list, 5, 5)

    success = generate_plan(user_id, july_16_survey, "2018-07-16", file_user_id, "a")

    assert True is success

    july_16_soreness_list = [body_part_soreness(5, 2)]

    july_16_post_survey = get_post_survey(4, july_16_soreness_list)
    july_16_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 16, 13, 55, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_16_post_survey)

    success = generate_plan(user_id, july_16_post_session_survey, "2018-07-16", file_user_id, "b")

    assert True is success

def test_jones_create_daily_july_17():

    user_id = "jjones@email.com"

    file_user_id = "juliejones"

    july_17_soreness_list = [body_part_soreness(5, 2)]

    july_17_survey = DailyReadiness(datetime.datetime(2018, 7, 17, 10, 35, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_17_soreness_list, 7, 7)

    success = generate_plan(user_id, july_17_survey, "2018-07-17", file_user_id, "a")

    assert True is success

    july_17_soreness_list = [body_part_soreness(5, 2)]

    july_17_post_survey = get_post_survey(5, july_17_soreness_list)
    july_17_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 17, 15, 3, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_17_post_survey)

    success = generate_plan(user_id, july_17_post_session_survey, "2018-07-17", file_user_id, "b")

    assert True is success

    july_17_soreness_list = [body_part_soreness(5, 2), body_part_soreness(12, 1)]

    july_17_post_survey = get_post_survey(3, july_17_soreness_list)
    july_17_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 17, 16, 4, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          1, july_17_post_survey)

    success = generate_plan(user_id, july_17_post_session_survey, "2018-07-17", file_user_id, "c")

    assert True is success


def test_jones_create_daily_july_18():

    user_id = "jjones@email.com"

    file_user_id = "juliejones"

    july_18_soreness_list = [body_part_soreness(5, 1)]

    july_18_survey = DailyReadiness(datetime.datetime(2018, 7, 18, 11, 7, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_18_soreness_list, 8, 7)

    success = generate_plan(user_id, july_18_survey, "2018-07-18", file_user_id, "a")

    assert True is success

    july_18_soreness_list = [body_part_soreness(5, 1)]

    july_18_post_survey = get_post_survey(6, july_18_soreness_list)
    july_18_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 18, 13, 46, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_18_post_survey)

    success = generate_plan(user_id, july_18_post_session_survey, "2018-07-18", file_user_id, "b")

    assert True is success

# AK


def test_ak_create_daily_july_12():

    user_id = "khan@email.com"

    file_user_id = "ak"

    july_12_soreness_list = []

    july_12_survey = DailyReadiness(datetime.datetime(2018, 7, 12, 11, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id,
                                    july_12_soreness_list, 8, 7)

    success = generate_plan(user_id, july_12_survey, "2018-07-12", file_user_id, "a")

    assert True is success

    july_12_soreness_list = []

    july_12_post_survey = get_post_survey(4, july_12_soreness_list)
    july_12_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 12, 12, 3, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_12_post_survey)

    success = generate_plan(user_id, july_12_post_session_survey, "2018-07-12", file_user_id, "b")

    assert True is success


def test_ak_create_daily_july_13():

    user_id = "khan@email.com"

    file_user_id = "ak"

    july_13_soreness_list = [body_part_soreness(6, 2), body_part_soreness(16,1), body_part_soreness(17, 1)]

    july_13_survey = DailyReadiness(datetime.datetime(2018, 7, 13, 9, 4, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_13_soreness_list, 7, 7)

    success = generate_plan(user_id, july_13_survey, "2018-07-13", file_user_id, "a")

    assert True is success

    july_13_soreness_list = [body_part_soreness(6, 2), body_part_soreness(17, 1), body_part_soreness(7, 2)]

    july_13_post_survey = get_post_survey(5, july_13_soreness_list)
    july_13_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 13, 11, 47, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, july_13_post_survey)

    success = generate_plan(user_id, july_13_post_session_survey, "2018-07-13", file_user_id, "b")

    assert True is success


def test_ak_create_daily_july_14():

    user_id = "khan@email.com"

    file_user_id = "ak"

    july_14_soreness_list = [body_part_soreness(6, 1), body_part_soreness(7, 2)]

    july_14_survey = DailyReadiness(datetime.datetime(2018, 7, 14, 12, 12, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_14_soreness_list, 10, 9)

    success = generate_plan(user_id, july_14_survey, "2018-07-14", file_user_id, "a")

    assert True is success


def test_ak_create_daily_july_15():

    user_id = "khan@email.com"

    file_user_id = "ak"

    july_15_soreness_list = [body_part_soreness(7, 2), body_part_soreness(17, 1)]

    july_15_survey = DailyReadiness(datetime.datetime(2018, 7, 15, 14, 27, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, july_15_soreness_list, 5, 4)

    success = generate_plan(user_id, july_15_survey, "2018-07-14", file_user_id, "a")

    assert True is success


def test_ak_create_daily_july_16():

    user_id = "khan@email.com"

    file_user_id = "ak"

    soreness_list = [body_part_soreness(7, 1), body_part_soreness(8, 1)]

    survey = DailyReadiness(datetime.datetime(2018, 7, 16, 8, 47, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 7, 6)

    success = generate_plan(user_id, survey, "2018-07-16", file_user_id, "a")

    assert True is success

    soreness_list = [body_part_soreness(6, 2), body_part_soreness(7, 2), body_part_soreness(15, 2), body_part_soreness(8, 1)]

    post_survey = get_post_survey(8, soreness_list)
    post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 16, 11, 53, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, post_survey)

    success = generate_plan(user_id, post_session_survey, "2018-07-16", file_user_id, "b")

    assert True is success



def test_ak_create_daily_july_17():

    user_id = "khan@email.com"

    file_user_id = "ak"

    soreness_list = [body_part_soreness(6, 1), body_part_soreness(14, 1), body_part_soreness(15, 2), body_part_soreness(7, 1)]

    survey = DailyReadiness(datetime.datetime(2018, 7, 17, 11, 7, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 6, 7)

    success = generate_plan(user_id, survey, "2018-07-17", file_user_id, "a")

    assert True is success

    soreness_list = [body_part_soreness(14, 1), body_part_soreness(15, 2), body_part_soreness(7, 1)]

    post_survey = get_post_survey(2, soreness_list)
    post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 17, 12, 37, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          1, post_survey)

    success = generate_plan(user_id, post_session_survey, "2018-07-17", file_user_id, "b")

    assert True is success



def test_ak_create_daily_july_18():

    user_id = "khan@email.com"

    file_user_id = "ak"

    soreness_list = [body_part_soreness(15, 1), body_part_soreness(7, 2)]

    survey = DailyReadiness(datetime.datetime(2018, 7, 18, 9, 1, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 5, 7)

    success = generate_plan(user_id, survey, "2018-07-18", file_user_id, "a")

    assert True is success

    soreness_list = [body_part_soreness(8, 2), body_part_soreness(7, 2)]

    post_survey = get_post_survey(6, soreness_list)
    post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 18, 13, 1, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          0, post_survey)

    success = generate_plan(user_id, post_session_survey, "2018-07-18", file_user_id, "b")

    assert True is success