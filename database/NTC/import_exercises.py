import os
import json
import pandas as pd
from models.movement_actions import Movement, MovementSpeed, MovementResistance
from models.movement_tags import TrainingType, MovementSurfaceStability, Equipment, BodyPosition, WeightDistribution

class ClientExercise(object):
    def __init__(self, name):
        self.name = name
        self.base_movement_id = None
        self.base_movement_name = None
        self.client_exercise_name = None

        self.training_type = None
        self.bilateral_distribution_of_resistance = None
        self.resistance = None
        self.speed = None
        self.surface_stability = None
        self.equipment = None
        self.rest_between_reps = None
        self.rep_tempo = None
        self.involvement = None
        self.plane = None
        self.body_position = None
        self.upper_body_symmetry = None

    def json_serialise(self):
        ret = {
            'name': self.name,
            'base_movement_id': self.base_movement_id,
            'base_movement_name': self.base_movement_name,
            'client_exercise_name': self.client_exercise_name,
            'training_type': self.training_type.value if self.training_type is not None else None,
            'bilateral_distribution_of_resistance': self.bilateral_distribution_of_resistance.value if self.bilateral_distribution_of_resistance is not None else None,
            'resistance': self.resistance.value if self.resistance is not None else None,
            'speed': self.speed.value if self.speed is not None else None,
            'surface_stability': self.surface_stability.value if self.surface_stability is not None else None,
            'equipment': self.equipment.value if self.equipment is not None else None,
            'rest_between_reps': self.rest_between_reps,
            'rep_tempo': self.rep_tempo,
            'involvement': self.involvement,
            'plane': self.plane,
            'body_position': self.body_position.value if self.body_position is not None else None,
            'upper_body_symmetry': self.upper_body_symmetry
        }
        return ret


class ExerciseParser(object):
    def __init__(self):
        self.exercise_pd = None
        self.exercises = []
        self.training_type_lookup = {
            'strength_core': 'strength_endurance',
            'strength_action_bw': 'strength_endurance'
        }
        self.equipment_name_loookup = {
            'kettlebell': 'kettlebells'
        }


    def load_data(self, files):
        """

        :param files: list of files to import
        :return:
        """
        all_exercises = []
        for file in files:
            self.exercise_pd = pd.read_csv(f'exercise_to_base_movement/{file}', keep_default_na=False)

            self.exercise_pd.rename(columns={'speed (as rep tempo or as max action pace)': 'speed'}, inplace=True)
            self.exercises = []

            for index, row in self.exercise_pd.iterrows():
                exercise = self.parse_row(row)
                if exercise is not None:
                    self.exercises.append(exercise)
            exercise_json = self.get_exercise_json()
            all_exercises.extend(exercise_json)
        all_movements = list({ex['base_movement_name'] for ex in all_exercises})
        all_movements.sort()


        self.write_json(all_exercises)

    def parse_row(self, row):
        if (row['nike_exercise_name'] is not None and row['nike_exercise_name'] != ''):
            name = row['nike_exercise_name'].strip().lower()
            ex = ClientExercise(name)
            ex.base_movement_name = row['base_movement_name'].strip().lower()
            training_type = self.training_type_lookup.get(row['training_type']) or row['training_type']
            ex.training_type = TrainingType[training_type]
            if self.is_valid(row['bilateral_distribution_of_resistance']):
                if len(row['bilateral_distribution_of_resistance'].split(',')) > 1:
                    row['bilateral_distribution_of_resistance'] = row['bilateral_distribution_of_resistance'].split(',')[0]
                ex.bilateral_distribution_of_resistance = WeightDistribution[row['bilateral_distribution_of_resistance']]
            if self.is_valid(row['resistance']):
                ex.resistance = MovementResistance[row['resistance']]
            if self.is_valid(row['speed']):
                ex.speed = MovementSpeed[row['speed']]
            if self.is_valid(row['rest_between_reps']):
                ex.rest_between_reps = float(row['rest_between_reps'])
            ex.rep_tempo = row['rep_tempo']
            if self.is_valid(row['surface_stability']):
                ex.surface_stability = MovementSurfaceStability[row['surface_stability']]
            ex.involvement = row['involvement']
            ex.plane = row['plane']
            if self.is_valid(row['body_position']):
                ex.body_position = BodyPosition[row['body_position']]
            ex.upper_body_symmetry = row['upper_body_symmetry']
            if self.is_valid(row['external_weight_implement']):
                ex.equipment = Equipment[self.equipment_name_loookup.get(row['external_weight_implement']) or row['external_weight_implement']]
            return ex
        return None

    def get_exercise_json(self):
        return [ex.json_serialise() for ex in self.exercises]

    def write_json(self, all_exercises):
        json_string = json.dumps(all_exercises, indent=4)
        file_name = os.path.join(f"libraries/nike_exercises.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

    @staticmethod
    def is_valid(value):
        if value is not None and value != "":
            return True
        return False


if __name__ == '__main__':
    files = os.listdir('exercise_to_base_movement/')
    ExerciseParser().load_data(files)
    # all_data = []
    # for file in files:
    #     data = pd.read_csv(f"exercise_to_base_movement/{file}")
    #     all_data.append(data)

print('')