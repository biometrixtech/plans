from enum import Enum, IntEnum

from models.exercise import Exercise, UnitOfMeasure
from serialisable import Serialisable
from random import shuffle
import datetime
from fathomapi.utils.exceptions import InvalidSchemaException

from utils import format_datetime, parse_datetime, parse_date
from models.sport import SportName


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
    doms = 12

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
                self.historic_soreness_status == HistoricSorenessStatus.doms or
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
        self.max_severity = None  # muscle_soreness_severity
        self.max_severity_date_time = None
        self.causal_session = None
        self.first_reported_date_time = None
        self.last_reported_date_time = None
        self.cleared_date_time = None
        self.daily = True

    @classmethod
    def json_deserialise(cls, input_dict):
        soreness = cls()
        soreness.body_part = BodyPart(BodyPartLocation(input_dict['body_part']), None)
        soreness.pain = input_dict.get('pain', False)
        soreness.severity = input_dict['severity']
        soreness.movement = input_dict.get('movement', None)
        soreness.side = input_dict.get('side', None)
        soreness.max_severity = input_dict.get('max_severity', None)
        soreness.first_reported_date_time = input_dict.get('first_reported_date_time', None)
        soreness.last_reported_date_time = input_dict.get('last_reported_date_time', None)
        soreness.cleared_date_time = input_dict.get('cleared_date_time', None)
        soreness.max_severity_date_time = input_dict.get('max_severity_date_time', None)
        soreness.causal_session = input_dict.get('causal_session', None)
        # if input_dict.get('first_reported_date_time', None) is not None:
        #     soreness.first_reported_date_time = parse_date(input_dict['first_reported_date_time'])
        if input_dict.get('reported_date_time', None) is not None:
            soreness.reported_date_time = parse_datetime(input_dict['reported_date_time'])
        return soreness

    def __hash__(self):
        return hash((self.body_part.location, self.side))

    def __eq__(self, other):
        return ((self.body_part.location == other.body_part.location,
                 self.side == other.side))

    def __setattr__(self, name, value):
        if name in ['first_reported_date_time', 'last_reported_date_time', 'reported_date_time', 'cleared_date_time', 'max_severity_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

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
    def is_joint(self):
        if (self.body_part.location == BodyPartLocation.hip_flexor or
                self.body_part.location == BodyPartLocation.knee or
                self.body_part.location == BodyPartLocation.ankle or
                self.body_part.location == BodyPartLocation.foot or
                self.body_part.location == BodyPartLocation.achilles or
                self.body_part.location == BodyPartLocation.elbow or
                self.body_part.location == BodyPartLocation.wrist):
            return True
        else:
            return False

    def is_muscle(self):
        if (self.body_part.location == BodyPartLocation.shoulder or
                self.body_part.location == BodyPartLocation.chest or
                self.body_part.location == BodyPartLocation.abdominals or
                self.body_part.location == BodyPartLocation.groin or
                self.body_part.location == BodyPartLocation.quads or
                self.body_part.location == BodyPartLocation.shin or
                self.body_part.location == BodyPartLocation.outer_thigh or
                self.body_part.location == BodyPartLocation.lower_back or
                self.body_part.location == BodyPartLocation.glutes or
                self.body_part.location == BodyPartLocation.hamstrings or
                self.body_part.location == BodyPartLocation.calves or
                self.body_part.location == BodyPartLocation.upper_back_neck or
                self.body_part.location == BodyPartLocation.lats):
            return True
        else:
            return False

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
                   'first_reported_date_time': format_datetime(self.first_reported_date_time) if self.first_reported_date_time is not None else None,
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


class BodyPartSide(object):
    def __init__(self, body_part_location, side):
        self.body_part_location = body_part_location
        self.side = side

    def json_serialise(self):
        return {
            "body_part_location": self.body_part_location.value,
            "side": self.side
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        return cls(BodyPartLocation(input_dict['body_part_location']), input_dict['side'])


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
    biceps = 22
    triceps = 23
    upper_body = 91
    lower_body = 92
    full_body = 93


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
        self.active_or_dynamic_stretch_exercises = []
        self.isolated_activate_exercises = []
        self.static_integrate_exercises = []
        self.dynamic_integrate_exercises = []
        self.dynamic_stretch_integrate_exercises = []
        self.dynamic_integrate_with_speed_exercises = []

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

    def add_dynamic_exercise_phases(self, dynamic_stretch, dynamic_integrate, dynamic_integrate_with_speed):

        self.dynamic_stretch_exercises = self.add_exercises(self.dynamic_stretch_exercises, dynamic_stretch, self.treatment_priority, False)
        self.dynamic_integrate_exercises = self.add_exercises(self.dynamic_integrate_exercises, dynamic_integrate, self.treatment_priority, False)
        self.dynamic_integrate_with_speed_exercises = self.add_exercises(self.dynamic_integrate_with_speed_exercises, dynamic_integrate_with_speed, self.treatment_priority, False)

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
        self.sport_name = None
        self.efficient_reps_assigned = 0
        self.efficient_sets_assigned = 0
        self.complete_reps_assigned = 0
        self.complete_sets_assigned = 0
        self.comprehensive_reps_assigned = 0
        self.comprehensive_sets_assigned = 0
        self.default_reps_assigned = 0
        self.default_sets_assigned = 0
        self.ranking = 0

    def severity(self):
        if self.soreness_source is not None:
            return self.soreness_source.severity
        else:
            return 0.5

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
               'default_reps_assigned': self.default_reps_assigned,
               'default_sets_assigned': self.default_sets_assigned,
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
        dosage.default_reps_assigned = input_dict.get('default_reps_assigned', 0)
        dosage.default_sets_assigned = input_dict.get('default_sets_assigned', 0)
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
        # self.goals = set()
        # self.priorities = set()
        # self.soreness_sources = set()
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
        elif self.exercise.unit_of_measure.name == "seconds" or self.exercise.unit_of_measure.name == 'yards':
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
        # assigned_exercise.efficient_reps_assigned = input_dict.get("efficient_reps_assigned", 0)
        # assigned_exercise.efficient_sets_assigned = input_dict.get("efficient_sets_assigned", 0)
        # assigned_exercise.complete_reps_assigned = input_dict.get("complete_reps_assigned", 0)
        # assigned_exercise.complete_sets_assigned = input_dict.get("complete_sets_assigned", 0)
        # assigned_exercise.comprehensive_reps_assigned = input_dict.get("comprehensive_reps_assigned", 0)
        # assigned_exercise.comprehensive_sets_assigned = input_dict.get("comprehensive_sets_assigned", 0)
        assigned_exercise.exercise.seconds_per_set = input_dict.get("seconds_per_set", 0)
        assigned_exercise.exercise.seconds_per_rep = input_dict.get("seconds_per_rep", 0)
        assigned_exercise.goal_text = input_dict.get("goal_text", "")
        assigned_exercise.equipment_required = input_dict.get("equipment_required", [])
        # assigned_exercise.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])
        # assigned_exercise.priorities = set(input_dict.get('priorities', []))
        # assigned_exercise.soreness_sources = set([Soreness.json_deserialise(soreness) for soreness in input_dict.get('soreness_sources', [])])
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
               # 'goals': [goal.json_serialise() for goal in self.goals],
               # 'priorities': list(self.priorities),
               # 'soreness_sources': [soreness.json_serialise(trigger=True) for soreness in self.soreness_sources],
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
    preempt_personalized_sport = 4
    preempt_corrective = 5
    corrective = 6
    injury_history = 7
    counter_overreaching = 8
    respond_risk = 9
    on_request = 10


class AthleteGoal(object):
    def __init__(self, text, priority, athlete_goal_type):
        self.text = text
        self.goal_type = athlete_goal_type
        self.priority = priority
        self.trigger_type = None

    def display_order(self):

        if self.goal_type == AthleteGoalType.pain:
            return 1
        elif self.goal_type == AthleteGoalType.sore:
            return 2
        elif self.goal_type == AthleteGoalType.counter_overreaching:
            return 3
        elif self.goal_type == AthleteGoalType.respond_risk:
            return 4
        elif self.goal_type == AthleteGoalType.sport:
            return 5
        elif self.goal_type == AthleteGoalType.preempt_corrective:
            return 6
        elif self.goal_type == AthleteGoalType.preempt_personalized_sport:
            return 7
        elif self.goal_type == AthleteGoalType.preempt_sport:
            return 8
        elif self.goal_type == AthleteGoalType.corrective:
            return 9
        elif self.goal_type == AthleteGoalType.injury_history:
            return 10

    def json_serialise(self):
        ret = {
            'text': self.text,
            'priority': self.priority,
            'trigger_type': self.trigger_type.value if self.trigger_type is not None else None,
            'goal_type': self.goal_type.value if self.goal_type is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        goal_type = input_dict.get('goal_type', None)
        athlete_goal_type = AthleteGoalType(goal_type) if goal_type is not None else None
        goal = cls(text=input_dict['text'], priority=input_dict['priority'], athlete_goal_type=athlete_goal_type)
        trigger_type = input_dict.get('trigger_type', None)
        goal.trigger_type = TriggerType(trigger_type) if trigger_type is not None else None
        return goal


class Alert(object):
    def __init__(self, goal):
        self.goal = goal
        self.body_part = None
        self.sport_name = None
        self.severity = None

    def json_serialise(self):
        return {
            "goal": self.goal.json_serialise(),
            "body_part": self.body_part.json_serialise() if self.body_part is not None else None,
            "sport_name": self.sport_name.value if self.sport_name is not None else None,
            "severity": self.severity
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        alert = cls(AthleteGoal.json_deserialise(input_dict['goal']))
        alert.body_part = BodyPartSide.json_deserialise(input_dict['body_part']) if input_dict['body_part'] is not None else None
        alert.sport_name = input_dict['sport_name']
        alert.severity = input_dict['severity']
        return alert

    def __setattr__(self, name, value):
        if name == "sport_name" and not isinstance(value, SportName) and value is not None:
            value = SportName(value)
        super().__setattr__(name, value)


class TriggerType(IntEnum):
    high_volume_intensity = 0  # "High Relative Volume or Intensity of Logged Session"
    hist_sore_greater_30_high_volume_intensity = 1  # "Pers, Pers-2 Soreness > 30d + High Relative Volume or Intensity of Logged Session" 
    hist_pain_high_volume_intensity = 2  # "Acute, Pers, Pers_2 Pain  + High Relative Volume or Intensity of Logged Session" 
    hist_sore_greater_30_no_sore_today_3_high_volume_intensity = 3  # "Pers, Pers-2 Soreness > 30d + No soreness reported today + Logged High Relative Volume or Intensity" 
    acute_pain_no_pain_today_high_volume_intensity = 4  # "Acute Pain + No pain reported today + High Relative Volume or Intensity of Logged Session" 
    pers_pers2_pain_no_pain_sore_today_high_volume_intensity = 5  # "Pers, Pers_2 Pain + No pain Reported Today + High Relative Volume or Intensity of Logged Session"
    hist_sore_less_30_sport = 6  # "Pers, Pers-2 Soreness < 30d + Correlated to Sport"
    hist_sore_less_30_no_sport = 7  # "Pers, Pers-2 Soreness < 30d + Not Correlated to Sport"  
    overreaching_increasing_strain = 8  # "Overreaching as increasing Muscular Strain (with context for Training Volume)"
    sore_today_no_session = 9  # "Sore reported today + not linked to session"    
    sore_today = 10  # "Sore reported today"
    sore_today_doms = 11  # "Soreness Reported Today as DOMs"
    hist_sore_less_30_sore_today = 12  # "Pers, Pers-2 Soreness < 30d + Soreness reported today"
    hist_sore_greater_30_sore_today = 13  # "Pers, Pers-2 Soreness > 30d + Soreness Reported Today"
    pain_today = 14  # "Pain reported today"
    pain_today_high = 15  # "Pain reported today high severity"
    hist_pain = 16  # "Acute, Pers, Pers-2 Pain"
    hist_pain_sport = 17  # "Acute, Pers, Pers_2 Pain + Correlated to Sport"
    pain_injury = 18  # 'Pain - Injury'
    hist_sore_greater_30 = 19  # "Pers, Pers-2 Soreness > 30d"
    hist_sore_greater_30_sport = 20  # "Pers, Pers-2 Soreness > 30d + Correlated to Sport"
    pers_pers2_pain_less_30_no_pain_today = 21
    pers_pers2_pain_greater_30_no_pain_today = 22

    def is_grouped_trigger(self):
        if self.value in [6, 7, 8, 10, 11, 14, 15]:
            return True
        else:
            return False

    def belongs_to_same_group(self, other):
        groups = {0: [6, 7, 8],
                  1: [10, 11],
                  2: [14, 15]}
        for group in groups.values():
            if self.value in group and other.value in group:
                return True
        return False
