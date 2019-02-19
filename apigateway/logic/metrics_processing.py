from models.metrics import AthleteMetric, AthleteSorenessMetricGenerator, AthleteTrainingVolumeMetricGenerator, DailyHighLevelInsight, MetricColor, MetricType, ThresholdRecommendation, WeeklyHighLevelInsight
from models.soreness import HistoricSorenessStatus

class MetricsProcessing(object):

    def get_athlete_metrics_from_stats(self, athlete_stats, event_date):

        metrics = []

        #if athlete_stats.session_RPE_event_date == event_date:
        #    metrics.extend(DailySessionRPEMetricGenerator(athlete_stats, athlete_stats.session_RPE_event_date).get_metric_list())

        if athlete_stats.event_date == event_date:
            metrics.extend(IncreasingIACWRGenerator(athlete_stats).get_metric_list())
            metrics.extend(IncreasingInternalRampGenerator(athlete_stats).get_metric_list())
            metrics.extend(InternalMonotonyEventGenerator(athlete_stats).get_metric_list())
            metrics.extend(InternalStrainEventsGenerator(athlete_stats).get_metric_list())
            metrics.extend(DecreasingIACWRGenerator(athlete_stats).get_metric_list())

        if athlete_stats.daily_severe_soreness_event_date == event_date:
            metrics.extend(DailySorenessMetricGenerator(athlete_stats.daily_severe_soreness).get_metric_list())

        if athlete_stats.daily_severe_pain_event_date == event_date:
            metrics.extend(DailyPainMetricGenerator(athlete_stats.daily_severe_pain).get_metric_list())

        pain_list = list(p for p in athlete_stats.historic_soreness if p.is_acute_pain())
        metrics.extend(AcutePainMetricGenerator(pain_list).get_metric_list())

        ps_list = list(p for p in athlete_stats.historic_soreness if p.historic_soreness_status ==
                       HistoricSorenessStatus.persistent_soreness or p.historic_soreness_status ==
                       HistoricSorenessStatus.almost_persistent_2_soreness)
        metrics.extend(PersistentSorenessMetricGenerator(ps_list).get_metric_list())

        cs_list = list(p for p in athlete_stats.historic_soreness if p.historic_soreness_status ==
                       HistoricSorenessStatus.persistent_2_soreness)

        metrics.extend(Persistent_2SorenessMetricGenerator(cs_list).get_metric_list())

        pp_list = list(p for p in athlete_stats.historic_soreness if p.historic_soreness_status ==
                       HistoricSorenessStatus.persistent_pain or p.historic_soreness_status ==
                       HistoricSorenessStatus.almost_persistent_2_pain)

        metrics.extend(PersistentPainMetricGenerator(pp_list).get_metric_list())

        cp_list = list(p for p in athlete_stats.historic_soreness if p.historic_soreness_status ==
                       HistoricSorenessStatus.persistent_2_pain)

        metrics.extend(Persistent_2PainMetricGenerator(cp_list).get_metric_list())

        rec_matrix = RecommendationMatrix()
        rec_matrix.add_metrics(metrics)
        metrics = rec_matrix.get_ranked_metrics()

        return metrics


class RecommendationMatrix(object):
    def __init__(self):
        self.recs = {}
        self.metrics = []

    def add_metrics(self, metrics):

        self.metrics = metrics

        for m in metrics:
            for a in m.specific_actions:
                if a.code not in self.recs:
                    self.recs[a.code] = 1
                else:
                    self.recs[a.code] += 1

    def get_winners(self):

        winners = []

        for r in range(1, 8):
            code = str(r)+'A'
            if code in self.recs:
                winners.append(code)
                continue
            code = str(r) + 'B'
            if code in self.recs:
                winners.append(code)
                continue
            code = str(r) + 'C'
            if code in self.recs:
                winners.append(code)

        return winners

    def get_ranked_metrics(self):

        winners = self.get_winners()

        top_ranked_insights = {}

        for m in range(0, len(self.metrics)):
            for a in range(0, len(self.metrics[m].specific_actions)):
                if self.metrics[m].specific_actions[a].code in winners:
                    self.metrics[m].specific_actions[a].display = True
                else:
                    self.metrics[m].specific_actions[a].display = False

        for m in range(0, len(self.metrics)):
            if self.metrics[m].high_level_insight in top_ranked_insights:
                if self.metrics[m].color is not None and top_ranked_insights[self.metrics[m].high_level_insight].color is not None:
                    if (self.metrics[m].color > top_ranked_insights[self.metrics[m].high_level_insight].color or
                            (not self.metrics[m].insufficient_data and
                             top_ranked_insights[self.metrics[m].high_level_insight].insufficient_data)):
                        top_ranked_insights[self.metrics[m].high_level_insight] = self.metrics[m]
            else:
                top_ranked_insights[self.metrics[m].high_level_insight] = self.metrics[m]

        unique_metrics = list(top_ranked_insights.values())

        self.metrics = unique_metrics

        return self.metrics


class DailySessionRPEMetricGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats, session_rpe_event_date):
        super(DailySessionRPEMetricGenerator, self).__init__("Session RPE", MetricType.daily,
                                                             athlete_stats, "session_RPE")
        self.high_level_action_description = "Shorten training or limit intensity & to help facilitate recovery from spike in load"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.recovery_day_recommended,
                                                     self.high_level_action_description,
                                                     ["2B", "7A"], 8.0, 10.0, None,
                                                     "A significant spike in workload on " + session_rpe_event_date +" which should be balanced with recovery time"
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.recovery_day_recommended,
                                                     self.high_level_action_description,
                                                     ["2B", "7A"], 6.0, 7.0, None,
                                                     "A significant spike in workload on " + session_rpe_event_date +" which should be balanced with recovery time"
                                                     )
        self.populate_thresholds()


class IncreasingIACWRGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(IncreasingIACWRGenerator, self).__init__("Increasing IACWR", MetricType.longitudinal,
                                                             athlete_stats, "internal_acwr")
        self.high_level_action_description = "Consider decreasing workload this week or prioritizing holistic recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_overtraining,
                                                     self.high_level_action_description,
                                                     ["3A", "7A"], 1.51, None, None,
                                                     "Workload increasing at a rate associated with a high risk of injury."
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_overtraining,
                                                     self.high_level_action_description,
                                                     ["3B", "7A"], 1.3, 1.5, None,
                                                     "Workload increasing at a rate associated with a moderate risk of injury."
                                                     )
        self.populate_thresholds()


class IncreasingInternalRampGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(IncreasingInternalRampGenerator, self).__init__("Increasing Internal Ramp", MetricType.longitudinal,
                                                             athlete_stats, "internal_ramp")
        self.high_level_action_description = "Consider decreasing workload this week or prioritizing holistic recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_overtraining,
                                                     self.high_level_action_description,
                                                     ["3A", "7A"], 1.151, None, None,
                                                     "Workload increasing at a rate associated with a high risk of injury."
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_overtraining,
                                                     self.high_level_action_description,
                                                     ["3B", "7A"], 1.11, 1.15, None,
                                                     "Workload increasing at a rate associated with a moderate risk of injury."
                                                     )
        self.populate_thresholds()


class InternalStrainEventsGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(InternalStrainEventsGenerator, self).__init__("Internal Strain Events", MetricType.longitudinal,
                                                             athlete_stats, "internal_strain_events")
        self.high_level_action_description = "Increase variety in training duration & intensity, prioritize holistic recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.low_variability_inhibiting_recovery,
                                                     self.high_level_action_description,
                                                     ["1A", "7A"], 2, None, None,
                                                     "Very low variability in workloads which suppresses the immune system"
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.low_variability_inhibiting_recovery,
                                                     self.high_level_action_description,
                                                     ["1B", "7A"], 1, 1, None,
                                                     "Very low variability in workloads which suppresses the immune system"
                                                     )

        self.populate_thresholds()


class InternalMonotonyEventGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(InternalMonotonyEventGenerator, self).__init__("Internal Monotony Event", MetricType.longitudinal,
                                                             athlete_stats, "historical_internal_monotony")
        self.high_level_action_description = "Increase variety in training duration & intensity, prioritize holistic recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.low_variability_inhibiting_recovery,
                                                     self.high_level_action_description,
                                                     ["1A", "7A"], 2.0, None, None,
                                                     "Very low variability in workloads which suppresses the immune system"
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.low_variability_inhibiting_recovery,
                                                     self.high_level_action_description,
                                                     ["1B", "7A"], 1.6, 1.99, None,
                                                     "Very low variability in workloads which suppresses the immune system"
                                                     )
        self.populate_thresholds()


class DecreasingIACWRGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(DecreasingIACWRGenerator, self).__init__("Decreasing IACWR", MetricType.longitudinal,
                                                             athlete_stats, "internal_acwr")
        self.high_level_action_description = "Unless tapering, increase load with longer or higher intensity session or supplemental session"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_undertraining,
                                                     self.high_level_action_description,
                                                     ["3C", "7A"], None, 0.5, None,
                                                     "Rapidly decreasing load which may elevate athlete's susceptibility to injury"
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_undertraining,
                                                     self.high_level_action_description,
                                                     ["3C", "7A"], 0.51, 0.8, None,
                                                     "Significantly decreasing load. If unintentional, can reduce injury resiliance"
                                                     )
        self.populate_thresholds()


class AcutePainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(AcutePainMetricGenerator, self).__init__("Acute Pain", MetricType.daily,
                                                       soreness_list, "average_severity")

        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.seek_med_eval_to_clear_for_training,
                                                     "Significant pain or soreness reported: consult medical staff, consider not training",
                                                     ["5A", "2A"], 3.0, 5.01,
                                                     "Severe {bodypart} pain for several days",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                     "Modify intensity, movements & drills to prevent severe pain & soreness from worsening",
                                                     ["5A", "2A"], 2.0, 3.0,
                                                     "Moderate {bodypart} pain for several days",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     DailyHighLevelInsight.monitor_modify_if_needed,
                                                     "Modify training if pain increases. Prioritize recovery to prevent development of injury",
                                                     ["6A", "7B"], 1.0, 2.0,
                                                     "Mild {bodypart} pain for several days which may worsen if not managed appropriately",
                                                     None)

        self.populate_thresholds_with_soreness()


class DailySorenessMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(DailySorenessMetricGenerator, self).__init__("Daily Soreness", MetricType.daily,
                                                           soreness_list, "severity")
        self.high_level_action_description = ""
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.seek_med_eval_to_clear_for_training,
                                                     "Significant pain or soreness reported: consult medical staff, consider not training",
                                                     ["5A", "2A"], 5.0, 5.01,
                                                     "Severe {bodypart} soreness today",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                     "Modify intensity, movements & drills to prevent severe pain & soreness from worsening",
                                                     ["2B", "7A", "6B"], 4.0, 5.0,
                                                     "Moderate {bodypart} soreness today",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_modify_if_needed,
                                                     "Modify training if pain increases. Prioritize recovery to prevent development of injury",
                                                     ["6A", "7A"], 2.0, 4.0,
                                                     "Mild {bodypart} soreness today",
                                                     None)
        self.populate_thresholds_with_soreness()


class DailyPainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(DailyPainMetricGenerator, self).__init__("Daily Pain", MetricType.daily,
                                                       soreness_list, "severity")

        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.seek_med_eval_to_clear_for_training,
                                                     "Significant pain or soreness reported: consult medical staff, consider not training",
                                                     ["5A", "2A"], 4.0, 5.01,
                                                     "Severe {bodypart} pain today",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.adapt_training_to_avoid_symptoms,
                                                     "Modify intensity, movements & drills to prevent severe pain & soreness from worsening",
                                                     ["2B", "7B", "6A"], 3.0, 4.0,
                                                     "Moderate {bodypart} pain today",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_modify_if_needed,
                                                     "Modify training if pain increases. Prioritize recovery to prevent development of injury",
                                                     ["6A", "7A", "9A"], 2.0, 3.0,
                                                     "Mild {bodypart} pain today",
                                                     None)
        self.populate_thresholds_with_soreness()


class PersistentSorenessMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(PersistentSorenessMetricGenerator, self).__init__("Persistent (Recurring) Soreness", MetricType.longitudinal,
                                                                soreness_list, "average_severity")
        self.high_level_action_description = "Modify intensity, movements & drills to avoid aggravating areas of severe pain & soreness"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                                                     self.high_level_action_description,
                                                     ["7A"], 4.0, 5.01,
                                                     "Persistent, {bodypart} soreness which increases soft tissue injury risk if high loads occur during periods of soreness.",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                                                     self.high_level_action_description,
                                                     ["7A","6C","3B"], 3.0, 4.0,
                                                     "Persistent, {bodypart} soreness which increases soft tissue injury risk if high loads occur during periods of soreness.",
                                                     None)
        self.populate_thresholds_with_soreness()


class Persistent_2SorenessMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(Persistent_2SorenessMetricGenerator, self).__init__("Persistent-2 (Constant) Soreness", MetricType.longitudinal,
                                                                  soreness_list, "average_severity")

        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     WeeklyHighLevelInsight.seek_med_eval_to_clear_for_training,
                                                     "Significant pain or soreness reported: consult medical staff before considering training",
                                                     ["3B", "7A"], 4.0, 5.01,
                                                     "Persistent, {bodypart} soreness which increases soft tissue injury risk if high loads occur during periods of soreness.",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                                                     "Consider reducing training intensity to lower risk of severe soreness developing into injury",
                                                     ["7A", "6C", "3B"], 2.0, 4.0,
                                                     "Persistent, {bodypart} soreness which increases soft tissue injury risk if high loads occur during periods of soreness.",
                                                     None)

        self.populate_thresholds_with_soreness()


class PersistentPainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(PersistentPainMetricGenerator, self).__init__("Persistent (Recurring) Pain", MetricType.longitudinal,
                                                            soreness_list, "average_severity")
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     WeeklyHighLevelInsight.seek_med_eval_to_clear_for_training,
                                                     "Significant pain or soreness reported: consult medical staff before considering training",
                                                     ["5A", "2A", "3A"], 4.0, 5.01,
                                                     "Persistent Severe {bodypart} pain",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                                                     "Modify intensity, movements & drills to avoid aggravating areas of severe pain & soreness",
                                                     ["6B", "7A", "3B"], 2.0, 4.0,
                                                     "Persistent Moderate {bodypart} pain",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                                                     "Modify intensity, movements & drills to avoid aggravating areas of severe pain & soreness",
                                                     ["7A"], 1.0, 2.0,
                                                     "Persistent Mild {bodypart} pain which may worsen if not managed appropriately",
                                                     None)
        self.populate_thresholds_with_soreness()


class Persistent_2PainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(Persistent_2PainMetricGenerator, self).__init__("Persistent-2 (Constant) Pain", MetricType.longitudinal,
                                                              soreness_list, "average_severity")
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     WeeklyHighLevelInsight.seek_med_eval_to_clear_for_training,
                                                     "Significant pain or soreness reported: consult medical staff before considering training",
                                                     ["5A", "2A", "3A"], 4.0, 5.01,
                                                     "Persistent Severe {bodypart} pain",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                                                     "Modify intensity, movements & drills to avoid aggravating areas of severe pain & soreness",
                                                     ["6B", "7A", "3B"], 2.0, 4.0,
                                                     "Persistent Moderate {bodypart} pain",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.at_risk_of_time_loss_injury,
                                                     "Modify intensity, movements & drills to avoid aggravating areas of severe pain & soreness",
                                                     ["7A"], 1.0, 2.0,
                                                     "Persistent Mild {bodypart} pain which may worsen if not managed appropriately",
                                                     None)
        self.populate_thresholds_with_soreness()
