from models.movement_actions import Movement, MovementSpeed, MovementResistance
from models.movement_tags import CardioAction, TrainingType, MovementSurfaceStability, Equipment, PowerAction, PowerDrillAction, StrengthEnduranceAction, StrengthResistanceAction
import os
import json
import pandas as pd


class MovementLibraryParser(object):
    def __init__(self, source):
        self.source = source
        self.movements_pd = None
        self.movements = []

    def load_data(self):
        self.movements_pd = pd.read_csv(f'movement_library_{self.source}.csv', keep_default_na=False, skiprows=1)

        self.movements = []

        for index, row in self.movements_pd.iterrows():
            movement_item = self.parse_row(row)
            if movement_item is not None:
                self.movements.append(movement_item)

        self.write_movements_json()

    def parse_row(self, row):
        if self.is_valid(row, 'id') or self.is_valid(row, 'base_movement_name') or self.is_valid(row, 'fathom_name'):
            # movement = Movement(row['id'], row['soflete_name'])
            if self.is_valid(row, 'id'):
                movement = Movement(row['id'], row['fathom_name'])
            elif self.is_valid(row, 'base_movement_name'):
                movement = Movement(row['base_movement_name'], row['fathom_name'])
            else:
                movement = Movement(row['fathom_name'], row['fathom_name'])


            if self.is_valid(row, 'training_type'):
                movement.training_type = TrainingType[row['training_type']]
            if self.is_valid(row, 'cardio_action'):
                if movement.training_type == TrainingType.strength_cardiorespiratory:
                    movement.cardio_action = CardioAction[row['cardio_action']]
            if self.is_valid(row, 'power_drill_action'):
                movement.power_drill_action = PowerDrillAction[row['power_drill_action']]
            if self.is_valid(row, 'power_action'):
                movement.power_action = PowerAction[row['power_action']]
            if self.is_valid(row, 'strength_endurance_action'):
                movement.strength_endurance_action = StrengthEnduranceAction[row['strength_endurance_action']]
            if self.is_valid(row, 'strength_resistance_action'):
                movement.strength_resistance_action = StrengthResistanceAction[row['strength_resistance_action']]
            # TODO: Possibly add strength_endurance_action and strength_resistance_action

            if self.is_valid(row, 'primary_actions'):
                primary_actions = row['primary_actions'].split(",")
                movement.primary_actions = [action.strip() for action in primary_actions]
            if self.is_valid(row, 'secondary_actions'):
                row['secondary_actions'].replace(", ", ",")
                secondary_actions = row['secondary_actions'].split(",")
                movement.secondary_actions = [action.strip() for action in secondary_actions]

            if self.is_valid(row, 'surface_stability'):
                movement.surface_stability = MovementSurfaceStability[row['surface_stability']]
            if self.is_valid(row, 'external_weight_implement'):
                row['external_weight_implement'].replace(", ", ",")
                external_weight_implement = row['external_weight_implement'].lower().split(",")
                try:
                    movement.external_weight_implement = [Equipment[equipment] for equipment in external_weight_implement]
                except:
                    print('here', external_weight_implement)

            if self.is_valid(row, 'resistance', False):
            # if row.get('resistance') is not None and row['resistance'] != "":
                movement.resistance = self.get_resistance(row['resistance'])
                # movement.resistance = MovementResistance[row['resistance']]
            if self.is_valid(row, 'speed', False):
            # if row.get('speed') is not None and row['speed'] != "":
                movement.speed = self.get_speed(row['speed'])
                # movement.speed = MovementSpeed[row['speed']]

            return movement
        else:
            return None
    @staticmethod
    def get_resistance(resistance):
        if 'resistance' in resistance:
            resistance = resistance.split('_')[0]
        return MovementResistance[resistance]

    @staticmethod
    def get_speed(speed):
        speed_conversion_dict = {
            'no_speed': 'none',
            'speed': 'slow',
            'normal': 'mod',
            'max_speed': 'fast'
        }
        if speed in speed_conversion_dict:
            speed = speed_conversion_dict[speed]
        return MovementSpeed[speed]


    @staticmethod
    def is_valid(row, name, check_none=True):
        if row.get(name) is not None and row[name] != "":
            if check_none:
                if row[name] != "none":
                    return True
            else:
                return True
        return False

    def write_movements_json(self):
        movements_json = {}
        for movement in self.movements:
            movements_json[movement.id] = movement.json_serialise()

        json_string = json.dumps(movements_json, indent=4)
        # file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/movement_library_soflete.json")
        file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/movement_library_{self.source}.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

def read_json(source):
    file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/movement_library_{source}.json")
    with open(file_name, 'r') as f:
        library = json.load(f)
    return library

def write_json(json_data):
    json_string = json.dumps(json_data, indent=4)
    # file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/movement_library_soflete.json")
    file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/movement_library_demo.json")
    print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()


if __name__ == '__main__':
    # sources = ['demo']
    sources = ['demo', 'strength_integrated_resistance']
    for movements_source in sources:
        mov_parser = MovementLibraryParser(movements_source)
        mov_parser.load_data()
    all_data = {}
    for source in sources:
        all_data.update(read_json(source))
    write_json(all_data)
