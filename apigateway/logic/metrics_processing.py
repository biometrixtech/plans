from models.metrics import AthleteMetric, AthleteSorenessMetricGenerator, AthleteTrainingVolumeMetricGenerator, DailyHighLevelInsight, MetricColor, MetricType, ThresholdRecommendation, WeeklyHighLevelInsight
from models.soreness import HistoricSorenessStatus

class MetricsProcessing(object):

    def get_athlete_metrics_from_stats(self, athlete_stats, event_date):

        metrics = []

        if athlete_stats.session_RPE_event_date == event_date:
            metrics.extend(DailySessionRPEMetricGenerator(athlete_stats, athlete_stats.session_RPE_event_date).get_metric_list())

        if athlete_stats.event_date == event_date:
            metrics.extend(IncreasingIACWRGenerator(athlete_stats).get_metric_list())
            metrics.extend(IncreasingInternalRampGenerator(athlete_stats).get_metric_list())
            metrics.extend(InternalMonotonyEventGenerator(athlete_stats).get_metric_list())
            metrics.extend(InternalStrainEventsGenerator(athlete_stats).get_metric_list())
            metrics.extend(DecreasingIACWRGenerator(athlete_stats).get_metric_list())

        if athlete_stats.daily_severe_soreness_event_date == event_date:
            metrics.extend(DailySevereSorenessMetricGenerator(athlete_stats.daily_severe_soreness).get_metric_list())

        if athlete_stats.daily_severe_pain_event_date == event_date:
            metrics.extend(DailySeverePainMetricGenerator(athlete_stats.daily_severe_pain).get_metric_list())

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
        self.high_level_action_description = "Shorten training or limit intensity and focus on recovery modalities"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.limit_time_intensity_of_training,
                                                     self.high_level_action_description,
                                                     ["2B", "7A"], 8.0, None, None,
                                                     "A spike in workload on "+session_rpe_event_date+" which should be countered with a recovery day soon for optimal recovery and gains"
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.limit_time_intensity_of_training,
                                                     self.high_level_action_description,
                                                     ["2B", "7A"], 6.0, 8.0, None,
                                                     "A spike in workload on "+session_rpe_event_date+" which should be countered with a recovery day soon for optimal recovery and gains"
                                                     )
        self.populate_thresholds()


class IncreasingIACWRGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(IncreasingIACWRGenerator, self).__init__("Increasing IACWR", MetricType.longitudinal,
                                                             athlete_stats, "internal_acwr")
        self.high_level_action_description = "Consider decreasing workload this week or prioritizing holistic recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.at_risk_of_overtraining,
                                                     self.high_level_action_description,
                                                     ["3A", "7A"], 1.5, None, None,
                                                     "Workload increasing at a high risk of injury."
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.at_risk_of_overtraining,
                                                     self.high_level_action_description,
                                                     ["3B", "7A"], 1.3, 1.5, None,
                                                     "Workload increasing at a moderate risk of injury."
                                                     )
        self.populate_thresholds()


class IncreasingInternalRampGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(IncreasingInternalRampGenerator, self).__init__("Increasing Internal Ramp", MetricType.longitudinal,
                                                             athlete_stats, "internal_ramp")
        self.high_level_action_description = "Consider decreasing workload this week or prioritizing holistic recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.at_risk_of_overtraining,
                                                     self.high_level_action_description,
                                                     ["3A", "7A"], 1.15, None, None,
                                                     "Workload increasing at a high risk of injury."
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.at_risk_of_overtraining,
                                                     self.high_level_action_description,
                                                     ["3B", "7A"], 1.11, 1.15, None,
                                                     "Workload increasing at a moderate risk of injury."
                                                     )
        self.populate_thresholds()


class InternalStrainEventsGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(InternalStrainEventsGenerator, self).__init__("Internal Strain Events", MetricType.longitudinal,
                                                             athlete_stats, "internal_strain_events")
        self.high_level_action_description = "ncrease variety in training duration & intensity, prioritize holistic recovery"
        self.high_level_extended_description = "Low variety in training duration & intensity raises cortoisol & inhibits recovery. Increase training variability & prioritize holistic recovery."
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.needs_workload_variability,
                                                     self.high_level_action_description,
                                                     ["1A", "7A"], 2, None, None,
                                                     "Very low training variability & high loads which increase risk of minor injury"
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.needs_workload_variability,
                                                     self.high_level_action_description,
                                                     ["1B", "7A"], 1, 1, None,
                                                     "Very low training variability & high loads which increase risk of minor injury"
                                                     )
        self.thresholds[0].high_level_extended_description = self.high_level_extended_description
        self.thresholds[1].high_level_extended_description = self.high_level_extended_description
        self.populate_thresholds()


class InternalMonotonyEventGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(InternalMonotonyEventGenerator, self).__init__("Internal Monotony event", MetricType.longitudinal,
                                                             athlete_stats, "historical_internal_monotony")
        self.high_level_action_description = "Increase variety in training duration & intensity, prioritize holistic recovery"
        self.high_level_extended_description = "Low variety in training duration & intensity raises cortoisol & inhibits recovery. Increase training variability & prioritize holistic recovery."
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.needs_workload_variability,
                                                     self.high_level_action_description,
                                                     ["1A", "7A"], 2.0, None, None,
                                                     "Very low variability in workloads which inhibits natural recovery ability"
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.needs_workload_variability,
                                                     self.high_level_action_description,
                                                     ["1B", "7A"], 1.6, 1.99, None,
                                                     "Very low variability in workloads which inhibits natural recovery ability"
                                                     )
        self.thresholds[0].high_level_extended_description = self.high_level_extended_description
        self.thresholds[1].high_level_extended_description = self.high_level_extended_description
        self.populate_thresholds()


class DecreasingIACWRGenerator(AthleteTrainingVolumeMetricGenerator):
    def __init__(self, athlete_stats):
        super(DecreasingIACWRGenerator, self).__init__("Decreasing IACWR", MetricType.longitudinal,
                                                             athlete_stats, "internal_acwr")
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.needs_higher_weekly_workload,
                                                     "Increase this week's load with a longer or higher intensity session or add supplemental session",
                                                     ["3C", "7A"], None, 0.5, None,
                                                     "Workload decreasing at a very significant rate. This is associated with an increased risk of injury"
                                                     )
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.needs_higher_weekly_workload,
                                                     "If tapering is unintentional, increase this week's load to reduce undertraining",
                                                     ["3C", "7A"], 0.51, 0.8, None,
                                                     "Workload decreasing at a significant rate. If unintentional, this can increase risk of injury."
                                                     )
        self.populate_thresholds()


class DailySevereSorenessMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(DailySevereSorenessMetricGenerator, self).__init__("Daily Severe Soreness", MetricType.daily,
                                                                 soreness_list, "severity")
        self.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.limit_time_intensity_of_training,
                                                     self.high_level_action_description,
                                                     ["2B", "7A", "6B"], 4.0, None,
                                                     "Severe {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     self.high_level_action_description,
                                                     ["6A", "7A"], 3.0, 4.0,
                                                     "Moderate {bodypart} soreness which may impact performance",
                                                     None)
        self.populate_thresholds_with_soreness()


class DailySeverePainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(DailySeverePainMetricGenerator, self).__init__("Daily Severe Pain", MetricType.daily,
                                                             soreness_list, "severity")
        self.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.not_cleared_for_training,
                                                     self.high_level_action_description,
                                                     ["5A", "2A"], 4.0, None,
                                                     "Severe {bodypart} pain that is too high to train today and may indicate injury",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.limit_time_intensity_of_training,
                                                     self.high_level_action_description,
                                                     ["2B", "7A", "6B"], 2.0, 4.0,
                                                     "Moderate {bodypart} pain which should be monitored to prevent injury",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     self.high_level_action_description,
                                                     ["6A", "7A"], 1.0, 2.0,
                                                     "Mild {bodypart} pain which should be monitored to prevent the development of injury",
                                                     None)
        self.populate_thresholds_with_soreness()


class AcutePainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(AcutePainMetricGenerator, self).__init__("Acute Pain", MetricType.daily,
                                                       soreness_list, "average_severity")
        self.high_level_action_description = ""
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.not_cleared_for_training,
                                                     "Pain severity is too high for training today, consult medical staff to evaluate status",
                                                     ["5A", "2A"], 4.0, None,
                                                     "Consistent severe {bodypart} pain that is too high to train today and may indicate injury",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     "Pain severity is too high for training today, consult medical staff to evaluate status",
                                                     ["6A", "7B"], 3.0, 4.0,
                                                     "Consistent reports of moderate {bodypart} pain which may be a sign of injury",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     "Stop training if pain increases and consider reducing workload to facilitate recovery",
                                                     ["6A", "7B"], 1.0, 3.0,
                                                     "Consistent reports of mild {bodypart} pain which may be a sign of injury",
                                                     None)

        self.populate_thresholds_with_soreness()


class PersistentSorenessMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(PersistentSorenessMetricGenerator, self).__init__("Persistent Soreness", MetricType.longitudinal,
                                                                soreness_list, "average_severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     "Consult medical staff to evaluate status before training",
                                                     ["7A"], 4.0, None,
                                                     "Severe, recurring {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", "3B"], 2.0, 4.0,
                                                     "Moderate, recurring {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 2.0,
                                                     "Mild, recurring {bodypart} soreness which may impact performance",
                                                     None)
        self.populate_thresholds_with_soreness()


class Persistent_2SorenessMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(Persistent_2SorenessMetricGenerator, self).__init__("Persistent-2 Soreness", MetricType.longitudinal,
                                                                  soreness_list, "average_severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     self.high_level_action_description,
                                                     ["3B", "7A"], 4.0, None,
                                                     "Severe, constant {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", "3B"], 2.0, 4.0,
                                                     "Moderate, constant {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 2.0,
                                                     "Mild, constant {bodypart} soreness which may impact performance",
                                                     None)
        self.populate_thresholds_with_soreness()


class PersistentPainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(PersistentPainMetricGenerator, self).__init__("Persistent Pain", MetricType.longitudinal,
                                                            soreness_list, "average_severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     self.high_level_action_description,
                                                     ["5A", "2A", "3A"], 4.0, None,
                                                     "Severe, recurring {bodypart} pain which may indicate injury",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["6B", "7A", "3B"], 1.0, 4.0,
                                                     "Moderate, recurring {bodypart} pain which should be monitored to prevent injury",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 1.0,
                                                     "Mild, recurring {bodypart} pain which should be monitored to prevent the development of injury",
                                                     None)
        self.populate_thresholds_with_soreness()


class Persistent_2PainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(Persistent_2PainMetricGenerator, self).__init__("Persistent-2 Pain", MetricType.longitudinal,
                                                              soreness_list, "average_severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     self.high_level_action_description,
                                                     ["5A", "2A", "3A"], 4.0, None,
                                                     "Severe, constant {bodypart} pain which may indicate injury",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["6B", "7A", "3B"], 1.0, 4.0,
                                                     "Moderate, constant {bodypart} pain which should be monitored to prevent injury",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", ], None, 1.0,
                                                     "Mild, constant {bodypart} pain which should be monitored to prevent the development of injury",
                                                     None)
        self.populate_thresholds_with_soreness()
