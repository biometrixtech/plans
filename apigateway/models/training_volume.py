from enum import Enum, IntEnum
from serialisable import Serialisable
from statistics import mean

'''deprecated for now
class TrainingStatus(object):
    def __init__(self, training_level, projected_days_duration=0):
        self.training_level = training_level
        self.projected_days_duration = projected_days_duration
        self.limiting_metric = None
'''


class LoadMonitoringType(Enum):
    RPExDuration = 0
    HeartRateSHRZ = 1
    HeartRateTRIMP = 2
    RPExRunningDistance = 3
    RPExWalkingDistance = 4
    RPExCyclingDistance = 5
    RPExSwimmingDistance = 6
    AccumulatedGRF = 7
    CenterOfMassAcceleration = 8


class FitFatigueStatus(Enum):
    undefined = 0
    trending_toward_fatigue = 1
    trending_toward_fitness = 2


class LoadMonitoringMeasures(object):
    def __init__(self, load_monitoring_type, update_date):
        self.load_monitoring_type = load_monitoring_type
        self.acwr = None
        self.ramp = None
        self.monotony = None
        self.strain = None
        self.muscular_strain = None
        self.date_updated = update_date
        self.maintenance_level = None
        self.functional_overreaching_level = None
        self.potentially_nfo_level = None
        self.non_functional_overreaching_level = None


'''dep
class MuscularStrain(object):
    def __init__(self):
        self.previous_muscular_strain = None
        self.current_muscular_strain = None


class TrainingStrain(object):
    def __init__(self):
        self.value = None
        self.events = 0
        self.historical = []
'''

class Monotony(object):
    def __init__(self):
        self.value = None
        self.historical = []


'''deprecated for now
class TrainingVolumeGapType(Enum):
    acwr = 0
    fit_fatigue_ratio = 1
    freshness_index = 2
    monotony = 3
    ramp = 4
    strain = 5


class TrainingLevel(IntEnum):
    insufficient_data = 0
    undertraining = 1
    possibly_undertraining = 2
    optimal = 3
    possibly_overreaching = 4
    overreaching = 5
    possibly_excessive = 6
    excessive = 7


class IndicatorLevel(IntEnum):
    low = 0
    moderate = 1
    high = 2
'''


class StandardErrorRange(Serialisable):
    def __init__(self, lower_bound=None, upper_bound=None, observed_value=None):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.observed_value = observed_value
        self.insufficient_data = False

    def json_serialise(self):
        ret = {
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound,
            'observed_value': self.observed_value,
            'insufficient_data' : self.insufficient_data
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):

        error_range = cls()

        if isinstance(input_dict, int) or isinstance(input_dict, float):
            error_range.observed_value = input_dict
        elif isinstance(input_dict, dict):
            error_range.observed_value = input_dict.get('observed_value')
            error_range.lower_bound = input_dict.get('lower_bound')
            error_range.upper_bound = input_dict.get('upper_bound')
            error_range.insufficient_data = input_dict.get('insufficient_data', False)

        return error_range

    @staticmethod
    def get_min_from_error_range_list(error_range_list):

        lower_bound_list = [e.lower_bound for e in error_range_list if e.lower_bound is not None]
        observed_value_list = [e.observed_value for e in error_range_list if e.observed_value is not None]
        observed_value_list.extend(lower_bound_list)

        if len(observed_value_list) > 0:
            return min(observed_value_list)
        else:
            return None

    @staticmethod
    def get_max_from_error_range_list(error_range_list):

        upper_bound_list = [e.upper_bound for e in error_range_list if e.upper_bound is not None]
        observed_value_list = [e.observed_value for e in error_range_list if e.observed_value is not None]
        observed_value_list.extend(upper_bound_list)

        if len(observed_value_list) > 0:
            return max(observed_value_list)
        else:
            return None

    @staticmethod
    def get_average_from_error_range_list(error_range_list):

        upper_bound_list = [e.upper_bound for e in error_range_list if e.upper_bound is not None]
        observed_value_list = [e.observed_value for e in error_range_list if e.observed_value is not None]
        lower_bound_list = [e.lower_bound for e in error_range_list if e.lower_bound is not None]

        average_range = StandardErrorRange()

        if len(lower_bound_list) > 0:
            average_range.lower_bound = mean(lower_bound_list)
        if len(observed_value_list) > 0:
            average_range.observed_value = mean(observed_value_list)
        if len(upper_bound_list) > 0:
            average_range.upper_bound = mean(upper_bound_list)

        return average_range

    def lowest_value(self):

        if self.lower_bound is not None:
            return self.lower_bound
        else:
            return self.observed_value

    def highest_value(self):

        if self.upper_bound is not None:
            return self.upper_bound
        else:
            return self.observed_value

    def plagiarize(self):

        new_object = StandardErrorRange(lower_bound=self.lower_bound, upper_bound=self.upper_bound, observed_value=self.observed_value)
        new_object.insufficient_data = self.insufficient_data
        return new_object

    def add(self, standard_error_range):
        if standard_error_range is not None and standard_error_range.lower_bound is not None:
            if self.lower_bound is None:
                self.lower_bound = standard_error_range.lower_bound
            else:
                self.lower_bound += standard_error_range.lower_bound
        if standard_error_range is not None and standard_error_range.upper_bound is not None:
            if self.upper_bound is None:
                self.upper_bound = standard_error_range.upper_bound
            else:
                self.upper_bound += standard_error_range.upper_bound
        if standard_error_range is not None and standard_error_range.observed_value is not None:
            if self.observed_value is None:
                self.observed_value = standard_error_range.observed_value
            else:
                self.observed_value += standard_error_range.observed_value

        # TODO: verify the assumption present in the following line: insufficient data trumps sufficient data
        if standard_error_range is not None:
            self.insufficient_data = min(self.insufficient_data, standard_error_range.insufficient_data)

    def add_value(self, number_value):
        if number_value is not None :
            if self.lower_bound is not None:
                self.lower_bound = self.lower_bound + number_value
        if number_value is not None:
            if self.upper_bound is not None:
                self.upper_bound = self.upper_bound + number_value
        if number_value is not None:
            if self.observed_value is not None:
                self.observed_value = self.observed_value + number_value
            else:
                self.observed_value = number_value

    def subtract_value(self, number_value):
        if number_value is not None :
            if self.lower_bound is not None:
                self.lower_bound = self.lower_bound - number_value
        if number_value is not None:
            if self.upper_bound is not None:
                self.upper_bound = self.upper_bound - number_value
        if number_value is not None:
            if self.observed_value is not None:
                self.observed_value = self.observed_value - number_value

        # TODO: verify the assumption present in the following line: insufficient data trumps sufficient data
        #if standard_error_range is not None:
        #    self.insufficient_data = min(self.insufficient_data, standard_error_range.insufficient_data)

    def multiply(self, factor):
        if self.lower_bound is not None:
            self.lower_bound = self.lower_bound * factor
        if self.upper_bound is not None:
            self.upper_bound = self.upper_bound * factor
        if self.observed_value is not None:
            self.observed_value = self.observed_value * factor

    def divide(self, factor):
        if self.lower_bound is not None:
            self.lower_bound = self.lower_bound / factor
        if self.upper_bound is not None:
            self.upper_bound = self.upper_bound / factor
        if self.observed_value is not None:
            self.observed_value = self.observed_value / factor

    def divide_range(self, standard_error_range):
        if standard_error_range is not None and standard_error_range.lower_bound is not None and self.lower_bound is not None:
            if standard_error_range.lower_bound > 0:
                self.lower_bound = self.lower_bound / float(standard_error_range.lower_bound)
        if standard_error_range is not None and standard_error_range.upper_bound is not None and self.upper_bound is not None:
            if standard_error_range.upper_bound > 0:
                self.upper_bound = self.upper_bound / float(standard_error_range.upper_bound)
        if standard_error_range is not None and standard_error_range.observed_value is not None and self.observed_value is not None:
            if standard_error_range.observed_value > 0:
                self.observed_value = self.observed_value / float(standard_error_range.observed_value)

    def max(self, standard_error_range):
        if standard_error_range is not None and standard_error_range.lower_bound is not None:
            if self.lower_bound is None:
                self.lower_bound = standard_error_range.lower_bound
            else:
                self.lower_bound = max(self.lower_bound, standard_error_range.lower_bound)
        if standard_error_range is not None and standard_error_range.upper_bound is not None:
            if self.upper_bound is None:
                self.upper_bound = standard_error_range.upper_bound
            else:
                self.upper_bound = max(self.upper_bound, standard_error_range.upper_bound)
        if standard_error_range is not None and standard_error_range.observed_value is not None:
            if self.observed_value is None:
                self.observed_value = standard_error_range.observed_value
            else:
                self.observed_value = max(self.observed_value, standard_error_range.observed_value)

        # TODO: verify the assumption present in the following line: insufficient data trumps sufficient data
        if standard_error_range is not None:
            self.insufficient_data = min(self.insufficient_data, standard_error_range.insufficient_data)

    def min(self, standard_error_range):
        if standard_error_range is not None and standard_error_range.lower_bound is not None:
            if self.lower_bound is None:
                self.lower_bound = standard_error_range.lower_bound
            else:
                self.lower_bound = min(self.lower_bound, standard_error_range.lower_bound)
        if standard_error_range is not None and standard_error_range.upper_bound is not None:
            if self.upper_bound is None:
                self.upper_bound = standard_error_range.upper_bound
            else:
                self.upper_bound = min(self.upper_bound, standard_error_range.upper_bound)
        if standard_error_range is not None and standard_error_range.observed_value is not None:
            if self.observed_value is None:
                self.observed_value = standard_error_range.observed_value
            else:
                self.observed_value = min(self.observed_value, standard_error_range.observed_value)

        # TODO: verify the assumption present in the following line: insufficient data trumps sufficient data
        if standard_error_range is not None:
            self.insufficient_data = min(self.insufficient_data, standard_error_range.insufficient_data)

class StandardErrorRangeMetric(StandardErrorRange):
    def __init__(self, lower_bound=None, upper_bound=None, observed_value=None):
        StandardErrorRange.__init__(self, lower_bound, upper_bound, observed_value)
        self.lower_bound_gap = None
        self.upper_bound_gap = None
        self.observed_value_gap = None

    def json_serialise(self):
        ret = {
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound,
            'observed_value': self.observed_value,
            'insufficient_data': self.insufficient_data,
            'lower_bound_gaps': self.lower_bound_gap,
            'upper_bound_gaps': self.upper_bound_gap,
            'observed_value_gaps': self.observed_value_gap,
        }
        return ret

'''deprecated for now
class TrainingVolumeGap(object):
    def __init__(self, low_optimal_threshold=None, low_overreaching_threshold=None, low_excessive_threshold=None, gap_type=None):
        #self.low_threshold = low_threshold
        #self.high_threshold = high_threshold
        self.low_optimal_threshold = low_optimal_threshold
        self.low_overreaching_threshold = low_overreaching_threshold
        self.low_excessive_threshold = low_excessive_threshold
        self.high_optimal_threshold = None
        self.high_overreaching_threshold = None
        self.high_excessive_threshold = None

        self.training_volume_gap_type = gap_type
        #self.internal_freshness_index = None
        #self.internal_acwr = None
        #self.internal_ramp = None
        #self.internal_monotony_index = None
        #self.internal_strain = None
        #self.training_level = None
        #self.performance_focused = False
        #self.competition_focused = False
        #self.need_for_variability = None
        #self.historic_soreness = []


class SuggestedTrainingDay(object):
    def __init__(self, user_id, date_time, low_optimal_threshold=None, low_overreaching_threshold=None, low_excessive_threshold=None,):
        self.user_id = user_id
        self.date_time = date_time
        #self.low_threshold = low_threshold
        #self.high_threshold = high_threshold
        #self.target_load = 0
        #self.most_limiting_gap_type_low = None
        #self.most_limiting_gap_type_high = None
        self.low_optimal_threshold = low_optimal_threshold
        self.low_optimal_gap_type = None
        self.low_overreaching_threshold = low_overreaching_threshold
        self.low_overreaching_gap_type = None
        self.low_excessive_threshold = low_excessive_threshold
        self.low_excessive_gap_type = None
        self.high_optimal_threshold = None
        self.high_optimal_gap_type = None
        self.high_overreaching_threshold = None
        self.high_overreaching_gap_type = None
        self.high_excessive_threshold = None
        self.high_excessive_gap_type = None
        self.training_volume_gaps_opt = []
        self.training_volume_gaps_ovr = []
        self.training_volume_gaps_exc = []
        self.training_volume_gaps_opt_high = []
        self.training_volume_gaps_ovr_high = []
        self.training_volume_gaps_exc_high = []
        self.matching_workouts = []


class TrainingReport(object):
    def __init__(self, user_id):
        self.user_id = user_id
        #self.low_threshold = low_threshold
        #self.high_threshold = high_threshold
        self.internal_freshness_index = None
        self.internal_acwr = None
        self.internal_ramp = None
        self.internal_monotony_index = None
        self.internal_strain = None
        #self.training_volume_gaps_opt = []
        #self.most_limiting_gap_type_low = None
        #self.most_limiting_gap_type_high = None
        self.training_level = None
        self.performance_focused = False
        self.competition_focused = False
        self.need_for_variability = None
        self.low_hs_severity = None
        self.high_hs_severity = None
        self.average_hs_severity = None
        self.acute_min_rpe = None
        self.acute_max_rpe = None
        self.acute_avg_rpe = None
        self.chronic_min_rpe = None
        self.chronic_max_rpe = None
        self.chronic_avg_rpe = None
        self.rpe_acwr = None
        self.acute_duration_minutes = None
        self.acute_min_duration_minutes = None
        self.acute_max_duration_minutss = None
        self.acute_avg_duration_minutes = None
        self.chronic_min_duration_minutes = None
        self.chronic_max_duration_minutes = None
        self.chronic_avg_duration_minutes = None
        self.chronic_duration_minutes = None
        self.acute_chronic_duration_minutes = None
        self.suggested_training_days = []
'''

