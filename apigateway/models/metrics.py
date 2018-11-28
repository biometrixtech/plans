from enum import Enum, IntEnum
from serialisable import Serialisable
from models.soreness import BodyPartLocationText


class AthleteMetric(Serialisable):
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

    def json_serialise(self):
        ret = {
               'name': self.name,
               'metric_type': self.metric_type.value,
               'color': self.color.value,
               'high_level_insight': self.high_level_insight.value,
               'high_level_action_description': self.high_level_action_description,
               'specific_insight_training_volume': self.specific_insight_training_volume,
               'specific_insight_recovery': self.specific_insight_recovery,
               # 'body_part_location': self.body_part_location,
               # 'body_part_side': self.body_part_side,
               # 'soreness': [s.json_serialise() for s in self.soreness],
               'specific_actions': self.specific_actions
              }
        return ret


class AthleteTrainingVolumeMetricGenerator(object):
    def __init__(self, name, metric_type, athlete_stats, threshold_attribute):
        self.name = name
        self.metric_type = metric_type
        self.athlete_stats = athlete_stats
        self.threshold_attribute = threshold_attribute
        self.thresholds = {}

    def populate_thresholds(self):

        for t, v in self.thresholds.items():
            if getattr(self.athlete_stats, self.threshold_attribute) is not None:
                if v.low_value is not None and v.high_value is not None:
                    if v.low_value <= getattr(self.athlete_stats, self.threshold_attribute) < v.high_value:
                        v.count += 1
                elif v.low_value is not None and v.high_value is None:
                    if v.low_value <= getattr(self.athlete_stats, self.threshold_attribute):
                        v.count += 1
                elif v.low_value is None and v.high_value is not None:
                    if v.high_value >= getattr(self.athlete_stats, self.threshold_attribute):
                        v.count += 1

    def get_metric_list(self):

        metric_list = []

        for key in sorted(self.thresholds.keys()):
            if self.thresholds[key].count > 0:
                metric = AthleteMetric(self.name, self.metric_type)
                metric.high_level_action_description = self.thresholds[key].high_level_action_description
                metric.specific_insight_training_volume = self.thresholds[key].specific_insight_training_volume
                metric.high_level_insight = self.thresholds[key].high_level_insight
                metric.specific_actions = self.thresholds[key].specific_actions
                metric.color = self.thresholds[key].color
                metric_list.append(metric)

        return metric_list


class AthleteSorenessMetricGenerator(object):
    def __init__(self, name, metric_type, soreness_list, threshold_attribute):
        self.name = name
        self.metric_type = metric_type
        self.soreness = soreness_list
        self.threshold_attribute = threshold_attribute
        self.thresholds = {}

    def populate_thresholds_with_soreness(self):

        for s in self.soreness:
            for t, v in self.thresholds.items():
                if v.low_value is not None and v.high_value is not None:
                    if v.low_value <= getattr(s, self.threshold_attribute) < v.high_value:
                        v.soreness_list.append(s)
                elif v.low_value is not None and v.high_value is None:
                    if v.low_value <= getattr(s, self.threshold_attribute):
                        v.soreness_list.append(s)
                elif v.low_value is None and v.high_value is not None:
                    if v.high_value >= getattr(s, self.threshold_attribute):
                        v.soreness_list.append(s)

    def get_body_part_text(self, text, soreness_list):

        body_part_list = []
        for soreness in soreness_list:
            try:
                part = BodyPartLocationText(soreness.body_part.location).value()
            except:
                part = BodyPartLocationText(soreness.body_part_location).value()
            side = soreness.side
            if side == 1:
                body_text = ' '.join(['left', part])
            elif side == 2:
                body_text = ' '.join(['right', part])
            else:  # side == 0:
                body_text = part

            body_part_list.append(body_text)
        if len(body_part_list) > 1:
            joined_text = ', '.join(body_part_list)
            pos = joined_text.rfind(',')
            joined_text = joined_text[:pos] + ' and' + joined_text[pos+1:]
            return text.format(bodypart=joined_text)
        elif len(body_part_list) == 1:
            joined_text = body_part_list[0]
            return text.format(bodypart=joined_text)
        else:
            return text

    def get_metric_list(self):

        metric_list = []

        for key in sorted(self.thresholds.keys()):
              if len(self.thresholds[key].soreness_list) > 0:
                  metric = AthleteMetric(self.name, self.metric_type)
                  metric.high_level_action_description = self.thresholds[key].high_level_action_description
                  metric.specific_insight_recovery = self.get_body_part_text(self.thresholds[key].specific_insight_recovery,
                                                                             self.thresholds[key].soreness_list)
                  metric.high_level_insight = self.thresholds[key].high_level_insight
                  metric.specific_actions = self.thresholds[key].specific_actions
                  metric.color = self.thresholds[key].color
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
                 high_value, specific_insight_recovery, specific_insight_training_volume):
        self.specific_actions = specific_actions
        self.color = metric_color
        self.high_level_description = ""
        self.high_level_action_description = high_level_action_description
        self.high_level_insight = high_level_insight
        self.specific_insight_recovery = specific_insight_recovery
        self.specific_insight_training_volume = specific_insight_training_volume
        self.low_value = low_value
        self.high_value = high_value
        self.soreness_list = []
        self.count = 0
