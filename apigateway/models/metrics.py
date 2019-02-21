from enum import Enum, IntEnum
from serialisable import Serialisable
from models.soreness import BodyPartLocationText
from models.training_volume import StandardErrorRange


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
        self.insufficient_data_for_thresholds = False
        self.range_wider_than_thresholds = False


    def json_serialise(self):
        ret = {
               'name': self.name,
               'metric_type': self.metric_type.value,
               'color': self.color.value,
               'high_level_insight': self.high_level_insight.value,
               'high_level_action_description': self.high_level_action_description,
               'specific_insight_training_volume': self.specific_insight_training_volume,
               'specific_insight_recovery': self.specific_insight_recovery,
               'insufficient_data_for_thresholds': self.insufficient_data_for_thresholds,
               'range_wider_than_thresholds': self.range_wider_than_thresholds,
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
        self.insufficient_data_for_thresholds = False
        self.range_wider_than_thresholds = False

    def populate_thresholds(self):

        lowest_threshold_value = min(list(v.low_value for v in self.thresholds.values() if v.low_value is not None))
        highest_threshold_value = max(list(v.high_value for v in self.thresholds.values() if v.high_value is not None))

        for t, v in self.thresholds.items():
            if (getattr(self.athlete_stats, self.threshold_attribute) is not None and
                    isinstance(getattr(self.athlete_stats, self.threshold_attribute), StandardErrorRange)):
                self.process_standard_error_threshold_value(v, self.threshold_attribute)

            elif (getattr(self.athlete_stats, self.threshold_attribute) is not None and
                    isinstance(getattr(self.athlete_stats, self.threshold_attribute), list)):
                attribute_list = getattr(self.athlete_stats, self.threshold_attribute)
                for a in range(0, len(attribute_list)):
                    self.process_standard_error_threshold_value(v, self.threshold_attribute, a)

            elif getattr(self.athlete_stats, self.threshold_attribute) is not None:
                attribute_value = round(getattr(self.athlete_stats, self.threshold_attribute), 3)
                if v.low_value is not None and v.high_value is not None:
                    if v.low_value <= attribute_value < v.high_value:
                        v.count += 1
                elif v.low_value is not None and v.high_value is None:
                    if v.low_value <= attribute_value:
                        v.count += 1
                elif v.low_value is None and v.high_value is not None:
                    if v.high_value > attribute_value:
                        v.count += 1

        if (getattr(self.athlete_stats, self.threshold_attribute) is not None and
                isinstance(getattr(self.athlete_stats, self.threshold_attribute), StandardErrorRange)):
            sre = getattr(self.athlete_stats, self.threshold_attribute)
            if ((sre.lower_bound is not None and sre.lower_bound < lowest_threshold_value or
                sre.observed_value is not None and sre.observed_value < lowest_threshold_value or
                sre.upper_bound is not None and sre.upper_bound < lowest_threshold_value) and
                    (sre.lower_bound is not None and sre.lower_bound > highest_threshold_value or
                     sre.observed_value is not None and sre.observed_value > highest_threshold_value or
                     sre.upper_bound is not None and sre.upper_bound > highest_threshold_value)):
                self.range_wider_than_thresholds = True
        elif (getattr(self.athlete_stats, self.threshold_attribute) is not None and
              isinstance(getattr(self.athlete_stats, self.threshold_attribute), list)):
            attribute_list = getattr(self.athlete_stats, self.threshold_attribute)
            for a in range(0, len(attribute_list)):
                is_lower = False
                is_higher = True
                if ((attribute_list[a].lower_bound is not None and attribute_list[a].lower_bound < lowest_threshold_value or
                     attribute_list[a].observed_value is not None and attribute_list[a].observed_value < lowest_threshold_value or
                     attribute_list[a].upper_bound is not None and attribute_list[a].upper_bound < lowest_threshold_value)):
                    is_lower = True
                if((attribute_list[a].lower_bound is not None and attribute_list[a].lower_bound > highest_threshold_value or
                         attribute_list[a].observed_value is not None and attribute_list[a].observed_value > highest_threshold_value or
                         attribute_list[a].upper_bound is not None and attribute_list[a].upper_bound > highest_threshold_value)):
                    is_higher = True
                if is_lower and is_higher:
                    self.range_wider_than_thresholds = True

    def process_standard_error_threshold_value(self, v, threshold_attribute, index_value=None):
        observed_value = self.get_metric_value("observed_value", threshold_attribute, index_value)
        upper_bound_value = self.get_metric_value("upper_bound", threshold_attribute, index_value)
        lower_bound_value = self.get_metric_value("lower_bound", threshold_attribute, index_value)
        if v.low_value is not None and v.high_value is not None:
            if observed_value is not None and v.low_value <= observed_value < v.high_value:
                v.count += 1
            if lower_bound_value is not None and v.low_value <= lower_bound_value < v.high_value:
                v.lower_bound_count += 1
            if upper_bound_value is not None and v.low_value <= upper_bound_value < v.high_value:
                v.upper_bound_count += 1
        elif v.low_value is not None and v.high_value is None:
            if observed_value is not None and v.low_value <= observed_value:
                v.count += 1
            if lower_bound_value is not None and v.low_value <= lower_bound_value:
                v.lower_bound_count += 1
            if upper_bound_value is not None and v.low_value <= upper_bound_value:
                v.upper_bound_count += 1
        elif v.low_value is None and v.high_value is not None:
            if observed_value is not None and v.high_value > observed_value:
                v.count += 1
            if lower_bound_value is not None and v.high_value > lower_bound_value:
                v.lower_bound_count += 1
            if upper_bound_value is not None and v.high_value > upper_bound_value:
                v.upper_bound_count += 1
        if index_value is None:
            standard_error_range = getattr(self.athlete_stats, threshold_attribute)
        else:
            standard_error_range_list = getattr(self.athlete_stats, threshold_attribute)
            standard_error_range = standard_error_range_list[index_value]
        if (standard_error_range.insufficient_data or (
                (upper_bound_value is not None and v.upper_bound_count != v.count) or
                (lower_bound_value is not None and v.lower_bound_count != v.count))):
            v.insufficient_data = True
            self.insufficient_data_for_thresholds = True

    def get_metric_value(self, attribute, threshold_attribute, index_value):

        if index_value is None:
            try:
                value_object = getattr(self.athlete_stats, threshold_attribute)
                value = getattr(value_object, attribute)
            except:
                value = None
        else:
            try:
                value_object = getattr(self.athlete_stats, threshold_attribute)
                value = getattr(value_object[index_value], attribute)
            except:
                value = None
        value = round(value, 3) if value is not None else None
        return value

    def get_metric_list(self):

        metric_list = []

        for key in sorted(self.thresholds.keys()):
            if (self.thresholds[key].count > 0 or (self.thresholds[key].lower_bound_count is not None and self.thresholds[key].lower_bound_count > 0) or
                    (self.thresholds[key].upper_bound_count is not None and self.thresholds[key].upper_bound_count > 0)):
                metric = AthleteMetric(self.name, self.metric_type)
                metric.high_level_action_description = self.thresholds[key].high_level_action_description
                metric.specific_insight_training_volume = self.thresholds[key].specific_insight_training_volume
                metric.high_level_insight = self.thresholds[key].high_level_insight
                metric.specific_actions = [TextGenerator().get_specific_action(rec=rec) for rec in self.thresholds[key].specific_actions]
                metric.color = self.thresholds[key].color
                metric.insufficient_data_for_thresholds = self.insufficient_data_for_thresholds
                metric.range_wider_than_thresholds = self.range_wider_than_thresholds
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
                    if round(v.low_value, 2) <= getattr(s, self.threshold_attribute) < round(v.high_value, 2):
                        v.soreness_list.append(s)
                elif v.low_value is not None and v.high_value is None:
                    if round(v.low_value, 2) <= getattr(s, self.threshold_attribute):
                        v.soreness_list.append(s)
                elif v.low_value is None and v.high_value is not None:
                    if round(v.high_value, 2) > getattr(s, self.threshold_attribute):
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
    adapt_training_to_avoid_symptoms = 2
    monitor_modify_if_needed = 3
    seek_med_eval_to_clear_for_training = 4
    recovery_day_recommended = 5

    # all_good = 0
    # seek_med_eval_to_clear_for_training = 1
    # monitor_modify_if_needed = 2
    # adapt_training_to_avoid_symptoms = 3
    # recovery_day_recommended = 4


class WeeklyHighLevelInsight(Enum):
    all_good = 0
    at_risk_of_overtraining = 1
    low_variability_inhibiting_recovery = 2
    at_risk_of_undertraining = 3
    at_risk_of_time_loss_injury = 4
    seek_med_eval_to_clear_for_training = 5

    # all_good = 0
    # seek_med_eval_to_clear_for_training = 1
    # at_risk_of_overtraining = 2
    # low_variability_inhibiting_recovery = 3
    # at_risk_of_undertraining = 4
    # at_risk_of_time_loss_injury = 5


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
        self.lower_bound_count = 0
        self.upper_bound_count = 0
        self.insufficient_data = False


class TextGenerator(object):
    def get_specific_action(self, rec, soreness=None):
        text = RecommendationText(rec).value()

        if soreness is None:
            return SpecificAction(rec, text, True)
        else:
            return SpecificAction(rec, self.get_body_part_text(text, soreness), True)

    def get_body_part_text(self, text, soreness_list=[], pain_type=None):

        body_part_list = []

        is_historic = False

        try:
            soreness_list.sort(key=lambda x: x.body_part.location.value, reverse=False)
        except:
            soreness_list.sort(key=lambda x: x.body_part_location.value, reverse=False)
            is_historic = True

        for soreness in soreness_list:
            if is_historic:
                part = BodyPartLocationText(soreness.body_part_location).value()
                is_pain = soreness.is_pain
            else:
                part = BodyPartLocationText(soreness.body_part.location).value()
                is_pain = soreness.pain
            side = soreness.side
            if side == 1:
                body_text = " ".join(["left", part])
            elif side == 2:
                body_text = " ".join(["right", part])
            else:  # side == 0:
                body_text = part

            body_part_list.append(body_text)
        sore_type = "pain" if is_pain else "soreness"

        body_part_list = self.merge_bilaterals(body_part_list)

        if len(body_part_list) > 2:
            joined_text = ", ".join(body_part_list)
            pos = joined_text.rfind(",")
            joined_text = joined_text[:pos] + " and" + joined_text[pos+1:]
            text = text.format(bodypart=joined_text, is_pain=sore_type)
            return text[0].upper()+text[1:]
        elif len(body_part_list) == 2:
            if "left and right" not in body_part_list[0] and "left and right" not in body_part_list[1]:
                joined_text = ", ".join(body_part_list)
                pos = joined_text.rfind(",")
                joined_text = joined_text[:pos] + " and" + joined_text[pos + 1:]
                text = text.format(bodypart=joined_text, is_pain=sore_type)
                return text[0].upper()+text[1:]
            else:
                joined_text = ", ".join(body_part_list)
                text = text.format(bodypart=joined_text, is_pain=sore_type)
                return text[0].upper()+text[1:]
        elif len(body_part_list) == 1:
            joined_text = body_part_list[0]
            text = text.format(bodypart=joined_text, is_pain=sore_type)
            return text[0].upper()+text[1:]
        else:
            return text

    def merge_bilaterals(self, body_part_list):

        last_part = ""

        for b in range(0, len(body_part_list)):

            cleaned_part = body_part_list[b].replace("left ", "").replace("right ", "")
            if cleaned_part == last_part:
                body_part_list[b] = "left and right " + cleaned_part
                body_part_list[b - 1] = ""
            last_part = cleaned_part

        new_body_part_list = [x for x in body_part_list if x != ""]

        return new_body_part_list

class RecommendationText(object):
    def __init__(self, rec):
        self.rec = rec

    def value(self):
        recs = {"1A": "Auditing monthly training to intro variety in duration & intensity",
                "1B": "Adding more variety in training duration, intensity, & movements",
                "2A": "Considering not training today",
                "2B": "Shorter or lower than usual intensity training session",
                "2C": "Longer or higher than usual intensity training session",
                "3A": "Significantly decreasing workload this week",
                "3B": "Moderately decreasing workload this week",
                "3C": "Moderately increasing workload this week",
                "5A": "Seeking help from a medical professional before training",
                "5B": "Limiting your training, seeking medical advice if symptoms persist/worsen",
                "6A": "Stopping activity if {bodypart} {is_pain} is present",
                "6B": "Avoiding activities which trigger {bodypart} {is_pain}",
                "6C": "Monitoring {bodypart} in training. If symptoms persists, reduce training",
                "7A": "Completing Fathom's pre & post-training Mobility & Recovery exercises",
                "7B": "Completing Fathom's pre-training Mobility exercises",
                "8A": "Heat {bodypart} before training for 10 minutes",
                "9A": "Ice {bodypart} immediately after training for 20 minutes",
                "9B": "Ice bath for 10 minutes after training"
                }

        return recs[self.rec]

