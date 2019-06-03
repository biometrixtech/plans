import pytest
import os
from aws_xray_sdk.core import xray_recorder
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore as MockDailyPlanDatastore
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore as MockAthleteStatsDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection as MockDatastoreCollection
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore as MockDailyReadinessDatastore
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore as MockPostSessionSurveyDatastore
from tests.mocks.mock_cleared_soreness_datastore import ClearedSorenessDatastore as MockClearedSorenessDatastore
from logic.training_plan_management import TrainingPlanManager
from logic.stats_processing import StatsProcessing
from tests.testing_utilities import TestUtilities, get_body_part_location_string, is_historic_soreness_pain, get_lines
from tests.database_tests.test_scenarios_spreadsheets import write_lines
from logic.training_volume_processing import TrainingVolumeProcessing
from logic.soreness_processing import SorenessCalculator
from models.stats import AthleteStats
from models.daily_readiness import DailyReadiness
from models.daily_plan import DailyPlan
from models.historic_soreness import HistoricSorenessStatus, SorenessCause
from config import get_secret
from utils import parse_date, format_date, format_datetime
from statistics import stdev, mean
from datetime import timedelta
from tests.testing_utilities import TestUtilities, get_body_part_location_string, is_historic_soreness_pain, \
    get_insights_string, get_alerts_ctas_goals_string, get_cool_down_line, get_goals_triggers, \
    calc_active_time_efficient, calc_active_time_complete, calc_active_time_comprehensive, get_summary_string, \
    convert_assigned_dict_exercises, get_priority_counts_for_dosages


mock_exercise_library_datastore = ExerciseLibraryDatastore()
mock_completed_exercise_datastore = CompletedExerciseDatastore()

@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):
    os.environ["ENVIRONMENT"] = "production"

    xray_recorder.configure(sampling=False)
    xray_recorder.begin_segment(name="test")

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

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    mock_exercise_library_datastore.side_load_exericse_list_from_csv()

def get_dates(start_date, end_date):

    dates = []

    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates

def get_soreness_string(soreness_list):

    soreness_string = ""

    for s in soreness_list:
        soreness_string += ("BodyPart=" + str(s.body_part.location) + ";side=" + str(s.side) + ";pain=" + str(s.pain) +
                            ";severity=" + str(s.severity) + ";daily=" + str(s.daily) + ";status=" +
                            str(s.historic_soreness_status) + ';first_reported_date=' + str(s.first_reported_date_time)) + ';'

    return soreness_string

def test_generate_spreadsheets_for_personas():

    start_date = parse_date("2019-05-01")
    end_date = parse_date("2019-06-01")

    users = []
    user_names = []

    users.append('e1b09f08-fc83-4957-9321-463001650440') # becky
    user_names.append('becky')
    #users.append('93176a69-2d5d-4326-b986-ca6b04a9a29d') #liz
    #users.append('e4fff5dc-6467-4717-8cef-3f2cb13e5c33')  #abbey
    #users.append('82ccf294-7c1e-48e6-8149-c5a001e76f78')  #pene
    #users.append('8bca10bf-8bdd-4971-85ca-cb2712c32478') #rhonda
    #users.append('5e516e2e-ac2d-425e-ba4d-bf2689c28cec')  #td
    #users.append('4f5567c7-a592-4c26-b89d-5c1287884d37')  #megan
    #users.append('fac4be57-35d6-4952-8af9-02aadf979982')  #bay
    #users.append('e9d78b6f-8695-4556-9369-d6a5702c6cc7') #mwoodard
    #users.append('5756fac1-3080-4979-9746-9d4c9a700acf') #lillian
    #users.append('06f2c55d-780c-47cf-9742-a74535bea45f')  #RG (aka User 6 from usability report 4/2/19)

    for u in range(0, len(users)):

        user_id = users[u]
        user_name = user_names[u]

        mock_data_store_collection = MockDatastoreCollection()

        mock_daily_plan_datastore = MockDailyPlanDatastore()
        mock_athlete_stats_datastore = MockAthleteStatsDatastore()
        mock_daily_readiness_datastore = MockDailyReadinessDatastore()
        mock_post_session_survey_datastore = MockPostSessionSurveyDatastore()

        dates = get_dates(start_date, end_date)

        prod_plans_dao = DailyPlanDatastore()
        prod_plans = prod_plans_dao.get(user_id, format_date(start_date), format_date(end_date))

        #prod_drs_dao = DailyReadinessDatastore()
        #daily_readiness_surveys = prod_drs_dao.get(user_id, start_date, end_date, False)
        daily_readiness_surveys = [plan.daily_readiness_survey for plan in prod_plans if
                                   plan.daily_readiness_survey is not None]

        pss_dao = PostSessionSurveyDatastore()
        ps_surveys = []
        post_session_surveys = pss_dao.get(user_id, start_date, end_date)
        for p in post_session_surveys:
            ps_surveys.append(p.survey)

        mock_data_store_collection.daily_plan_datastore = mock_daily_plan_datastore
        mock_data_store_collection.exercise_datastore = mock_exercise_library_datastore
        mock_data_store_collection.athlete_stats_datastore = mock_athlete_stats_datastore
        mock_data_store_collection.daily_readiness_datastore = mock_daily_readiness_datastore
        mock_data_store_collection.post_session_survey_datastore = mock_post_session_survey_datastore

        athlete_stats = StatsProcessing(user_id, event_date=start_date,
                                        datastore_collection=mock_data_store_collection).process_athlete_stats()

        mock_data_store_collection.daily_readiness_datastore.side_load_surveys(daily_readiness_surveys)

        pre_active_rest_file = open('../../output_persona/' + user_name + '_pre_active_rest.csv', 'w')
        summary_pre_active_rest_file = open('../../output_persona/' + user_name + '_pre_active_rest_summary.csv', 'w')
        post_active_rest_file = open('../../output_persona/' + user_name + '_post_active_rest.csv', 'w')
        summary_post_active_rest_file = open('../../output_persona/' + user_name + '_post_active_rest_summary.csv', 'w')
        cooldown_file = open('../../output_persona/' + user_name + '_cooldown.csv', 'w')

        line = ('date,soreness,default_plan,insights,'+
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
        sline = ('date,soreness,default_plan,insights,' +
                 't:biomechanics_triggers,t:biomechanics_ctas,t:biomechanics_goals,t:response_triggers,t:response_ctas,t:response_goals,t:stress_triggers,t:stress_ctas,t:stress_goals,'+
                 'heat, pre_active_rest, post_active_rest, cooldown, ice, cold_water_immersion')
        cline = ('date,soreness,default_plan,alerts,dynamic_stretch,dynamic_integrate,ds_efficient_time, ds_complete_time,ds_comprehensive_time,'+
                 'di_efficient_time,di_complete_time,di_comprehensive_time')
        pre_active_rest_file.write(line + '\n')
        summary_pre_active_rest_file.write(sline + '\n')
        post_active_rest_file.write(line + '\n')
        summary_post_active_rest_file.write(sline + '\n')
        cooldown_file.write(cline + '\n')

        for date in dates:

            #yesterday = date - timedelta(days=1)

            #yesterdays_plans = list(p for p in prod_plans if parse_date(p.event_date).date() == yesterday.date())

            #mock_data_store_collection.daily_plan_datastore.daily_plans.extend(yesterdays_plans)

            surveys = list(r for r in daily_readiness_surveys if r.event_date.date() == date.date())

            # simulate nightly processing
            athlete_stats = StatsProcessing(user_id, event_date=date,
                                            datastore_collection=mock_data_store_collection).process_athlete_stats(current_athlete_stats=athlete_stats)

            if len(surveys) > 0:
                survey = surveys[0]

                train_later = False

                today_ps_surveys = list(p for p in ps_surveys if p.event_date.date() == date.date())

                if len(today_ps_surveys) > 0:
                    train_later = True

                daily_plan = DailyPlan(format_date(date))
                daily_plan.user_id = user_id
                daily_plan.train_later = train_later
                daily_plan.daily_readiness_survey = survey

                mock_data_store_collection.daily_plan_datastore.daily_plans.append(daily_plan)

                athlete_stats = StatsProcessing(user_id, event_date=date,
                                                datastore_collection=mock_data_store_collection).process_athlete_stats(
                                                current_athlete_stats=athlete_stats)

                mgr = TrainingPlanManager(user_id, mock_data_store_collection)

                mgr.daily_plan = mgr.create_daily_plan(format_date(date), format_datetime(survey.event_date),
                                                       athlete_stats=athlete_stats)

                body_part_line = str(date) + ',' + get_soreness_string(mgr.soreness_list)

                cool_down_line, line, sline = get_lines(mgr.daily_plan)

                if len(cool_down_line) > 0:
                    cool_down_line = body_part_line + ',' + cool_down_line
                    cooldown_file.write(cool_down_line + '\n')

                line = body_part_line + ',' + line
                pre_active_rest_file.write(line + '\n')
                sline = body_part_line + ',' + sline
                summary_pre_active_rest_file.write(sline + '\n')

                mock_data_store_collection.daily_plan_datastore.daily_plans[
                    len(mock_data_store_collection.daily_plan_datastore.daily_plans) - 1] = mgr.daily_plan

                daily_plans = list(p for p in prod_plans if format_date(date) == p.event_date)

                if len(daily_plans) > 0:
                    for t in range(0, len(daily_plans[0].training_sessions)):

                        #mgr = TrainingPlanManager(user_id, mock_data_store_collection)
                        #mgr.daily_plan = previous_plan

                        training_session = daily_plans[0].training_sessions[t]

                        mgr.daily_plan.training_sessions.append(training_session)

                        if t == len(daily_plans[0].training_sessions) - 1:
                            mgr.daily_plan.train_later = False
                        else:
                            mgr.daily_plan.train_later = True

                        mock_data_store_collection.daily_plan_datastore.daily_plans[
                            len(mock_data_store_collection.daily_plan_datastore.daily_plans) - 1] = mgr.daily_plan

                        athlete_stats = StatsProcessing(user_id, event_date=date,
                                                        datastore_collection=mock_data_store_collection).process_athlete_stats(
                            current_athlete_stats=athlete_stats)

                        #mgr.training_sessions.append(training_session)

                        #for p in post_session_surveys:
                        #    if p.session_id == training_session.id:
                        #        mgr.post_session_surveys.append(p.survey)

                        mgr = TrainingPlanManager(user_id, mock_data_store_collection)

                        mgr.daily_plan = mgr.create_daily_plan(format_date(date), format_datetime(training_session.created_date),
                                                               athlete_stats=athlete_stats)

                        body_part_line = str(date) + ',' + get_soreness_string(mgr.soreness_list)

                        cool_down_line, line, sline = get_lines(mgr.daily_plan)

                        if len(cool_down_line) > 0:
                            cool_down_line = body_part_line + ',' + cool_down_line
                            cooldown_file.write(cool_down_line + '\n')

                        line = body_part_line + ',' + line
                        sline = body_part_line + ',' + sline

                        if mgr.daily_plan.train_later:
                            pre_active_rest_file.write(line + '\n')
                            summary_pre_active_rest_file.write(sline + '\n')
                        else:
                            post_active_rest_file.write(line + '\n')
                            summary_post_active_rest_file.write(sline + '\n')

                        mock_data_store_collection.daily_plan_datastore.daily_plans[len(mock_data_store_collection.daily_plan_datastore.daily_plans) -1] = mgr.daily_plan

        pre_active_rest_file.close()
        post_active_rest_file.close()
        summary_pre_active_rest_file.close()
        summary_post_active_rest_file.close()
        cooldown_file.close()




