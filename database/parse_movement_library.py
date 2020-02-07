from models.movement_actions import Movement
from movement_tags import CardioAction, TrainingType, BodyPosition, Equipment
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
            self.movements.append(movement_item)

        self.write_movements_json()

    def parse_row(self, row):
        movement = Movement(row['id'], row['soflete_name'])

        if row.get('training_type') is not None and row['training_type'] != "" and row['training_type'] != "none":
            movement.training_type = TrainingType[row['training_type']]
            if movement.training_type == TrainingType.strength_cardiorespiratory:
                try:
                    movement.cardio_action = CardioAction[row['cardio_action']]
                except KeyError:
                    print(f"cardio_action: {row['cardio_action']}")
        if row.get('body_position') is not None and row['body_position'] != "" and row['body_position'] != "none":
            movement.body_position = BodyPosition[row['body_position']]

        if row.get('primary_actions') is not None and row["primary_actions"] != "" and row['primary_actions'] != "none":
            primary_actions = row['primary_actions'].split(",")
            movement.primary_actions = [action.strip() for action in primary_actions]
        if row.get('secondary_actions') is not None and row["secondary_actions"] != "" and row['secondary_actions'] != "none":
            row['secondary_actions'].replace(", ", ",")
            secondary_actions = row['secondary_actions'].split(",")
            movement.secondary_actions = [action.strip() for action in secondary_actions]
        if row.get('equipment') is not None and row['equipment'] != "":
            try:
                movement.equipment = Equipment[row['equipment']]
            except KeyError:
                print(f"equipment: {row['equipment']}")
        return movement

    def write_movements_json(self):
        movements_json = {}
        for movement in self.movements:
            movements_json[movement.id] = movement.json_serialise()

        json_string = json.dumps(movements_json, indent=4)
        file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/movement_library_{self.source}.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()


if __name__ == '__main__':
    sources = ['soflete']
    for movements_source in sources:
        mov_parser = MovementLibraryParser(movements_source)
        mov_parser.load_data()
