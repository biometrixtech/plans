from serialisable import Serialisable


class WorkoutProgramModule(Serialisable):
    def __init__(self):
        self.provider_id = None
        self.program_id = None
        self.program_module_id = None
        self.workout_sections = []

    def json_serialise(self):
        ret = {
            'provider_id': self.provider_id,
            'program_id': self.program_id,
            'program_module_id': self.program_module_id,
            'workout_sections': [w.json_serialise() for w in self.workout_sections]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout_program_module = cls()
        workout_program_module.provider_id = input_dict.get('provider_id')
        workout_program_module.program_id = input_dict.get('program_id')
        workout_program_module.program_module_id = input_dict.get('program_module_id')
        workout_program_module.workout_sections = [WorkoutSection.json_deserialise(workout_section) for workout_section in input_dict.get('workout_sections', [])]

        return workout_program_module


class WorkoutSection(Serialisable):
    def __init__(self):
        self.name = ''
        self.duration_seconds = None
        self.workout_section_type = None
        self.difficulty = None
        self.intensity_pace = None
        self.exercises = []

    def json_serialise(self):
        ret = {
            'name': self.name,
            'duration_seconds': self.duration_seconds,
            'workout_section_type': self.workout_section_type,
            'difficulty': self.difficulty,
            'intensity_pace': self.intensity_pace,
            'exercises': [e.json_serialise() for e in self.exercises]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout_section = cls()
        workout_section.name = input_dict.get('name')
        workout_section.duration_seconds = input_dict.get('duration_seconds')
        workout_section.workout_section_type = input_dict.get('workout_section_type')
        workout_section.difficulty = input_dict.get('difficulty')
        workout_section.intensity_pace = input_dict.get('intensity_pace')
        workout_section.exercises = [WorkoutExercise.json_deserialise(workout_exercise) for workout_exercise
                                                   in input_dict.get('exercises', [])]

        return workout_section


class WorkoutExercise(Serialisable):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.weight_in_lbs = None
        self.weight_type = None
        self.sets = 0
        self.reps_per_set = 0
        self.reps_unit = None
        self.intensity_pace = None

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'weight_in_lbs': self.weight_in_lbs,
            'weight_type': self.weight_type,
            'sets': self.sets,
            'reps_per_set': self.reps_per_set,
            'reps_unit': self.reps_unit,
            'intensity_pace': self.intensity_pace
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        exercise = cls()
        exercise.id = input_dict.get('id', '')
        exercise.name = input_dict.get('name', '')
        exercise.weight_in_lbs = input_dict.get('weight_in_lbs')
        exercise.weight_type = input_dict.get('weight_type')
        exercise.sets = input_dict.get('sets', 0)
        exercise.reps_per_set = input_dict.get('reps_per_set', 0)
        exercise.reps_unit = input_dict.get('reps_unit')
        exercise.intensity_pace = input_dict.get('intensity_pace')

        return exercise
