from enum import Enum, IntEnum


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


class Exercise(object):
    def __init__(self):
        self.name = ""
        self.body_parts_targeted = []
        self.min_reps = None
        self.max_reps = None
        self.min_sets = None
        self.max_sets = None
        self.bilateral = False
        self.progression_interval = 0
        self.exposure_target = 0
        self.unit_of_measure = UnitOfMeasure.seconds
        self.seconds_rest_between_sets = 0
        self.time_per_set = 0
        self.progresses_to = None   # another exercise if it progresses to another

        self.technical_difficulty = TechnicalDifficulty.beginner
        self.program_type = ProgramType.comprehensive_warm_up
        self.exercise_phase = Phase.inhibit

        self.tempo = Tempo.controlled
        self.cues = ""
        self.procedure = ""
        self.goal = ""


class AssignedExercise(Exercise):

    def __init__(self):
        Exercise.__init__()
        self.athlete_id = ""
        self.reps_assigned = 0
        self.sets_assigned = 0
        self.exposures_completed = 0
        self.last_completed_date = None
        self.expire_date_time = None
