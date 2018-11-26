from enum import Enum


class AthleteRecommendation(object):
    def __init__(self):
        self.metric = ""
        self.metric_type = MetricType.daily
        self.threshold = 0.0
        self.color = ""
        self.high_level_insight = ""
        self.high_level_action_description = ""
        self.specific_insight_training_volume = ""
        self.specific_insight_recovery = ""
        self.body_part_location = None
        self.body_part_side = 0
        self.recommendations = []


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