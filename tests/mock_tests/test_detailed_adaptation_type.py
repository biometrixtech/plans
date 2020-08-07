from models.functional_movement import FunctionalMovementActionMapping, FunctionalMovementFactory
from models.soreness_base import BodyPartSide
from models.workout_program import BaseWorkoutExercise
from tests.mocks.mock_action_library_datastore import ActionLibraryDatastore
from datetime import datetime
from logic.detailed_load_processing import DetailedLoadProcessor
from models.training_volume import StandardErrorRange
from models.movement_tags import AdaptationType, TrainingType
from models.movement_actions import MovementSpeed, MovementResistance


action_dictionary = ActionLibraryDatastore().get()

# def get_actions():
#     datastore = ActionLibraryDatastore()
#     actions = datastore.get()
#     return actions
#

def get_filtered_actions(training_type_list):

    #action_dictionary = get_actions()

    action_list = list(action_dictionary.values())

    filtered_list = [a for a in action_list if a.training_type in training_type_list]

    return filtered_list

def process_adaptation_types(action_list, reps_list, rpe_list, duration=None):

    detailed_load_processor = DetailedLoadProcessor()

    functional_movement_factory = FunctionalMovementFactory()
    functional_movement_dict = functional_movement_factory.get_functional_movement_dictionary()
    event_date = datetime.now()

    for action in action_list:
        for reps in reps_list:
            for rpe in rpe_list:
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
                #for muscle_string, load in functional_movement_action_mapping.muscle_load.items():
                detailed_load_processor.add_load(functional_movement_action_mapping,
                                                 adaptation_type=base_exercise.adaptation_type,
                                                 movement_action=action,
                                                 training_load_range=base_exercise.power_load,
                                                 reps=reps,
                                                 duration=duration,
                                                 rpe_range=rpe)

    return detailed_load_processor

def process_adaptation_types_no_reps(action_list, rpe_list, duration=None):

    detailed_load_processor = DetailedLoadProcessor()

    functional_movement_factory = FunctionalMovementFactory()
    functional_movement_dict = functional_movement_factory.get_functional_movement_dictionary()
    event_date = datetime.now()

    for action in action_list:
        for rpe in rpe_list:
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
            #for muscle_string, load in functional_movement_action_mapping.muscle_load.items():
            detailed_load_processor.add_load(functional_movement_action_mapping,
                                             adaptation_type=base_exercise.adaptation_type,
                                             movement_action=action,
                                             training_load_range=base_exercise.power_load,
                                             duration=duration,
                                             rpe_range=rpe)

    return detailed_load_processor


# def process_adaptation_types_duration(action_list, duration):
#
#     detailed_load_processor = DetailedLoadProcessor()
#
#     functional_movement_factory = FunctionalMovementFactory()
#     functional_movement_dict = functional_movement_factory.get_functional_movement_dictinary()
#     event_date = datetime.now()
#
#     for action in action_list:
#         duration = duration
#
#         base_exercise = BaseWorkoutExercise()
#         base_exercise.training_type = action.training_type
#         base_exercise.power_load = StandardErrorRange(lower_bound=50, observed_value=75, upper_bound=100)
#         base_exercise.set_adaption_type()
#
#         action.power_load_left = base_exercise.power_load
#         action.power_load_right = base_exercise.power_load
#
#         functional_movement_action_mapping = FunctionalMovementActionMapping(action,
#                                                                              {},
#                                                                              event_date, functional_movement_dict)
#         #for muscle_string, load in functional_movement_action_mapping.muscle_load.items():
#         detailed_load_processor.add_load(functional_movement_action_mapping,
#                                          adaptation_type=base_exercise.adaptation_type,
#                                          movement_action=action,
#                                          training_load_range=base_exercise.power_load,
#                                          duration=duration)
#
#     return detailed_load_processor

def process_adaptation_types_percent_max_hr(action_list, percent_max_hr_list, duration=None):

    detailed_load_processor = DetailedLoadProcessor()

    functional_movement_factory = FunctionalMovementFactory()
    functional_movement_dict = functional_movement_factory.get_functional_movement_dictionary()
    event_date = datetime.now()

    for action in action_list:
        for percent_max_hr in percent_max_hr_list:
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
            #for muscle_string, load in functional_movement_action_mapping.muscle_load.items():
            detailed_load_processor.add_load(functional_movement_action_mapping,
                                             adaptation_type=base_exercise.adaptation_type,
                                             movement_action=action,
                                             training_load_range=base_exercise.power_load,
                                             duration=duration,
                                             percent_max_hr=percent_max_hr)

    return detailed_load_processor


def test_basic_aerobic_training_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_cardiorespiratory])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]

    percent_max_hr_list = [70]

    detailed_load_processor = process_adaptation_types_percent_max_hr(action_list, percent_max_hr_list)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.base_aerobic_training.lowest_value() > 0


def test_anaerobic_threshold_training_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_cardiorespiratory])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]

    percent_max_hr_list = [82]

    detailed_load_processor = process_adaptation_types_percent_max_hr(action_list, percent_max_hr_list)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.anaerobic_threshold_training.lowest_value() > 0


def test_high_intensity_anaerobic_training_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_cardiorespiratory])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]

    percent_max_hr_list = [90]

    detailed_load_processor = process_adaptation_types_percent_max_hr(action_list, percent_max_hr_list)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.high_intensity_anaerobic_training.lowest_value() > 0

def test_stabilization_endurance_from_strength_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_integrated_resistance, TrainingType.strength_endurance])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]
    slow_tempo_list = [a for a in action_list if a.speed == MovementSpeed.slow]

    reps_list = [15]
    rpes = [StandardErrorRange(observed_value=6)]

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    #assert 0 < len(slow_tempo_list)
    assert detailed_load_processor.session_detailed_load.stabilization_endurance.lowest_value() > 0


def test_stabilization_endurance_from_cardio_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_cardiorespiratory])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]
    slow_tempo_list = [a for a in action_list if a.speed == MovementSpeed.slow]

    reps_list = [15]
    rpes = [StandardErrorRange(observed_value=6)]

    detailed_load_processor = process_adaptation_types_no_reps(action_list, rpes, duration=15)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    #assert 0 < len(slow_tempo_list)
    assert detailed_load_processor.session_detailed_load.stabilization_endurance.lowest_value() > 0


def test_stabilization_strength_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_integrated_resistance, TrainingType.strength_endurance])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]

    reps_list = [10]
    rpes = [StandardErrorRange(observed_value=7.5)]

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.stabilization_strength.lowest_value() > 0


def test_stabilization_power_detection():
    # should go to power_explosive_action => Maximal Power, Power, Sustained_power, Speed, Stabilization Power
    action_list = get_filtered_actions([TrainingType.power_action_olympic_lift, TrainingType.power_action_plyometrics])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]
    fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
    explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]

    reps_list = [10]
    rpes = [StandardErrorRange(observed_value=4)]
    #duration = 60

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.stabilization_power.lowest_value() > 0

#
# def test_stabilization_power_from_power_drills_plyometrics():
#
#     action_list = get_filtered_actions([TrainingType.power_drills_plyometrics])
#
#     no_speed_list = [a for a in action_list if a.speed is None]
#     no_resistance_list = [a for a in action_list if a.resistance is None]
#     fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
#     explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]
#
#     reps_list = [10]
#     rpes = [4]
#     #duration = 60
#
#     detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)
#
#     action_list_length = len(action_list)
#     no_speed_length = len(no_speed_list)
#     no_resistance_length = len(no_resistance_list)
#
#     assert detailed_load_processor.session_detailed_load.stabilization_power is not None


def test_functional_strength_from_strength_endurance_strength_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_integrated_resistance, TrainingType.strength_endurance])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]

    reps_list = [10]
    rpes = [StandardErrorRange(observed_value=7.5)]

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.functional_strength.lowest_value() > 0


def test_muscular_endurance_cardio_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_cardiorespiratory])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]

    rpes = [StandardErrorRange(observed_value=6)]

    detailed_load_processor = process_adaptation_types_no_reps(action_list, rpes, duration=300)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.muscular_endurance.lowest_value() > 0


def test_muscular_endurance_strength_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_cardiorespiratory])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]
    slow_tempo_list = [a for a in action_list if a.speed in [MovementSpeed.slow, MovementSpeed.none]]

    rpes = [StandardErrorRange(observed_value=6)]
    reps = [15]

    detailed_load_processor = process_adaptation_types_no_reps(action_list, rpes,duration=300)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    #assert 0 < len(slow_tempo_list)
    assert detailed_load_processor.session_detailed_load.muscular_endurance.lowest_value() > 0


def test_strength_endurance_detection():
    # should go to Stabilization Endurance, Stabilization Strength, Functional Strength, Strength Endurance
    action_list = get_filtered_actions([TrainingType.strength_integrated_resistance, TrainingType.strength_endurance])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]

    reps_list = [10]
    rpes = [StandardErrorRange(observed_value=7.5)]

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.strength_endurance.lowest_value() > 0


def test_speed_detection():
    # should go to power_explosive_action => Maximal Power, Power, Sustained_power, Speed, Stabilization Power
    action_list = get_filtered_actions([TrainingType.power_action_olympic_lift, TrainingType.power_action_plyometrics])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]
    fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
    explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]

    reps_list = [15]
    rpes = [StandardErrorRange(observed_value=4)]
    # duration = 60

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.speed.lowest_value() > 0

#
# def test_speed_from_power_drills_plyometrics():
#     action_list = get_filtered_actions([TrainingType.power_drills_plyometrics])
#
#     no_speed_list = [a for a in action_list if a.speed is None]
#     no_resistance_list = [a for a in action_list if a.resistance is None]
#     fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
#     explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]
#
#     reps_list = [10]
#     rpes = [4]
#     # duration = 60
#
#     detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)
#
#     action_list_length = len(action_list)
#     no_speed_length = len(no_speed_list)
#     no_resistance_length = len(no_resistance_list)
#
#     assert detailed_load_processor.session_detailed_load.speed is not None


def test_sustained_power_from_power_detection():
    # should go to power_explosive_action => Maximal Power, Power, Sustained_power, Speed, Stabilization Power
    action_list = get_filtered_actions([TrainingType.power_action_olympic_lift, TrainingType.power_action_plyometrics])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]
    fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
    explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]

    reps_list = [15]
    rpes = [StandardErrorRange(observed_value=4)]
    duration = 60

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes, duration=60)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.sustained_power.lowest_value() > 0


def test_sustained_power_from_caridio_detection():
    # should go to power_explosive_action => Maximal Power, Power, Sustained_power, Speed, Stabilization Power
    action_list = get_filtered_actions([TrainingType.strength_cardiorespiratory])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]
    fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
    explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]

    reps_list = [15]
    rpes = [StandardErrorRange(observed_value=8)]
    duration = 60

    detailed_load_processor = process_adaptation_types_no_reps(action_list, rpes, duration=60)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.sustained_power.lowest_value() > 0


#
# def test_sustained_power_from_power_drills_plyometrics():
#
#     action_list = get_filtered_actions([TrainingType.power_drills_plyometrics])
#
#     no_speed_list = [a for a in action_list if a.speed is None]
#     no_resistance_list = [a for a in action_list if a.resistance is None]
#     fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
#     explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]
#
#     reps_list = [10]
#     rpes = [4]
#     #duration = 60
#
#     detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)
#
#     action_list_length = len(action_list)
#     no_speed_length = len(no_speed_list)
#     no_resistance_length = len(no_resistance_list)
#
#     assert detailed_load_processor.session_detailed_load.sustained_power is not None


def test_power_detection():
    # should go to power_explosive_action => Maximal Power, Power, Sustained_power, Speed, Stabilization Power
    action_list = get_filtered_actions([TrainingType.power_action_olympic_lift, TrainingType.power_action_plyometrics])

    no_speed_list = [a for a in action_list if a.speed is None]
    no_resistance_list = [a for a in action_list if a.resistance is None]
    fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
    explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]

    reps_list = [15]
    rpes = [StandardErrorRange(observed_value=4)]

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(no_resistance_list)

    assert detailed_load_processor.session_detailed_load.power.lowest_value() > 0


# def test_power_from_power_drills_plyometrics():
#
#     action_list = get_filtered_actions([TrainingType.power_drills_plyometrics])
#
#     no_speed_list = [a for a in action_list if a.speed is None]
#     no_resistance_list = [a for a in action_list if a.resistance is None]
#     fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
#     explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]
#
#     reps_list = [10]
#     rpes = [4]
#     #duration = 60
#
#     detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)
#
#     action_list_length = len(action_list)
#     no_speed_length = len(no_speed_list)
#     no_resistance_length = len(no_resistance_list)
#
#     assert detailed_load_processor.session_detailed_load.power is not None


def test_maximal_power_detection():
    # should go to power_explosive_action => Maximal Power, Power, Sustained_power, Speed, Stabilization Power
    action_list = get_filtered_actions([TrainingType.power_action_olympic_lift, TrainingType.power_action_plyometrics])

    no_speed_list = [a for a in action_list if a.speed is None]
    high_resistance_list = [a for a in action_list if a.resistance in [MovementResistance.high, MovementResistance.max]]
    fast_speed_list = [a for a in action_list if a.speed == MovementSpeed.fast]
    explosive_speed_list = [a for a in action_list if a.speed == MovementSpeed.explosive]

    reps_list = [15]
    rpes = [StandardErrorRange(observed_value=4)]

    detailed_load_processor = process_adaptation_types(action_list, reps_list, rpes)

    action_list_length = len(action_list)
    no_speed_length = len(no_speed_list)
    no_resistance_length = len(high_resistance_list)

    detailed_load_processor.rank_types()

    assert detailed_load_processor.session_detailed_load.maximal_power.lowest_value() > 0

