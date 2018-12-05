from enum import Enum
from serialisable import Serialisable
from models.sport import SportName, NoSportPosition, BaseballPosition, BasketballPosition, FootballPosition, LacrossePosition, SoccerPosition, SoftballPosition, FieldHockeyPosition, TrackAndFieldPosition
from utils import format_date, parse_date
from models.soreness import HistoricSorenessStatus
from logic.soreness_processing import SorenessCalculator

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
        self.readiness_soreness = []
        self.post_session_soreness = []
        self.readiness_pain = []
        self.post_session_pain = []
        self.daily_severe_soreness = []
        self.daily_severe_pain = []
        self.daily_severe_pain_event_date = None
        self.daily_severe_soreness_event_date = None
        self.acute_pain = False
        self.metrics = []

    def update_historic_soreness(self, soreness, event_date):

        for h in self.historic_soreness:
            if (h.body_part_location == soreness.body_part.location.value and
                h.side == soreness.side and
                h.is_pain == soreness.pain):
                # was historic_soreness already updated today?
                if format_date(event_date) != h.last_reported: #not updated
                    if h.is_pain:
                        if h.historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain:
                            h.historic_soreness_status = HistoricSorenessStatus.persistent_pain
                        elif h.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain:
                            h.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
                        else:
                            break
                    else:
                        if h.historic_soreness_status == HistoricSorenessStatus.almost_persistent_soreness:
                            h.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
                        elif h.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_soreness:
                            h.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
                        else:
                            break
                    h.last_reported = event_date
                    # weighted average
                    h.average_severity = round(h.average_severity * float(h.streak) / (float(h.streak) + 1) +
                                               soreness.severity * float(1) / (float(h.streak) + 1), 2)
                    

                    h.streak = h.streak + 1
                    break
                else:
                    # we first have to determine if current value is higher previous day's value
                    pain_soreness_list = self.daily_severe_soreness
                    pain_soreness_list.extend(self.daily_severe_pain)
                    for s in pain_soreness_list:
                        if (s.body_part.location.value == soreness.body_part.location.value and
                            s.side == soreness.side and
                            s.pain == soreness.pain):
                            if s.severity >= soreness.severity:
                                break
                            else:
                                new_severity = ((h.average_severity * h.streak) - s.severity) / (float(h.streak - 1))
                                h.average_severity = new_severity
                                # temporarily set it back to keep consistency with algo
                                h.streak = h.streak - 1
                                h.average_severity = round(h.average_severity * float(h.streak) / (float(h.streak) + 1) +
                                                           soreness.severity * float(1) / (float(h.streak) + 1), 2)
                                h.streak = h.streak + 1
                                break

    def persist_soreness(self, event_date, soreness):
        if soreness.reported_date_time is not None:
            if (parse_date(event_date).date() - soreness.reported_date_time.date()).days <= 1:
                return True
            else:
                return False
        else:
            return False

    def update_daily_soreness(self, severe_soreness):
        # make sure old sorenesses are cleared out
        soreness_list = [s for s in self.daily_severe_soreness if self.persist_soreness(self.event_date, s)]
        # merge sorenesses from current survey
        soreness_list = SorenessCalculator().update_soreness_list(soreness_list, severe_soreness)
        self.daily_severe_soreness = soreness_list

    def update_daily_pain(self, severe_pain):
        # make sure old pains are cleared out
        pain_list = [s for s in self.daily_severe_pain if self.persist_soreness(self.event_date, s)]
        # merge pains from the current survey
        pain_list = SorenessCalculator().update_soreness_list(pain_list, severe_pain)
        self.daily_severe_pain = pain_list

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
            'readiness_soreness': [s.json_serialise_daily_soreness() for s in self.readiness_soreness],
            'post_session_soreness': [s.json_serialise_daily_soreness() for s in self.post_session_soreness],
            'readiness_pain': [s.json_serialise_daily_soreness() for s in self.readiness_pain],
            'post_session_pain': [s.json_serialise_daily_soreness() for s in self.post_session_pain],
            'daily_severe_pain': [s.json_serialise_daily_soreness() for s in self.daily_severe_pain],
            'daily_severe_soreness': [s.json_serialise_daily_soreness() for s in self.daily_severe_soreness],
            'daily_severe_soreness_event_date': self.daily_severe_soreness_event_date,
            'daily_severe_pain_event_date': self.daily_severe_pain_event_date,
            'metrics': [m.json_serialise() for m in self.metrics]
        }
        return ret
