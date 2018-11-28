from logic.metrics_processing import MetricsProcessing
from models.stats import AthleteStats
from models.metrics import MetricColor


def test_session_rpe_specific_actions():
    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = 8.0
    athlete_stats.session_RPE_event_date = "2018-07-01"

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].specific_actions[0] == "2B"
    assert metrics_list[0].specific_actions[1] == "7A"


def test_red_session_rpe():
    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = 8.0
    athlete_stats.session_RPE_event_date = "2018-07-01"

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.red


def test_yellow_high_session_rpe():
    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = 7.9
    athlete_stats.session_RPE_event_date = "2018-07-01"

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow


def test_yellow_low_session_rpe():
    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = 6.0
    athlete_stats.session_RPE_event_date = "2018-07-01"

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow


def test_no_session_rpe_diff_date():
    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = 6.0
    athlete_stats.session_RPE_event_date = "2018-07-01"

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-02")

    assert len(metrics_list) == 0