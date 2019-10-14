import pytest
import logic.soreness_processing as soreness_and_injury
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation
from models.daily_readiness import DailyReadiness
from models.post_session_survey import PostSessionSurvey, PostSurvey
from tests.testing_utilities import TestUtilities
import datetime


# 1 body part


@pytest.fixture(scope="module")
def trigger_date_time():
    return datetime.datetime(2018, 6, 27, 14, 30, 0)


@pytest.fixture(scope="module")
def soreness_calculator():
    soreness_calc = soreness_and_injury.SorenessCalculator()
    return soreness_calc


@pytest.fixture(scope="module")
def get_readiness_survey(body_part_location, severity_score=None, movement=None, pain=False, tight=None, knots=None, ache=None, sharp=None):
    if severity_score is not None:
        if not pain:
            soreness_item = TestUtilities().body_part_soreness(body_part_location, severity_score, movement=movement)
        else:
            soreness_item = TestUtilities().body_part_pain(body_part_location, severity_score, movement=movement)
    else:
        soreness_item = TestUtilities().body_part_symptoms(body_part_location, tight=tight, knots=knots, ache=ache, sharp=sharp)

    survey = DailyReadiness(datetime.datetime(2018, 6, 27, 14, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "tester", [soreness_item], 5, 5)

    return survey


def test_muscle_soreness_severity_to_ache():
    readiness_survey = get_readiness_survey(2, 3, 5)
    assert len(readiness_survey.soreness) == 1
    soreness = readiness_survey.soreness[0]
    assert soreness.severity == 3
    assert soreness.movement == 5
    assert soreness.ache == 5
    assert soreness.sharp is None
    assert soreness.tight == 7
    assert soreness.knots == 7


def test_muscle_pain_severity_to_sharp():
    readiness_survey = get_readiness_survey(2, 3, 5, True)
    assert len(readiness_survey.soreness) == 1
    soreness = readiness_survey.soreness[0]
    assert soreness.severity == 3
    assert soreness.movement == 5
    assert soreness.ache is None
    assert soreness.sharp == 4
    assert soreness.tight == 7
    assert soreness.knots == 7


def test_joint_pain_severity_to_sharp_movement_to_tight():
    readiness_survey = get_readiness_survey(20, 3, 5, True)
    assert len(readiness_survey.soreness) == 1
    soreness = readiness_survey.soreness[0]
    assert soreness.severity == 3
    assert soreness.movement == 5
    assert soreness.ache is None
    assert soreness.sharp == 4
    assert soreness.tight == 7
    assert soreness.knots is None


def test_joint_pain_severity_to_sharp_no_movement():
    readiness_survey = get_readiness_survey(20, 3, None, True)
    assert len(readiness_survey.soreness) == 1
    soreness = readiness_survey.soreness[0]
    assert soreness.pain
    assert soreness.severity == 3
    assert soreness.ache is None
    assert soreness.sharp == 4


def test_joint_ache_to_pain():
    readiness_survey = get_readiness_survey(20, ache=5)
    assert len(readiness_survey.soreness) == 1
    soreness = readiness_survey.soreness[0]
    assert soreness.pain
    assert soreness.severity == 4
    assert soreness.movement is None

def test_joint_ache_sharp_to_pain():
    readiness_survey = get_readiness_survey(20, ache=5, sharp=3)
    assert len(readiness_survey.soreness) == 1
    soreness = readiness_survey.soreness[0]
    assert soreness.pain
    assert soreness.severity == 4
    assert soreness.movement is None


def test_muscle_ache_sharp_to_pain():
    readiness_survey = get_readiness_survey(2, ache=5, sharp=10)
    assert len(readiness_survey.soreness) == 1
    soreness = readiness_survey.soreness[0]
    assert soreness.pain
    assert soreness.severity == 5
    assert soreness.movement is None


def test_severity_update():
    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(2), None)
    soreness.side = 2
    soreness.ache = 2  # severity is 1
    assert soreness.severity == 1
    assert not soreness.pain

    soreness.sharp = 3  # severity is 2
    assert soreness.severity == 2
    assert soreness.pain

    soreness.ache = 3  # severity is 1
    assert soreness.severity == 2
    assert soreness.pain


