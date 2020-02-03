from models.workout_program import Movement
from movement_tags import MovementAction, TrainingType, BodyPosition, Equipment
import os
import json
import pandas as pd


class MovementLibraryParser(object):
    def __init__(self, source):
        self.source = source
        self.movements_pd = None
        self.movements = []

    def load_data(self):
        self.movements_pd = pd.read_csv(f'movement_library_{self.source}.csv', keep_default_na=False)

        self.movements = []

        for index, row in self.movements_pd.iterrows():
            movement_item = self.parse_row(row)
            self.movements.append(movement_item)

        self.write_movements_json()

    def parse_row(self, row):
        movement = Movement(row['id'], row['name'])
        movement.name = row['name']
        if row.get('action') is not None and row['action'] != "":
            movement.movement_action = MovementAction[row['action']]
        if row.get('training_type_original') is not None and row['training_type_original'] != "" and row['training_type_original'] != "none":
            movement.training_type = TrainingType[row['training_type_original']]
        if row.get('body_position') is not None and row['body_position'] != "" and row['body_position'] != "none":
            movement.body_position = BodyPosition[row['body_position']]
        if row.get('equipment') is not None and row['equipment'] != "":
            try:
                movement.equipment = Equipment[row['equipment']]
            except KeyError:
                pass
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
