from models.movement_actions import Movement, MovementSpeed, MovementResistance
from models.movement_tags import CardioAction, TrainingType, MovementSurfaceStability, Equipment, PowerAction, PowerDrillAction, StrengthEnduranceAction, StrengthResistanceAction, WeightDistribution
import os
import json
import pandas as pd


class MovementLibraryParser(object):
    def __init__(self, source):
        self.source = source
        self.movements_pd = None
        self.movements = []

    def load_data(self, alt_movement_id):
        #self.movements_pd = pd.read_csv(f'movement_library_{self.source}.csv', keep_default_na=False, skiprows=1)
        self.movements_pd = pd.read_csv(f'fml/{self.source}.csv', keep_default_na=False)

        self.movements = []

        for index, row in self.movements_pd.iterrows():
            movement_item = self.parse_row(row, alt_movement_id)
            if movement_item is not None:
                alt_movement_id += 1
                self.movements.append(movement_item)

        self.write_movements_json()

        return alt_movement_id

    def parse_row(self, row, alt_movement_id):
        if self.is_valid(row, 'compound_actions') and (self.is_valid(row, 'base_movement_id') or self.is_valid(row, 'base_movement_name')):
            if self.is_valid(row, 'base_movement_id') and self.is_valid(row, 'base_movement_name'):
                base_movement_name = row['base_movement_name']
                base_movement_name = base_movement_name.lower().strip()
                movement = Movement(row['base_movement_id'], base_movement_name)
            elif self.is_valid(row, 'base_movement_name'):
                base_movement_name = row['base_movement_name']
                base_movement_name = base_movement_name.lower().strip()
                movement = Movement(str(alt_movement_id), base_movement_name)
            else:
                movement = Movement(str(alt_movement_id), "ERROR")
                print('error!')

            if self.is_valid(row, 'compound_actions'):
                compound_actions = row['compound_actions'].split(",")
                movement.compound_actions = [action.strip() for action in compound_actions]

            if self.is_valid(row, 'typical_training_type'):
                movement.training_type = self.get_training_type(row['typical_training_type'])
            if self.is_valid(row, 'cardio_action'):
                if movement.training_type == TrainingType.strength_cardiorespiratory:
                    movement.cardio_action = CardioAction[row['cardio_action']]

            if self.is_valid(row, 'typical_bilateral_distribution_of_resistance'):
                movement.bilateral_distribution_of_resistance = WeightDistribution[row['typical_bilateral_distribution_of_resistance']]

            if self.is_valid(row, 'typical_surface_stability'):
                movement.surface_stability = MovementSurfaceStability[row['typical_surface_stability']]

            if self.is_valid(row, 'typical_eligible_external_weight_implement'):
                row['typical_eligible_external_weight_implement'].replace(", ", ",")
                external_weight_implement = row['typical_eligible_external_weight_implement'].lower().split(",")
                try:
                    movement.external_weight_implement = [Equipment[equipment] for equipment in external_weight_implement]
                except:
                    print('here', external_weight_implement)

            if self.is_valid(row, 'typical_resistance', False):
                movement.resistance = self.get_resistance(row['typical_resistance'])
            if self.is_valid(row, 'typical_speed', False):
                movement.speed = self.get_speed(row['typical_speed'])

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
        # speed_conversion_dict = {
        #     'no_speed': 'none',
        #     'speed': 'slow',
        #     'normal': 'mod',
        #     'max_speed': 'fast'
        # }
        # if speed in speed_conversion_dict:
        #     speed = speed_conversion_dict[speed]
        if 'speed' in speed:
            speed = speed.split('_')[0]
        elif speed == "low":
            speed = "slow"
        return MovementSpeed[speed]


    @staticmethod
    def get_training_type(training_type):
        if training_type in ['strength_core','strength_action_bw']:
            training_type_value = TrainingType.strength_endurance
        else:
            training_type_value = TrainingType[training_type]

        return training_type_value

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
            movements_json[movement.name] = movement.json_serialise()

        json_string = json.dumps(movements_json, indent=4)
        file_name = os.path.join(os.path.realpath('..'), f"apigateway/fml/movement_library_{self.source}.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

def read_json(source):
    file_name = os.path.join(os.path.realpath('..'), f"apigateway/fml/movement_library_{source}.json")
    with open(file_name, 'r') as f:
        library = json.load(f)
    return library

def write_json(json_data):
    json_string = json.dumps(json_data, indent=4)
    file_name = os.path.join(os.path.realpath('..'), f"apigateway/fml/movement_library_fml.json")
    print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()


if __name__ == '__main__':
    # sources = ['demo']
    sources = ["Base Movements - BW Strength-Base Movements strength_action_bw, strength_core, strength_integrated_resistance",
               "Base Movements - Strength Int. Resistance-Base Movements strength_action_bw, strength_core, strength_integrated_resistance",
               "Base Movements Cardio-Base Movements strength_cardiorespiratory",
               "Base Movements Power-Base Movements strength_action_bw, strength_core, strength_integrated_resistance"
               ]
    #sources = ['demo', 'strength_integrated_resistance']
    alt_movement_id = 1
    for movements_source in sources:
        mov_parser = MovementLibraryParser(movements_source)
        alt_movement_id = mov_parser.load_data(alt_movement_id)
    all_data = {}
    for source in sources:
        all_data.update(read_json(source))
    write_json(all_data)
