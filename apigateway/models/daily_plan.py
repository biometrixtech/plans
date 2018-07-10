from serialisable import Serialisable


class DailyPlan(Serialisable):
    
    def __init__(self,
                 date,
                 user_id,
                 practice=None,
                 recovery_am=None,
                 recovery_pm=None
                 ):
        self.date = date
        self.use_id = user_id
        self.practice = practice
        self.recovery_am = recovery_am
        self.recovery_mp = recovery_pm

    def get_id(self):
        return self.user_id

    def get_date(self):
        return self.date_time

    def json_serialise(self):
        ret = {
        }
        return ret



