from enum import Enum


class TrainingType(Enum):
    flexibility = 0
    cardiorespiratory = 1
    core = 2
    balance = 3
    plyometrics = 4
    plyometrics_drills = 5
    speed_agility_quickness = 6
    integrated_resistance = 7
    olympic_lifting = 8
    skill_development = 9


class AdaptationType(Enum):
    not_tracked = None
    strength_endurance_cardiorespiratory = 1
    strength_endurance_strength = 2
    maximal_strength_hypertrophic = 3
    power_explosive_action = 4
    power_drill = 5


class MovementAction(Enum):
    walk = 0
    step = 1
    lunge = 2
    skips = 3
    jump = 4
    sprint = 5
    cut = 6
    row = 7
    cycle = 8
    ski_erg = 9
    swim_freestyle = 10
    ruck = 11
    run = 12


class BodyPosition(Enum):
    supine = 0
    prone = 1
    side = 2
    lying = 3
    quadruped = 4
    bridge = 5
    kneeling = 6
    half_kneeling = 7
    double_leg_standing = 8
    split_leg_standing = 9
    staggered_leg_standing = 10
    single_leg_standing = 11
    non_stationary = 12


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
    sandbags = 10
    atlas_stones = 11
    yoke = 12
    dip_belt = 13
    medicine_balls = 14
    sled = 15
    farmers_carry_handles = 16
    resistence_bands = 17
    machine = 18
