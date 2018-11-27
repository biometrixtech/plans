from enum import Enum, IntEnum
from models.soreness import BodyPartLocationText


class AthleteMetric(object):
    def __init__(self, name, metric_type):
        self.name = name
        self.metric_type = metric_type
        self.color = None
        self.high_level_insight = None
        self.high_level_action_description = ""
        self.specific_insight_training_volume = ""
        self.specific_insight_recovery = ""
        #self.body_part_location = None
        #self.body_part_side = 0

        self.specific_actions = []


class AthleteMetricGenerator(object):
    def __init__(self, name, metric_type, soreness_list, threshold_attribute):
        self.name = name,
        self.metric_type = metric_type
        self.soreness = soreness_list
        self.threshold_attribute = threshold_attribute
        self.thresholds = {}

    def populate_thresholds_with_soreness(self):

        for s in self.soreness:
            for t, v in self.thresholds:
                if v.low_value is not None and v.high_value is not None:
                    if v.low_value <= getattr(s, self.threshold_attribute) < v.high_value:
                        v.soreness_list.append(s)
                if v.low_value is not None and v.high_value is None:
                    if v.low_value <= getattr(s, self.threshold_attribute):
                        v.soreness_list.append(s)
                if v.low_value is None and v.high_value is not None:
                    if v.high_value < getattr(s, self.threshold_attribute):
                        v.soreness_list.append(s)

    def get_body_part_text(self, text, soreness_list):

        body_part_list = []
        for soreness in soreness_list:
            part = BodyPartLocationText(soreness.body_part.location).value()
            side = soreness.side
            if side == 1:
                body_text = ' '.join(['left', part])
            elif side == 2:
                body_text = ' '.join(['right', part])
            else:  # side == 0:
                body_text = part

            body_part_list.append(body_text)
        joined_text = ', '.join(body_part_list)
        pos = joined_text.rfind(',')
        joined_text = joined_text[:pos] + ' and' + joined_text[pos+1:]

        return text.format(bodypart=joined_text)

    def get_metric_list(self):

        metric_list = []

        for key in sorted(self.thresholds.keys()):
            metric = AthleteMetric(self.name, self.metric_type)
            metric.high_level_action_description = self.thresholds[key].high_level_action_description
            metric.specific_insight_recovery = self.get_body_part_text(self.thresholds[key].specific_insight_recovery,
                                                                       self.thresholds[key].soreness_list)
            metric_list.append(metric)

        return metric_list


class MetricType(Enum):
    daily = 0
    longitudinal = 1


class DailyHighLevelInsight(Enum):
    all_good = 0
    increase_workload = 1
    limit_time_intensity_of_training = 2
    monitor_in_training = 3
    not_cleared_for_training = 4


class WeeklyHighLevelInsight(Enum):
    all_good = 0
    balance_overtraining_risk = 1
    add_variety_to_training_risk = 2
    increase_weekly_workload = 3
    address_pain_or_soreness = 4
    evaluate_health_status = 5


class MetricColor(IntEnum):
    green = 0
    yellow = 1
    red = 2


class ThresholdRecommendation(object):
    def __init__(self, metric_color, high_level_insight, high_level_action_description, specific_actions, low_value,
                 high_value, specific_insight_recovery):
        self.specific_actions = specific_actions
        self.color = metric_color
        self.high_level_description = ""
        self.high_level_action_description = high_level_action_description
        self.high_level_insight = high_level_insight
        self.specific_insight_recovery = specific_insight_recovery
        self.low_value = low_value
        self.high_value = high_value
        self.soreness_list = []






