from serialisable import Serialisable
from models.metrics import MetricColor


class TeamDashboardData(Serialisable):

    def __init__(self, name):
        self.name = name
        self.compliance = {}
        self.daily_insights_dict = {}
        self.daily_insights = DailySummary()
        self.weekly_insights_dict = {}
        self.weekly_insights = WeeklySummary()
        self.athletes = []


    def json_serialise(self):
        ret = {'name': self.name,
               'compliance': self.compliance,
               'daily_insights': self.daily_insights.json_serialise(),
               'weekly_insights': self.weekly_insights.json_serialise(),
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


class DailySummary(Serialisable):
    def __init__(self):
        self.all_good = []
        self.increase_workload = []
        self.limit_time_intensity_of_training = []
        self.monitor_in_training = []
        self.not_cleared_for_training = []


    def json_serialise(self):
        ret = {'all_good': [a.json_serialise() for a in self.all_good],
               'increase_workload': [a.json_serialise() for a in self.increase_workload],
               'limit_time_intensity_of_training': [a.json_serialise() for a in self.limit_time_intensity_of_training],
               'monitor_in_training': [a.json_serialise() for a in self.monitor_in_training],
               'not_cleared_for_training': [a.json_serialise() for a in self.not_cleared_for_training]
                }
        return ret

class WeeklySummary(Serialisable):
    def __init__(self):
        self.all_good = []
        self.balance_overtraining_risk = []
        self.add_variety_to_training_risk = []
        self.increase_weekly_workload = []
        self.address_pain_or_soreness = []
        self.evaluate_health_status = []

    def json_serialise(self):
        ret = {'all_good': [a.json_serialise() for a in self.all_good],
               'balance_overtraining_risk': [a.json_serialise() for a in self.balance_overtraining_risk],
               'add_variety_to_training_risk': [a.json_serialise() for a in self.add_variety_to_training_risk],
               'increase_weekly_workload': [a.json_serialise() for a in self.increase_weekly_workload],
               'address_pain_or_soreness': [a.json_serialise() for a in self.address_pain_or_soreness],
               'evaluate_health_status': [a.json_serialise() for a in self.evaluate_health_status]
                }
        return ret

class AthleteDashboardSummary(Serialisable):
    def __init__(self, user_id, first_name, last_name):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.cleared_to_train = True
        self.color = MetricColor(0)

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