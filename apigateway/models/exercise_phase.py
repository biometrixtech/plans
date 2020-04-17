from enum import Enum
from models.exercise import AssignedExercise


class ExercisePhaseType(Enum):
    inhibit = 0
    static_stretch = 1
    active_stretch = 2
    dynamic_stretch = 3
    isolated_activate = 4
    static_integrate = 5
    dynamic_integrate = 6

    def get_display_name(self):
        display_names = {
            0: 'FOAM ROLL',
            1: 'STATIC STRETCH',
            2: 'ACTIVE STRETCH',
            3: 'DYNAMIC STRETCH',
            4: 'ACTIVATE',
            5: 'STATIC INTEGRATE',
            6: 'DYNAMIC INTEGRATE'
            }
        return display_names[self.value]


class ExercisePhase(object):
    def __init__(self, phase_type):
        self.type = ExercisePhaseType(phase_type)
        self.name = self.type.name
        self.title = self.type.get_display_name()
        self.exercises = {}

    def json_serialise(self, mobility_api=False, api=False, consolidated=False):
        return {
            "type": self.type.value,
            "name": self.name,
            "title": self.title,
            "exercises": [e.json_serialise(mobility_api=mobility_api, api=api, consolidated=consolidated) for e in self.exercises.values()]
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        exercise_phase = cls(input_dict['type'])
        exercise_phase.exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                    for s in input_dict['exercises']}
        return exercise_phase
