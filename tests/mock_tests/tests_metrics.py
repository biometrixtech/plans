from models.metrics import AthleteSorenessMetricGenerator, AthleteTrainingVolumeMetricGenerator, MetricColor, DailyHighLevelInsight, MetricType, ThresholdRecommendation
from models.stats import AthleteStats
from models.soreness import BodyPartLocation, Soreness, HistoricSoreness, HistoricSorenessStatus


def get_atv(rpe_val):

    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = rpe_val

    atv = AthleteTrainingVolumeMetricGenerator("session RPE", MetricType.daily, athlete_stats, "session_RPE")
    atv.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                 DailyHighLevelInsight.limit_time_intensity_of_training,
                                                 "high_level_action_description",
                                                 ["2B", "7A"], 8.0, None, None,
                                                 "stop now")
    atv.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                 DailyHighLevelInsight.limit_time_intensity_of_training,
                                                "high_level_action_description",
                                                 ["2B", "7A"], 6.0, 8.0, None,
                                                 "consider stopping")

    return atv


def get_asg(soreness_list, attribute_name):

    asg = AthleteSorenessMetricGenerator("deep pain", MetricType.daily, soreness_list, attribute_name)
    asg.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                 DailyHighLevelInsight.limit_time_intensity_of_training,
                                                 "high_level_action_description",
                                                 ["2B", "7A"], 4.0, None, None,
                                                 "stop now")
    asg.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                 DailyHighLevelInsight.limit_time_intensity_of_training,
                                                "high_level_action_description",
                                                 ["2B", "7A"], 3.0, 4.0, None,
                                                 "consider stopping")

    asg.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                DailyHighLevelInsight.limit_time_intensity_of_training,
                                                "high_level_action_description",
                                                ["2B", "7A"], None, 3.0, None,
                                                "don't stop")

    return asg


def test_populate_thresholds_athlete_training_volume_low():

    atv = get_atv(3)

    atv.populate_thresholds()

    assert atv.thresholds[0].count == 0
    assert atv.thresholds[1].count == 0


def test_populate_thresholds_athlete_training_volume_thresh_1():

    atv = get_atv(6)

    atv.populate_thresholds()

    assert atv.thresholds[0].count == 0
    assert atv.thresholds[1].count == 1

def test_populate_thresholds_athlete_training_volume_thresh_2():

    atv = get_atv(8)

    atv.populate_thresholds()

    assert atv.thresholds[0].count == 1
    assert atv.thresholds[1].count == 0

def test_populate_thresholds_athlete_training_volume_thresh_None():

    atv = get_atv(None)

    atv.populate_thresholds()

    assert atv.thresholds[0].count == 0
    assert atv.thresholds[1].count == 0

def test_populate_thresholds_athlete_soreness_thresh_low():

    hist_soreness = HistoricSoreness(BodyPartLocation(12), 1, True)
    hist_soreness.historic_soreness_status = HistoricSorenessStatus.chronic
    hist_soreness.average_severity = 3
    hist_soreness_list = [hist_soreness]

    asg = get_asg(soreness_list=hist_soreness_list, attribute_name="average_severity")

    asg.populate_thresholds_with_soreness()

    assert len(asg.thresholds[0].soreness_list) == 0
    assert len(asg.thresholds[1].soreness_list) == 1
    assert len(asg.thresholds[2].soreness_list) == 0

