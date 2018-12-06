import pytest
from logic.functional_strength_mapping import FSProgramGenerator
from logic.stats_processing import StatsProcessing
from logic.training_plan_management import TrainingPlanManager
from models.stats import AthleteStats
from models.daily_plan import DailyPlan
from models.daily_readiness import DailyReadiness
from models.post_session_survey import PostSessionSurvey
from models.session import FunctionalStrengthSession, PracticeSession, SessionType
from models.sport import BasketballPosition, SportName, SoccerPosition, NoSportPosition, TrackAndFieldPosition, SoftballPosition, FieldHockeyPosition
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from tests.testing_utilities import TestUtilities
from datetime import datetime, timedelta

fs_exercise_library_datastore = ExerciseLibraryDatastore()
exercise_library_datastore = ExerciseLibraryDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    fs_exercise_library_datastore.side_load_exericse_list_from_csv(library_file='database/FS_Exercise_Library.csv',
                                                                   desc_file='database/FS_Exercise_Descriptions.tsv')

    exercise_library_datastore.side_load_exericse_list_from_csv(library_file='database/Exercise_Library.csv',
                                                                   desc_file='database/Exercise_Descriptions.tsv')

def get_dates(start_date, end_date):

    dates = []

    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates


def get_daily_plans(start_date, end_date):

    plans = []

    dates = get_dates(start_date, end_date)

    i = 1

    for d in dates:
        daily_plan = DailyPlan(event_date=d.strftime("%Y-%m-%d"))
        practice_session = PracticeSession()
        practice_session.event_date = d
        daily_plan.training_sessions.append(practice_session)
        plans.append(daily_plan)
        i += 1

    return plans

def get_daily_readiness_surveys(start_date, end_date):

    surveys = []

    dates = get_dates(start_date, end_date)

    for d in dates:
        soreness = TestUtilities().body_part_soreness(9, 1)
        daily_readiness = DailyReadiness(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", [soreness], 4, 5)
        surveys.append(daily_readiness)

    return surveys


def get_daily_readiness_survey_high_soreness(date, soreness_level):

    soreness = TestUtilities().body_part_soreness(9, soreness_level)
    daily_readiness = DailyReadiness(date.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", [soreness], 4, 5)

    return daily_readiness


def get_post_session_surveys(start_date, end_date):

    surveys = []

    dates = get_dates(start_date, end_date)

    for d in dates:
        soreness = TestUtilities().body_part_soreness(9, 1)

        soreness_list = [soreness]

        post_survey = TestUtilities().get_post_survey(6, soreness_list)

        post_session = PostSessionSurvey(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester",None, SessionType.practice, post_survey )
        surveys.append(post_session)

    return surveys


def test_generate_session_for_soccer():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.soccer, position=SoccerPosition.forward)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_generate_session_for_cycling():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.cycling)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_generate_session_for_field_hockey():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.field_hockey, FieldHockeyPosition.goalie)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_generate_session_for_rowing():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.rowing)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_generate_session_for_skate_sports():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.skate_sports)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_generate_session_for_softball():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.softball, SoftballPosition.catcher)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_generate_session_for_pool_sports():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.pool_sports)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_generate_session_for_sprinter():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.track_field, TrackAndFieldPosition.sprinter)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

    fs_session_power = mapping.getFunctionalStrengthForSportPosition(SportName.no_sport, NoSportPosition.power)
    assert True is ([i.json_serialise() for i in fs_session.warm_up] == [i.json_serialise() for i in fs_session_power.warm_up])
    assert True is ([i.json_serialise() for i in fs_session.dynamic_movement] == [i.json_serialise() for i in fs_session_power.dynamic_movement])
    assert True is ([i.json_serialise() for i in fs_session.stability_work] == [i.json_serialise() for i in fs_session_power.stability_work])
    assert True is ([i.json_serialise() for i in fs_session.victory_lap] == [i.json_serialise() for i in fs_session_power.victory_lap])

def test_generate_session_for_distance():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.track_field, TrackAndFieldPosition.distance)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_generate_session_for_speed():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.no_sport, position=NoSportPosition.speed_agility)
    assert True is (len(fs_session.warm_up) > 0)
    assert True is (len(fs_session.dynamic_movement) > 0)
    assert True is (len(fs_session.stability_work) > 0)
    assert True is (len(fs_session.victory_lap) > 0)
    assert True is (fs_session.duration_minutes > 0)

def test_fs_exercises_populated():
    mapping = FSProgramGenerator(fs_exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.basketball, position=BasketballPosition.guard)
    assert True is (len(fs_session.warm_up[0].exercise.description) > 0)


def test_athlete_doesnt_have_enough_training_sessions():
    stats_processing = StatsProcessing("tester", "2018-07-31", DatastoreCollection())
    logged_enough = stats_processing.athlete_logged_enough_sessions()
    assert False is logged_enough


def test_athlete_has_enough_training_sessions():

    plans_1_7_days = get_daily_plans(datetime(2018, 7, 24, 0, 0, 0), datetime(2018, 7, 30, 0, 0, 0))
    plans_8_14_days = get_daily_plans(datetime(2018, 7, 17, 0, 0, 0), datetime(2018, 7, 23, 0, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 7, 17, 12, 0, 0), datetime(2018, 7, 31, 0, 0, 0))
    ps_surveys = get_post_session_surveys(datetime(2018, 7, 17, 0, 0, 0), datetime(2018, 7, 30, 0, 0, 0))

    all_plans = []
    all_plans.extend(plans_8_14_days)
    all_plans.extend(plans_1_7_days)

    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(all_plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)
    post_session_datastore = PostSessionSurveyDatastore()
    post_session_datastore.side_load_surveys(ps_surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore
    datastore_collection.post_session_survey_datastore = post_session_datastore

    stats_processing = StatsProcessing("tester", "2018-07-31", datastore_collection)
    stats_processing.process_athlete_stats()
    logged_enough = stats_processing.athlete_logged_enough_sessions()
    assert True is logged_enough


def test_athlete_not_onboarded_two_weeks():
    stats_processing = StatsProcessing("tester", "2018-07-31", DatastoreCollection())
    logged_enough = stats_processing.is_athlete_two_weeks_from_onboarding()
    assert False is logged_enough


def test_athlete_is_onboarded_twoweeks():

    plans_1_7_days = get_daily_plans(datetime(2018, 7, 24, 0, 0, 0), datetime(2018, 7, 30, 0, 0, 0))
    plans_8_14_days = get_daily_plans(datetime(2018, 7, 17, 0, 0, 0), datetime(2018, 7, 23, 0, 0, 0))

    surveys = get_daily_readiness_surveys(datetime(2018, 7, 17, 12, 0, 0), datetime(2018, 7, 31, 0, 0, 0))

    all_plans = []
    all_plans.extend(plans_8_14_days)
    all_plans.extend(plans_1_7_days)

    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(all_plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats_processing = StatsProcessing("tester", "2018-07-31", datastore_collection)
    stats_processing.process_athlete_stats()
    logged_enough = stats_processing.is_athlete_two_weeks_from_onboarding()
    assert True is logged_enough


def test_athlete_completed_yesterday():

    plans_1_7_days = get_daily_plans(datetime(2018, 7, 24, 0, 0, 0), datetime(2018, 7, 30, 0, 0, 0))
    plans_1_7_days[6].functional_strength_completed = True

    all_plans = []
    all_plans.extend(plans_1_7_days)

    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(all_plans)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore

    stats_processing = StatsProcessing("tester", "2018-07-31", datastore_collection)
    stats_processing.process_athlete_stats()
    completed_yesterday = stats_processing.functional_strength_yesterday()
    assert False is completed_yesterday


def test_athlete_not_completed_yesterday():

    plans_1_7_days = get_daily_plans(datetime(2018, 7, 24, 0, 0, 0), datetime(2018, 7, 30, 0, 0, 0))
    plans_1_7_days[6].functional_strength_completed = False

    all_plans = []
    all_plans.extend(plans_1_7_days)

    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(all_plans)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore

    stats_processing = StatsProcessing("tester", "2018-07-31", datastore_collection)
    stats_processing.process_athlete_stats()
    completed_yesterday = stats_processing.functional_strength_yesterday()
    assert False is completed_yesterday


def test_athlete_no_ap_ar():

    plans_1_7_days = get_daily_plans(datetime(2018, 7, 24, 0, 0, 0), datetime(2018, 7, 30, 0, 0, 0))
    plans_8_14_days = get_daily_plans(datetime(2018, 7, 17, 0, 0, 0), datetime(2018, 7, 23, 0, 0, 0))

    surveys = get_daily_readiness_surveys(datetime(2018, 7, 17, 12, 0, 0), datetime(2018, 7, 31, 0, 0, 0))

    all_plans = []
    all_plans.extend(plans_8_14_days)
    all_plans.extend(plans_1_7_days)

    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(all_plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats_processing = StatsProcessing("tester", "2018-07-31", datastore_collection)
    stats_processing.process_athlete_stats()
    logged_enough = stats_processing.athlete_has_enough_active_prep_recovery_sessions()
    assert False is logged_enough


def test_athlete_enough_ap_ar():

    plans_1_7_days = get_daily_plans(datetime(2018, 7, 24, 0, 0, 0), datetime(2018, 7, 30, 0, 0, 0))
    plans_8_14_days = get_daily_plans(datetime(2018, 7, 17, 0, 0, 0), datetime(2018, 7, 23, 0, 0, 0))

    plans_1_7_days[0].post_recovery_completed = True
    plans_1_7_days[0].pre_recovery_completed = True

    plans_8_14_days[0].post_recovery_completed = True
    plans_8_14_days[0].pre_recovery_completed = True

    surveys = get_daily_readiness_surveys(datetime(2018, 7, 17, 12, 0, 0), datetime(2018, 7, 31, 0, 0, 0))

    all_plans = []
    all_plans.extend(plans_8_14_days)
    all_plans.extend(plans_1_7_days)

    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(all_plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats_processing = StatsProcessing("tester", "2018-07-31", datastore_collection)
    stats_processing.process_athlete_stats()
    logged_enough = stats_processing.athlete_has_enough_active_prep_recovery_sessions()
    assert True is logged_enough


def test_no_fs_with_high_readiness_soreness():
    daily_plan = get_daily_plans(datetime(2018, 7, 24, 0, 0, 0), datetime(2018, 7, 25, 0, 0, 0))[0]
    daily_plan.functional_strength_session = FunctionalStrengthSession()
    survey = get_daily_readiness_survey_high_soreness(datetime(2018, 7, 24, 12, 0, 0), 4)
    athlete_stats = AthleteStats("tester")

    daily_plan_datastore = DailyPlanDatastore()
    athlete_stats_datastore = AthleteStatsDatastore()
    daily_plan_datastore.side_load_plans([daily_plan])
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys([survey])
    athlete_stats_datastore.side_load_athlete_stats(athlete_stats)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore
    datastore_collection.exercise_datastore = exercise_library_datastore

    tpm = TrainingPlanManager("tester", datastore_collection)
    plan = tpm.create_daily_plan("2018-07-24")
    assert(None is plan.functional_strength_session)


def test_no_fs_with_high_post_session_soreness():
    daily_plan = get_daily_plans(datetime(2018, 7, 24, 0, 0, 0), datetime(2018, 7, 25, 0, 0, 0))[0]
    daily_plan.functional_strength_session = FunctionalStrengthSession()
    survey = get_daily_readiness_survey_high_soreness(datetime(2018, 7, 24, 12, 0, 0), 1)

    athlete_stats = AthleteStats("tester")

    daily_plan_datastore = DailyPlanDatastore()
    athlete_stats_datastore = AthleteStatsDatastore()
    daily_plan_datastore.side_load_plans([daily_plan])
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys([survey])
    post_session_datastore = PostSessionSurveyDatastore()
    athlete_stats_datastore.side_load_athlete_stats(athlete_stats)
    soreness_list = [TestUtilities().body_part_soreness(12, 4)]
    post_survey = TestUtilities().get_post_survey(4, soreness_list)
    post_session_survey = \
        PostSessionSurvey(datetime(2018, 7, 24, 17, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", None,
                          1, post_survey)

    post_session_datastore.side_load_surveys([post_session_survey])

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore
    datastore_collection.post_session_survey_datastore = post_session_datastore
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore
    datastore_collection.exercise_datastore = exercise_library_datastore
    tpm = TrainingPlanManager("tester", datastore_collection)
    plan = tpm.create_daily_plan("2018-07-24")
    assert(None is plan.functional_strength_session)