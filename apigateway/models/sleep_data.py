from enum import Enum
from serialisable import Serialisable
from utils import format_datetime, parse_datetime, format_date

class DailySleepData(Serialisable):
    
    def __init__(self, user_id, event_date):
        self.user_id = user_id
        self.event_date = event_date
        self.sleep_events = []

    def json_serialise(self):
        ret = {
            'user_id': self.user_id,
            'event_date': format_date(self.event_date),
            'sleep_events': [sd.json_serialise() for sd in self.sleep_events]
        }
        return ret

class SleepEvent(Serialisable):
    def __init__(self, sleep_event):
        self.start_date = parse_datetime(sleep_event['start_date'])
        self.end_date = parse_datetime(sleep_event['end_date'])
        self.sleep_type = SleepType[sleep_event['value']]

    def json_serialise(self):
        ret = {'start_date': format_datetime(self.start_date),
               'end_date': format_datetime(self.end_date),
               'sleep_type': self.sleep_type.value}
        return ret

class SleepType(Enum):
    INBED = 0
    ASLEEP = 1
    UNKNOWN = 2
