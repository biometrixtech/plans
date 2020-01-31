from enum import Enum


class TrainingType(Enum):
    flexibility = 0
    cardiorespiratory = 1
    core = 2
    balance = 3
    plyometrics = 4
    speed_agility_quickness = 5
    integrated_resistance = 6
    olympic_lifting = 7
    skill_development = 8


class AdaptationType(Enum):
    not_tracked = None
    strength_indurance_cardiorespiratory = 1
    strength_indurance_strength = 2
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
    skierg = 9
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
