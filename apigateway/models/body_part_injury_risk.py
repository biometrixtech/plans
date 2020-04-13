from datetime import datetime, date

from models.compensation_source import CompensationSource
from models.soreness_base import BodyPartSide
from utils import format_date, format_datetime, parse_datetime, parse_date


class BodyPartInjuryRisk(object):
    def __init__(self):
        # volume
        self.concentric_volume_today = 0
        self.eccentric_volume_today = 0
        self.concentric_volume_last_week = 0
        self.concentric_volume_this_week = 0

        self.eccentric_volume_last_week = 0
        self.eccentric_volume_this_week = 0

        self.compensating_concentric_volume_today = 0
        self.compensating_eccentric_volume_today = 0

        self.total_volume_ramp_today = 0
        self.eccentric_volume_ramp_today = 0

        # intensity
        # self.concentric_intensity_last_week = 0
        # self.concentric_intensity_this_week = 0
        #
        # self.eccentric_intensity_last_week = 0
        # self.eccentric_intensity_this_week = 0
        # self.concentric_intensity_today = 0
        # self.eccentric_intensity_today = 0
        # self.total_intensity_today = 0
        #
        # self.compensating_concentric_intensity_today = 0
        # self.compensating_eccentric_intensity_today = 0
        # self.compensating_total_intensity_today = 0
        self.total_compensation_percent = 0
        self.eccentric_compensation_percent = 0
        self.total_compensation_percent_tier = 0
        self.eccentric_compensation_percent_tier = 0
        self.total_volume_percent_tier = 0
        self.eccentric_volume_percent_tier = 0

        self.compensating_causes_volume_today = []
        # self.compensating_causes_intensity_today = []
        self.compensating_source_volume = None
        # self.compensating_source_intensity = None

        self.last_compensation_date = None
        self.compensation_count_last_0_20_days = 0

        # ache
        self.ache_count_last_0_10_days = 0
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
        self.last_muscle_spasm_trigger_date = None
        self.last_muscle_spasm_level = 0

        # adhesions
        self.last_adhesions_date = None

        # inhibited
        self.last_inhibited_date = None

        # long
        self.last_long_date = None
        self.long_count_last_0_20_days = 0

        # overactive / underactive
        self.last_overactive_short_date = None
        self.last_overactive_long_date = None
        self.last_underactive_short_date = None
        self.last_underactive_long_date = None
        self.overactive_short_count_last_0_20_days = 0
        self.overactive_long_count_last_0_20_days = 0
        self.underactive_short_count_last_0_20_days = 0
        self.underactive_long_count_last_0_20_days = 0

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
        self.weak_count_last_0_20_days = 0

        # muscle_imbalance = None
        self.last_muscle_imbalance_date = None

        # joints and ligaments
        self.last_tendinopathy_date = None
        self.last_tendinosis_date = None
        self.last_altered_joint_arthokinematics_date = None

        # movement dysfunction
        self.last_movement_dysfunction_stress_date = None
        self.last_dysfunction_cause_date = None

        # votes
        self.overactive_short_vote_count = 0
        self.overactive_long_vote_count = 0
        self.underactive_short_vote_count = 0
        self.underactive_long_vote_count = 0
        self.weak_vote_count = 0
        self.last_vote_updated_date_time = None
        self.limited_mobility_tier = 0
        self.underactive_weak_tier = 0

        # max values
        self.max_not_tracked = 0.0
        self.max_strength_endurance_cardiorespiratory = 0.0
        self.max_strength_endurance_strength = 0.0
        self.max_power_drill = 0.0
        self.max_maximal_strength_hypertrophic = 0.0
        self.max_power_explosive_action = 0.0

        self.max_not_tracked_date = None
        self.max_strength_endurance_cardiorespiratory_date = None
        self.max_strength_endurance_strength_date = None
        self.max_power_drill_date = None
        self.max_maximal_strength_hypertrophic_date = None
        self.max_power_explosive_action_date = None

    def json_serialise(self):
        return {
                "concentric_volume_today": self.concentric_volume_today,

                "eccentric_volume_today": self.eccentric_volume_today,

                "compensating_concentric_volume_today": self.compensating_concentric_volume_today,
                "compensating_eccentric_volume_today": self.compensating_eccentric_volume_today,
                "total_compensation_percent": self.total_compensation_percent,
                "eccentric_compensation_percent": self.eccentric_compensation_percent,
                "total_compensation_percent_tier": self.total_compensation_percent_tier,
                "eccentric_compensation_percent_tier": self.eccentric_compensation_percent_tier,
                "total_volume_percent_tier": self.total_volume_percent_tier,
                "eccentric_volume_percent_tier": self.eccentric_volume_percent_tier,

                "total_volume_ramp_today": self.total_volume_ramp_today,
                "eccentric_volume_ramp_today": self.eccentric_volume_ramp_today,

                # "concentric_intensity_today": self.concentric_intensity_today,
                # "eccentric_intensity_today": self.eccentric_intensity_today,
                # "compensating_concentric_intensity_today": self.compensating_concentric_intensity_today,
                # "compensating_eccentric_intensity_today": self.compensating_eccentric_intensity_today,

                "compensating_causes_volume_today": [c.json_serialise() for c in self.compensating_causes_volume_today],
                # "compensating_causes_intensity_today": [c.json_serialise() for c in self.compensating_causes_intensity_today],

                "compensating_source_volume": self.compensating_source_volume.value if self.compensating_source_volume is not None else None,
                # "compensating_source_intensity": self.compensating_source_intensity.value if self.compensating_source_intensity is not None else None,
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
                "last_muscle_spasm_trigger_date": format_date(self.last_muscle_spasm_trigger_date),
                "last_muscle_spasm_level": self.last_muscle_spasm_level,

                # adhesions
                "last_adhesions_date": format_date(self.last_adhesions_date),

                # inhibited
                "last_inhibited_date": format_date(self.last_inhibited_date),

                # long
                "last_long_date": format_date(self.last_long_date),
                "long_count_last_0_20_days": self.long_count_last_0_20_days,

                # overactive / underactive
                "last_overactive_short_date": format_date(self.last_overactive_short_date),
                "last_underactive_short_date": format_date(self.last_underactive_short_date),
                "last_overactive_long_date": format_date(self.last_overactive_long_date),
                "last_underactive_long_date": format_date(self.last_underactive_long_date),
                'overactive_short_count_last_0_20_days': self.overactive_short_count_last_0_20_days,
                'overactive_long_count_last_0_20_days': self.overactive_long_count_last_0_20_days,
                'underactive_long_count_last_0_20_days': self.underactive_long_count_last_0_20_days,
                'underactive_short_count_last_0_20_days': self.underactive_short_count_last_0_20_days,


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
                'weak_count_last_0_20_days': self.weak_count_last_0_20_days,

                # muscle imbalance
                "last_muscle_imbalance_date": format_date(self.last_muscle_imbalance_date),

                # joints and ligaments
                "last_tendinopathy_date": format_date(self.last_tendinopathy_date),
                "last_tendinosis_date": format_date(self.last_tendinosis_date),
                "last_altered_joint_arthokinematics_date": format_date(self.last_altered_joint_arthokinematics_date),

                "last_movement_dysfunction_stress_date": format_date(self.last_movement_dysfunction_stress_date),
                "last_dysfunction_cause_date": format_date(self.last_dysfunction_cause_date),

                "overactive_short_vote_count": self.overactive_short_vote_count,
                "overactive_long_vote_count": self.overactive_long_vote_count,
                "underactive_short_vote_count": self.underactive_short_vote_count,
                "underactive_long_vote_count": self.underactive_long_vote_count,
                "weak_vote_count": self.weak_vote_count,
                "last_vote_updated_date_time": format_datetime(self.last_vote_updated_date_time),
                "limited_mobility_tier": self.limited_mobility_tier,
                "underactive_weak_tier": self.underactive_weak_tier,

                "max_not_tracked": self.max_not_tracked,
                "max_strength_endurance_cardiorespiratory": self.max_strength_endurance_cardiorespiratory,
                "max_strength_endurance_strength": self.max_strength_endurance_strength,
                "max_power_drill": self.max_power_drill,
                "max_maximal_strength_hypertrophic": self.max_maximal_strength_hypertrophic,
                "max_power_explosive_action": self.max_power_explosive_action,

                "max_not_tracked_date": format_date(self.max_not_tracked_date) if self.max_not_tracked_date is not None else None,
                "max_strength_endurance_cardiorespiratory_date": format_date(self.max_strength_endurance_cardiorespiratory_date) if self.max_strength_endurance_cardiorespiratory_date is not None else None,
                "max_strength_endurance_strength_date": format_date(self.max_strength_endurance_strength_date) if self.max_strength_endurance_strength_date is not None else None,
                "max_power_drill_date": format_date(self.max_power_drill_date) if self.max_power_drill_date is not None else None,
                "max_maximal_strength_hypertrophic_date": format_date(self.max_maximal_strength_hypertrophic_date) if self.max_maximal_strength_hypertrophic_date is not None else None,
                "max_power_explosive_action_date": format_date(self.max_power_explosive_action_date) if self.max_power_explosive_action_date is not None else None

        }

    @classmethod
    def json_deserialise(cls, input_dict):
        injury_risk = cls()
        concentric_volume_today = 0
        concentric_volume_today += input_dict.get('prime_mover_concentric_volume_today', 0)
        concentric_volume_today += input_dict.get('synergist_concentric_volume_today', 0)
        concentric_volume_today += input_dict.get('concentric_volume_today', 0)
        injury_risk.concentric_volume_today = concentric_volume_today

        eccentric_volume_today = 0
        eccentric_volume_today += input_dict.get('prime_mover_eccentric_volume_today', 0)
        eccentric_volume_today += input_dict.get('synergist_eccentric_volume_today', 0)
        eccentric_volume_today += input_dict.get('eccentric_volume_today', 0)
        injury_risk.eccentric_volume_today = eccentric_volume_today

        compensating_concentric_volume_today = 0
        compensating_concentric_volume_today += input_dict.get('synergist_compensating_concentric_volume_today', 0)
        compensating_concentric_volume_today += input_dict.get('compensating_concentric_volume_today', 0)
        injury_risk.compensating_concentric_volume_today = compensating_concentric_volume_today

        compensating_eccentric_volume_today = 0
        compensating_eccentric_volume_today += input_dict.get('synergist_compensating_eccentric_volume_today', 0)
        compensating_eccentric_volume_today += input_dict.get('compensating_eccentric_volume_today', 0)
        injury_risk.compensating_eccentric_volume_today = compensating_eccentric_volume_today

        injury_risk.total_compensation_percent = input_dict.get('total_compensation_percent', 0)
        injury_risk.eccentric_compensation_percent = input_dict.get('eccentric_compensation_percent', 0)
        injury_risk.total_compensation_percent_tier = input_dict.get('total_compensation_percent_tier', 0)
        injury_risk.eccentric_compensation_percent_tier = input_dict.get('eccentric_compensation_percent_tier', 0)
        injury_risk.total_volume_percent_tier = input_dict.get('total_volume_percent_tier', 0)
        injury_risk.eccentric_volume_percent_tier = input_dict.get('eccentric_volume_percent_tier', 0)

        injury_risk.total_volume_ramp_today = input_dict.get('total_volume_ramp_today')
        injury_risk.eccentric_volume_ramp_today = input_dict.get('eccentric_volume_ramp_today')

        # concentric_intensity_today = 0
        # concentric_intensity_today += input_dict.get('prime_mover_concentric_intensity_today', 0)
        # concentric_intensity_today += input_dict.get('synergist_concentric_intensity_today', 0)
        # concentric_intensity_today += input_dict.get('concentric_intensity_today', 0)
        # injury_risk.concentric_intensity_today = concentric_intensity_today

        # eccentric_intensity_today = 0
        # eccentric_intensity_today += input_dict.get('prime_mover_eccentric_intensity_today', 0)
        # eccentric_intensity_today += input_dict.get('synergist_eccentric_intensity_today', 0)
        # eccentric_intensity_today += input_dict.get('eccentric_intensity_today', 0)
        # injury_risk.eccentric_intensity_today = eccentric_intensity_today
        #
        # compensating_concentric_intensity_today = 0
        # compensating_concentric_intensity_today += input_dict.get('synergist_compensating_concentric_intensity_today', 0)
        # compensating_concentric_intensity_today += input_dict.get('compensating_concentric_intensity_today', 0)
        # injury_risk.compensating_concentric_intensity_today = compensating_concentric_intensity_today

        # compensating_eccentric_intensity_today = 0
        # compensating_eccentric_intensity_today += input_dict.get('synergist_compensating_eccentric_intensity_today', 0)
        # compensating_eccentric_intensity_today += input_dict.get('compensating_eccentric_intensity_today', 0)
        # injury_risk.compensating_eccentric_intensity_today = compensating_eccentric_intensity_today

        injury_risk.compensating_causes_volume_today = [BodyPartSide.json_deserialise(c) for c in
                                                  input_dict.get('compensating_causes_volume_today', [])]
        # injury_risk.compensating_causes_intensity_today = [BodyPartSide.json_deserialise(c) for c in
        #                                           input_dict.get('compensating_causes_intensity_today', [])]

        injury_risk.last_compensation_date = input_dict.get('last_compensation_date')

        injury_risk.compensating_source_volume = CompensationSource(
            input_dict['compensating_source_volume']) if input_dict.get(
            "compensating_source_volume") is not None else None
        # injury_risk.compensating_source_intensity = CompensationSource(
        #     input_dict['compensating_source_intensity']) if input_dict.get(
        #     "compensating_source_intensity") is not None else None

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
        injury_risk.last_muscle_spasm_trigger_date = input_dict.get('last_muscle_spasm_trigger_date')
        injury_risk.last_muscle_spasm_level = input_dict.get('last_muscle_spasm_level', 0)

        # adhesions
        injury_risk.last_adhesions_date = input_dict.get('last_adhesions_date')

        # inhibited
        injury_risk.last_inhibited_date = input_dict.get('last_inhibited_date')

        # long
        injury_risk.last_long_date = input_dict.get('last_long_date')
        injury_risk.long_count_last_0_20_days = input_dict.get('long_count_last_0_20_days', 0)

        # overactive / underactive
        injury_risk.last_overactive_short_date = input_dict.get('last_overactive_short_date')
        injury_risk.last_underactive_short_date = input_dict.get('last_underactive_short_date')
        injury_risk.last_overactive_long_date = input_dict.get('last_overactive_long_date')
        injury_risk.last_underactive_long_date = input_dict.get('last_underactive_long_date')
        injury_risk.overactive_short_count_last_0_20_days = input_dict.get('overactive_short_count_last_0_20_days',0)
        injury_risk.overactive_long_count_last_0_20_days = input_dict.get('overactive_long_count_last_0_20_days',0)
        injury_risk.underactive_short_count_last_0_20_days = input_dict.get('underactive_short_count_last_0_20_days', 0)
        injury_risk.underactive_long_count_last_0_20_days = input_dict.get('underactive_long_count_last_0_20_days', 0)

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
        injury_risk.weak_count_last_0_20_days = input_dict.get('weak_count_last_0_20_days', 0)

        # muscle imbalance
        injury_risk.last_muscle_imbalance_date = input_dict.get('last_muscle_imbalance_date')

        # joints and ligaments
        injury_risk.last_tendinopathy_date = input_dict.get('last_tendinopathy_date')
        injury_risk.last_tendinosis_date = input_dict.get('last_tendinosis_date')
        injury_risk.last_altered_joint_arthokinematics_date = input_dict.get('last_altered_joint_arthokinematics_date')

        # movement dysfunction
        injury_risk.last_movement_dysfunction_stress_date = input_dict.get('last_movement_dysfunction_stress_date')
        injury_risk.last_dysfunction_cause_date = input_dict.get('last_dysfunction_cause_date')

        injury_risk.overactive_short_vote_count = input_dict.get('overactive_short_vote_count',0)
        injury_risk.overactive_long_vote_count = input_dict.get('overactive_long_vote_count',0)
        injury_risk.underactive_short_vote_count = input_dict.get('underactive_short_vote_count',0)
        injury_risk.underactive_long_vote_count = input_dict.get('underactive_long_vote_count',0)
        injury_risk.weak_vote_count = input_dict.get('weak_vote_count', 0)
        injury_risk.last_vote_updated_date_time = input_dict.get('last_vote_updated_date_time')
        injury_risk.limited_mobility_tier = input_dict.get('limited_mobility_tier', 0)
        injury_risk.underactive_weak_tier = input_dict.get('underactive_weak_tier', 0)

        injury_risk.max_not_tracked = input_dict.get("max_not_tracked", 0)
        injury_risk.max_strength_endurance_cardiorespiratory = input_dict.get("max_strength_endurance_cardiorespiratory", 0)
        injury_risk.max_strength_endurance_strength = input_dict.get("max_strength_endurance_strength", 0)
        injury_risk.max_power_drill = input_dict.get("max_power_drill", 0)
        injury_risk.max_maximal_strength_hypertrophic = input_dict.get("max_maximal_strength_hypertrophic", 0)
        injury_risk.max_power_explosive_action = input_dict.get("max_power_explosive_action", 0)

        injury_risk.max_not_tracked_date = input_dict.get("max_not_tracked_date")
        injury_risk.max_strength_endurance_cardiorespiratory_date = input_dict.get("max_strength_endurance_cardiorespiratory_date")
        injury_risk.max_strength_endurance_strength_date = input_dict.get("max_strength_endurance_strength_date")
        injury_risk.max_power_drill_date = input_dict.get("max_power_drill_date")
        injury_risk.max_maximal_strength_hypertrophic_date = input_dict.get("max_maximal_strength_hypertrophic_date")
        injury_risk.max_power_explosive_action_date = input_dict.get("max_power_explosive_action_date")

        return injury_risk

    def __setattr__(self, name, value):
        if 'date_time' in name:
            if value is not None and not isinstance(value, datetime):
                value = parse_datetime(value)
        elif 'date' in name:
            if value is not None and not isinstance(value, date):
                value = parse_date(value).date()
        super().__setattr__(name, value)

    def merge(self, body_part_injury_risk):

        self.concentric_volume_last_week = max(self.concentric_volume_last_week, body_part_injury_risk.concentric_volume_last_week)
        self.concentric_volume_this_week = max(self.concentric_volume_this_week, body_part_injury_risk.concentric_volume_this_week)
        self.concentric_volume_today = max(self.concentric_volume_today, body_part_injury_risk.concentric_volume_today)
        self.eccentric_volume_last_week = max(self.eccentric_volume_last_week, body_part_injury_risk.eccentric_volume_last_week)
        self.eccentric_volume_this_week = max(self.eccentric_volume_this_week, body_part_injury_risk.eccentric_volume_this_week)
        self.eccentric_volume_today = max(self.eccentric_volume_today, body_part_injury_risk.eccentric_volume_today)

        # self.prime_mover_concentric_volume_last_week = max(self.prime_mover_concentric_volume_last_week, body_part_injury_risk.prime_mover_concentric_volume_last_week)
        # self.prime_mover_concentric_volume_this_week = max(self.prime_mover_concentric_volume_this_week, body_part_injury_risk.prime_mover_concentric_volume_this_week)
        #self.prime_mover_concentric_volume_today = max(self.prime_mover_concentric_volume_today, body_part_injury_risk.prime_mover_concentric_volume_today)
        # self.prime_mover_eccentric_volume_last_week = max(self.prime_mover_eccentric_volume_last_week, body_part_injury_risk.prime_mover_eccentric_volume_last_week)
        # self.prime_mover_eccentric_volume_this_week = max(self.prime_mover_eccentric_volume_this_week, body_part_injury_risk.prime_mover_eccentric_volume_this_week)
        #self.prime_mover_eccentric_volume_today = max(self.prime_mover_eccentric_volume_today, body_part_injury_risk.prime_mover_eccentric_volume_today)

        # self.synergist_concentric_volume_last_week = max(self.synergist_concentric_volume_last_week, body_part_injury_risk.synergist_concentric_volume_last_week)
        # self.synergist_concentric_volume_this_week = max(self.synergist_concentric_volume_this_week, body_part_injury_risk.synergist_concentric_volume_this_week)
        #self.synergist_concentric_volume_today = max(self.synergist_concentric_volume_today, body_part_injury_risk.synergist_concentric_volume_today)
        # self.synergist_eccentric_volume_last_week = max(self.synergist_eccentric_volume_last_week, body_part_injury_risk.synergist_eccentric_volume_last_week)
        # self.synergist_eccentric_volume_this_week = max(self.synergist_eccentric_volume_this_week, body_part_injury_risk.synergist_eccentric_volume_this_week)
        #self.synergist_eccentric_volume_today = max(self.synergist_eccentric_volume_today, body_part_injury_risk.synergist_eccentric_volume_today)

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
        self.last_muscle_spasm_trigger_date = self.merge_with_none(self.last_muscle_spasm_trigger_date,
                                                           body_part_injury_risk.last_muscle_spasm_trigger_date)
        self.last_muscle_spasm_level = max(self.last_muscle_spasm_level, body_part_injury_risk.last_muscle_spasm_level)

        # adhesions
        self.last_adhesions_date = self.merge_with_none(self.last_adhesions_date, body_part_injury_risk.last_adhesions_date)

        # inhibited
        self.last_inhibited_date = self.merge_with_none(self.last_inhibited_date, body_part_injury_risk.last_inhibited_date)

        # long
        self.last_long_date = self.merge_with_none(self.last_long_date, body_part_injury_risk.last_long_date)
        self.long_count_last_0_20_days = max(self.long_count_last_0_20_days, body_part_injury_risk.long_count_last_0_20_days)

        # overactive / underactive
        self.last_overactive_short_date = self.merge_with_none(self.last_overactive_short_date, body_part_injury_risk.last_overactive_short_date)
        self.last_underactive_short_date = self.merge_with_none(self.last_underactive_short_date, body_part_injury_risk.last_underactive_short_date)
        self.last_overactive_long_date = self.merge_with_none(self.last_overactive_long_date,
                                                               body_part_injury_risk.last_overactive_long_date)
        self.last_underactive_long_date = self.merge_with_none(self.last_underactive_long_date,
                                                                body_part_injury_risk.last_underactive_long_date)

        self.overactive_short_count_last_0_20_days = max(self.overactive_short_count_last_0_20_days, body_part_injury_risk.overactive_short_count_last_0_20_days)
        self.underactive_short_count_last_0_20_days = max(self.underactive_short_count_last_0_20_days,
                                                          body_part_injury_risk.underactive_short_count_last_0_20_days)
        self.overactive_long_count_last_0_20_days = max(self.overactive_long_count_last_0_20_days, body_part_injury_risk.overactive_long_count_last_0_20_days)
        self.underactive_long_count_last_0_20_days = max(self.underactive_long_count_last_0_20_days,
                                                          body_part_injury_risk.underactive_long_count_last_0_20_days)

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

        self.weak_count_last_0_20_days = max(self.weak_count_last_0_20_days,
                                                         body_part_injury_risk.weak_count_last_0_20_days)

        # joints and ligaments
        self.last_tendinopathy_date = self.merge_with_none(
            self.last_tendinopathy_date, body_part_injury_risk.last_tendinopathy_date)
        self.last_tendinosis_date = self.merge_with_none(
            self.last_tendinosis_date, body_part_injury_risk.last_tendinosis_date)
        self.last_altered_joint_arthokinematics_date = self.merge_with_none(
            self.last_altered_joint_arthokinematics_date,
            body_part_injury_risk.last_altered_joint_arthokinematics_date)

        # update calcuations after new values are set
        self.total_compensation_percent = self.percent_total_compensation()
        self.eccentric_compensation_percent = self.percent_eccentric_compensation()
        self.total_volume_ramp_today = self.total_volume_ramp()
        self.eccentric_volume_ramp_today = self.eccentric_volume_ramp()

        self.eccentric_volume_percent_tier = self.merge_tiers(self.eccentric_volume_percent_tier,
                                                              body_part_injury_risk.eccentric_volume_percent_tier)
        self.eccentric_compensation_percent_tier = self.merge_tiers(self.eccentric_compensation_percent_tier,
                                                                    body_part_injury_risk.eccentric_compensation_percent_tier)
        self.total_compensation_percent_tier = self.merge_tiers(self.total_compensation_percent_tier,
                                                                body_part_injury_risk.total_compensation_percent_tier)
        self.total_volume_percent_tier = self.merge_tiers(self.total_volume_percent_tier,
                                                   body_part_injury_risk.total_volume_percent_tier)

        self.last_movement_dysfunction_stress_date = self.merge_with_none(self.last_movement_dysfunction_stress_date,
                                                                          body_part_injury_risk.last_movement_dysfunction_stress_date)
        self.last_dysfunction_cause_date = self.merge_with_none(self.last_dysfunction_cause_date,
                                                                body_part_injury_risk.last_dysfunction_cause_date)

        self.overactive_short_vote_count = max(self.overactive_short_vote_count, body_part_injury_risk.overactive_short_vote_count)
        self.overactive_long_vote_count = max(self.overactive_long_vote_count,
                                               body_part_injury_risk.overactive_long_vote_count)
        self.underactive_short_vote_count = max(self.underactive_short_vote_count,
                                               body_part_injury_risk.underactive_short_vote_count)
        self.underactive_long_vote_count = max(self.underactive_long_vote_count,
                                               body_part_injury_risk.overactive_short_vote_count)

        self.weak_vote_count = max(self.weak_vote_count, body_part_injury_risk.weak_vote_count)

        self.last_vote_updated_date_time = self.merge_with_none(self.last_vote_updated_date_time,
                                                                body_part_injury_risk.last_vote_updated_date_time)
        self.limited_mobility_tier = self.merge_tiers(self.limited_mobility_tier, body_part_injury_risk.limited_mobility_tier)
        self.underactive_weak_tier = self.merge_tiers(self.underactive_weak_tier,
                                                      body_part_injury_risk.underactive_weak_tier)

    def merge_tiers(self, value_a, value_b):

        if value_a > 0 and value_b > 0:
            return min(value_a, value_b)
        elif value_a > 0 and value_b == 0:
            return value_a
        elif value_a == 0 and value_b > 0:
            return value_b
        else:
            return 0

    def merge_with_none(self, value_a, value_b):

        if value_a is None and value_b is None:
            return None
        if value_a is not None and value_b is None:
            return value_a
        if value_b is not None and value_a is None:
            return value_b
        if value_a is not None and value_b is not None:
            return max(value_a, value_b)

    def test_date(self, attribute, base_date):

        if attribute is not None and attribute == base_date:
            return True
        else:
            return False

    def get_percentage(self, count_attribute):

        attribute_list = ["overactive_short_vote_count", "overactive_long_vote_count", "underactive_short_vote_count", "underactive_long_vote_count"]

        total_count = 0

        for a in attribute_list:
            total_count += getattr(self, a)

        if total_count == 0:
            return 0.0

        percent = (getattr(self, count_attribute) / total_count) * 100

        return percent

    def is_highest_count(self, count_attribute):

        attribute_list = ["overactive_short_vote_count", "overactive_long_vote_count", "underactive_short_vote_count",
                          "underactive_long_vote_count"]

        new_attribute_list = [a for a in attribute_list if a != count_attribute]

        if getattr(self, count_attribute) == 0:
            return False

        for n in new_attribute_list:
            if getattr(self, count_attribute) < getattr(self, n):
                return False

        return True

    def get_inflammation_severity(self, base_date):

        max_severity = 0

        if self.test_date(self.last_sharp_date, base_date):
            max_severity = max(max_severity, self.last_sharp_level)
        if self.test_date(self.last_ache_date, base_date):
            max_severity = max(max_severity, self.last_ache_level)

        return max_severity

    def get_knots_severity(self, base_date):

        max_severity = 0

        if self.test_date(self.last_knots_date, base_date):
            max_severity = max(max_severity, self.last_knots_level)

        return max_severity

    def get_muscle_spasm_severity(self, base_date):

        max_severity = 0

        if self.test_date(self.last_tight_date, base_date):
            max_severity = max(max_severity, self.last_tight_level)
        if self.test_date(self.last_sharp_date, base_date):
            max_severity = max(max_severity, self.last_sharp_level)
        if self.test_date(self.last_ache_date, base_date):
            max_severity = max(max_severity, self.last_ache_level)
        if self.test_date(self.last_muscle_spasm_date, base_date):
            max_severity = max(max_severity, self.last_muscle_spasm_level)
        if self.test_date(self.last_muscle_spasm_trigger_date, base_date):
            max_severity = max(max_severity, self.last_muscle_spasm_level)

        return max_severity

    def get_adhesions_severity(self, base_date):

        max_severity = 0

        if self.test_date(self.last_tight_date, base_date):
            max_severity = max(max_severity, self.last_tight_level)
        if self.test_date(self.last_sharp_date, base_date):
            max_severity = max(max_severity, self.last_sharp_level)
        if self.test_date(self.last_ache_date, base_date):
            max_severity = max(max_severity, self.last_ache_level)
        if self.test_date(self.last_knots_date, base_date):
            max_severity = max(max_severity, self.last_knots_level)

        return max_severity

    def eccentric_volume_ramp(self):

        this_weeks_volume = 0
        if self.eccentric_volume_this_week is not None:
            this_weeks_volume += self.eccentric_volume_this_week
        this_weeks_volume += self.eccentric_volume_today

        if self.eccentric_volume_last_week is not None and self.eccentric_volume_last_week > 0:
            if this_weeks_volume is not None:
                return this_weeks_volume / self.eccentric_volume_last_week

        return 0

    def percent_eccentric_compensation(self):

        percentage = 0

        #eccentric_volume_today = self.eccentric_volume_today()

        if self.eccentric_volume_today > 0:
            percentage = (self.compensating_eccentric_volume_today / float(self.eccentric_volume_today)) * 100

        return percentage

    def percent_total_compensation(self):

        percentage = 0

        total_volume_today = self.total_volume_today()

        if total_volume_today > 0:
            compensating_volume_today = self.compensating_eccentric_volume_today + self.compensating_concentric_volume_today
            percentage = (compensating_volume_today / float(total_volume_today)) * 100

        return percentage

    # def eccentric_volume_today(self):
    #
    #     eccentric_load = 0
    #
    #     if self.prime_mover_eccentric_volume_today is not None:
    #         eccentric_load += self.prime_mover_eccentric_volume_today
    #
    #     if self.synergist_eccentric_volume_today is not None:
    #         eccentric_load += self.synergist_eccentric_volume_today
    #
    #     if self.synergist_compensating_eccentric_volume_today is not None:
    #         eccentric_load += self.synergist_compensating_eccentric_volume_today
    #
    #     return eccentric_load
    #
    # def concentric_volume_today(self):
    #
    #     concentric_load = 0
    #
    #     if self.prime_mover_concentric_volume_today is not None:
    #         concentric_load += self.prime_mover_concentric_volume_today
    #
    #     if self.synergist_concentric_volume_today is not None:
    #         concentric_load += self.synergist_concentric_volume_today
    #
    #     if self.synergist_compensating_concentric_volume_today is not None:
    #         concentric_load += self.synergist_compensating_concentric_volume_today
    #
    #     return concentric_load

    def compensating_volume_today(self):

        volume = 0

        if self.compensating_eccentric_volume_today is not None:
            volume += self.compensating_eccentric_volume_today

        if self.compensating_concentric_volume_today is not None:
            volume += self.compensating_concentric_volume_today

        return volume

    def total_volume_today(self):

        concentric_volume = self.concentric_volume_today
        eccentric_volume = self.eccentric_volume_today

        return concentric_volume + eccentric_volume

    # def prime_mover_total_volume_today(self):
    #
    #     concentric_load = self.prime_mover_concentric_volume_today
    #     eccentric_load = self.prime_mover_eccentric_volume_today
    #
    #     return concentric_load + eccentric_load
    #
    # def synergist_total_volume_today(self):
    #
    #     concentric_load = self.synergist_concentric_volume_today
    #     eccentric_load = self.synergist_eccentric_volume_today
    #
    #     return concentric_load + eccentric_load + self.synergist_compensating_eccentric_volume_today + self.synergist_compensating_concentric_volume_today

    # def prime_mover_eccentric_volume_ramp(self):
    #
    #     this_weeks_volume = 0
    #     if self.prime_mover_eccentric_volume_this_week is not None:
    #         this_weeks_volume += self.prime_mover_eccentric_volume_this_week
    #     if self.prime_mover_eccentric_volume_today is not None:
    #         this_weeks_volume += self.prime_mover_eccentric_volume_today
    #
    #     if self.prime_mover_eccentric_volume_last_week is not None and self.prime_mover_eccentric_volume_last_week > 0:
    #         if this_weeks_volume is not None:
    #             return this_weeks_volume / self.prime_mover_eccentric_volume_last_week
    #
    #     return 0

    # def synegist_eccentric_volume_ramp(self):
    #
    #     this_weeks_volume = 0
    #     if self.synergist_eccentric_volume_this_week is not None:
    #         this_weeks_volume += self.synergist_eccentric_volume_this_week
    #     if self.synergist_eccentric_volume_today is not None:
    #         this_weeks_volume += self.synergist_eccentric_volume_today
    #
    #     if self.synergist_eccentric_volume_last_week is not None and self.synergist_eccentric_volume_last_week > 0:
    #         if this_weeks_volume is not None:
    #             return this_weeks_volume / self.synergist_eccentric_volume_last_week
    #
    #     return 0

    def total_volume_last_week(self):

        eccentric_volume_last_week = 0
        concentric_volume_last_week = 0

        if self.eccentric_volume_last_week is not None:
            eccentric_volume_last_week = self.eccentric_volume_last_week

        if self.concentric_volume_last_week is not None:
            concentric_volume_last_week = self.concentric_volume_last_week

        return eccentric_volume_last_week + concentric_volume_last_week

    # def prime_mover_total_volume_last_week(self):
    #
    #     eccentric_volume_last_week = 0
    #     concentric_volume_last_week = 0
    #
    #     if self.prime_mover_eccentric_volume_last_week is not None:
    #         eccentric_volume_last_week = self.prime_mover_eccentric_volume_last_week
    #
    #     if self.prime_mover_concentric_volume_last_week is not None:
    #         concentric_volume_last_week = self.prime_mover_concentric_volume_last_week
    #
    #     return eccentric_volume_last_week + concentric_volume_last_week
    #
    # def synergist_total_volume_last_week(self):
    #
    #     eccentric_volume_last_week = 0
    #     concentric_volume_last_week = 0
    #
    #     if self.synergist_eccentric_volume_last_week is not None:
    #         eccentric_volume_last_week = self.synergist_eccentric_volume_last_week
    #
    #     if self.synergist_concentric_volume_last_week is not None:
    #         concentric_volume_last_week = self.synergist_concentric_volume_last_week
    #
    #     return eccentric_volume_last_week + concentric_volume_last_week

    def total_volume_this_week(self):

        eccentric_volume_this_week = 0
        concentric_volume_this_week = 0

        if self.eccentric_volume_this_week is not None:
            eccentric_volume_this_week += self.eccentric_volume_this_week

        if self.concentric_volume_this_week is not None:
            concentric_volume_this_week += self.concentric_volume_this_week

        return concentric_volume_this_week + eccentric_volume_this_week

    # def prime_mover_total_volume_this_week(self):
    #
    #     eccentric_volume_this_week = 0
    #     concentric_volume_this_week = 0
    #
    #     if self.prime_mover_eccentric_volume_this_week is not None:
    #         eccentric_volume_this_week += self.prime_mover_eccentric_volume_this_week
    #
    #     if self.prime_mover_concentric_volume_this_week is not None:
    #         concentric_volume_this_week += self.prime_mover_concentric_volume_this_week
    #
    #     return concentric_volume_this_week + eccentric_volume_this_week
    #
    # def synergist_total_volume_this_week(self):
    #
    #     eccentric_volume_this_week = 0
    #     concentric_volume_this_week = 0
    #
    #     if self.synergist_eccentric_volume_this_week is not None:
    #         eccentric_volume_this_week += self.synergist_eccentric_volume_this_week
    #
    #     if self.synergist_concentric_volume_this_week is not None:
    #         concentric_volume_this_week += self.synergist_concentric_volume_this_week
    #
    #     return concentric_volume_this_week + eccentric_volume_this_week

    def total_volume_ramp(self):

        total_volume_last_week = self.total_volume_last_week()

        if total_volume_last_week > 0:
            return (self.total_volume_this_week() + self.total_volume_today()) / total_volume_last_week

        return 0

    # def prime_mover_total_volume_ramp(self):
    #
    #     total_volume_last_week = self.prime_mover_total_volume_last_week()
    #
    #     if total_volume_last_week > 0:
    #         return self.prime_mover_total_volume_this_week() + self.prime_mover_total_volume_today() / total_volume_last_week
    #
    #     return 0
    #
    # def synergist_total_volume_ramp(self):
    #
    #     total_volume_last_week = self.synergist_total_volume_last_week()
    #
    #     if total_volume_last_week > 0:
    #         return self.synergist_total_volume_this_week() + self.synergist_total_volume_today() / total_volume_last_week
    #
    #     return 0


class BodyPartHistInjuryRisk(object):
    def __init__(self):
        self.concentric_volume_last_week = 0
        self.concentric_volume_this_week = 0
        # self.prime_mover_concentric_volume_last_week = 0
        # self.prime_mover_concentric_volume_this_week = 0
        # self.synergist_concentric_volume_last_week = 0
        # self.synergist_concentric_volume_this_week = 0
        # self.synergist_compensating_concentric_volume_last_week = 0
        # self.synergist_compensating_concentric_volume_this_week = 0

        self.eccentric_volume_last_week = 0
        self.eccentric_volume_this_week = 0
        # self.prime_mover_eccentric_volume_last_week = 0
        # self.prime_mover_eccentric_volume_this_week = 0
        # self.synergist_eccentric_volume_last_week = 0
        self.synergist_eccentric_volume_this_week = 0
        # self.synergist_compensating_eccentric_volume_last_week = 0
        # self.synergist_compensating_eccentric_volume_this_week = 0

        # intensity
        self.concentric_intensity_last_week = 0
        self.concentric_intensity_this_week = 0
        # self.prime_mover_concentric_intensity_last_week = 0
        # self.prime_mover_concentric_intensity_this_week = 0
        # self.synergist_concentric_intensity_last_week = 0
        # self.synergist_concentric_intensity_this_week = 0
        # self.synergist_compensating_concentric_intensity_last_week = 0
        # self.synergist_compensating_concentric_intensity_this_week = 0

        self.eccentric_intensity_last_week = 0
        self.eccentric_intensity_this_week = 0
        # self.prime_mover_eccentric_intensity_last_week = 0
        # self.prime_mover_eccentric_intensity_this_week = 0
        # self.synergist_eccentric_intensity_last_week = 0
        # self.synergist_eccentric_intensity_this_week = 0
        # self.synergist_compensating_eccentric_intensity_last_week = 0
        # self.synergist_compensating_eccentric_intensity_this_week = 0

    def json_serialise(self):
        return {
            "concentric_volume_last_week": self.concentric_volume_last_week,
            "concentric_volume_this_week": self.concentric_volume_this_week,
            # "prime_mover_concentric_volume_last_week": self.prime_mover_concentric_volume_last_week,
            # "prime_mover_concentric_volume_this_week": self.prime_mover_concentric_volume_this_week,
            # "synergist_concentric_volume_last_week": self.synergist_concentric_volume_last_week,
            # "synergist_concentric_volume_this_week": self.synergist_concentric_volume_this_week,
            # "synergist_compensating_concentric_volume_last_week": self.synergist_compensating_concentric_volume_last_week,
            # "synergist_compensating_concentric_volume_this_week": self.synergist_compensating_concentric_volume_this_week,
            # "prime_mover_eccentric_volume_last_week": self.prime_mover_eccentric_volume_last_week,
            # "prime_mover_eccentric_volume_this_week": self.prime_mover_eccentric_volume_this_week,
            # "synergist_eccentric_volume_last_week": self.synergist_eccentric_volume_last_week,
            # "synergist_eccentric_volume_this_week": self.synergist_eccentric_volume_this_week,
            # "synergist_compensating_eccentric_volume_last_week": self.synergist_compensating_eccentric_volume_last_week,
            # "synergist_compensating_eccentric_volume_this_week": self.synergist_compensating_eccentric_volume_this_week,
            "concentric_intensity_last_week": self.concentric_intensity_last_week,
            "concentric_intensity_this_week": self.concentric_intensity_this_week,
            "eccentric_intensity_last_week": self.eccentric_intensity_last_week,
            "eccentric_intensity_this_week": self.eccentric_intensity_this_week,
            # "prime_mover_concentric_intensity_last_week": self.prime_mover_concentric_intensity_last_week,
            # "prime_mover_concentric_intensity_this_week": self.prime_mover_concentric_intensity_this_week,
            # "prime_mover_eccentric_intensity_last_week": self.prime_mover_eccentric_intensity_last_week,
            # "prime_mover_eccentric_intensity_this_week": self.prime_mover_eccentric_intensity_this_week,
            # "synergist_concentric_intensity_last_week": self.synergist_concentric_intensity_last_week,
            # "synergist_concentric_intensity_this_week": self.synergist_concentric_intensity_this_week,
            # "synergist_eccentric_intensity_last_week": self.synergist_eccentric_intensity_last_week,
            # "synergist_eccentric_intensity_this_week": self.synergist_eccentric_intensity_this_week,
            # "synergist_compensating_concentric_intensity_last_week": self.synergist_compensating_concentric_intensity_last_week,
            # "synergist_compensating_concentric_intensity_this_week": self.synergist_compensating_concentric_intensity_this_week,
            # "synergist_compensating_eccentric_intensity_last_week": self.synergist_compensating_eccentric_intensity_last_week,
            # "synergist_compensating_eccentric_intensity_this_week": self.synergist_compensating_eccentric_intensity_this_week,

        }

    @classmethod
    def json_deserialise(cls, input_dict):
        injury_risk = cls()
        injury_risk.concentric_volume_last_week = input_dict.get('concentric_volume_last_week', 0)
        injury_risk.concentric_volume_this_week = input_dict.get('concentric_volume_this_week', 0)
        injury_risk.eccentric_volume_last_week = input_dict.get('eccentric_volume_last_week', 0)
        injury_risk.eccentric_volume_this_week = input_dict.get('eccentric_volume_this_week', 0)

        # injury_risk.prime_mover_concentric_volume_last_week = input_dict.get('prime_mover_concentric_volume_last_week', 0)
        # injury_risk.prime_mover_concentric_volume_this_week = input_dict.get('prime_mover_concentric_volume_this_week', 0)
        # injury_risk.prime_mover_eccentric_volume_last_week = input_dict.get('prime_mover_eccentric_volume_last_week', 0)
        # injury_risk.prime_mover_eccentric_volume_this_week = input_dict.get('prime_mover_eccentric_volume_this_week', 0)
        #
        # injury_risk.synergist_concentric_volume_last_week = input_dict.get('synergist_concentric_volume_last_week', 0)
        # injury_risk.synergist_concentric_volume_this_week = input_dict.get('synergist_concentric_volume_this_week', 0)
        # injury_risk.synergist_eccentric_volume_last_week = input_dict.get('synergist_eccentric_volume_last_week', 0)
        # injury_risk.synergist_eccentric_volume_this_week = input_dict.get('synergist_eccentric_volume_this_week', 0)
        # injury_risk.synergist_compensating_concentric_volume_last_week = input_dict.get('synergist_compensating_concentric_volume_last_week', 0)
        # injury_risk.synergist_compensating_concentric_volume_this_week = input_dict.get('synergist_compensating_concentric_volume_this_week', 0)
        # injury_risk.synergist_compensating_eccentric_volume_last_week = input_dict.get('synergist_compensating_eccentric_volume_last_week', 0)
        # injury_risk.synergist_compensating_eccentric_volume_this_week = input_dict.get('synergist_compensating_eccentric_volume_this_week', 0)

        injury_risk.concentric_intensity_last_week = input_dict.get('concentric_intensity_last_week', 0)
        injury_risk.concentric_intensity_this_week = input_dict.get('concentric_intensity_this_week', 0)
        injury_risk.eccentric_intensity_last_week = input_dict.get('eccentric_intensity_last_week', 0)
        injury_risk.eccentric_intensity_this_week = input_dict.get('eccentric_intensity_this_week', 0)

        # injury_risk.prime_mover_concentric_intensity_last_week = input_dict.get('prime_mover_concentric_intensity_last_week', 0)
        # injury_risk.prime_mover_concentric_intensity_this_week = input_dict.get('prime_mover_concentric_intensity_this_week', 0)
        # injury_risk.prime_mover_eccentric_intensity_last_week = input_dict.get('prime_mover_eccentric_intensity_last_week', 0)
        # injury_risk.prime_mover_eccentric_intensity_this_week = input_dict.get('prime_mover_eccentric_intensity_this_week', 0)
        #
        # injury_risk.synergist_concentric_intensity_last_week = input_dict.get('synergist_concentric_intensity_last_week', 0)
        # injury_risk.synergist_concentric_intensity_this_week = input_dict.get('synergist_concentric_intensity_this_week', 0)
        # injury_risk.synergist_eccentric_intensity_last_week = input_dict.get('synergist_eccentric_intensity_last_week', 0)
        # injury_risk.synergist_eccentric_intensity_this_week = input_dict.get('synergist_eccentric_intensity_this_week', 0)
        # injury_risk.synergist_compensating_concentric_intensity_last_week = input_dict.get('synergist_compensating_concentric_intensity_last_week', 0)
        # injury_risk.synergist_compensating_concentric_intensity_this_week = input_dict.get('synergist_compensating_concentric_intensity_this_week', 0)
        # injury_risk.synergist_compensating_eccentric_intensity_last_week = input_dict.get('synergist_compensating_eccentric_intensity_last_week', 0)
        # injury_risk.synergist_compensating_eccentric_intensity_this_week = input_dict.get('synergist_compensating_eccentric_intensity_this_week', 0)

        return injury_risk

    def __setattr__(self, name, value):
        if 'date_time' in name:
            if value is not None and not isinstance(value, datetime):
                value = parse_datetime(value)
        elif 'date' in name:
            if value is not None and not isinstance(value, date):
                value = parse_date(value).date()
        super().__setattr__(name, value)

    def merge(self, body_part_hist_injury_risk):

        self.concentric_volume_last_week = max(self.concentric_volume_last_week, body_part_hist_injury_risk.concentric_volume_last_week)
        self.concentric_volume_this_week = max(self.concentric_volume_this_week, body_part_hist_injury_risk.concentric_volume_this_week)
        self.eccentric_volume_last_week = max(self.eccentric_volume_last_week, body_part_hist_injury_risk.eccentric_volume_last_week)
        self.eccentric_volume_this_week = max(self.eccentric_volume_this_week, body_part_hist_injury_risk.eccentric_volume_this_week)

        # self.prime_mover_concentric_volume_last_week = max(self.prime_mover_concentric_volume_last_week, body_part_hist_injury_risk.prime_mover_concentric_volume_last_week)
        # self.prime_mover_concentric_volume_this_week = max(self.prime_mover_concentric_volume_this_week, body_part_hist_injury_risk.prime_mover_concentric_volume_this_week)
        # self.prime_mover_eccentric_volume_last_week = max(self.prime_mover_eccentric_volume_last_week, body_part_hist_injury_risk.prime_mover_eccentric_volume_last_week)
        # self.prime_mover_eccentric_volume_this_week = max(self.prime_mover_eccentric_volume_this_week, body_part_hist_injury_risk.prime_mover_eccentric_volume_this_week)
        #
        # self.synergist_concentric_volume_last_week = max(self.synergist_concentric_volume_last_week, body_part_hist_injury_risk.synergist_concentric_volume_last_week)
        # self.synergist_concentric_volume_this_week = max(self.synergist_concentric_volume_this_week, body_part_hist_injury_risk.synergist_concentric_volume_this_week)
        # self.synergist_eccentric_volume_last_week = max(self.synergist_eccentric_volume_last_week, body_part_hist_injury_risk.synergist_eccentric_volume_last_week)
        # self.synergist_eccentric_volume_this_week = max(self.synergist_eccentric_volume_this_week, body_part_hist_injury_risk.synergist_eccentric_volume_this_week)

    def merge_tiers(self, value_a, value_b):

        if value_a > 0 and value_b > 0:
            return min(value_a, value_b)
        elif value_a > 0 and value_b == 0:
            return value_a
        elif value_a == 0 and value_b > 0:
            return value_b
        else:
            return 0

    def merge_with_none(self, value_a, value_b):

        if value_a is None and value_b is None:
            return None
        if value_a is not None and value_b is None:
            return value_a
        if value_b is not None and value_a is None:
            return value_b
        if value_a is not None and value_b is not None:
            return max(value_a, value_b)

    def test_date(self, attribute, base_date):

        if attribute is not None and attribute == base_date:
            return True
        else:
            return False