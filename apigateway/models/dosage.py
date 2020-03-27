from models.goal import AthleteGoal
from models.trigger import Trigger
from enum import Enum


class DosageProgression(Enum):
    min_mod_max = 0
    mod_max_super_max = 1


class ExerciseDosage(object):
    def __init__(self):
        self.goal = None
        self.priority = 0
        self.last_severity = 0
        self.tier = 0
        self.soreness_source = None
        self.sports = []
        self.efficient_reps_assigned = 0
        self.efficient_sets_assigned = 0
        self.complete_reps_assigned = 0
        self.complete_sets_assigned = 0
        self.comprehensive_reps_assigned = 0
        self.comprehensive_sets_assigned = 0
        self.default_efficient_reps_assigned = 0
        self.default_efficient_sets_assigned = 0
        self.default_complete_reps_assigned = 0
        self.default_complete_sets_assigned = 0
        self.default_comprehensive_reps_assigned = 0
        self.default_comprehensive_sets_assigned = 0
        self.ranking = 0
        self.dosage_progression = None  # just used for calcs, no need to ser/de-ser

    def set_reps_and_sets(self, exercise):

        if self.priority == '1':
            if self.dosage_progression == DosageProgression.min_mod_max:
                self.efficient_reps_assigned = exercise.min_reps
                self.efficient_sets_assigned = 1
                self.default_efficient_reps_assigned = exercise.min_reps
                self.default_efficient_sets_assigned = 1

                self.complete_reps_assigned = exercise.max_reps
                self.complete_sets_assigned = 1
                self.default_complete_reps_assigned = exercise.max_reps
                self.default_complete_sets_assigned = 1

                self.comprehensive_reps_assigned = exercise.max_reps
                self.comprehensive_sets_assigned = 2
                self.default_comprehensive_reps_assigned = exercise.max_reps
                self.default_comprehensive_sets_assigned = 2
            elif self.dosage_progression == DosageProgression.mod_max_super_max:
                self.efficient_reps_assigned = exercise.max_reps
                self.efficient_sets_assigned = 1
                self.default_efficient_reps_assigned = exercise.max_reps
                self.default_efficient_sets_assigned = 1

                self.complete_reps_assigned = exercise.max_reps
                self.complete_sets_assigned = 2
                self.default_complete_reps_assigned = exercise.max_reps
                self.default_complete_sets_assigned = 2

                self.comprehensive_reps_assigned = exercise.max_reps
                self.comprehensive_sets_assigned = 3
                self.default_comprehensive_reps_assigned = exercise.max_reps
                self.default_comprehensive_sets_assigned = 3
        elif self.priority == '2':
            if self.dosage_progression == DosageProgression.min_mod_max:
                self.efficient_reps_assigned = 0
                self.efficient_sets_assigned = 0
                self.default_efficient_reps_assigned = 0
                self.default_efficient_sets_assigned = 0

                self.complete_reps_assigned = exercise.min_reps
                self.complete_sets_assigned = 1
                self.default_complete_reps_assigned = exercise.min_reps
                self.default_complete_sets_assigned = 1

                self.comprehensive_reps_assigned = exercise.max_reps
                self.comprehensive_sets_assigned = 1
                self.default_comprehensive_reps_assigned = exercise.max_reps
                self.default_comprehensive_sets_assigned = 1
            elif self.dosage_progression == DosageProgression.mod_max_super_max:
                self.efficient_reps_assigned = 0
                self.efficient_sets_assigned = 0
                self.default_efficient_reps_assigned = 0
                self.default_efficient_sets_assigned = 0

                self.complete_reps_assigned = exercise.max_reps
                self.complete_sets_assigned = 1
                self.default_complete_reps_assigned = exercise.max_reps
                self.default_complete_sets_assigned = 1

                self.comprehensive_reps_assigned = exercise.max_reps
                self.comprehensive_sets_assigned = 2
                self.default_comprehensive_reps_assigned = exercise.max_reps
                self.default_comprehensive_sets_assigned = 2
        elif self.priority == '3':
            if self.dosage_progression == DosageProgression.min_mod_max:
                self.efficient_reps_assigned = 0
                self.efficient_sets_assigned = 0
                self.default_efficient_reps_assigned = 0
                self.default_efficient_sets_assigned = 0

                self.complete_reps_assigned = 0
                self.complete_sets_assigned = 0
                self.default_complete_reps_assigned = 0
                self.default_complete_sets_assigned = 0

                self.comprehensive_reps_assigned = exercise.min_reps
                self.comprehensive_sets_assigned = 1
                self.default_comprehensive_reps_assigned = exercise.min_reps
                self.default_comprehensive_sets_assigned = 1
            elif self.dosage_progression == DosageProgression.mod_max_super_max:
                self.efficient_reps_assigned = 0
                self.efficient_sets_assigned = 0
                self.default_efficient_reps_assigned = 0
                self.default_efficient_sets_assigned = 0

                self.complete_reps_assigned = 0
                self.complete_sets_assigned = 0
                self.default_complete_reps_assigned = 0
                self.default_complete_sets_assigned = 0

                self.comprehensive_reps_assigned = exercise.max_reps
                self.comprehensive_sets_assigned = 1
                self.default_comprehensive_reps_assigned = exercise.max_reps
                self.default_comprehensive_sets_assigned = 1

    def severity(self):
        if self.last_severity is not None and self.last_severity > 0:
        #if self.soreness_source is not None:
            #return self.soreness_source.severity
            return self.last_severity
        else:
            return 0.5

    def get_total_dosage(self):
        return self.efficient_reps_assigned * self.efficient_sets_assigned + \
         self.complete_reps_assigned * self.complete_sets_assigned + \
         self.comprehensive_reps_assigned * self.comprehensive_sets_assigned

    def json_serialise(self, mobility_api=False):
        ret = {
            'goal': self.goal.json_serialise(mobility_api) if self.goal is not None else None,
            'efficient_reps_assigned': self.efficient_reps_assigned,
            'efficient_sets_assigned': self.efficient_sets_assigned,
            'complete_reps_assigned': self.complete_reps_assigned,
            'complete_sets_assigned': self.complete_sets_assigned,
            'comprehensive_reps_assigned': self.comprehensive_reps_assigned,
            'comprehensive_sets_assigned': self.comprehensive_sets_assigned,
            'priority': self.priority,
        }
        if not mobility_api:
            other_attributes = {
                'ranking': self.ranking,
                'tier': self.tier,
                'default_efficient_reps_assigned': self.default_efficient_reps_assigned,
                'default_efficient_sets_assigned': self.default_efficient_sets_assigned,
                'default_complete_reps_assigned': self.default_complete_reps_assigned,
                'default_complete_sets_assigned': self.default_complete_sets_assigned,
                'default_comprehensive_reps_assigned': self.default_comprehensive_reps_assigned,
                'default_comprehensive_sets_assigned': self.default_comprehensive_sets_assigned
                }
            ret.update(other_attributes)
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        goal = input_dict.get('goal', None)
        dosage = cls()
        dosage.goal = AthleteGoal.json_deserialise(goal) if goal is not None else None
        dosage.priority = input_dict.get('priority', 0)
        dosage.tier = input_dict.get('tier', 0)
        dosage.efficient_reps_assigned = input_dict.get('efficient_reps_assigned', 0)
        dosage.efficient_sets_assigned = input_dict.get('efficient_sets_assigned', 0)
        dosage.complete_reps_assigned = input_dict.get('complete_reps_assigned', 0)
        dosage.complete_sets_assigned = input_dict.get('complete_sets_assigned', 0)
        dosage.comprehensive_reps_assigned = input_dict.get('comprehensive_reps_assigned', 0)
        dosage.comprehensive_sets_assigned = input_dict.get('comprehensive_sets_assigned', 0)
        dosage.default_efficient_reps_assigned = input_dict.get('default_efficient_reps_assigned', 0)
        dosage.default_efficient_sets_assigned = input_dict.get('default_efficient_sets_assigned', 0)
        dosage.default_complete_reps_assigned = input_dict.get('default_complete_reps_assigned', 0)
        dosage.default_complete_sets_assigned = input_dict.get('default_complete_sets_assigned', 0)
        dosage.default_comprehensive_reps_assigned = input_dict.get('default_comprehensive_reps_assigned', 0)
        dosage.default_comprehensive_sets_assigned = input_dict.get('default_comprehensive_sets_assigned', 0)
        dosage.ranking = input_dict.get('ranking', 0)

        return dosage