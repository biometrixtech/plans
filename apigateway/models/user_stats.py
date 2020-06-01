from serialisable import Serialisable
from models.load_stats import LoadStats
from models.session import HighLoadSession, HighDetailedLoadSession
from models.stats import StandardErrorRange
from utils import format_date, parse_date, format_datetime, parse_datetime
from fathomapi.utils.exceptions import InvalidSchemaException


class UserStats(Serialisable):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id
        self.event_date = None
        self.api_version = '4_8'
        self.timezone = '-04:00'
        self.load_stats = LoadStats()
        self.sport_max_load = {}
        self.high_relative_load_sessions = []
        self.eligible_for_high_load_trigger = False

        self.expected_weekly_workouts = 3

        self.vo2_max = None
        self.functional_threshold_power = None

        self.average_newtons_5_day = None
        self.average_newtons_20_day = None
        self.average_watts_5_day = None
        self.average_watts_20_day = None
        self.average_work_vo2_5_day = None
        self.average_work_vo2_20_day = None
        self.average_rpe_5_day = None
        self.average_rpe_20_day = None

        self.average_newtons_load_5_day = None
        self.average_newtons_load_20_day = None
        self.average_watts_load_5_day = None
        self.average_watts_load_20_day = None
        self.average_work_vo2_load_5_day = None
        self.average_work_vo2_load_20_day = None
        self.average_rpe_load_5_day = None
        self.average_rpe_load_20_day = None

        self.average_trimp_5_day = None
        self.average_trimp_20_day = None

    def __setattr__(self, name, value):
        if name == 'event_date' and value is not None:
            if isinstance(value, str):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def newtons_load_5_20(self):

        if self.average_newtons_load_5_day is not None and self.average_newtons_load_20_day is not None:
            standard_error_range = StandardErrorRange()
            standard_error_range.lower_bound = self.average_newtons_load_5_day.lower_bound / self.average_newtons_load_20_day.lower_bound
            standard_error_range.upper_bound = self.average_newtons_load_5_day.upper_bound / self.average_newtons_load_20_day.upper_bound
            standard_error_range.observed_value = self.average_newtons_load_5_day.observed_value / self.average_newtons_load_20_day.observed_value
            standard_error_range.insufficient_data = min(self.average_newtons_load_5_day.insufficient_data, self.average_newtons_load_20_day.insufficient_data)

            return standard_error_range

        else:

            return None

    def rpe_load_5_20(self):

        if self.average_rpe_load_5_day is not None and self.average_rpe_load_20_day is not None:
            standard_error_range = StandardErrorRange()
            standard_error_range.lower_bound = self.average_rpe_load_5_day.lower_bound / self.average_rpe_load_20_day.lower_bound
            standard_error_range.upper_bound = self.average_rpe_load_5_day.upper_bound / self.average_rpe_load_20_day.upper_bound
            standard_error_range.observed_value = self.average_rpe_load_5_day.observed_value / self.average_rpe_load_20_day.observed_value
            standard_error_range.insufficient_data = min(self.average_rpe_load_5_day.insufficient_data,
                                                         self.average_rpe_load_20_day.insufficient_data)

            return standard_error_range

        else:

            return None

    def trimp_5_20(self):

        if self.average_trimp_5_day is not None and self.average_trimp_20_day is not None:
            standard_error_range = StandardErrorRange()
            standard_error_range.lower_bound = self.average_trimp_5_day.lower_bound / self.average_trimp_20_day.lower_bound
            standard_error_range.upper_bound = self.average_trimp_5_day.upper_bound / self.average_trimp_20_day.upper_bound
            standard_error_range.observed_value = self.average_trimp_5_day.observed_value / self.average_trimp_20_day.observed_value
            standard_error_range.insufficient_data = min(self.average_trimp_5_day.insufficient_data,
                                                         self.average_trimp_20_day.insufficient_data)

            return standard_error_range

        else:

            return None

    def watts_load_5_20(self):

        if self.average_watts_load_5_day is not None and self.average_watts_load_20_day is not None:
            standard_error_range = StandardErrorRange()
            standard_error_range.lower_bound = self.average_watts_load_5_day.lower_bound / self.average_watts_load_20_day.lower_bound
            standard_error_range.upper_bound = self.average_watts_load_5_day.upper_bound / self.average_watts_load_20_day.upper_bound
            standard_error_range.observed_value = self.average_watts_load_5_day.observed_value / self.average_watts_load_20_day.observed_value
            standard_error_range.insufficient_data = min(self.average_watts_load_5_day.insufficient_data,
                                                         self.average_watts_load_20_day.insufficient_data)

            return standard_error_range

        else:

            return None

    def work_vo2_load_5_20(self):

        if self.average_work_vo2_5_day is not None and self.average_work_vo2_load_20_day is not None:
            standard_error_range = StandardErrorRange()
            standard_error_range.lower_bound = self.average_work_vo2_5_day.lower_bound / self.average_work_vo2_load_20_day.lower_bound
            standard_error_range.upper_bound = self.average_work_vo2_5_day.upper_bound / self.average_work_vo2_load_20_day.upper_bound
            standard_error_range.observed_value = self.average_work_vo2_5_day.observed_value / self.average_work_vo2_load_20_day.observed_value
            standard_error_range.insufficient_data = min(self.average_work_vo2_5_day.insufficient_data,
                                                         self.average_work_vo2_load_20_day.insufficient_data)

            return standard_error_range

        else:

            return None

    def json_serialise(self):
        ret = {
            'athlete_id': self.athlete_id,
            'event_date': format_datetime(self.event_date),
            'load_stats': self.load_stats.json_serialise() if self.load_stats is not None else None,
            'high_relative_load_sessions': [high_load.json_serialise() for high_load in self.high_relative_load_sessions],
            'eligible_for_high_load_trigger': self.eligible_for_high_load_trigger,
            'sport_max_load': {str(sport_name): sport_max_load.json_serialise() for (sport_name, sport_max_load) in self.sport_max_load.items()},
            'api_version': self.api_version,
            'timezone': self.timezone,
            'vo2_max': self.vo2_max,
            'functional_threshold_power': self.functional_threshold_power,
            'average_newtons_5_day': self.average_newtons_5_day.json_serialise() if self.average_newtons_5_day is not None else None,
            'average_newtons_20_day': self.average_newtons_20_day.json_serialise() if self.average_newtons_20_day is not None else None,
            'average_watts_5_day': self.average_watts_5_day.json_serialise() if self.average_watts_5_day is not None else None,
            'average_watts_20_day': self.average_watts_20_day.json_serialise() if self.average_watts_20_day is not None else None,
            'average_work_vo2_5_day': self.average_work_vo2_5_day.json_serialise() if self.average_work_vo2_5_day is not None else None,
            'average_work_vo2_20_day': self.average_work_vo2_20_day.json_serialise() if self.average_work_vo2_20_day is not None else None,
            'average_rpe_5_day': self.average_rpe_5_day.json_serialise() if self.average_rpe_5_day is not None else None,
            'average_rpe_20_day': self.average_rpe_20_day.json_serialise() if self.average_rpe_20_day is not None else None,
            'average_newtons_load_5_day': self.average_newtons_load_5_day.json_serialise() if self.average_newtons_load_5_day is not None else None,
            'average_newtons_load_20_day': self.average_newtons_load_20_day.json_serialise() if self.average_newtons_load_20_day is not None else None,
            'average_watts_load_5_day': self.average_watts_load_5_day.json_serialise() if self.average_watts_load_5_day is not None else None,
            'average_watts_load_20_day': self.average_watts_load_20_day.json_serialise() if self.average_watts_load_20_day is not None else None,
            'average_work_vo2_load_5_day': self.average_work_vo2_load_5_day.json_serialise() if self.average_work_vo2_load_5_day is not None else None,
            'average_work_vo2_load_20_day': self.average_work_vo2_load_20_day.json_serialise() if self.average_work_vo2_load_20_day is not None else None,
            'average_rpe_load_5_day': self.average_rpe_load_5_day.json_serialise() if self.average_rpe_load_5_day is not None else None,
            'average_rpe_load_20_day': self.average_rpe_load_20_day.json_serialise() if self.average_rpe_load_20_day is not None else None,
            'average_trimp_5_day': self.average_trimp_5_day.json_serialise() if self.average_trimp_5_day is not None else None,
            'average_trimp_20_day': self.average_trimp_20_day.json_serialise() if self.average_trimp_20_day is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        user_stats = cls(athlete_id=input_dict['athlete_id'])
        user_stats.event_date = input_dict.get('event_date')
        user_stats.api_version = input_dict.get('api_version', '4_8')
        user_stats.timezone = input_dict.get('timezone', '-04:00')
        user_stats.load_stats = LoadStats.json_deserialise(input_dict.get('load_stats', None))
        user_stats.high_relative_load_sessions = [HighLoadSession.json_deserialise(session) if 'sport_name' in session else HighDetailedLoadSession.json_deserialise(session) for session in input_dict.get('high_relative_load_sessions', [])]
        user_stats.eligible_for_high_load_trigger = input_dict.get('eligible_for_high_load_trigger', False)
        user_stats.sport_max_load = {int(sport_name): SportMaxLoad.json_deserialise(sport_max_load) for (sport_name, sport_max_load) in input_dict.get('sport_max_load', {}).items()}
        user_stats.vo2_max = input_dict.get('vo2_max')
        user_stats.functional_threshold_power = input_dict.get('functional_threshold_power')
        user_stats.average_newtons_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_newtons_5_day') is not None else None
        user_stats.average_newtons_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_newtons_20_day') is not None else None
        user_stats.average_watts_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_watts_5_day') is not None else None
        user_stats.average_watts_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_watts_20_day') is not None else None
        user_stats.average_work_vo2_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_work_vo2_5_day') is not None else None
        user_stats.average_work_vo2_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_work_vo2_20_day') is not None else None
        user_stats.average_rpe_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_rpe_5_day') is not None else None
        user_stats.average_rpe_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_rpe_20_day') is not None else None
        user_stats.average_newtons_load_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_newtons_load_5_day') is not None else None
        user_stats.average_newtons_load_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_newtons_load_20_day') is not None else None
        user_stats.average_watts_load_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_watts_load_5_day') is not None else None
        user_stats.average_watts_load_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_watts_load_20_day') is not None else None
        user_stats.average_work_vo2_load_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_work_vo2_load_5_day') is not None else None
        user_stats.average_work_vo2_load_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_work_vo2_load_20_day') is not None else None
        user_stats.average_rpe_load_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_rpe_load_5_day') is not None else None
        user_stats.average_rpe_load_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_rpe_load_20_day') is not None else None
        user_stats.average_trimp_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_trimp_5_day') is not None else None
        user_stats.average_trimp_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_trimp_20_day') is not None else None

        return user_stats


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
