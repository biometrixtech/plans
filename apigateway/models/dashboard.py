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

    def get_compliance_data(self, user_ids, users, daily_plan_list):
        users_with_plan = [plan.user_id for plan in daily_plan_list]
        self.compliance['complete'] = []
        self.compliance['incomplete'] = [users[user_id] for user_id in user_ids if user_id not in users_with_plan]
        training_compliance = TrainingCompliance()
        training_compliance.no_response = []
        training_compliance.no_response.extend(self.compliance['incomplete'])
        for plan in daily_plan_list:
            if plan.daily_readiness_survey_completed():
                self.compliance['complete'].append(users[plan.user_id])
                if not plan.sessions_planned:
                    training_compliance.rest_day.append(users[plan.user_id])
                else:
                    if len(plan.training_sessions) == 0:
                        training_compliance.no_response.append(users[plan.user_id])
                    else:
                        training_compliance.sessions_logged.append(users[plan.user_id])
            else:
                self.compliance['incomplete'].append(users[plan.user_id])
                training_compliance.no_response.append(users[plan.user_id])
        self.compliance['training_compliance'] = training_compliance.json_serialise()

    def insert_user(self, athlete):
        athlete_summary = AthleteDashboardSummary(athlete.user_id, athlete.first_name, athlete.last_name)
        athlete_summary.cleared_to_train = athlete.cleared_to_train
        athlete_summary.color = athlete.color
        athlete_summary.insufficient_data = athlete.insufficient_data
        # if not cleared to train, add to not_cleared to train for daily and check if belong to weekly red insight
        if not athlete_summary.cleared_to_train:
            self.daily_insights.not_cleared_for_training.append(athlete_summary)
            if WeeklyHighLevelInsight.needs_lower_training_intensity in athlete.weekly_insights:
                self.weekly_insights.evaluate_health_status.append(athlete_summary)
        else:
            # group athletes into daily_insight bins
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
                elif insight == WeeklyHighLevelInsight.signs_of_elevated_injury_risk:
                    self.weekly_insights.address_pain_or_soreness.append(athlete_summary)


class TrainingCompliance(Serialisable):
    def __init__(self):
        self.no_response = []
        self.rest_day = []
        self.sessions_logged = []

    def json_serialise(self):
        ret = {"no_response": self.no_response,
               "rest_day": self.rest_day,
               "sessions_logged": self.sessions_logged
              }
        return ret

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
               'seek_med_staff_evaluation': [a.json_serialise() for a in self.not_cleared_for_training]
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
               'signs_of_elevated_injury_risk': [a.json_serialise() for a in self.address_pain_or_soreness],
               'needs_lower_training_intensity': [a.json_serialise() for a in self.evaluate_health_status]
              }
        return ret

class AthleteDashboardSummary(Serialisable):
    def __init__(self, user_id, first_name, last_name):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.cleared_to_train = True
        self.color = MetricColor(0)
        self.insufficient_data = False

    def json_serialise(self):
        ret = {'user_id': self.user_id,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'cleared_to_train': self.cleared_to_train,
               'color': self.color.value,
               'insufficient_data': self.insufficient_data
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
        self.insufficient_data = False

    def aggregate(self, metrics):
        if len(metrics) == 0:
            self.daily_recommendation = set(['Training as normal and completing Fathom’s Mobility and Recovery exercises'])
            self.insights =["No signs of overtraining or injury risk"]
        else:
            not_cleared_recs_day = []
            not_cleared_recs_week = []
            insufficient_data_red = False
            for metric in metrics:
                self.color = MetricColor(max([self.color.value, metric.color.value]))
                self.cleared_to_train = False if self.color.value == 2 else True
                self.add_insight(metric)
                daily_recs = [(m.text, metric.insufficient_data) for m in metric.specific_actions if m.display and m.code[0] in ["2", "5", "6", "7"]]
                weekly_recs = [(m.text, metric.insufficient_data) for m in metric.specific_actions if m.display and m.code[0] in ["1", "3"]]
                if metric.color == MetricColor.red: # not cleared to train
                    not_cleared_recs_day.extend(daily_recs)
                    not_cleared_recs_week.extend(weekly_recs)
                    if metric.insufficient_data:
                        insufficient_data_red = True
                elif metric.color != MetricColor.red and self.cleared_to_train:
                    self.daily_recommendation.update(daily_recs)
                    self.weekly_recommendation.update(weekly_recs)
                else: # not cleared to train but current metric is yellow
                    pass

                if metric.metric_type == MetricType.daily:
                    self.daily_insights.add(metric.high_level_insight)
                elif metric.metric_type == MetricType.longitudinal and metric.color != MetricColor.green:
                    self.weekly_insights.add(metric.high_level_insight)
            # if not cleared to train, removed recs from other insights
            if not self.cleared_to_train:
                self.daily_recommendation = set(not_cleared_recs_day)
                self.weekly_recommendation = set(not_cleared_recs_week)
                self.insufficient_data = insufficient_data_red
            elif self.color == MetricColor.yellow and len(self.daily_insights) == 0:
                self.daily_insights.add(DailyHighLevelInsight.monitor_in_training)

            sorted_insights = sorted(self.insights,  key=lambda k: k[1], reverse=True)
            self.insights = [i[0] for i in sorted_insights]
            self.daily_recommendation = self.cleanup_recs('daily')
            self.weekly_recommendation = self.cleanup_recs('weekly')

    def add_insight(self, metric):
        if metric.specific_insight_training_volume != "":
            if metric.insufficient_data:
                self.insufficient_data = True
                self.insights.append(("*"+metric.specific_insight_training_volume, metric.color))
            else:
                self.insights.append((metric.specific_insight_training_volume, metric.color))
        if metric.specific_insight_recovery != "":
            self.insights.append((metric.specific_insight_recovery, metric.color))


    def cleanup_recs(self, rec_type='daily'):
        if rec_type == 'daily':
            all_recs = self.daily_recommendation
        elif rec_type == 'weekly':
            all_recs = self.weekly_recommendation
        recs = {}
        for rec in all_recs:
            if rec[0] not in recs:
                recs[rec[0]] = rec[1]
            else:
                if not rec[1]:
                    recs[rec[0]] = rec[1]
        cleaned_recs = set()
        for rec in recs:
            if recs[rec]:
                cleaned_recs.add("*" + rec)
            else:
                cleaned_recs.add(rec)
        return cleaned_recs



    def json_serialise(self):
        ret = {'user_id': self.user_id,
               'first_name': self.first_name,
               'last_name': self.last_name,
               'cleared_to_train': self.cleared_to_train,
               'color': self.color.value,
               'daily_recommendation': list(self.daily_recommendation),
               'weekly_recommendation': list(self.weekly_recommendation),
               'insights': self.insights,
               'insufficient_data': self.insufficient_data
              }
        return ret