from serialisable import Serialisable
from fathomapi.utils.exceptions import InvalidSchemaException
from logic.soreness_processing import SorenessCalculator
from models.athlete_trend import Trend
from models.data_series import DataSeries
from models.historic_soreness import HistoricSeverity, HistoricSoreness
from models.insights import AthleteInsight
from models.load_stats import LoadStats
from models.metrics import AthleteMetric
from models.session import StrengthConditioningType, HighLoadSession
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus
from models.sport import SportName, BaseballPosition, BasketballPosition, FootballPosition, LacrossePosition, SoccerPosition,\
    SoftballPosition, FieldHockeyPosition, TrackAndFieldPosition, VolleyballPosition
from models.training_volume import StandardErrorRange
from models.trigger import TriggerType, Trigger
from utils import format_date, format_datetime, parse_date, parse_datetime
import datetime
import numbers


class SportMaxLoad(Serialisable):
    def __init__(self, event_date_time, load):
        self.event_date_time = event_date_time
        self.load = load
        self.first_time_logged = False

    def json_serialise(self):
        ret = {
            'event_date_time': format_datetime(self.event_date_time),
            'load': self.load,
            'first_time_logged': self.first_time_logged
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        sport_max_load = cls(parse_datetime(input_dict['event_date_time']), input_dict['load'])
        sport_max_load.first_time_logged = input_dict.get('first_time_logged', False)
        return sport_max_load


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
        # self.acute_external_total_load = None
        # self.acute_external_high_intensity_load = None
        # self.acute_external_mod_intensity_load = None
        # self.acute_external_low_intensity_load = None

        self.chronic_avg_RPE = None
        self.chronic_avg_readiness = None
        self.chronic_avg_sleep_quality = None
        self.chronic_avg_max_soreness = None
        self.chronic_internal_total_load = None
        # self.chronic_external_total_load = None
        # self.chronic_external_high_intensity_load = None
        # self.chronic_external_mod_intensity_load = None
        # self.chronic_external_low_intensity_load = None

        self.internal_monotony = None
        self.internal_strain = None
        # self.external_monotony = None
        # self.external_strain = None
        self.internal_ramp = None
        # self.external_ramp = None

        self.training_load_ramp = {}

        self.internal_acwr = None
        # self.external_acwr = None
        self.internal_freshness_index = None
        # self.external_freshness_index = None
        self.historical_internal_strain = []
        self.historical_internal_monotony = []
        self.historical_external_strain = []
        self.internal_strain_events = None
        # self.functional_strength_eligible = False
        # self.next_functional_strength_eligible_date = None
        # self.completed_functional_strength_sessions = 0
        self.current_sport_name = None
        self.current_position = None

        self.expected_weekly_workouts = None

        self.historic_soreness = []
        self.readiness_soreness = []
        self.post_session_soreness = []
        self.readiness_pain = []
        self.post_session_pain = []
        self.daily_severe_soreness = []
        self.daily_severe_pain = []
        self.daily_severe_pain_event_date = None
        self.daily_severe_soreness_event_date = None
        # self.delayed_onset_muscle_soreness = []

        self.metrics = []
        self.typical_weekly_sessions = None
        self.wearable_devices = []

        self.muscular_strain_increasing = False
        self.muscular_strain = []
        # self.high_relative_load_session = False
        # self.high_relative_load_session_sport_name = None
        # self.high_relative_intensity_session = False
        self.high_relative_load_benchmarks = {}
        self.exposed_triggers = []
        self.longitudinal_insights = []
        self.longitudinal_trends = []
        self.load_stats = LoadStats()
        self.high_relative_load_sessions = []
        self.training_volume_chart_data = []

        self.soreness_chart_data = {}
        self.pain_chart_data = {}
        self.muscular_strain_chart_data = []
        self.high_relative_load_chart_data = []
        self.doms_chart_data = []

        self.workout_chart = None
        self.body_response_chart = None

        self.eligible_for_high_load_trigger = False

        self.sport_max_load = {}

        self.triggers = []

    def update_historic_soreness(self, soreness, event_date):

        soreness_calc = SorenessCalculator

        for h in self.historic_soreness:
            if (h.body_part_location == soreness.body_part.location and
                    h.side == soreness.side and h.is_pain == soreness.pain):
                # was historic_soreness already updated today?
                if event_date != h.last_reported_date_time:  # not updated
                    if h.is_pain:
                        if h.historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain:
                            h.historic_soreness_status = HistoricSorenessStatus.persistent_pain
                        elif h.historic_soreness_status in [HistoricSorenessStatus.almost_persistent_2_pain, HistoricSorenessStatus.almost_persistent_2_pain_acute]:
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
                    h.last_reported_date_time = event_date
                    # weighted average
                    h.average_severity = round(h.average_severity * float(h.streak) / (float(h.streak) + 1) +
                                               soreness_calc.get_severity(soreness.severity, soreness.movement) * float(1) / (float(h.streak) + 1), 2)

                    h.streak = h.streak + 1
                    break
                else:
                    # we first have to determine if current value is higher previous day's value
                    pain_soreness_list = [s for s in self.daily_severe_soreness if self.persist_soreness(s, days=0)]
                    pain_soreness_list.extend([s for s in self.daily_severe_pain if self.persist_soreness(s, days=0)])
                    for s in pain_soreness_list:
                        if (s.body_part.location.value == soreness.body_part.location.value and
                                s.side == soreness.side and s.pain == soreness.pain):
                            if s.severity >= soreness_calc.get_severity(soreness.severity, soreness.movement):
                                break
                            else:
                                new_severity = ((h.average_severity * h.streak) - s.severity) / (float(h.streak - 1))
                                h.average_severity = new_severity
                                # temporarily set it back to keep consistency with algo
                                h.streak = h.streak - 1
                                h.average_severity = round(h.average_severity * float(h.streak) / (float(h.streak) + 1) +
                                                           soreness_calc.get_severity(soreness.severity,
                                                                                      soreness.movement) * float(1) / (float(h.streak) + 1), 2)
                                h.streak = h.streak + 1
                                break

    def persist_soreness(self, soreness, days=1):
        if soreness.reported_date_time is not None:
            if (self.event_date.date() - soreness.reported_date_time.date()).days <= days:
                return True
            else:
                return False
        else:
            return False

    def update_readiness_soreness(self, severe_soreness):
        self.readiness_soreness = [s for s in self.readiness_soreness if self.persist_soreness(s)]
        self.readiness_soreness.extend(severe_soreness)

    def update_readiness_pain(self, severe_pain):
        self.readiness_pain = [s for s in self.readiness_pain if self.persist_soreness(s)]
        self.readiness_pain.extend(severe_pain)

    def update_post_session_soreness(self, severe_soreness):
        self.post_session_soreness = [s for s in self.post_session_soreness if self.persist_soreness(s)]
        self.post_session_soreness.extend(severe_soreness)

    def update_post_session_pain(self, severe_pain):
        self.post_session_pain = [s for s in self.post_session_pain if self.persist_soreness(s)]
        self.post_session_pain.extend(severe_pain)

    def update_daily_soreness(self):
        # make sure old sorenesses are cleared out
        soreness_list = [s for s in self.daily_severe_soreness if self.persist_soreness(s)]
        # merge sorenesses from current survey
        soreness_list = SorenessCalculator().update_soreness_list(soreness_list, self.readiness_soreness)
        soreness_list = SorenessCalculator().update_soreness_list(soreness_list, self.post_session_soreness)
        self.daily_severe_soreness = soreness_list

    def update_daily_pain(self):
        # make sure old pains are cleared out
        pain_list = [s for s in self.daily_severe_pain if self.persist_soreness(s)]
        # merge pains from the current survey
        pain_list = SorenessCalculator().update_soreness_list(pain_list, self.readiness_pain)
        pain_list = SorenessCalculator().update_soreness_list(pain_list, self.post_session_pain)
        self.daily_severe_pain = pain_list

    def update_delayed_onset_muscle_soreness(self, soreness):
        body_part_exists = False
        if not soreness.pain:
            current_soreness = HistoricSeverity(soreness.reported_date_time, soreness.severity, soreness.movement)
            current_severity = SorenessCalculator.get_severity(soreness.severity, soreness.movement)
            for doms in self.historic_soreness:
                if doms.body_part_location == soreness.body_part.location and \
                        doms.side == soreness.side and not doms.is_pain:
                    body_part_exists = True
                    if doms.historic_soreness_status == HistoricSorenessStatus.doms:
                        doms.historic_severity.append(current_soreness)
                        doms.last_reported_date_time = current_soreness.reported_date_time
                        doms.average_severity = current_severity
                        if current_severity > doms.max_severity:
                            doms.max_severity = current_severity
                            doms.max_severity_date_time = current_soreness.reported_date_time
                    elif doms.historic_soreness_status == HistoricSorenessStatus.dormant_cleared:
                        doms.historic_soreness_status = HistoricSorenessStatus.doms
                        doms.first_reported_date_time = soreness.reported_date_time
                        doms.last_reported_date_time = soreness.reported_date_time
                        doms.max_severity = current_severity
                        doms.average_severity = current_severity
                        doms.max_severity_date_time = soreness.reported_date_time
                        doms.historic_severity.append(current_soreness)
            if not body_part_exists:
                doms = HistoricSoreness(soreness.body_part.location, soreness.side, False)
                doms.historic_soreness_status = HistoricSorenessStatus.doms
                doms.first_reported_date_time = soreness.reported_date_time
                doms.last_reported_date_time = soreness.reported_date_time
                doms.average_severity = current_severity
                doms.max_severity = current_severity
                doms.max_severity_date_time = soreness.reported_date_time
                doms.historic_severity.append(current_soreness)
                self.historic_soreness.append(doms)

    def clear_delayed_onset_muscle_soreness(self, current_date_time):
        cleared_doms = []
        for doms in self.historic_soreness:
            if doms.historic_soreness_status == HistoricSorenessStatus.doms:
                last_reported_severity = [hist for hist in doms.historic_severity if hist.reported_date_time == doms.last_reported_date_time][0]
                last_severity_value = SorenessCalculator.get_severity(last_reported_severity.severity, last_reported_severity.movement)
                if last_severity_value <= 2:
                    clearance_window = 1
                else:
                    clearance_window = 2
                days_since_last_report = (current_date_time.date() - doms.last_reported_date_time.date()).days
                if days_since_last_report >= clearance_window:
                    doms.user_id = self.athlete_id
                    doms.cleared_date_time = current_date_time
                    cleared_doms.append(doms)
        self.historic_soreness = [doms for doms in self.historic_soreness if doms.cleared_date_time is None]
        return cleared_doms

    def severe_pain_soreness_today(self):
        severe_pain = [s for s in self.daily_severe_pain if s.severity >= 3]
        severe_soreness = [s for s in self.daily_severe_soreness if s.severity >= 4]
        if len(severe_pain) + len(severe_soreness) == 0:
            return False
        else:
            return True

    '''deprecated
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
    '''
    def get_q2_q3_list(self):
        q2 = []
        q3 = []
        tipping_status = []
        unique_q2 = []
        unique_q3 = []
        unique_tipping_status = []
        for soreness in self.historic_soreness:
            new_part = soreness.json_serialise(api=True)
            if soreness.ask_persistent_2_question or soreness.ask_acute_pain_question:
                self._add_body_part(new_part, q3, unique_q3)
            elif soreness.historic_soreness_status in [HistoricSorenessStatus.almost_persistent_pain,
                                                       HistoricSorenessStatus.almost_persistent_soreness,
                                                       HistoricSorenessStatus.almost_acute_pain]:
                self._add_body_part(new_part, tipping_status, unique_tipping_status)
            elif soreness.historic_soreness_status != HistoricSorenessStatus.dormant_cleared:
                self._add_body_part(new_part, q2, unique_q2)

        for q2_part in q2:
            if {q2_part["body_part"]: q2_part["side"]} in unique_q3:
                q2_part['delete'] = True
        for tipping_part in tipping_status:
            if {tipping_part["body_part"]: tipping_part["side"]} in unique_q3 or {tipping_part["body_part"]: tipping_part["side"]} in unique_q2:
                tipping_part['delete'] = True
        q2 = [s for s in q2 if not s.get('delete', False)]
        tipping_status = [s for s in tipping_status if not s.get('delete', False)]

        return q2, q3, tipping_status

    @staticmethod
    def _add_body_part(new_part, full_list, unique_list):
        # add body part to the list if it doesn't already exist. update to pain if new is pain and existing is soreness
        if {new_part["body_part"]: new_part["side"]} in unique_list:
            for part in full_list:
                if part['body_part'] == new_part['body_part'] and part['side'] == new_part['side']:
                    if new_part['pain']:
                        part['pain'] = True
                        part['status'] = new_part['status']
                    break
        else:
            unique_list.append({new_part["body_part"]: new_part["side"]})
            full_list.append(new_part)

    def __setattr__(self, name, value):
        if name in ["current_sport_name", "high_relative_load_session_sport_name"]:
            try:
                value = SportName(value)
            except ValueError:
                value = SportName(None)
        elif name in ['daily_severe_soreness_event_date', 'daily_severe_pain_event_date']:
            if value is not None and not isinstance(value, datetime.datetime):
                try:
                    value = parse_date(value)
                except InvalidSchemaException:
                    value = parse_datetime(value)
        elif name == "current_position":
            if self.current_sport_name.value is None and value is not None:
                value = StrengthConditioningType(value)
            else:
                try:
                    if self.current_sport_name == SportName.soccer:
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
                    elif self.current_sport_name == SportName.volleyball:
                        value = VolleyballPosition(value)
                    elif value is not None:
                            raise InvalidSchemaException("Positions do not exist for the provided sport")
                except ValueError:
                    raise InvalidSchemaException("Position is required for the provided sport")
                except InvalidSchemaException:
                    raise
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'athlete_id': self.athlete_id,
            'event_date': format_date(self.event_date),
            'session_RPE': self.session_RPE,
            'session_RPE_event_date': self.session_RPE_event_date,
            'acute_avg_RPE': self.acute_avg_RPE,
            'acute_avg_readiness': self.acute_avg_readiness,
            'acute_avg_sleep_quality': self.acute_avg_sleep_quality,
            'acute_avg_max_soreness': self.acute_avg_max_soreness,
            'acute_internal_total_load': self.acute_internal_total_load.json_serialise() if self.acute_internal_total_load is not None else None,
            # 'acute_external_total_load': self.acute_external_total_load.json_serialise() if self.acute_external_total_load is not None else None,
            # 'acute_external_high_intensity_load': self.acute_external_high_intensity_load.json_serialise() if self.acute_external_high_intensity_load is not None else None,
            # 'acute_external_mod_intensity_load': self.acute_external_mod_intensity_load.json_serialise() if self.acute_external_mod_intensity_load is not None else None,
            # 'acute_external_low_intensity_load': self.acute_external_low_intensity_load.json_serialise() if self.acute_external_low_intensity_load is not None else None,
            'chronic_avg_RPE': self.chronic_avg_RPE,
            'chronic_avg_readiness': self.chronic_avg_readiness,
            'chronic_avg_sleep_quality': self.chronic_avg_sleep_quality,
            'chronic_avg_max_soreness': self.chronic_avg_max_soreness,
            'chronic_internal_total_load': self.chronic_internal_total_load.json_serialise() if self.chronic_internal_total_load is not None else None,
            # 'chronic_external_total_load': self.chronic_external_total_load.json_serialise() if self.chronic_external_total_load is not None else None,
            # 'chronic_external_high_intensity_load': self.chronic_external_high_intensity_load.json_serialise() if self.chronic_external_high_intensity_load is not None else None,
            # 'chronic_external_mod_intensity_load': self.chronic_external_mod_intensity_load.json_serialise() if self.chronic_external_mod_intensity_load is not None else None,
            # 'chronic_external_low_intensity_load': self.chronic_external_low_intensity_load.json_serialise() if self.chronic_external_low_intensity_load is not None else None,
            'internal_monotony': self.internal_monotony.json_serialise() if self.internal_monotony is not None else None,
            'historical_internal_monotony': [h.json_serialise() for h in self.historical_internal_monotony],
            'internal_strain': self.internal_strain.json_serialise() if self.internal_strain is not None else None,
            'historical_internal_strain': [h.json_serialise() for h in self.historical_internal_strain],
            'internal_strain_events': self.internal_strain_events.json_serialise() if self.internal_strain_events is not None else None,
            # 'external_monotony': self.external_monotony.json_serialise() if self.external_monotony is not None else None,
            # 'external_strain': self.external_strain.json_serialise() if self.external_strain is not None else None,
            'internal_ramp': self.internal_ramp.json_serialise() if self.internal_ramp is not None else None,
            # 'external_ramp': self.external_ramp.json_serialise() if self.external_ramp is not None else None,
            'training_load_ramp': {str(sport_name.value): standardard_error_range.json_serialise()
                                   for (sport_name, standardard_error_range) in self.training_load_ramp.items()},
            'internal_acwr': self.internal_acwr.json_serialise() if self.internal_acwr is not None else None,
            # 'external_acwr': self.external_acwr.json_serialise() if self.external_acwr is not None else None,
            # 'functional_strength_eligible': self.functional_strength_eligible,
            # 'completed_functional_strength_sessions': self.completed_functional_strength_sessions,
            # 'next_functional_strength_eligible_date': self.next_functional_strength_eligible_date,
            'current_sport_name': self.current_sport_name.value,
            'current_position': self.current_position.value if self.current_position is not None else None,
            'expected_weekly_workouts': self.expected_weekly_workouts,
            'historic_soreness': [h.json_serialise() for h in self.historic_soreness],
            'readiness_soreness': [s.json_serialise(daily=True) for s in self.readiness_soreness],
            'post_session_soreness': [s.json_serialise(daily=True) for s in self.post_session_soreness],
            'readiness_pain': [s.json_serialise(daily=True) for s in self.readiness_pain],
            'post_session_pain': [s.json_serialise(daily=True) for s in self.post_session_pain],
            'daily_severe_pain': [s.json_serialise(daily=True) for s in self.daily_severe_pain],
            'daily_severe_soreness': [s.json_serialise(daily=True) for s in self.daily_severe_soreness],
            'daily_severe_soreness_event_date': format_date(self.daily_severe_soreness_event_date),
            'daily_severe_pain_event_date': format_date(self.daily_severe_pain_event_date),
            # 'delayed_onset_muscle_soreness': [s.json_serialise() for s in self.delayed_onset_muscle_soreness],
            'metrics': [m.json_serialise() for m in self.metrics],
            'typical_weekly_sessions': self.typical_weekly_sessions,
            'wearable_devices': self.wearable_devices,
            'muscular_strain_increasing': self.muscular_strain_increasing,
            # 'high_relative_load_session': self.high_relative_load_session,
            # 'high_relative_load_session_sport_name': self.high_relative_load_session_sport_name.value,
            # 'high_relative_intensity_session': self.high_relative_intensity_session,
            'high_relative_load_benchmarks': {sport_name.value: load for (sport_name, load) in
                                              self.high_relative_load_benchmarks.items()},
            'exposed_triggers': [trigger.value for trigger in self.exposed_triggers],
            'longitudinal_insights': [insight.json_serialise() for insight in self.longitudinal_insights],
            'longitudinal_trends': [trend.json_serialise() for trend in self.longitudinal_trends],
            'load_stats': self.load_stats.json_serialise() if self.load_stats is not None else None,
            'muscular_strain': [muscular_strain.json_serialise() for muscular_strain in self.muscular_strain],
            'high_relative_load_sessions': [high_load.json_serialise() for high_load in self.high_relative_load_sessions],
            'eligible_for_high_load_trigger' : self.eligible_for_high_load_trigger,
            'sport_max_load': {str(sport_name): sport_max_load.json_serialise() for (sport_name, sport_max_load) in self.sport_max_load.items()},
            'triggers': [s.json_serialise() for s in self.triggers]
            # 'workout_chart': self.workout_chart.json_serialise() if self.workout_chart is not None else None,
            # 'body_response_chart': self.body_response_chart.json_serialise() if self.body_response_chart is not None else None
            # 'training_volume_chart_data': [chart_data.json_serialise() for chart_data in self.training_volume_chart_data]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        athlete_stats = AthleteStats(athlete_id=input_dict['athlete_id'])
        athlete_stats.event_date = parse_date(input_dict['event_date']) if input_dict['event_date'] is not None else None
        athlete_stats.session_RPE = input_dict.get('session_RPE', None)
        athlete_stats.session_RPE_event_date = input_dict.get('session_RPE_event_date', None)
        athlete_stats.acute_avg_RPE = input_dict['acute_avg_RPE']
        athlete_stats.acute_avg_readiness = input_dict['acute_avg_readiness']
        athlete_stats.acute_avg_sleep_quality = input_dict['acute_avg_sleep_quality']
        athlete_stats.acute_avg_max_soreness = input_dict['acute_avg_max_soreness']
        athlete_stats.chronic_avg_RPE = input_dict['chronic_avg_RPE']
        athlete_stats.chronic_avg_readiness = input_dict['chronic_avg_readiness']
        athlete_stats.chronic_avg_sleep_quality = input_dict['chronic_avg_sleep_quality']
        athlete_stats.chronic_avg_max_soreness = input_dict['chronic_avg_max_soreness']
        athlete_stats.acute_internal_total_load = cls._standard_error_from_monogodb(input_dict.get('acute_internal_total_load', None))
        athlete_stats.chronic_internal_total_load = cls._standard_error_from_monogodb(input_dict.get('chronic_internal_total_load', None))
        athlete_stats.internal_monotony = cls._standard_error_from_monogodb(input_dict.get('internal_monotony', None))
        athlete_stats.historical_internal_monotony = [cls._standard_error_from_monogodb(s)
                                                      for s in input_dict.get('historic_internal_monotony', [])]
        athlete_stats.internal_strain = cls._standard_error_from_monogodb(input_dict.get('internal_strain', None))
        athlete_stats.historical_internal_strain = [cls._standard_error_from_monogodb(s)
                                                    for s in input_dict.get('historic_internal_strain', [])]
        athlete_stats.internal_strain_events = cls._standard_error_from_monogodb(input_dict.get('internal_strain_events', None))
        athlete_stats.internal_ramp = cls._standard_error_from_monogodb(input_dict.get('internal_ramp', None))
        athlete_stats.training_load_ramp = {SportName(int(value)): cls._standard_error_from_monogodb(load) for (value, load) in
                                            input_dict.get('training_load_ramp', {}).items()}
        athlete_stats.internal_acwr = cls._standard_error_from_monogodb(input_dict.get('internal_acwr', None))
        athlete_stats.current_sport_name = input_dict.get('current_sport_name', None)
        athlete_stats.current_position = input_dict.get('current_position', None)
        athlete_stats.expected_weekly_workouts = cls._expected_workouts_from_mongo(input_dict)
        athlete_stats.historic_soreness = [HistoricSoreness.json_deserialise(s) for s in input_dict.get('historic_soreness', [])]
        athlete_stats.daily_severe_soreness = [Soreness.json_deserialise(s) for s in input_dict.get('daily_severe_soreness', [])]
        athlete_stats.daily_severe_pain = [Soreness.json_deserialise(s) for s in input_dict.get('daily_severe_pain', [])]
        athlete_stats.readiness_soreness = [Soreness.json_deserialise(s) for s in input_dict.get('readiness_soreness', [])]
        athlete_stats.post_session_soreness = [Soreness.json_deserialise(s) for s in input_dict.get('post_session_soreness', [])]
        athlete_stats.readiness_pain = [Soreness.json_deserialise(s) for s in input_dict.get('readiness_pain', [])]
        athlete_stats.post_session_pain = [Soreness.json_deserialise(s) for s in input_dict.get('post_session_pain', [])]
        athlete_stats.daily_severe_soreness_event_date = input_dict.get('daily_severe_soreness_event_date', None)
        athlete_stats.daily_severe_pain_event_date = input_dict.get('daily_severe_soreness_event_date', None)
        athlete_stats.metrics = [AthleteMetric.json_deserialise(s) for s in input_dict.get('metrics', [])]
        athlete_stats.typical_weekly_sessions = input_dict.get('typical_weekly_sessions', None)
        athlete_stats.wearable_devices = input_dict.get('wearable_devices', [])
        athlete_stats.muscular_strain_increasing = input_dict.get('muscular_strain_increasing', False)
        athlete_stats.high_relative_load_benchmarks = {SportName(value): load for (value, load) in input_dict.get('high_relative_load_benchmarks', {}).items()}
        athlete_stats.exposed_triggers = [TriggerType(trigger) for trigger in input_dict.get('exposed_triggers', [])]
        athlete_stats.longitudinal_insights = [AthleteInsight.json_deserialise(insight) for insight in input_dict.get('longitudinal_insights', [])]
        athlete_stats.longitudinal_trends = [Trend.json_deserialise(trend) for trend in input_dict.get('longitudinal_trends', [])]
        athlete_stats.load_stats = LoadStats.json_deserialise(input_dict.get('load_stats', None))
        athlete_stats.muscular_strain = [DataSeries.json_deserialise(muscular_strain) for muscular_strain in input_dict.get('muscular_strain', [])]
        athlete_stats.high_relative_load_sessions = [HighLoadSession.json_deserialise(session) for session in input_dict.get('high_relative_load_sessions', [])]
        athlete_stats.eligible_for_high_load_trigger = input_dict.get('eligible_for_high_load_trigger', False)
        athlete_stats.sport_max_load = {int(sport_name): SportMaxLoad.json_deserialise(sport_max_load) for (sport_name, sport_max_load) in input_dict.get('sport_max_load', {}).items()}
        athlete_stats.triggers = [Trigger.json_deserialise(trigger) for trigger in input_dict.get('triggers', [])]
        return athlete_stats

    @classmethod
    def _standard_error_from_monogodb(cls, std_error):
        standard_error_range = StandardErrorRange()
        if std_error is None or isinstance(std_error, numbers.Number):
            standard_error_range.observed_value = std_error
        elif isinstance(std_error, dict):
            standard_error_range.lower_bound = std_error.get("lower_bound", None)
            standard_error_range.observed_value = std_error.get("observed_value", None)
            standard_error_range.upper_bound = std_error.get("upper_bound", None)
            standard_error_range.insufficient_data = std_error.get("insufficient_data", False)
        return standard_error_range

    @classmethod
    def _expected_workouts_from_mongo(cls, mongo_result):
        typ_sessions_exp_workout = {"0-1": 0.5, "2-4": 3.0, "5+": 5.0, None: None}
        exp_workouts = mongo_result.get('expected_weekly_workouts', None)
        if exp_workouts is None:
            typical_weekly_sessions = mongo_result.get('typical_weekly_sessions', None)
            exp_workouts = typ_sessions_exp_workout[typical_weekly_sessions]
        return exp_workouts
