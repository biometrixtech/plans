from enum import Enum

from models.exposure import TrainingExposure, TargetTrainingExposure
from models.movement_tags import DetailedAdaptationType
from models.training_volume import StandardErrorRange

class PeriodizationGoalType(Enum):
    #building_foundation_proficiency_move_well = 5
    increase_cardiovascular_health = 10
    lose_weight = 15
    increase_cardio_endurance = 20
    increase_cardio_endurance_with_speed = 25
    increase_strength_max_strength = 30
    increase_athleticism_high_force = 35
    increase_athleticism_low_force = 40
    #increase_functional_strength = 45
    #increase_general_fitness = 50


class PeriodizationGoal(object):
    def __init__(self, periodization_goal_type):
        self.periodization_goal_type = periodization_goal_type
        self.target_training_exposures = []


class PeriodizationGoalFactory(object):

    def create(self, periodization_goal_type):
        goal = PeriodizationGoal(periodization_goal_type)
        weekly_load_20_30_percentage = StandardErrorRange(lower_bound=20, upper_bound=30)
        weekly_load_10_20_percentage = StandardErrorRange(lower_bound=10, upper_bound=20)
        base_training = [TrainingExposure(DetailedAdaptationType.base_aerobic_training)]
        base_training_long = [TrainingExposure(DetailedAdaptationType.base_aerobic_training,
                                               weekly_load_percentage=weekly_load_20_30_percentage)]
        base_training_short_mod = [TrainingExposure(DetailedAdaptationType.base_aerobic_training,
                                                    weekly_load_percentage=weekly_load_10_20_percentage)]
        anaerobic_threshold = [TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training)]
        strength_endurance_strength = [TrainingExposure(DetailedAdaptationType.strength_endurance)]
        high_intensity_anaerobic_training = [TrainingExposure(DetailedAdaptationType.high_intensity_anaerobic_training)]
        speed = TrainingExposure(DetailedAdaptationType.speed)
        sustained_power = TrainingExposure(DetailedAdaptationType.sustained_power)
        power = TrainingExposure(DetailedAdaptationType.power)
        speed_sustained_power_power =[speed, sustained_power, power]

        one_required_count = StandardErrorRange(observed_value=1)
        one_two_required_count = StandardErrorRange(lower_bound=1, upper_bound=2)
        two_three_required_count = StandardErrorRange(lower_bound=2, upper_bound=3)

        if periodization_goal_type == PeriodizationGoalType.increase_cardio_endurance:

            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=base_training_long, exposure_count=one_required_count.plagiarize(), priority=1))
            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=anaerobic_threshold, exposure_count=one_required_count.plagiarize(), priority=2))
            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=base_training_short_mod, exposure_count=two_three_required_count.plagiarize(), priority=3))
            # ignoring correctives for now
            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=strength_endurance_strength, exposure_count=two_three_required_count.plagiarize(), priority=5))
            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=high_intensity_anaerobic_training, exposure_count=one_two_required_count.plagiarize(), priority=6))

        if periodization_goal_type == PeriodizationGoalType.increase_athleticism_low_force:

            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=speed_sustained_power_power, exposure_count=two_three_required_count.plagiarize(), priority=1))
            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=anaerobic_threshold, exposure_count=one_two_required_count.plagiarize(), priority=2))
            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=high_intensity_anaerobic_training, exposure_count=one_two_required_count.plagiarize(), priority=2))
            # ignoring correctives for now
            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=base_training, exposure_count=one_two_required_count.plagiarize(), priority=4))
            goal.target_training_exposures.append(
                TargetTrainingExposure(training_exposures=strength_endurance_strength, exposure_count=one_two_required_count.plagiarize(), priority=5))

        return goal

