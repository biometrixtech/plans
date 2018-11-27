from enum import Enum
from serialisable import Serialisable
from models.metrics import MetricColor


class TeamDashboardData(Serialisable):

    def __init__(self, name):
        self.name = name
        self.compliance = []
        self.daily_insights_dict = {}
        self.daily_insights = []
        self.weekly_insights_dict = {}
        self.weekly_insights = []
        self.athletes = []


    def json_serialise(self):
        ret = {'name': self.name,
               'compliance': self.compliance,
               'daily_insights': [d.json_serialise() for d in self.daily_insights],
               'weekly_insights': [w.json_serialise() for w in self.weekly_insights],
               'athletes': [a.json_serialise() for a in self.athletes]
                }
        return ret

    def add_user_to_daily_report(self, user, metric):
        if metric.high_level_insight.value not in self.daily_insights_dict.keys():
            self.daily_insights_dict[metric.high_level_insight.value] = {}
        if user['user_id'] not in self.daily_insights_dict[metric.high_level_insight.value].keys():
            athlete = AthleteDashboardSummary(user['user_id'], user['first_name'], user['last_name'])
            athlete.color = metric.color
            athlete.cleared_to_train = False if metric.color.value == 2 else True
            self.daily_insights_dict[metric.high_level_insight.value][user['user_id']] = athlete
        else:
            athlete = self.daily_insights_dict[metric.high_level_insight.value][user['user_id']]
            athlete.color = MetricColor(max([athlete.color.value, metric.color.value]))
            athlete.cleared_to_train = False if athlete.color.value == 2 else True


    def add_user_to_weekly_report(self, user, metric):
        if user['user_id'] not in self.weekly_insights_dict[metric.high_level_insight.value].keys():
            athlete = AthleteDashboardSummary(user['user_id'], user['first_name'], user['last_name'])
            athlete.color = metric.color
            athlete.cleared_to_train = False if metric.color.value == 2 else True
            self.weekly_insights_dict[metric.high_level_insight.value][user['user_id']] = athlete
        else:
            athlete = self.weekly_insights_dict[metric.high_level_insight.value][user['user_id']]
            athlete.color = MetricColor(max([athlete.color.value, metric.color.value]))
            athlete.cleared_to_train = False if athlete.color.value == 2 else True


class AthleteDashboardSummary(Serialisable):
    def __init__(self, user_id, first_name, last_name):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.cleared_to_train = True
        self.color = 0

    def json_serialise(self):
        ret = {'user_id': self.user_id,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'cleared_to_train': self.cleared_to_train,
               'color': self.color.value
              }
        return ret


class AthleteDashboardData(Serialisable):

    def __init__(self, user_id, first_name, last_name):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.cleared_to_train = True
        self.color = MetricColor(0)
        self.daily_recommendation = []
        self.weekly_recommendation = []
        self.insights =[]


    def json_serialise(self):
        ret = {'user_id': self.user_id,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'cleared_to_train': self.cleared_to_train,
               'color': self.color.value,
               'daily_recommendation': self.daily_recommendation,
               'weekly_recommendation': self.weekly_recommendation,
               'insights': self.insights
              }
        return ret