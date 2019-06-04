from aws_xray_sdk.core import xray_recorder

xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from logic.training_plan_management import TrainingPlanManager
from models.session import SportTrainingSession
from models.historic_soreness import HistoricSoreness
from models.stats import AthleteStats
from pandas import DataFrame
from datetime import datetime, timedelta, date, time
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from models.soreness import Soreness, BodyPart, BodyPartLocation, HistoricSorenessStatus
from models.daily_plan import DailyPlan
from models.sport import SportName
from tests.testing_utilities import TestUtilities, get_body_part_location_string, is_historic_soreness_pain, \
    get_lines
from models.daily_readiness import DailyReadiness
from models.data_series import DataSeries
from utils import format_datetime, format_date
import random

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()
df = DataFrame()


class TestParameters(object):
    def __init__(self, file_name, athlete_stats, train_later, high_volume, doms=False, no_soreness=False):
        self.file_name = file_name
        self.athlete_stats = athlete_stats
        self.train_later = train_later
        self.high_volume = high_volume
        self.doms = doms
        self.no_soreness = no_soreness


def get_test_parameters_list(current_date):

    parm_list = []

    as1 = AthleteStats("tester")
    as1.historic_soreness = []
    as1.muscular_strain_increasing = False
    parm_list.append(TestParameters("PreActiveRest_no_doms_no_muscular_strain_no_high_volume", as1, train_later=True, high_volume=False))
    parm_list.append(TestParameters("PostActiveRest_no_doms_no_muscular_strain_no_high_volume", as1, train_later=False, high_volume=False))
    parm_list.append(TestParameters("PreActiveRest_no_doms_no_muscular_strain_no_high_volume_no_soreness", as1, train_later=True, high_volume=False, no_soreness=True))
    parm_list.append(TestParameters("PostActiveRest_no_doms_no_muscular_strain_no_high_volume_no_soreness", as1, train_later=False, high_volume=False, no_soreness=True))
    parm_list.append(TestParameters("PreActiveRest_no_doms_no_muscular_strain_high_volume", as1, train_later=True, high_volume=True))
    parm_list.append(TestParameters("PostActiveRest_no_doms_no_muscular_strain_high_volume", as1, train_later=False, high_volume=True))
    parm_list.append(TestParameters("PreActiveRest_no_doms_no_muscular_strain_high_volume_no_soreness", as1, train_later=True,
                           high_volume=True, no_soreness=True))
    parm_list.append(TestParameters("PostActiveRest_no_doms_no_muscular_strain_high_volume_no_soreness", as1, train_later=False,
                           high_volume=True, no_soreness=True))

    as2 = AthleteStats("tester")
    as2.historic_soreness = []
    as2.muscular_strain_increasing = True

    high_muscular_strain = DataSeries(current_date, 35)
    low_muscular_strain = DataSeries(current_date, 65)

    as1.muscular_strain.append(low_muscular_strain)
    as2.muscular_strain.append(high_muscular_strain)

    parm_list.append(TestParameters("PreActiveRest_no_doms_muscular_strain_no_high_volume", as2, train_later=True, high_volume=False))
    parm_list.append(TestParameters("PostActiveRest_no_doms_muscular_strain_no_high_volume", as2, train_later=False, high_volume=False))
    parm_list.append(TestParameters("PreActiveRest_no_doms_muscular_strain_high_volume", as2, train_later=True, high_volume=True))
    parm_list.append(TestParameters("PostActiveRest_no_doms_muscular_strain_high_volume", as2, train_later=False, high_volume=True))
    parm_list.append(TestParameters("PreActiveRest_no_doms_muscular_strain_no_high_volume_no_soreness", as2, train_later=True, high_volume=False, no_soreness=True))
    parm_list.append(TestParameters("PostActiveRest_no_doms_muscular_strain_no_high_volume_no_soreness", as2, train_later=False, high_volume=False, no_soreness=True))
    parm_list.append(TestParameters("PreActiveRest_no_doms_muscular_strain_high_volume_no_soreness", as2, train_later=True, high_volume=True, no_soreness=True))
    parm_list.append(TestParameters("PostActiveRest_no_doms_muscular_strain_high_volume_no_soreness", as2, train_later=False, high_volume=True, no_soreness=True))
    parm_list.append(TestParameters("PreActiveRest_doms_muscular_strain_no_high_volume", as2, train_later=True, high_volume=False, doms=True))
    parm_list.append(TestParameters("PostActiveRest_doms_muscular_strain_no_high_volume", as2, train_later=False, high_volume=False, doms=True))
    parm_list.append(TestParameters("PreActiveRest_doms_muscular_strain_high_volume", as2, train_later=True, high_volume=True, doms=True))
    parm_list.append(TestParameters("PostActiveRest_doms_muscular_strain_high_volume", as2, train_later=False, high_volume=True, doms=True))

    return parm_list

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def create_plan(test_parameter, body_part_list, severity_list, side_list, pain_list, train_later, historic_soreness_list=None):

    athlete_stats = test_parameter.athlete_stats

    training_sessions = []

    if test_parameter.high_volume:
        training_session = SportTrainingSession()
        training_session.session_RPE = 7
        training_session.sport_name = SportName.basketball
        training_sessions.append(training_session)

    user_id = athlete_stats.athlete_id

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    soreness_list = []
    for b in range(0, len(body_part_list)):
        if len(pain_list) > 0 and pain_list[b]:
            soreness_list.append(TestUtilities().body_part_pain(body_part_list[b], severity_list[b], side_list[b]))
        else:
            if len(severity_list) == 0:
                soreness_list.append(TestUtilities().body_part_soreness(body_part_list[b], 2, side=1))
            else:
                soreness_list.append(TestUtilities().body_part_soreness(body_part_list[b], severity_list[b], side=1))

    survey = DailyReadiness(current_date_time.strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 7, 9)

    daily_plan_datastore = DailyPlanDatastore()
    athlete_stats_datastore = AthleteStatsDatastore()
    athlete_stats.historic_soreness = historic_soreness_list
    for s in survey.soreness:
        if not s.pain and not s.is_joint():
            athlete_stats.update_delayed_onset_muscle_soreness(s)
    athlete_stats_datastore.side_load_athlete_stats(athlete_stats)

    daily_plan = DailyPlan(format_date(current_date))
    daily_plan.user_id = user_id
    daily_plan.train_later = train_later
    daily_plan.daily_readiness_survey = survey
    daily_plan_datastore.side_load_plans([daily_plan])
    data_store_collection = DatastoreCollection()
    data_store_collection.daily_plan_datastore = daily_plan_datastore
    data_store_collection.exercise_datastore = exercise_library_datastore
    data_store_collection.athlete_stats_datastore = athlete_stats_datastore

    '''
    if historic_soreness_list is not None and len(historic_soreness_list) > 0:
        athlete_stats_datastore = AthleteStatsDatastore()
        athlete_stats = AthleteStats(user_id)
       
        athlete_stats_datastore.side_load_athlete_stats(athlete_stats)
        data_store_collection.athlete_stats_datastore = athlete_stats_datastore
    '''
    mgr = TrainingPlanManager(user_id, data_store_collection)
    mgr.training_sessions = training_sessions

    athlete_stats.longitudinal_insights = []
    athlete_stats.longitudinal_trends = []
    daily_plan = mgr.create_daily_plan(format_date(current_date), format_datetime(current_date_time), athlete_stats=athlete_stats)

    return daily_plan

'''deprec
@pytest.fixture(scope="module")
def recovery_session(soreness_list, target_minutes, max_severity, historic_soreness_present=False,
                     functional_strength_active=False, is_active_prep=True):
    target_recovery_session = RecoverySession()
    target_recovery_session.set_exercise_target_minutes(soreness_list, target_minutes, max_severity,
                                                        historic_soreness_present=historic_soreness_present,
                                                        functional_strength_active=functional_strength_active,
                                                        is_active_prep=is_active_prep)
    return target_recovery_session
'''

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


def soreness_two_body_parts_random(body_part_list, body_enum, severity_score, historic_soreness_status,treatment_priority=1):

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


def test_generate_spreadsheets():

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(9, 0, 0))
    # current_date_time = current_date_time - timedelta(days=16)

    parm_list = get_test_parameters_list(current_date)

    for test_parm in parm_list:

        j = 0
        athlete_id = "tester"
        made_it_through = False

        historic_soreness_status_1 = [None,
                                      HistoricSorenessStatus.dormant_cleared,
                                      # HistoricSorenessStatus.almost_acute_pain,
                                      HistoricSorenessStatus.acute_pain,
                                      # HistoricSorenessStatus.almost_persistent_pain,
                                      HistoricSorenessStatus.persistent_pain,
                                      # HistoricSorenessStatus.almost_persistent_2_pain,
                                      # HistoricSorenessStatus.almost_persistent_2_pain_acute,
                                      HistoricSorenessStatus.persistent_2_pain,
                                      # HistoricSorenessStatus.almost_persistent_soreness,
                                      HistoricSorenessStatus.persistent_soreness,
                                      # HistoricSorenessStatus.almost_persistent_2_soreness,
                                      HistoricSorenessStatus.persistent_2_soreness]

        days_sore = [16, 32]

        if not test_parm.no_soreness:
            max_severity_1 = [1, 2, 3, 4, 5]

            is_pain_1 = [True, False]

            body_parts_1 = [1, 4, 5, 6, 7, 8, 11, 14, 15, 16]

        else:
            max_severity_1 = []
            is_pain_1 = []
            body_parts_1 = []

        f1 = open('../../output/' + test_parm.file_name + "_a.csv", 'w')
        s1 = open('../../output/' + 'summary_' + test_parm.file_name + "_a.csv", 'w')
        f2 = open('../../output/' + test_parm.file_name + "_b.csv", 'w')
        s2 = open('../../output/' + 'summary_' + test_parm.file_name + "_b.csv", 'w')
        c1 = open('../../output/' + test_parm.file_name + "_cooldown_a.csv", 'w')
        c2 = open('../../output/' + test_parm.file_name + "_cooldown_b.csv", 'w')

        f1_32 = open('../../output/' + test_parm.file_name + "_32_a.csv", 'w')
        s1_32 = open('../../output/' + 'summary_' + test_parm.file_name + "_32_a.csv", 'w')
        f2_32 = open('../../output/' + test_parm.file_name + "_32_b.csv", 'w')
        s2_32 = open('../../output/' + 'summary_' + test_parm.file_name + "_32_b.csv", 'w')
        c1_32 = open('../../output/' + test_parm.file_name + "_32_cooldown_a.csv", 'w')
        c2_32 = open('../../output/' + test_parm.file_name + "_32_cooldown_b.csv", 'w')

        line = ('BodyPart,is_pain,severity,hs_status,hs_days,default_plan,insights,'+
                't:biomechanics_triggers,t:biomechanics_ctas, t:biomechanics_goals,t:response_triggers,t:response_ctas,t:response_goals,t:stress_triggers,t:stress_ctas,t:stress_goals,'+
                'inhibit_goals_triggers,inhibit_minutes_efficient,inhibit_miniutes_complete, inhibit_minutes_comprehensive,'+
                'inhibit_exercises,static_stretch_goals_triggers,static_stretch_minutes_efficient,'+
                'static_stretch_minutes_complete,static_stretch_minutes_comprehensive, static_stretch_exercises,' +
                'active_stretch_goals_triggers, active_stretch_minutes_efficient, active_stretch_minutes_complete,'+
                'active_stretch_minutes_comprehensive, active_stretch_exercises,isolated_activate_goals_triggers,'+
                'isolated_activate_minutes_efficient, isolated_activate_minutes_complete,isolated_activate_minutes_comprehensive,'+
                'isolated_activate_exercises,static_integrate_goals_triggers,static_integrate_minutes_efficient, '+
                'static_integrate_minutes_complete,static_integrate_minutes_comprehensive, static_integrate_exercises,'+
                'total_minutes_efficient, total_minutes_complete, total_minutes_comprehensive,priority_1_count,priority_2_count,priority_3_count')
        sline = ('BodyPart,is_pain,severity,hs_status,hs_days,default_plan,insights,' +
                 't:biomechanics_triggers,t:biomechanics_ctas,t:biomechanics_goals,t:response_triggers,t:response_ctas,t:response_goals,t:stress_triggers,t:stress_ctas,t:stress_goals,'+
                 'heat, pre_active_rest, post_active_rest, cooldown, ice, cold_water_immersion')
        cline = ('BodyPart,is_pain,severity,hs_status,hs_days,default_plan,alerts,dynamic_stretch,dynamic_integrate,ds_efficient_time, ds_complete_time,ds_comprehensive_time,'+
                 'di_efficient_time,di_complete_time,di_comprehensive_time')
        f1.write(line + '\n')
        s1.write(sline + '\n')
        f2.write(line + '\n')
        s2.write(sline + '\n')
        c1.write(cline + '\n')
        c2.write(cline + '\n')
        f1_32.write(line + '\n')
        s1_32.write(sline + '\n')
        f2_32.write(line + '\n')
        s2_32.write(sline + '\n')
        c1_32.write(cline + '\n')
        c2_32.write(cline + '\n')

        for h1 in historic_soreness_status_1:
            for day_diff in days_sore:

                historic_soreness_list = []

                historic_soreness = HistoricSoreness(BodyPartLocation(14), 1, is_historic_soreness_pain(h1))
                historic_soreness.first_reported_date_time = current_date_time - timedelta(days=day_diff)
                historic_soreness.historic_soreness_status = h1
                #historic_soreness.average_severity = 2
                historic_soreness_list.append(historic_soreness)

                if test_parm.no_soreness:
                    daily_plan = create_plan(test_parameter=test_parm, body_part_list=[],
                                             severity_list=[], side_list=[],
                                             pain_list=[], train_later=test_parm.train_later,
                                             historic_soreness_list=[historic_soreness])

                    body_part_line = (
                            get_body_part_location_string([]) + ',N/A,N/A,' + str(h1) + ',' + str(day_diff))

                    cool_down_line, line, sline = get_lines(daily_plan)

                    if len(cool_down_line) > 0:
                        cool_down_line = body_part_line + ',' + cool_down_line

                    line = body_part_line + ',' + line
                    sline = body_part_line + ',' + sline

                    write_lines(c1, c1_32, c2, c2_32, cool_down_line, day_diff, f1, f1_32, f2, f2_32, j, line, s1,
                                s1_32, s2, s2_32, sline)
                    j += 1

                else:
                    for b1 in body_parts_1:
                        for m1 in max_severity_1:
                            for p in is_pain_1:
                                #if h1 == HistoricSorenessStatus.persistent_pain and b1==1:
                                #    k=0
                                if (0==0) or h1 == HistoricSorenessStatus.persistent_2_soreness and b1 == 14 and p == False and test_parm.doms and day_diff == 32:
                                    body_part_list = [b1]
                                    severity_list = [m1]
                                    pain_list = [p]

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

                                    body_part_line = (
                                            get_body_part_location_string(body_part_list) + ',' + str(p) + ',' + str(m1) + ',' + str(h1) + ',' + str(day_diff))

                                    cool_down_line, line, sline = get_lines(daily_plan)

                                    if len(cool_down_line) > 0:
                                        cool_down_line = body_part_line + ',' + cool_down_line

                                    line = body_part_line + ',' + line
                                    sline = body_part_line + ',' + sline

                                    write_lines(c1, c1_32, c2, c2_32, cool_down_line, day_diff, f1, f1_32, f2, f2_32, j,
                                                line, s1,
                                                s1_32, s2, s2_32, sline)
                                    j += 1

        f1.close()
        s1.close()
        f2.close()
        s2.close()
        c1.close()
        c2.close()

        made_it_through = True


def write_lines(c1, c1_32, c2, c2_32, cool_down_line, day_diff, f1, f1_32, f2, f2_32, j, line, s1, s1_32, s2, s2_32,
                sline):
    if j % 2 == 0:
        if day_diff == 32:
            s1_32.write(sline + '\n')
            f1_32.write(line + '\n')
            if len(cool_down_line) > 0:
                c1_32.write(cool_down_line + '\n')
        else:
            s1.write(sline + '\n')
            f1.write(line + '\n')
            if len(cool_down_line) > 0:
                c1.write(cool_down_line + '\n')
    else:
        if day_diff == 32:
            s2_32.write(sline + '\n')
            f2_32.write(line + '\n')
            if len(cool_down_line) > 0:
                c2_32.write(cool_down_line + '\n')
        else:
            s2.write(sline + '\n')
            f2.write(line + '\n')
            if len(cool_down_line) > 0:
                c2.write(cool_down_line + '\n')


