from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
import logic.exercise_mapping as exercise_mapping
from logic.training_plan_management import TrainingPlanManager
from models.session import Session, SportTrainingSession
from models.historic_soreness import HistoricSoreness
from models.stats import AthleteStats

from datetime import datetime, timedelta, date, time
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from models.soreness import Soreness, BodyPart, BodyPartLocation, HistoricSorenessStatus
from models.daily_plan import DailyPlan
from tests.testing_utilities import TestUtilities
from models.daily_readiness import DailyReadiness
from utils import format_datetime, format_date
import random

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


class TestParameters(object):
    def __init__(self, file_name, athlete_stats, train_later, high_volume, doms=False):
        self.file_name = file_name
        self.athlete_stats = athlete_stats
        self.train_later = train_later
        self.high_volume = high_volume
        self.doms = doms


def get_test_parameters_list():
    parm_list = []

    as1 = AthleteStats("tester")
    as1.historic_soreness = []
    as1.muscular_strain_increasing = False
    parm1 = TestParameters("PreActiveRest_no_doms_no_muscular_strain", as1, train_later=True, high_volume=False)
    parm2 = TestParameters("PostActiveRest_no_doms_no_muscular_strain", as1, train_later=False, high_volume=False)
    parm3 = TestParameters("PreActiveRest_no_doms_no_muscular_strain_high_volume", as1, train_later=True,
                           high_volume=True)
    parm4 = TestParameters("PostActiveRest_no_doms_no_muscular_strain_high_volume", as1, train_later=False,
                           high_volume=True)

    as2 = AthleteStats("tester")
    as2.historic_soreness = []
    as2.muscular_strain_increasing = True

    parm5 = TestParameters("PreActiveRest_no_doms_muscular_strain_no_high_volume", as2, train_later=True,
                           high_volume=False)
    parm6 = TestParameters("PostActiveRest_no_doms_muscular_strain_no_high_volume", as2, train_later=False,
                           high_volume=False)
    parm7 = TestParameters("PreActiveRest_no_doms_muscular_strain_high_volume", as2, train_later=True, high_volume=True)
    parm8 = TestParameters("PostActiveRest_no_doms_muscular_strain_high_volume", as2, train_later=False,
                           high_volume=True)
    parm9 = TestParameters("PreActiveRest_doms_muscular_strain_no_high_volume", as2, train_later=True,
                           high_volume=False, doms=True)
    parm10 = TestParameters("PostActiveRest_doms_muscular_strain_no_high_volume", as2, train_later=False,
                            high_volume=False, doms=True)
    parm11 = TestParameters("PreActiveRest_doms_muscular_strain_high_volume", as2, train_later=True, high_volume=True,
                            doms=True)
    parm12 = TestParameters("PostActiveRest_doms_muscular_strain_high_volume", as2, train_later=False, high_volume=True,
                            doms=True)
    parm_list.append(parm1)
    parm_list.append(parm2)
    parm_list.append(parm3)
    parm_list.append(parm4)
    parm_list.append(parm5)
    parm_list.append(parm6)
    parm_list.append(parm7)
    parm_list.append(parm8)
    parm_list.append(parm9)
    parm_list.append(parm10)
    parm_list.append(parm11)
    parm_list.append(parm12)

    return parm_list


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def create_plan(test_parameter, body_part_list, severity_list, side_list, pain_list, train_later,
                historic_soreness_list=None):
    athlete_stats = test_parameter.athlete_stats

    training_sessions = []

    if test_parameter.high_volume:
        training_session = SportTrainingSession()
        training_session.session_RPE = 7
        training_sessions.append(training_session)

    user_id = athlete_stats.athlete_id

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    daily_plan_datastore = DailyPlanDatastore()
    athlete_stats_datastore = AthleteStatsDatastore()
    athlete_stats.historic_soreness = historic_soreness_list
    athlete_stats_datastore.side_load_athlete_stats(athlete_stats)

    soreness_list = []
    for b in range(0, len(body_part_list)):
        if len(pain_list) > 0 and pain_list[b]:
            soreness_list.append(TestUtilities().body_part_pain(body_part_list[b], severity_list[b], side_list[b]))
        else:
            if len(severity_list) == 0:
                soreness_list.append(TestUtilities().body_part_soreness(body_part_list[b], 2))
            else:
                soreness_list.append(TestUtilities().body_part_soreness(body_part_list[b], severity_list[b]))

    survey = DailyReadiness(current_date_time.strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 7, 9)

    daily_plan = DailyPlan(format_date(current_date))
    daily_plan.user_id = user_id
    daily_plan.train_later = train_later
    daily_plan.daily_readiness_survey = survey
    daily_plan_datastore.side_load_plans([daily_plan])
    data_store_collection = DatastoreCollection()
    data_store_collection.daily_plan_datastore = daily_plan_datastore
    data_store_collection.exercise_datastore = exercise_library_datastore
    data_store_collection.athlete_stats_datastore = athlete_stats_datastore
    mgr = TrainingPlanManager(user_id, data_store_collection)
    mgr.training_sessions = training_sessions

    daily_plan = mgr.create_daily_plan(format_date(current_date), format_datetime(current_date_time),
                                       athlete_stats=athlete_stats)

    return daily_plan


@pytest.fixture(scope="module")
def soreness_one_body_part(body_enum, severity_score, historic_soreness_status, treatment_priority=1):
    soreness_list = []
    soreness_item = Soreness()
    soreness_item.historic_soreness_status = historic_soreness_status
    soreness_item.severity = severity_score
    soreness_body_part = BodyPart(BodyPartLocation(body_enum),
                                  treatment_priority)
    soreness_item.body_part = soreness_body_part
    soreness_list.append(soreness_item)
    return soreness_list


def soreness_two_body_parts_random(body_part_list, body_enum, severity_score, historic_soreness_status,
                                   treatment_priority=1):
    soreness_list = []

    soreness_item = Soreness()
    soreness_item.historic_soreness_status = historic_soreness_status
    soreness_item.severity = severity_score
    soreness_body_part = BodyPart(BodyPartLocation(body_enum),
                                  treatment_priority)
    soreness_item.body_part = soreness_body_part
    soreness_list.append(soreness_item)

    temp_list = list(b for b in body_part_list if b != body_enum)
    temp_enum = random.choice(temp_list)
    random_soreness = Soreness()
    random_soreness.historic_soreness_status = HistoricSorenessStatus.doms
    random_soreness.severity = severity_score
    random_soreness_body_part = BodyPart(BodyPartLocation(temp_enum), treatment_priority)
    random_soreness.body_part = random_soreness_body_part
    soreness_list.append(random_soreness)

    return soreness_list


@pytest.fixture(scope="module")
def pain_one_body_part(body_enum, severity_score, historic_soreness_status, treatment_priority=1):
    soreness_list = []
    soreness_item = Soreness()
    soreness_item.historic_soreness_status = historic_soreness_status
    soreness_item.severity = severity_score
    soreness_item.pain = True
    soreness_body_part = BodyPart(BodyPartLocation(body_enum),
                                  treatment_priority)
    soreness_item.body_part = soreness_body_part
    soreness_list.append(soreness_item)
    return soreness_list


def get_trigger_date_time():
    return datetime(2018, 7, 10, 2, 0, 0)


def is_status_pain(historic_soreness_status):
    if historic_soreness_status is None:
        return False
    elif (historic_soreness_status == HistoricSorenessStatus.almost_acute_pain or
          historic_soreness_status == HistoricSorenessStatus.acute_pain or
          historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain or
          historic_soreness_status == HistoricSorenessStatus.persistent_pain or
          historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain or
          historic_soreness_status == HistoricSorenessStatus.persistent_2_pain):
        return True
    else:
        return False


def is_historic_soreness_pain(historic_soreness_status):

    if historic_soreness_status in[HistoricSorenessStatus.acute_pain,HistoricSorenessStatus.persistent_pain,
                                   HistoricSorenessStatus.persistent_2_pain,HistoricSorenessStatus.almost_persistent_pain,
                                   HistoricSorenessStatus.almost_persistent_2_pain_acute,
                                   HistoricSorenessStatus.almost_persistent_2_pain,
                                   HistoricSorenessStatus.almost_acute_pain]:
        return True
    else:
        return False


def calc_active_time_efficient(exercise_dictionary):

    active_time = 0

    for id, assigned_excercise in exercise_dictionary.items():
        active_time += assigned_excercise.duration_efficient() / 60

    return active_time


def calc_active_time_complete(exercise_dictionary):

    active_time = 0

    for id, assigned_excercise in exercise_dictionary.items():
        active_time += assigned_excercise.duration_complete() / 60

    return active_time


def calc_active_time_comprehensive(exercise_dictionary):

    active_time = 0

    for id, assigned_excercise in exercise_dictionary.items():
        active_time += assigned_excercise.duration_comprehensive() / 60

    return active_time


def test_ensure_minimum_dosage_assigned():

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(9, 0, 0))
    current_date_time = current_date_time - timedelta(days=16)

    parm_list = get_test_parameters_list()

    min_efficient = 1000
    min_complete = 1000
    min_comprehensive = 1000
    max_efficient = 0
    max_complete = 0
    max_comprehensive = 0

    for test_parm in parm_list:

        j = 0
        athlete_id = "tester"
        made_it_through = False
        max_severity_1 = [1, 2, 3, 4, 5]

        is_pain_1 = [True, False]

        body_parts_1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

        historic_soreness_status_1 = [None,
                                      HistoricSorenessStatus.dormant_cleared,
                                      HistoricSorenessStatus.almost_acute_pain,
                                      HistoricSorenessStatus.acute_pain,
                                      HistoricSorenessStatus.almost_persistent_pain,
                                      HistoricSorenessStatus.persistent_pain,
                                      HistoricSorenessStatus.almost_persistent_2_pain,
                                      HistoricSorenessStatus.almost_persistent_2_pain_acute,
                                      HistoricSorenessStatus.persistent_2_pain,
                                      HistoricSorenessStatus.almost_persistent_soreness,
                                      HistoricSorenessStatus.persistent_soreness,
                                      HistoricSorenessStatus.almost_persistent_2_soreness,
                                      HistoricSorenessStatus.persistent_2_soreness]

        for b1 in body_parts_1:
            for m1 in max_severity_1:
                for h1 in historic_soreness_status_1:
                    for p in is_pain_1:
                        if 0==0 or (b1 == 6 and h1 is None and not test_parm.doms and not test_parm.athlete_stats.muscular_strain_increasing):
                            body_part_list = []
                            body_part_list.append(b1)

                            severity_list = []
                            severity_list.append(m1)

                            pain_list = []
                            pain_list.append(p)

                            historic_soreness_list = []

                            historic_soreness = HistoricSoreness(BodyPartLocation(14), 1, is_historic_soreness_pain(h1))
                            historic_soreness.first_reported_date_time = current_date_time - timedelta(days=16)
                            historic_soreness.historic_soreness_status = h1
                            historic_soreness_list.append(historic_soreness)

                            if test_parm.doms and not p:
                                temp_list = list(b for b in body_parts_1 if b != b1)
                                temp_enum = random.choice(temp_list)
                                historic_soreness_2 = HistoricSoreness(BodyPartLocation(temp_enum), 2, False)
                                historic_soreness_2.first_reported_date_time = current_date_time - timedelta(days=8)
                                historic_soreness_2.historic_soreness_status = HistoricSorenessStatus.doms
                                historic_soreness_list.append(historic_soreness_2)
                                body_part_list.append(temp_enum)
                                severity_list.append(2)
                                pain_list.append(False)

                            daily_plan = create_plan(test_parameter=test_parm, body_part_list=body_part_list, severity_list=severity_list, side_list=[1],
                                                     pain_list=pain_list, train_later=test_parm.train_later, historic_soreness_list=[historic_soreness])

                            if test_parm.train_later:
                                plan_obj = daily_plan.pre_active_rest[0]
                            else:
                                plan_obj = daily_plan.post_active_rest[0]
                                plan_obj.active_stretch_exercises = {}

                            efficient_inhibit_minutes = calc_active_time_efficient(plan_obj.inhibit_exercises)
                            efficient_static_stretch_minutes = calc_active_time_efficient(
                                plan_obj.static_stretch_exercises)
                            if test_parm.train_later:
                                efficient_active_stretch_minutes = calc_active_time_efficient(
                                    plan_obj.active_stretch_exercises)
                            else:
                                efficient_active_stretch_minutes = 0
                            efficient_isolated_activate_minutes = calc_active_time_efficient(
                                plan_obj.isolated_activate_exercises)
                            efficient_static_integrate_minutes = calc_active_time_efficient(
                                plan_obj.static_integrate_exercises)
                            efficient_total_minutes = efficient_inhibit_minutes + efficient_static_stretch_minutes + efficient_active_stretch_minutes + efficient_isolated_activate_minutes + efficient_static_integrate_minutes

                            complete_inhibit_minutes = calc_active_time_complete(plan_obj.inhibit_exercises)
                            complete_static_stretch_minutes = calc_active_time_complete(plan_obj.static_stretch_exercises)
                            if test_parm.train_later:
                                complete_active_stretch_minutes = calc_active_time_complete(plan_obj.active_stretch_exercises)
                            else:
                                complete_active_stretch_minutes = 0

                            complete_isolated_activate_minutes = calc_active_time_complete(plan_obj.isolated_activate_exercises)
                            complete_static_integrate_minutes = calc_active_time_complete(plan_obj.static_integrate_exercises)
                            complete_total_minutes = complete_inhibit_minutes + complete_static_stretch_minutes + complete_active_stretch_minutes + complete_isolated_activate_minutes + complete_static_integrate_minutes

                            comprehensive_inhibit_minutes = calc_active_time_comprehensive(plan_obj.inhibit_exercises)
                            comprehensive_static_stretch_minutes = calc_active_time_comprehensive(
                                plan_obj.static_stretch_exercises)
                            if test_parm.train_later:
                                comprehensive_active_stretch_minutes = calc_active_time_comprehensive(
                                    plan_obj.active_stretch_exercises)
                            else:
                                comprehensive_active_stretch_minutes = 0
                            comprehensive_isolated_activate_minutes = calc_active_time_comprehensive(
                                plan_obj.isolated_activate_exercises)
                            comprehensive_static_integrate_minutes = calc_active_time_comprehensive(
                                plan_obj.static_integrate_exercises)
                            comprehensive_total_minutes = comprehensive_inhibit_minutes + comprehensive_static_stretch_minutes + comprehensive_active_stretch_minutes + comprehensive_isolated_activate_minutes + comprehensive_static_integrate_minutes

                            min_efficient = min(min_efficient, efficient_total_minutes)
                            min_complete = min(min_complete, complete_total_minutes)
                            min_comprehensive = min(min_comprehensive, comprehensive_total_minutes)

                            max_efficient = max(max_efficient, efficient_total_minutes)
                            max_complete = max(max_complete, complete_total_minutes)
                            max_comprehensive = max(max_comprehensive, comprehensive_total_minutes)

                            if comprehensive_total_minutes == 0:
                                stop_here = True

    made_it_through = True
