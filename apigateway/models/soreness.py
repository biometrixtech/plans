from enum import Enum, IntEnum

from models.exercise import Exercise, UnitOfMeasure
from serialisable import Serialisable
from random import shuffle

from utils import format_datetime, parse_datetime, format_date, parse_date


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


class BaseSoreness(object):
    def __init__(self):
        self.historic_soreness_status = HistoricSorenessStatus.dormant_cleared

    def is_acute_pain(self):
        if (self.historic_soreness_status is not None and (self.historic_soreness_status == HistoricSorenessStatus.acute_pain or
                                                           self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain_acute)):
            return True
        else:
            return False

    def is_persistent_soreness(self):
        if (self.historic_soreness_status is not None and (self.historic_soreness_status == HistoricSorenessStatus.persistent_soreness or
                                                           self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_soreness)):
            return True
        else:
            return False

    def is_persistent_pain(self):
        if (self.historic_soreness_status is not None and (self.historic_soreness_status == HistoricSorenessStatus.persistent_pain or
                                                           self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain)):
            return True
        else:
            return False

    def is_dormant_cleared(self):
        if (self.historic_soreness_status is None or
                self.historic_soreness_status == HistoricSorenessStatus.dormant_cleared or
                self.historic_soreness_status == HistoricSorenessStatus.almost_acute_pain or
                self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain or
                self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_soreness):
            return True
        else:
            return False


class Soreness(BaseSoreness, Serialisable):
    def __init__(self):
        super().__init__()
        self.body_part = None
        self.historic_soreness_status = None
        self.pain = False
        self.reported_date_time = None
        self.severity = None  # muscle_soreness_severity or joint_soreness_severity
        self.movement = None
        self.side = None
        self.type = None  # soreness_type
        self.count = 1
        self.streak = 0
        self.first_reported = None
        self.daily = True

    @classmethod
    def json_deserialise(cls, input_dict):
        soreness = cls()
        soreness.body_part = BodyPart(BodyPartLocation(input_dict['body_part']), None)
        soreness.pain = input_dict.get('pain', False)
        soreness.severity = input_dict['severity']
        soreness.movement = input_dict.get('movement', None)
        soreness.side = input_dict.get('side', None)
        soreness.first_reported = input_dict.get('first_reported', None)
        # if input_dict.get('first_reported', None) is not None:
        #     soreness.first_reported = parse_date(input_dict['first_reported'])
        if input_dict.get('reported_date_time', None) is not None:
            soreness.reported_date_time = parse_datetime(input_dict['reported_date_time'])
        return soreness

    def __hash__(self):
        return hash((self.body_part.location, self.side))

    def __eq__(self, other):
        return ((self.body_part.location == other.body_part.location,
                 self.side == other.side))

    '''deprecated
    def is_dormant_cleared(self):
        try:
            if (self.historic_soreness_status is None or
               self.historic_soreness_status == HistoricSorenessStatus.dormant_cleared or
                self.historic_soreness_status == HistoricSorenessStatus.almost_acute_pain or 
                self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain or
                self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_soreness):
                return True
            else:
                return False
        except AttributeError:
            return False
    '''

    def json_serialise(self, api=False, daily=False, trigger=False):
        if api:
            ret = {
                   'body_part': self.body_part.location.value,
                   'side': self.side,
                   'pain': self.pain,
                   'status': self.historic_soreness_status.name if self.historic_soreness_status is not None else HistoricSorenessStatus.dormant_cleared.name
                   }
        elif daily:
            ret = {
                   'body_part': self.body_part.location.value,
                   'pain': self.pain,
                   'severity': self.severity,
                   'movement': self.movement,
                   'side': self.side,
                   'reported_date_time': format_datetime(self.reported_date_time)
                   }
        elif trigger:
            ret = {
                   'body_part': self.body_part.location.value,
                   'pain': self.pain,
                   'severity': self.severity,
                   'movement': self.movement,
                   'side': self.side,
                   'first_reported': self.first_reported,  # format_date(self.first_reported) if self.first_reported is not None else None,
                  }

        else:
            ret = {
                   'body_part': self.body_part.location.value,
                   'pain': self.pain,
                   'severity': self.severity,
                   'movement': self.movement,
                   'side': self.side
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
    elbow = 19
    wrist = 20
    lats = 21


class BodyPart(object):

    def __init__(self, body_part_location, treatment_priority):
        self.location = body_part_location
        self.treatment_priority = treatment_priority
        self.inhibit_exercises = []
        self.lengthen_exercises = []
        self.activate_exercises = []
        self.integrate_exercises = []

        self.static_stretch_exercises = []
        self.active_stretch_exercises = []
        self.dynamic_stretch_exercises = []
        self.isolated_activate_exercises = []
        self.static_integrate_exercises = []

        self.agonists = []
        self.synergists = []
        self.stabilizers = []
        self.antagonists = []

    @staticmethod
    def add_exercises(exercise_list, exercise_dict, treatment_priority, randomize=False):

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

    def add_extended_exercise_phases(self, inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, static_integrate, randomize=False):

        self.inhibit_exercises = self.add_exercises(self.inhibit_exercises, inhibit,
                                                    self.treatment_priority, randomize)

        self.static_stretch_exercises = self.add_exercises(self.static_stretch_exercises, static_stretch,
                                                           self.treatment_priority, randomize)

        self.active_stretch_exercises = self.add_exercises(self.active_stretch_exercises, active_stretch,
                                                           self.treatment_priority, randomize)

        self.dynamic_stretch_exercises = self.add_exercises(self.dynamic_stretch_exercises, dynamic_stretch,
                                                            self.treatment_priority, randomize)

        self.isolated_activate_exercises = self.add_exercises(self.isolated_activate_exercises, isolated_activation,
                                                                self.treatment_priority, randomize)

        self.static_integrate_exercises = self.add_exercises(self.static_integrate_exercises, static_integrate,
                                                             self.treatment_priority, randomize)

    def add_muscle_groups(self, agonists, synergists, stabilizers, antagonists):

        self.agonists = agonists
        self.synergists = synergists
        self.stabilizers = stabilizers
        self.antagonists = antagonists


class HistoricSorenessStatus(IntEnum):
    dormant_cleared = 0
    persistent_pain = 1
    persistent_2_pain = 2
    almost_persistent_pain = 3
    almost_persistent_2_pain = 4
    almost_persistent_2_pain_acute = 5
    persistent_soreness = 6
    persistent_2_soreness = 7
    almost_persistent_soreness = 8
    almost_persistent_2_soreness = 9
    acute_pain = 10
    almost_acute_pain = 11


class HistoricSoreness(BaseSoreness, Serialisable):

    def __init__(self, body_part_location, side, is_pain):
        super().__init__()
        self.body_part_location = body_part_location
        # self.historic_soreness_status = HistoricSorenessStatus.dormant_cleared
        self.is_pain = is_pain
        self.side = side
        self.streak = 0
        self.streak_start_date = None
        self.average_severity = 0.0
        self.first_reported = None
        self.last_reported = ""
        self.ask_acute_pain_question = False
        self.ask_persistent_2_question = False

    def json_serialise(self, api=False):
        if api:
            ret = {"body_part": self.body_part_location.value,
                   "side": self.side,
                   "pain": self.is_pain,
                   "status": self.historic_soreness_status.name}
        else:
            ret = {
                   'body_part_location': self.body_part_location.value,
                   'historic_soreness_status': self.historic_soreness_status.value,
                   'is_pain': self.is_pain,
                   'side': self.side,
                   'streak': self.streak,
                   'streak_start_date': self.streak_start_date,
                   'average_severity': self.average_severity,
                   'first_reported': self.first_reported,
                   'last_reported': self.last_reported,
                   'ask_acute_pain_question': self.ask_acute_pain_question,
                   'ask_persistent_2_question': self.ask_persistent_2_question
                  }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        soreness = cls(BodyPartLocation(input_dict['body_part_location']), input_dict.get('side', None), input_dict.get('is_pain', False))
        hist_sore_status = input_dict.get('historic_soreness_status', None)
        soreness.historic_soreness_status = HistoricSorenessStatus(hist_sore_status) if hist_sore_status is not None else HistoricSorenessStatus.dormant_cleared
        soreness.streak = input_dict.get('streak', 0)
        soreness.streak_start_date = input_dict.get("streak_start_date", None)
        soreness.average_severity = input_dict.get('average_severity', 0.0)
        soreness.first_reported = input_dict.get("first_reported", None)
        if soreness.first_reported == "":
            soreness.first_reported = None
        soreness.last_reported = input_dict.get("last_reported", "")
        soreness.ask_acute_pain_question = input_dict.get("ask_acute_pain_question", False)
        soreness.ask_persistent_2_question = input_dict.get("ask_persistent_2_question", False)

        return soreness

    def is_joint(self):
        if (self.body_part_location == BodyPartLocation.hip_flexor or
                self.body_part_location == BodyPartLocation.knee or
                self.body_part_location == BodyPartLocation.ankle or
                self.body_part_location == BodyPartLocation.foot or
                self.body_part_location == BodyPartLocation.achilles or
                self.body_part_location == BodyPartLocation.elbow or
                self.body_part_location == BodyPartLocation.wrist):
            return True
        else:
            return False

    def is_muscle(self):
        if (self.body_part_location == BodyPartLocation.shoulder or
                self.body_part_location == BodyPartLocation.chest or
                self.body_part_location == BodyPartLocation.abdominals or
                self.body_part_location == BodyPartLocation.groin or
                self.body_part_location == BodyPartLocation.quads or
                self.body_part_location == BodyPartLocation.shin or
                self.body_part_location == BodyPartLocation.outer_thigh or
                self.body_part_location == BodyPartLocation.lower_back or
                self.body_part_location == BodyPartLocation.glutes or
                self.body_part_location == BodyPartLocation.hamstrings or
                self.body_part_location == BodyPartLocation.calves or
                self.body_part_location == BodyPartLocation.upper_back_neck or
                self.body_part_location == BodyPartLocation.lats):
            return True
        else:
            return False


class BodyPartLocationText(object):
    def __init__(self, body_part_location):
        self.body_part_location = body_part_location

    def value(self):
        body_part_text = {'head': 'head',
                          'shoulder': 'shoulder',
                          'chest': 'pecs',
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
                          'upper_back_neck': 'upper back',
                          'elbow': 'elbow',
                          'wrist': 'wrist',
                          'lats': 'lat'}

        return body_part_text[self.body_part_location.name]


class ExerciseDosage(object):
    def __init__(self):
        self.goal = None
        self.priority = 0
        self.soreness_source = None
        self.efficient_reps_assigned = 0
        self.efficient_sets_assigned = 0
        self.complete_reps_assigned = 0
        self.complete_sets_assigned = 0
        self.comprehensive_reps_assigned = 0
        self.comprehensive_sets_assigned = 0
        self.ranking = 0

    def get_total_dosage(self):
        return self.efficient_reps_assigned * self.efficient_sets_assigned + \
         self.complete_reps_assigned * self.complete_sets_assigned + \
         self.comprehensive_reps_assigned * self.comprehensive_sets_assigned

    def json_serialise(self):
        ret = {'goal': self.goal.json_serialise() if self.goal is not None else None,
               'priority': self.priority,
               'soreness_source': self.soreness_source.json_serialise(trigger=True) if self.soreness_source is not None else None,
               'efficient_reps_assigned': self.efficient_reps_assigned,
               'efficient_sets_assigned': self.efficient_sets_assigned,
               'complete_reps_assigned': self.complete_reps_assigned,
               'complete_sets_assigned': self.complete_sets_assigned,
               'comprehensive_reps_assigned': self.comprehensive_reps_assigned,
               'comprehensive_sets_assigned': self.comprehensive_sets_assigned,
               'ranking': self.ranking
               }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        goal = input_dict.get('goal', None)
        soreness_source = input_dict.get('soreness_source', None)
        dosage = cls()
        dosage.goal = AthleteGoal.json_deserialise(goal) if goal is not None else None
        dosage.priority = input_dict.get('priority', 0)
        dosage.soreness_source = Soreness.json_deserialise(soreness_source) if soreness_source is not None else None
        dosage.efficient_reps_assigned = input_dict.get('efficient_reps_assigned', 0)
        dosage.efficient_sets_assigned = input_dict.get('efficient_sets_assigned', 0)
        dosage.complete_reps_assigned = input_dict.get('complete_reps_assigned', 0)
        dosage.complete_sets_assigned = input_dict.get('complete_sets_assigned', 0)
        dosage.comprehensive_reps_assigned = input_dict.get('comprehensive_reps_assigned', 0)
        dosage.comprehensive_sets_assigned = input_dict.get('comprehensive_sets_assigned', 0)
        dosage.ranking = input_dict.get('ranking', 0)

        return dosage


class AssignedExercise(Serialisable):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0,
                 body_part_location=BodyPartLocation.general, progressions=[]):
        self.exercise = Exercise(library_id)
        self.exercise.progressions = progressions
        # self.body_part_priority = body_part_priority
        # self.body_part_exercise_priority = body_part_exercise_priority
        # self.body_part_soreness_level = body_part_soreness_level
        # self.body_part_location = body_part_location
        self.athlete_id = ""

        self.expire_date_time = None
        self.position_order = 0
        self.goal_text = ""
        self.equipment_required = []
        #self.goals = set()
        #self.priorities = set()
        #self.soreness_sources = set()
        self.dosages = []


    def set_dosage_ranking(self):
        if len(self.dosages) > 1:
            self.dosages = sorted(self.dosages, key=lambda x: x.get_total_dosage(), reverse=True)
            rank = 0
            for dosage in self.dosages:
                dosage.ranking = rank
                rank += 1

    def duration_efficient(self):

        if len(self.dosages) > 0:
            dosages = sorted(self.dosages, key=lambda x: (x.efficient_sets_assigned, x.efficient_reps_assigned), reverse=True)

            return self.duration(dosages[0].efficient_reps_assigned, dosages[0].efficient_sets_assigned)
        else:
            return 0

    def duration_complete(self):

        if len(self.dosages) > 0:
            dosages = sorted(self.dosages, key=lambda x: (x.complete_sets_assigned, x.complete_reps_assigned), reverse=True)

            return self.duration(dosages[0].complete_reps_assigned, dosages[0].complete_sets_assigned)
        else:
            return 0

    def duration_comprehensive(self):

        if len(self.dosages) > 0:
            dosages = sorted(self.dosages, key=lambda x: (x.comprehensive_sets_assigned, x.comprehensive_reps_assigned), reverse=True)

            return self.duration(dosages[0].comprehensive_reps_assigned, dosages[0].comprehensive_sets_assigned)
        else:
            return 0

    def duration(self, reps_assigned, sets_assigned):
        if self.exercise.unit_of_measure.name == "count":
            if not self.exercise.bilateral:
                return self.exercise.seconds_per_rep * reps_assigned * sets_assigned
            else:
                return (self.exercise.seconds_per_rep * reps_assigned * sets_assigned) * 2
        elif self.exercise.unit_of_measure.name == "seconds":
            if not self.exercise.bilateral:
                return self.exercise.seconds_per_set * sets_assigned
            else:
                return (self.exercise.seconds_per_set * sets_assigned) * 2
        else:
            return None

    '''
    def soreness_priority(self):
        return ExercisePriority.neutral
    '''

    def __setattr__(self, name, value):
        if name == "unit_of_measure" and not isinstance(value, UnitOfMeasure):
            value = UnitOfMeasure[value]
        super().__setattr__(name, value)

    @classmethod
    def json_deserialise(cls, input_dict):
        assigned_exercise = cls(input_dict.get("library_id", None))
        assigned_exercise.exercise.name = input_dict.get("name", "")
        assigned_exercise.exercise.display_name = input_dict.get("display_name", "")
        assigned_exercise.exercise.youtube_id = input_dict.get("youtube_id", "")
        assigned_exercise.exercise.description = input_dict.get("description", "")
        assigned_exercise.exercise.bilateral = input_dict.get("bilateral", False)
        assigned_exercise.exercise.unit_of_measure = input_dict.get("unit_of_measure", None)
        assigned_exercise.position_order = input_dict.get("position_order", 0)
        #assigned_exercise.efficient_reps_assigned = input_dict.get("efficient_reps_assigned", 0)
        #assigned_exercise.efficient_sets_assigned = input_dict.get("efficient_sets_assigned", 0)
        #assigned_exercise.complete_reps_assigned = input_dict.get("complete_reps_assigned", 0)
        #assigned_exercise.complete_sets_assigned = input_dict.get("complete_sets_assigned", 0)
        #assigned_exercise.comprehensive_reps_assigned = input_dict.get("comprehensive_reps_assigned", 0)
        #assigned_exercise.comprehensive_sets_assigned = input_dict.get("comprehensive_sets_assigned", 0)
        assigned_exercise.exercise.seconds_per_set = input_dict.get("seconds_per_set", 0)
        assigned_exercise.exercise.seconds_per_rep = input_dict.get("seconds_per_rep", 0)
        assigned_exercise.goal_text = input_dict.get("goal_text", "")
        assigned_exercise.equipment_required = input_dict.get("equipment_required", [])
        #assigned_exercise.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])
        #assigned_exercise.priorities = set(input_dict.get('priorities', []))
        #assigned_exercise.soreness_sources = set([Soreness.json_deserialise(soreness) for soreness in input_dict.get('soreness_sources', [])])
        assigned_exercise.dosages = [ExerciseDosage.json_deserialise(dosage) for dosage in input_dict.get('dosages', [])]

        return assigned_exercise

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
               'duration_efficient': self.duration_efficient(),
               'duration_complete': self.duration_complete(),
               'duration_comprehensive': self.duration_comprehensive(),
               'goal_text': self.goal_text,
               'equipment_required': self.equipment_required,
               #'goals': [goal.json_serialise() for goal in self.goals],
               #'priorities': list(self.priorities),
               #'soreness_sources': [soreness.json_serialise(trigger=True) for soreness in self.soreness_sources],
               'dosages': [dosage.json_serialise() for dosage in self.dosages]
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


class AthleteGoalType(Enum):
    pain = 0
    sore = 1
    sport = 2
    preempt_sport = 3
    preempt_soreness = 4
    preempt_corrective = 5
    corrective = 6
    injury_history = 7


class AthleteGoal(object):
    def __init__(self, text, priority, athlete_goal_type):
        self.text = text
        self.goal_type = athlete_goal_type
        self.priority = priority
        self.trigger = ''

    def json_serialise(self):
        ret = {
            'text': self.text,
            'priority': self.priority,
            'trigger': self.trigger,
            'goal_type': self.goal_type.value if self.goal_type is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        goal_type = input_dict.get('goal_type', None)
        athlete_goal_type = AthleteGoalType(goal_type) if goal_type is not None else None
        goal = cls(text=input_dict['text'], priority=input_dict['priority'], athlete_goal_type=athlete_goal_type)
        goal.trigger = input_dict.get('trigger', "")
        return goal
