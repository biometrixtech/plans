from serialisable import Serialisable


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
        }
        return ret
