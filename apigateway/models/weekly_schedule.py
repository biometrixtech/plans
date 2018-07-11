from serialisable import Serialisable


class WeeklySchedule(Serialisable):
    
    def __init__(self,
                 user_id,
                 week_start,
                 cross_training=None,
                 sports=[]
                 ):
        self.user_id = user_id
        self.week_start = week_start
        self.cross_training = cross_training
        self.sports = sports

    def get_id(self):
        return self.user_id

    def get_start_date(self):
        return self.week_start

    def json_serialise(self):
        ret = {
            'user_id': self.user_id,
            'week_start': self.week_start,
            'cross_training': self.cross_training,
            'sports': self.sports,
        }
        return ret
