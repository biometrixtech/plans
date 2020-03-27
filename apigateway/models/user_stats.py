from serialisable import Serialisable
from models.load_stats import LoadStats
from models.session import HighLoadSession, HighDetailedLoadSession
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

    def __setattr__(self, name, value):
        if name == 'event_date' and value is not None:
            if isinstance(value, str):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'athlete_id': self.athlete_id,
            'event_date': format_datetime(self.event_date),
            'load_stats': self.load_stats.json_serialise() if self.load_stats is not None else None,
            'high_relative_load_sessions': [high_load.json_serialise() for high_load in self.high_relative_load_sessions],
            'eligible_for_high_load_trigger': self.eligible_for_high_load_trigger,
            'sport_max_load': {str(sport_name): sport_max_load.json_serialise() for (sport_name, sport_max_load) in self.sport_max_load.items()},
            'api_version': self.api_version,
            'timezone': self.timezone
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
