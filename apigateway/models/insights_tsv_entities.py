from serialisable import Serialisable
from models.trigger import TriggerType
from models.insights import InsightType


class TriggerCollection(Serialisable):
    def __init__(self, trigger_list):
        self.trigger_list = trigger_list

    def json_serialise(self):
        ret = {
            'triggers': {trigger.trigger_enum.value: trigger.json_serialise() for trigger in self.trigger_list}
        }

        return ret


class InsightsPlotsDataItem(Serialisable):
    def __init__(self, unit_of_aggregation, visualization_type, vizualization_range, overlay_variable, title):
        self.unit_of_aggregation = unit_of_aggregation
        self.visualization_type = visualization_type
        self.visualization_range = vizualization_range
        self.overlay_variable = overlay_variable
        self.title = title

    def __setattr__(self, name, value):
            if name in ['visualization_type', 'visualization_range']:
                if value is not None and not isinstance(value, int):
                    value = int(value)
            super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'unit_of_aggregation': self.unit_of_aggregation,
            'visualization_type': self.visualization_type,
            'visualization_range': self.visualization_range,
            'overlay_variable': self.overlay_variable,
            'title': self.title
        }

        return ret


class InsightsCTA(Serialisable):
    def __init__(self, input, heat, warmup, cooldown, active_rest, ice, cwi, increase_default):
        self.input = input
        self.heat = heat
        self.warmup = warmup
        self.cooldown = cooldown
        self.active_rest = active_rest
        self.ice = ice
        self.cwi = cwi
        self.increase_default = increase_default

    def __setattr__(self, name, value):
            if name in ['heat', 'warmup', 'cooldown', 'active_rest', 'ice', 'cwi']:
                if value is not None and not isinstance(value, bool):
                    if value in ['x', 'X']:
                        value = True
                    else:
                        value = False
            super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'input': self.input,
            'heat': self.heat,
            'warmup': self.warmup,
            'cooldown': self.cooldown,
            'active_rest': self.active_rest,
            'ice': self.ice,
            'cwi': self.cwi,
            'increase_default': self.increase_default
        }

        return ret


class InsightsTrendsDataItem(Serialisable):
    def __init__(self, priority_styling, content_to_pass, present_in_trends, new_title, new_body, ongoing_title,
                 ongoing_body, pos_change_title, pos_change_body, neg_change_title, neg_change_body, cleared_title,
                 cleared_body):
        self.priority_styling = priority_styling
        self.content_to_pass = content_to_pass
        self.present_in_trends = present_in_trends
        self.new_title = new_title
        self.new_body = new_body
        self.ongoing_title = ongoing_title
        self.ongoing_body = ongoing_body
        self.pos_change_title = pos_change_title
        self.pos_change_body = pos_change_body
        self.neg_change_title = neg_change_title
        self.neg_change_body = neg_change_body
        self.cleared_title = cleared_title
        self.cleared_body = cleared_body

    def __setattr__(self, name, value):
        if name in ['present_in_trends']:
            if value is not None and not isinstance(value, bool):
                if value == '0':
                    value = False
                else:
                    value = True
        elif name in ['priority_styling']:
                if value is not None and not isinstance(value, int):
                    value = int(value)
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'priority_styling': self.priority_styling,
            'content_to_pass': self.content_to_pass,
            'present_in_trends': self.present_in_trends,
            'new_title': self.new_title,
            'new_body': self.new_body,
            'ongoing_title': self.ongoing_title,
            'ongoing_body': self.ongoing_body,
            'pos_change_title': self.pos_change_title,
            'pos_change_body': self.pos_change_body,
            'neg_change_title': self.neg_change_title,
            'neg_change_body': self.neg_change_body,
            'cleared_title': self.cleared_title,
            'cleared_body': self.cleared_body
        }

        return ret


class InsightsPlansDataItem(Serialisable):
    def __init__(self, priority_styling, content_to_pass, present_in_plans, cleared_title):
        self.priority_styling = priority_styling
        self.content_to_pass = content_to_pass
        self.present_in_plans = present_in_plans
        self.parent_data_item = None
        self.child_data_item = None
        self.cleared_title = cleared_title

    def __setattr__(self, name, value):
        if name in ['present_in_plans']:
            if value is not None and not isinstance(value, bool):
                if value == '0':
                    value = False
                else:
                    value = True
                # value = bool(value)
        elif name in ['priority_styling']:
            if value is not None and not isinstance(value, int):
                value = int(value)
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'priority_styling': self.priority_styling,
            'content_to_pass': self.content_to_pass,
            'present_in_plans': self.present_in_plans,
            'parent_data': self.parent_data_item.json_serialise(),
            'child_data': self.child_data_item.json_serialise(),
            'cleared_title': self.cleared_title
        }

        return ret


class InsightsParentDataItem(Serialisable):
    def __init__(self, enum, new_first_time_title, new_first_time_body, new_subsequent_title, new_subsequent_body,
                 cleared_body):
        self.enum = enum
        self.new_first_time_title = new_first_time_title
        self.new_first_time_body = new_first_time_body
        self.new_subsequent_title = new_subsequent_title
        self.new_subsequent_body = new_subsequent_body
        self.cleared_body = cleared_body

    def __setattr__(self, name, value):
        if name in ['enum']:
            if value is not None and not isinstance(value, TriggerType):
                if value == '':
                    value = None
                else:
                    value = TriggerType(int(value))
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'enum': self.enum.value if self.enum is not None else None,
            'new_first_time_title': self.new_first_time_title,
            'new_first_time_body': self.new_first_time_body,
            'new_subsequent_title': self.new_subsequent_title,
            'new_subsequent_body': self.new_subsequent_body,
            'cleared_body': self.cleared_body
        }

        return ret


class InsightsChildDataItem(Serialisable):
    def __init__(self, new_first_time_title, new_first_time_body, new_subsequent_title, new_subsequent_body,
                 cleared_body):
        self.new_first_time_title = new_first_time_title
        self.new_first_time_body = new_first_time_body
        self.new_subsequent_title = new_subsequent_title
        self.new_subsequent_body = new_subsequent_body
        self.cleared_body = cleared_body

    def json_serialise(self):
        ret = {
            'new_first_time_title': self.new_first_time_title,
            'new_first_time_body': self.new_first_time_body,
            'new_subsequent_title': self.new_subsequent_title,
            'new_subsequent_body': self.new_subsequent_body,
            'cleared_body': self.cleared_body
        }

        return ret


class InsightsDataItem(Serialisable):
    def __init__(self, trigger_enum, trend_type, triggers, goal_names, length_of_impact, data_source, insight_priority_plans, insight_priority_trend_type):
        self.trigger_enum = trigger_enum
        self.trend_type = trend_type
        self.triggers = triggers
        self.goal_names = goal_names
        self.length_of_impact = length_of_impact
        self.data_source = data_source
        self.insight_priority_plans = insight_priority_plans
        self.insight_priority_trend_type = insight_priority_trend_type
        self.plans_data_item = None
        self.trends_data_item = None
        self.plots_data_item = None
        self.cta_data_item = None

    def __setattr__(self, name, value):
        if name in ['trigger_enum']:
            if value is not None and not isinstance(value, TriggerType):
                if value == '':
                    value = None
                else:
                    value = TriggerType(int(value))
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'trigger_enum': self.trigger_enum.value,
            'trend_type': self.trend_type,
            'triggers': self.triggers,
            'goal_names': self.goal_names,
            'length_of_impact': self.length_of_impact,
            'data_source': self.data_source,
            'insight_priority_plans': self.insight_priority_plans,
            'insight_priority_trend_type': self.insight_priority_trend_type,
            'plans': self.plans_data_item.json_serialise(),
            'trends': self.trends_data_item.json_serialise(),
            'plots': self.plots_data_item.json_serialise(),
            'cta': self.cta_data_item.json_serialise(),
        }

        return ret

