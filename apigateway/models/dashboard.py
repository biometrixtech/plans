from enum import Enum
from serialisable import Serialisable


class TeamDashboardData(Serialisable):

    def __init__(self, name):
        self.name = name
        self.compliance = []
        self.daily_insights = []
        self.weekly_insights = []
        self.athletes = []


    def json_serialise(self):
        ret = {'name': self.name,
               'compliance': self.compliance,
               'daily_insights': self.daily_insights,
               'weekly_insights': self.weekly_insights,
               'athletes': [a.json_serialise() for a in self.athletes]
                }
        return ret

    def add_user_to_daily_report(self, user, metric):
        pass

    def add_user_to_weekly_report(self, user, metric):
        pass

class AthleteDashboardData(Serialisable):

    def __init__(self, id, first_name, last_name):
        self.user_id = id
        self.first_name = ""
        self.last_name = ""
        self.cleared_to_train = True
        self.color = 0
        self.daily_recommendation = []
        self.weekly_recommendation = []
        self.insights =[]


    def json_serialise(self):
        ret = {'id': self.name,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'cleared_to_train': self.cleared_to_train,
               'color': self.color.value,
               'daily_recommendation': self.daily_recommendation,
               'weekly_recommendation': self.weekly_recommendation,
               'insights': self.insights
              }
        return ret