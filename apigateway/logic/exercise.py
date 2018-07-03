import abc
from enum import Enum, IntEnum
import soreness_and_injury


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


class ExercisePriority(IntEnum):
    present = 0
    high = 1
    avoid = 2


class Exercise(metaclass=abc.ABCMeta):
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

        self.tempo = Tempo.controlled
        self.cues = ""
        self.procedure = ""
        self.goal = ""

    @abc.abstractmethod
    def exercise_phase(self):
        return Phase.inhibit


class InhibitExercise(Exercise):
    def __init__(self):
        Exercise.__init__()

    def exercise_phase(self):
        return Phase.inhibit


class LengthenExercise(Exercise):
    def __init__(self):
        Exercise.__init__()

    def exercise_phase(self):
        return Phase.lengthen


class ActivateExercise(Exercise):
    def __init__(self):
        Exercise.__init__()

    def exercise_phase(self):
        return Phase.activate


class IntegrateExercise(Exercise):
    def __init__(self):
        Exercise.__init__()

    def exercise_phase(self):
        return Phase.integrate


class RecommendedExercise(object):

    def __init__(self):
        self.exercise = None
        self.athlete_id = ""
        self.reps_assigned = 0
        self.sets_assigned = 0
        self.exposures_completed = 0
        self.last_completed_date = None
        self.expire_date_time = None
        self.priority = ExercisePriority.neutral
        self.position_order = 0


class ExerciseRecommendations(object):

    def __init__(self):
        self.recommended_inhibit_exercises = []
        self.recommended_lengthen_exercises = []
        self.recommended_activate_exercises = []
        self.recommended_integrate_exercises = []

    def update(self, soreness_severity, soreness_exercises):
        for soreness_exercise in soreness_exercises:
            exercise_assignment = RecommendedExercise()
            exercise_assignment.exercise = soreness_exercise
            exercise_assignment.priority = \
                self.get_exercise_priority_from_soreness_level(soreness_severity,
                                                               soreness_exercise.exercise_phase())

            # TODO expand to accommodate if exercise already exists or if others already exist
            if isinstance(soreness_exercise, InhibitExercise):
                self.recommended_inhibit_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, LengthenExercise):
                    self.recommended_lengthen_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, ActivateExercise):
                    self.recommended_activate_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, IntegrateExercise):
                    self.recommended_integrate_exercises.append(exercise_assignment)

    def get_exercise_priority_from_soreness_level(self, soreness_level, exercise_phase):

        exercise_priority = ExercisePriority

        if exercise_phase == Phase.inhibit or exercise_phase == Phase.lengthen:

            if soreness_level is None or soreness_level <= 1:
                return exercise_priority.present
            elif 2 <= soreness_level < 4:
                return exercise_priority.high
            else:
                return exercise_priority.avoid

        elif exercise_phase == Phase.activate:

            if soreness_level is None or soreness_level <= 1:
                return exercise_priority.present
            elif soreness_level == 2:
                return exercise_priority.high
            elif soreness_level == 3:
                return exercise_priority.present
            else:
                return exercise_priority.avoid

        elif exercise_phase == Phase.integrate:

            if soreness_level is None or soreness_level <= 3:
                return exercise_priority.present
            else:
                return exercise_priority.avoid

