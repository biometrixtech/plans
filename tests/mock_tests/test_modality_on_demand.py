import datetime
import pytest

from logic.training_plan_management import TrainingPlanManager
from models.stats import AthleteStats
from models.functional_movement_modalities import ModalityType
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()
data_store_collection = DatastoreCollection()


@pytest.fixture(scope="session", autouse=True)
def setup_local():
    exercise_library_datastore.side_load_exericse_list_from_csv()
    data_store_collection.exercise_datastore = exercise_library_datastore


def test_get_active_rest():
    user_id = 'on_demand_modality_test'
    event_date = datetime.datetime.now()
    athlete_stats = AthleteStats(user_id)
    athlete_stats.event_date = event_date
    plan_manager = TrainingPlanManager(user_id, data_store_collection)
    plan = plan_manager.add_modality(event_date, modality_type=1, athlete_stats=athlete_stats)
    assert plan.modalities[0].type == ModalityType.post_active_rest


def test_get_movement_prep():
    user_id = 'on_demand_modality_test'
    event_date = datetime.datetime.now()
    athlete_stats = AthleteStats(user_id)
    athlete_stats.event_date = event_date
    plan_manager = TrainingPlanManager(user_id, data_store_collection)
    plan = plan_manager.add_modality(event_date, modality_type=5, athlete_stats=athlete_stats)
    assert plan.modalities[0].type == ModalityType.movement_integration_prep
