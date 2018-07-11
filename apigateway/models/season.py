from serialisable import Serialisable

class AthleteSeason(Serialisable):
    def __init__(self,
                 user_id,
                 sports
                 ):
        self.user_id = user_id
        self.sports = sports

    def get_id(self):
        return self.user_id

    def get_start_date(self):
        return self.week_start

    def json_serialise(self):
        ret = {"user_id": self.user_id,
               "sports": self.sports}
        return ret

class Sport(Serialisable):
    def __init__(self,
                 name,
                 competition_level,
                 positions,
                 start_date,
                 end_date):
        self.name = name
        self.competition_level = competition_level
        self.positions = positions
        self.start_date = start_date
        self.end_date = end_date

    def json_serialise(self):
        ret = {
                "name": self.name,
                "competition_level" : self.competition_level,
                "positions" : self.positions,
                "start_date" : self.start_date,
                "end_date" : self.end_date
               }
        return ret
