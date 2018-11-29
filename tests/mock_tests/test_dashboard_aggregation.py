from logic.metrics_processing import MetricsProcessing
from models.stats import AthleteStats
from models.metrics import AthleteMetric, MetricColor, WeeklyHighLevelInsight, DailyHighLevelInsight, MetricType
from models.soreness import BodyPartLocation, HistoricSorenessStatus, HistoricSoreness
from models.dashboard import AthleteDashboardData


def test_not_cleared_to_train():
    metric = AthleteMetric('Severe Chronic Pain', MetricType.longitudinal)
    metric.color = MetricColor.red
    metric.high_level_insight = WeeklyHighLevelInsight.evaluate_health_status
    metrics = [metric]
    athlete = AthleteDashboardData('tester', 'first_name', 'last_name')
    athlete.aggregate(metrics)
    assert athlete.color == MetricColor.red
    assert athlete.cleared_to_train  == False


# def test_session_rpe_specific_actions():
#     athlete_stats = AthleteStats("tester")
#     athlete_stats.session_RPE = 8.0
#     athlete_stats.session_RPE_event_date = "2018-07-01"

#     metrics_processor = MetricsProcessing()
#     metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

#     assert metrics_list[0].specific_actions[0] == "2B"
#     assert metrics_list[0].specific_actions[1] == "7A"


# def test_red_session_rpe():
#     athlete_stats = AthleteStats("tester")
#     athlete_stats.session_RPE = 8.0
#     athlete_stats.session_RPE_event_date = "2018-07-01"

#     metrics_processor = MetricsProcessing()
#     metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

#     assert metrics_list[0].color == MetricColor.red


# def test_yellow_high_session_rpe():
#     athlete_stats = AthleteStats("tester")
#     athlete_stats.session_RPE = 7.9
#     athlete_stats.session_RPE_event_date = "2018-07-01"

#     metrics_processor = MetricsProcessing()
#     metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

#     assert metrics_list[0].color == MetricColor.yellow


# def test_yellow_low_session_rpe():
#     athlete_stats = AthleteStats("tester")
#     athlete_stats.session_RPE = 6.0
#     athlete_stats.session_RPE_event_date = "2018-07-01"

#     metrics_processor = MetricsProcessing()
#     metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

#     assert metrics_list[0].color == MetricColor.yellow


# def test_no_session_rpe_diff_date():
#     athlete_stats = AthleteStats("tester")
#     athlete_stats.session_RPE = 6.0
#     athlete_stats.session_RPE_event_date = "2018-07-01"

#     metrics_processor = MetricsProcessing()
#     metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-02")

#     assert len(metrics_list) == 0


# def test_chronic_pain_specific_actions():
#     athlete_stats = AthleteStats("tester")

#     hist_soreness = HistoricSoreness(BodyPartLocation(12), 1, True)
#     hist_soreness.historic_soreness_status = HistoricSorenessStatus.chronic
#     hist_soreness.average_severity = 3
#     hist_soreness_list = [hist_soreness]
#     athlete_stats.historic_soreness = hist_soreness_list

#     metrics_processor = MetricsProcessing()
#     metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

#     assert metrics_list[0].specific_actions[0] == "6B"
#     assert metrics_list[0].specific_actions[1] == "7A"