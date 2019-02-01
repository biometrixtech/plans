from enum import Enum, IntEnum
from serialisable import Serialisable

class FitFatigueStatus(Enum):
    undefined = 0
    trending_toward_fatigue = 1
    trending_toward_fitness = 2


class TrainingVolumeGapType(Enum):
    acwr = 0
    fit_fatigue_ratio = 1
    freshness_index = 2
    monotony = 3
    ramp = 4
    strain = 5


class TrainingLevel(IntEnum):
    undertraining = -1
    optimal = 0
    overreaching = 1
    excessive = 2


class IndicatorLevel(IntEnum):
    low = 0
    moderate = 1
    high = 2


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


class StandardErrorRangeMetric(StandardErrorRange):
    def __init__(self, lower_bound=None, upper_bound=None, observed_value=None):
        StandardErrorRange.__init__(self, lower_bound, upper_bound, observed_value)
        self.training_volume_gaps = []

    def json_serialise(self):
        ret = {
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound,
            'observed_value': self.observed_value,
            'insufficient_data': self.insufficient_data,
            'training_volume_gaps': [x.json_serialise() for x in self.training_volume_gaps]
        }
        return ret

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


