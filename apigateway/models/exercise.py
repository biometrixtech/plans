import datetime
from enum import IntEnum, Enum
from serialisable import Serialisable
from models.soreness import BodyPartLocation
from utils import format_datetime


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


class AssignedExercise(Serialisable):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0,
                 body_part_location=BodyPartLocation.general):
        self.exercise = Exercise(library_id)
        self.body_part_priority = body_part_priority
        self.body_part_exercise_priority = body_part_exercise_priority
        self.body_part_soreness_level = body_part_soreness_level
        self.body_part_location = body_part_location
        self.athlete_id = ""
        self.reps_assigned = 0
        self.sets_assigned = 0
        self.expire_date_time = None
        self.position_order = 0
        self.goal_text = ""

    '''
    def soreness_priority(self):
        return ExercisePriority.neutral
    '''
    def duration(self):
        if self.exercise.unit_of_measure.name == "count":
            if not self.exercise.bilateral:
                return self.exercise.seconds_per_rep * self.reps_assigned * self.sets_assigned
            else:
                return (self.exercise.seconds_per_rep * self.reps_assigned * self.sets_assigned) * 2
        elif self.exercise.unit_of_measure.name == "seconds":
            if not self.exercise.bilateral:
                return self.exercise.seconds_per_set * self.sets_assigned
            else:
                return (self.exercise.seconds_per_set * self.sets_assigned) * 2
        else:
            return None
    def __setattr__(self, name, value):
        if name == "unit_of_measure" and not isinstance(value, UnitOfMeasure):
            value = UnitOfMeasure[value]
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {'name': self.exercise.name,
               'display_name': self.exercise.display_name,
               'library_id': self.exercise.id,
               'description': self.exercise.description,
               'youtube_id': self.exercise.youtube_id,
               'bilateral': self.exercise.bilateral,
               'seconds_per_rep': self.exercise.seconds_per_rep,
               'seconds_per_set': self.exercise.seconds_per_set,
               'unit_of_measure': self.exercise.unit_of_measure.name,
               'position_order': self.position_order,
               'reps_assigned': self.reps_assigned,
               'sets_assigned': self.sets_assigned,
               'seconds_duration': self.duration(),
               'goal_text': self.goal_text
              }
        return ret


class CompletedExercise(Serialisable):

    def __init__(self, athlete_id, exercise_id, event_date):
        self.athlete_id = athlete_id
        self.exercise_id = exercise_id
        self.event_date = event_date

    def json_serialise(self):
        ret = {'athlete_id': self.athlete_id,
               'exercise_id': self.exercise_id,
               'event_date': format_datetime(self.event_date),
               }
        return ret


class CompletedExerciseSummary(Serialisable):

    def __init__(self, athlete_id, exercise_id, exposures):
        self.athlete_id = athlete_id
        self.exercise_id = exercise_id
        self.exposures = exposures

    def json_serialise(self):
        ret = {'athlete_id': self.athlete_id,
               'exercise_id': self.exercise_id,
               'exposures': self.exposures,
               }
        return ret
