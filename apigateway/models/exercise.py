from enum import IntEnum, Enum

from models.dosage import ExerciseDosage
from models.soreness_base import BodyPartLocation

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
    feet = 3
    meters = 4
    miles = 5
    kilometers = 6
    calories = 7


class Tempo(Enum):
    controlled = 0


class ExerciseBuckets(object):
    @staticmethod
    def get_exercise_bucket_list():

        group = dict()

        group[0] = ["9", "121", "116", "216", "217", "218", "219", "220"]
        group[1] = ["119", "122"]
        group[2] = ["6", "46", "221"]
        group[3] = ["28", "49", "222", "223", "224"]
        group[4] = ["7", "26", "214", "215"]
        group[5] = ["81", "50", "226", "227"]
        group[6] = ["108", "14", "228", "229", "230"]
        group[7] = ["10", "77", "232", "233"]
        group[8] = ["85", "89", "84", "79", "234"]
        group[9] = ["117", "225"]
        group[10] = ["83", "82", "231"]
        group[11] = ["86", "90", "235", "237"]
        group[12] = ["87", "91", "236"]
        group[13] = ["88", "92"]

        return group

    def get_bucket_for_exercise(self, exercise):

        group = self.get_exercise_bucket_list()

        for k, v in group.items():
            if exercise in v:
                return v

        return [exercise]


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
        self.equipment_required = []

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
        self.phase = ''

    def set_dosage_ranking(self):
        if len(self.dosages) > 1:
            self.dosages = sorted(self.dosages, key=lambda x: (3-int(x.priority), x.severity(),
                                                               x.default_comprehensive_sets_assigned,
                                                               x.default_comprehensive_reps_assigned,
                                                               x.default_complete_sets_assigned,
                                                               x.default_complete_reps_assigned,
                                                               x.default_efficient_sets_assigned,
                                                               x.default_efficient_reps_assigned), reverse=True)
            rank = 0
            for dosage in self.dosages:
                dosage.ranking = rank
                rank += 1

    def duration_efficient(self):

        if len(self.dosages) > 0:
            dosages = sorted(self.dosages, key=lambda x: (x.efficient_sets_assigned, x.efficient_reps_assigned), reverse=True)

            return self.duration(dosages[0].efficient_reps_assigned, dosages[0].efficient_sets_assigned)
            # duration = 0
            # for d in self.dosages:
            #     duration += self.duration(d.efficient_reps_assigned, d.efficient_sets_assigned)
            #
            # return duration
        else:
            return 0

    def duration_complete(self):

        if len(self.dosages) > 0:
            dosages = sorted(self.dosages, key=lambda x: (x.complete_sets_assigned, x.complete_reps_assigned), reverse=True)

            return self.duration(dosages[0].complete_reps_assigned, dosages[0].complete_sets_assigned)
            # duration = 0
            # for d in self.dosages:
            #     duration += self.duration(d.complete_reps_assigned, d.complete_sets_assigned)
            #
            # return duration
        else:
            return 0

    def duration_comprehensive(self):

        if len(self.dosages) > 0:
            dosages = sorted(self.dosages, key=lambda x: (x.comprehensive_sets_assigned, x.comprehensive_reps_assigned), reverse=True)

            return self.duration(dosages[0].comprehensive_reps_assigned, dosages[0].comprehensive_sets_assigned)
            # duration = 0
            # for d in self.dosages:
            #     duration += self.duration(d.comprehensive_reps_assigned, d.comprehensive_sets_assigned)
            #
            # return duration
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

    def json_serialise(self, mobility_api=False, api=False, consolidated=False):
        ret = {
            'name': self.exercise.name,
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
            'equipment_required': self.equipment_required
        }
        if api and consolidated:
            dosage_parameters = self.get_consolidated_dosage_parameters()
        else:
            dosage_parameters = {'dosages': [dosage.json_serialise(mobility_api) for dosage in self.dosages]}
        ret.update(dosage_parameters)
        return ret

    def get_consolidated_dosage_parameters(self):
        consolidated_dosage = ConsolidatedDosage()
        for dosage in self.dosages:
            dosage.goal.priority = dosage.priority
            consolidated_dosage.extend_goals(dosage.goal)
            consolidated_dosage.efficient_reps_assigned = dosage.efficient_reps_assigned
            consolidated_dosage.efficient_sets_assigned = dosage.efficient_sets_assigned
            consolidated_dosage.complete_reps_assigned = dosage.complete_reps_assigned
            consolidated_dosage.complete_sets_assigned = dosage.complete_sets_assigned
            consolidated_dosage.comprehensive_reps_assigned = dosage.comprehensive_reps_assigned
            consolidated_dosage.comprehensive_sets_assigned = dosage.comprehensive_sets_assigned
        return consolidated_dosage.json_serialise()


class ConsolidatedDosage(object):
    def __init__(self):
        self.goals = []
        self.efficient_reps_assigned = 0
        self.efficient_sets_assigned = 0
        self.complete_reps_assigned = 0
        self.complete_sets_assigned = 0
        self.comprehensive_reps_assigned = 0
        self.comprehensive_sets_assigned = 0

    def extend_goals(self, goal):
        existing_goal_names = [g.text for g in self.goals]
        if goal.text not in existing_goal_names:
            self.goals.append(goal)
        else:
            existing_goal = [g for g in self.goals if g.text == goal.text][0]
            existing_goal.priority = min([existing_goal.priority, goal.priority])


    def __setattr__(self, name, value):
        if "assigned" in name and hasattr(self, name) and value is not None:
            value = max([getattr(self, name), value])
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            "goals": [{g.text: g.priority} for g in self.goals],
            "efficient_reps_assigned": self.efficient_reps_assigned,
            "efficient_sets_assigned": self.efficient_sets_assigned,
            "complete_reps_assigned": self.complete_reps_assigned,
            "complete_sets_assigned": self.complete_sets_assigned,
            "comprehensive_reps_assigned": self.comprehensive_reps_assigned,
            "comprehensive_sets_assigned": self.comprehensive_sets_assigned
        }
        return ret


class WeightMeasure(Enum):
    rep_max = 0
    percent_bodyweight = 1
    actual_weight = 2