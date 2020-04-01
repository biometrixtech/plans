import pytest
from datetime import datetime, timedelta
from utils import format_datetime, parse_datetime
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus
from models.body_parts import BodyPart, BodyPartLocation, BodyPartFactory
#from models.historic_soreness import HistoricSoreness
from models.functional_movement_modalities import MovementIntegrationPrepModality
from logic.injury_risk_processing import InjuryRiskProcessor
from models.stats import AthleteStats
from models.exercise_phase import ExercisePhaseType
#from models.trigger import Trigger, TriggerType
#from logic.trigger_processing import TriggerFactory
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from models.body_part_injury_risk import BodyPartInjuryRisk
from models.functional_movement import BodyPartFunction

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()

body_parts_1 = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()

# post active rest


def test_movement_prep_check_care_severity_3():

    now_date = datetime.now()
    max_severity = 3

    for b in body_parts_1:

        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.side = 1
        soreness.sharp = max_severity
        soreness.reported_date_time = now_date
        exercise_library = exercise_library_datastore.get()

        proc = InjuryRiskProcessor(now_date, [soreness], [], {}, AthleteStats("tester"), "tester")
        injury_risk_dict = proc.process(aggregate_results=True)
        consolidated_injury_risk_dict = proc.get_consolidated_dict()

        for body_part, body_part_injury_risk in consolidated_injury_risk_dict.items():

            if (body_part_injury_risk.last_muscle_spasm_date is not None and
                    body_part_injury_risk.last_muscle_spasm_date == datetime.today().date()):
                muscle_spasm = True
            else:
                muscle_spasm = False

            if (body_part_injury_risk.last_knots_date is not None and
                    body_part_injury_risk.last_knots_date == datetime.today().date()):
                knots = True
            else:
                knots = False

            movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
            movement_prep.check_care(body_part, body_part_injury_risk, exercise_library, max_severity)

            assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
            assert len(movement_prep.exercise_phases[0].exercises) > 0

            assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

            if muscle_spasm or knots:
                assert len(movement_prep.exercise_phases[1].exercises) > 0
            else:
                assert len(movement_prep.exercise_phases[1].exercises) == 0

            # should be either active or dynamic stretch but not both
            assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
            assert len(movement_prep.exercise_phases[2].exercises) > 0
            assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
            assert len(movement_prep.exercise_phases[3].exercises) == 0

            assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
            assert len(movement_prep.exercise_phases[4].exercises) == 0
            assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
            assert len(movement_prep.exercise_phases[5].exercises) == 0
            assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
            assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_care_severity_7():

    now_date = datetime.now()
    max_severity = 7

    for b in body_parts_1:

        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.side = 1
        soreness.sharp = max_severity
        soreness.reported_date_time = now_date
        exercise_library = exercise_library_datastore.get()

        proc = InjuryRiskProcessor(now_date, [soreness], [], {}, AthleteStats("tester"), "tester")
        injury_risk_dict = proc.process(aggregate_results=True)
        consolidated_injury_risk_dict = proc.get_consolidated_dict()

        for body_part, body_part_injury_risk in consolidated_injury_risk_dict.items():

            if (body_part_injury_risk.last_muscle_spasm_date is not None and
                    body_part_injury_risk.last_muscle_spasm_date == datetime.today().date()):
                muscle_spasm = True
            else:
                muscle_spasm = False

            if (body_part_injury_risk.last_knots_date is not None and
                    body_part_injury_risk.last_knots_date == datetime.today().date()):
                knots = True
            else:
                knots = False

            movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
            movement_prep.check_care(body_part, body_part_injury_risk, exercise_library, max_severity)

            assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
            assert len(movement_prep.exercise_phases[0].exercises) > 0

            assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

            # shouldn't have any difference in this case
            if muscle_spasm or knots:
                assert len(movement_prep.exercise_phases[1].exercises) == 0
            else:
                assert len(movement_prep.exercise_phases[1].exercises) == 0

            # should be either active or dynamic stretch but not both
            assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
            assert len(movement_prep.exercise_phases[2].exercises) == 0
            assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
            assert len(movement_prep.exercise_phases[3].exercises) == 0

            assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
            assert len(movement_prep.exercise_phases[4].exercises) == 0
            assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
            assert len(movement_prep.exercise_phases[5].exercises) == 0
            assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
            assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_overactive_short():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.overactive_short_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:

        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) > 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_overactive_short_severity_7():

    exercise_library = exercise_library_datastore.get()
    max_severity = 7
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.overactive_short_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:

        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_overactive_long():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.overactive_long_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:

        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_underactive_short_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.underactive_short_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) > 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) > 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) > 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_underactive_short_severity_5():

    exercise_library = exercise_library_datastore.get()
    max_severity = 5
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.underactive_short_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) > 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) > 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_underactive_short_severity_7():

    exercise_library = exercise_library_datastore.get()
    max_severity = 7
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.underactive_short_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_underactive_long_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.underactive_long_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) == 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) > 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_underactive_long_severity_7():

    exercise_library = exercise_library_datastore.get()
    max_severity = 7
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.underactive_long_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) == 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_weak():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.weak_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) == 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) > 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_prevention_weak_severity_5():

    exercise_library = exercise_library_datastore.get()
    max_severity = 5
    body_part_factory = BodyPartFactory()

    body_part_injury_risk_1 = BodyPartInjuryRisk()
    body_part_injury_risk_1.weak_count_last_0_20_days = 3

    body_part_injury_risk_list = [
        body_part_injury_risk_1
    ]

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for b in body_part_injury_risk_list:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        movement_prep.check_prevention(body_part, b, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) == 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_recovery_volume_tier_1_3_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    volume_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for v in volume_tiers:

        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        body_part_injury_risk_1.total_volume_percent_tier = v
        movement_prep.check_recovery(body_part, body_part_injury_risk_1, exercise_library, max_severity, sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) > 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) > 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_movement_prep_check_recovery_volume_tiers_0_6_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    volume_tiers = [0, 6]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for v in volume_tiers:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        body_part_injury_risk_1.total_volume_percent_tier = v
        movement_prep.check_recovery(body_part, body_part_injury_risk_1, exercise_library, max_severity,
                                     sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) == 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_active_rest_check_recovery_volume_tier_1_3_severity_5():

    exercise_library = exercise_library_datastore.get()
    max_severity = 5
    body_part_factory = BodyPartFactory()

    volume_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for v in volume_tiers:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        body_part_injury_risk_1.total_volume_percent_tier = v
        movement_prep.check_recovery(body_part, body_part_injury_risk_1, exercise_library, max_severity,
                                     sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) > 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_active_rest_check_recovery_volume_tier_1_3_severity_7():

    exercise_library = exercise_library_datastore.get()
    max_severity = 7
    body_part_factory = BodyPartFactory()

    volume_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for v in volume_tiers:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        body_part_injury_risk_1.total_volume_percent_tier = v
        movement_prep.check_recovery(body_part, body_part_injury_risk_1, exercise_library, max_severity,
                                     sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_active_rest_check_recovery_compensation_tier_1_3_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    comp_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for v in comp_tiers:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        body_part_injury_risk_1.total_compensation_percent_tier = v
        body_part_injury_risk_1.last_compensation_date = datetime.today().date()
        movement_prep.check_recovery(body_part, body_part_injury_risk_1, exercise_library, max_severity,
                                     sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) > 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_active_rest_check_recovery_compensation_tiers_0_6_severity_3():

    exercise_library = exercise_library_datastore.get()
    max_severity = 3
    body_part_factory = BodyPartFactory()

    comp_tiers = [0, 6]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for v in comp_tiers:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        body_part_injury_risk_1.total_compensation_percent_tier = v
        body_part_injury_risk_1.last_compensation_date = datetime.today().date()
        movement_prep.check_recovery(body_part, body_part_injury_risk_1, exercise_library, max_severity,
                                     sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) == 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0


def test_active_rest_check_recovery_compensation_tier_1_3_severity_7():

    exercise_library = exercise_library_datastore.get()
    max_severity = 7
    body_part_factory = BodyPartFactory()

    comp_tiers = [1, 2, 3]

    body_part_injury_risk_1 = BodyPartInjuryRisk()

    body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.quads, None))

    sport_body_parts = {}
    sport_body_parts[BodyPartLocation.quads] = BodyPartFunction.prime_mover

    for v in comp_tiers:
        movement_prep = MovementIntegrationPrepModality(event_date_time=datetime.today())
        body_part_injury_risk_1.total_compensation_percent_tier = v
        body_part_injury_risk_1.last_compensation_date = datetime.today().date()
        movement_prep.check_recovery(body_part, body_part_injury_risk_1, exercise_library, max_severity,
                                     sport_body_parts)

        assert movement_prep.exercise_phases[0].type == ExercisePhaseType.inhibit
        assert len(movement_prep.exercise_phases[0].exercises) > 0

        assert movement_prep.exercise_phases[1].type == ExercisePhaseType.static_stretch

        assert len(movement_prep.exercise_phases[1].exercises) == 0

        # should be either active or dynamic stretch but not both
        assert movement_prep.exercise_phases[2].type == ExercisePhaseType.active_stretch
        assert len(movement_prep.exercise_phases[2].exercises) == 0
        assert movement_prep.exercise_phases[3].type == ExercisePhaseType.dynamic_stretch
        assert len(movement_prep.exercise_phases[3].exercises) == 0

        assert movement_prep.exercise_phases[4].type == ExercisePhaseType.isolated_activate
        assert len(movement_prep.exercise_phases[4].exercises) == 0
        assert movement_prep.exercise_phases[5].type == ExercisePhaseType.static_integrate
        assert len(movement_prep.exercise_phases[5].exercises) == 0
        assert movement_prep.exercise_phases[6].type == ExercisePhaseType.dynamic_integrate
        assert len(movement_prep.exercise_phases[6].exercises) == 0
