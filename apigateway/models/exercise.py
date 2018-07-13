import datetime
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
        # self.body_parts_targeted = []
        self.min_reps = None
        self.max_reps = None
        self.min_sets = None
        self.max_sets = None
        self.bilateral = False
        self.progression_interval = 0
        self.exposure_target = 0
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

    def json_serialise(self):
        ret = {'library_id': self.id,
               'name': self.name,
               'min_sets': self.min_sets,
               'max_sets': self.max_sets,
               'min_reps': self.min_reps,
               'max_reps': self.max_reps,
               'bilateral': self.bilateral,
               'progression_interval': self.progression_interval,
               'exposure_target': self.exposure_target,
               'unit_of_measure': self.unit_of_measure,
               'seconds_rest_between_sets': self.seconds_rest_between_sets,
               'time_per_set': self.seconds_per_set,
               'time_per_rep': self.seconds_per_rep,
               'progresses_to': self.progresses_to,
               'technical_difficulty': self.technical_difficulty,
               'equipment_required': self.equipment_required
         }
        return ret


class AssignedExercise(Serialisable):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0):
        self.exercise = Exercise(library_id)
        self.body_part_priority = body_part_priority
        self.body_part_exercise_priority = body_part_exercise_priority
        self.body_part_soreness_level = body_part_soreness_level

        self.athlete_id = ""
        self.reps_assigned = 0
        self.sets_assigned = 0
        self.expire_date_time = None
        self.position_order = 0

    '''
    def soreness_priority(self):
        return ExercisePriority.neutral
    '''
    def duration(self):
        if self.exercise.unit_of_measure == "count":
            if not self.exercise.bilateral:
                return self.exercise.seconds_per_rep * self.reps_assigned * self.sets_assigned
            else:
                return (self.exercise.seconds_per_rep * self.reps_assigned * self.sets_assigned) * 2
        elif self.exercise.unit_of_measure == "seconds":
            if not self.exercise.bilateral:
                return self.exercise.seconds_per_set * self.sets_assigned
            else:
                return (self.exercise.seconds_per_set * self.sets_assigned) * 2
        else:
            return None

    def json_serialise(self):
        ret = {'name': self.exercise.name,
               'library_id': self.exercise.id,
               'bilateral': self.exercise.bilateral,
               # 'seconds_per_rep': self.exercise.seconds_per_rep,
               # 'seconds_per_set': self.exercise.seconds_per_set,
               'unit_of_measure': self.exercise.unit_of_measure,
               'position_order': self.position_order,
               'reps_assigned': self.reps_assigned,
               'sets_assigned': self.sets_assigned,
               'seconds_duration': self.duration()
              }
        return ret


class ExerciseDeserialiser(object):

    def get_assigned_exercise(self, json_data):
        assigned_exercise = AssignedExercise(json_data["library_id"])
        assigned_exercise.exercise.name = json_data["name"]
        assigned_exercise.exercise.bilateral = json_data["bilateral"]
        assigned_exercise.exercise.seconds_per_rep = json_data["seconds_per_rep"]
        assigned_exercise.exercise.seconds_per_set = json_data["seconds_per_set"]
        assigned_exercise.exercise.unit_of_measure = json_data["unit_of_measure"]
        assigned_exercise.position_order = json_data["position_order"]
        assigned_exercise.reps_assigned = json_data["reps_assigned"]
        assigned_exercise.sets_assigned = json_data["sets_assigned"]
        return assigned_exercise

class CompletedExercise(object):

    def __init__(self, athlete_id, exercise_id):
        self.athlete_id = athlete_id
        self.exercise_id = exercise_id
        self.exposures_completed = 0
        self.last_completed_date = None

    def increment(self):
        self.exposures_completed = self.exposures_completed + 1
        self.last_completed_date = datetime.date.today()