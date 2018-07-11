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

    def get_sports(self):
        sports = []
        for sport in self.sports:
            sport = {'name': sport['name'],
                     'competition_level': sport['competition_level'],
                     'positions': sport['positions'],
                     'start_date': sport['start_date'],
                     'end_date': sport['end_date']
                     }
            sports.append(sport)
        return sports
