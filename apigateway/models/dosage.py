from models.goal import AthleteGoal
from models.trigger import Trigger


class ExerciseDosage(object):
    def __init__(self):
        self.goal = None
        self.priority = 0
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
               'default_efficient_reps_assigned': self.default_efficient_reps_assigned,
               'default_efficient_sets_assigned': self.default_efficient_sets_assigned,
               'default_complete_reps_assigned': self.default_complete_reps_assigned,
               'default_complete_sets_assigned': self.default_complete_sets_assigned,
               'default_comprehensive_reps_assigned': self.default_comprehensive_reps_assigned,
               'default_comprehensive_sets_assigned': self.default_comprehensive_sets_assigned,
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
        dosage.soreness_source = Trigger.json_deserialise(soreness_source) if soreness_source is not None else None
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