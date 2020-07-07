from models.functional_movement import FunctionalMovementActionMapping, FunctionalMovementFactory
from models.soreness_base import BodyPartSide
from models.workout_program import BaseWorkoutExercise
from tests.mocks.mock_action_library_datastore import ActionLibraryDatastore
from datetime import datetime
from logic.detailed_load_processing import DetailedLoadProcessor
from models.training_volume import StandardErrorRange
from models.movement_tags import AdaptationType

def get_actions():
    datastore = ActionLibraryDatastore()
    actions = datastore.get()
    return actions

# def test_actions():
#     functional_movement_factory = FunctionalMovementFactory()
#     functional_movement_dict = functional_movement_factory.get_functional_movement_dictinary()
#     event_date = datetime.now()
#     action_list = get_actions()
#
#     detailed_load_processor = DetailedLoadProcessor()
#
#     no_speed_list = []
#     no_resistance_list = []
#
#     for id, action in action_list.items():
#
#         reps = None
#         duration = None
#         rpe = None
#
#         base_exercise = BaseWorkoutExercise()
#         base_exercise.training_type = action.training_type
#         base_exercise.power_load = StandardErrorRange(lower_bound=50, observed_value=75, upper_bound=100)
#         base_exercise.set_adaption_type()
#
#         action.power_load_left = base_exercise.power_load
#         action.power_load_right = base_exercise.power_load
#
#         if action.resistance is None:
#             no_resistance_list.append(action)
#
#         if action.speed is None:
#             no_speed_list.append(action)
#
#         if base_exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
#             duration = 600
#             rpe = 5
#         else:
#             reps = 10
#             rpe = 6
#
#         functional_movement_action_mapping = FunctionalMovementActionMapping(action,
#                                                                              {},
#                                                                              event_date, functional_movement_dict)
#         for muscle_string, load in functional_movement_action_mapping.muscle_load.items():
#
#
#             detailed_load_processor.add_load(functional_movement_action_mapping,
#                                              adaptation_type=base_exercise.adaptation_type,
#                                              movement_action=action,
#                                              training_load_range=base_exercise.power_load,
#                                              reps=reps,
#                                              duration=duration,
#                                              rpe=rpe)
#     action_list_length = len(action_list)
#     no_speed_length = len(no_speed_list)
#     no_resistance_length = len(no_resistance_list)
#
#     assert 1==1