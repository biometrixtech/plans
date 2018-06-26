from enum import Enum, IntEnum
import exercise


class LongTermRecovery(object):
    def __init__(self):
        self.expire_date_time = None
        self.active_recovery_exercises = []
        self.active_recovery_compressions = []
        self.nutrition_recommendation = None
        self.hydration_recommendation = None
        self.sleep_recommendation = None


class ActiveRecoveryExercise(exercise.Exercise):
    def __init__(self):
        exercise.Exercise.__init__(self)
        self.soreness_triggers = []     # body parts triggering this exercise
        self.injury_history_triggers = []   # injuries triggering this exercise


class CompressionLevel(IntEnum):
    ace_bandage = 0
    compression_sleeve_or_garment = 1


class ActiveRecoveryCompression(object):
    def __init__(self):
        self.soreness_triggers = []     # body parts triggering this exercise
        self.injury_history_triggers = []   # injuries triggering this exercise
        self.compression_level = CompressionLevel.ace_bandage


class ColdTherapyLevel(IntEnum):
    ice_bag_ice_pack = 0
    tub_with_ice = 1


class ActiveRecoveryColdTherapy(object):
    def __init__(self):
        self.soreness_triggers = []
        self.cold_therapy_level = ColdTherapyLevel.ice_bag_ice_pack


class NutritionRecommendation(object):
    def __init__(self):
        self.acwr_triggered = False
        self.upcoming_sessions_triggered = False    # sessions = practices or competitions
        self.recommendation = ""


class HydrationRecommendation(object):
    def __init__(self):
        self.upcoming_sessions_triggered = False
        self.session_intensity_RPE_triggered = False
        self.recommendation = ""


class SleepRecommendation(object):
    def __init__(self):
        self.upcoming_sessions_triggered = False
        self.session_intensity_RPE_triggered = False
        self.sleep_quality_triggered = False
        self.recommendation = ""
