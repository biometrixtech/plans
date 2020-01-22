from fathomapi.api.config import Config
Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                             'body_part_mapping_filename': 'body_part_mapping_fathom.json'})

from logic.scoring_processor import ScoringProcessor, ScoringSummaryProcessor
from models.scoring import MovementVariableScores, MovementVariableType, EquationType
import tests.mock_users.movement_pattern_history as mph
from models.functional_movement import MovementPatterns, Elasticity
from models.asymmetry import Asymmetry, AnteriorPelvicTilt, AnklePitch,HipDrop, KneeValgus, HipRotation
from models.chart_data import BiomechanicsSummaryChart
from datetime import datetime, timedelta
from utils import format_datetime
from models.session import SessionFactory, SessionType, PostSurvey, SessionSource


# def get_session(event_date, rpe):

#     ps_event_date = event_date + timedelta(minutes=40)
#     session = SessionFactory().create(SessionType(6))
#     session.event_date = ps_event_date
#     session.sport_name = 72
#     session.duration_minutes = 30
#     session.source = SessionSource.three_sensor
#     session.post_session_survey = PostSurvey(survey={'RPE': rpe, 'soreness': []},
#                                              event_date=format_datetime(ps_event_date))

#     return session

# def get_run_a_sessions():

#     session_list = []

#     history, session_details = mph.run_a_regressions()
#     days = len(history)
#     base_date_time = datetime.now() - timedelta(days=len(history)-1)

#     for i in range(days):
#         if history[i] is not None:
#             movement_patterns_response = mph.create_elasticity_adf(history[i])
#             movement_patterns = MovementPatterns.json_deserialise(movement_patterns_response)
#             asymmetry = Asymmetry()
#             apt = AnteriorPelvicTilt(6, 8)
#             apt.percent_events_asymmetric = 65
#             ankle_pitch = AnklePitch(8,5)
#             ankle_pitch.percent_events_asymmetric = 74
#             asymmetry.ankle_pitch = ankle_pitch
#             hip_drop = HipDrop(7, 8.5)
#             hip_drop.percent_events_asymmetric = 82
#             asymmetry.anterior_pelvic_tilt = apt
#             asymmetry.hip_drop = hip_drop
#             knee_valgus = KneeValgus(6,7)
#             knee_valgus.percent_events_asymmetric = 79
#             asymmetry.knee_valgus = knee_valgus
#             hip_rotation = HipRotation(7,9)
#             hip_rotation.percent_events_asymmetric = 91
#             asymmetry.hip_rotation = hip_rotation
#             session = get_session(base_date_time + timedelta(days=i), 5)
#             session.asymmetry = asymmetry
#             session.movement_patterns = movement_patterns
#             session_list.append(session)

#     return session_list


# def test_get_apt_scores():

#     proc = ScoringProcessor()
#     history, session_details = mph.run_a_regressions()
#     days = len(history)
#     for i in range(days):
#         if history[i] is not None:
#             movement_patterns_response = mph.create_elasticity_adf(history[i])
#             movement_patterns = MovementPatterns.json_deserialise(movement_patterns_response)
#             asymmetry = Asymmetry()
#             apt = AnteriorPelvicTilt(6, 8)
#             hip_drop = HipDrop(7, 8.5)
#             asymmetry.anterior_pelvic_tilt = apt
#             asymmetry.hip_drop = hip_drop
#             knee_valgus = KneeValgus(6,7)
#             asymmetry.knee_valgus = knee_valgus
#             hip_rotation = HipRotation(7,9)
#             asymmetry.hip_rotation = hip_rotation
#             apt_scores = proc.get_apt_scores(asymmetry, movement_patterns)
#             ankle_pitch_scores = proc.get_ankle_pitch_scores(movement_patterns)
#             hip_drop_scores= proc.get_hip_drop_scores(asymmetry, movement_patterns)
#             knee_valgus_scores = proc.get_knee_valgus_scores(asymmetry, movement_patterns)
#             hip_rotation_scores = proc.get_hip_rotation_scores(asymmetry, movement_patterns)
#             j=0
#     j=0


# def test_biomechanics_summary_chart():

#     sessions = get_run_a_sessions()

#     chart = BiomechanicsSummaryChart()
#     chart.add_sessions(sessions)

#     json_data = chart.json_serialise()

#     scoring_summary_proc = ScoringSummaryProcessor()

#     base_date = datetime.now().date()

#     recovery_quality = scoring_summary_proc.get_recovery_quality(chart.sessions, base_date)

#     recovery_quality_json = recovery_quality.json_serialise()

#     k=0