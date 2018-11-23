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
