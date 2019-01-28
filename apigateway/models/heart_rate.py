from serialisable import Serialisable
from utils import format_datetime, parse_datetime

class SessionHeartRate(Serialisable):
    
    def __init__(self, user_id, session_id, event_date):
        self.user_id = user_id
        self.session_id = session_id
        self.event_date = event_date
        self.hr_pre_workout = []
        self.hr_workout = []
        self.hr_post_workout = []

    def json_serialise(self):
        ret = {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'event_date': format_datetime(self.event_date),
            'hr_pre_workout': [hr.json_serialise() for hr in self.hr_pre_workout],
            'hr_workout': [hr.json_serialise() for hr in self.hr_workout],
            'hr_post_workout': [hr.json_serialise() for hr in self.hr_post_workout]
        }
        return ret

class HeartRateData(Serialisable):
    def __init__(self, hr_data):
        self.start_date = parse_datetime(hr_data['start_date'])
        self.end_date = parse_datetime(hr_data['end_date'])
        self.value = hr_data['value']

    def json_serialise(self):
        ret = {'start_date': format_datetime(self.start_date),
               'end_date': format_datetime(self.end_date),
               'value': self.value}
        return ret