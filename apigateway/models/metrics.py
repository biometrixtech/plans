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
               'specific_actions': [s.json_serialise() for s in self.specific_actions]
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
                metric.specific_actions = [TextGenerator().get_specific_action(rec=rec) for rec in self.thresholds[key].specific_actions]
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
                    if v.high_value > getattr(s, self.threshold_attribute):
                        v.soreness_list.append(s)

    def get_metric_list(self):

        metric_list = []

        for key in sorted(self.thresholds.keys()):
            if len(self.thresholds[key].soreness_list) > 0:
                metric = AthleteMetric(self.name, self.metric_type)
                metric.high_level_action_description = self.thresholds[key].high_level_action_description
                metric.specific_insight_recovery = TextGenerator().get_body_part_text(self.thresholds[key].specific_insight_recovery,
                                                                                    self.thresholds[key].soreness_list)
                metric.high_level_insight = self.thresholds[key].high_level_insight
                metric.specific_actions = [TextGenerator().get_specific_action(rec=rec, soreness=self.thresholds[key].soreness_list) for rec in self.thresholds[key].specific_actions]
                metric.color = self.thresholds[key].color
                metric_list.append(metric)

        return metric_list


class MetricType(Enum):
    daily = 0
    longitudinal = 1


class SpecificAction(Serialisable):
    def __init__(self, code, text, display):
        self.code = code
        self.text = text
        self.display = display

    def json_serialise(self):
        ret = {
               'code': self.code,
               'text': self.text,
               'display': self.display
                }
        return ret


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


class TextGenerator(object):
    def get_specific_action(self, rec, soreness=None):
        text = RecommendationText(rec).value()

        if soreness is None:
            return SpecificAction(rec, text, True)
        else:
            return SpecificAction(rec, self.get_body_part_text(text, soreness), True)

    def get_body_part_text(self, text, soreness_list=[], pain_type=None):

        body_part_list = []
        for soreness in soreness_list:
            try:
                part = BodyPartLocationText(soreness.body_part.location).value()
                is_pain = soreness.pain
            except:
                part = BodyPartLocationText(soreness.body_part_location).value()
                is_pain = soreness.is_pain
            side = soreness.side
            if side == 1:
                body_text = " ".join(["left", part])
            elif side == 2:
                body_text = " ".join(["right", part])
            else:  # side == 0:
                body_text = part

            body_part_list.append(body_text)
        sore_type = "pain" if is_pain else "soreness"
        if len(body_part_list) > 1:
            joined_text = ", ".join(body_part_list)
            pos = joined_text.rfind(",")
            joined_text = joined_text[:pos] + " and" + joined_text[pos+1:]
            return text.format(bodypart=joined_text, is_pain=sore_type)
        elif len(body_part_list) == 1:
            joined_text = body_part_list[0]
            return text.format(bodypart=joined_text, is_pain=sore_type)
        else:
            return text

class RecommendationText(object):
    def __init__(self, rec):
        self.rec = rec

    def value(self):
        recs = {"1A": "Creating a periodized plan for the next month to introduce a variety of different stimuli",
                "1B": "Increasing variety in your training regimen",
                "2A": "Considering not training today",
                "2B": "A shorter or lower-intensity training session",
                "2C": "Exposure to a longer or higher-intensity training session",
                "3A": "Drastically decreasing workload this week",
                "3B": "Consider decreasing weekly workload",
                "3C": "Consider increasing weekly workload",
                "5A": "Seeking help from a medical professional",
                "5B": "Limiting your training. Seek medical advice if symptoms persist after warm-up.",
                "6A": "Stopping activity if {bodypart} {is_pain} present",
                "6B": "Modifying training so all activity is free of {bodypart} {is_pain}",
                "6C": "Monitoring {bodypart} symptoms during training. If symptoms persists, consider decreasing training in the next few days to allow recovery",
                "7A": "Completing Fathom's personalized Prep & Recovery",
                "7B": "Completing Fathom's Prep",
                "8A": "Heat {bodypart} before training for 10 minutes",
                "9A": "Ice {bodypart} immediately after training for 20 minutes",
                "9C": "Ice bath for 10 minutes after training"
                }

        return recs[self.rec]

