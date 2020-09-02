import os, json
from models.movement_actions import Movement
from database.NTC.import_exercises import ClientExercise


class ExerciseMovementParser(object):
    def __init__(self):
        self.exercises = self.get_nike_exercise_library()
        self.base_movements = self.get_base_movement_library()
        self.attributes_to_copy = [
            'training_type',
            'bilateral_distribution_of_resistance',
            'resistance',
            'speed',
            'surface_stability',
            'displacement',
            'external_weight_implement',
            'rest_between_reps',
            'rep_tempo',
            'involvement',
            'plane',
            'body_position',
            'upper_body_symmetry'
        ]
        self.movements = []

    @staticmethod
    def get_base_movement_library():
        base_m_l_path = os.path.join(os.path.realpath('../..'), f"apigateway/fml/movement_library_fml.json")
        base_movement_library = read_json(base_m_l_path)
        return base_movement_library

    @staticmethod
    def get_nike_exercise_library():
        print(os.path.realpath(''))
        nike_exercises_path = os.path.join(os.path.realpath(''), "libraries/nike_exercises.json")
        nike_exercises = read_json(nike_exercises_path)
        return nike_exercises

    def merge_nike_exercise_with_base_movement(self):
        # all_movements = {}
        # for movement in movements:
        #     all_movements[movement['base_movement_name']] = movement
        # all_movements = {}
        for exercise in self.exercises:
            exercise = ClientExercise.json_deserialise(exercise)
            base_movement = self.base_movements.get(exercise.base_movement_name)
            if base_movement is None:
                if exercise.training_type.value not in [0, 7, 8]:
                    print(f"{exercise.name}, {exercise.base_movement_name}")
                else:
                    print(f"{exercise.name}, {exercise.training_type.value}")
            else:
                base_movement = Movement.json_deserialise(base_movement)
                movement = Movement(exercise.name, base_movement.name)
                for attribute in self.attributes_to_copy:
                    movement = self.copy_attributes(exercise, base_movement, movement, attribute)
                movement.compound_actions = base_movement.compound_actions
                movement.primary_actions = base_movement.primary_actions
                movement.cardio_action = base_movement.cardio_action
                self.movements.append(movement)
                # all_movements[exercise.name] = movement
        self.write_movements_json()
        print('here')
    @staticmethod
    def copy_attributes(exercise, base_movement, movement, attribute):
        if getattr(exercise, attribute) is not None:
            setattr(movement, attribute, getattr(exercise, attribute))
        else:
            if getattr(base_movement, attribute, None) is not None:
                setattr(movement, attribute, getattr(base_movement, attribute))
            # elif getattr(base_movement, f"typical_{attribute}") is not None:
            #     setattr(movement, attribute, getattr(base_movement, f"typical_{attribute}"))
        return movement

    def write_movements_json(self):
        movements_json = {}
        for movement in self.movements:
            movements_json[movement.id] = movement.json_serialise()

        json_string = json.dumps(movements_json, indent=4)
        file_name = os.path.join(os.path.realpath('../..'), f"apigateway/models/movement_library_nike.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

def read_json(file_name):
    with open(file_name, 'r') as f:
        library = json.load(f)
    return library

if __name__ == '__main__':
    parser = ExerciseMovementParser()
    parser.merge_nike_exercise_with_base_movement()