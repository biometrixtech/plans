import pytest
from logic.training_plan_management import TrainingPlanManager
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection
from models.stats import AthleteStats
from datetime import datetime, timedelta, date, time
from utils import format_datetime, format_date
from tests.testing_utilities import TestUtilities
from models.daily_readiness import DailyReadiness
from models.daily_plan import DailyPlan
from models.soreness_base import BodyPartLocation
from models.functional_movement_modalities import ModalityType
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def create_plan(body_part_list, severity_list, side_list, pain_list, train_later=True):

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
    daily_plan.train_later = train_later
    daily_plan_datastore.side_load_plans([daily_plan])
    data_store_collection = DatastoreCollection()
    data_store_collection.daily_plan_datastore = daily_plan_datastore
    data_store_collection.exercise_datastore = exercise_library_datastore

    athlete_stats = AthleteStats(user_id)

    mgr = TrainingPlanManager(user_id, data_store_collection)

    daily_plan = mgr.create_daily_plan(format_date(current_date), format_datetime(current_date_time), athlete_stats=athlete_stats)

    return daily_plan


def create_no_soreness_plan():
    user_id = "tester"

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    # daily_readiness_datastore = DailyReadinessDatastore()
    daily_plan_datastore = DailyPlanDatastore()
    athlete_stats_datastore = AthleteStatsDatastore()
    athlete_stats = AthleteStats("tester")

    soreness_list = []

    survey = DailyReadiness(current_date_time.strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 7, 9)
    daily_plan = DailyPlan(format_date(current_date))
    daily_plan.user_id = user_id
    daily_plan.daily_readiness_survey = survey
    daily_plan_datastore.side_load_plans([daily_plan])

    # daily_readiness_datastore.side_load_surveys([survey])
    athlete_stats_datastore.side_load_athlete_stats(athlete_stats)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    # datastore_collection.daily_readiness_datastore = daily_readiness_datastore
    datastore_collection.exercise_datastore = exercise_library_datastore
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    mgr = TrainingPlanManager(user_id, datastore_collection)

    daily_plan = mgr.create_daily_plan(format_date(current_date), last_updated=format_datetime(current_date_time), athlete_stats=AthleteStats(user_id))

    return daily_plan


def test_active_rest_after_training_knee():

    daily_plan = create_plan([14], [], [], [], train_later=False)
    post_active_rest = [m for m in daily_plan.modalities if m.type == ModalityType.post_active_rest][0]
    assert len(post_active_rest.exercise_phases[0].exercises) > 0
    assert len(post_active_rest.exercise_phases[1].exercises) > 0
    assert len(post_active_rest.exercise_phases[2].exercises) == 0
    assert len(post_active_rest.exercise_phases[3].exercises) == 0

    assert daily_plan.cool_down is not None
    assert daily_plan.heat is None
    assert daily_plan.ice is None
    assert len(daily_plan.pre_active_rest) == 0


def test_movement_prep_before_training_knee():

    daily_plan = create_plan([14], [], [], [], train_later=True)
    movement_prep = [m for m in daily_plan.modalities if m.type == ModalityType.movement_integration_prep][0]
    assert len(movement_prep.exercise_phases[0].exercises) > 0
    assert len(movement_prep.exercise_phases[1].exercises) == 0
    assert len(movement_prep.exercise_phases[2].exercises) > 0
    assert len(movement_prep.exercise_phases[3].exercises) == 0
    assert len(movement_prep.exercise_phases[4].exercises) == 0
    assert len(movement_prep.exercise_phases[5].exercises) == 0

    assert daily_plan.cool_down is not None
    assert daily_plan.heat is None
    assert daily_plan.ice is None

