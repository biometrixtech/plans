from enum import Enum, IntEnum


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


class TrainingVolumeGap(object):
    def __init__(self, low_threshold=None, high_threshold=None, gap_type=None):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.training_volume_gap_type = gap_type
        self.internal_freshness_index = None
        self.internal_acwr = None
        self.internal_ramp = None
        self.internal_monotony_index = None
        self.internal_strain = None
        self.training_level = None
        self.performance_focused = False
        self.competition_focused = False
        self.need_for_variability = None


class TrainingReport(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.internal_freshness_index = None
        self.internal_acwr = None
        self.internal_ramp = None
        self.internal_monotony_index = None
        self.internal_strain = None
        self.training_volume_gaps = []
        self.most_limiting_gap_type = None
        self.training_level = None
        self.performance_focused = False
        self.competition_focused = False
        self.need_for_variability = None


