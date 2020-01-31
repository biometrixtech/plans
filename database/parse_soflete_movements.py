import pandas as pd
from models.workout_program import Movement
from movement_tags import *
import os, json

movements_pd = pd.read_csv('soflete_movements.csv', keep_default_na=False)

movements = []

for index, row in movements_pd.iterrows():
    movement = Movement(row['id'], row['name'])
    movement.name = row['name']
    if row.get('action') is not None and row['action'] != "":
        movement.movement_action = MovementAction[row['action']]
    if row.get('training_type_original') is not None and row['training_type_original'] != "" and row['training_type_original'] != "none":
        movement.training_type = TrainingType[row['training_type_original']]
    if row.get('equipment') is not None and row['equipment'] != "":
        try:
            movement.equipment = Equipment[row['equipment']]
        except KeyError:
            pass
    movements.append(movement)

movements_json = {}
for movement in movements:
    movements_json[movement.id] = movement.json_serialise()

json_string = json.dumps(movements_json, indent=4)
file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/movement_library_soflete.json")
print(f"writing: {file_name}")
f1 = open(file_name, 'w')
f1.write(json_string)
f1.close()

print('here')
