from datastores.movement_library_datastore import MovementLibraryDatastore, Movement
from models.movement_actions import MovementSpeed, MovementDisplacement, MovementResistance
from models.movement_tags import TrainingType
from logic.calculators import  Calculators


movement_library = MovementLibraryDatastore().get()
all_movements = []
for movement in movement_library.values():
    all_movements.append(Movement.json_deserialise(movement))


def test_ntc_exercises_speed_resistance():
    print(len(all_movements))
    strength_table = {}
    for resistance in MovementResistance:
        resistance_dict = {}
        for speed in MovementSpeed:
            resistance_dict[speed.name] = 0
        strength_table[resistance.name] = resistance_dict

    no_resistance_table = {}
    for displacement in ['min', 'mod', 'large', 'max']:
        displacement_dict = {}
        for speed in ['mod', 'fast', 'explosive']:
            displacement_dict[speed] = 0
        no_resistance_table[displacement] = displacement_dict

    low_resistance_table = {}
    for displacement in ['min', 'mod', 'large', 'max']:
        displacement_dict = {}
        for speed in ['mod', 'fast', 'explosive']:
            displacement_dict[speed] = 0
        low_resistance_table[displacement] = displacement_dict
    strength_count = 0
    plyo_count = 0
    for movement in all_movements:
        if movement.training_type != TrainingType.strength_cardiorespiratory:
        # if movement.training_type in [TrainingType.power_drills_plyometrics, TrainingType.power_action_plyometrics]:
            plyo_count += 1
            if movement.displacement is None or movement.displacement.name in ['none', 'partial_rom', 'full_rom']:
                # print(f"{movement.id}: {movement.displacement.name} ")
                strength_table[movement.resistance.name][movement.speed.name] += 1
            elif movement.resistance.name == 'none':
                no_resistance_table[movement.displacement.name][movement.speed.name] += 1
            elif movement.resistance.name == 'low':
                low_resistance_table[movement.displacement.name][movement.speed.name] += 1
            else:
                print(f"Not found in RPE lookup table: {movement.id}, {movement.displacement.name, movement.resistance.name, movement.speed.name}")
        elif movement.training_type in [TrainingType.power_action_olympic_lift]:
            print(f"olympic action: {movement.id}")
        else:
            if movement.training_type != TrainingType.strength_cardiorespiratory:
                strength_count += 1

    # print(strength_table)
    # print(low_resistance_table)
    # print(no_resistance_table)
    # print(strength_count, plyo_count)

def test_power_med_ball_slams():
    from logic.calculators import Calculators

    movement = movement_library.get('med ball slams')
    movement['actions_for_power'][3]['muscle_action'][0] = 1
    movement = Movement.json_deserialise(movement)
    actions = movement.actions_for_power
    # actions[4].muscle_action

    power = Calculators.power_resistance_exercise(5, actions, duration_per_rep=None)
    assert power is not None


def test_power_kettlebell_swings():
    from logic.workout_processing import WorkoutProcessor
    from models.planned_exercise import PlannedExercise
    from models.exercise import WeightMeasure
    from models.training_volume import Assignment
    workout_processor = WorkoutProcessor()
    exercise = PlannedExercise()
    exercise.weight_measure = WeightMeasure.percent_rep_max
    exercise.weight = Assignment(min_value=60, max_value=70)
    exercise.movement_id = 'alternating dumbbell chest press'
    workout_processor.add_movement_detail_to_planned_exercise(exercise, assignment_type=None)
    movement = movement_library.get(exercise.movement_id)
    movement = Movement.json_deserialise(movement)
    exercise.initialize_from_movement(movement)
    exercise.set_reps_duration()
    workout_processor.set_force_power_weighted(exercise)
    external_weight = workout_processor.get_external_weight(exercise)

    # power = Calculators.power_resistance_exercise(5, actions, duration_per_rep=None)
    # assert power is not None