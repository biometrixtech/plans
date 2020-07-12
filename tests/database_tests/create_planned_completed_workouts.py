from models.workout_program import BaseWorkoutExercise
from models.functional_movement import FunctionalMovementActionMapping, FunctionalMovementFactory
from models.movement_tags import TrainingType
from models.training_volume import StandardErrorRange
from models.planned_exercise import PlannedWorkoutLoad
from logic.detailed_load_processing import DetailedLoadProcessor
from tests.mocks.mock_action_library_datastore import ActionLibraryDatastore
from datetime import datetime
import os
import json


action_dictionary = ActionLibraryDatastore().get()


def get_filtered_actions(training_type_list):

    action_list = list(action_dictionary.values())

    filtered_list = [a for a in action_list if a.training_type in training_type_list]

    return filtered_list


def process_adaptation_types(action_list, reps, rpe, duration=None, percent_max_hr=None):

    detailed_load_processor = DetailedLoadProcessor()

    functional_movement_factory = FunctionalMovementFactory()
    functional_movement_dict = functional_movement_factory.get_functional_movement_dictionary()
    event_date = datetime.now()

    for action in action_list:
        duration = duration

        base_exercise = BaseWorkoutExercise()
        base_exercise.training_type = action.training_type
        base_exercise.power_load = StandardErrorRange(lower_bound=50, observed_value=75, upper_bound=100)
        base_exercise.set_adaption_type()

        action.power_load_left = base_exercise.power_load
        action.power_load_right = base_exercise.power_load

        functional_movement_action_mapping = FunctionalMovementActionMapping(action,
                                                                             {},
                                                                             event_date, functional_movement_dict)

        detailed_load_processor.add_load(functional_movement_action_mapping,
                                         adaptation_type=base_exercise.adaptation_type,
                                         movement_action=action,
                                         training_load_range=base_exercise.power_load,
                                         reps=reps,
                                         duration=duration,
                                         rpe=rpe,
                                         percent_max_hr=percent_max_hr)
    detailed_load_processor.rank_types()

    return detailed_load_processor


def get_planned_workout(workout_id, training_type_list, session_rpe, projected_rpe_load, reps, rpe, duration=None,
                        percent_max_hr=None):

    workout = PlannedWorkoutLoad(workout_id=workout_id)
    workout.projected_session_rpe = session_rpe
    workout.duration = 75
    workout.projected_rpe_load = projected_rpe_load

    action_list = get_filtered_actions(training_type_list)

    detailed_load_processor = process_adaptation_types(action_list, reps=reps, rpe=rpe, duration=duration,
                                                       percent_max_hr=percent_max_hr)

    workout.session_detailed_load = detailed_load_processor.session_detailed_load
    workout.session_training_type_load = detailed_load_processor.session_training_type_load
    workout.muscle_detailed_load = detailed_load_processor.muscle_detailed_load

    session_load = StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)
    for training_type_load in detailed_load_processor.session_training_type_load.load.values():
        session_load.add(training_type_load)

    workout.projected_power_load = session_load

    return workout


def get_workout_library(rpe_list, duration_list):

    workouts = []
    id = 1

    training_type_list_1 = [TrainingType.strength_cardiorespiratory]
    training_type_list_2 = [TrainingType.strength_integrated_resistance, TrainingType.strength_endurance]

    for r in rpe_list:
        for d in duration_list:

            projected_rpe_load = StandardErrorRange(lower_bound=r*d, upper_bound=r*d, observed_value=r*d)
            projected_rpe = StandardErrorRange(lower_bound=r, upper_bound=r, observed_value=r)
            planned_workout = get_planned_workout(id, training_type_list_1,projected_rpe,projected_rpe_load,reps=None,
                                                  rpe=r,duration=d,percent_max_hr=70)
            workouts.append(planned_workout)
            id += 1

    for r in rpe_list:
        for d in duration_list:
            projected_rpe_load = StandardErrorRange(lower_bound=r * d, upper_bound=r * d, observed_value=r * d)
            projected_rpe = StandardErrorRange(lower_bound=r, upper_bound=r, observed_value=r)
            planned_workout = get_planned_workout(id, training_type_list_2, projected_rpe, projected_rpe_load, reps=10, rpe=r)
            workouts.append(planned_workout)
            id += 1

    return workouts


def write_workouts_json(workout_json):
    json_string = json.dumps(workout_json, indent=4)
    file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/planned_workout_library.json")
    print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()

def test_create_workouts():
    rpe_list = list(range(5,6))
    duration_list = list(range(30, 60, 10))
    workouts = get_workout_library(rpe_list, duration_list)
    for w in workouts:
        write_workouts_json(w.json_serialise())
