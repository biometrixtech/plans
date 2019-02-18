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
                    if insight == DailyHighLevelInsight.recovery_day_recommended:
                        self.daily_insights.increase_workload.append(athlete_summary)
                    elif insight == DailyHighLevelInsight.adapt_training_to_avoid_symptoms:
                        self.daily_insights.limit_time_intensity_of_training.append(athlete_summary)
                    elif insight == DailyHighLevelInsight.monitor_modify_if_needed:
                        self.daily_insights.monitor_in_training.append(athlete_summary)
            # group athletes in weekly_insight bins
            for insight in athlete.weekly_insights:
                if insight == WeeklyHighLevelInsight.at_risk_of_overtraining:
                    self.weekly_insights.balance_overtraining_risk.append(athlete_summary)
                elif insight == WeeklyHighLevelInsight.low_variability_inhibiting_recovery:
                    self.weekly_insights.add_variety_to_training_risk.append(athlete_summary)
                elif insight == WeeklyHighLevelInsight.at_risk_of_undertraining:
                    self.weekly_insights.increase_weekly_workload.append(athlete_summary)
                elif insight == WeeklyHighLevelInsight.at_risk_of_time_loss_injury:
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
               'recovery_day_recommended': [a.json_serialise() for a in self.increase_workload],
               'adapt_training_to_avoid_symptoms': [a.json_serialise() for a in self.limit_time_intensity_of_training],
               'monitor_modify_if_needed': [a.json_serialise() for a in self.monitor_in_training],
               'seek_med_eval_to_clear_for_training': [a.json_serialise() for a in self.not_cleared_for_training]
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
               'at_risk_of_overtraining': [a.json_serialise() for a in self.balance_overtraining_risk],
               'low_variability_inhibiting_recovery': [a.json_serialise() for a in self.add_variety_to_training_risk],
               'at_risk_of_undertraining': [a.json_serialise() for a in self.increase_weekly_workload],
               'at_risk_of_time_loss_injury': [a.json_serialise() for a in self.address_pain_or_soreness],
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
            self.daily_recommendation = set(['Training as normal and completing Fathom’s Mobility and Recovery exercises'])
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

                daily_recs = [m.text for m in metric.specific_actions if m.display and m.code[0] in ["2", "5", "6", "7"]]
                weekly_recs = [m.text for m in metric.specific_actions if m.display and m.code[0] in ["1", "3"]]
                
                self.daily_recommendation.update(daily_recs)
                self.weekly_recommendation.update(weekly_recs)
                if metric.color == MetricColor.red:
                    not_cleared_recs_day.extend(daily_recs)
                    not_cleared_recs_week.extend(weekly_recs)

                if metric.metric_type == MetricType.daily:
                    self.daily_insights.add(metric.high_level_insight)
                elif metric.metric_type == MetricType.longitudinal and metric.color != MetricColor.green:
                    self.weekly_insights.add(metric.high_level_insight)
            # if not cleared to train, removed recs from other insights
            if not self.cleared_to_train:
                self.daily_recommendation = set(not_cleared_recs_day)
                self.weekly_recommendation = set(not_cleared_recs_week)
            elif self.color == MetricColor.yellow and len(self.daily_insights) == 0:
                self.daily_insights.add(DailyHighLevelInsight.monitor_modify_if_needed)

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