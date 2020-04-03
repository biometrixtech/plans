from enum import Enum


class AthleteGoalType(Enum):
    pain = 0
    sore = 1
    high_load = 2
    preempt_sport = 3
    preempt_personalized_sport = 4
    preempt_corrective = 5
    corrective = 6
    injury_history = 7
    counter_overreaching = 8
    respond_risk = 9
    on_request = 10
    asymmetric_session = 20
    asymmetric_pattern = 21
    expected_high_load = 22
    expected_asymmetric_session = 23


class AthleteGoal(object):
    def __init__(self, text, priority, athlete_goal_type):
        self.text = text
        self.goal_type = athlete_goal_type
        self.priority = priority
        #self.trigger_type = None

    def display_order(self):

        if self.goal_type == AthleteGoalType.pain:
            return 1
        elif self.goal_type == AthleteGoalType.sore:
            return 2
        elif self.goal_type == AthleteGoalType.counter_overreaching:
            return 3
        elif self.goal_type == AthleteGoalType.respond_risk:
            return 4
        elif self.goal_type == AthleteGoalType.high_load:
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

    def json_serialise(self, mobility_api=False):
        ret = {
            'text': self.text,
            #'trigger_type': self.trigger_type.value if self.trigger_type is not None else None,
            'goal_type': self.goal_type.value if self.goal_type is not None else None
        }
        if not mobility_api:
            ret.update({
                'priority': self.priority
            })
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        goal_type = input_dict.get('goal_type', None)
        athlete_goal_type = AthleteGoalType(goal_type) if goal_type is not None else None
        goal = cls(text=input_dict['text'], priority=input_dict.get('priority', 1), athlete_goal_type=athlete_goal_type)
        #trigger_type = input_dict.get('trigger_type', None)
        #goal.trigger_type = TriggerType(trigger_type) if trigger_type is not None else None
        return goal


class AthleteGoalDef(object):
    def __init__(self, id, goal_type, goal_name):
        self.id = id
        self.goal_type = goal_type
        self.goal_name = goal_name

    def json_serialise(self):
        return {
            "id" : self.id,
            "goal_type": self.goal_type.value,
            "goal_name": self.goal_name
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        return cls(input_dict.get('id'), AthleteGoalType(input_dict.get('goal_type')), input_dict.get('goal_name', ''))
