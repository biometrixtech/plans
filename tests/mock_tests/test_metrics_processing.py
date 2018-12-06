from logic.metrics_processing import MetricsProcessing, RecommendationMatrix
from models.stats import AthleteStats
from models.metrics import AthleteMetric, MetricColor, MetricType, SpecificAction
from models.soreness import BodyPartLocation, HistoricSorenessStatus, HistoricSoreness


def test_session_rpe_specific_actions():
    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = 8.0
    athlete_stats.session_RPE_event_date = "2018-07-01"

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].specific_actions[0].code == "2B"
    assert metrics_list[0].specific_actions[1].code == "7A"


def test_top_yellow_session_rpe():
    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = 8.0
    athlete_stats.session_RPE_event_date = "2018-07-01"

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow


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


def test_persistent_2_pain_specific_actions():
    athlete_stats = AthleteStats("tester")

    hist_soreness = HistoricSoreness(BodyPartLocation(12), 1, True)
    hist_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2
    hist_soreness.average_severity = 3
    hist_soreness_list = [hist_soreness]
    athlete_stats.historic_soreness = hist_soreness_list

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].specific_actions[0].code == "6B"
    assert metrics_list[0].specific_actions[1].code == "7A"


def test_recommendation_matrix_ranking():

    metric1 = AthleteMetric("Cool metric", MetricType.daily)
    metric2 = AthleteMetric("Cooler metric", MetricType.daily)
    metric3 = AthleteMetric("Coolest metric", MetricType.daily)

    specific_action1 = SpecificAction("7A", "Cool", True)
    specific_action2 = SpecificAction("7B", "Cooler", True)
    specific_action3 = SpecificAction("7C", "Coolest", True)

    metric1.specific_actions.append(specific_action1)
    metric2.specific_actions.append(specific_action2)
    metric3.specific_actions.append(specific_action3)

    metric_list = [metric3, metric2, metric1]  # add reverse order to make sorting harder

    rec_matrix = RecommendationMatrix()
    rec_matrix.add_metrics(metric_list)

    ranked_list = rec_matrix.get_ranked_metrics()

    assert ranked_list[0].specific_actions[0].display == False
    assert ranked_list[1].specific_actions[0].display == False
    assert ranked_list[2].specific_actions[0].display == True