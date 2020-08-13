from models.workout_program import BaseWorkoutExercise
from models.functional_movement import FunctionalMovementActionMapping, FunctionalMovementFactory
from models.training_volume import StandardErrorRange
from models.planned_exercise import PlannedWorkoutLoad
from models.movement_tags import DetailedAdaptationType
from logic.detailed_load_processing import DetailedLoadProcessor
from datetime import datetime
from tests.mocks.mock_action_library_datastore import ActionLibraryDatastore

action_dictionary = ActionLibraryDatastore().get()
action_list = list(action_dictionary.values())

def group_actions(training_type_list):

    # action_list = list(action_dictionary.values())
    filtered_list = [a for a in action_list if a.training_type in training_type_list]
    action_ids = [a.id for a in filtered_list]

    grouped_actions = {}
    for action_id in action_ids:
        if '.' in action_id:
            id_group = action_id.split('.')[0]
        elif '_' in action_id:
            id_group = action_id.split('_')[0]
        else:
            id_group = action_id
        if id_group not in grouped_actions:
            grouped_actions[id_group] = [action_id]
        else:
            grouped_actions[id_group].append(action_id)

    return grouped_actions


def get_filtered_actions(training_type_list):

    # action_list = list(action_dictionary.values())

    filtered_list = [a for a in action_list if a.training_type in training_type_list]

    return filtered_list

def get_all_actions_for_groups(action_id_list):
    filtered_list = [a for a in action_list if a.id in action_id_list]
    return filtered_list


def process_action(action, detailed_load_processor, event_date, functional_movement_dict, reps, duration, rpe, percent_max_hr):
    base_exercise = BaseWorkoutExercise()
    base_exercise.training_type = action.training_type
    base_exercise.power_load = StandardErrorRange(lower_bound=50, observed_value=75, upper_bound=100)
    base_exercise.set_adaption_type()

    action.power_load_left = base_exercise.power_load
    action.power_load_right = base_exercise.power_load

    functional_movement_action_mapping = FunctionalMovementActionMapping(action,
                                                                         {},
                                                                         event_date, functional_movement_dict)

    return detailed_load_processor.add_load(functional_movement_action_mapping,
                                            adaptation_type=base_exercise.adaptation_type,
                                            movement_action=action,
                                            training_load_range=base_exercise.power_load,
                                            reps=reps,
                                            duration=duration,
                                            rpe_range=rpe,
                                            percent_max_hr=percent_max_hr,
                                            return_adaptation_types=True)

def process_adaptation_types(training_type_list, reps, rpe, duration=None, percent_max_hr=None, actions_group_dict=None):

    detailed_load_processor = DetailedLoadProcessor()

    functional_movement_factory = FunctionalMovementFactory()
    functional_movement_dict = functional_movement_factory.get_functional_movement_dictionary()
    event_date = datetime.now()

    if actions_group_dict is not None:  # if we want all actions for the training types
        if duration is not None:
            duration /= len(actions_group_dict)
        for action__id_list in actions_group_dict.values():
            action_list = get_all_actions_for_groups(action__id_list)
            exercise_detail_adaptation_types = set()
            for action in action_list:
                action_detailed_adaptation_types = process_action(action, detailed_load_processor, event_date, functional_movement_dict, reps, duration, rpe, percent_max_hr)
                exercise_detail_adaptation_types.update(action_detailed_adaptation_types)
            for detailed_adaptation_type in exercise_detail_adaptation_types:
                detailed_load_processor.session_detailed_load.add_duration(detailed_adaptation_type, duration)
    else:  # if a subset of specific actions is defined
        action_list = get_filtered_actions(training_type_list)
        for action in action_list:
            process_action(action, detailed_load_processor, event_date, functional_movement_dict, reps, duration, rpe, percent_max_hr)
        for detailed_adaptation_type in DetailedAdaptationType:
            if getattr(detailed_load_processor.session_detailed_load, detailed_adaptation_type.name) is not None:
                detailed_load_processor.session_detailed_load.add_duration(detailed_adaptation_type, duration)

    # for action in action_list:
    #     duration = duration
    #
    #     base_exercise = BaseWorkoutExercise()
    #     base_exercise.training_type = action.training_type
    #     base_exercise.power_load = StandardErrorRange(lower_bound=50, observed_value=75, upper_bound=100)
    #     base_exercise.set_adaption_type()
    #
    #     action.power_load_left = base_exercise.power_load
    #     action.power_load_right = base_exercise.power_load
    #
    #     functional_movement_action_mapping = FunctionalMovementActionMapping(action,
    #                                                                          {},
    #                                                                          event_date, functional_movement_dict)
    #
    #     detailed_load_processor.add_load(functional_movement_action_mapping,
    #                                      adaptation_type=base_exercise.adaptation_type,
    #                                      movement_action=action,
    #                                      training_load_range=base_exercise.power_load,
    #                                      reps=reps,
    #                                      duration=duration,
    #                                      rpe_range=rpe,
    #                                      percent_max_hr=percent_max_hr)
    detailed_load_processor.rank_types()

    return detailed_load_processor


def get_planned_workout(workout_id, training_type_list, session_rpe, projected_rpe_load, reps, rpe, duration=None,
                        percent_max_hr=None, actions_group_dict=None):

    workout = PlannedWorkoutLoad(workout_id=workout_id)
    workout.projected_session_rpe = session_rpe
    workout.duration = duration or 75 * 60
    workout.projected_rpe_load = projected_rpe_load

    detailed_load_processor = process_adaptation_types(training_type_list, reps=reps, rpe=rpe, duration=duration,
                                                       percent_max_hr=percent_max_hr, actions_group_dict=actions_group_dict)

    workout.session_detailed_load = detailed_load_processor.session_detailed_load
    workout.session_training_type_load = detailed_load_processor.session_training_type_load
    workout.muscle_detailed_load = detailed_load_processor.muscle_detailed_load
    workout.ranked_muscle_detailed_load = detailed_load_processor.ranked_muscle_load

    session_load = StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)
    for training_type_load in detailed_load_processor.session_training_type_load.load.values():
        session_load.add(training_type_load)

    workout.projected_power_load = session_load

    return workout