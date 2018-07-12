from serialisable import Serialisable
import datetime

from utils import parse_datetime


class DailyReadiness(Serialisable):
    
    def __init__(self,
                 event_date,
                 user_id,
                 soreness,
                 sleep_quality,
                 readiness
                 ):
        self.event_date = event_date
        self.user_id = user_id
        self.soreness = soreness
        self.sleep_quality = int(sleep_quality)
        self.readiness = int(readiness)

    def get_id(self):
        return self.user_id

    def get_event_date(self):
        return parse_datetime(self.event_date)

    def json_serialise(self):
        ret = {
            'event_date': self.event_date,
            'user_id': self.user_id,
            'soreness': self.soreness,
            'sleep_quality': self.sleep_quality,
            'readiness': self.readiness,
            'sore_body_parts': [s.body_part.location.value for s in self.soreness if s.severity > 1]
        }
        return ret
