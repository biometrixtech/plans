import os
import json
import pandas as pd

if __package__ is None or __package__ == '':
    import sys
    working_dir = os.path.realpath('..') + "/apigateway"
    sys.path.append(working_dir)

from models.exercise import Exercise

class ExerciseLibraryParser(object):
    def __init__(self):
        self.exercises_pd = None
        self.exercises_fathom = []
        self.exercises_soflete = []
        self.body_parts_fathom = {}
        self.body_parts_soflete = {}

    def load_data(self):
        self.exercises_pd = pd.read_csv('Exercise_Library.tsv', sep='\t', keep_default_na=False, skiprows=1)
        # self.body_parts_pd = pd.read_csv('Body_Parts.tsv', sep='\t', keep_default_na=False, skiprows=1)
        fathom_exercises_pd = self.exercises_pd[self.exercises_pd[f'present_in_fathom_mapping_logic'] == 'x']

        for index, row in fathom_exercises_pd.iterrows():
            exercise_item = self.parse_row(row, source='fathom')
            self.exercises_fathom.append(exercise_item)
        self.write_exercise_json('fathom')
        self.write_body_parts_json('fathom')

        soflete_exercises_pd = self.exercises_pd[self.exercises_pd['present_in_soflete_mapping_logic'] == 'x']
        for index, row in soflete_exercises_pd.iterrows():
            exercise_item = self.parse_row(row, source='soflete')
            self.exercises_soflete.append(exercise_item)
        self.write_exercise_json('soflete')
        self.write_body_parts_json('soflete')

    def parse_row(self, row, source):
        if source == 'soflete':
            exercise_item = Exercise(str(row['soflete_id']))
        else:
            exercise_item = Exercise(str(row['id']))
        exercise_item.display_name = row['display_name']
        exercise_item.name = row['name']
        if row["min_sets"] in ["-", ""]:
            exercise_item.min_sets = 0
        else:
            exercise_item.min_sets = int(row['min_sets'])
        if row["max_sets"] in ["-", ""]:
            exercise_item.max_sets = 0
        else:
            exercise_item.max_sets = int(row["max_sets"])
        if row["min_reps"] in ["-", ""]:
            exercise_item.min_reps = None
        else:
            exercise_item.min_reps = int(row["min_reps"])
        if row["max_reps"] in ["-", ""]:
            exercise_item.max_reps = None
        else:
            exercise_item.max_reps = int(row["max_reps"])
        exercise_item.bilateral = (row["bilateral"] == "Y")
        if row["progression_intervals"] in ["-", ""]:
            exercise_item.progression_interval = 0
        else:
            exercise_item.progression_interval = int(row["progression_intervals"])
        if row["exposure_target"] in ["-", ""]:
            exercise_item.exposure_target = 0
        else:
            exercise_item.exposure_target = int(row["exposure_target"])
        if row["exposure_minimum"] in ["-", ""]:
            exercise_item.exposure_minimum = 0
        else:
            exercise_item.exposure_minimum = int(row["exposure_minimum"])
        exercise_item.unit_of_measure = row["unit_of_measure"]
        if row["rest_between_sets"] in ["-", ""]:
            exercise_item.seconds_rest_between_sets = 0
        else:
            exercise_item.seconds_rest_between_sets = int(row["rest_between_sets"])
        if row["time_per_set"] in ["-", ""]:
            exercise_item.seconds_per_set = None
        else:
            exercise_item.seconds_per_set = int(row["time_per_set"])
        if row["time_per_rep"] in ["-", ""]:
            exercise_item.seconds_per_rep = None
        else:
            exercise_item.seconds_per_rep = int(row["time_per_rep"])
        exercise_item.progresses_to = row["progress_to"]
        exercise_item.technical_difficulty = row["technical_difficulty"]
        exercise_item.equipment_required = row["equipment_required"].split(';')
        exercise_item.description = row["description"]
        body_parts = self.__getattribute__(f"body_parts_{source}")
        try:
            mapped_body_parts = json.loads(row['muscle_group_joint'])
            for key, value in mapped_body_parts.items():
                if key not in body_parts.keys():
                    body_part = dict()
                    body_part['id'] = value
                    body_part['name'] = key
                    body_part['inhibit'] = []
                    body_part['static_lengthen'] = []
                    body_part['active_lengthen'] = []
                    body_part['dynamic_lengthen'] = []
                    body_part['activate'] = []
                    body_part['static_integrate'] = []
                    body_part['dynamic_integrate'] = []
                    body_parts[key] = body_part
                body_part = body_parts[key]
                if row['inhibit'] == 'x':
                    body_part['inhibit'].append(row['id'])
                elif row['static_lengthen'] == 'x':
                    body_part['static_lengthen'].append(row['id'])
                elif row['active_lengthen'] == 'x':
                    body_part['active_lengthen'].append(row['id'])
                elif row['dynamic_lengthen'] == 'x':
                    body_part['dynamic_lengthen'].append(row['id'])
                elif row['activate'] == 'x':
                    body_part['activate'].append(row['id'])
                elif row['static_integrate'] == 'x':
                    body_part['static_integrate'].append(row['id'])
                elif row['dynamic_integrate'] == 'x':
                    body_part['dynamic_integrate'].append(row['id'])
        except:
            pass

        return exercise_item

    def write_exercise_json(self, source):
        exercise_list = self.__getattribute__(f"exercises_{source}")
        exercises_json = []
        for exercise_item in exercise_list:
            exercises_json.append(exercise_item.json_serialise())
        json_string = json.dumps(exercises_json, indent=4)
        file_name = os.path.join(os.path.realpath('..'), f'apigateway/models/exercise_library_{source}.json')
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

    def write_body_parts_json(self, source):
        body_parts = self.__getattribute__(f"body_parts_{source}")
        body_parts_json = []
        for key, value in body_parts.items():
            body_parts_json.append(value)
        json_string = json.dumps(body_parts_json, indent=4)
        file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/body_part_mapping_{source}.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()


if __name__ == '__main__':
    ex_parser = ExerciseLibraryParser()
    ex_parser.load_data()
