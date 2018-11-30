from logic.metrics_processing import MetricsProcessing
from models.stats import AthleteStats
from models.metrics import AthleteMetric, MetricColor, WeeklyHighLevelInsight, DailyHighLevelInsight, MetricType, SpecificAction
from models.soreness import BodyPartLocation, HistoricSorenessStatus, HistoricSoreness
from models.dashboard import AthleteDashboardData



def get_metric(metric_type, color, high_level_insight, specific_insight, rec1, rec2):
    metric = AthleteMetric('Metric', metric_type)
    metric.color = color
    metric.high_level_insight = high_level_insight
    metric.specific_insight_recovery = specific_insight
    metric.specific_actions = [rec1, rec2]
    return metric


def test_no_metrics():
    metrics = []
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.green
    assert athlete.cleared_to_train  == True
    assert athlete.daily_recommendation == set(['Training as normal and complete Fathom’s Prep and Recovery'])
    assert athlete.insights == ["No signs of overtraining or injury risk"]


def test_not_cleared_to_train():
    metric = get_metric(MetricType.daily,
                        MetricColor.red,
                        DailyHighLevelInsight.not_cleared_for_training,
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
                         WeeklyHighLevelInsight.address_pain_or_soreness,
                         "Metric1 insight",
                         SpecificAction("1B", "metric1_rec1", True),
                         SpecificAction("3B", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.red,
                         DailyHighLevelInsight.not_cleared_for_training,
                         "Metric2 insight",
                         SpecificAction("2A", "metric2_rec1", True),
                         SpecificAction("5A", "metric2_rec2", True)
                         )
    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert athlete.cleared_to_train  == False
    assert athlete.weekly_recommendation == set()
    assert athlete.daily_recommendation == set(["metric2_rec1", "metric2_rec2"])
    assert athlete.insights == ["Metric1 insight", "Metric2 insight"]

def test_not_cleared_to_train_daily_weekly():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.red,
                         WeeklyHighLevelInsight.evaluate_health_status,
                         "Metric1 insight",
                         SpecificAction("1A", "metric1_rec1", True),
                         SpecificAction("2A", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.red,
                         DailyHighLevelInsight.not_cleared_for_training,
                         "Metric2 insight",
                         SpecificAction("5A", "metric2_rec1", True),
                         SpecificAction("3A", "metric2_rec2", True)
                         )
    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert athlete.cleared_to_train  == False
    assert athlete.weekly_recommendation == set(["metric1_rec1", "metric2_rec2"])
    assert athlete.daily_recommendation == set(["metric1_rec2", "metric2_rec1"])
    assert athlete.insights == ["Metric1 insight", "Metric2 insight"]


def test_not_cleared_to_train_weekly():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.red,
                         WeeklyHighLevelInsight.evaluate_health_status,
                         "Metric1 insight",
                         SpecificAction("1A", "metric1_rec1", True),
                         SpecificAction("2A", "metric1_rec2", True)
                         )
    metric2 = get_metric(MetricType.daily,
                         MetricColor.yellow,
                         DailyHighLevelInsight.monitor_in_training,
                         "Metric2 insight",
                         SpecificAction("2B", "metric2_rec1", True),
                         SpecificAction("5B", "metric2_rec2", True)
                         )

    metrics = [metric1, metric2]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert athlete.cleared_to_train  == False
    assert athlete.weekly_recommendation == set(["metric1_rec1"])
    assert athlete.daily_recommendation == set(["metric1_rec2"])
    assert athlete.insights == ["Metric1 insight", "Metric2 insight"]


def test_cleared_to_train():
    metric1 = get_metric(MetricType.longitudinal,
                         MetricColor.yellow,
                         WeeklyHighLevelInsight.address_pain_or_soreness,
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
