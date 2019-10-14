from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from models.session import SportTrainingSession
from datetime import datetime, timedelta
from models.sport import SportName
from models.functional_movement import ActivityFunctionalMovementFactory, FunctionalMovementFactory, BodyPartFunctionalMovement, SessionFunctionalMovement
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation, BodyPartSide
from logic.injury_risk_processing import InjuryRiskProcessor



def get_sessions(dates, rpes, durations, sport_names):

    if len(dates) != len(rpes) != len(durations) != len(sport_names):
        raise Exception("dates, rpes, durations must match in length")

    sessions = []

    for d in range(0, len(dates)):
        session = SportTrainingSession()
        session.event_date = dates[d]
        session.session_RPE = rpes[d]
        session.duration_minutes = durations[d]
        session.sport_name = sport_names[d]
        sessions.append(session)

    return sessions


def test_body_parts_have_volume():

    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    s = sessions[0]
    session_functional_movement = SessionFunctionalMovement(s, {})
    session_functional_movement.process(s.event_date)

    assert len(session_functional_movement.body_parts) > 0
    for b in session_functional_movement.body_parts:
        assert b.concentric_volume > 0 or b.eccentric_volume > 0


def test_body_parts_have_intensity():

    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    s = sessions[0]
    session_functional_movement = SessionFunctionalMovement(s, {})
    session_functional_movement.process(s.event_date)

    assert len(session_functional_movement.body_parts) > 0
    for b in session_functional_movement.body_parts:
        assert b.concentric_intensity > 0 or b.eccentric_intensity > 0


def test_sharp_symptom():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(3), None)
    soreness.side = 1
    soreness.sharp = 3
    soreness.reported_date_time = now_date

    # this needs muscle groups

    proc = InjuryRiskProcessor(now_date, [soreness], [], {})
    proc.process()
    j=0


def test_inflammation_affects_load():
    now_date = datetime.now()

    soreness = Soreness()
    # TODO why doesn't a sore knee make load increase?
    #soreness.body_part = BodyPart(BodyPartLocation(7), None)
    soreness.body_part = BodyPart(BodyPartLocation(55), None)
    soreness.side = 1
    soreness.sharp = 3
    soreness.reported_date_time = now_date

    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    # running this with and without the symptoms

    sessions = get_sessions(dates, rpes, durations, sport_names)

    session_functional_movement = SessionFunctionalMovement(sessions[0], {})
    session_functional_movement.process(sessions[0].event_date)

    proc = InjuryRiskProcessor(now_date, [soreness], sessions, {})
    proc.process()

    # this is a section to better understand changes in volume
    for j in proc.injury_risk_dict.keys():
        matching_parts = [b for b in session_functional_movement.body_parts if b.body_part_side == j]
        if len(matching_parts) > 0:
            if proc.injury_risk_dict[j].concentric_volume_today != matching_parts[0].concentric_volume:
                k=0
            if proc.injury_risk_dict[j].eccentric_volume_today != matching_parts[0].eccentric_volume:
                k=0

    vastus_lateralis_1 = BodyPartSide(BodyPartLocation(55), 1)
    vastus_lateralis_2 = BodyPartSide(BodyPartLocation(55), 2)
    vastus_medialis_1 = BodyPartSide(BodyPartLocation(56), 1)
    vastus_medialis_2 = BodyPartSide(BodyPartLocation(56), 2)
    vastus_intermedius_1 = BodyPartSide(BodyPartLocation(57), 1)
    vastus_intermedius_2 = BodyPartSide(BodyPartLocation(57), 2)
    rectus_femoris_1 = BodyPartSide(BodyPartLocation(58), 1)
    rectus_femoris_2 = BodyPartSide(BodyPartLocation(58), 2)

    assert proc.injury_risk_dict[vastus_lateralis_1].concentric_volume_today == 80  # affected body part
    assert proc.injury_risk_dict[vastus_lateralis_2].concentric_volume_today == 100  # was 80
    assert proc.injury_risk_dict[vastus_medialis_1].concentric_volume_today == 100  # was 80
    assert proc.injury_risk_dict[vastus_medialis_2].concentric_volume_today == 100  # was 80
    assert proc.injury_risk_dict[vastus_intermedius_1].concentric_volume_today == 100  # was 80
    assert proc.injury_risk_dict[vastus_intermedius_2].concentric_volume_today == 100  # was 80
    assert proc.injury_risk_dict[rectus_femoris_1].concentric_volume_today == 260  # was 240
    assert proc.injury_risk_dict[rectus_femoris_2].concentric_volume_today == 260  # was 240

    b=0



