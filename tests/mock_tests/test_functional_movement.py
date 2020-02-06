from models.session import SportTrainingSession
from datetime import datetime, timedelta
from models.sport import SportName
from models.functional_movement import ActivityFunctionalMovementFactory, FunctionalMovementFactory, \
    SessionFunctionalMovement
from models.body_part_injury_risk import BodyPartInjuryRisk
from models.movement_patterns import Elasticity, LeftRightElasticity, MovementPatterns
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation, BodyPartSide
from models.stats import AthleteStats
from models.load_stats import LoadStats
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
    session_functional_movement.process(s.event_date, LoadStats())

    assert len(session_functional_movement.functional_movement_mappings) > 0
    for c in session_functional_movement.functional_movement_mappings:
        for b in c.prime_movers:
            assert b.concentric_volume > 0 or b.eccentric_volume > 0
        for b in c.synergists:
            assert b.concentric_volume > 0 or b.eccentric_volume > 0


# def test_body_parts_overactive():
#
#     dates = [datetime.now()]
#     rpes = [5]
#     durations = [100]
#     sport_names = [SportName.distance_running]
#
#     sessions = get_sessions(dates, rpes, durations, sport_names)
#
#     s = sessions[0]
#     s.movement_patterns = MovementPatterns()
#     s.movement_patterns.apt_ankle_pitch = LeftRightElasticity()
#     s.movement_patterns.apt_ankle_pitch.left = Elasticity()
#     s.movement_patterns.apt_ankle_pitch.left.elasticity = .56
#
#     session_functional_movement = SessionFunctionalMovement(s, {})
#     session_functional_movement.process(s.event_date, LoadStats())
#
#     overactive = [i for i in session_functional_movement.injury_risk_dict.values() if i.last_overactive_date is not None]
#     underactive = [i for i in session_functional_movement.injury_risk_dict.values() if
#                   i.last_underactive_date is not None]
#     inhibited = [i for i in session_functional_movement.injury_risk_dict.values() if
#                   i.last_inhibited_date is not None]
#
#     assert len(overactive) > 0
#     assert len(underactive) > 0
#     assert len(inhibited) > 0
#
#
# def test_body_parts_overactive_weak():
#
#     dates = [datetime.now()]
#     rpes = [5]
#     durations = [100]
#     sport_names = [SportName.distance_running]
#
#     sessions = get_sessions(dates, rpes, durations, sport_names)
#
#     s = sessions[0]
#     s.movement_patterns = MovementPatterns()
#     s.movement_patterns.apt_ankle_pitch = LeftRightElasticity()
#     s.movement_patterns.apt_ankle_pitch.left = Elasticity()
#     s.movement_patterns.apt_ankle_pitch.left.elasticity = .56
#     s.movement_patterns.apt_ankle_pitch.left.y_adf = 3.0
#
#     session_functional_movement = SessionFunctionalMovement(s, {}, "tester")
#     session_functional_movement.process(s.event_date, LoadStats())
#
#     overactive = [i for i in session_functional_movement.injury_risk_dict.values() if i.last_overactive_date is not None]
#     underactive = [i for i in session_functional_movement.injury_risk_dict.values() if
#                   i.last_underactive_date is not None]
#     weak = [i for i in session_functional_movement.injury_risk_dict.values() if
#                   i.last_weak_date is not None]
#
#     assert len(overactive) > 0
#     assert len(underactive) > 0
#     assert len(weak) > 0
#
# def test_body_parts_muscle_imbalance():
#
#     dates = [datetime.now()]
#     rpes = [5]
#     durations = [100]
#     sport_names = [SportName.distance_running]
#
#     sessions = get_sessions(dates, rpes, durations, sport_names)
#
#     s = sessions[0]
#     s.movement_patterns = MovementPatterns()
#     s.movement_patterns.apt_ankle_pitch = LeftRightElasticity()
#     s.movement_patterns.apt_ankle_pitch.left = Elasticity()
#     s.movement_patterns.apt_ankle_pitch.left.elasticity = .56
#     s.movement_patterns.apt_ankle_pitch.left.y_adf = 3.0
#
#     injury_risk_dict = {}
#     body_part_side = BodyPartSide(BodyPartLocation(58), 1)
#     injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
#     injury_risk_dict[body_part_side].last_muscle_spasm_date = datetime.now().date()
#
#     session_functional_movement = SessionFunctionalMovement(s, injury_risk_dict)
#     session_functional_movement.process(s.event_date.date(), LoadStats())
#
#     overactive = [i for i in session_functional_movement.injury_risk_dict.values() if i.last_overactive_date is not None]
#     underactive = [i for i in session_functional_movement.injury_risk_dict.values() if
#                   i.last_underactive_date is not None]
#     weak = [i for i in session_functional_movement.injury_risk_dict.values() if
#                   i.last_weak_date is not None]
#     short = [i for i in session_functional_movement.injury_risk_dict.values() if
#                   i.last_short_date is not None]
#     muscle_imbalance = [i for i in session_functional_movement.injury_risk_dict.values() if
#                   i.last_muscle_imbalance_date is not None]
#
#     assert len(overactive) == 0
#     assert len(underactive) == 0
#     assert len(weak) == 0
#     assert len(short) > 0
#     assert len(muscle_imbalance) > 0



def test_body_parts_have_intensity():

    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    s = sessions[0]
    session_functional_movement = SessionFunctionalMovement(s, {}, )
    session_functional_movement.process(s.event_date.date(), LoadStats())

    assert len(session_functional_movement.functional_movement_mappings) > 0
    for c in session_functional_movement.functional_movement_mappings:
        for b in c.prime_movers:
            assert b.concentric_intensity > 0 or b.eccentric_intensity > 0
        for b in c.synergists:
            assert b.concentric_intensity > 0 or b.eccentric_intensity > 0


def test_sharp_symptom_inflammation():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(48), None)
    soreness.side = 1
    soreness.sharp = 3
    soreness.reported_date_time = now_date

    proc = InjuryRiskProcessor(now_date, [soreness], [], {},  AthleteStats("Tester"), "tester")

    injury_risk_dict = proc.process()

    body_part_side = BodyPartSide(BodyPartLocation(48), 1)

    assert injury_risk_dict[body_part_side].last_inflammation_date == now_date.date()
    assert injury_risk_dict[body_part_side].last_inhibited_date == now_date.date()


def test_ache_symptom_inflammation():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(48), None)
    soreness.side = 1
    soreness.ache = 1
    soreness.reported_date_time = now_date

    proc = InjuryRiskProcessor(now_date, [soreness], [], {}, AthleteStats("Tester"), "tester")
    injury_risk_dict = proc.process()

    body_part_side = BodyPartSide(BodyPartLocation(48), 1)

    assert injury_risk_dict[body_part_side].last_inflammation_date == now_date.date()
    assert injury_risk_dict[body_part_side].last_inhibited_date == now_date.date()


def test_tight_symptom_muscle_spasn():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(48), None)
    soreness.side = 1
    soreness.tight = 1
    soreness.reported_date_time = now_date

    proc = InjuryRiskProcessor(now_date, [soreness], [], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process()

    body_part_side = BodyPartSide(BodyPartLocation(48), 1)

    assert injury_risk_dict[body_part_side].last_muscle_spasm_date == now_date.date()
    assert injury_risk_dict[body_part_side].last_inhibited_date is None
    assert injury_risk_dict[body_part_side].last_inflammation_date is None

def test_muscle_deconstruction():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.tight = 1
    soreness.reported_date_time = now_date

    soreness_2 = Soreness()
    soreness_2.body_part = BodyPart(BodyPartLocation(7), None)
    soreness_2.side = 1
    soreness_2.sharp = 2
    soreness_2.reported_date_time = now_date

    proc = InjuryRiskProcessor(now_date, [soreness, soreness_2], [], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process()
    body_parts = list(injury_risk_dict.keys())
    assert len(injury_risk_dict) == 9

def test_muscle_deconstruction_reconstruction():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.tight = 1
    soreness.reported_date_time = now_date

    soreness_2 = Soreness()
    soreness_2.body_part = BodyPart(BodyPartLocation(7), None)
    soreness_2.side = 1
    soreness_2.sharp = 2
    soreness_2.reported_date_time = now_date

    proc = InjuryRiskProcessor(now_date, [soreness, soreness_2], [], {}, AthleteStats("Tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    body_parts = list(injury_risk_dict.keys())
    assert len(injury_risk_dict) == 3

# def test_inflammation_affects_load():
#     now_date = datetime.now()
#
#     soreness = Soreness()
#     #soreness.body_part = BodyPart(BodyPartLocation(7), None)
#     soreness.body_part = BodyPart(BodyPartLocation(55), None)
#     soreness.side = 1
#     soreness.sharp = 3
#     soreness.reported_date_time = now_date
#
#     dates = [datetime.now()]
#     rpes = [5]
#     durations = [100]
#     sport_names = [SportName.distance_running]
#
#     sessions = get_sessions(dates, rpes, durations, sport_names)
#
#     # running this with and without the symptoms
#     session_functional_movement = SessionFunctionalMovement(sessions[0], {})
#     session_functional_movement.process(sessions[0].event_date, LoadStats())
#
#     proc = InjuryRiskProcessor(now_date, [soreness], sessions, {}, AthleteStats("Tester"), "tester")
#     proc.process()
#
#     # this is a section to better understand changes in volume
#     #
#     # for body_part_side, body_part_injury_risk in proc.injury_risk_dict.items():
#     #     matching_parts = [b for b in session_functional_movement.functional_movement_mappings if body_part_side == j]
#     #     if len(matching_parts) > 0:
#     #         if proc.injury_risk_dict[j].concentric_volume_today != matching_parts[0].concentric_volume:
#     #             k=0
#     #         elif proc.injury_risk_dict[j].concentric_volume_today == matching_parts[0].concentric_volume:
#     #             k=0
#     #         if proc.injury_risk_dict[j].eccentric_volume_today != matching_parts[0].eccentric_volume:
#     #             k=0
#     #         elif proc.injury_risk_dict[j].eccentric_volume_today == matching_parts[0].eccentric_volume:
#     #             k=0
#
#     vastus_lateralis_1 = BodyPartSide(BodyPartLocation(55), 1)
#     vastus_lateralis_2 = BodyPartSide(BodyPartLocation(55), 2)
#     vastus_medialis_1 = BodyPartSide(BodyPartLocation(56), 1)
#     vastus_medialis_2 = BodyPartSide(BodyPartLocation(56), 2)
#     vastus_intermedius_1 = BodyPartSide(BodyPartLocation(57), 1)
#     vastus_intermedius_2 = BodyPartSide(BodyPartLocation(57), 2)
#     rectus_femoris_1 = BodyPartSide(BodyPartLocation(58), 1)
#     rectus_femoris_2 = BodyPartSide(BodyPartLocation(58), 2)
#
#     assert proc.injury_risk_dict[vastus_lateralis_1].concentric_volume_today == 80  # affected body part
#     assert proc.injury_risk_dict[vastus_lateralis_2].concentric_volume_today == 100  # was 80
#     assert proc.injury_risk_dict[vastus_medialis_1].concentric_volume_today == 100  # was 80
#     assert proc.injury_risk_dict[vastus_medialis_2].concentric_volume_today == 100  # was 80
#     assert proc.injury_risk_dict[vastus_intermedius_1].concentric_volume_today == 100  # was 80
#     assert proc.injury_risk_dict[vastus_intermedius_2].concentric_volume_today == 100  # was 80
#     assert proc.injury_risk_dict[rectus_femoris_1].concentric_volume_today == 260  # was 240
#     assert proc.injury_risk_dict[rectus_femoris_2].concentric_volume_today == 260  # was 240



