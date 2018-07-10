from serialisable import Serialisable


class DailyPlan(Serialisable):
    
    def __init__(self,
                 date,
                 user_id,
                 soreness,
                 sleep_quality,
                 readiness
                 ):
        self.date_time = date
        self.date = user_id
        self.practice = practice
        self.recoveryAM = recoveryAM
        self.recoveryPM = recoveryPM

    def get_id(self):
        return self.user_id

    def get_date(self):
        return self.date_time

    def json_serialise(self):
        ret = {
        }
        return ret



