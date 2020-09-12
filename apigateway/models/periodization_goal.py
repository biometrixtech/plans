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


class TrainingPersona(Enum):
    beginner = 0
    novice = 1
    intermediate = 2
    advanced = 3
    elite = 4


class PeriodizationGoal(object):
    def __init__(self, periodization_goal_type):
        self.periodization_goal_type = periodization_goal_type
        self.training_exposures = []


class AthleteCardioCapacity(object):
    def __init__(self):
        self.base_aerobic_training = None
        self.anaerobic_threshold_training = None
        self.high_intensity_anaerobic_training = None


class AthletePowerCapacity(object):
    def __init__(self):
        self.speed = None
        self.sustained_power = None
        self.power = None
        self.maximal_power = None


class AthleteStrengthCapacity(object):
    def __init__(self):
        self.muscular_endurance = None
        self.strength_endurance = None
        self.hypertrophy = None
        self.maximal_strength = None


class AthleteBaselineCapacities(object):
    def __init__(self):
        # Cardio
        self.base_aerobic_training = None
        self.anaerobic_threshold_training = None
        self.high_intensity_anaerobic_training = None
        # Strength
        self.muscular_endurance = None
        self.strength_endurance = None
        self.hypertrophy = None
        self.maximal_strength = None
        # Power
        self.speed = None
        self.sustained_power = None
        self.power = None
        self.maximal_power = None
        # Personas
        self.cardio_training_persona = TrainingPersona.beginner
        self.power_training_persona = TrainingPersona.beginner
        self.strength_training_persona = TrainingPersona.beginner


class TrainingUnit(object):
    def __init__(self, rpe=None, volume=None):
        self.rpe = rpe
        self.volume = volume


class AthleteDefaultCapacityFactory(object):

    def get_default_cardio_capacity(self, training_persona):

        athlete_capacity = AthleteCardioCapacity()

        if training_persona == TrainingPersona.beginner:

            athlete_capacity.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=5 * 60))
            athlete_capacity.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=None)
            athlete_capacity.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=None)

        elif training_persona == TrainingPersona.novice:

            athlete_capacity.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=5 * 60))
            athlete_capacity.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=4 * 60))
            athlete_capacity.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=None)

        elif training_persona == TrainingPersona.intermediate:

            athlete_capacity.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            athlete_capacity.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=9 * 60))
            athlete_capacity.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=1 * 60))

        elif training_persona == TrainingPersona.advanced:

            athlete_capacity.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            athlete_capacity.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=12 * 60))
            athlete_capacity.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=2 * 60))

        elif training_persona == TrainingPersona.elite:

            athlete_capacity.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            athlete_capacity.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=15 * 60))
            athlete_capacity.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=2 * 60))

        return athlete_capacity

    def get_default_power_capacity(self, training_persona):

        athlete_capacity = AthletePowerCapacity()

        return athlete_capacity

    def get_default_strength_capacity(self, training_persona):

        athlete_capacity = AthleteStrengthCapacity()

        if training_persona == TrainingPersona.beginner:

            athlete_capacity.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=48))
            athlete_capacity.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=None)
            athlete_capacity.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=None)

        elif training_persona == TrainingPersona.novice:

            athlete_capacity.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=60))
            athlete_capacity.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=None)
            athlete_capacity.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=None)

        elif training_persona == TrainingPersona.intermediate:

            athlete_capacity.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=72))
            athlete_capacity.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange(observed_value=72))
            athlete_capacity.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=None)

        elif training_persona == TrainingPersona.advanced:

            athlete_capacity.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=84))
            athlete_capacity.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange(observed_value=90))
            athlete_capacity.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange(observed_value=4))

        elif training_persona == TrainingPersona.elite:

            athlete_capacity.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=96))
            athlete_capacity.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange(observed_value=108))
            athlete_capacity.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange(observed_value=5))

        return athlete_capacity


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

            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=base_training_long, exposure_count=one_required_count, priority=1))
            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=anaerobic_threshold, exposure_count=one_required_count, priority=2))
            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=base_training_short_mod, exposure_count=two_three_required_count, priority=3))
            # ignoring correctives for now
            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=strength_endurance_strength, exposure_count=two_three_required_count, priority=5))
            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=high_intensity_anaerobic_training, exposure_count=one_two_required_count, priority=6))

        if periodization_goal_type == PeriodizationGoalType.increase_athleticism_low_force:

            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=speed_sustained_power_power, exposure_count=two_three_required_count, priority=1))
            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=anaerobic_threshold, exposure_count=two_three_required_count, priority=2))
            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=high_intensity_anaerobic_training, exposure_count=two_three_required_count, priority=2))
            # ignoring correctives for now
            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=base_training, exposure_count=one_two_required_count, priority=4))
            goal.training_exposures.append(
                TargetTrainingExposure(training_exposures=strength_endurance_strength, exposure_count=one_two_required_count, priority=5))

        return goal

