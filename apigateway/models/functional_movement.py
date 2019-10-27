from enum import IntEnum, Enum
from serialisable import Serialisable
from models.sport import SportName
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.body_parts import BodyPart, BodyPartFactory
from datetime import timedelta, date
from utils import format_date, parse_date


class FunctionalMovementType(Enum):
    ankle_dorsiflexion = 0
    ankle_plantar_flexion = 1
    inversion_of_the_foot = 2
    eversion_of_the_foot = 3
    knee_flexion = 4
    knee_extension = 5
    tibial_external_rotation = 6
    tibial_internal_rotation = 7
    hip_adduction = 8
    hip_abduction = 9
    hip_internal_rotation = 10
    hip_external_rotation = 11
    hip_extension = 12
    hip_flexion = 13
    pelvic_anterior_tilt = 14
    pelvic_posterior_tilt = 15
    trunk_flexion = 16
    trunk_extension = 17
    trunk_lateral_flexion = 18
    trunk_rotation = 19
    trunk_flexion_and_rotation = 20
    trunk_extension_with_rotation = 21


class BodyPartFunction(Enum):
    prime_mover = 0
    antagonist = 1
    synergist = 2


class FunctionalMovement(object):
    def __init__(self, functional_movement_type):
        self.functional_movement_type = functional_movement_type
        self.prime_movers = []
        self.antagonists = []
        self.synergists = []


class Elasticity(Serialisable):
    def __init__(self):
        self.elasticity = 0.0
        self.y_adf = 0.0

    def json_serialise(self):
        ret = {
            'elasticity': self.elasticity,
            'y_adf': self.y_adf
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        elasticity_data = cls()
        elasticity_data.elasticity = input_dict.get("elasticity", 0.0)
        elasticity_data.y_adf = input_dict.get("y_adf", 0.0)
        return elasticity_data


class LeftRightElasticity(Serialisable):
    def __init__(self):
        self.left = None
        self.right = None

    def json_serialise(self):
        ret = {
            'left': self.left.json_serialise() if self.left is not None else None,
            'right': self.right.json_serialise() if self.right is not None else None
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        left_right = cls()
        left_right.left = Elasticity.json_deserialise(input_dict["left"]) if input_dict.get("left") is not None else None
        left_right.right = Elasticity.json_deserialise(input_dict["right"]) if input_dict.get("right") is not None else None
        return left_right


class MovementPatterns(Serialisable):
    def __init__(self):
        self.apt_ankle_pitch = None
        self.hip_drop_apt = None
        self.hip_drop_pva = None
        self.knee_valgus_hip_drop = None
        self.knee_valgus_pva = None
        self.knee_valgus_apt = None

    def json_serialise(self):
        ret = {
            'apt_ankle_pitch': self.apt_ankle_pitch.json_serialise() if self.apt_ankle_pitch is not None else None,
            'hip_drop_apt': self.hip_drop_apt.json_serialise() if self.hip_drop_apt is not None else None,
            'hip_drop_pva': self.hip_drop_pva.json_serialise() if self.hip_drop_pva is not None else None,
            'knee_valgus_hip_drop': self.knee_valgus_hip_drop.json_serialise() if self.knee_valgus_hip_drop is not None else None,
            'knee_valgus_pva': self.knee_valgus_pva.json_serialise() if self.knee_valgus_pva is not None else None,
            'knee_valgus_apt': self.knee_valgus_apt.json_serialise() if self.knee_valgus_apt is not None else None,
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        movement_patterns = cls()
        movement_patterns.apt_ankle_pitch = LeftRightElasticity.json_deserialise(
            input_dict['apt_ankle_pitch']) if input_dict.get('apt_ankle_pitch') is not None else None
        movement_patterns.hip_drop_apt = LeftRightElasticity.json_deserialise(
            input_dict['hip_drop_apt']) if input_dict.get('hip_drop_apt') is not None else None
        movement_patterns.hip_drop_pva = LeftRightElasticity.json_deserialise(
            input_dict['hip_drop_pva']) if input_dict.get('hip_drop_pva') is not None else None
        movement_patterns.knee_valgus_hip_drop = LeftRightElasticity.json_deserialise(
            input_dict['knee_valgus_hip_drop']) if input_dict.get('knee_valgus_hip_drop') is not None else None
        movement_patterns.knee_valgus_pva = LeftRightElasticity.json_deserialise(
            input_dict['knee_valgus_pva']) if input_dict.get('knee_valgus_pva') is not None else None
        movement_patterns.knee_valgus_apt = LeftRightElasticity.json_deserialise(
            input_dict['knee_valgus_apt']) if input_dict.get('knee_valgus_apt') is not None else None
        return movement_patterns


class CompensationSource(Enum):
    internal_processing = 0
    movement_patterns_3s = 1


class BodyPartInjuryRisk(object):
    def __init__(self):
        # volume
        self.concentric_volume_last_week = 0
        self.concentric_volume_this_week = 0
        self.prime_mover_concentric_volume_last_week = 0
        self.prime_mover_concentric_volume_this_week = 0
        self.synergist_concentric_volume_last_week = 0
        self.synergist_concentric_volume_this_week = 0
        self.synergist_compensating_concentric_volume_last_week = 0
        self.synergist_compensating_concentric_volume_this_week = 0

        self.eccentric_volume_last_week = 0
        self.eccentric_volume_this_week = 0
        self.prime_mover_eccentric_volume_last_week = 0
        self.prime_mover_eccentric_volume_this_week = 0
        self.synergist_eccentric_volume_last_week = 0
        self.synergist_eccentric_volume_this_week = 0
        self.synergist_compensating_eccentric_volume_last_week = 0
        self.synergist_compensating_eccentric_volume_this_week = 0

        self.prime_mover_concentric_volume_today = 0
        self.prime_mover_eccentric_volume_today = 0

        self.synergist_concentric_volume_today = 0
        self.synergist_eccentric_volume_today = 0
        self.synergist_compensating_concentric_volume_today = 0
        self.synergist_compensating_eccentric_volume_today = 0

        self.total_volume_ramp_today = 0
        self.eccentric_volume_ramp_today = 0

        # intensity
        self.concentric_intensity_last_week = 0
        self.concentric_intensity_this_week = 0
        self.prime_mover_concentric_intensity_last_week = 0
        self.prime_mover_concentric_intensity_this_week = 0
        self.synergist_concentric_intensity_last_week = 0
        self.synergist_concentric_intensity_this_week = 0
        self.synergist_compensating_concentric_intensity_last_week = 0
        self.synergist_compensating_concentric_intensity_this_week = 0

        self.eccentric_intensity_last_week = 0
        self.eccentric_intensity_this_week = 0
        self.prime_mover_eccentric_intensity_last_week = 0
        self.prime_mover_eccentric_intensity_this_week = 0
        self.synergist_eccentric_intensity_last_week = 0
        self.synergist_eccentric_intensity_this_week = 0
        self.synergist_compensating_eccentric_intensity_last_week = 0
        self.synergist_compensating_eccentric_intensity_this_week = 0

        #self.concentric_intensity_today = 0
        #self.eccentric_intensity_today = 0

        self.prime_mover_concentric_intensity_today = 0
        self.prime_mover_eccentric_intensity_today = 0
        self.prime_mover_total_intensity_today = 0

        self.synergist_concentric_intensity_today = 0
        self.synergist_eccentric_intensity_today = 0
        self.synergist_total_intensity_today = 0
        self.synergist_compensating_concentric_intensity_today = 0
        self.synergist_compensating_eccentric_intensity_today = 0
        self.synergist_compensating_total_intensity_today = 0
        
        self.compensating_causes_volume_today = []
        self.compensating_causes_intensity_today = []
        self.compensating_source_volume = None
        self.compensating_source_intensity = None

        self.last_compensation_date = None
        self.compensation_count_last_0_20_days = 0

        # ache
        self.ache_count_last_0_10_days = 0
        # self.ache_count_last_0_10_days = 0 # 0 to 10
        self.ache_count_last_0_20_days = 0 # 0 to 20
        self.last_ache_level = 0
        self.last_ache_date = None

        # excessive strain
        self.last_excessive_strain_date = None
        self.last_non_functional_overreaching_date = None
        self.last_functional_overreaching_date = None
        
        # inflammation
        self.last_inflammation_date = None

        # knots
        self.knots_count_last_0_20_days = 0
        self.last_knots_level = 0
        self.last_knots_date = None

        # muscle spasm
        self.last_muscle_spasm_date = None

        # adhesions
        self.last_adhesions_date = None

        # inhibited
        self.last_inhibited_date = None

        # long
        self.last_long_date = None
        self.long_count_last_0_20_days = 0

        # overactive / underactive
        self.last_overactive_date = None
        self.last_underactive_date = None
        self.overactive_count_last_0_20_days = 0
        self.underactive_inhibited_count_last_0_20_days = 0
        self.underactive_weak_count_last_0_20_days = 0

        # sharp
        self.sharp_count_last_0_10_days = 0  
        self.sharp_count_last_0_20_days = 0  # 0-20
        self.last_sharp_level = 0
        self.last_sharp_date = None

        # short
        self.last_short_date = None
        self.short_count_last_0_20_days = 0

        # tight
        self.tight_count_last_0_20_days = 0  # 0-20
        self.last_tight_level = 0
        self.last_tight_date = None

        # weak
        self.last_weak_date = None

        # muscle_imbalance = None
        self.last_muscle_imbalance_date = None

        # joints and ligaments
        self.last_tendinopathy_date = None
        self.last_tendinosis_date = None
        self.last_altered_joint_arthokinematics_date = None

    def json_serialise(self):
        return {
                "concentric_volume_last_week": self.concentric_volume_last_week,
                "concentric_volume_this_week": self.concentric_volume_this_week,
                "prime_mover_concentric_volume_last_week": self.prime_mover_concentric_volume_last_week,
                "prime_mover_concentric_volume_this_week": self.prime_mover_concentric_volume_this_week,
                "synergist_concentric_volume_last_week": self.synergist_concentric_volume_last_week,
                "synergist_concentric_volume_this_week": self.synergist_concentric_volume_this_week,
                "synergist_compensating_concentric_volume_last_week": self.synergist_compensating_concentric_volume_last_week,
                "synergist_compensating_concentric_volume_this_week": self.synergist_compensating_concentric_volume_this_week,
                #"concentric_volume_today": self.concentric_volume_today,
                "eccentric_volume_last_week": self.eccentric_volume_last_week,
                "eccentric_volume_this_week": self.eccentric_volume_this_week,
                #"eccentric_volume_today": self.eccentric_volume_today,

                "prime_mover_eccentric_volume_last_week": self.prime_mover_eccentric_volume_last_week,
                "prime_mover_eccentric_volume_this_week": self.prime_mover_eccentric_volume_this_week,
                "synergist_eccentric_volume_last_week": self.synergist_eccentric_volume_last_week,
                "synergist_eccentric_volume_this_week": self.synergist_eccentric_volume_this_week,
                "synergist_compensating_eccentric_volume_last_week": self.synergist_compensating_eccentric_volume_last_week,
                "synergist_compensating_eccentric_volume_this_week": self.synergist_compensating_eccentric_volume_this_week,

                "prime_mover_concentric_volume_today": self.prime_mover_concentric_volume_today,

                "prime_mover_eccentric_volume_today": self.prime_mover_eccentric_volume_today,

                "synergist_concentric_volume_today": self.synergist_concentric_volume_today,
                "synergist_eccentric_volume_today": self.synergist_eccentric_volume_today,
                "synergist_compensating_concentric_volume_today": self.synergist_compensating_concentric_volume_today,
                "synergist_compensating_eccentric_volume_today": self.synergist_compensating_eccentric_volume_today,

                "total_volume_ramp_today": self.total_volume_ramp_today,
                "eccentric_volume_ramp_today": self.eccentric_volume_ramp_today,

                "concentric_intensity_last_week": self.concentric_intensity_last_week,
                "concentric_intensity_this_week": self.concentric_intensity_this_week,
                #"concentric_intensity_today": self.concentric_intensity_today,
                "eccentric_intensity_last_week": self.eccentric_intensity_last_week,
                "eccentric_intensity_this_week": self.eccentric_intensity_this_week,
                #"eccentric_intensity_today": self.eccentric_intensity_today,
                "prime_mover_concentric_intensity_last_week": self.prime_mover_concentric_intensity_last_week,
                "prime_mover_concentric_intensity_this_week": self.prime_mover_concentric_intensity_this_week,
                "prime_mover_concentric_intensity_today": self.prime_mover_concentric_intensity_today,
                "prime_mover_eccentric_intensity_last_week": self.prime_mover_eccentric_intensity_last_week,
                "prime_mover_eccentric_intensity_this_week": self.prime_mover_eccentric_intensity_this_week,
                "prime_mover_eccentric_intensity_today": self.prime_mover_eccentric_intensity_today,
                "synergist_concentric_intensity_last_week": self.synergist_concentric_intensity_last_week,
                "synergist_concentric_intensity_this_week": self.synergist_concentric_intensity_this_week,
                "synergist_concentric_intensity_today": self.synergist_concentric_intensity_today,
                "synergist_eccentric_intensity_last_week": self.synergist_eccentric_intensity_last_week,
                "synergist_eccentric_intensity_this_week": self.synergist_eccentric_intensity_this_week,
                "synergist_eccentric_intensity_today": self.synergist_eccentric_intensity_today,
                "synergist_compensating_concentric_intensity_last_week": self.synergist_compensating_concentric_intensity_last_week,
                "synergist_compensating_concentric_intensity_this_week": self.synergist_compensating_concentric_intensity_this_week,
                "synergist_compensating_concentric_intensity_today": self.synergist_compensating_concentric_intensity_today,
                "synergist_compensating_eccentric_intensity_last_week": self.synergist_compensating_eccentric_intensity_last_week,
                "synergist_compensating_eccentric_intensity_this_week": self.synergist_compensating_eccentric_intensity_this_week,
                "synergist_compensating_eccentric_intensity_today": self.synergist_compensating_eccentric_intensity_today,

                "compensating_causes_volume_today": [c.json_serialise() for c in self.compensating_causes_volume_today],
                "compensating_causes_intensity_today": [c.json_serialise() for c in self.compensating_causes_intensity_today],
                
                "compensating_source_volume": self.compensating_source_volume.value if self.compensating_source_volume is not None else None,
                "compensating_source_intensity": self.compensating_source_intensity.value if self.compensating_source_intensity is not None else None,
                "last_compensation_date": format_date(self.last_compensation_date),
                "compensation_count_last_0_20_days": self.compensation_count_last_0_20_days,
                
                # ache
                "ache_count_last_0_10_days": self.ache_count_last_0_10_days,
                # "ache_count_last_0_10_days": self.ache_count_last_0_10_days,
                "ache_count_last_0_20_days": self.ache_count_last_0_20_days,
                "last_ache_level": self.last_ache_level,
                "last_ache_date": format_date(self.last_ache_date),

                # excessive strain
                "last_excessive_strain_date": format_date(self.last_excessive_strain_date),
                "last_non_functional_overreaching_date": format_date(self.last_non_functional_overreaching_date),
                "last_functional_overreaching_date": format_date(self.last_functional_overreaching_date),
                

                # inflammation
                "last_inflammation_date": format_date(self.last_inflammation_date),

                # knots
                "knots_count_last_0_20_days": self.knots_count_last_0_20_days,
                "last_knots_level": self.last_knots_level,
                "last_knots_date": format_date(self.last_knots_date),

                # muscle spasm
                "last_muscle_spasm_date": format_date(self.last_muscle_spasm_date),

                # adhesions
                "last_adhesions_date": format_date(self.last_adhesions_date),

                # inhibited
                "last_inhibited_date": format_date(self.last_inhibited_date),

                # long
                "last_long_date": format_date(self.last_long_date),
                "long_count_last_0_20_days": self.long_count_last_0_20_days,

                # overactive / underactive
                "last_overactive_date": format_date(self.last_overactive_date),
                "last_underactive_date": format_date(self.last_underactive_date),
                'overactive_count_last_0_20_days': self.overactive_count_last_0_20_days,
                'underactive_inhibited_count_last_0_20_days': self.underactive_inhibited_count_last_0_20_days,
                'underactive_weak_count_last_0_20_days': self.underactive_weak_count_last_0_20_days,

                # sharp
                "sharp_count_last_0_10_days": self.sharp_count_last_0_10_days,
                "sharp_count_last_0_20_days": self.sharp_count_last_0_20_days,
                "last_sharp_level": self.last_sharp_level,
                "last_sharp_date": format_date(self.last_sharp_date),

                # short
                "last_short_date": format_date(self.last_short_date),
                "short_count_last_0_20_days": self.short_count_last_0_20_days,

                # tight
                "tight_count_last_0_20_days": self.tight_count_last_0_20_days,
                "last_tight_level": self.last_tight_level,
                "last_tight_date": format_date(self.last_tight_date),

                # weak
                "last_weak_date": format_date(self.last_weak_date),

                # muscle imbalance
                "last_muscle_imbalance_date": format_date(self.last_muscle_imbalance_date),

                # joints and ligaments
                "last_tendinopathy_date": format_date(self.last_tendinopathy_date),
                "last_tendinosis_date": format_date(self.last_tendinosis_date),
                "last_altered_joint_arthokinematics_date": format_date(self.last_altered_joint_arthokinematics_date),

        }

    @classmethod
    def json_deserialise(cls, input_dict):
        injury_risk = cls()
        injury_risk.concentric_volume_last_week = input_dict.get('concentric_volume_last_week', 0)
        injury_risk.concentric_volume_this_week = input_dict.get('concentric_volume_this_week', 0)
        injury_risk.eccentric_volume_last_week = input_dict.get('eccentric_volume_last_week', 0)
        injury_risk.eccentric_volume_this_week = input_dict.get('eccentric_volume_this_week', 0)

        injury_risk.prime_mover_concentric_volume_last_week = input_dict.get('prime_mover_concentric_volume_last_week', 0)
        injury_risk.prime_mover_concentric_volume_this_week = input_dict.get('prime_mover_concentric_volume_this_week', 0)
        injury_risk.prime_mover_concentric_volume_today = input_dict.get('prime_mover_concentric_volume_today', 0)
        injury_risk.prime_mover_eccentric_volume_last_week = input_dict.get('prime_mover_eccentric_volume_last_week', 0)
        injury_risk.prime_mover_eccentric_volume_this_week = input_dict.get('prime_mover_eccentric_volume_this_week', 0)
        injury_risk.prime_mover_eccentric_volume_today = input_dict.get('prime_mover_eccentric_volume_today', 0)

        injury_risk.synergist_concentric_volume_last_week = input_dict.get('synergist_concentric_volume_last_week', 0)
        injury_risk.synergist_concentric_volume_this_week = input_dict.get('synergist_concentric_volume_this_week', 0)
        injury_risk.synergist_concentric_volume_today = input_dict.get('synergist_concentric_volume_today', 0)
        injury_risk.synergist_eccentric_volume_last_week = input_dict.get('synergist_eccentric_volume_last_week', 0)
        injury_risk.synergist_eccentric_volume_this_week = input_dict.get('synergist_eccentric_volume_this_week', 0)
        injury_risk.synergist_eccentric_volume_today = input_dict.get('synergist_eccentric_volume_today', 0)
        injury_risk.synergist_compensating_concentric_volume_last_week = input_dict.get('synergist_compensating_concentric_volume_last_week', 0)
        injury_risk.synergist_compensating_concentric_volume_this_week = input_dict.get('synergist_compensating_concentric_volume_this_week', 0)
        injury_risk.synergist_compensating_concentric_volume_today = input_dict.get('synergist_compensating_concentric_volume_today', 0)
        injury_risk.synergist_compensating_eccentric_volume_last_week = input_dict.get('synergist_compensating_eccentric_volume_last_week', 0)
        injury_risk.synergist_compensating_eccentric_volume_this_week = input_dict.get('synergist_compensating_eccentric_volume_this_week', 0)
        injury_risk.synergist_compensating_eccentric_volume_today = input_dict.get('synergist_compensating_eccentric_volume_today', 0)

        injury_risk.total_volume_ramp_today = input_dict.get('total_volume_ramp_today')
        injury_risk.eccentric_volume_ramp_today = input_dict.get('eccentric_volume_ramp_today')

        injury_risk.concentric_intensity_last_week = input_dict.get('concentric_intensity_last_week', 0)
        injury_risk.concentric_intensity_this_week = input_dict.get('concentric_intensity_this_week', 0)
        injury_risk.concentric_intensity_today = input_dict.get('concentric_intensity_today', 0)
        injury_risk.eccentric_intensity_last_week = input_dict.get('eccentric_intensity_last_week', 0)
        injury_risk.eccentric_intensity_this_week = input_dict.get('eccentric_intensity_this_week', 0)
        injury_risk.eccentric_intensity_today = input_dict.get('eccentric_intensity_today', 0)

        injury_risk.prime_mover_concentric_intensity_last_week = input_dict.get('prime_mover_concentric_intensity_last_week', 0)
        injury_risk.prime_mover_concentric_intensity_this_week = input_dict.get('prime_mover_concentric_intensity_this_week', 0)
        injury_risk.prime_mover_concentric_intensity_today = input_dict.get('prime_mover_concentric_intensity_today', 0)
        injury_risk.prime_mover_eccentric_intensity_last_week = input_dict.get('prime_mover_eccentric_intensity_last_week', 0)
        injury_risk.prime_mover_eccentric_intensity_this_week = input_dict.get('prime_mover_eccentric_intensity_this_week', 0)
        injury_risk.prime_mover_eccentric_intensity_today = input_dict.get('prime_mover_eccentric_intensity_today', 0)

        injury_risk.synergist_concentric_intensity_last_week = input_dict.get('synergist_concentric_intensity_last_week', 0)
        injury_risk.synergist_concentric_intensity_this_week = input_dict.get('synergist_concentric_intensity_this_week', 0)
        injury_risk.synergist_concentric_intensity_today = input_dict.get('synergist_concentric_intensity_today', 0)
        injury_risk.synergist_eccentric_intensity_last_week = input_dict.get('synergist_eccentric_intensity_last_week', 0)
        injury_risk.synergist_eccentric_intensity_this_week = input_dict.get('synergist_eccentric_intensity_this_week', 0)
        injury_risk.synergist_eccentric_intensity_today = input_dict.get('synergist_eccentric_intensity_today', 0)
        injury_risk.synergist_compensating_concentric_intensity_last_week = input_dict.get('synergist_compensating_concentric_intensity_last_week', 0)
        injury_risk.synergist_compensating_concentric_intensity_this_week = input_dict.get('synergist_compensating_concentric_intensity_this_week', 0)
        injury_risk.synergist_compensating_concentric_intensity_today = input_dict.get('synergist_compensating_concentric_intensity_today', 0)
        injury_risk.synergist_compensating_eccentric_intensity_last_week = input_dict.get('synergist_compensating_eccentric_intensity_last_week', 0)
        injury_risk.synergist_compensating_eccentric_intensity_this_week = input_dict.get('synergist_compensating_eccentric_intensity_this_week', 0)
        injury_risk.synergist_compensating_eccentric_intensity_today = input_dict.get('synergist_compensating_eccentric_intensity_today', 0)

        injury_risk.compensating_causes_volume_today = [BodyPartSide.json_deserialise(c) for c in
                                                  input_dict.get('compensating_causes_volume_today', [])]
        injury_risk.compensating_causes_intensity_today = [BodyPartSide.json_deserialise(c) for c in
                                                  input_dict.get('compensating_causes_intensity_today', [])]

        injury_risk.last_compensation_date = input_dict.get('last_compensation_date')

        injury_risk.compensating_source_volume = CompensationSource(
            input_dict['compensating_source_volume']) if input_dict.get(
            "compensating_source_volume") is not None else None
        injury_risk.compensating_source_intensity = CompensationSource(
            input_dict['compensating_source_intensity']) if input_dict.get(
            "compensating_source_intensity") is not None else None

        injury_risk.compensation_count_last_0_20_days = input_dict.get('compensation_count_last_0_20_days', 0)

        # ache
        injury_risk.ache_count_last_0_10_days = input_dict.get('ache_count_last_0_10_days', 0)
        injury_risk.ache_count_last_0_20_days = input_dict.get('ache_count_last_0_20_days', 0)
        injury_risk.last_ache_level = input_dict.get('last_ache_level', 0)
        injury_risk.last_ache_date = input_dict.get('last_ache_date')

        # excessive strain
        injury_risk.last_excessive_strain_date = input_dict.get('last_excessive_strain_date')
        injury_risk.last_non_functional_overreaching_date = input_dict.get('last_non_functional_overreaching_date')
        injury_risk.last_functional_overreaching_date = input_dict.get('last_functional_overreaching_date')

        # inflammation
        injury_risk.last_inflammation_date = input_dict.get('last_inflammation_date')

        # knots
        injury_risk.knots_count_last_0_20_days = input_dict.get('knots_count_last_0_20_days', 0)
        injury_risk.last_knots_level = input_dict.get('last_knots_level', 0)
        injury_risk.last_knots_date = input_dict.get('last_knots_date')

        # muscle spasm
        injury_risk.last_muscle_spasm_date = input_dict.get('last_muscle_spasm_date')

        # adhesions
        injury_risk.last_adhesions_date = input_dict.get('last_adhesions_date')

        # inhibited
        injury_risk.last_inhibited_date = input_dict.get('last_inhibited_date')

        # long
        injury_risk.last_long_date = input_dict.get('last_long_date')
        injury_risk.long_count_last_0_20_days = input_dict.get('long_count_last_0_20_days', 0)

        # overactive / underactive
        injury_risk.last_overactive_date = input_dict.get('last_overactive_date')
        injury_risk.last_underactive_date = input_dict.get('last_underactive_date')
        injury_risk.overactive_count_last_0_20_days = input_dict.get('overactive_count_last_0_20_days',0)
        injury_risk.underactive_inhibited_count_last_0_20_days = input_dict.get('underactive_inhibited_count_last_0_20_days', 0)
        injury_risk.underactive_weak_count_last_0_20_days = input_dict.get('underactive_weak_count_last_0_20_days', 0)

        # sharp
        injury_risk.sharp_count_last_0_10_days = input_dict.get('sharp_count_last_0_10_days', 0)
        injury_risk.sharp_count_last_0_20_days = input_dict.get('sharp_count_last_0_20_days', 0)
        injury_risk.last_sharp_level = input_dict.get('last_sharp_level', 0)
        injury_risk.last_sharp_date = input_dict.get('last_sharp_date')

        # short
        injury_risk.last_short_date = input_dict.get('last_short_date')
        injury_risk.short_count_last_0_20_days = input_dict.get('short_count_last_0_20_days', 0)

        # tight
        injury_risk.tight_count_last_0_20_days = input_dict.get('tight_count_last_0_20_days', 0)
        injury_risk.last_tight_level = input_dict.get('last_tight_level', 0)
        injury_risk.last_tight_date = input_dict.get('last_tight_date')

        # weak
        injury_risk.last_weak_date = input_dict.get('last_weak_date')

        # muscle imbalance
        injury_risk.last_muscle_imbalance_date = input_dict.get('last_muscle_imbalance_date')

        # joints and ligaments
        injury_risk.last_tendinopathy_date = input_dict.get('last_tendinopathy_date')
        injury_risk.last_tendinosis_date = input_dict.get('last_tendinosis_date')
        injury_risk.last_altered_joint_arthokinematics_date = input_dict.get('last_altered_joint_arthokinematics_date')

        return injury_risk

    def __setattr__(self, name, value):
        if 'date' in name:
            if value is not None and not isinstance(value, date):
                value = parse_date(value).date()
        super().__setattr__(name, value)

    def merge(self, body_part_injury_risk):

        self.concentric_volume_last_week = max(self.concentric_volume_last_week, body_part_injury_risk.concentric_volume_last_week)
        self.concentric_volume_this_week = max(self.concentric_volume_this_week, body_part_injury_risk.concentric_volume_this_week)
        #self.concentric_volume_today = max(self.concentric_volume_today, body_part_injury_risk.concentric_volume_today)
        self.eccentric_volume_last_week = max(self.eccentric_volume_last_week, body_part_injury_risk.eccentric_volume_last_week)
        self.eccentric_volume_this_week = max(self.eccentric_volume_this_week, body_part_injury_risk.eccentric_volume_this_week)
        #self.eccentric_volume_today = max(self.eccentric_volume_today, body_part_injury_risk.eccentric_volume_today)

        self.prime_mover_concentric_volume_last_week = max(self.prime_mover_concentric_volume_last_week, body_part_injury_risk.prime_mover_concentric_volume_last_week)
        self.prime_mover_concentric_volume_this_week = max(self.prime_mover_concentric_volume_this_week, body_part_injury_risk.prime_mover_concentric_volume_this_week)
        self.prime_mover_concentric_volume_today = max(self.prime_mover_concentric_volume_today, body_part_injury_risk.prime_mover_concentric_volume_today)
        self.prime_mover_eccentric_volume_last_week = max(self.prime_mover_eccentric_volume_last_week, body_part_injury_risk.prime_mover_eccentric_volume_last_week)
        self.prime_mover_eccentric_volume_this_week = max(self.prime_mover_eccentric_volume_this_week, body_part_injury_risk.prime_mover_eccentric_volume_this_week)
        self.prime_mover_eccentric_volume_today = max(self.prime_mover_eccentric_volume_today, body_part_injury_risk.prime_mover_eccentric_volume_today)

        self.synergist_concentric_volume_last_week = max(self.synergist_concentric_volume_last_week, body_part_injury_risk.synergist_concentric_volume_last_week)
        self.synergist_concentric_volume_this_week = max(self.synergist_concentric_volume_this_week, body_part_injury_risk.synergist_concentric_volume_this_week)
        self.synergist_concentric_volume_today = max(self.synergist_concentric_volume_today, body_part_injury_risk.synergist_concentric_volume_today)
        self.synergist_eccentric_volume_last_week = max(self.synergist_eccentric_volume_last_week, body_part_injury_risk.synergist_eccentric_volume_last_week)
        self.synergist_eccentric_volume_this_week = max(self.synergist_eccentric_volume_this_week, body_part_injury_risk.synergist_eccentric_volume_this_week)
        self.synergist_eccentric_volume_today = max(self.synergist_eccentric_volume_today, body_part_injury_risk.synergist_eccentric_volume_today)

        # ache
        self.ache_count_last_0_10_days = max(self.ache_count_last_0_10_days, body_part_injury_risk.ache_count_last_0_10_days)
        self.ache_count_last_0_10_days = max(self.ache_count_last_0_10_days, body_part_injury_risk.ache_count_last_0_10_days)
        self.ache_count_last_0_20_days = max(self.ache_count_last_0_20_days, body_part_injury_risk.ache_count_last_0_20_days)
        self.last_ache_level = max(self.last_ache_level, body_part_injury_risk.last_ache_level)
        self.last_ache_date = self.merge_with_none(self.last_ache_date, body_part_injury_risk.last_ache_date)

        # excessive strain
        self.last_excessive_strain_date = self.merge_with_none(self.last_excessive_strain_date, body_part_injury_risk.last_excessive_strain_date)
        self.last_non_functional_overreaching_date = self.merge_with_none(self.last_non_functional_overreaching_date, body_part_injury_risk.last_non_functional_overreaching_date)
        self.last_functional_overreaching_date = self.merge_with_none(self.last_functional_overreaching_date, body_part_injury_risk.last_functional_overreaching_date)
        self.last_compensation_date = self.merge_with_none(self.last_compensation_date, body_part_injury_risk.last_compensation_date)

        # inflammation
        self.last_inflammation_date = self.merge_with_none(self.last_inflammation_date, body_part_injury_risk.last_inflammation_date)

        # knots
        self.last_knots_level = max(self.last_knots_level, body_part_injury_risk.last_knots_level)
        self.last_knots_date = self.merge_with_none(self.last_knots_date, body_part_injury_risk.last_knots_date)

        # muscle spasm
        self.last_muscle_spasm_date = self.merge_with_none(self.last_muscle_spasm_date, body_part_injury_risk.last_muscle_spasm_date)

        # adhesions
        self.last_adhesions_date = self.merge_with_none(self.last_adhesions_date, body_part_injury_risk.last_adhesions_date)

        # inhibited
        self.last_inhibited_date = self.merge_with_none(self.last_inhibited_date, body_part_injury_risk.last_inhibited_date)

        # long
        self.last_long_date = self.merge_with_none(self.last_long_date, body_part_injury_risk.last_long_date)
        self.long_count_last_0_20_days = max(self.long_count_last_0_20_days, body_part_injury_risk.long_count_last_0_20_days)

        # overactive / underactive
        self.last_overactive_date = self.merge_with_none(self.last_overactive_date, body_part_injury_risk.last_overactive_date)
        self.last_underactive_date = self.merge_with_none(self.last_underactive_date, body_part_injury_risk.last_underactive_date)
        self.overactive_count_last_0_20_days = max(self.overactive_count_last_0_20_days, body_part_injury_risk.overactive_count_last_0_20_days)
        self.underactive_inhibited_count_last_0_20_days = max(self.underactive_inhibited_count_last_0_20_days,
                                                   body_part_injury_risk.underactive_inhibited_count_last_0_20_days)
        self.underactive_weak_count_last_0_20_days = max(self.underactive_weak_count_last_0_20_days,
                                                   body_part_injury_risk.underactive_weak_count_last_0_20_days)

        # sharp
        self.sharp_count_last_0_10_days = max(self.sharp_count_last_0_10_days, body_part_injury_risk.sharp_count_last_0_10_days)
        self.sharp_count_last_0_20_days = max(self.sharp_count_last_0_20_days, body_part_injury_risk.sharp_count_last_0_20_days)
        self.last_sharp_level = max(self.last_sharp_level, body_part_injury_risk.last_sharp_level)
        self.last_sharp_date = self.merge_with_none(self.last_sharp_date, body_part_injury_risk.last_sharp_date)

        # short
        self.last_short_date = self.merge_with_none(self.last_short_date, body_part_injury_risk.last_short_date)

        # tight
        self.tight_count_last_0_20_days = max(self.tight_count_last_0_20_days, body_part_injury_risk.tight_count_last_0_20_days)
        self.last_tight_level = max(self.last_tight_level, body_part_injury_risk.last_tight_level)
        self.last_tight_date = self.merge_with_none(self.last_tight_date, body_part_injury_risk.last_tight_date)

        # weak
        self.last_weak_date = self.merge_with_none(self.last_weak_date, body_part_injury_risk.last_weak_date)

        # joints and ligaments
        self.last_tendinopathy_date = self.merge_with_none(
            self.last_tendinopathy_date, body_part_injury_risk.last_tendinopathy_date)
        self.last_tendinosis_date = self.merge_with_none(
            self.last_tendinosis_date, body_part_injury_risk.last_tendinosis_date)
        self.last_altered_joint_arthokinematics_date = self.merge_with_none(
            self.last_altered_joint_arthokinematics_date,
            body_part_injury_risk.last_altered_joint_arthokinematics_date)

    def merge_with_none(self, value_a, value_b):

        if value_a is None and value_b is None:
            return None
        if value_a is not None and value_b is None:
            return value_a
        if value_b is not None and value_a is None:
            return value_b
        if value_a is not None and value_b is not None:
            return max(value_a, value_b)

    def eccentric_volume_ramp(self):

        this_weeks_volume = 0
        if self.eccentric_volume_this_week is not None:
            this_weeks_volume += self.eccentric_volume_this_week
        this_weeks_volume += self.eccentric_volume_today()

        if self.eccentric_volume_last_week is not None and self.eccentric_volume_last_week > 0:
            if this_weeks_volume is not None:
                return this_weeks_volume / self.eccentric_volume_last_week

        return 0

    def eccentric_volume_today(self):

        eccentric_volume = 0

        if self.prime_mover_eccentric_volume_today is not None:
            eccentric_volume += self.prime_mover_eccentric_volume_today

        if self.synergist_eccentric_volume_today is not None:
            eccentric_volume += self.synergist_eccentric_volume_today

        if self.synergist_compensating_eccentric_volume_today is not None:
            eccentric_volume += self.synergist_compensating_eccentric_volume_today

        return eccentric_volume

    def concentric_volume_today(self):

        concentric_volume = 0

        if self.prime_mover_concentric_volume_today is not None:
            concentric_volume += self.prime_mover_concentric_volume_today

        if self.synergist_concentric_volume_today is not None:
            concentric_volume += self.synergist_concentric_volume_today

        if self.synergist_compensating_concentric_volume_today is not None:
            concentric_volume += self.synergist_compensating_concentric_volume_today

        return concentric_volume

    def compensating_volume_today(self):

        volume = 0

        if self.synergist_compensating_eccentric_volume_today is not None:
            volume += self.synergist_compensating_eccentric_volume_today

        if self.synergist_compensating_concentric_volume_today is not None:
            volume += self.synergist_compensating_concentric_volume_today

        return volume

    def total_volume_today(self):

        concentric_volume = self.concentric_volume_today()
        eccentric_volume = self.eccentric_volume_today()

        return concentric_volume + eccentric_volume

    def prime_mover_total_volume_today(self):

        concentric_volume = self.prime_mover_concentric_volume_today
        eccentric_volume = self.prime_mover_eccentric_volume_today

        return concentric_volume + eccentric_volume

    def synergist_total_volume_today(self):

        concentric_volume = self.synergist_concentric_volume_today
        eccentric_volume = self.synergist_eccentric_volume_today

        return concentric_volume + eccentric_volume + self.synergist_compensating_eccentric_volume_today + self.synergist_compensating_concentric_volume_today

    def prime_mover_eccentric_volume_ramp(self):

        this_weeks_volume = 0
        if self.prime_mover_eccentric_volume_this_week is not None:
            this_weeks_volume += self.prime_mover_eccentric_volume_this_week
        if self.prime_mover_eccentric_volume_today is not None:
            this_weeks_volume += self.prime_mover_eccentric_volume_today

        if self.prime_mover_eccentric_volume_last_week is not None and self.prime_mover_eccentric_volume_last_week > 0:
            if this_weeks_volume is not None:
                return this_weeks_volume / self.prime_mover_eccentric_volume_last_week

        return 0

    def synegist_eccentric_volume_ramp(self):

        this_weeks_volume = 0
        if self.synergist_eccentric_volume_this_week is not None:
            this_weeks_volume += self.synergist_eccentric_volume_this_week
        if self.synergist_eccentric_volume_today is not None:
            this_weeks_volume += self.synergist_eccentric_volume_today

        if self.synergist_eccentric_volume_last_week is not None and self.synergist_eccentric_volume_last_week > 0:
            if this_weeks_volume is not None:
                return this_weeks_volume / self.synergist_eccentric_volume_last_week

        return 0

    def total_volume_last_week(self):

        eccentric_volume_last_week = 0
        concentric_volume_last_week = 0

        if self.eccentric_volume_last_week is not None:
            eccentric_volume_last_week = self.eccentric_volume_last_week

        if self.concentric_volume_last_week is not None:
            concentric_volume_last_week = self.concentric_volume_last_week

        return eccentric_volume_last_week + concentric_volume_last_week

    def prime_mover_total_volume_last_week(self):

        eccentric_volume_last_week = 0
        concentric_volume_last_week = 0

        if self.prime_mover_eccentric_volume_last_week is not None:
            eccentric_volume_last_week = self.prime_mover_eccentric_volume_last_week

        if self.prime_mover_concentric_volume_last_week is not None:
            concentric_volume_last_week = self.prime_mover_concentric_volume_last_week

        return eccentric_volume_last_week + concentric_volume_last_week

    def synergist_total_volume_last_week(self):

        eccentric_volume_last_week = 0
        concentric_volume_last_week = 0

        if self.synergist_eccentric_volume_last_week is not None:
            eccentric_volume_last_week = self.synergist_eccentric_volume_last_week

        if self.synergist_concentric_volume_last_week is not None:
            concentric_volume_last_week = self.synergist_concentric_volume_last_week

        return eccentric_volume_last_week + concentric_volume_last_week

    def total_volume_this_week(self):

        eccentric_volume_this_week = 0
        concentric_volume_this_week = 0

        if self.eccentric_volume_this_week is not None:
            eccentric_volume_this_week += self.eccentric_volume_this_week

        if self.concentric_volume_this_week is not None:
            concentric_volume_this_week += self.concentric_volume_this_week

        return concentric_volume_this_week + eccentric_volume_this_week

    def prime_mover_total_volume_this_week(self):

        eccentric_volume_this_week = 0
        concentric_volume_this_week = 0

        if self.prime_mover_eccentric_volume_this_week is not None:
            eccentric_volume_this_week += self.prime_mover_eccentric_volume_this_week

        if self.prime_mover_concentric_volume_this_week is not None:
            concentric_volume_this_week += self.prime_mover_concentric_volume_this_week

        # if self.prime_mover_eccentric_volume_today is not None:
        #     eccentric_volume_this_week += self.prime_mover_eccentric_volume_today
        #
        # if self.prime_mover_concentric_volume_today is not None:
        #     concentric_volume_this_week += self.prime_mover_concentric_volume_today

        return concentric_volume_this_week + eccentric_volume_this_week

    def synergist_total_volume_this_week(self):

        eccentric_volume_this_week = 0
        concentric_volume_this_week = 0

        if self.synergist_eccentric_volume_this_week is not None:
            eccentric_volume_this_week += self.synergist_eccentric_volume_this_week

        if self.synergist_concentric_volume_this_week is not None:
            concentric_volume_this_week += self.synergist_concentric_volume_this_week

        # if self.synergist_eccentric_volume_today is not None:
        #     eccentric_volume_this_week += self.synergist_eccentric_volume_today + self.synergist_compensating_eccentric_volume_today
        #
        # if self.synergist_concentric_volume_today is not None:
        #     concentric_volume_this_week += self.synergist_concentric_volume_today + self.synergist_compensating_concentric_volume_today

        return concentric_volume_this_week + eccentric_volume_this_week

    def total_volume_ramp(self):

        total_volume_last_week = self.total_volume_last_week()

        if total_volume_last_week > 0:
            return (self.total_volume_this_week() + self.total_volume_today()) / total_volume_last_week

        return 0

    def prime_mover_total_volume_ramp(self):

        total_volume_last_week = self.prime_mover_total_volume_last_week()

        if total_volume_last_week > 0:
            return self.prime_mover_total_volume_this_week() + self.prime_mover_total_volume_today() / total_volume_last_week

        return 0

    def synergist_total_volume_ramp(self):

        total_volume_last_week = self.synergist_total_volume_last_week()

        if total_volume_last_week > 0:
            return self.synergist_total_volume_this_week() + self.synergist_total_volume_today() / total_volume_last_week

        return 0


class BodyPartFunctionalMovement(object):
    def __init__(self, body_part_side):
        self.body_part_side = body_part_side
        self.concentric_volume = 0
        self.eccentric_volume = 0
        self.compensated_concentric_volume = 0
        self.compensated_eccentric_volume = 0
        self.compensating_causes_volume = []
        self.concentric_intensity = 0
        self.eccentric_intensity = 0
        self.compensated_concentric_intensity = 0
        self.compensated_eccentric_intensity = 0
        self.compensating_causes_intensity = []
        self.concentric_ramp = 0.0
        self.eccentric_ramp = 0.0
        self.is_compensating = False
        self.compensation_source_volume = None
        self.compensation_source_intensity = None
        self.body_part_function = None
        self.inhibited = 0
        self.weak = 0
        self.tight = 0
        self.inflamed = 0
        self.long = 0

    def total_volume(self):

        return self.concentric_volume + self.eccentric_volume + self.compensated_concentric_volume + self.compensated_eccentric_volume

    def total_intensity(self):

        return max(self.concentric_intensity, self.eccentric_intensity, self.compensated_concentric_intensity, self.compensated_eccentric_intensity)

    def __hash__(self):
        return hash((self.body_part_side.body_part_location.value, self.body_part_side.side))

    def __eq__(self, other):
        return self.body_part_side.body_part_location == other.body_part_side.body_part_location and self.body_part_side.side == other.body_part_side.side

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)


class SessionFunctionalMovement(object):
    def __init__(self, session, injury_risk_dict):
        self.body_parts = []
        self.session = session
        self.functional_movement_mappings = []
        self.injury_risk_dict = injury_risk_dict

    def process_anc_and_muscle_imbalance(self, event_date):

        if self.session.movement_patterns is not None and self.session.movement_patterns.apt_ankle_pitch is not None:

            # Left
            self.process_apt_ankle_side(event_date, 1)

            # Right
            self.process_apt_ankle_side(event_date, 2)

    def process_apt_ankle_side(self, event_date, side):

        movement_factory = FunctionalMovementFactory()
        if self.session.movement_patterns is not None and self.session.movement_patterns.apt_ankle_pitch is not None:
            apt_ankle = self.session.movement_patterns.apt_ankle_pitch

            if side == 1:
                if apt_ankle.left is not None:
                    key_elasticity_value = apt_ankle.left.elasticity
                    key_adf_value = apt_ankle.left.y_adf
                else:
                    key_elasticity_value = 0.0
                    key_adf_value = 0.0
            else:
                if apt_ankle.right is not None:
                    key_elasticity_value = apt_ankle.right.elasticity
                    key_adf_value = apt_ankle.right.y_adf
                else:
                    key_elasticity_value = 0.0
                    key_adf_value = 0.0

            if key_elasticity_value != 0:
                pelvic_tilt_movement = movement_factory.get_functional_movement(FunctionalMovementType.pelvic_anterior_tilt)
                # are any muscles associated with Pelvic Anterior Tilt considered to be short with adhesions or muscle spasm?
                any_short_confirmed = False
                body_part_factory = BodyPartFactory()

                # presence of elasticity indicates overactivity
                for p in pelvic_tilt_movement.prime_movers:
                    bilateral = body_part_factory.get_bilateral(BodyPartLocation(p))
                    if bilateral:
                        body_part_side = BodyPartSide(BodyPartLocation(p), side)
                    else:
                        body_part_side = BodyPartSide(BodyPartLocation(p), 0)
                    if body_part_side in self.injury_risk_dict:
                        if (self.injury_risk_dict[body_part_side].last_overactive_date is not None and
                                self.injury_risk_dict[body_part_side].last_overactive_date < event_date):
                            self.injury_risk_dict[body_part_side].last_overactive_date = event_date
                            self.injury_risk_dict[body_part_side].overactive_count_last_0_20_days += 1
                            self.session.overactive_body_parts.append(body_part_side)
                    else:
                        body_part_injury_risk = BodyPartInjuryRisk()
                        body_part_injury_risk.last_overactive_date = event_date
                        body_part_injury_risk.overactive_count_last_0_20_days += 1
                        self.injury_risk_dict[body_part_side] = body_part_injury_risk
                        self.session.overactive_body_parts.append(body_part_side)
                    self.injury_risk_dict[body_part_side].compensation_source = CompensationSource.movement_patterns_3s

                for p in pelvic_tilt_movement.prime_movers:
                    bilateral = body_part_factory.get_bilateral(BodyPartLocation(p))
                    if bilateral:
                        body_part_side = BodyPartSide(BodyPartLocation(p), side)
                    else:
                        body_part_side = BodyPartSide(BodyPartLocation(p), 0)
                    if body_part_side in self.injury_risk_dict:
                        if self.injury_risk_dict[body_part_side].last_adhesions_date is not None and \
                                self.injury_risk_dict[body_part_side].last_adhesions_date == event_date:
                            any_short_confirmed = True
                        #
                        # if self.injury_risk_dict[body_part_side].last_muscle_spasm_date is not None and \
                        #         self.injury_risk_dict[body_part_side].last_muscle_spasm_date == event_date:
                        #     any_short_confirmed = True

                if any_short_confirmed:  # mark all muscle imbalance and short
                    for p in pelvic_tilt_movement.prime_movers:
                        bilateral = body_part_factory.get_bilateral(BodyPartLocation(p))
                        if bilateral:
                            body_part_side = BodyPartSide(BodyPartLocation(p), side)
                        else:
                            body_part_side = BodyPartSide(BodyPartLocation(p), 0)
                        if body_part_side in self.injury_risk_dict:
                            self.injury_risk_dict[body_part_side].last_short_date = event_date
                            self.injury_risk_dict[body_part_side].last_muscle_imbalance_date = event_date
                        else:
                            body_part_injury_risk = BodyPartInjuryRisk()
                            body_part_injury_risk.last_short_date = event_date
                            body_part_injury_risk.last_muscle_imbalance_date = event_date
                            self.injury_risk_dict[body_part_side] = body_part_injury_risk
                        self.injury_risk_dict[body_part_side].compensation_source = CompensationSource.movement_patterns_3s
                        self.session.short_body_parts.append(body_part_side)

                    self.mark_hip_extension_compensating(side)

                # TODO - add long muscle imbalance (antagonists); not sure how to do it yet

                # checking for underactive inhibited or weak
                # check for evidence of short else assume and mark long (by muscle)
                # adhesions reported or (63, 64, 66, 73, 74, 21) is short muscle imbalance
                if key_adf_value != 0:
                    for b in [63, 64, 66, 73, 74]:
                        body_part_side = BodyPartSide(BodyPartLocation(b), side)
                        if body_part_side in self.injury_risk_dict:
                            if (self.injury_risk_dict[body_part_side].last_underactive_date is not None and
                                    self.injury_risk_dict[body_part_side].last_underactive_date < event_date):
                                self.injury_risk_dict[body_part_side].last_underactive_date = event_date
                                self.injury_risk_dict[body_part_side].underactive_weak_count_last_0_20_days += 1
                            if (self.injury_risk_dict[body_part_side].last_weak_date is not None and
                                 self.injury_risk_dict[body_part_side].last_weak_date < event_date):
                                self.injury_risk_dict[body_part_side].last_weak_date = event_date

                            is_short = self.is_short_from_adhesions_or_muscle_imbalance(self.injury_risk_dict[body_part_side], event_date)

                            if not is_short:
                                self.injury_risk_dict[body_part_side].last_long_date = event_date
                                self.session.long_body_parts.append(body_part_side)

                            self.session.underactive_weak_body_parts.append(body_part_side)
                        else:
                            body_part_injury_risk = BodyPartInjuryRisk()
                            body_part_injury_risk.last_underactive_date = event_date
                            body_part_injury_risk.last_weak_date = event_date
                            body_part_injury_risk.underactive_weak_count_last_0_20_days += 1

                            is_short = self.is_short_from_adhesions_or_muscle_imbalance(body_part_injury_risk, event_date)

                            if not is_short:
                                body_part_injury_risk.last_long_date = event_date
                                self.session.long_body_parts.append(body_part_side)

                            self.injury_risk_dict[body_part_side] = body_part_injury_risk
                            self.session.underactive_weak_body_parts.append(body_part_side)
                        self.injury_risk_dict[
                            body_part_side].compensation_source = CompensationSource.movement_patterns_3s

                    self.mark_hip_extension_compensating(side)
                else:
                    for b in [63, 64, 66, 73, 74]:
                        body_part_side = BodyPartSide(BodyPartLocation(b), side)
                        if body_part_side in self.injury_risk_dict:
                            if (self.injury_risk_dict[body_part_side].last_underactive_date is not None and
                                    self.injury_risk_dict[body_part_side].last_underactive_date < event_date):
                                self.injury_risk_dict[body_part_side].last_underactive_date = event_date
                                self.injury_risk_dict[body_part_side].underactive_inhibited_count_last_0_20_days += 1
                            if (self.injury_risk_dict[body_part_side].last_inhibited_date and
                                    self.injury_risk_dict[body_part_side].last_inhibited_date < event_date):
                                self.injury_risk_dict[body_part_side].last_inhibited_date = event_date

                            is_short = self.is_short_from_adhesions_or_muscle_imbalance(
                                self.injury_risk_dict[body_part_side], event_date)

                            if not is_short:
                                self.injury_risk_dict[body_part_side].last_long_date = event_date
                                self.session.long_body_parts.append(body_part_side)

                            self.session.underactive_inhibited_body_parts.append(body_part_side)
                        else:
                            body_part_injury_risk = BodyPartInjuryRisk()
                            body_part_injury_risk.last_underactive_date = event_date
                            body_part_injury_risk.last_inhibited_date = event_date
                            body_part_injury_risk.underactive_inhibited_count_last_0_20_days += 1

                            is_short = self.is_short_from_adhesions_or_muscle_imbalance(body_part_injury_risk,
                                                                                        event_date)

                            if not is_short:
                                body_part_injury_risk.last_long_date = event_date
                                self.session.long_body_parts.append(body_part_side)

                            self.injury_risk_dict[body_part_side] = body_part_injury_risk
                            self.session.underactive_inhibited_body_parts.append(body_part_side)
                        self.injury_risk_dict[
                            body_part_side].compensation_source = CompensationSource.movement_patterns_3s

                    self.mark_hip_extension_compensating(side)

    def is_short_from_adhesions_or_muscle_imbalance(self, body_part_injury_risk, event_date):

        is_short = False
        if body_part_injury_risk.last_adhesions_date is not None and body_part_injury_risk.last_adhesions_date == event_date:
            is_short = True
        if body_part_injury_risk.last_short_date is not None and body_part_injury_risk.last_short_date == event_date:
            is_short = True

        return is_short

    def mark_hip_extension_compensating(self, side):

        movement_factory = FunctionalMovementFactory()

        hip_extension = movement_factory.get_functional_movement(
            FunctionalMovementType.hip_extension)
        body_part_factory = BodyPartFactory()
        for m in hip_extension.prime_movers:
            bilateral = body_part_factory.get_bilateral(BodyPartLocation(m))
            if bilateral:
                body_part_side = BodyPartSide(BodyPartLocation(m), side)
            else:
                body_part_side = BodyPartSide(BodyPartLocation(m), 0)
            if body_part_side in self.injury_risk_dict:
                self.injury_risk_dict[body_part_side].is_compensationg = True
            else:
                body_part_injury_risk = BodyPartInjuryRisk()
                body_part_injury_risk.is_compensationg = True
                self.injury_risk_dict[body_part_side] = body_part_injury_risk
            self.injury_risk_dict[
                body_part_side].compensation_source = CompensationSource.movement_patterns_3s
            self.session.compensating_body_parts.append(body_part_side)

    def process(self, event_date, load_stats):
        activity_factory = ActivityFunctionalMovementFactory()
        movement_factory = FunctionalMovementFactory()

        #self.process_anc_and_muscle_imbalance(event_date)

        self.functional_movement_mappings = activity_factory.get_functional_movement_mappings(self.session.sport_name)

        for m in self.functional_movement_mappings:
            functional_movement = movement_factory.get_functional_movement(m.functional_movement_type)
            for p in functional_movement.prime_movers:
                body_part_side_list = self.get_body_part_side_list(p)
                for b in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(b)
                    m.prime_movers.append(functional_movement_body_part_side)

            for a in functional_movement.synergists:
                body_part_side_list = self.get_body_part_side_list(a)
                for b in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(b)
                    m.synergists.append(functional_movement_body_part_side)

            m.attribute_training_volume(self.session.training_volume(load_stats), self.injury_risk_dict, event_date)
            # TODO - ensure we're using the correct (and all) intensity measures
            if self.session.session_RPE is not None:
                m.attribute_intensity(self.session.session_RPE, self.injury_risk_dict, event_date)

        #self.aggregate_body_parts()

        return self.session

    def aggregate_body_parts(self):

        body_part_sides = {}

        for m in self.functional_movement_mappings:
            for p in m.prime_movers:
                if p not in body_part_sides:
                    body_part_sides[p] = p
                else:
                    body_part_sides[p].concentric_volume += p.concentric_volume
                    body_part_sides[p].eccentric_volume += p.eccentric_volume
                    body_part_sides[p].concentric_intensity = max(p.concentric_intensity, body_part_sides[p].concentric_intensity)
                    body_part_sides[p].eccentric_intensity = max(p.eccentric_intensity, body_part_sides[p].eccentric_intensity)

        self.body_parts = list(body_part_sides.values())

    def get_body_part_side_list(self, body_part_enum):

        body_part_side_list = []

        body_part_factory = BodyPartFactory()
        #body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(body_part_enum), None))
        bilateral = body_part_factory.get_bilateral(BodyPartLocation(body_part_enum))
        # if bilateral:
        #     body_part_side = BodyPartSide(BodyPartLocation(p), side)
        # else:
        #     body_part_side = BodyPartSide(BodyPartLocation(p), 0)
        if not bilateral:
            sides = [0]
        else:
            sides = [1, 2]
        for side in sides:
            body_part_side = BodyPartSide(BodyPartLocation(body_part_enum), side=side)
            body_part_side_list.append(body_part_side)

        return body_part_side_list


class FunctionalMovementActivityMapping(object):
    def __init__(self, functional_movement_type, is_concentric, concentric_level, is_eccentric, eccentric_level):
        self.functional_movement_type = functional_movement_type
        self.is_concentric = is_concentric
        self.concentric_level = concentric_level
        self.is_eccentric = is_eccentric
        self.eccentric_level = eccentric_level
        self.prime_movers = []
        self.antagonists = []
        self.synergists = []

    def attribute_training_volume(self, training_volume, injury_risk_dict, event_date):

        prime_mover_ratio = 0.8
        synergist_ratio = 0.6

        compensation_causing_prime_movers = self.get_compensating_body_parts(injury_risk_dict, event_date)

        compensated_concentric_volume = training_volume * self.concentric_level * .04
        compensated_eccentric_volume = training_volume * self.eccentric_level * .04

        for c in compensation_causing_prime_movers:
            for s in self.synergists:
                if c.side == s.body_part_side.side or c.side == 0 or s.body_part_side.side == 0:
                    synergist_compensated_concentric_volume = compensated_concentric_volume / float(len(self.synergists))
                    synergist_compensated_eccentric_volume = compensated_eccentric_volume / float(len(self.synergists))
                    s.body_part_function = BodyPartFunction.synergist
                    s.compensated_concentric_volume += synergist_compensated_concentric_volume
                    s.compensated_eccentric_volume += synergist_compensated_eccentric_volume
                    s.compensating_causes_volume.append(c)
                    s.compensation_source_volume = CompensationSource.internal_processing

        for p in self.prime_movers:
            attributed_concentric_volume = training_volume * self.concentric_level * prime_mover_ratio
            attributed_eccentric_volume = training_volume * self.eccentric_level * prime_mover_ratio
            p.body_part_function = BodyPartFunction.prime_mover
            p.concentric_volume = attributed_concentric_volume
            p.eccentric_volume = attributed_eccentric_volume

        for s in self.synergists:
            attributed_concentric_volume = training_volume * self.concentric_level * synergist_ratio
            attributed_eccentric_volume = training_volume * self.eccentric_level * synergist_ratio
            s.body_part_function = BodyPartFunction.synergist
            s.concentric_volume = attributed_concentric_volume
            s.eccentric_volume = attributed_eccentric_volume

    def attribute_intensity(self, intensity, injury_risk_dict, event_date):

        prime_mover_ratio = 0.8
        synergist_ratio = 0.6

        # TODO make sure we implement logic to test for high intensity on processing, esp for eccentric intensity

        compensation_causing_prime_movers = self.get_compensating_body_parts(injury_risk_dict, event_date)

        compensated_concentric_intensity = intensity * self.concentric_level * .04
        compensated_eccentric_intensity = intensity * self.eccentric_level * .04

        for c in compensation_causing_prime_movers:
            for s in self.synergists:
                if c.side == s.body_part_side.side or c.side == 0 or s.body_part_side.side == 0:
                    synergist_compensated_concentric_intensity = compensated_concentric_intensity / float(len(self.synergists))
                    synergist_compensated_eccentric_intensity = compensated_eccentric_intensity / float(len(self.synergists))
                    s.body_part_function = BodyPartFunction.synergist
                    s.compensated_concentric_intensity = synergist_compensated_concentric_intensity  # note this isn't a max or additive; one time only
                    s.compensated_eccentric_intensity = synergist_compensated_eccentric_intensity
                    s.compensating_causes_intensity.append(c)
                    s.compensation_source_intensity = CompensationSource.internal_processing

        for p in self.prime_movers:
            attributed_concentric_intensity = intensity * self.concentric_level * prime_mover_ratio
            attributed_eccentric_intensity = intensity * self.eccentric_level * prime_mover_ratio
            p.body_part_function = BodyPartFunction.prime_mover
            p.concentric_intensity = attributed_concentric_intensity
            p.eccentric_intensity = attributed_eccentric_intensity

        for s in self.synergists:
            attributed_concentric_intensity = intensity * self.concentric_level * synergist_ratio
            attributed_eccentric_intensity = intensity * self.eccentric_level * synergist_ratio
            s.body_part_function = BodyPartFunction.synergist
            s.concentric_intensity = attributed_concentric_intensity
            s.eccentric_intensity = attributed_eccentric_intensity

    def other_body_parts_affected(self, target_body_part, injury_risk_dict, event_date, prime_movers):

        # we want to look at both the prime movers and synergists
        body_part_list = []
        if prime_movers:
            body_part_list.extend(self.prime_movers)
        else:
            body_part_list.extend(self.synergists)

        affected_list = []

        filtered_list = [b for b in body_part_list if b.body_part_side.side == target_body_part.body_part_side.side]
        filtered_list = [b for b in filtered_list if b.body_part_side != target_body_part.body_part_side]

        two_days_ago = event_date - timedelta(days=1)

        for f in filtered_list:
            # we are looking for recent statuses that we've determined, different than those reported in symptom intake
            if f.body_part_side in injury_risk_dict:
                if (injury_risk_dict[f.body_part_side].last_weak_date is not None and
                        injury_risk_dict[f.body_part_side].last_weak_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_muscle_spasm_date is not None and
                        injury_risk_dict[f.body_part_side].last_muscle_spasm_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_adhesions_date is not None and
                        injury_risk_dict[f.body_part_side].last_adhesions_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_short_date is not None and
                        injury_risk_dict[f.body_part_side].last_short_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_long_date is not None and
                        injury_risk_dict[f.body_part_side].last_long_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_inhibited_date is not None and
                        injury_risk_dict[f.body_part_side].last_inhibited_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_inflammation_date is not None and
                        injury_risk_dict[f.body_part_side].last_inflammation_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_excessive_strain_date is not None and
                        injury_risk_dict[f.body_part_side].last_non_functional_overreaching_date is not None and
                        injury_risk_dict[f.body_part_side].last_excessive_strain_date >= two_days_ago and
                        injury_risk_dict[f.body_part_side].last_non_functional_overreaching_date >= two_days_ago):
                    affected_list.append(f.body_part_side)

        return affected_list

    def get_compensating_body_parts(self, injury_risk_dict, event_date):

        affected_list = []

        two_days_ago = event_date - timedelta(days=1)

        for f in self.prime_movers:
            # we are looking for recent statuses that we've determined, different than those reported in symptom intake
            if f.body_part_side in injury_risk_dict:
                if (injury_risk_dict[f.body_part_side].last_weak_date is not None and
                        injury_risk_dict[f.body_part_side].last_weak_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_muscle_spasm_date is not None and
                        injury_risk_dict[f.body_part_side].last_muscle_spasm_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_adhesions_date is not None and
                        injury_risk_dict[f.body_part_side].last_adhesions_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_short_date is not None and
                        injury_risk_dict[f.body_part_side].last_short_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_long_date is not None and
                        injury_risk_dict[f.body_part_side].last_long_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_inhibited_date is not None and
                        injury_risk_dict[f.body_part_side].last_inhibited_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_inflammation_date is not None and
                        injury_risk_dict[f.body_part_side].last_inflammation_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_excessive_strain_date is not None and
                        injury_risk_dict[f.body_part_side].last_non_functional_overreaching_date is not None and
                        injury_risk_dict[f.body_part_side].last_excessive_strain_date >= two_days_ago and
                        injury_risk_dict[f.body_part_side].last_non_functional_overreaching_date >= two_days_ago):
                    affected_list.append(f.body_part_side)

        affected_list = list(set(affected_list))

        return affected_list


class ActivityFunctionalMovementFactory(object):

    def get_functional_movement_mappings(self, sport_name):

        mapping = []

        # TODO: actually support sports
        # if sport_name == SportName.distance_running:
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.ankle_dorsiflexion, True, .0025, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.ankle_plantar_flexion, True, .01425, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.inversion_of_the_foot, True, .019, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.eversion_of_the_foot, False, 0, True, .0475))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.knee_flexion, True, 0.125, True, .1188))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.knee_extension, True, .1188, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.hip_adduction, False, 0, True, .0713))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.hip_abduction, True, .0380, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.hip_extension, True, .2850, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.hip_flexion, True, .0375, True, .2375))

        return mapping


class FunctionalMovementFactory(object):

    def get_functional_movement(self, movement_type):

        if movement_type == FunctionalMovementType.ankle_dorsiflexion:
            return self.get_ankle_dorsiflexion()
        elif movement_type == FunctionalMovementType.ankle_plantar_flexion:
            return self.get_ankle_plantar_flexion()
        elif movement_type == FunctionalMovementType.inversion_of_the_foot:
            return self.get_inversion_of_the_foot()
        elif movement_type == FunctionalMovementType.eversion_of_the_foot:
            return self.get_eversion_of_the_foot()
        elif movement_type == FunctionalMovementType.knee_flexion:
            return self.get_knee_flexion()
        elif movement_type == FunctionalMovementType.knee_extension:
            return self.get_knee_extension()
        # elif movement_type == FunctionalMovementType.tibial_external_rotation:
        #     return self.get_tibial_external_rotation()
        # elif movement_type == FunctionalMovementType.tibial_internal_rotation:
        #     return self.get_tibial_internal_rotation()
        elif movement_type == FunctionalMovementType.hip_adduction:
            return self.get_hip_adduction()
        elif movement_type == FunctionalMovementType.hip_abduction:
            return self.get_hip_abduction()
        elif movement_type == FunctionalMovementType.hip_internal_rotation:
            return self.get_hip_internal_rotation()
        elif movement_type == FunctionalMovementType.hip_external_rotation:
            return self.get_hip_external_rotation()
        elif movement_type == FunctionalMovementType.hip_extension:
            return self.get_hip_extension()
        elif movement_type == FunctionalMovementType.hip_flexion:
            return self.get_hip_flexion()
        elif movement_type == FunctionalMovementType.pelvic_anterior_tilt:
            return self.get_pelvic_anterior_tilt()
        elif movement_type == FunctionalMovementType.pelvic_posterior_tilt:
            return self.get_pelvic_posterior_tilt()


    def get_ankle_dorsiflexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_dorsiflexion)
        functional_movement.prime_movers = [40]
        functional_movement.antagonists = [41, 43, 44, 75]
        functional_movement.synergists = []
        return functional_movement

    def get_ankle_plantar_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_plantar_flexion)
        functional_movement.prime_movers = [43, 44, 75]
        functional_movement.antagonists = [40]
        functional_movement.synergists = [41, 42]
        return functional_movement

    def get_inversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.inversion_of_the_foot)
        functional_movement.prime_movers = [40, 42]
        functional_movement.antagonists = [41, 43, 75]
        functional_movement.synergists = [44]
        return functional_movement

    def get_eversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.eversion_of_the_foot)
        functional_movement.prime_movers = [41]
        functional_movement.antagonists = [40, 42, 44]
        functional_movement.synergists = [43, 75]
        return functional_movement

    def get_knee_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_flexion)
        functional_movement.prime_movers = [45, 46, 47, 48]
        functional_movement.antagonists = [55, 56, 57, 58]
        functional_movement.synergists = [44, 75, 53]
        return functional_movement

    def get_knee_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_extension)
        functional_movement.prime_movers = [55, 56, 57, 58]
        functional_movement.antagonists = [44, 75, 45, 46, 47, 48, 53]
        return functional_movement

    #TODO - what happened to thses
    # def get_tibial_external_rotation(self):
    #
    #     functional_movement = FunctionalMovement(FunctionalMovementType.tibial_external_rotation)
    #     functional_movement.prime_movers = [45, 46]
    #     functional_movement.antagonists = [47, 48]
    #     return functional_movement
    #
    # def get_tibial_internal_rotation(self):
    #
    #     functional_movement = FunctionalMovement(FunctionalMovementType.tibial_internal_rotation)
    #     functional_movement.prime_movers = [47, 48]
    #     functional_movement.antagonists = [45, 46, 53]
    #     return functional_movement

    def get_hip_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_extension)
        functional_movement.prime_movers = [66]
        functional_movement.antagonists = [50, 54, 58, 59, 71]
        functional_movement.synergists = [45, 47, 48, 51]
        return functional_movement

    def get_hip_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_flexion)
        functional_movement.prime_movers = [54, 71]
        functional_movement.antagonists = [45, 47, 48, 51, 66]
        functional_movement.synergists = [49, 50, 52, 53, 58, 59, 65]
        return functional_movement

    def get_hip_adduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_adduction)
        functional_movement.prime_movers = [49, 50, 51, 52, 53]
        functional_movement.antagonists = [55, 59, 63, 64, 65]
        functional_movement.synergists = [47, 48, 54, 67, 66]
        return functional_movement

    def get_hip_abduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_abduction)
        functional_movement.prime_movers = [63, 64]
        functional_movement.antagonists = [49, 50, 51, 52, 53, 54, 67]
        functional_movement.synergists = [55, 59, 65, 66]
        return functional_movement

    def get_hip_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_internal_rotation)
        functional_movement.prime_movers = [54, 65]
        functional_movement.antagonists = [45, 51, 67, 64, 66]
        functional_movement.synergists = [46, 47, 48, 49, 50, 52, 53, 59, 63]
        return functional_movement

    def get_hip_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_external_rotation)
        functional_movement.prime_movers = [60]
        functional_movement.antagonists = [47, 48, 49, 50, 52, 53, 54, 59, 63, 65]
        functional_movement.synergists = [45, 51, 67, 64, 66]
        return functional_movement

    def get_pelvic_anterior_tilt(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.pelvic_anterior_tilt)
        functional_movement.prime_movers = [58, 71, 72, 26, 70, 21]
        functional_movement.antagonists = [74, 75]
        functional_movement.synergists = [54, 59]
        return functional_movement

    def get_pelvic_posterior_tilt(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.pelvic_posterior_tilt)
        functional_movement.prime_movers = [74, 75]
        functional_movement.antagonists = [58, 71, 72, 26, 70, 21]
        functional_movement.synergists = [45, 69]
        return functional_movement

    def get_trunk_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_flexion)
        functional_movement.prime_movers = []
