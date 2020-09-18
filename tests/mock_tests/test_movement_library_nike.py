from datastores.movement_library_datastore import MovementLibraryDatastore, Movement
from models.movement_actions import MovementSpeed, MovementDisplacement, MovementResistance
from models.movement_tags import TrainingType


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
