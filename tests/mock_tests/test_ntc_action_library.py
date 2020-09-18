from datastores.action_library_datastore import ActionLibraryDatastore
from models.movement_actions import MovementSpeed, MovementDisplacement, MovementResistance, CompoundAction
from models.movement_tags import TrainingType


action_library = ActionLibraryDatastore().get()
all_actions = []
for compound_action in action_library.values():
    all_actions.append(CompoundAction.json_deserialise(compound_action))

def test_ntc_exercises_speed_resistance():
    print(len(all_actions))
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
    compound_action_count = 0
    actions_count = 0
    for compound_action in all_actions:
        compound_action_count += 1
        if compound_action.training_type != TrainingType.strength_cardiorespiratory:
            for action in compound_action.actions:
                actions_count += 1
                if action.displacement is None or action.displacement.name in ['none', 'partial_rom', 'full_rom']:
                    strength_table[action.resistance.name][action.speed.name] += 1
                else:
                    print(f"Not found in force lookup table: {compound_action.id}, {action.id}")

    # print(strength_table)
    # print(low_resistance_table)
    # print(no_resistance_table)
    # print(actions_count, compound_action_count)
