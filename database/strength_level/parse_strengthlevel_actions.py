"""
Need to download Strength_Level_Exercise_Library.numbers and export to csv before running this file
"""

import database.NTC.set_up_config

import os
import json
import pandas as pd
from models.workout_program import WorkoutExercise
from logic.workout_processing import WorkoutProcessor
from models.movement_actions import CompoundAction


def read_json(file_name):
    with open(file_name, 'r') as f:
        library = json.load(f)
    return library

class ExerciseParser(object):
    def __init__(self):
        self.exercise_pd = None

    @staticmethod
    def get_base_movement_library():
        base_m_l_path = os.path.join(os.path.realpath('../..'), f"apigateway/fml/movement_library_fml.json")
        base_movement_library = read_json(base_m_l_path)
        return base_movement_library

    @staticmethod
    def get_action_library():
        action_library_path = os.path.join(os.path.realpath('../..'), f"apigateway/models/actions_library.json")
        action_library = read_json(action_library_path)
        return action_library

    def load_data(self, file_name):
        """

        :param files: list of files to import
        :return:
        """
        self.exercise_pd = pd.read_csv(f'{file_name}', keep_default_na=False)

        exercises = []
        base_movement_library = self.get_base_movement_library()
        action_library = self.get_action_library()
        workout_processor = WorkoutProcessor()
        exercise_joint_actions = {}


        for index, row in self.exercise_pd.iterrows():
            if (row['strength_level_exercise_name'] is not None and row['strength_level_exercise_name'] != ''):
                exercise = WorkoutExercise()
                exercise_name = row['strength_level_exercise_name'].strip().lower()
                exercise.name = exercise_name
                base_movement_name = row['base_movement_name'].strip().lower()
                if base_movement_name == "":
                    print(f"base movement not defined: {exercise_name}")
                    continue
                base_movement = base_movement_library.get(base_movement_name)
                if base_movement is not None:
                    exercises.append(exercise)
                    for compound_action_id in base_movement['compound_actions']:
                        compound_action_json = action_library.get(compound_action_id)
                        if compound_action_json is not None:
                            compound_action = CompoundAction.json_deserialise(compound_action_json)
                            exercise.compound_actions.append(compound_action)
                        else:
                            print(f'compound_action not found: {exercise_name.name}')
                else:
                    print(f'base_movement not found: {exercise_name}')
        for exercise in exercises:
            ex_name = exercise.name
            if 'lat pull' in ex_name:
                print('here')
            exercise_joint_actions[ex_name] = {}
            prime_movers = workout_processor.get_prime_movers_for_ex(exercise)
            exercise_joint_actions[ex_name]["prime_movers"] = ",".join([str(ex) for ex in prime_movers['first_prime_movers']])
            exercise_joint_actions[ex_name]["second_prime_movers"] = ",".join([str(ex) for ex in prime_movers['second_prime_movers']])
            exercise_joint_actions[ex_name]["third_prime_movers"] = ",".join([str(ex) for ex in prime_movers['third_prime_movers']])
            exercise_joint_actions[ex_name]["fourth_prime_movers"] = ",".join([str(ex) for ex in prime_movers['fourth_prime_movers']])
            exercise_joint_actions[ex_name]['exercise'] = ex_name

        exercises_pd = pd.DataFrame(exercise_joint_actions.values())
        exercises_pd.to_csv('strengthlevel_primemovers.csv', index=False)


if __name__ == '__main__':
    ExerciseParser().load_data('Strength_Level_Exercise_Library.csv')