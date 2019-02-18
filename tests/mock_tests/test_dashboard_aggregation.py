from models.metrics import AthleteMetric, MetricColor, WeeklyHighLevelInsight, DailyHighLevelInsight, MetricType, SpecificAction
from models.dashboard import AthleteDashboardData, TeamDashboardData
from models.daily_readiness import DailyReadiness
from models.daily_plan import  DailyPlan
import datetime

def get_metric(metric_type, color, high_level_insight, specific_insight, rec1, rec2, insufficient_data=False):
    metric = AthleteMetric('Metric', metric_type)
    metric.color = color
    metric.high_level_insight = high_level_insight
    metric.specific_insight_recovery = specific_insight
    metric.specific_actions = [rec1, rec2]
    metric.insufficient_data = insufficient_data
    return metric


def get_athlete(metrics):
    athlete = AthleteDashboardData("user_id", "fisrt_name", 'last_name')
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
    assert athlete.daily_recommendation == set(['Training as normal and completing Fathom’s Mobility and Recovery exercises'])
    assert athlete.insights == ["No signs of overtraining or injury risk"]


def test_not_cleared_to_train():
    metric = get_metric(MetricType.daily,
                        MetricColor.red,
                        DailyHighLevelInsight.seek_med_staff_evaluation,
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
                         WeeklyHighLevelInsight.signs_of_elevated_injury_risk,
                         "Metric1 insight",
                         SpecificAction("1B", "metric1_rec1", True),
                         SpecificAction("3B", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.red,
                         DailyHighLevelInsight.seek_med_staff_evaluation,
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
    assert athlete.weekly_recommendation == set()
    assert athlete.daily_recommendation == set(["*metric2_rec1", "*metric2_rec2"])
    assert athlete.insufficient_data
    assert athlete.insights == ["Metric2 insight", "Metric1 insight"]

def test_not_cleared_to_train_daily_weekly():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.red,
                         WeeklyHighLevelInsight.needs_lower_training_intensity,
                         "Metric1 insight",
                         SpecificAction("1A", "metric1_rec1", True),
                         SpecificAction("2A", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.red,
                         DailyHighLevelInsight.seek_med_staff_evaluation,
                         "Metric2 insight",
                         SpecificAction("5A", "metric2_rec1", True),
                         SpecificAction("3A", "metric2_rec2", True)
                         )
    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert not athlete.insufficient_data
    assert athlete.weekly_recommendation == set(["metric1_rec1", "metric2_rec2"])
    assert athlete.daily_recommendation == set(["metric1_rec2", "metric2_rec1"])
    assert athlete.insights == ["Metric1 insight", "Metric2 insight"]


def test_not_cleared_to_train_weekly():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.red,
                         WeeklyHighLevelInsight.needs_lower_training_intensity,
                         "Metric1 insight",
                         SpecificAction("1A", "metric1_rec1", True),
                         SpecificAction("2A", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.yellow,
                         DailyHighLevelInsight.monitor_in_training,
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
    assert athlete.weekly_recommendation == set(["metric1_rec1"])
    assert athlete.daily_recommendation == set(["metric1_rec2"])
    assert athlete.insights == ["Metric1 insight", "Metric2 insight"]


def test_cleared_to_train():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.yellow,
                         WeeklyHighLevelInsight.signs_of_elevated_injury_risk,
                         "Metric1 insight",
                         SpecificAction("1B", "metric1_rec1", True),
                         SpecificAction("2B", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.yellow,
                         DailyHighLevelInsight.monitor_in_training,
                         "Metric2 insight",
                         SpecificAction("3B", "metric2_rec1", True),
                         SpecificAction("5B", "metric2_rec2", True)
                         )

    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.yellow
    assert athlete.cleared_to_train  == True
    assert athlete.weekly_recommendation == set(["metric1_rec1", "metric2_rec1"])
    assert athlete.daily_recommendation == set(["metric1_rec2", "metric2_rec2"])
    assert athlete.insights == ["Metric1 insight", "Metric2 insight"]


def test_athlete_grouping():
    daily_increase_workload = get_metric(MetricType.daily,
                                         MetricColor.yellow,
                                         DailyHighLevelInsight.increase_workload,
                                         "insight",
                                         SpecificAction("1B", "rec1", True),
                                         SpecificAction("2B", "rec2", True)
                                         )
    daily_limit_time_intensity_of_training = get_metric(MetricType.daily,
                                                        MetricColor.yellow,
                                                        DailyHighLevelInsight.limit_time_intensity_of_training,
                                                        "insight",
                                                        SpecificAction("1B", "rec1", True),
                                                        SpecificAction("2B", "rec2", True)
                                                        )
    daily_monitor_in_training = get_metric(MetricType.daily,
                                           MetricColor.yellow,
                                           DailyHighLevelInsight.monitor_in_training,
                                           "insight",
                                           SpecificAction("1B", "rec1", True),
                                           SpecificAction("2B", "rec2", True)
                                           )

    weekly_balance_overtraining_risk = get_metric(MetricType.longitudinal,
                                                  MetricColor.yellow,
                                                  WeeklyHighLevelInsight.balance_overtraining_risk,
                                                  "insight",
                                                  SpecificAction("1B", "rec1", True),
                                                  SpecificAction("2B", "rec2", True)
                                                 )
    weekly_add_variety_to_training_risk = get_metric(MetricType.longitudinal,
                                                     MetricColor.yellow,
                                                     WeeklyHighLevelInsight.add_variety_to_training_risk,
                                                     "insight",
                                                     SpecificAction("1B", "rec1", True),
                                                     SpecificAction("2B", "rec2", True)
                                                    )

    weekly_evaluate_health_status = get_metric(MetricType.longitudinal,
                                               MetricColor.red,
                                               WeeklyHighLevelInsight.needs_lower_training_intensity,
                                               "insight",
                                               SpecificAction("1B", "rec1", True),
                                               SpecificAction("2B", "rec2", True)
                                               )
    team = TeamDashboardData("Fathom Team")
    athlete1 = get_athlete([daily_limit_time_intensity_of_training, daily_monitor_in_training, weekly_balance_overtraining_risk])
    team.insert_user(athlete1)
    athlete2 = get_athlete([daily_increase_workload, weekly_add_variety_to_training_risk])
    team.insert_user(athlete2)
    athlete3 = get_athlete([daily_limit_time_intensity_of_training, daily_monitor_in_training, weekly_add_variety_to_training_risk])
    team.insert_user(athlete3)
    athlete4 = get_athlete([daily_limit_time_intensity_of_training, daily_monitor_in_training, weekly_evaluate_health_status])
    team.insert_user(athlete4)


    assert len(team.daily_insights.all_good) == 0
    assert len(team.daily_insights.increase_workload) == 1
    assert len(team.daily_insights.limit_time_intensity_of_training) == 2
    assert len(team.daily_insights.monitor_in_training) == 2
    assert len(team.daily_insights.not_cleared_for_training) == 1

    assert len(team.weekly_insights.all_good) == 0
    assert len(team.weekly_insights.balance_overtraining_risk) == 1
    assert len(team.weekly_insights.add_variety_to_training_risk) == 2
    assert len(team.weekly_insights.increase_weekly_workload) == 0
    assert len(team.weekly_insights.address_pain_or_soreness) == 0
    assert len(team.weekly_insights.evaluate_health_status) == 1


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

