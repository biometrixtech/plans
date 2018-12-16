from enum import Enum, IntEnum

from models.exercise import Exercise, UnitOfMeasure
from serialisable import Serialisable
from random import shuffle

from utils import format_datetime


class SorenessType(Enum):
    muscle_related = 0
    joint_related = 1


class MuscleSorenessSeverity(IntEnum):
    a_little_tight_sore = 1
    sore_can_move_ok = 2
    limits_movement = 3
    struggling_to_move = 4
    painful_to_move = 5


class JointSorenessSeverity(IntEnum):
    discomfort = 1
    dull_ache = 2
    more_severe_dull_ache = 3
    sharp_pain = 4
    inability_to_move = 5


class Soreness(Serialisable):
    def __init__(self):
        self.body_part = None
        self.historic_soreness_status = None
        self.pain = False
        self.reported_date_time = None
        self.severity = None  # muscle_soreness_severity or joint_soreness_severity
        self.side = None
        self.type = None  # soreness_type
        self.count = 1
        self.streak = 0
        self.daily = True

    def json_serialise(self):
        ret = {
            'body_part': self.body_part.location.value,
            'pain': self.pain,
            'severity': self.severity,
            'side': self.side
        }
        return ret

    def json_serialise_daily_soreness(self):
        ret = {
            'body_part': self.body_part.location.value,
            'pain': self.pain,
            'severity': self.severity,
            'side': self.side,
            'reported_date_time': format_datetime(self.reported_date_time)
        }
        return ret

    def __getitem__(self, item):
        return getattr(self, item)


class InjuryStatus(Enum):
    healthy = 0
    healthy_chronically_injured = 1
    returning_from_injury = 2
    returning_from_chronic_injury = 3


class BodyPartLocation(Enum):
    head = 0
    shoulder = 1
    chest = 2
    abdominals = 3
    hip_flexor = 4
    groin = 5
    quads = 6
    knee = 7
    shin = 8
    ankle = 9
    foot = 10
    outer_thigh = 11
    lower_back = 12
    general = 13
    glutes = 14
    hamstrings = 15
    calves = 16
    achilles = 17
    upper_back_neck = 18


class BodyPart(object):

    def __init__(self, body_part_location, treatment_priority):
        self.location = body_part_location
        self.treatment_priority = treatment_priority
        self.inhibit_exercises = []
        self.lengthen_exercises = []
        self.activate_exercises = []
        self.integrate_exercises = []

    def add_exercises(self, exercise_list, exercise_dict, treatment_priority, randomize=False):

        priority = 1

        keys = list(exercise_dict.keys())

        if randomize:
            shuffle(keys)

        for k in keys:
            if len(exercise_dict[k]) == 0:
                exercise_list.append(AssignedExercise(k, treatment_priority, priority))
            else:
                progression_exercise = AssignedExercise(k, treatment_priority, priority)
                progression_exercise.exercise.progressions = exercise_dict[k]
                exercise_list.append(progression_exercise)
            priority += 1

        return exercise_list

    def add_exercise_phases(self, inhibit, lengthen, activate, randomize=False):

        self.inhibit_exercises = self.add_exercises(self.inhibit_exercises, inhibit,
                                                    self.treatment_priority, randomize)
        self.lengthen_exercises = self.add_exercises(self.lengthen_exercises, lengthen,
                                                     self.treatment_priority, randomize)
        self.activate_exercises = self.add_exercises(self.activate_exercises, activate,
                                                     self.treatment_priority, randomize)


class HistoricSorenessStatus(IntEnum):
    dormant_cleared = 0
    persistent_pain = 1
    persistent_2_pain = 2
    almost_persistent_pain = 3
    almost_persistent_2_pain = 4
    persistent_soreness = 5
    persistent_2_soreness = 6
    almost_persistent_soreness = 7
    almost_persistent_2_soreness = 8
    acute_pain = 9


class HistoricSoreness(Serialisable):

    def __init__(self, body_part_location, side, is_pain):
        self.body_part_location = body_part_location
        self.historic_soreness_status = HistoricSorenessStatus.dormant_cleared
        self.is_pain = is_pain
        self.side = side
        self.streak = 0
        self.streak_start_date = None
        self.average_severity = 0.0
        self.last_reported = ""
        self.ask_acute_pain_question = False
        self.ask_persistent_2_question = False

    def json_serialise(self):
        ret = {
            'body_part_location': self.body_part_location.value,
            'historic_soreness_status': self.historic_soreness_status.value,
            'is_pain': self.is_pain,
            'side': self.side,
            'streak': self.streak,
            'streak_start_date': self.streak_start_date,
            'average_severity': self.average_severity,
            'last_reported': self.last_reported,
            'ask_acute_pain_question': self.ask_acute_pain_question,
            'ask_persistent_2_question': self.ask_persistent_2_question
        }
        return ret


class BodyPartLocationText(object):
    def __init__(self, body_part_location):
        self.body_part_location = body_part_location

    def value(self):
        body_part_text = {'head': 'head',
                          'shoulder': 'shoulder',
                          'chest': 'chest',
                          'abdominals': 'abdominal',
                          'hip_flexor': 'hip',
                          'groin': 'groin',
                          'quads': 'quad',
                          'knee': 'knee',
                          'shin': 'shin',
                          'ankle': 'ankle',
                          'foot': 'foot',
                          'outer_thigh': 'IT band',
                          'lower_back': 'lower back',
                          'general': 'general',
                          'glutes': 'glute',
                          'hamstrings': 'hamstring',
                          'calves': 'calf',
                          'achilles': 'achilles',
                          'upper_back_neck': 'upper back'}

        return body_part_text[self.body_part_location.name]


class AssignedExercise(Serialisable):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0,
                 body_part_location=BodyPartLocation.general, progressions=[]):
        self.exercise = Exercise(library_id)
        self.exercise.progressions = progressions
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