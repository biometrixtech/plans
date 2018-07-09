 from serialisable import Serialisable


class WeeklySchedule(Serialisable):
    
    def __init__(self,
                 user_id,
                 date,
                 activity,
                 duration=None,
                 sport=None
                 ):
        self.user_id = user_id
        self.date = date
        self.activity = activity
        self.duration = duration
        self.sport = sport

    def get_id(self):
        return self.user_id

    def get_date(self):
        return self.date

    def json_serialise(self):
        ret = {
            'user_id': self.user_id,
            'date': self.date,
            'activity': self.activity,
            'duration': self.duration,
            'sport': self.sport
        }
        return ret


class WeeklyCrossTrainingSchedule(Serialisable):
    
    def __init__(self,
                 user_id,
                 week_start,
                 dates,
                 activities
                 ):
        self.user_id = user_id
        self.week_start = week_start
        self.dates = dates
        self.activities = activities
        self.duration = duration

    def get_id(self):
        return self.user_id

    def get_start_date(self):
        return self.week_start

    def json_serialise(self):
        ret = {
            'user_id': self.user_id,
            'week_start': self.week_start,
            'dates': self.date,
            'activities': self.activity,
            'duration': self.duration,
        }
        return ret

