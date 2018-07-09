from serialisable import Serialisable


class WeeklyCrossTrainingSchedule(Serialisable):
    
    def __init__(self,
                 user_id,
                 week_start,
                 days_of_week,
                 activities,
                 duration
                 ):
        self.user_id = user_id
        self.week_start = week_start
        self.days_of_week = days_of_week
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
            'days_of_week': self.days_of_week,
            'activities': self.activities,
            'duration': self.duration,
        }
        return ret


class WeeklyTrainingSchedule(Serialisable):
    
    def __init__(self,
                 user_id,
                 week_start,
                 sports,
                 # practice,
                 # competition
                 ):
        self.user_id = user_id
        self.week_start = week_start
        self.sports = sports
        # self.practice = practice
        # self.competition = competition

    def get_id(self):
        return self.user_id

    def get_start_date(self):
        return self.week_start

    def json_serialise(self):
        ret = {
            'user_id': self.user_id,
            'week_start': self.week_start,
            'sports': self.sports,
            # 'practice': self.practice,
            # 'competition': self.competition
        }
        return ret

