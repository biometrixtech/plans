from enum import Enum, IntEnum


class AdaptationTypeMeasure(Enum):
    training_type = 0
    adaptation_type = 1
    sub_adaptation_type = 2
    detailed_adaptation_type = 3


class TrainingType(Enum):
    movement_prep = 0
    strength_cardiorespiratory = 1
    strength_endurance = 2
    strength_integrated_resistance = 3
    power_action_olympic_lift = 4
    power_action_plyometrics = 5
    power_drills_plyometrics = 6
    skill_development = 7
    flexibility = 8


class AdaptationType(Enum):
    not_tracked = None
    strength_endurance_cardiorespiratory = 1
    strength_endurance_strength = 2
    power_drill = 3
    maximal_strength_hypertrophic = 4
    power_explosive_action = 5


class DetailedAdaptationType(IntEnum):
    mobility = 0
    corrective = 1
    base_aerobic_training = 2
    anaerobic_threshold_training = 3
    high_intensity_anaerobic_training = 4
    stabilization_endurance = 5
    stabilization_strength = 6
    stabilization_power = 7
    functional_strength = 8
    muscular_endurance = 9
    strength_endurance = 10
    hypertrophy = 11
    maximal_strength = 12
    speed = 13
    sustained_power = 14
    power = 15
    maximal_power = 16


class SubAdaptationType(Enum):
    movement_efficiency = 0
    cardiorespiratory_training = 1
    core_strength = 2
    strength = 3
    power = 4


class AdaptationDictionary(object):

    def __init__(self):
        self.detailed_types = {}
        self.initialize()

    def initialize(self):
        self.detailed_types[DetailedAdaptationType.mobility] = SubAdaptationType.movement_efficiency
        self.detailed_types[DetailedAdaptationType.corrective] = SubAdaptationType.movement_efficiency
        self.detailed_types[DetailedAdaptationType.stabilization_endurance] = SubAdaptationType.core_strength
        self.detailed_types[DetailedAdaptationType.stabilization_strength] = SubAdaptationType.core_strength
        self.detailed_types[DetailedAdaptationType.stabilization_power] = SubAdaptationType.core_strength
        self.detailed_types[DetailedAdaptationType.base_aerobic_training] = SubAdaptationType.cardiorespiratory_training
        self.detailed_types[DetailedAdaptationType.anaerobic_threshold_training] = SubAdaptationType.cardiorespiratory_training
        self.detailed_types[DetailedAdaptationType.high_intensity_anaerobic_training] = SubAdaptationType.cardiorespiratory_training
        self.detailed_types[DetailedAdaptationType.functional_strength] = SubAdaptationType.strength
        self.detailed_types[DetailedAdaptationType.muscular_endurance] = SubAdaptationType.strength
        self.detailed_types[DetailedAdaptationType.strength_endurance] = SubAdaptationType.strength
        self.detailed_types[DetailedAdaptationType.hypertrophy] = SubAdaptationType.strength
        self.detailed_types[DetailedAdaptationType.maximal_strength] = SubAdaptationType.strength
        self.detailed_types[DetailedAdaptationType.speed] = SubAdaptationType.power
        self.detailed_types[DetailedAdaptationType.sustained_power] = SubAdaptationType.power
        self.detailed_types[DetailedAdaptationType.power] = SubAdaptationType.power
        self.detailed_types[DetailedAdaptationType.maximal_power] = SubAdaptationType.power


class CardioAction(Enum):
    race_walking = 0
    run = 1
    sprint = 2
    row = 3
    cycle = 4
    ski_erg = 5
    swim = 6
    ruck = 7


class PowerDrillAction(Enum):
    drills_speed_agility = 0
    hurdles_speed_agility = 1
    sprints_speed_agility = 2
    power_production = 3


class PowerAction(Enum):
    jump = 0
    throw = 1
    olympic_lift = 2
    strength_action = 3


class StrengthResistanceAction(Enum):
    olympic_lift = 0


class StrengthEnduranceAction(Enum):
    supine = 0
    prone = 1
    side_lying = 2
    quadruped = 3
    bridge = 4
    kneeling = 5
    half_kneeling = 6
    seated = 7
    double_leg = 8
    staggered_leg = 9
    split_leg = 10
    single_leg = 11


class BodyPosition(Enum):
    supine = 0
    prone = 1
    side_lying = 2
    quadruped = 3
    bridge = 4
    kneeling = 5
    half_kneeling = 6
    double_leg_standing = 7
    split_leg_standing = 8
    staggered_leg_standing = 9
    single_leg_standing = 10
    single_leg_moving = 11
    seated = 12
    double_leg_moving = 13
    split_leg_moving = 14
    non_stationary_other = 15
    hanging = 16
    upright_torso = 17
    staggered_leg_moving = 18


class Equipment(Enum):
    no_equipment = 0
    rower = 1
    airbike = 2
    bike = 3
    ski_erg = 4
    swimming = 5
    ruck = 6
    barbells = 7
    dumbbells = 8
    kettlebells = 9
    double_kettlebell = 10
    sandbags = 11
    atlas_stones = 12
    yoke = 13
    dip_belt = 14
    medicine_balls = 15
    sled = 16
    farmers_carry_handles = 17
    resistence_bands = 18
    machine = 19
    plate = 20
    assistance_resistence_bands = 21
    cable = 22
    barbell_without_plates = 23
    step = 24
    bodyweight = 25
    hex_bar = 26
    trx = 27
    mini_bands = 28
    single_dumbbell = 29

    def distribute_weights(self):
        if self.name in ['no_equipment', 'airbike', 'bike', 'swimming', 'dumbbells',
                         'double_kettlebells', 'bodyweight', 'mini_bands']:
            return False
        else:
            return True


class WeightDistribution(Enum):
    bilateral = 0
    bilateral_uneven = 1
    unilateral = 2
    unilateral_alternating = 3
    contralateral = 4


class MovementSurfaceStability(Enum):
    stable = 0
    unstable = 1
    very_unstable = 2


class Gender(Enum):
    female = 0
    male = 1


class RunningDistances(Enum):
    m100 = 0
    m200 = 1
    m300 = 2
    m400 = 3
    m500 = 4
    m600 = 5
    m800 = 6
    m1000 = 7
    m1200 = 8
    m1600 = 9
    m4000 = 10
    mile3 = 11
    k5 = 12
    mile5 = 12
    k10 = 14
    k12 = 15
    marathon_half = 16
    mile15 = 17
    k25 = 18
    marathon = 19
    k50 = 20
    mile50 = 21


class ProficiencyLevel(Enum):
    beginner = 0
    novice = 1
    intermediate = 2
    advanced = 3
    elite = 4
