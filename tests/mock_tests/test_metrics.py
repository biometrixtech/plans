from models.metrics import AthleteSorenessMetricGenerator, AthleteTrainingVolumeMetricGenerator, MetricColor, DailyHighLevelInsight, MetricType, TextGenerator, ThresholdRecommendation
from models.stats import AthleteStats
from models.soreness import BodyPart, BodyPartLocation, Soreness, HistoricSoreness, HistoricSorenessStatus


def get_atv(rpe_val):

    athlete_stats = AthleteStats("tester")
    athlete_stats.session_RPE = rpe_val

    atv = AthleteTrainingVolumeMetricGenerator("session RPE", MetricType.daily, athlete_stats, "session_RPE")
    atv.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                 "high_level_action_description",
                                                ["2B", "7A"], 8.0, None, None,
                                                 "stop now")
    atv.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                "high_level_action_description",
                                                ["2B", "7A"], 6.0, 8.0, None,
                                                 "consider stopping")

    return atv


def get_asg(soreness_list, attribute_name):

    asg = AthleteSorenessMetricGenerator("deep pain", MetricType.daily, soreness_list, attribute_name)
    asg.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                 "high_level_action_description",
                                                ["2B", "7A"], 4.0, None, "stop with your {bodypart}!", None)
    asg.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                "high_level_action_description",
                                                ["2B", "7A"], 3.0, 4.0, "consider stopping your {bodypart}!", None,
                                                )

    asg.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                "high_level_action_description",
                                                ["2B", "7A"], None, 3.0, "don't stop your {bodypart}!", None)

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


def test_populate_thresholds_athlete_hist_soreness_thresh_low():

    hist_soreness = HistoricSoreness(BodyPartLocation(12), 1, True)
    hist_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
    hist_soreness.average_severity = 3
    hist_soreness_list = [hist_soreness]

    asg = get_asg(soreness_list=hist_soreness_list, attribute_name="average_severity")

    asg.populate_thresholds_with_soreness()

    assert len(asg.thresholds[0].soreness_list) == 0
    assert len(asg.thresholds[1].soreness_list) == 1
    assert len(asg.thresholds[2].soreness_list) == 0


def test_populate_thresholds_athlete_hist_soreness_thresh_mod():

    hist_soreness = HistoricSoreness(BodyPartLocation(12), 1, True)
    hist_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
    hist_soreness.average_severity = 4
    hist_soreness_list = [hist_soreness]

    asg = get_asg(soreness_list=hist_soreness_list, attribute_name="average_severity")

    asg.populate_thresholds_with_soreness()

    assert len(asg.thresholds[0].soreness_list) == 1
    assert len(asg.thresholds[1].soreness_list) == 0
    assert len(asg.thresholds[2].soreness_list) == 0


def test_populate_thresholds_athlete_daily_soreness_thresh_mod_diff():

    soreness1 = Soreness()
    soreness1.severity = 4
    soreness1.pain = True
    soreness1.streak = 2
    soreness1.side = 1
    soreness1.body_part = BodyPart(BodyPartLocation.lats, None)

    soreness2 = Soreness()
    soreness2.severity = 4
    soreness2.pain = True
    soreness2.streak = 3
    soreness2.side = 2
    soreness2.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness_list = [soreness1, soreness2]

    asg = get_asg(soreness_list=soreness_list, attribute_name="severity")

    asg.populate_thresholds_with_soreness()

    assert len(asg.thresholds[0].soreness_list) == 2
    assert len(asg.thresholds[1].soreness_list) == 0
    assert len(asg.thresholds[2].soreness_list) == 0

def test_populate_thresholds_athlete_daily_soreness_thresh_mod_metrics_same():

    soreness1 = Soreness()
    soreness1.severity = 4
    soreness1.pain = True
    soreness1.streak = 2
    soreness1.side = 1
    soreness1.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness2 = Soreness()
    soreness2.severity = 4
    soreness2.pain = True
    soreness2.streak = 3
    soreness2.side = 2
    soreness2.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness_list = [soreness1, soreness2]

    asg = get_asg(soreness_list=soreness_list, attribute_name="severity")

    asg.populate_thresholds_with_soreness()

    metrics = asg.get_metric_list()

    assert len(metrics) == 1


def test_populate_thresholds_athlete_daily_soreness_thresh_mod_metrics_diff():

    soreness1 = Soreness()
    soreness1.severity = 4
    soreness1.pain = True
    soreness1.streak = 2
    soreness1.side = 1
    soreness1.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness2 = Soreness()
    soreness2.severity = 1
    soreness2.pain = True
    soreness2.streak = 3
    soreness2.side = 2
    soreness2.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness_list = [soreness1, soreness2]

    asg = get_asg(soreness_list=soreness_list, attribute_name="severity")

    asg.populate_thresholds_with_soreness()

    metrics = asg.get_metric_list()

    assert len(metrics) == 2


def test_body_part_text_uppercase_if_first():

    soreness1 = Soreness()
    soreness1.severity = 4
    soreness1.pain = True
    soreness1.streak = 2
    soreness1.side = 1
    soreness1.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness2 = Soreness()
    soreness2.severity = 1
    soreness2.pain = True
    soreness2.streak = 3
    soreness2.side = 2
    soreness2.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness_list = [soreness1, soreness2]

    text_gen = TextGenerator()

    test_text = text_gen.get_body_part_text("{bodypart} hurts badly!!", soreness_list)

    test_text2 = text_gen.get_body_part_text("bodypart hurts badly, complete Fathom's Prep!!", soreness_list)

    assert test_text[0].isupper() is True

    assert test_text2 == "Bodypart hurts badly, complete Fathom's Prep!!"

def test_body_part_text_bilateral_grouping():

    soreness1 = Soreness()
    soreness1.severity = 4
    soreness1.pain = True
    soreness1.streak = 2
    soreness1.side = 1
    soreness1.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness2 = Soreness()
    soreness2.severity = 1
    soreness2.pain = True
    soreness2.streak = 3
    soreness2.side = 1
    soreness2.body_part = BodyPart(BodyPartLocation.ankle, None)

    soreness3 = Soreness()
    soreness3.severity = 1
    soreness3.pain = True
    soreness3.streak = 3
    soreness3.side = 2
    soreness3.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness_list = [soreness1, soreness2, soreness3]

    text_gen = TextGenerator()

    test_text = text_gen.get_body_part_text("{bodypart} hurts badly!!", soreness_list)

    assert test_text == "Left ankle, left and right calf hurts badly!!"


def test_3_body_part_text_no_bilateral_grouping():

    soreness1 = Soreness()
    soreness1.severity = 4
    soreness1.pain = True
    soreness1.streak = 2
    soreness1.side = 1
    soreness1.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness2 = Soreness()
    soreness2.severity = 1
    soreness2.pain = True
    soreness2.streak = 3
    soreness2.side = 1
    soreness2.body_part = BodyPart(BodyPartLocation.ankle, None)

    soreness3 = Soreness()
    soreness3.severity = 1
    soreness3.pain = True
    soreness3.streak = 3
    soreness3.side = 2
    soreness3.body_part = BodyPart(BodyPartLocation.foot, None)

    soreness_list = [soreness1, soreness2, soreness3]

    text_gen = TextGenerator()

    test_text = text_gen.get_body_part_text("{bodypart} Hurts badly!!", soreness_list)

    assert test_text == "Left ankle, right foot and left calf Hurts badly!!"


def test_2_body_part_text_no_bilateral_grouping():

    soreness1 = Soreness()
    soreness1.severity = 4
    soreness1.pain = True
    soreness1.streak = 2
    soreness1.side = 1
    soreness1.body_part = BodyPart(BodyPartLocation.calves, None)

    soreness2 = Soreness()
    soreness2.severity = 1
    soreness2.pain = True
    soreness2.streak = 3
    soreness2.side = 1
    soreness2.body_part = BodyPart(BodyPartLocation.ankle, None)

    soreness_list = [soreness1, soreness2]

    text_gen = TextGenerator()

    test_text = text_gen.get_body_part_text("{bodypart} Hurts badly!!", soreness_list)

    assert test_text == "Left ankle and left calf Hurts badly!!"


def test_1_body_part_text_no_bilateral_grouping():

    soreness2 = Soreness()
    soreness2.severity = 1
    soreness2.pain = True
    soreness2.streak = 3
    soreness2.side = 1
    soreness2.body_part = BodyPart(BodyPartLocation.ankle, None)

    soreness_list = [soreness2]

    text_gen = TextGenerator()

    test_text = text_gen.get_body_part_text("{bodypart} hurts badly!!", soreness_list)

    assert test_text == "Left ankle hurts badly!!"