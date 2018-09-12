from enum import Enum
from serialisable import Serialisable


class FitFatigueStatus(Enum):
    undefined = 0
    trending_toward_fatigue = 1
    trending_toward_fitness = 2


class AthleteStats(Serialisable):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id
        self.event_date = None

        self.acute_avg_RPE = None
        self.acute_avg_readiness = None
        self.acute_avg_sleep_quality = None
        self.acute_avg_max_soreness = None
        self.acute_internal_total_load = None
        self.acute_external_total_load = None
        self.acute_external_high_intensity_load = None
        self.acute_external_mod_intensity_load = None
        self.acute_external_low_intensity_load = None

        self.chronic_avg_RPE = None
        self.chronic_avg_readiness = None
        self.chronic_avg_sleep_quality = None
        self.chronic_avg_max_soreness = None
        self.chronic_internal_total_load = None
        self.chronic_external_total_load = None
        self.chronic_external_high_intensity_load = None
        self.chronic_external_mod_intensity_load = None
        self.chronic_external_low_intensity_load = None

        self.internal_monotony = None
        self.internal_strain = None
        self.external_monotony = None
        self.external_strain = None
        self.internal_ramp = None
        self.external_ramp = None
        self.functional_strength_eligible = False
        self.current_sport_name = None
        self.current_position = None
        self.last_functional_strength_completed_date = None

    def acute_to_chronic_external_ratio(self):
        if self.acute_external_total_load is not None and self.chronic_external_total_load is not None:
            return self.acute_external_total_load / self.chronic_external_total_load
        else:
            return None

    def acute_to_chronic_internal_ratio(self):
        if self.acute_internal_total_load is not None and self.chronic_internal_total_load is not None:
            return self.acute_internal_total_load / self.chronic_internal_total_load
        else:
            return None

    def acute_il_el_ratio(self):
        if self.acute_internal_total_load is not None and self.acute_external_total_load is not None:
            return self.acute_internal_total_load / self.acute_external_total_load
        else:
            return None

    def chronic_il_el_ratio(self):
        if self.chronic_internal_total_load is not None and self.chronic_external_total_load is not None:
            return self.chronic_internal_total_load / self.chronic_external_total_load
        else:
            return None

    def fit_fatigue_status(self):
        acute = self.acute_il_el_ratio()
        chronic = self.chronic_il_el_ratio()
        status = FitFatigueStatus.undefined

        if acute is not None and chronic is not None:
            if acute > chronic:
                status = FitFatigueStatus.trending_toward_fatigue
            elif chronic > acute:
                status = FitFatigueStatus.trending_toward_fitness

        return status

    def external_freshness_index(self):
        if self.chronic_external_total_load is not None and self.acute_external_total_load is not None:
            return self.chronic_external_total_load - self.acute_external_total_load
        else:
            return None

    def internal_freshness_index(self):
        if self.chronic_internal_total_load is not None and self.acute_internal_total_load is not None:
            return self.chronic_internal_total_load - self.acute_internal_total_load
        else:
            return None


    def json_serialise(self):
        ret = {
            'athlete_id': self.athlete_id,
            'event_date': self.event_date,
            'acute_avg_RPE': self.acute_avg_RPE,
            'acute_avg_readiness': self.acute_avg_readiness,
            'acute_avg_sleep_quality': self.acute_avg_sleep_quality,
            'acute_avg_max_soreness': self.acute_avg_max_soreness,
            'acute_internal_total_load': self.acute_internal_total_load,
            'acute_external_total_load': self.acute_external_total_load,
            'acute_external_high_intensity_load': self.acute_external_high_intensity_load,
            'acute_external_mod_intensity_load': self.acute_external_mod_intensity_load,
            'acute_external_low_intensity_load': self.acute_external_low_intensity_load,
            'chronic_avg_RPE': self.chronic_avg_RPE,
            'chronic_avg_readiness': self.chronic_avg_readiness,
            'chronic_avg_sleep_quality': self.chronic_avg_sleep_quality,
            'chronic_avg_max_soreness': self.chronic_avg_max_soreness,
            'chronic_internal_total_load': self.chronic_internal_total_load,
            'chronic_external_total_load': self.chronic_external_total_load,
            'chronic_external_high_intensity_load': self.chronic_external_high_intensity_load,
            'chronic_external_mod_intensity_load': self.chronic_external_mod_intensity_load,
            'chronic_external_low_intensity_load': self.chronic_external_low_intensity_load,
            'functional_strength_eligible': self.functional_strength_eligible,
        }
        return ret
