from serialisable import Serialisable
from utils import parse_datetime


class DailyPlan(Serialisable):
    
    def __init__(self,
                 event_date,
                 user_id,
                 practice=None,
                 recovery_am=None,
                 recovery_pm=None
                 ):
        self.event_date = event_date
        self.user_id = user_id
        self.practice = practice
        self.recovery_am = recovery_am
        self.recovery_mp = recovery_pm

    def get_id(self):
        return self.user_id

    def get_event_datetime(self):
        return parse_datetime(self.event_date)

    def json_serialise(self):
        ret = {
        }
        return ret



