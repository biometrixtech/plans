from enum import Enum
from serialisable import Serialisable
from models.sport import SportName, NoSportPosition, BaseballPosition, BasketballPosition, FootballPosition, LacrossePosition, SoccerPosition, SoftballPosition, FieldHockeyPosition, TrackAndFieldPosition
from utils import format_date
from models.soreness import HistoricSorenessStatus

class FitFatigueStatus(Enum):
    undefined = 0
    trending_toward_fatigue = 1
    trending_toward_fitness = 2


class AthleteStats(Serialisable):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id
        self.event_date = None

        self.session_RPE = None
        self.session_RPE_event_date = None

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
        self.next_functional_strength_eligible_date = None
        self.completed_functional_strength_sessions = 0
        self.current_sport_name = None
        self.current_position = None

        self.historic_soreness = []
        self.daily_severe_soreness = []
        self.daily_severe_pain = []
        self.daily_severe_pain_event_date = None
        self.daily_severe_soreness_event_date = None

    def update_historic_soreness(self, soreness, event_date):

        for h in range(0, len(self.historic_soreness)):
            if (self.historic_soreness[h].body_part_location == soreness.body_part.location.value and
                    self.historic_soreness[h].side == soreness.side and
                    self.historic_soreness[h].is_pain == soreness.pain):
                # was historic_soreness already updated today?
                if format_date(event_date) != self.historic_soreness[h].last_updated: #not updated
                    if self.historic_soreness[h].historic_soreness_status == HistoricSorenessStatus.almost_persistent:
                        self.historic_soreness[h].historic_soreness_status = HistoricSorenessStatus.persistent
                    elif self.historic_soreness[h].historic_soreness_status == HistoricSorenessStatus.persistent_almost_chronic:
                        self.historic_soreness[h].historic_soreness_status = HistoricSorenessStatus.chronic
                    else:
                        break

                    self.historic_soreness[h].last_updated = event_date
                    # weighted average
                    self.historic_soreness[h].average_severity = (
                        ((self.historic_soreness[h].average_severity * (float(self.historic_soreness[h].streak) /
                                                                      float(self.historic_soreness[h].streak) + 1
                                                                      )) +
                        (soreness.severity * (float(1) / float(self.historic_soreness[h].streak) + 1))) /
                        float(self.historic_soreness[h].streak) + 1
                    )

                    self.historic_soreness[h].streak = self.historic_soreness[h].streak + 1
                    break
                else:
                    # we first have to determine if current value is higher previous day's value
                    for s in self.daily_severe_soreness:
                        if (self.daily_severe_soreness[h].body_part.location.value == soreness.body_part.location.value and
                                self.daily_severe_soreness[h].side == soreness.side and
                                self.daily_severe_soreness[h].pain == soreness.pain):
                            if s.severity >= soreness.severity:
                                break
                            else:
                                new_severity = (((self.historic_soreness[h].average_severity *
                                                self.historic_soreness[h].streak) - s.severity) /
                                                (float(self.historic_soreness[h].streak - 1)))
                                self.historic_soreness[h].average_severity = new_severity
                                # temporarily set it back to keep consistency with algo
                                self.historic_soreness[h].streak = self.historic_soreness[h].streak - 1
                                self.historic_soreness[h].average_severity = (
                                        ((self.historic_soreness[h].average_severity * (
                                                    float(self.historic_soreness[h].streak) /
                                                    float(self.historic_soreness[h].streak) + 1
                                                    )) +
                                         (soreness.severity * (
                                                     float(1) / float(self.historic_soreness[h].streak) + 1))) /
                                        float(self.historic_soreness[h].streak) + 1
                                )
                                self.historic_soreness[h].streak = self.historic_soreness[h].streak + 1
                                break


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

    def __setattr__(self, name, value):
        if name == "current_sport_name":
            value = SportName(value)
        elif name == "current_position":
            if self.current_sport_name.value is None and value is not None:
                value = NoSportPosition(value)
            elif self.current_sport_name == SportName.soccer:
                value = SoccerPosition(value)
            elif self.current_sport_name == SportName.basketball:
                value = BasketballPosition(value)
            elif self.current_sport_name == SportName.baseball:
                value = BaseballPosition(value)
            elif self.current_sport_name == SportName.softball:
                value = SoftballPosition(value)
            elif self.current_sport_name == SportName.football:
                value = FootballPosition(value)
            elif self.current_sport_name == SportName.lacrosse:
                value = LacrossePosition(value)
            elif self.current_sport_name == SportName.field_hockey:
                value = FieldHockeyPosition(value)
            elif self.current_sport_name == SportName.track_field:
                value = TrackAndFieldPosition(value)
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'athlete_id': self.athlete_id,
            'event_date': self.event_date,
            'session_RPE': self.session_RPE,
            'session_RPE_event_date': self.session_RPE_event_date,
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
            'completed_functional_strength_sessions': self.completed_functional_strength_sessions,
            'next_functional_strength_eligible_date': self.next_functional_strength_eligible_date,
            'current_sport_name': self.current_sport_name.value,
            'current_position': self.current_position.value if self.current_position is not None else None,
            'historic_soreness': [h.json_serialise() for h in self.historic_soreness],
            'daily_severe_pain': [s.json_serialise() for s in self.daily_severe_pain],
            'daily_severe_soreness': [s.json_serialise() for s in self.daily_severe_soreness],
            'daily_severe_soreness_event_date': self.daily_severe_soreness_event_date,
            'daily_severe_pain_event_date': self.daily_severe_pain_event_date
        }
        return ret
