from models.metrics import AthleteMetric, MetricColor, WeeklyHighLevelInsight, DailyHighLevelInsight, MetricType, SpecificAction
from models.dashboard import AthleteDashboardData, TeamDashboardData
from models.daily_readiness import DailyReadiness
from models.daily_plan import  DailyPlan
import datetime

def get_metric(metric_type, color, high_level_insight, specific_insight, rec1, rec2, insufficient_data=False, tv=False, name=None):
    metric = AthleteMetric('Metric', metric_type)
    if name is not None:
        metric.name = name
    metric.color = color
    metric.high_level_insight = high_level_insight
    if not tv:
        metric.specific_insight_recovery = specific_insight
    else:
        metric.specific_insight_training_volume = specific_insight
    metric.specific_actions = [rec1, rec2]
    metric.insufficient_data = insufficient_data
    return metric


def get_athlete(metrics):
    athlete = AthleteDashboardData("user_id", "first_name", 'last_name')
    athlete.aggregate(metrics)
    return athlete

def create_plan(user_id, readiness_survey_date, sessions_planned, training_sessions):
    plan = DailyPlan('2018-11-30')
    plan.user_id = user_id
    plan.daily_readiness_survey = readiness_survey_date
    plan.sessions_planned = sessions_planned
    plan.training_sessions = training_sessions
    return plan

def test_no_metrics():
    metrics = []
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.green
    assert athlete.cleared_to_train  == True
    assert athlete.daily_recommendation == ['Training as normal and completing Fathom’s Mobility and Recovery exercises']
    assert athlete.insights == ["No signs of overtraining or injury risk"]


def test_not_cleared_to_train():
    metric = get_metric(MetricType.daily,
                        MetricColor.red,
                        DailyHighLevelInsight.seek_med_eval_to_clear_for_training,
                        "Metric insight",
                        SpecificAction("2A", "metric1_rec1", True),
                        SpecificAction("5A", "metric1_rec2", True)
                        )
    metrics = [metric]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert athlete.cleared_to_train  == False

def test_not_cleared_to_train_daily():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.yellow,
                         WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                         "Metric1 insight",
                         SpecificAction("1B", "metric1_rec1", True),
                         SpecificAction("3B", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.red,
                         DailyHighLevelInsight.seek_med_eval_to_clear_for_training,
                         "Metric2 insight",
                         SpecificAction("2A", "metric2_rec1", True),
                         SpecificAction("5A", "metric2_rec2", True),
                         insufficient_data=True
                         )
    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert athlete.cleared_to_train  == False
    athlete = athlete.json_serialise()
    assert athlete["weekly_recommendation"] == []
    assert athlete["daily_recommendation"] == ["*metric2_rec2", "*metric2_rec1"]
    assert athlete["insufficient_data"]
    assert athlete["insights"] == ["Metric2 insight", "Metric1 insight"]

def test_insights_order_both_yellow():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.yellow,
                         WeeklyHighLevelInsight.at_risk_of_overtraining,
                         "Metric1 insight",
                         SpecificAction("1A", "metric1_rec1", True),
                         SpecificAction("2A", "metric1_rec2", True),
                         tv=True
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.yellow,
                         DailyHighLevelInsight.monitor_modify_if_needed,
                         "Metric2 insight",
                         SpecificAction("5A", "metric2_rec1", True),
                         SpecificAction("3A", "metric2_rec2", True)
                         )
    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.yellow
    assert not athlete.insufficient_data
    athlete = athlete.json_serialise()
    assert athlete['weekly_recommendation'] == ["metric2_rec2", "metric1_rec1"]
    assert athlete['daily_recommendation'] == ["metric2_rec1", "metric1_rec2"]
    assert athlete['insights'] == ["Metric2 insight", "Metric1 insight"]

def test_not_cleared_to_train_daily_weekly():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.red,
                         WeeklyHighLevelInsight.at_risk_of_overtraining,
                         "Metric1 insight",
                         SpecificAction("1A", "metric1_rec1", True),
                         SpecificAction("2A", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.red,
                         DailyHighLevelInsight.seek_med_eval_to_clear_for_training,
                         "Metric2 insight",
                         SpecificAction("5A", "metric2_rec1", True),
                         SpecificAction("3A", "metric2_rec2", True)
                         )
    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert not athlete.insufficient_data
    athlete = athlete.json_serialise()
    assert athlete["weekly_recommendation"] == ["metric2_rec2", "metric1_rec1"]
    assert athlete["daily_recommendation"] == ["metric2_rec1", "metric1_rec2"]
    assert athlete["insights"] == ["Metric1 insight", "Metric2 insight"]


def test_not_cleared_to_train_weekly():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.red,
                         WeeklyHighLevelInsight.at_risk_of_overtraining,
                         "Metric1 insight",
                         SpecificAction("1A", "metric1_rec1", True),
                         SpecificAction("2A", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.yellow,
                         DailyHighLevelInsight.monitor_modify_if_needed,
                         "Metric2 insight",
                         SpecificAction("2B", "metric2_rec1", True),
                         SpecificAction("5B", "metric2_rec2", True),
                         insufficient_data=True
                         )

    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert athlete.cleared_to_train  == False
    assert not athlete.insufficient_data
    assert athlete.weekly_recommendation == ["metric1_rec1"]
    assert athlete.daily_recommendation == ["metric1_rec2"]
    assert athlete.insights == ["Metric1 insight", "Metric2 insight"]

def test_pain_weekly_no_daily():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.yellow,
                         WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                         "Metric1 insight",
                         SpecificAction("6B", "metric1_rec1", True),
                         SpecificAction("3B", "metric1_rec2", True),
                         name = "Persistent-2 (Constant) Pain"
                         )

    metrics = [metric1]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.yellow
    assert athlete.cleared_to_train  == True
    assert not athlete.insufficient_data
    assert athlete.weekly_recommendation == ["metric1_rec2"]
    assert athlete.daily_recommendation == ["metric1_rec1"]
    assert athlete.insights == ["Metric1 insight"]
    assert athlete.daily_insights == {DailyHighLevelInsight.adapt_training_to_avoid_symptoms}


def test_soreness_weekly_no_daily():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.yellow,
                         WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                         "Metric1 insight",
                         SpecificAction("6B", "metric1_rec1", True),
                         SpecificAction("3B", "metric1_rec2", True),
                         name = "Persistent-2 (Constant) Soreness"
                         )

    metrics = [metric1]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.yellow
    assert athlete.cleared_to_train  == True
    assert not athlete.insufficient_data
    assert athlete.weekly_recommendation == ["metric1_rec2"]
    assert athlete.daily_recommendation == ["metric1_rec1"]
    assert athlete.insights == ["Metric1 insight"]
    assert athlete.daily_insights == set()

def test_cleared_to_train():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.yellow,
                         WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                         "Metric1 insight",
                         SpecificAction("1B", "metric1_rec1", True),
                         SpecificAction("2B", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.yellow,
                         DailyHighLevelInsight.monitor_modify_if_needed,
                         "Metric2 insight",
                         SpecificAction("3B", "metric2_rec1", True),
                         SpecificAction("5B", "metric2_rec2", True)
                         )

    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.yellow
    assert athlete.cleared_to_train  == True
    athlete = athlete.json_serialise()
    assert athlete["weekly_recommendation"] == ["metric2_rec1", "metric1_rec1"]
    assert athlete["daily_recommendation"] == ["metric2_rec2", "metric1_rec2"]
    assert athlete["insights"] == ["Metric1 insight", "Metric2 insight"]


def test_athlete_grouping():
    recovery_day_recommended = get_metric(MetricType.daily,
                                         MetricColor.yellow,
                                         DailyHighLevelInsight.recovery_day_recommended,
                                         "insight",
                                         SpecificAction("1B", "rec1", True),
                                         SpecificAction("2B", "rec2", True)
                                         )
    adapt_training_to_avoid_symptoms = get_metric(MetricType.daily,
                                                        MetricColor.yellow,
                                                        DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                        "insight",
                                                        SpecificAction("1B", "rec1", True),
                                                        SpecificAction("2B", "rec2", True)
                                                        )
    monitor_modify_if_needed = get_metric(MetricType.daily,
                                           MetricColor.yellow,
                                           DailyHighLevelInsight.monitor_modify_if_needed,
                                           "insight",
                                           SpecificAction("1B", "rec1", True),
                                           SpecificAction("2B", "rec2", True)
                                           )

    at_risk_of_overtraining = get_metric(MetricType.longitudinal,
                                                  MetricColor.yellow,
                                                  WeeklyHighLevelInsight.at_risk_of_overtraining,
                                                  "insight",
                                                  SpecificAction("1B", "rec1", True),
                                                  SpecificAction("2B", "rec2", True)
                                                  )
    low_variability_inhibiting_recovery = get_metric(MetricType.longitudinal,
                                                     MetricColor.yellow,
                                                     WeeklyHighLevelInsight.low_variability_inhibiting_recovery,
                                                     "insight",
                                                     SpecificAction("1B", "rec1", True),
                                                     SpecificAction("2B", "rec2", True)
                                                     )

    seek_med_eval_to_clear_for_training = get_metric(MetricType.longitudinal,
                                               MetricColor.red,
                                               WeeklyHighLevelInsight.seek_med_eval_to_clear_for_training,
                                               "insight",
                                               SpecificAction("1B", "rec1", True),
                                               SpecificAction("2B", "rec2", True)
                                               )
    team = TeamDashboardData("Fathom Team")
    athlete1 = get_athlete([adapt_training_to_avoid_symptoms, monitor_modify_if_needed, at_risk_of_overtraining])
    team.insert_user(athlete1)
    athlete2 = get_athlete([recovery_day_recommended, low_variability_inhibiting_recovery])
    team.insert_user(athlete2)
    athlete3 = get_athlete([adapt_training_to_avoid_symptoms, monitor_modify_if_needed, low_variability_inhibiting_recovery])
    team.insert_user(athlete3)
    athlete4 = get_athlete([adapt_training_to_avoid_symptoms, monitor_modify_if_needed, seek_med_eval_to_clear_for_training])
    team.insert_user(athlete4)


    assert len(team.daily_insights.all_good) == 0
    assert len(team.daily_insights.adapt_training_to_avoid_symptoms) == 2
    assert len(team.daily_insights.recovery_day_recommended) == 1
    assert len(team.daily_insights.monitor_modify_if_needed) == 2
    assert len(team.daily_insights.seek_med_eval_to_clear_for_training) == 1

    assert len(team.weekly_insights.all_good) == 0
    assert len(team.weekly_insights.at_risk_of_overtraining) == 1
    assert len(team.weekly_insights.low_variability_inhibiting_recovery) == 2
    assert len(team.weekly_insights.at_risk_of_undertraining) == 0
    assert len(team.weekly_insights.at_risk_of_time_loss_injury) == 0
    assert len(team.weekly_insights.seek_med_eval_to_clear_for_training) == 1


def test_compliance_grouping():
    user_ids = ["1", "2", "3", "4", "5"]
    users = {}
    for user_id in user_ids:
        users[user_id] = {"user_id": user_id,
                          "first_name": "user"+user_id,
                          "last_name": "last_name"
                          }

    daily_plan_list = [create_plan("1", "2018-11-30", True, []),
                       create_plan("2", "2018-11-30", True, ["session1", "session2"]),
                       create_plan("3", "2018-11-30", False, []),
                       create_plan("4", None, True, ["sensor_data"])]
    team = TeamDashboardData("Fathom Team")
    team.get_compliance_data(user_ids, users, daily_plan_list)

    assert len(team.compliance["complete"]) == 3
    assert len(team.compliance["incomplete"]) == 2
    assert len(team.compliance["training_compliance"]["no_response"]) == 3
    assert len(team.compliance["training_compliance"]["rest_day"]) == 1
    assert len(team.compliance["training_compliance"]["sessions_logged"]) == 1

