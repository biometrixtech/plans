from logic.scoring_processor import ScoringProcessor, ScoringSummaryProcessor
from models.scoring import MovementVariableScores, MovementVariableType, EquationType
import movement_pattern_history as mph
from models.functional_movement import MovementPatterns, Elasticity
from models.asymmetry import Asymmetry, AnteriorPelvicTilt, AnklePitch,HipDrop, KneeValgus, HipRotation
from models.chart_data import BiomechanicsSummaryChart
from datetime import datetime, timedelta
from utils import format_datetime
from models.session import SessionFactory, SessionType, PostSurvey, SessionSource


def get_session(event_date, rpe):

    ps_event_date = event_date + timedelta(minutes=40)
    session = SessionFactory().create(SessionType(6))
    session.event_date = ps_event_date
    session.sport_name = 72
    session.duration_minutes = 30
    session.source = SessionSource.three_sensor
    session.post_session_survey = PostSurvey(survey={'RPE': rpe, 'soreness': []},
                                             event_date=format_datetime(ps_event_date))

    return session

def get_run_a_sessions():

    session_list = []

    history, session_details = mph.run_a_regressions()
    days = len(history)
    base_date_time = datetime.now() - timedelta(days=len(history)-1)

    for i in range(days):
        if history[i] is not None:
            movement_patterns_response = mph.create_elasticity_adf(history[i])
            movement_patterns = MovementPatterns.json_deserialise(movement_patterns_response)
            asymmetry = Asymmetry()
            apt = AnteriorPelvicTilt(6, 8)
            apt.percent_events_asymmetric = 65
            ankle_pitch = AnklePitch(8,5)
            ankle_pitch.percent_events_asymmetric = 74
            asymmetry.ankle_pitch = ankle_pitch
            hip_drop = HipDrop(7, 8.5)
            hip_drop.percent_events_asymmetric = 82
            asymmetry.anterior_pelvic_tilt = apt
            asymmetry.hip_drop = hip_drop
            knee_valgus = KneeValgus(6,7)
            knee_valgus.percent_events_asymmetric = 79
            asymmetry.knee_valgus = knee_valgus
            hip_rotation = HipRotation(7,9)
            hip_rotation.percent_events_asymmetric = 91
            asymmetry.hip_rotation = hip_rotation
            session = get_session(base_date_time + timedelta(days=i), 5)
            session.asymmetry = asymmetry
            session.movement_patterns = movement_patterns
            session_list.append(session)

    return session_list


def test_get_apt_scores():

    proc = ScoringProcessor()
    history, session_details = mph.run_a_regressions()
    days = len(history)
    for i in range(days):
        if history[i] is not None:
            movement_patterns_response = mph.create_elasticity_adf(history[i])
            movement_patterns = MovementPatterns.json_deserialise(movement_patterns_response)
            asymmetry = Asymmetry()
            apt = AnteriorPelvicTilt(6, 8)
            hip_drop = HipDrop(7, 8.5)
            asymmetry.anterior_pelvic_tilt = apt
            asymmetry.hip_drop = hip_drop
            knee_valgus = KneeValgus(6,7)
            asymmetry.knee_valgus = knee_valgus
            hip_rotation = HipRotation(7,9)
            asymmetry.hip_rotation = hip_rotation
            apt_scores = proc.get_apt_scores(asymmetry, movement_patterns)
            ankle_pitch_scores = proc.get_ankle_pitch_scores(movement_patterns)
            hip_drop_scores= proc.get_hip_drop_scores(asymmetry, movement_patterns)
            knee_valgus_scores = proc.get_knee_valgus_scores(asymmetry, movement_patterns)
            hip_rotation_scores = proc.get_hip_rotation_scores(asymmetry, movement_patterns)
            j=0
    j=0


def test_biomechanics_summary_chart():

    sessions = get_run_a_sessions()

    chart = BiomechanicsSummaryChart()
    chart.add_sessions(sessions)

    json_data = chart.json_serialise()

    scoring_summary_proc = ScoringSummaryProcessor()

    base_date = datetime.now().date()

    recovery_quality = scoring_summary_proc.get_recovery_quality(chart.sessions, base_date)

    recovery_quality_json = recovery_quality.json_serialise()

#     k=0

def get_equation_list(value_list):
    equation_list = []
    for value in value_list:
        elasticity = Elasticity()
        elasticity.elasticity = value
        equation_list.append(elasticity)
    return equation_list

def test_elasticity_dysfunction_score():
    sp = ScoringProcessor()
    coefficients_list  = (
        # examples
        [.4, 0],
        [0.4, .4], #  --> 76
        [.5, .5], #  --> 85
        [.5, 0], #  --> 85
        [.5, 0., .5, 0],  # --> 77.5
        [.5, 0., .5, .5],  # --> 77.5
        [1.5, 0],  # --> 55
        [1.5, 1.5],  # --> 10
        [1.5, 1.5, 1.5, 1.5],  # --> 10
        [1, 1],
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 0, 0],
        [1, 1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 0, 0],
        [1, 0],
        [2, 2, 2, 2],
        [2, 2, 2, 0],
        [2, 2, 0, 0],

        # 7bbff8e0
        [0, 0.206490226954283], # apt -->  93
        [-0.159515012897757, -0.277147155116258, 0.0723139465482049, 0.0],  # hip_drop --> 99
        [0.0, 0.0, 0.0, -0.350647636838605, 0.0, -0.251201252875501],  # knee_valgus --> 100
        [0.924804782628251, 0.626882930247725, 0, 0.258772334759487],  # hip_rotation --> 73
        [0.924804782628251, 0.626882930247725, 0.01, 0.258772334759487],  # hip_rotation --> 73

        # c14f1728
        [0.0345736161517883, 0.288488188735086], # apt --> 90
        [0.135184178791529, 0.196180582682485, 0.0510926754299412, 0.0], # hip_drop --> 94
        [0.0, 0.0, 0.0,  0.0, 0.0, -0.239635631923202],  # knee_valgus --> 100
        [0.0471320102970911, -0.731835173000968, -0.228395501234287, -0.531684824385146],  # hip_rotation --> 99

        # f93e004d
        [-0.891180773774133, -1.46141158488873], # apt --> 100
        [0.20416289977369, 0.0, 0.0, 0.0], # hip_drop --> 97
        [0.20416289977369, 0.001, 0.001, 0.001],
        [0.0, 0.141232487324098, 0.0, 0.0, -0.161874154731829, -0.20458903087513],  # knee_valgus --> 98
        [1.16584437793462, 1.31813819855037, 0.0, -0.480878531935277], # hip_rotation --> 62
        [1.16584437793462, 1.31813819855037],  # --> 25 (see f93 hip_rotation for comparision)

    )
    for coefficients in coefficients_list:
        equation_list = get_equation_list(coefficients)
        equations = [EquationType.apt_ankle_pitch] * 3
        scores = MovementVariableScores(MovementVariableType.apt)
        score = sp.get_elasticity_dysfunction_score(equation_list, equations, scores)
        print(f"Coefficients: {coefficients} --> {round(score,1)}")
        assert score != -999