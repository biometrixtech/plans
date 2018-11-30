from serialisable import Serialisable
from models.metrics import MetricColor, WeeklyHighLevelInsight, DailyHighLevelInsight, MetricType


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

    # def add_user_to_daily_report(self, user, metric):
    #     if metric.high_level_insight.value not in self.daily_insights_dict.keys():
    #         self.daily_insights_dict[metric.high_level_insight.value] = {}
    #     if user['user_id'] not in self.daily_insights_dict[metric.high_level_insight.value].keys():
    #         athlete = AthleteDashboardSummary(user['user_id'], user['first_name'], user['last_name'])
    #         athlete.color = metric.color
    #         athlete.cleared_to_train = False if metric.color.value == 2 else True
    #         self.daily_insights_dict[metric.high_level_insight.value][user['user_id']] = athlete
    #     else:
    #         athlete = self.daily_insights_dict[metric.high_level_insight.value][user['user_id']]
    #         athlete.color = MetricColor(max([athlete.color.value, metric.color.value]))
    #         athlete.cleared_to_train = False if athlete.color.value == 2 else True


    # def add_user_to_weekly_report(self, user, metric):
    #     if user['user_id'] not in self.weekly_insights_dict[metric.high_level_insight.value].keys():
    #         athlete = AthleteDashboardSummary(user['user_id'], user['first_name'], user['last_name'])
    #         athlete.color = metric.color
    #         athlete.cleared_to_train = False if metric.color.value == 2 else True
    #         self.weekly_insights_dict[metric.high_level_insight.value][user['user_id']] = athlete
    #     else:
    #         athlete = self.weekly_insights_dict[metric.high_level_insight.value][user['user_id']]
    #         athlete.color = MetricColor(max([athlete.color.value, metric.color.value]))
    #         athlete.cleared_to_train = False if athlete.color.value == 2 else True

    def get_compliance_data(self, user_ids, users, readiness_survey_list):
        completed_users = [survey.user_id for survey in readiness_survey_list]
        self.compliance['completed'] = [users[user_id] for user_id in user_ids if user_id in completed_users]
        self.compliance['incomplete'] = [users[user_id] for user_id in user_ids if user_id not in completed_users]


    def insert_user(self, athlete):
        athlete_summary = AthleteDashboardSummary(athlete.user_id, athlete.first_name, athlete.last_name)
        athlete_summary.cleared_to_train = athlete.cleared_to_train
        athlete_summary.color = athlete.color
        # if not cleared to train, add to not_cleared to train for daily and check if belong to weekly red insight
        if not athlete_summary.cleared_to_train:
            self.daily_insights.not_cleared_for_training.append(athlete_summary)
            if WeeklyHighLevelInsight.evaluate_health_status in athlete.weekly_insights:
                self.weekly_insights.evaluate_health_status.append(athlete_summary)
        else:
            # grpup athletes into daily_insight bins
            if len(athlete.daily_insights) == 0:
                self.daily_insights.all_good.append(athlete_summary)
            else:
                for insight in athlete.daily_insights:
                    if insight == DailyHighLevelInsight.increase_workload:
                        self.daily_insights.increase_workload.append(athlete_summary)
                    elif insight == DailyHighLevelInsight.limit_time_intensity_of_training:
                        self.daily_insights.limit_time_intensity_of_training.append(athlete_summary)
                    elif insight == DailyHighLevelInsight.monitor_in_training:
                        self.daily_insights.monitor_in_training.append(athlete_summary)
            # group athletes in weekly_insight bins
            for insight in athlete.weekly_insights:
                if insight == WeeklyHighLevelInsight.balance_overtraining_risk:
                    self.weekly_insights.balance_overtraining_risk.append(athlete_summary)
                elif insight == WeeklyHighLevelInsight.add_variety_to_training_risk:
                    self.weekly_insights.add_variety_to_training_risk.append(athlete_summary)
                elif insight == WeeklyHighLevelInsight.increase_weekly_workload:
                    self.weekly_insights.increase_weekly_workload.append(athlete_summary)
                elif insight == WeeklyHighLevelInsight.address_pain_or_soreness:
                    self.weekly_insights.address_pain_or_soreness.append(athlete_summary)


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
        self.daily_recommendation = set()
        self.weekly_recommendation = set()
        self.insights =[]
        self.daily_insights = set()
        self.weekly_insights = set()

    def aggregate(self, metrics):
        if len(metrics) == 0:
            self.daily_recommendation = set(['Training as normal and complete Fathom’s Prep and Recovery'])
            self.insights =["No signs of overtraining or injury risk"]
        else:
            not_cleared_recs_day = []
            not_cleared_recs_week = []
            for metric in metrics:
                if metric.specific_insight_training_volume != "":
                    self.insights.append(metric.specific_insight_training_volume)
                if metric.specific_insight_recovery != "":
                    self.insights.append(metric.specific_insight_recovery)
                self.color = MetricColor(max([self.color.value, metric.color.value]))
                self.cleared_to_train = False if self.color.value == 2 else True

                if metric.metric_type == MetricType.daily:
                    self.daily_insights.add(metric.high_level_insight)
                    self.daily_recommendation.update([m.text for m in metric.specific_actions if m.display])
                    if metric.color == MetricColor.red:
                        not_cleared_recs_day.extend([m.text for m in metric.specific_actions if m.display])
                elif metric.metric_type == MetricType.longitudinal and metric.color != MetricColor.green:
                    self.weekly_insights.add(metric.high_level_insight)
                    self.weekly_recommendation.update([m.text for m in metric.specific_actions if m.display])
                    if metric.color == MetricColor.red:
                        not_cleared_recs_week.extend([m.text for m in metric.specific_actions if m.display])
            # if not cleared to train, removed recs from other insights
            if not self.cleared_to_train:
                self.daily_recommendation = set(not_cleared_recs_day)
                self.weekly_recommendation = set(not_cleared_recs_week)

    def json_serialise(self):
        ret = {'user_id': self.user_id,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'cleared_to_train': self.cleared_to_train,
               'color': self.color.value,
               'daily_recommendation': list(self.daily_recommendation),
               'weekly_recommendation': list(self.weekly_recommendation),
               'insights': self.insights
              }
        return ret