
from fathomapi.api.config import Config
provider_info = Config.get('PROVIDER_INFO')
provider_info['movement_library_filename'] = 'movement_library_nike.json'
Config.set('PROVIDER_INFO', provider_info)

from models.planned_exercise import PlannedWorkout
from models.session import PlannedSession
from models.sport import SportName
from models.movement_tags import TrainingType
from models.workout_program import WorkoutProgramModule
from logic.workout_processing import WorkoutProcessor
from logic.calculators import Calculators
import os, json
import datetime


def get_completed_ntc_workout():
    all_workouts = []
    base_path = '../../database/ntc/libraries/NTC_completed/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    json_data = json.load(f)
                    workout = WorkoutProgramModule.json_deserialise(json_data)
                    all_workouts.append(workout)
    return all_workouts

def get_ntc_workout():
    all_workouts = []
    base_path = '../../database/ntc/libraries/workouts/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    json_data = json.load(f)
                    workout = PlannedWorkout.json_deserialise(json_data)
                    all_workouts.append(workout)
    return all_workouts


def get_nrc_workout():
    all_workouts = []
    base_path = '../../database/ntc/libraries/NRC_workouts/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    json_data = json.load(f)
                    workout = PlannedWorkout.json_deserialise(json_data)
                    # for section in workout.sections:
                    #     for exercise in section.exercises:
                    #         exercise.movement_id = '58459de6dc2ce90011f93d86'
                    all_workouts.append(workout)
    return all_workouts


def get_completed_session(date, workout):
    session = PlannedSession()
    session.event_date = date
    session.session_RPE = workout.rpe or 5
    # session.duration_minutes = workout.duration / 60
    session.sport_name = SportName.high_intensity_interval_training

    session.workout_program_module = workout
    WorkoutProcessor(user_weight=70, user_age=30).process_workout(session)

    return session

def get_planned_session(date, workout, assignment_type='default', movement_option=None):
    session = PlannedSession()
    session.event_date = date
    session.session_RPE = workout.rpe or 5
    # session.duration_minutes = workout.duration / 60
    session.sport_name = SportName.high_intensity_interval_training

    session.workout = workout
    WorkoutProcessor(user_weight=70, user_age=30).process_planned_workout(session, assignment_type=assignment_type, movement_option=movement_option)

    return session


def detect_plyo(all_workouts):
    workouts_with_plyo = 0
    total_workouts = 0
    plyo_ex_details = []
    for workout in all_workouts:
        total_workouts += 1
        total_exercises = 0
        plyo_exercises = 0
        for section in workout.sections:
            for exercise in section.exercises:
                total_exercises += 1
                if exercise.training_type in [TrainingType.power_action_plyometrics, TrainingType.power_drills_plyometrics]:
                    plyo_exercises += 1
        if plyo_exercises > 0:
            workouts_with_plyo += 1
            percent_plyo = plyo_exercises / total_exercises
            plyo_ex_details.append({
                'workout': workout.name,
                'total_exercises': total_exercises,
                'plyometric_workouts': plyo_exercises,
                'plyometrics_percentage': round(percent_plyo * 100, 2)
            })
    import pandas as pd
    pd.DataFrame(plyo_ex_details).to_csv('../../database/NTC/plyometrics_prevalence.csv', index=False)
    print(workouts_with_plyo, total_workouts)


def validate_result(workout):
    import pandas as pd
    powers = []
    for section in workout.sections:
        if section.assess_load:
            for exercise in section.exercises:
                if exercise.movement_id != "" and exercise.adaptation_type is not None:  # ignore rest intervals
                    if exercise.predicted_rpe is None:
                        print('here')
                    assert exercise.predicted_rpe.lower_bound is not None or exercise.predicted_rpe.observed_value is not None or exercise.predicted_rpe.upper_bound is not None
                    assert exercise.total_volume is not None
                    if exercise.predicted_rpe is not None:
                        try:
                            power = {
                                "exercise": exercise.name,
                                "training_type": exercise.training_type.name,
                                "rep_tempo": exercise.movement_rep_tempo,
                                "duration_per_rep": exercise.duration_per_rep.observed_value,
                                "reps_per_set": exercise.get_exercise_reps_per_set().observed_value,
                                "duration": exercise.duration.assigned_value if exercise.duration is not None else None,
                                "power": exercise.power.observed_value, #[int(exercise.power.lower_bound), int(exercise.power.observed_value), int(exercise.power.upper_bound)],
                                "rpe": [exercise.predicted_rpe.lower_bound, exercise.predicted_rpe.observed_value, exercise.predicted_rpe.upper_bound],
                                "force": Calculators.get_force_level(exercise.movement_speed, exercise.resistance, exercise.displacement),
                                "times": [ap.time for ap in exercise.actions_for_power],
                                "percent_bodyweights": [[round(bw, 2) for bw in ap.percent_bodyweight] for ap in exercise.actions_for_power],
                                "percent_bodyheights": [[round(bh, 2) for bh in ap.percent_bodyheight] for ap in exercise.actions_for_power],
                                "external_weight": [exercise.weight.min_value, exercise.weight.assigned_value, exercise.weight.max_value] if exercise.weight is not None else None,
                            }
                        except:
                            print('here')
                        powers.append(power)
                    assert exercise.power.lower_bound is not None or exercise.power.observed_value is not None or exercise.power.upper_bound is not None
    powers_pd = pd.DataFrame(powers)
    return powers
    # print('here')


# def test_ntc():
#     all_workouts = get_ntc_workout()
#     failed_count = 0
#     success_count = 0
#     all_powers = []
#     for planned_workout in all_workouts:
#         try:
#             session = get_planned_session(date=datetime.datetime.now(), workout=planned_workout)
#             all_powers.extend(validate_result(session.workout))
#             if session.power_load is None or session.power_load.observed_value is None:
#                 print(f"workout has no load: {planned_workout.name}")
#             if session.rpe_load is None or session.rpe_load.observed_value is None:
#                 print(f"workout has no rpe load: {planned_workout.name}")
#             success_count += 1
#         except Exception as e:
#             raise
#             failed_count += 1
#             print(f"processing failed: {planned_workout.name}")
#             print(e)
#     import pandas as pd
#     all_powers_pd = pd.DataFrame(all_powers)
#     all_powers_pd.to_csv('../data/power_outputs.csv')
#     # detect_plyo(all_workouts)
#     print(failed_count, success_count)
#
#



# def test_nrc():
#     all_workouts = get_nrc_workout()
#     failed_count = 0
#     success_count = 0
#     for planned_workout in all_workouts:
#         try:
#             session = get_session(date=datetime.datetime.now(), workout=planned_workout)
#             validate_result(session.workout)
#             if session.power_load is None or session.power_load.observed_value is None:
#                 print(f"workout has no power load: {planned_workout.name}")
#             if session.rpe_load is None or session.rpe_load.observed_value is None:
#                 print(f"workout has no rpe load: {planned_workout.name}")
#             success_count += 1
#         except Exception as e:
#             failed_count += 1
#             print(f"processing failed: {planned_workout.name}")
#             print(e)
#     print(failed_count, success_count)


# def test_completed_ntc():
#     all_workouts = get_completed_ntc_workout()
#     failed_count = 0
#     success_count = 0
#     all_powers = []
#     for workout in all_workouts:
#         try:
#             session = get_completed_session(date=datetime.datetime.now(), workout=workout)
#             # all_powers.extend(validate_result(session.workout))
#             if session.power_load is None or session.power_load.observed_value is None:
#                 print(f"workout has no load: {workout.name}")
#             if session.rpe_load is None or session.rpe_load.observed_value is None:
#                 print(f"workout has no rpe load: {workout.name}")
#             success_count += 1
#         except Exception as e:
#             raise
#             failed_count += 1
#             print(f"processing failed: {workout.name}")
#             print(e)
    # import pandas as pd
    # all_powers_pd = pd.DataFrame(all_powers)
    # all_powers_pd.to_csv('../data/power_outputs.csv')
    # # detect_plyo(all_workouts)
    # print(failed_count, success_count)
