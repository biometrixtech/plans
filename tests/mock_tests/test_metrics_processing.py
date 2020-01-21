from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from fathomapi.api.config import Config
Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                             'body_part_mapping_filename': 'body_part_mapping_fathom.json'})


from logic.metrics_processing import MetricsProcessing, RecommendationMatrix
from models.stats import AthleteStats
from models.metrics import AthleteMetric, MetricColor, MetricType, SpecificAction
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.historic_soreness import HistoricSoreness
from models.training_volume import StandardErrorRange


'''Excluding session RPE for now
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
'''

def test_yellow_internal_acwr_insufficient():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.observed_value = 1.4
    standard_error_range.upper_bound = 1.6
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_acwr = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert True is metrics_list[0].insufficient_data_for_thresholds


def test_yellow_internal_acwr():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.observed_value = 1.4
    standard_error_range.upper_bound = None
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_acwr = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert False is metrics_list[0].insufficient_data_for_thresholds

def test_yellow_internal_acwr_range_wider_partial():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.observed_value = 0.6
    standard_error_range.upper_bound = 3.0
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_acwr = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert True is metrics_list[0].range_wider_than_thresholds
    assert False is metrics_list[1].range_wider_than_thresholds

def test_yellow_internal_acwr_range_wider_full():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.observed_value = 0.3
    standard_error_range.upper_bound = 3.0
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_acwr = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert True is metrics_list[0].range_wider_than_thresholds
    assert True is metrics_list[1].range_wider_than_thresholds

def test_yellow_internal_monotony():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.observed_value = 1.4
    standard_error_range.upper_bound = None

    standard_error_range_2 = StandardErrorRange()
    standard_error_range_2.observed_value = 1.8
    standard_error_range_2.upper_bound = None

    monotony_list = [standard_error_range, standard_error_range_2]

    athlete_stats.event_date = "2018-07-01"
    athlete_stats.historical_internal_monotony = monotony_list

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert False is metrics_list[0].insufficient_data_for_thresholds

def test_yellow_internal_monotony_range_threshold_error():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.observed_value = 0.2
    standard_error_range.upper_bound = None

    standard_error_range_2 = StandardErrorRange()
    standard_error_range_2.observed_value = 3.8
    standard_error_range_2.upper_bound = None

    monotony_list = [standard_error_range, standard_error_range_2]

    athlete_stats.event_date = "2018-07-01"
    athlete_stats.historical_internal_monotony = monotony_list

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert True is metrics_list[0].range_wider_than_thresholds


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
    hist_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
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

    metric1.color = MetricColor.red
    metric2.color = MetricColor.yellow
    metric3.color = MetricColor.yellow

    metric1.high_level_insight = "insight A"
    metric2.high_level_insight = "insight B"
    metric3.high_level_insight = "insight C"

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

def test_recommendation_matrix_color_ranking():

    metric1 = AthleteMetric("Cool metric", MetricType.daily)
    metric2 = AthleteMetric("Cooler metric", MetricType.daily)
    metric3 = AthleteMetric("Coolest metric", MetricType.daily)

    metric1.color = MetricColor.red
    metric2.color = MetricColor.yellow
    metric3.color = MetricColor.yellow

    metric1.high_level_insight = "insight A"
    metric2.high_level_insight = "insight A"
    metric3.high_level_insight = "insight B"

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

    assert len(ranked_list) == 2


def test_green_internal_acwr_range_wider_lower():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.lower_bound = 0.75
    standard_error_range.observed_value = 1.0
    standard_error_range.upper_bound = 1.15
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_acwr = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert not metrics_list[0].range_wider_than_thresholds
    assert metrics_list[0].insufficient_data_for_thresholds

def test_green_internal_acwr_range_wider_higher():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.lower_bound = 0.85
    standard_error_range.observed_value = 1.0
    standard_error_range.upper_bound = 1.5
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_acwr = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert not metrics_list[0].range_wider_than_thresholds
    assert metrics_list[0].insufficient_data_for_thresholds

def test_green_internal_acwr_range_wider_both():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.lower_bound = 0.75
    standard_error_range.observed_value = 1.0
    standard_error_range.upper_bound = 1.35
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_acwr = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert len(metrics_list) == 2
    assert metrics_list[0].color == MetricColor.yellow
    assert not metrics_list[0].range_wider_than_thresholds
    assert metrics_list[0].insufficient_data_for_thresholds

    assert metrics_list[1].color == MetricColor.yellow
    assert not metrics_list[1].range_wider_than_thresholds
    assert metrics_list[1].insufficient_data_for_thresholds

def test_green_internal_ramp_range_wider():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.lower_bound = 0.75
    standard_error_range.observed_value = 1.1
    standard_error_range.upper_bound = 1.151
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_ramp = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert not metrics_list[0].range_wider_than_thresholds
    assert metrics_list[0].insufficient_data_for_thresholds

def test_green_internal_ramp_range_wider_out_of_range():
    athlete_stats = AthleteStats("tester")
    standard_error_range = StandardErrorRange()
    standard_error_range.lower_bound = 0.75
    standard_error_range.observed_value = 1.1
    standard_error_range.upper_bound = 1.15101
    athlete_stats.event_date = "2018-07-01"
    athlete_stats.internal_ramp = standard_error_range

    metrics_processor = MetricsProcessing()
    metrics_list = metrics_processor.get_athlete_metrics_from_stats(athlete_stats, "2018-07-01")

    assert metrics_list[0].color == MetricColor.yellow
    assert metrics_list[0].range_wider_than_thresholds
    assert metrics_list[0].insufficient_data_for_thresholds