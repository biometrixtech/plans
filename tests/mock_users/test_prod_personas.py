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
from logic.survey_processing import SurveyProcessing
from tests.testing_utilities import TestUtilities, get_body_part_location_string, is_historic_soreness_pain, get_lines
from tests.database_tests.test_scenarios_spreadsheets import write_lines
from logic.training_volume_processing import TrainingVolumeProcessing
from logic.soreness_processing import SorenessCalculator
from models.stats import AthleteStats
from models.daily_readiness import DailyReadiness
from models.daily_plan import DailyPlan
from models.athlete_trend import VisualizationType
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

def get_trends_dashboard_training_volume(daily_plan):

    output = ""

    if daily_plan.trends.dashboard.training_volume_data is not None:
        output += daily_plan.event_date + ","
        count = 0
        for d in daily_plan.trends.dashboard.training_volume_data:
            if count > 0:
                output += ","
            output += str(round(d.training_volume, 2))
            count += 1
    else:
        output = daily_plan.event_date + ',0,0,0,0,0,0,0,0,0,0,0,0,0,0'

    return output

def get_trends_high_training_loads(daily_plan):

    output = ""
    found = False
    for i in daily_plan.trends.stress.alerts:
        if i.visualization_type == VisualizationType.session:
            found = True
            output += daily_plan.event_date + ","
            count = 0
            for d in i.data:
                if count > 0:
                    output += ","
                output += str(round(d.value, 2))
                count += 1
    if not found:
        output = daily_plan.event_date + ',0,0,0,0,0,0,0,0,0,0,0,0,0,0'

    return output


def get_trends_muscular_strain(daily_plan):

    output = ""
    found = False
    for i in daily_plan.trends.response.alerts:
        if i.visualization_type == VisualizationType.muscular_strain:
            found = True
            output += daily_plan.event_date + ","
            count = 0
            for d in i.data:
                if count > 0:
                    output += ","
                output += str(round(d.value, 2))
                count += 1
    if not found:
        output = daily_plan.event_date + ',0,0,0,0,0,0,0,0,0,0,0,0,0,0'

    return output


def get_trends_doms(daily_plan):

    output = ""
    found = False
    for i in daily_plan.trends.response.alerts:
        if i.visualization_type == VisualizationType.doms:
            found = True
            output += daily_plan.event_date + ","
            count = 0
            for d in i.data:
                if count > 0:
                    output += ","
                if d.value is None:
                    output += "None"
                else:
                    output += str(round(d.value, 2))
                count += 1
    if not found:
        output = daily_plan.event_date + ',0,0,0,0,0,0,0,0,0,0,0,0,0,0'

    return output

def get_soreness_string(soreness_list):

    soreness_string = ""
    pain_string = ""

    soreness_max_severity = 0
    pain_max_severity = 0

    for s in soreness_list:
        if s.pain:
            pain_max_severity = max(s.severity, pain_max_severity)
            pain_string += ("BodyPart=" + str(s.body_part.location) + ";side=" + str(s.side) +
                                ";severity=" + str(s.severity) + ";daily=" + str(s.daily) + ";status=" +
                                str(s.historic_soreness_status) + ';first_reported_date=' + str(s.first_reported_date_time)) + ';'

        else:
            soreness_max_severity = max(s.severity, soreness_max_severity)

            soreness_string += ("BodyPart=" + str(s.body_part.location) + ";side=" + str(s.side) +
                                ";severity=" + str(s.severity) + ";daily=" + str(s.daily) + ";status=" +
                                str(s.historic_soreness_status) + ';first_reported_date=' + str(s.first_reported_date_time)) + ';'

    full_string = soreness_string + "," + str(soreness_max_severity) + "," + pain_string + "," + str(pain_max_severity)

    return full_string

def test_generate_spreadsheets_for_personas():

    start_date = parse_date("2019-05-01")
    end_date = parse_date("2019-06-04")

    users = []
    user_names = []

    users.append('e1b09f08-fc83-4957-9321-463001650440')
    user_names.append('becky')

    users.append('06f2c55d-780c-47cf-9742-a74535bea45f')
    user_names.append('rachael')

    users.append('55b040ff-4eab-4469-be30-39ab4574c3b3')
    user_names.append('gary')

    users.append('589c625a-cdd6-429f-aa36-3ae66756af3b')
    user_names.append('cm')

    users.append('d061ca16-b1e1-4d20-b483-8f9c740064c0')
    user_names.append('ryan')

    users.append('e83814ba-3784-4b24-8a23-95cd8d238045')
    user_names.append('connor')

    users.append('e9d78b6f-8695-4556-9369-d6a5702c6cc7')
    user_names.append('matthew')

    users.append('a8172baf-4ca9-4676-84a6-e64f3cd50b13')
    user_names.append('doug')

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

        #mock_data_store_collection.daily_readiness_datastore.side_load_surveys(daily_readiness_surveys)

        pre_active_rest_file = open('../../output_persona/' + user_name + '_pre_active_rest.csv', 'w')
        summary_pre_active_rest_file = open('../../output_persona/' + user_name + '_pre_active_rest_summary.csv', 'w')
        post_active_rest_file = open('../../output_persona/' + user_name + '_post_active_rest.csv', 'w')
        summary_post_active_rest_file = open('../../output_persona/' + user_name + '_post_active_rest_summary.csv', 'w')
        cooldown_file = open('../../output_persona/' + user_name + '_cooldown.csv', 'w')
        training_volume_file = open('../../output_persona/' + user_name + '_chart_training_volume.csv', 'w')
        high_training_load_file = open('../../output_persona/' + user_name + '_chart_high_training_load.csv', 'w')
        muscular_strain_file = open('../../output_persona/' + user_name + '_chart_muscular_strain.csv', 'w')
        doms_file = open('../../output_persona/' + user_name + '_chart_doms.csv', 'w')

        line = ('date,soreness,soreness_max_severity,pain, pain_max_severity, default_plan,insights,'+
                't:biomechanics_triggers,t:biomechanics_goals,t:response_triggers,t:response_goals,t:stress_triggers,t:stress_goals,'+
                'inhibit_goals_triggers,inhibit_minutes_efficient,inhibit_miniutes_complete, inhibit_minutes_comprehensive,'+
                'inhibit_exercises,static_stretch_goals_triggers,static_stretch_minutes_efficient,'+
                'static_stretch_minutes_complete,static_stretch_minutes_comprehensive, static_stretch_exercises,' +
                'active_stretch_goals_triggers, active_stretch_minutes_efficient, active_stretch_minutes_complete,'+
                'active_stretch_minutes_comprehensive, active_stretch_exercises,isolated_activate_goals_triggers,'+
                'isolated_activate_minutes_efficient, isolated_activate_minutes_complete,isolated_activate_minutes_comprehensive,'+
                'isolated_activate_exercises,static_integrate_goals_triggers,static_integrate_minutes_efficient, '+
                'static_integrate_minutes_complete,static_integrate_minutes_comprehensive, static_integrate_exercises,'+
                'total_minutes_efficient, total_minutes_complete, total_minutes_comprehensive,priority_1_count,priority_2_count,priority_3_count')
        sline = ('date,soreness,soreness_max_severity,pain, pain_max_severity, default_plan,insights,' +
                 't:biomechanics_triggers,t:biomechanics_goals,t:response_triggers,t:response_goals,t:stress_triggers,t:stress_goals,'+
                 'heat, pre_active_rest, post_active_rest, cooldown, ice, cold_water_immersion')
        cline = ('date,soreness,soreness_max_severity,pain, pain_max_severity,default_plan,alerts,dynamic_stretch,dynamic_integrate,ds_efficient_time, ds_complete_time,ds_comprehensive_time,'+
                 'di_efficient_time,di_complete_time,di_comprehensive_time')
        tline = ('date, day_14,day_13, day_12, day_11, day_10, day_9, day_8, day_7, day_6, day_5, day_4, day_3, day_2, day_1')
        pre_active_rest_file.write(line + '\n')
        summary_pre_active_rest_file.write(sline + '\n')
        post_active_rest_file.write(line + '\n')
        summary_post_active_rest_file.write(sline + '\n')
        cooldown_file.write(cline + '\n')
        training_volume_file.write(tline + '\n')
        high_training_load_file.write(tline + '\n')
        muscular_strain_file.write(tline + '\n')
        doms_file.write(tline + '\n')

        for date in dates:

            #yesterday = date - timedelta(days=1)

            #yesterdays_plans = list(p for p in prod_plans if parse_date(p.event_date).date() == yesterday.date())

            #mock_data_store_collection.daily_plan_datastore.daily_plans.extend(yesterdays_plans)

            surveys = list(r for r in daily_readiness_surveys if r.event_date.date() == date.date())

            # simulate nightly processing
            athlete_stats = StatsProcessing(user_id, event_date=date,
                                            datastore_collection=mock_data_store_collection).process_athlete_stats(current_athlete_stats=athlete_stats)

            if len(surveys) > 0:

                # in athlete stats look for either question being asked
                candidate_clear_candidates = []
                for h in athlete_stats.historic_soreness:
                    if h.ask_acute_pain_question or h.ask_persistent_2_question:
                        candidate_clear_candidates.append(h)

                survey = surveys[0]

                # check for body part exists in survey to determine
                clear_candidates = []
                for c in candidate_clear_candidates:
                    #is final pain condition correct?
                    matches = list(s for s in survey.soreness if c.body_part_location == s.body_part.location and
                                   c.side == s.side and c.is_pain == s.pain)
                    if len(matches) == 0:
                        soreness = {
                            "body_part": c.body_part_location.value,
                            "severity": 0,
                            "movement": 0,
                            "side": c.side,
                            "pain": c.is_pain,
                            "status": c.historic_soreness_status.name
                        }
                        # pain?
                        clear_candidates.append(soreness)

                # survey processing, answer appropriate question
                survey_processing = SurveyProcessing(user_id, date, athlete_stats, mock_data_store_collection)
                survey_processing.process_clear_status_answers(clear_candidates, date, survey.soreness)
                survey_processing.soreness = survey.soreness
                survey_processing.patch_daily_and_historic_soreness('readiness')
                athlete_stats = survey_processing.athlete_stats

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

                training_volume_line = get_trends_dashboard_training_volume(mgr.daily_plan)

                high_training_load_line = get_trends_high_training_loads(mgr.daily_plan)

                muscular_strain_line = get_trends_muscular_strain(mgr.daily_plan)

                doms_line = get_trends_doms(mgr.daily_plan)

                cool_down_line, line, sline = get_lines(mgr.daily_plan)

                if len(cool_down_line) > 0:
                    cool_down_line = body_part_line + ',' + cool_down_line
                    cooldown_file.write(cool_down_line + '\n')

                line = body_part_line + ',' + line
                pre_active_rest_file.write(line + '\n')
                sline = body_part_line + ',' + sline
                summary_pre_active_rest_file.write(sline + '\n')
                training_volume_file.write(training_volume_line + '\n')
                high_training_load_file.write(high_training_load_line + '\n')
                muscular_strain_file.write(muscular_strain_line + '\n')
                doms_file.write(doms_line + '\n')

                mock_data_store_collection.daily_plan_datastore.daily_plans[
                    len(mock_data_store_collection.daily_plan_datastore.daily_plans) - 1] = mgr.daily_plan

                daily_plans = list(p for p in prod_plans if format_date(date) == p.event_date)

                if len(daily_plans) > 0:
                    for t in range(0, len(daily_plans[0].training_sessions)):

                        training_session = daily_plans[0].training_sessions[t]

                        survey_processing = SurveyProcessing(user_id, date, athlete_stats, mock_data_store_collection)
                        survey_processing.soreness = training_session.post_session_soreness
                        survey_processing.sessions.append(training_session)
                        survey_processing.patch_daily_and_historic_soreness('post_session')
                        survey_processing.check_high_relative_load_sessions(survey_processing.sessions)
                        athlete_stats = survey_processing.athlete_stats

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

                        high_training_load_line = get_trends_high_training_loads(mgr.daily_plan)

                        muscular_strain_line = get_trends_muscular_strain(mgr.daily_plan)

                        doms_line = get_trends_doms(mgr.daily_plan)

                        training_volume_line = get_trends_dashboard_training_volume(mgr.daily_plan)

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
                        training_volume_file.write(training_volume_line + '\n')
                        high_training_load_file.write(high_training_load_line + '\n')
                        muscular_strain_file.write(muscular_strain_line + '\n')
                        doms_file.write(doms_line + '\n')

                        mock_data_store_collection.daily_plan_datastore.daily_plans[len(mock_data_store_collection.daily_plan_datastore.daily_plans) -1] = mgr.daily_plan

        pre_active_rest_file.close()
        post_active_rest_file.close()
        summary_pre_active_rest_file.close()
        summary_post_active_rest_file.close()
        cooldown_file.close()
        training_volume_file.close()
        high_training_load_file.close()
        muscular_strain_file.close()
        doms_file.close()




