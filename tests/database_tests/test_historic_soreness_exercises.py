from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
import logic.exercise_mapping as exercise_mapping
from logic.training_plan_management import TrainingPlanManager
import models.session as session
from models.soreness import HistoricSoreness, HistoricSorenessStatus
from models.stats import AthleteStats
from pandas import DataFrame
from datetime import datetime, timedelta, date, time
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from models.soreness import Soreness, BodyPart, BodyPartLocation
from models.daily_plan import DailyPlan
from tests.testing_utilities import TestUtilities
from models.daily_readiness import DailyReadiness
from utils import format_datetime, format_date

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()
df = DataFrame()

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()

def create_plan(body_part_list, severity_list, side_list, pain_list, historic_soreness_list=None):
    user_id = "tester"

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    daily_plan_datastore = DailyPlanDatastore()

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
    daily_plan.daily_readiness_survey = survey
    daily_plan_datastore.side_load_plans([daily_plan])
    data_store_collection = DatastoreCollection()
    data_store_collection.daily_plan_datastore = daily_plan_datastore
    data_store_collection.exercise_datastore = exercise_library_datastore

    if historic_soreness_list is not None and len(historic_soreness_list) > 0:
        athlete_stats_datastore = AthleteStatsDatastore()
        athlete_stats = AthleteStats(user_id)
        athlete_stats.historic_soreness = historic_soreness_list
        athlete_stats_datastore.side_load_athlete_stats(athlete_stats)
        data_store_collection.athlete_stats_datastore = athlete_stats_datastore

    mgr = TrainingPlanManager(user_id, data_store_collection)

    daily_plan = mgr.create_daily_plan(format_date(current_date), format_datetime(current_date_time))

    return daily_plan

@pytest.fixture(scope="module")
def recovery_session(soreness_list, target_minutes, max_severity, historic_soreness_present=False,
                     functional_strength_active=False, is_active_prep=True):
    target_recovery_session = session.RecoverySession()
    target_recovery_session.set_exercise_target_minutes(soreness_list, target_minutes, max_severity,
                                                        historic_soreness_present=historic_soreness_present,
                                                        functional_strength_active=functional_strength_active,
                                                        is_active_prep=is_active_prep)
    return target_recovery_session


@pytest.fixture(scope="module")
def soreness_one_body_part(body_enum, severity_score, historic_soreness_status,treatment_priority=1):
    soreness_list = []
    soreness_item = Soreness()
    soreness_item.historic_soreness_status = historic_soreness_status
    soreness_item.severity = severity_score
    soreness_body_part = BodyPart(BodyPartLocation(body_enum),
                                                  treatment_priority)
    soreness_item.body_part = soreness_body_part
    soreness_list.append(soreness_item)
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


def convert_assigned_exercises(assigned_exercises):

    exercise_list = []

    for a in assigned_exercises:
        exercise_list.append(a.exercise.id)

    return exercise_list

def convert_assigned_dict_exercises(assigned_exercises):

    exercise_list = []

    for key, assigned_exercise in assigned_exercises.items():
        exercise_list.append(str(key))

    return exercise_list

def get_goals_triggers(assigned_exercises):

    goal_trigger_list = []

    for key, assigned_exercise in assigned_exercises.items():
        for d in assigned_exercises[key].dosages:
            goals = 'Goal=' + d.goal.text.replace(',','-') + '-->' + d.goal.trigger.replace(',',';') + ' Priority=' + d.priority + ' Dosages='
            goals += "Eff Reps="+ str(d.efficient_reps_assigned) + ' & Eff Sets=' + str(d.efficient_sets_assigned)
            goals += " & Complete Reps=" + str(d.complete_reps_assigned) + ' & Complete Sets=' + str(
                d.complete_sets_assigned)
            goals += " & Compr Reps=" + str(d.comprehensive_reps_assigned) + ' & Compr Sets=' + str(
                d.comprehensive_sets_assigned)
            goal_trigger_list.append(goals)

    unique_list = set(goal_trigger_list)

    return unique_list

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

def test_pre_active_rest_limited_body_parts():

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(9, 0, 0))
    current_date_time = current_date_time - timedelta(days=16)

    athlete_id = "tester"
    made_it_through = False
    max_severity_1 = [1, 2, 3, 4, 5]

    is_pain_1 = [True, False]

    body_parts_1 = [4, 5, 6, 7, 8, 11, 14, 15, 16]

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

    f = open('pre_ar_plans_time.csv', 'w')
    line = ('BodyPart,is_pain,severity,hs_status,default_plan'+
            'inhibit_goals_triggers,inhibit_minutes_efficient,inhibit_miniutes_complete, inhibit_minutes_comprehensive,'+
            'inhibit_exercises,static_stretch_goals_triggers,static_stretch_minutes_efficient,'+
            'static_stretch_minutes_complete,static_stretch_minutes_comprehensive, static_stretch_exercises,' +
            'active_stretch_goals_triggers, active_stretch_minutes_efficient, active_stretch_minutes_complete,'+
            'active_stretch_minutes_comprehensive, active_stretch_exercises,isolated_activate_goals_triggers,'+
            'isolated_activate_minutes_efficient, isolated_activate_minutes_complete,isolated_activate_minutes_comprehensive,'+
            'isolated_activate_exercises,static_integrate_goals_triggers,static_integrate_minutes_efficient, '+
            'static_integrate_minutes_complete,static_integrate_minutes_comprehensive, static_integrate_exercises,'+
            'total_minutes_efficient, total_minutes_complete, total_minutes_comprehensive')
    f.write(line + '\n')

    for b1 in body_parts_1:
        for m1 in max_severity_1:
            for h1 in historic_soreness_status_1:
                for p in is_pain_1:
                    soreness_list = []

                    historic_soreness = HistoricSoreness(BodyPartLocation(14), 1, True)
                    historic_soreness.first_reported = current_date_time
                    historic_soreness.historic_soreness_status = h1

                    if not p:
                        soreness_list.extend(soreness_one_body_part(b1, m1, h1))
                    else:
                        soreness_list.extend(pain_one_body_part(b1, m1, h1))

                    body_part_line = (
                            str(BodyPartLocation(b1)) + ',' + str(p) + ',' + str(m1) + ',' + str(h1))

                    daily_plan = create_plan(body_part_list=[b1], severity_list=[m1], side_list=[1],
                                             pain_list=[p], historic_soreness_list=[historic_soreness])

                    body_part_line += ',' + daily_plan.pre_active_rest.default_plan

                    inhibit_goals_triggers = get_goals_triggers(daily_plan.pre_active_rest.inhibit_exercises)
                    static_stretch_goals_triggers = get_goals_triggers(daily_plan.pre_active_rest.static_stretch_exercises)
                    active_stretch_goals_triggers = get_goals_triggers(daily_plan.pre_active_rest.active_stretch_exercises)
                    isolated_activate_goals_triggers = get_goals_triggers(daily_plan.pre_active_rest.isolated_activate_exercises)
                    static_integrate_goals_triggers = get_goals_triggers(daily_plan.pre_active_rest.static_integrate_exercises)

                    efficient_inhibit_minutes = calc_active_time_efficient(daily_plan.pre_active_rest.inhibit_exercises)
                    efficient_static_stretch_minutes = calc_active_time_efficient(
                        daily_plan.pre_active_rest.static_stretch_exercises)
                    efficient_active_stretch_minutes = calc_active_time_efficient(
                        daily_plan.pre_active_rest.active_stretch_exercises)
                    efficient_isolated_activate_minutes = calc_active_time_efficient(
                        daily_plan.pre_active_rest.isolated_activate_exercises)
                    efficient_static_integrate_minutes = calc_active_time_efficient(
                        daily_plan.pre_active_rest.static_integrate_exercises)
                    efficient_total_minutes = efficient_inhibit_minutes + efficient_static_stretch_minutes + efficient_active_stretch_minutes + efficient_isolated_activate_minutes + efficient_static_integrate_minutes

                    complete_inhibit_minutes = calc_active_time_complete(daily_plan.pre_active_rest.inhibit_exercises)
                    complete_static_stretch_minutes = calc_active_time_complete(daily_plan.pre_active_rest.static_stretch_exercises)
                    complete_active_stretch_minutes = calc_active_time_complete(daily_plan.pre_active_rest.active_stretch_exercises)
                    complete_isolated_activate_minutes = calc_active_time_complete(daily_plan.pre_active_rest.isolated_activate_exercises)
                    complete_static_integrate_minutes = calc_active_time_complete(daily_plan.pre_active_rest.static_integrate_exercises)
                    complete_total_minutes = complete_inhibit_minutes + complete_static_stretch_minutes + complete_active_stretch_minutes + complete_isolated_activate_minutes + complete_static_integrate_minutes

                    comprehensive_inhibit_minutes = calc_active_time_comprehensive(daily_plan.pre_active_rest.inhibit_exercises)
                    comprehensive_static_stretch_minutes = calc_active_time_comprehensive(
                        daily_plan.pre_active_rest.static_stretch_exercises)
                    comprehensive_active_stretch_minutes = calc_active_time_comprehensive(
                        daily_plan.pre_active_rest.active_stretch_exercises)
                    comprehensive_isolated_activate_minutes = calc_active_time_comprehensive(
                        daily_plan.pre_active_rest.isolated_activate_exercises)
                    comprehensive_static_integrate_minutes = calc_active_time_comprehensive(
                        daily_plan.pre_active_rest.static_integrate_exercises)
                    comprehensive_total_minutes = comprehensive_inhibit_minutes + comprehensive_static_stretch_minutes + comprehensive_active_stretch_minutes + comprehensive_isolated_activate_minutes + comprehensive_static_integrate_minutes

                    line = (body_part_line + ',' +

                            ' ** '.join(inhibit_goals_triggers) + ',' +

                            str(round(efficient_inhibit_minutes, 2)) + ',' + str(round(complete_inhibit_minutes, 2)) + ',' + str(round(comprehensive_inhibit_minutes, 2)) + ',' +

                            ';'.join(convert_assigned_dict_exercises(
                                daily_plan.pre_active_rest.inhibit_exercises)) + ',' +

                            ' ** '.join(static_stretch_goals_triggers) + ',' +

                            str(round(efficient_static_stretch_minutes, 2)) + ',' + str(round(complete_static_stretch_minutes, 2)) + ',' + str(round(comprehensive_static_stretch_minutes, 2)) + ',' +

                            ';'.join(convert_assigned_dict_exercises(
                                daily_plan.pre_active_rest.static_stretch_exercises)) + ',' +

                            ' ** '.join(active_stretch_goals_triggers) + ',' +

                            str(round(efficient_active_stretch_minutes, 2)) + ',' +str(round(complete_active_stretch_minutes, 2)) + ',' +str(round(comprehensive_active_stretch_minutes, 2)) + ',' +

                            ';'.join(convert_assigned_dict_exercises(
                                daily_plan.pre_active_rest.active_stretch_exercises)) + ',' +

                            ' ** '.join(isolated_activate_goals_triggers) + ',' +

                            str(round(efficient_isolated_activate_minutes, 2)) + ',' +str(round(complete_isolated_activate_minutes, 2)) + ',' +str(round(complete_isolated_activate_minutes, 2)) + ',' +

                            ';'.join(convert_assigned_dict_exercises(
                                daily_plan.pre_active_rest.isolated_activate_exercises)) + ',' +

                            ' ** '.join(static_integrate_goals_triggers) + ',' +

                            str(round(efficient_static_integrate_minutes, 2)) + ',' +str(round(complete_static_integrate_minutes, 2)) + ',' +str(round(comprehensive_static_integrate_minutes, 2)) + ',' +

                            ';'.join(convert_assigned_dict_exercises(
                                daily_plan.pre_active_rest.static_integrate_exercises)) + ',' +

                            str(round(efficient_total_minutes, 2))+ ',' +str(round(complete_total_minutes, 2))+ ',' +str(round(comprehensive_total_minutes, 2))

                            )
                    f.write(line + '\n')

    f.close()

    made_it_through = True


def test_no_soreness_baseline_active_prep_no_fs_1_body_part():

    target_minutes = 15
    athlete_id = "tester"
    made_it_through = False
    historic_soreness_present = False
    max_severity_1 = [1, 3, 5]

    fs_active = [False, True]
    is_active_prep = [False, True]
    is_pain_1 = False

    body_parts_1 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18]

    historic_soreness_status_1 = [HistoricSorenessStatus.dormant_cleared,
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

    f = open('hs_status_plans_single.csv', 'w')
    line = ('is_active_prep,fs_active,BodyPart,is_pain,severity,hs_status,inhibit_target_minutes,' +
            'inhibit_max_percentage,inhibit_minutes,inhibit_percentage,inhibit_iterations,' +
            'inhibit_exercises,lengthen_target_minutes,lengthen_max_percentage,lengthen_minutes,' +
            'lengthen_percentage,lengthen_iterations,lengthen_exercises,activate_target_minutes,' +
            'activate_max_percentage,activate_minutes,activate_percentage,activate_iterations,' +
            'activate_exercises')
    f.write(line + '\n')

    for b1 in body_parts_1:
        for m1 in max_severity_1:
            for h1 in historic_soreness_status_1:
                for fs in fs_active:
                    for ap in is_active_prep:

                        soreness_list = []
                        historic_soreness_present = False
                        is_pain_1 = is_status_pain(h1)
                        severity = m1

                        if h1 != HistoricSorenessStatus.dormant_cleared:
                            historic_soreness_present = True

                        if not is_pain_1:
                            soreness_list.extend(soreness_one_body_part(b1, m1, h1))
                        else:
                            soreness_list.extend(pain_one_body_part(b1, m1, h1))
                        historic_soreness_present = True
                        body_part_line = (
                                str(BodyPartLocation(b1)) + ',' + str(is_pain_1) + ',' + str(m1) + ',' + str(h1))

                        recovery = recovery_session(soreness_list,
                                                    target_minutes,
                                                    severity,
                                                    historic_soreness_present,
                                                    fs,
                                                    ap)
                        calc = exercise_mapping.ExerciseAssignmentCalculator(athlete_id,
                                                                             exercise_library_datastore,
                                                                             completed_exercise_datastore,
                                                                             historic_soreness_present)
                        exercise_assignments = calc.create_exercise_assignments(recovery, soreness_list,
                                                                                get_trigger_date_time(),
                                                                                target_minutes)

                        line = (str(ap) + ',' + str(fs) + ',' + body_part_line + ',' +

                                str(round(
                                    exercise_assignments.inhibit_target_minutes if exercise_assignments.inhibit_target_minutes is not None else 0,
                                    2)) + ',' +
                                str(round(
                                    exercise_assignments.inhibit_max_percentage if exercise_assignments.inhibit_max_percentage is not None else 0,
                                    2)) + ',' +
                                str(round(exercise_assignments.inhibit_minutes, 2)) + ',' +
                                str(round(
                                    exercise_assignments.inhibit_percentage if exercise_assignments.inhibit_percentage is not None else 0,
                                    2)) + ',' +
                                str(round(exercise_assignments.inhibit_iterations, 2)) + ',' +
                                ';'.join(convert_assigned_exercises(
                                    exercise_assignments.inhibit_exercises)) + ',' +

                                str(round(
                                    exercise_assignments.lengthen_target_minutes if exercise_assignments.lengthen_target_minutes is not None else 0,
                                    2)) + ',' +
                                str(round(
                                    exercise_assignments.lengthen_max_percentage if exercise_assignments.lengthen_max_percentage is not None else 0,
                                    2)) + ',' +
                                str(round(exercise_assignments.lengthen_minutes, 2)) + ',' +
                                str(round(
                                    exercise_assignments.lengthen_percentage if exercise_assignments.lengthen_percentage is not None else 0,
                                    2)) + ',' +
                                str(round(exercise_assignments.lengthen_iterations, 2)) + ',' +
                                ';'.join(convert_assigned_exercises(
                                    exercise_assignments.lengthen_exercises)) + ',' +

                                str(round(
                                    exercise_assignments.activate_target_minutes if exercise_assignments.activate_target_minutes is not None else 0,
                                    2)) + ',' +
                                str(round(
                                    exercise_assignments.activate_max_percentage if exercise_assignments.activate_max_percentage is not None else 0,
                                    2)) + ',' +
                                str(round(exercise_assignments.activate_minutes, 2)) + ',' +
                                str(round(
                                    exercise_assignments.activate_percentage if exercise_assignments.activate_percentage is not None else 0,
                                    2)) + ',' +
                                str(round(exercise_assignments.activate_iterations, 2)) + ',' +
                                ';'.join(
                                    convert_assigned_exercises(exercise_assignments.activate_exercises)))
                        f.write(line + '\n')

    f.close()

    made_it_through = True

    assert made_it_through is True

def test_no_soreness_baseline_active_prep_no_fs_2_body_parts():

    target_minutes = 15
    athlete_id = "tester"
    made_it_through = False
    historic_soreness_present = False
    max_severity_1 = [1, 3, 5]
    max_severity_2 = [3]
    fs_active = [False, True]
    is_active_prep = [False, True]
    is_pain_1 = False
    is_pain_2 = False
    body_parts_1 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18]
    body_parts_2 = [3, 5, 8, 11, 14, 17]


    historic_soreness_status_1 = [HistoricSorenessStatus.dormant_cleared,
                                    HistoricSorenessStatus.acute_pain,
                                    HistoricSorenessStatus.persistent_pain,
                                    HistoricSorenessStatus.persistent_2_pain,
                                    HistoricSorenessStatus.persistent_soreness,
                                    HistoricSorenessStatus.persistent_2_soreness]


    historic_soreness_status_2 = [HistoricSorenessStatus.dormant_cleared,
                                    HistoricSorenessStatus.acute_pain,
                                    HistoricSorenessStatus.persistent_pain,
                                    HistoricSorenessStatus.persistent_2_pain,
                                    HistoricSorenessStatus.persistent_soreness,
                                    HistoricSorenessStatus.persistent_2_soreness]

    f = open('hs_status_plans.csv', 'w')
    line = ('is_active_prep,fs_active,BodyPart-is_pain-severity-hs_status,inhibit_target_minutes,' +
            'inhibit_max_percentage,inhibit_minutes,inhibit_percentage,inhibit_iterations,' +
            'inhibit_exercises,lengthen_target_minutes,lengthen_max_percentage,lengthen_minutes,' +
            'lengthen_percentage,lengthen_iterations,lengthen_exercises,activate_target_minutes,' +
            'activate_max_percentage,activate_minutes,activate_percentage,activate_iterations,' +
            'activate_exercises')
    f.write(line + '\n')

    for b1 in body_parts_1:
        for m1 in max_severity_1:
            for h1 in historic_soreness_status_1:
                for fs in fs_active:
                    for ap in is_active_prep:
                        for b2 in body_parts_2:

                            if b2 >= b1:
                                if b2 > b1:
                                    for h2 in historic_soreness_status_2:
                                        for m2 in max_severity_2:
                                            soreness_list = []
                                            historic_soreness_present = False
                                            is_pain_1 = is_status_pain(h1)
                                            severity = m1

                                            if h1 != HistoricSorenessStatus.dormant_cleared:
                                                historic_soreness_present = True

                                            if not is_pain_1:
                                                soreness_list.extend(soreness_one_body_part(b1, m1, h1))
                                            else:
                                                soreness_list.extend(pain_one_body_part(b1, m1, h1))
                                            historic_soreness_present = True
                                            body_part_line = (
                                                    str(BodyPartLocation(b1)) + '-' + str(is_pain_1) + '-' + str(
                                                m1) + '-' + str(h1))
                                            is_pain_2 = is_status_pain(h2)

                                            if h2 != HistoricSorenessStatus.dormant_cleared:
                                                historic_soreness_present = True

                                            if not is_pain_2:
                                                soreness_list.extend(soreness_one_body_part(b2, m2, h2))
                                            else:
                                                soreness_list.extend(pain_one_body_part(b2, m2, h2))

                                            severity = max(m1, m2)
                                            body_part_line = (
                                                str(BodyPartLocation(b1)) + '-' + str(is_pain_1) + '-' + str(m1) + '-' + str(h1) + ';' +
                                                str(BodyPartLocation(b2)) + '-' + str(is_pain_2) + '-' + str(m2) + '-' + str(h2))

                                            recovery = recovery_session(soreness_list,
                                                                        target_minutes,
                                                                        severity,
                                                                        historic_soreness_present,
                                                                        fs,
                                                                        ap)
                                            calc = exercise_mapping.ExerciseAssignmentCalculator(athlete_id,
                                                                                                 exercise_library_datastore,
                                                                                                 completed_exercise_datastore,
                                                                                                 historic_soreness_present)
                                            exercise_assignments = calc.create_exercise_assignments(recovery, soreness_list,
                                                                                                    get_trigger_date_time(),
                                                                                                    target_minutes)



                                            line = (str(ap)+',' + str(fs) + ',' + body_part_line + ',' +

                                                    str(round(exercise_assignments.inhibit_target_minutes if exercise_assignments.inhibit_target_minutes is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.inhibit_max_percentage if exercise_assignments.inhibit_max_percentage is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.inhibit_minutes, 2)) + ',' +
                                                    str(round(exercise_assignments.inhibit_percentage if exercise_assignments.inhibit_percentage is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.inhibit_iterations, 2)) + ',' +
                                                    ';'.join(convert_assigned_exercises(exercise_assignments.inhibit_exercises)) + ',' +

                                                    str(round(exercise_assignments.lengthen_target_minutes if exercise_assignments.lengthen_target_minutes is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.lengthen_max_percentage if exercise_assignments.lengthen_max_percentage is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.lengthen_minutes, 2)) + ',' +
                                                    str(round(exercise_assignments.lengthen_percentage if exercise_assignments.lengthen_percentage is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.lengthen_iterations, 2)) + ',' +
                                                    ';'.join(convert_assigned_exercises(exercise_assignments.lengthen_exercises)) + ',' +

                                                    str(round(exercise_assignments.activate_target_minutes if exercise_assignments.activate_target_minutes is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.activate_max_percentage if exercise_assignments.activate_max_percentage is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.activate_minutes, 2)) + ',' +
                                                    str(round(exercise_assignments.activate_percentage if exercise_assignments.activate_percentage is not None else 0, 2)) + ',' +
                                                    str(round(exercise_assignments.activate_iterations, 2)) + ',' +
                                                    ';'.join(convert_assigned_exercises(exercise_assignments.activate_exercises)))
                                            f.write(line + '\n')
                                else:
                                    soreness_list = []
                                    historic_soreness_present = False
                                    is_pain_1 = is_status_pain(h1)
                                    severity = m1

                                    if h1 != HistoricSorenessStatus.dormant_cleared:
                                        historic_soreness_present = True

                                    if not is_pain_1:
                                        soreness_list.extend(soreness_one_body_part(b1, m1, h1))
                                    else:
                                        soreness_list.extend(pain_one_body_part(b1, m1, h1))
                                    historic_soreness_present = True
                                    body_part_line = (
                                            str(BodyPartLocation(b1)) + '-' + str(is_pain_1) + '-' + str(
                                        m1) + '-' + str(h1))

                                    recovery = recovery_session(soreness_list,
                                                                target_minutes,
                                                                severity,
                                                                historic_soreness_present,
                                                                fs,
                                                                ap)
                                    calc = exercise_mapping.ExerciseAssignmentCalculator(athlete_id,
                                                                                         exercise_library_datastore,
                                                                                         completed_exercise_datastore,
                                                                                         historic_soreness_present)
                                    exercise_assignments = calc.create_exercise_assignments(recovery, soreness_list,
                                                                                            get_trigger_date_time(),
                                                                                            target_minutes)

                                    line = (str(ap) + ',' + str(fs) + ',' + body_part_line + ',' +

                                            str(round(
                                                exercise_assignments.inhibit_target_minutes if exercise_assignments.inhibit_target_minutes is not None else 0,
                                                2)) + ',' +
                                            str(round(
                                                exercise_assignments.inhibit_max_percentage if exercise_assignments.inhibit_max_percentage is not None else 0,
                                                2)) + ',' +
                                            str(round(exercise_assignments.inhibit_minutes, 2)) + ',' +
                                            str(round(
                                                exercise_assignments.inhibit_percentage if exercise_assignments.inhibit_percentage is not None else 0,
                                                2)) + ',' +
                                            str(round(exercise_assignments.inhibit_iterations, 2)) + ',' +
                                            ';'.join(convert_assigned_exercises(
                                                exercise_assignments.inhibit_exercises)) + ',' +

                                            str(round(
                                                exercise_assignments.lengthen_target_minutes if exercise_assignments.lengthen_target_minutes is not None else 0,
                                                2)) + ',' +
                                            str(round(
                                                exercise_assignments.lengthen_max_percentage if exercise_assignments.lengthen_max_percentage is not None else 0,
                                                2)) + ',' +
                                            str(round(exercise_assignments.lengthen_minutes, 2)) + ',' +
                                            str(round(
                                                exercise_assignments.lengthen_percentage if exercise_assignments.lengthen_percentage is not None else 0,
                                                2)) + ',' +
                                            str(round(exercise_assignments.lengthen_iterations, 2)) + ',' +
                                            ';'.join(convert_assigned_exercises(
                                                exercise_assignments.lengthen_exercises)) + ',' +

                                            str(round(
                                                exercise_assignments.activate_target_minutes if exercise_assignments.activate_target_minutes is not None else 0,
                                                2)) + ',' +
                                            str(round(
                                                exercise_assignments.activate_max_percentage if exercise_assignments.activate_max_percentage is not None else 0,
                                                2)) + ',' +
                                            str(round(exercise_assignments.activate_minutes, 2)) + ',' +
                                            str(round(
                                                exercise_assignments.activate_percentage if exercise_assignments.activate_percentage is not None else 0,
                                                2)) + ',' +
                                            str(round(exercise_assignments.activate_iterations, 2)) + ',' +
                                            ';'.join(
                                                convert_assigned_exercises(exercise_assignments.activate_exercises)))
                                    f.write(line + '\n')

    f.close()

    made_it_through = True

    assert made_it_through is True