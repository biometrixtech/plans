from enum import Enum


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
    non_stationary_single_leg = 11
    seated = 12
    non_stationary_double_leg = 13
    non_stationary_lunge = 14
    non_stationary_other = 15
    two_arms = 16
    single_arm = 17


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

    def distribute_weights(self):
        if self.name in ['no_equipment', 'airbike', 'bike', 'swimming', 'dumbbells', 'double_kettlebells']:
            return False
        else:
            return True


class WeightDistribution(Enum):
    bilateral = 0
    bilateral_uneven = 1
    unilateral = 2
    unilateral_alternating = 3


class MovementSurfaceStability(Enum):
    stable = 0
    unstable = 1
    very_unstable = 2
