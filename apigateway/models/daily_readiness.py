from serialisable import Serialisable
import datetime

from utils import parse_datetime, format_datetime
from logic.soreness_and_injury import DailySoreness, BodyPart, BodyPartLocation

class DailyReadiness(Serialisable):
    
    def __init__(self,
                 event_date,
                 user_id,
                 soreness,
                 sleep_quality,
                 readiness
                 ):
        self.event_date = parse_datetime(event_date)
        self.user_id = user_id
        self.soreness = [self._soreness_from_dict(s) for s in soreness]
        self.sleep_quality = int(sleep_quality)
        self.readiness = int(readiness)

    def get_id(self):
        return self.user_id

    def get_event_date(self):
        return parse_datetime(self.event_date)

    def json_serialise(self):
        ret = {
            'event_date': format_datetime(self.event_date),
            'user_id': self.user_id,
            'soreness': [s.json_serialise() for s in self.soreness],
            'sleep_quality': self.sleep_quality,
            'readiness': self.readiness,
            'sore_body_parts': [{"body_part": s.body_part.location.value, "side": s.side} for s in self.soreness if s.severity > 1]
        }
        return ret

    def _soreness_from_dict(self, soreness_dict):
        soreness = DailySoreness()
        soreness.body_part = BodyPart(BodyPartLocation(soreness_dict['body_part']), None)
        soreness.severity = soreness_dict['severity']
        soreness.side = soreness_dict['side']
        soreness.reported_date_time = self.event_date
        return soreness
