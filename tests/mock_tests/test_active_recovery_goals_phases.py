import pytest
from datetime import datetime, timedelta
from utils import format_datetime, parse_datetime
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus
from models.body_parts import BodyPart, BodyPartLocation, BodyPartFactory
#from models.historic_soreness import HistoricSoreness
from models.functional_movement_modalities import ActiveRecovery
from logic.injury_risk_processing import InjuryRiskProcessor
from models.stats import AthleteStats
from models.exercise_phase import ExercisePhaseType
#from models.trigger import Trigger, TriggerType
#from logic.trigger_processing import TriggerFactory
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from models.body_part_injury_risk import BodyPartInjuryRisk

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()

# post active rest


def test_active_recovery_check_recovery_volume_tier_1_3_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    volume_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    for v in volume_tiers:

        active_recovery = ActiveRecovery(event_date_time=datetime.today())
        body_part_injury_risk_1.total_volume_percent_tier = v
        body_part_injury_risk_1.last_sharp_level = max_severity
        body_part_injury_risk_1.last_sharp_date = datetime.today().date()
        injury_risk_dict = {}
        injury_risk_dict[body_part] = body_part_injury_risk_1
        active_recovery.fill_exercises(exercise_library, injury_risk_dict, sport_body_parts=[],
                                       high_intensity_session=True)

        assert active_recovery.exercise_phases[0].type == ExercisePhaseType.dynamic_integrate
        assert len(active_recovery.exercise_phases[0].exercises) == 2


def test_active_recovery_check_recovery_volume_tier_1_3_severity_3_no_high_intensity():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    volume_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    for v in volume_tiers:

        active_recovery = ActiveRecovery(event_date_time=datetime.today())
        body_part_injury_risk_1.total_volume_percent_tier = v
        body_part_injury_risk_1.last_sharp_level = max_severity
        body_part_injury_risk_1.last_sharp_date = datetime.today().date()
        injury_risk_dict = {}
        injury_risk_dict[body_part] = body_part_injury_risk_1
        active_recovery.fill_exercises(exercise_library, injury_risk_dict, sport_body_parts=[],
                                       high_intensity_session=False)

        assert len(active_recovery.exercise_phases) == 0


def test_active_recovery_check_recovery_volume_tiers_0_4_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    volume_tiers = [0, 4]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    for v in volume_tiers:

        active_recovery = ActiveRecovery(event_date_time=datetime.today())
        body_part_injury_risk_1.total_volume_percent_tier = v
        body_part_injury_risk_1.last_sharp_level = max_severity
        body_part_injury_risk_1.last_sharp_date = datetime.today().date()
        injury_risk_dict = {}
        injury_risk_dict[body_part] = body_part_injury_risk_1
        active_recovery.fill_exercises(exercise_library, injury_risk_dict, sport_body_parts=[],
                                       high_intensity_session=True)

        assert len(active_recovery.exercise_phases) == 0


def test_active_recovery_check_recovery_volume_tier_1_3_severity_4():

    exercise_library = exercise_library_datastore.get()
    max_severity = 4
    body_part_factory = BodyPartFactory()

    volume_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    for v in volume_tiers:

        active_recovery = ActiveRecovery(event_date_time=datetime.today())
        body_part_injury_risk_1.total_volume_percent_tier = v
        body_part_injury_risk_1.last_sharp_level = max_severity
        body_part_injury_risk_1.last_sharp_date = datetime.today().date()
        injury_risk_dict = {}
        injury_risk_dict[body_part] = body_part_injury_risk_1
        active_recovery.fill_exercises(exercise_library, injury_risk_dict, sport_body_parts=[],
                                       high_intensity_session=True)

        assert len(active_recovery.exercise_phases) == 0


def test_active_recovery_check_recovery_compensation_tier_1_3_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    comp_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    for v in comp_tiers:

        active_recovery = ActiveRecovery(event_date_time=datetime.today())
        body_part_injury_risk_1.total_compensation_percent_tier = v
        body_part_injury_risk_1.last_compensation_date = datetime.today().date()
        body_part_injury_risk_1.last_sharp_level = max_severity
        body_part_injury_risk_1.last_sharp_date = datetime.today().date()
        injury_risk_dict = {}
        injury_risk_dict[body_part] = body_part_injury_risk_1
        active_recovery.fill_exercises(exercise_library, injury_risk_dict, sport_body_parts=[],
                                       high_intensity_session=True)

        assert active_recovery.exercise_phases[0].type == ExercisePhaseType.dynamic_integrate
        assert len(active_recovery.exercise_phases[0].exercises) == 2


def test_active_recovery_check_recovery_compensation_tier_1_3_severity_4():

    exercise_library = exercise_library_datastore.get()
    max_severity = 4
    body_part_factory = BodyPartFactory()

    comp_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    for v in comp_tiers:

        active_recovery = ActiveRecovery(event_date_time=datetime.today())
        body_part_injury_risk_1.total_compensation_percent_tier = v
        body_part_injury_risk_1.last_compensation_date = datetime.today().date()
        body_part_injury_risk_1.last_sharp_level = max_severity
        body_part_injury_risk_1.last_sharp_date = datetime.today().date()
        injury_risk_dict = {}
        injury_risk_dict[body_part] = body_part_injury_risk_1
        active_recovery.fill_exercises(exercise_library, injury_risk_dict, sport_body_parts=[],
                                       high_intensity_session=True)

        assert len(active_recovery.exercise_phases) == 0


def test_active_recovery_check_recovery_compensation_tier_1_3_severity_3_no_high_intensity():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    comp_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    for v in comp_tiers:

        active_recovery = ActiveRecovery(event_date_time=datetime.today())
        body_part_injury_risk_1.total_compensation_percent_tier = v
        body_part_injury_risk_1.last_compensation_date = datetime.today().date()
        body_part_injury_risk_1.last_sharp_level = max_severity
        body_part_injury_risk_1.last_sharp_date = datetime.today().date()
        injury_risk_dict = {}
        injury_risk_dict[body_part] = body_part_injury_risk_1
        active_recovery.fill_exercises(exercise_library, injury_risk_dict, sport_body_parts=[],
                                       high_intensity_session=False)

        assert len(active_recovery.exercise_phases) == 0


def test_active_recovery_check_recovery_compensation_tiers_0_4_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    comp_tiers = [0, 4]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    for v in comp_tiers:
        active_recovery = ActiveRecovery(event_date_time=datetime.today())
        body_part_injury_risk_1.total_compensation_percent_tier = v
        body_part_injury_risk_1.last_compensation_date = datetime.today().date()
        body_part_injury_risk_1.last_sharp_level = max_severity
        body_part_injury_risk_1.last_sharp_date = datetime.today().date()
        injury_risk_dict = {}
        injury_risk_dict[body_part] = body_part_injury_risk_1
        active_recovery.fill_exercises(exercise_library, injury_risk_dict, sport_body_parts=[],
                                       high_intensity_session=True)

        assert len(active_recovery.exercise_phases) == 0
