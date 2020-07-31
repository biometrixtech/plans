import os
from models.workout_program import BaseWorkoutExercise
from models.functional_movement import FunctionalMovementActionMapping, FunctionalMovementFactory
from models.movement_tags import TrainingType
from models.training_volume import StandardErrorRange
from models.planned_exercise import PlannedWorkoutLoad
from logic.detailed_load_processing import DetailedLoadProcessor
from datetime import datetime
from tests.mocks.planned_workout_utilities import get_planned_workout
import json


def get_workout_library(rpe_list, duration_list):

    workouts = []
    id = 1

    training_type_list_cardio = [TrainingType.strength_cardiorespiratory]
    training_type_list_resistance_endurance = [TrainingType.strength_integrated_resistance, TrainingType.strength_endurance]
    training_type_list_power = [TrainingType.power_action_olympic_lift, TrainingType.power_action_plyometrics]

    percent_max_hr_list = [70, 82, 90]

    for p in percent_max_hr_list:
        for r in rpe_list:
            for d in duration_list:
                projected_rpe_load = StandardErrorRange(lower_bound=r * d, upper_bound=r * d, observed_value=r * d)
                projected_rpe = StandardErrorRange(lower_bound=r, upper_bound=r, observed_value=r)
                planned_workout = get_planned_workout(id,
                                                      training_type_list_cardio,
                                                      projected_rpe,
                                                      projected_rpe_load,
                                                      reps=None,
                                                      rpe=r, duration=d,
                                                      percent_max_hr=p)
                workouts.append(planned_workout)
                id += 1

    reps_list = [10, 15]
    for reps in reps_list:
        for r in rpe_list:
            for d in duration_list:
                projected_rpe_load = StandardErrorRange(lower_bound=r * d, upper_bound=r * d, observed_value=r * d)
                projected_rpe = StandardErrorRange(lower_bound=r, upper_bound=r, observed_value=r)
                planned_workout = get_planned_workout(id, training_type_list_resistance_endurance, projected_rpe, projected_rpe_load, reps=reps, rpe=r)
                workouts.append(planned_workout)
                id += 1

    for reps in reps_list:
        for r in rpe_list:
            for d in duration_list:
                projected_rpe_load = StandardErrorRange(lower_bound=r*d, upper_bound=r*d, observed_value=r*d)
                projected_rpe = StandardErrorRange(lower_bound=r, upper_bound=r, observed_value=r)
                planned_workout = get_planned_workout(id, training_type_list_power,projected_rpe,projected_rpe_load,
                                                      reps=reps,rpe=r,duration=d,percent_max_hr=None)
                workouts.append(planned_workout)
                id += 1

    return workouts


def get_workouts_json(workouts):
    workouts_json = {}
    for workout in workouts:
        workouts_json[workout.workout_id] = workout.json_serialise()
    return workouts_json


def write_workouts_json(workout_json):
    json_string = json.dumps(workout_json, indent=4)
    file_name = os.path.join(os.path.realpath('..'), f"../apigateway/models/planned_workout_library.json")
    print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()


def test_write_workout_library_json():
    rpe_list = list(range(1, 11))
    duration_list = list(range(30, 90, 5))
    workouts = get_workout_library(rpe_list, duration_list)
    workouts_json = get_workouts_json(workouts)
    write_workouts_json(workouts_json)
