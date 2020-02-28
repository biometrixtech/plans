from serialisable import Serialisable
from models.load_stats import LoadStats
from models.session import HighLoadSession
from utils import format_date, parse_date


class UserStats(Serialisable):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id
        self.event_date = None
        self.api_version = '4_8'
        self.timezone = '-04:00'
        self.load_stats = LoadStats()
        self.high_relative_load_sessions = []
        self.eligible_for_high_load_trigger = False

    def __setattr__(self, name, value):
        if name == 'event_date' and value is not None:
            if isinstance(value, str):
                value = parse_date(value)
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'athlete_id': self.athlete_id,
            'event_date': format_date(self.event_date),
            'load_stats': self.load_stats.json_serialise() if self.load_stats is not None else None,
            'high_relative_load_sessions': [high_load.json_serialise() for high_load in self.high_relative_load_sessions],
            'eligible_for_high_load_trigger': self.eligible_for_high_load_trigger,
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
        user_stats.high_relative_load_sessions = [HighLoadSession.json_deserialise(session) for session in input_dict.get('high_relative_load_sessions', [])]
        user_stats.eligible_for_high_load_trigger = input_dict.get('eligible_for_high_load_trigger', False)
        return user_stats
