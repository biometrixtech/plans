from serialisable import Serialisable

class AthleteSeason(Serialisable):
    def __init__(self,
                 user_id,
                 seasons
                 ):
        self.user_id = user_id
        self.seasons = seasons

    def get_id(self):
        return self.user_id

    def get_start_date(self):
        return self.week_start

    def json_serialise(self):
        ret = {"user_id": self.user_id,
               "seasons": self.seasons}
        return ret

class Season(Serialisable):
    def __init__(self,
                 sport,
                 competition_level,
                 positions,
                 start_date,
                 end_date):
        self.sport = sport
        self.competition_level = competition_level
        self.positions = positions
        self.start_date = start_date
        self.end_date = end_date

    def json_serialise(self):
        ret = {
                "sport": self.sport,
                "competition_level" : self.competition_level,
                "positions" : self.positions,
                "start_date" : self.start_date,
                "end_date" : self.end_date
               }
        return ret

    def is_similar(self, season):
        return self.sport == season.sport and \
               self.competition_level==season.competition_level and \
               self.start_date == season.start_date
