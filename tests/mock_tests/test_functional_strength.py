import pytest
from logic.functional_strength_mapping import FSProgramGenerator
from models.sport import SportName, SoccerPosition
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore

exercise_library_datastore = ExerciseLibraryDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv(library_file='database/FS_Exercise_Library.csv',
                                                                desc_file='database/FS_Exercise_Descriptions.tsv')


def test_generate_session_for_soccer():
    mapping = FSProgramGenerator(exercise_library_datastore)
    fs_session = mapping.getFunctionalStrengthForSportPosition(SportName.soccer, position=SoccerPosition.Forward)
    assert True is (len(fs_session.warm_up) > 0)
