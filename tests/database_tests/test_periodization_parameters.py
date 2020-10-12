from models.training_load import DetailedTrainingLoad, CompletedSessionDetails
from models.training_volume import StandardErrorRange
from models.movement_tags import DetailedAdaptationType
from logic.periodization_processor import TargetLoadCalculator
from models.periodization import PeriodizedExercise
from models.periodization_plan import TrainingPhaseType, PeriodizationPersona, TrainingPhaseFactory, \
    PeriodizationProgression
from models.periodization_goal import PeriodizationGoalType
from models.session import MixedActivitySession, SportTrainingSession
from models.session_functional_movement import SessionFunctionalMovement
from tests.mocks.mock_completed_session_details_datastore import CompletedSessionDetailsDatastore
from models.movement_tags import AdaptationDictionary, SubAdaptationType, TrainingType, AdaptationTypeMeasure
from models.ranked_types import RankedAdaptationType
from models.planned_exercise import PlannedWorkoutLoad
from models.user_stats import UserStats
from datetime import datetime, timedelta

#
# def get_35_day_completed_data_store():
#
#     data = [
#         # (days lag, rpe, watts, duration)
#         (1, 5, 50, 60),
#         (3, 6, 60, 60),
#         (4, 8, 80, 50),
#         (6, 7, 70, 40),
#         (8, 4, 40, 100),
#         (10, 7, 70, 50),
#         (12, 6, 60, 70),
#         (14, 6, 60, 80),
#         (15, 7, 70, 70),
#         (16, 6, 60, 80),
#         (18, 4, 40, 100),
#         (20, 8, 80, 50),
#         (23, 5, 50, 60),
#         (24, 5, 50, 80),
#         (25, 6, 60, 90),
#         (27, 8, 80, 70),
#         (30, 6, 60, 60),
#         (32, 4, 40, 100),
#         (34, 5, 50, 60),
#     ]
#
#     completed_session_details_list = []
#
#     for d in data:
#         session_date_time = datetime.now() - timedelta(days=d[0])
#         completed_session_details = CompletedSessionDetails(session_date_time,provider_id="1", workout_id="2")
#         completed_session_details.session_RPE = d[1]
#         completed_session_details.power_load = d[2] * d[3]
#         completed_session_details.rpe_load = d[1] * d[3]
#         completed_session_details.duration = d[3]
#         completed_session_details_list.append(completed_session_details)
#
#     data_store = CompletedSessionDetailsDatastore()
#     data_store.side_load_planned_workout(completed_session_details_list)
#
#     return data_store

# def get_seven_day_completed_data_store():
#
#     session_types = [7, 7, 7, 7, 7, 7, 7]
#     sections = [0, 1, 2, 3, 4, 5, 2]
#
#     dates = []
#     for d in range(0, 7):
#         dates.append(datetime.now() - timedelta(days=d))
#     rpes = [StandardErrorRange(observed_value=5),
#             StandardErrorRange(observed_value=6),
#             StandardErrorRange(observed_value=4),
#             StandardErrorRange(observed_value=5),
#             StandardErrorRange(observed_value=6),
#             StandardErrorRange(observed_value=3),
#             StandardErrorRange(observed_value=4)]
#
#     duration_minutes = [100, 90, 80, 90, 95, 85, 105]
#     sport_names = [None, None, None, None, None, None, None]
#
#     # workout_programs = [get_workout_program(sections=sections)]
#
#     sessions = get_sessions(session_types, dates, rpes, duration_minutes, sport_names, sections)
#
#     completed_session_details_list = []
#
#     for session in sessions:
#         session_functional_movement = SessionFunctionalMovement(session, {})
#         session_functional_movement.process(session.event_date, None)
#         completed_session_details_list.append(session_functional_movement.completed_session_details)
#
#     completed_session_details_list = [c for c in completed_session_details_list if c is not None]
#
#     data_store = CompletedSessionDetailsDatastore()
#     data_store.side_load_planned_workout(completed_session_details_list)
#
#     return data_store

# def get_section_json(name, exercises):
#     return {
#                 "name": name,
#                 "duration_seconds": 360,
#                 "start_date_time": None,
#                 "end_date_time": None,
#                 "exercises": exercises
#             }
#
#
# def get_workout_program(session, sections):
#     all_exercises = define_all_exercises()
#     workout_program = {
#         "workout_sections": []
#     }
#
#     for section_name, exercises in sections.items():
#         workout_program['workout_sections'].append(get_section_json(section_name, exercises=[all_exercises[ex] for ex in exercises]))
#
#     workout = WorkoutProgramModule.json_deserialise(workout_program)
#     processor = WorkoutProcessor()
#     session.workout_program_module = workout
#     processor.process_workout(session)
#     return workout


# def get_sessions(session_types, dates, rpes, duration_minutes, sport_names, sections_list):
#
#     if len(session_types) != len(dates) != len(rpes) != len(duration_minutes) != len(sport_names):
#         raise Exception("length must match for all arguments")
#
#     sessions = []
#
#     for d in range(0, len(dates)):
#         if session_types[d] == 7:
#             session = MixedActivitySession()
#             sections = get_section(sections_list[d])
#             session.workout_program_module = get_workout_program(session, sections=sections)
#         else:
#             session = SportTrainingSession()
#             session.sport_name = sport_names[d]
#         session.event_date = dates[d]
#         session.session_RPE = rpes[d]
#         session.duration_minutes = duration_minutes[d]
#
#         sessions.append(session)
#
#     return sessions

# def test_weekly_target_workload():
#
#     data_store = get_35_day_completed_data_store()
#     current_date_time = datetime.now()
#     user_stats = UserStats("tester")
#     user_stats.training_phase_type = TrainingPhaseType.increase
#     user_stats.demo_persona = PeriodizationPersona.well_trained
#     user_stats.periodization_goals = [PeriodizationGoalType.increase_cardiovascular_health]
#     injury_risk_dict = {}
#     proc = PeriodizationPlanProcessor(current_date_time, user_stats, injury_risk_dict, data_store, None)
#     h=0

# def test_training_load_calculator_weekly_load_target():
#
#     calc = TargetLoadCalculator()
#     training_phase_types = list(TrainingPhaseType)
#     chronic_average_weekly_load = StandardErrorRange(lower_bound=1000, upper_bound=1300)
#     last_weeks_load = StandardErrorRange(lower_bound=1100, observed_value=1200, upper_bound=1400)
#     average_session_rpe = StandardErrorRange(lower_bound=4, observed_value=5, upper_bound=6)
#     average_session_load = StandardErrorRange(lower_bound=216, observed_value=230, upper_bound=250)
#
#     factory = TrainingPhaseFactory()
#
#     f1 = open('../../output_periodization/periodization.csv', 'w')
#     f1.write("training_phase_type," +
#              "training_phase_acwr_lower_bound," +
#              "training_phase_acwr_observed_value," +
#              "training_phase_acwr_upper_bound," +
#              "progression_week_number," +
#              "progression_rpe_load_contribution," +
#              "progression_volume_load_contribution," +
#              "weekly_load_target_lower_bound," +
#              "weekly_load_target_observed_value," +
#              "weekly_load_target_upper_bound," +
#              "safe_weekly_load_target_lower_bound," +
#              "safe_weekly_load_target_observed_value," +
#              "safe_weekly_load_target_upper_bound," +
#              "target_session_load_lower_bound," +
#              "target_session_load_observed_value," +
#              "target_session_load_upper_bound," +
#              "safe_target_session_load_lower_bound," +
#              "safe_target_session_load_observed_value," +
#              "safe_target_session_load_upper_bound," +
#              "target_load_rate_lower_bound," +
#              "target_load_rate_observed_value," +
#              "target_load_rate_upper_bound," +
#              "safe_load_rate_lower_bound," +
#              "safe_load_rate_observed_value," +
#              "safe_load_rate_upper_bound," +
#              "safe_derived_rate_lower_bound," +
#              "safe_derived_rate_observed_value," +
#              "safe_derived_rate_upper_bound," +
#              "target_session_rpe_lower_bound," +
#              "target_session_rpe_observed_value," +
#              "target_session_rpe_upper_bound," +
#              "safe_session_rpe_lower_bound," +
#              "safe_session_rpe_observed_value," +
#              "safe_session_rpe_upper_bound," +
#              "safe_derived_session_rpe_lower_bound," +
#              "safe_derived_session_rpe_observed_value," +
#              "safe_derived_session_rpe_upper_bound," +
#              "target_session_volume_lower_bound," +
#              "target_session_volume_observed_value," +
#              "target_session_volume_upper_bound," +
#              "safe_session_volume_lower_bound," +
#              "safe_session_volume_observed_value," +
#              "safe_session_volume_upper_bound," +
#              "safe_derived_session_volume_lower_bound," +
#              "safe_derived_session_volume_observed_value," +
#              "safe_derived_session_volume_upper_bound" + '\n'
#              )
#
#     for training_phase_type in training_phase_types:
#         training_phase = factory.create(training_phase_type)
#
#         periodization_progression_1 = PeriodizationProgression(week_number=0, training_phase=training_phase,
#                                                                rpe_load_contribution=0.20,
#                                                                volume_load_contribution=0.80)
#         periodization_progression_2 = PeriodizationProgression(week_number=1, training_phase=training_phase,
#                                                                rpe_load_contribution=0.40,
#                                                                volume_load_contribution=0.60)
#         periodization_progression_3 = PeriodizationProgression(week_number=2, training_phase=training_phase,
#                                                                rpe_load_contribution=0.60,
#                                                                volume_load_contribution=0.40)
#         periodization_progression_4 = PeriodizationProgression(week_number=3, training_phase=training_phase,
#                                                                rpe_load_contribution=0.80,
#                                                                volume_load_contribution=0.20)
#
#         progressions = [periodization_progression_1, periodization_progression_2, periodization_progression_3,
#                         periodization_progression_4]
#
#         for progression in progressions:
#             if training_phase.acwr.lower_bound is not None:
#                 safe_target_rate = StandardErrorRange(lower_bound=.8,
#                                                       observed_value=None,
#                                                       upper_bound=max(1.5, training_phase.acwr.upper_bound))
#
#                 # given their training phase and history, what's an appropriate weekly total load target?
#                 weekly_load_target = calc.get_weekly_load_target(chronic_average_weekly_load, training_phase.acwr)
#
#                 # given their training phase and history, what's a safe maximum range of weekly load for this athlete?
#                 safe_weekly_load_target = calc.get_weekly_load_target(chronic_average_weekly_load, safe_target_rate)
#
#                 # given the average load they're used to in a session, and the implied ramp of the weekly load target,
#                 # what is the average range of load for a session?
#                 target_average_session_load, target_implied_ramp = calc.get_target_session_load_and_ramp(average_session_load,
#                                                                                                  last_weeks_load,
#                                                                                                  weekly_load_target)
#
#                 # given the average load they're used to in a session, and the implied ramp of the weekly load target,
#                 # what is the maximum safe load range of load for a session?
#                 safe_target_average_session_load, safe_target_implied_ramp = calc.get_target_session_load_and_ramp(average_session_load,
#                                                                                                                    last_weeks_load,
#                                                                                                                    safe_weekly_load_target)
#
#                 # why could we not just apply the safe acwr range to the average session load?
#
#                 # could we ignore the previous step and just proceed with the average session rpe?
#
#                 target_average_session_rpe = calc.get_target_session_intensity(average_session_rpe, progression, target_implied_ramp)
#
#                 safe_limit_session_rpe = calc.get_target_session_intensity(average_session_rpe, progression, safe_target_rate)
#
#                 safe_derived_session_rpe = calc.get_target_session_intensity(average_session_rpe, progression,
#                                                                              safe_target_implied_ramp)
#
#                 target_session_volume = calc.get_target_session_volume(target_average_session_load, target_average_session_rpe)
#                 safe_target_session_volume = calc.get_target_session_volume(target_average_session_load, safe_limit_session_rpe)
#                 safe_derived_session_volume = calc.get_target_session_volume(target_average_session_load, safe_derived_session_rpe)
#                 f1.write(str(training_phase_type.name) + "," +
#                          str(training_phase.acwr.lower_bound) + "," +
#                          str(training_phase.acwr.observed_value) + "," +
#                          str(training_phase.acwr.upper_bound) + "," +
#                          str(progression.week_number) + "," +
#                          str(progression.rpe_load_contribution) + "," +
#                          str(progression.volume_load_contribution) + "," +
#                          str(weekly_load_target.lower_bound) + "," +
#                          str(weekly_load_target.observed_value) + "," +
#                          str(weekly_load_target.upper_bound) + "," +
#                          str(safe_weekly_load_target.lower_bound) + "," +
#                          str(safe_weekly_load_target.observed_value) + "," +
#                          str(safe_weekly_load_target.upper_bound) + "," +
#                          str(target_average_session_load.lower_bound) + "," +
#                          str(target_average_session_load.observed_value) + "," +
#                          str(target_average_session_load.upper_bound) + "," +
#                          str(safe_target_average_session_load.lower_bound) + "," +
#                          str(safe_target_average_session_load.observed_value) + "," +
#                          str(safe_target_average_session_load.upper_bound) + "," +
#                          str(target_implied_ramp.lower_bound) + "," +
#                          str(target_implied_ramp.observed_value) + "," +
#                          str(target_implied_ramp.upper_bound) + "," +
#                          str(safe_target_rate.lower_bound) + "," +
#                          str(safe_target_rate.observed_value) + "," +
#                          str(safe_target_rate.upper_bound) + "," +
#                          str(safe_target_implied_ramp.lower_bound) + "," +
#                          str(safe_target_implied_ramp.observed_value) + "," +
#                          str(safe_target_implied_ramp.upper_bound) + "," +
#                          str(target_average_session_rpe.lower_bound) + "," +
#                          str(target_average_session_rpe.observed_value) + "," +
#                          str(target_average_session_rpe.upper_bound) + "," +
#                          str(safe_limit_session_rpe.lower_bound) + "," +
#                          str(safe_limit_session_rpe.observed_value) + "," +
#                          str(safe_limit_session_rpe.upper_bound) + "," +
#                          str(safe_derived_session_rpe.lower_bound) + "," +
#                          str(safe_derived_session_rpe.observed_value) + "," +
#                          str(safe_derived_session_rpe.upper_bound) + "," +
#                          str(target_session_volume.lower_bound) + "," +
#                          str(target_session_volume.observed_value) + "," +
#                          str(target_session_volume.upper_bound) + "," +
#                          str(safe_target_session_volume.lower_bound) + "," +
#                          str(safe_target_session_volume.observed_value) + "," +
#                          str(safe_target_session_volume.upper_bound) + "," +
#                          str(safe_derived_session_volume.lower_bound) + "," +
#                          str(safe_derived_session_volume.observed_value) + "," +
#                          str(safe_derived_session_volume.upper_bound) + '\n')
#     f1.close()


