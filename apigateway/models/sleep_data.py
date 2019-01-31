from enum import Enum
import datetime
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
        self.sleep_type = sleep_event['sleep_type']
        self.event_date = self.get_event_date()

    def json_serialise(self):
        ret = {'start_date': format_datetime(self.start_date),
               'end_date': format_datetime(self.end_date),
               'sleep_type': self.sleep_type.value}
        return ret
    def get_event_date(self):
        if self.start_date.hour < 17:
            event_date = format_datetime(self.start_date).split("T")[0]
        else:
            event_date = format_datetime(self.start_date + datetime.timedelta(days=1)).split("T")[0]
        return event_date

    def __setattr__(self, name, value):
        if name == "sleep_type":
            if isinstance(value, str):
                value = SleepType[value]
            elif isinstance(value, int):
                value = SleepType(value)
        super().__setattr__(name, value)

class SleepType(Enum):
    INBED = 0
    ASLEEP = 1
    UNKNOWN = 2
