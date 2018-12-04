from models.metrics import AthleteMetric, AthleteSorenessMetricGenerator, AthleteTrainingVolumeMetricGenerator, DailyHighLevelInsight, MetricColor, MetricType, ThresholdRecommendation, WeeklyHighLevelInsight
from models.soreness import HistoricSorenessStatus

class MetricsProcessing(object):

    def get_athlete_metrics_from_stats(self, athlete_stats, event_date):

        metrics = []

        if athlete_stats.session_RPE_event_date == event_date:
            metrics.extend(DailySessionRPEMetricGenerator(athlete_stats, athlete_stats.session_RPE_event_date).get_metric_list())

        if athlete_stats.daily_severe_soreness_event_date == event_date:
            metrics.extend(DailySevereSorenessMetricGenerator(athlete_stats.daily_severe_soreness).get_metric_list())

        if athlete_stats.daily_severe_pain_event_date == event_date:
            metrics.extend(DailySeverePainMetricGenerator(athlete_stats.daily_severe_pain).get_metric_list())

        # pain_list = list(p for p in athlete_stats.historic_soreness if p.is_pain and p.streak >= 3)
        # metrics.extend(ThreeDayConsecutivePainMetricGenerator(pain_list).get_metric_list())

        ps_list = list(p for p in athlete_stats.historic_soreness if not p.is_pain and p.historic_soreness_status ==
                         HistoricSorenessStatus.persistent)
        metrics.extend(PersistentSorenessMetricGenerator(ps_list).get_metric_list())

        cs_list = list(p for p in athlete_stats.historic_soreness if not p.is_pain and p.historic_soreness_status ==
                       HistoricSorenessStatus.persistent_2)

        metrics.extend(Persistent_2SorenessMetricGenerator(cs_list).get_metric_list())

        pp_list = list(p for p in athlete_stats.historic_soreness if p.is_pain and p.historic_soreness_status ==
                       HistoricSorenessStatus.persistent)

        metrics.extend(PersistentPainMetricGenerator(pp_list).get_metric_list())

        cp_list = list(p for p in athlete_stats.historic_soreness if p.is_pain and p.historic_soreness_status ==
                       HistoricSorenessStatus.persistent_2)

        metrics.extend(ChronicPainMetricGenerator(cp_list).get_metric_list())

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

        for m in range(0, len(self.metrics)):
            for a in range(0, len(self.metrics[m].specific_actions)):
                if self.metrics[m].specific_actions[a].code in winners:
                    self.metrics[m].specific_actions[a].display = True
                else:
                    self.metrics[m].specific_actions[a].display = False
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
                                                     "Elevated {bodypart} soreness which may impact performance",
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
                                                     "{bodypart} pain severity that is too high to train today and may indicate injury",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.limit_time_intensity_of_training,
                                                     self.high_level_action_description,
                                                     ["2B", "7A", "6B"], 2.0, 4.0,
                                                     "Elevated {bodypart} pain which should be monitored to prevent injury",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     self.high_level_action_description,
                                                     ["6A", "7A"], 1.0, 2.0,
                                                     "Low severity {bodypart} pain which should be monitored to prevent the development of injury",
                                                     None)
        self.populate_thresholds_with_soreness()


class ThreeDayConsecutivePainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(ThreeDayConsecutivePainMetricGenerator, self).__init__("3 Day Consecutive Pain", MetricType.daily,
                                                                     soreness_list, "average_severity")
        self.high_level_action_description = ""
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.not_cleared_for_training,
                                                     "Pain severity is too high for training today, consult medical staff to evaluate status",
                                                     ["5A", "2A"], 3.0, None,
                                                     "Consistent reports of significant {bodypart} pain which may be a sign of injury",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     "Stop training if pain increases and consider reducing workload to facilitate recovery",
                                                     ["6A", "7B"], 1.0, 3.0,
                                                     "Consistent reports of {bodypart} pain which may be a sign of injury",
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
                                                     "Persistent, severe {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", "3B"], 2.0, 4.0,
                                                     "Persistent, moderate {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 2.0,
                                                     "Persistent, mild {bodypart} soreness which may impact performance",
                                                     None)
        self.populate_thresholds_with_soreness()


class Persistent_2SorenessMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(Persistent_2SorenessMetricGenerator, self).__init__("Chronic Soreness", MetricType.longitudinal,
                                                                  soreness_list, "average_severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     self.high_level_action_description,
                                                     ["3B", "7A"], 4.0, None,
                                                     "Chronic, severe {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", "3B"], 2.0, 4.0,
                                                     "Chronic, moderate {bodypart} soreness which may impact performance & indicate elevated injury risk",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 2.0,
                                                     "Chronic, mild {bodypart} soreness which may impact performance",
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
                                                     "Persistent, severe {bodypart} pain which may indicate injury",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["6B", "7A", "3B"], 1.0, 4.0,
                                                     "Persistent, moderate {bodypart} pain which should be monitored to prevent injury",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 1.0,
                                                     "Persistent, mild {bodypart} pain which should be monitored to prevent the development of injury",
                                                     None)
        self.populate_thresholds_with_soreness()


class ChronicPainMetricGenerator(AthleteSorenessMetricGenerator):
    def __init__(self, soreness_list):
        super(ChronicPainMetricGenerator, self).__init__("Chronic Pain", MetricType.longitudinal,
                                                         soreness_list, "average_severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     self.high_level_action_description,
                                                     ["5A", "2A", "3A"], 4.0, None,
                                                     "Chronic, severe {bodypart} pain which may indicate injury",
                                                     None)
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["6B", "7A", "3B"], 1.0, 4.0,
                                                     "Chronic, moderate {bodypart} pain which should be monitored to prevent injury",
                                                     None)
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", ], None, 1.0,
                                                     "Chronic, mild {bodypart} pain which should be monitored to prevent the development of injury",
                                                     None)
        self.populate_thresholds_with_soreness()
