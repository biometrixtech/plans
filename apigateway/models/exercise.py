from enum import IntEnum, Enum
from serialisable import Serialisable


class TechnicalDifficulty(IntEnum):
    beginner = 0
    intermediate = 1
    advanced = 2


class ProgramType(Enum):
    comprehensive_warm_up = 0
    targeted_warm_up = 1
    comprehensive_recovery = 2
    targeted_recovery = 3
    long_term_recovery = 4
    corrective_exercises = 5


class Phase(IntEnum):
    inhibit = 0
    lengthen = 1
    activate = 2
    integrate = 3


class UnitOfMeasure(Enum):
    seconds = 0
    count = 1
    yards = 2


class Tempo(Enum):
    controlled = 0


'''Deprecated
class ExercisePriority(IntEnum):
    present = 0
    high = 1
    avoid = 2
'''


class Exercise(Serialisable):
    def __init__(self, library_id):
        self.id = library_id
        self.name = ""
        self.display_name = ""
        self.youtube_id = ""
        self.description = ""
        # self.body_parts_targeted = []
        self.min_reps = None
        self.max_reps = None
        self.min_sets = None
        self.max_sets = None
        self.bilateral = False
        self.progression_interval = 0
        self.exposure_target = 0
        self.exposure_minimum = 0
        self.unit_of_measure = UnitOfMeasure.seconds
        self.seconds_rest_between_sets = 0
        self.seconds_per_set = 0
        self.seconds_per_rep = 0
        self.progressions = []
        self.progresses_to = None
        self.technical_difficulty = TechnicalDifficulty.beginner
        self.program_type = ProgramType.comprehensive_warm_up

        self.tempo = Tempo.controlled
        self.cues = ""
        self.procedure = ""
        self.goal = ""
        self.equipment_required = None

    def __setattr__(self, name, value):
        if name == "unit_of_measure" and not isinstance(value, UnitOfMeasure):
            value = UnitOfMeasure[value]
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {'library_id': self.id,
               'name': self.name,
               'display_name': self.display_name,
               'description': self.description,
               'youtube_id': self.youtube_id,
               'min_sets': self.min_sets,
               'max_sets': self.max_sets,
               'min_reps': self.min_reps,
               'max_reps': self.max_reps,
               'bilateral': self.bilateral,
               'progression_interval': self.progression_interval,
               'exposure_target': self.exposure_target,
               'exposure_minimum': self.exposure_minimum,
               'unit_of_measure': self.unit_of_measure.name,
               'seconds_rest_between_sets': self.seconds_rest_between_sets,
               'time_per_set': self.seconds_per_set,
               'time_per_rep': self.seconds_per_rep,
               'progresses_to': self.progresses_to,
               'technical_difficulty': self.technical_difficulty,
               'equipment_required': self.equipment_required
         }
        return ret


