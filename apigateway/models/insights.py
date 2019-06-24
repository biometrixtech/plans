import datetime
from enum import Enum
from serialisable import Serialisable
from models.soreness import BodyPartSide
from models.trigger import TriggerType
from models.trigger_data import TriggerData
from models.sport import SportName
from logic.text_generator import TextGenerator
from utils import format_datetime, parse_datetime


class AthleteInsight(Serialisable):
    def __init__(self, trigger_type):
        self.trigger_type = trigger_type
        self.goal_targeted = []
        self.start_date_time = None
        self.last_triggered_date_time = None
        self.title = ""
        self.text = ""
        self.parent = False
        self.first = False
        self.body_parts = []
        self.sport_names = []
        self.severity = []
        self.cleared = False
        self.insight_type = InsightType.stress
        self.longitudinal = self.is_multi_day()
        self.priority = None
        self.styling = 0
        self.read = False
        self.parent_group = TriggerType.get_parent_group(self.trigger_type)
        self.present_in_plans = True
        self.child_triggers = {}

    def json_serialise(self):
        ret = {
            'trigger_type': self.trigger_type.value,
            'title': self.title,
            'goal_targeted': self.goal_targeted,
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'last_triggered_date_time': format_datetime(self.last_triggered_date_time) if self.last_triggered_date_time is not None else None,
            'text': self.text,
            'parent': self.parent,
            'first': self.first,
            'body_parts': [body_part.json_serialise() for body_part in self.body_parts],
            'sport_names': [sport_name.value for sport_name in self.sport_names],
            'severity': self.severity,
            'cleared': self.cleared,
            'insight_type': self.insight_type.value,
            'longitudinal': self.longitudinal,
            'priority': self.priority,
            'styling': self.styling,
            'read': self.read,
            'present_in_plans': self.present_in_plans,
            'child_triggers': {str(trigger_type.value): [body_part.json_serialise() for
                                                         body_part in body_parts] for
                               (trigger_type, body_parts) in self.child_triggers.items()}
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        insight = cls(TriggerType(input_dict['trigger_type']))
        insight.title = input_dict.get('title', "")
        insight.goal_targeted = input_dict.get('goal_targeted', [])
        insight.start_date_time = input_dict.get('start_date_time', None)
        insight.last_triggered_date_time = input_dict.get('last_triggered_date_time', None)
        insight.text = input_dict.get('text', "")
        insight.parent = input_dict.get('parent', False)
        insight.first = input_dict.get('first', False)
        insight.body_parts = [BodyPartSide.json_deserialise(body_part) for body_part in input_dict['body_parts']]
        insight.sport_names = [SportName(sport_name) for sport_name in input_dict['sport_names']]
        insight.severity = input_dict.get('severity', [])
        insight.cleared = input_dict.get('cleared', False)
        insight.priority = input_dict.get('priority', 0)
        insight.styling = input_dict.get('styling', 0)
        insight.read = input_dict.get('read', False)
        insight.insight_type = InsightType(input_dict.get('insight_type', 0))
        insight.present_in_plans = input_dict.get('present_in_plans', True)
        insight.child_triggers = {TriggerType(int(trigger_type)): set([BodyPartSide.json_deserialise(body_part) for
                                                                   body_part in body_parts]) for
                                  (trigger_type, body_parts) in input_dict.get('child_triggers', {}).items()}

        return insight

    def add_data(self):
        trigger_data = TriggerData().get_trigger_data(self.trigger_type.value)
        plan_data = trigger_data['plans']
        if self.parent:
            if self.cleared:
                title = plan_data["cleared_title"]
                text = plan_data['parent_data']['cleared_body']
            else:
                if self.first:
                    title = plan_data['parent_data']['new_first_time_title']
                    text = plan_data['parent_data']['new_first_time_body']
                else:
                    title = plan_data['parent_data']['new_subsequent_title']
                    text = plan_data['parent_data']['new_subsequent_body']
        else:
            if self.cleared:
                title = plan_data["cleared_title"]
                text = plan_data['child_data']['cleared_body']
            else:
                if self.first:
                    title = plan_data['child_data']['new_first_time_title']
                    text = plan_data['child_data']['new_first_time_body']
                else:
                    title = plan_data['child_data']['new_subsequent_title']
                    text = plan_data['child_data']['new_subsequent_body']
        self.text = TextGenerator().get_cleaned_text(text, self.goal_targeted, self.body_parts, self.sport_names, severity=self.severity)
        self.title = TextGenerator().get_cleaned_text(title, self.goal_targeted, self.body_parts, self.sport_names, severity=self.severity)
        if self.parent and self.parent_group == 2:
            self.priority = 1
            self.styling = 1
        else:
            self.priority = int(trigger_data['insight_priority_plans'])
            self.styling = int(plan_data['priority_styling'])
        self.insight_type = InsightType[trigger_data['trend_type'].lower()]
        self.present_in_plans = plan_data['present_in_plans']

    def is_multi_day(self):
        if self.trigger_type.value in [7, 8, 11, 16, 19, 103, 104]:
            return True
        else:
            return False

    # def get_styling(self):
    #     if self.trigger_type.value in [15]:
    #         return 1
    #     else:
    #         return 0

    def __setattr__(self, name, value):
        if name in ['start_date_time', 'last_triggered_date_time'] and value is not None and not isinstance(value, datetime.datetime):
            value = parse_datetime(value)
        super().__setattr__(name, value)


class InsightType(Enum):
    stress = 0
    response = 1
    biomechanics = 2
