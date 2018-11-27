from models.metrics import AthleteMetric, AthleteMetricGenerator, DailyHighLevelInsight, MetricColor, MetricType, ThresholdRecommendation, WeeklyHighLevelInsight


class MetricsProcessing(object):

    def get_athlete_metrics_from_stats(self, athlete_stats, event_date):

        metrics = []

        if athlete_stats.session_RPE is not None and athlete_stats.session_RPE_event_date == event_date:
            if athlete_stats.session_RPE >= 5.0:
                met = AthleteMetric("Session RPE", MetricType.daily)
                met.high_level_insight = DailyHighLevelInsight.limit_time_intensity_of_training
                met.high_level_action_description = "Shorten training or limit intensity and focus on recovery modalities"
                met.specific_insight_recovery = ""
                met.specific_insight_training_volume = (
                            "A spike in workload on " + athlete_stats.session_RPE_event_date +
                            " which should be countered with a recovery day soon for optimal " +
                            "recovery and gains")
                met.specific_actions.append("2B")
                met.specific_actions.append("7A")

                if athlete_stats.session_RPE >= 8.0:
                    met.color = MetricColor.red

                elif 6.0 <= athlete_stats.session_RPE < 8.0:
                    met.color = MetricColor.yellow

                metrics.append(met)

        if athlete_stats.daily_severe_soreness_event_date == event_date:
            metrics.extend(DailySevereSorenessMetricGenerator(athlete_stats.daily_severe_soreness).get_metric_list())

        if athlete_stats.daily_severe_pain_event_date == event_date:
            metrics.extend(DailySeverePainMetricGenerator(athlete_stats.daily_severe_pain).get_metric_list())

        pain_list = list(p for p in athlete_stats.historic_soreness if p.is_pain and p.streak >= 3)
        metrics.extend(ThreeDayConsecutivePainMetricGenerator(pain_list).get_metric_list())

        metrics.extend(PersistentSorenessMetricGenerator(athlete_stats.historic_soreness).get_metric_list())
        metrics.extend(ChronicSorenessMetricGenerator(athlete_stats.historic_soreness).get_metric_list())
        metrics.extend(PersistentPainMetricGenerator(athlete_stats.historic_soreness).get_metric_list())
        metrics.extend(ChronicPainMetricGenerator(athlete_stats.historic_soreness).get_metric_list())

        return metrics


class DailySevereSorenessMetricGenerator(AthleteMetricGenerator):
    def __init__(self, soreness_list):
        super(DailySevereSorenessMetricGenerator, self).__init__("Daily Severe Soreness", MetricType.daily,
                                                                 soreness_list, "severity")
        self.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.limit_time_intensity_of_training,
                                                     self.high_level_action_description,
                                                     ["2B", "7A", "6B"], 4.0, None,
                                                     "Severe [bodypart] soreness which may impact performance & indicate elevated injury risk")
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     self.high_level_action_description,
                                                     ["6A", "7A"], 3.0, 4.0,
                                                     "Elevated [bodypart] soreness which may impact performance")
        self.populate_thresholds_with_soreness()


class DailySeverePainMetricGenerator(AthleteMetricGenerator):
    def __init__(self, soreness_list):
        super(DailySeverePainMetricGenerator, self).__init__("Daily Severe Pain", MetricType.daily,
                                                             soreness_list, "severity")
        self.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.not_cleared_for_training,
                                                     self.high_level_action_description,
                                                     ["5A", "2A"], 4.0, None,
                                                     "[bodypart] pain severity that is too high to train today and may indicate injury")
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.limit_time_intensity_of_training,
                                                     self.high_level_action_description,
                                                     ["2B", "7A", "6B"], 2.0, 4.0,
                                                     "Elevated [bodypart] pain which should be monitored to prevent injury")
        self.thresholds[2] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     self.high_level_action_description,
                                                     ["6A", "7A"], 1.0, 2.0,
                                                     "Low severity [bodypart] pain which should be monitored to prevent the development of injury")
        self.populate_thresholds_with_soreness()


class ThreeDayConsecutivePainMetricGenerator(AthleteMetricGenerator):
    def __init__(self, soreness_list):
        super(ThreeDayConsecutivePainMetricGenerator, self).__init__("3 Day Consecutive Pain", MetricType.daily,
                                                                     soreness_list, "severity")
        self.high_level_action_description = ""
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     DailyHighLevelInsight.not_cleared_for_training,
                                                     "Pain severity is too high for training today, consult medical staff to evaluate status",
                                                     ["5A", "2A"], 3.0, None,
                                                     "Consistent reports of significant [bodypart] pain which may be a sign of injury")
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     DailyHighLevelInsight.monitor_in_training,
                                                     "Stop training if pain increases and consider reducing workload to facilitate recovery",
                                                     ["6A", "7B"], 1.0, 3.0,
                                                     "Consistent reports of [bodypart] pain which may be a sign of injury")
        self.populate_thresholds_with_soreness()


class PersistentSorenessMetricGenerator(AthleteMetricGenerator):
    def __init__(self, soreness_list):
        super(PersistentSorenessMetricGenerator, self).__init__("Persistent Soreness", MetricType.longitudinal,
                                                                soreness_list, "severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     "Consult medical staff to evaluate status before training",
                                                     ["7A", "9"], 4.0, None,
                                                     "Persistent, severe [bodypart] soreness which may impact performance & indicate elevated injury risk")
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", "3B"], 2.0, 4.0,
                                                     "Persistent, moderate [bodypart] soreness which may impact performance & indicate elevated injury risk")
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 2.0,
                                                     "Persistent, mild [bodypart] soreness which may impact performance")
        self.populate_thresholds_with_soreness()


class ChronicSorenessMetricGenerator(AthleteMetricGenerator):
    def __init__(self, soreness_list):
        super(ChronicSorenessMetricGenerator, self).__init__("Chronic Soreness", MetricType.longitudinal,
                                                             soreness_list, "severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     self.high_level_action_description,
                                                     ["3B", "7A", "9"], 4.0, None,
                                                     "Chronic, severe [bodypart] soreness which may impact performance & indicate elevated injury risk")
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", "3B"], 2.0, 4.0,
                                                     "Chronic, moderate [bodypart] soreness which may impact performance & indicate elevated injury risk")
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 2.0,
                                                     "Chronic, mild [bodypart] soreness which may impact performance")
        self.populate_thresholds_with_soreness()


class PersistentPainMetricGenerator(AthleteMetricGenerator):
    def __init__(self, soreness_list):
        super(PersistentPainMetricGenerator, self).__init__("Persistent Pain", MetricType.longitudinal,
                                                            soreness_list, "severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     self.high_level_action_description,
                                                     ["5A", "2A", "3A"], 4.0, None,
                                                     "Persistent, severe [bodypart] pain which may indicate injury")
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["6B", "7A", "3B"], 1.0, 4.0,
                                                     "Persistent, moderate [bodypart] pain which should be monitored to prevent injury")
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     [], None, 1.0,
                                                     "Persistent, mild [bodypart] pain which should be monitored to prevent the development of injury")
        self.populate_thresholds_with_soreness()


class ChronicPainMetricGenerator(AthleteMetricGenerator):
    def __init__(self, soreness_list):
        super(ChronicPainMetricGenerator, self).__init__("Chronic Pain", MetricType.longitudinal,
                                                         soreness_list, "severity")
        self.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
        self.thresholds[0] = ThresholdRecommendation(MetricColor.red,
                                                     WeeklyHighLevelInsight.evaluate_health_status,
                                                     self.high_level_action_description,
                                                     ["5A", "2A", "3A"], 4.0, None,
                                                     "Chronic, severe [bodypart] pain which may indicate injury")
        self.thresholds[1] = ThresholdRecommendation(MetricColor.yellow,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["6B", "7A", "3B"], 1.0, 4.0,
                                                     "Chronic, moderate [bodypart] pain which should be monitored to prevent injury")
        self.thresholds[2] = ThresholdRecommendation(MetricColor.green,
                                                     WeeklyHighLevelInsight.address_pain_or_soreness,
                                                     self.high_level_action_description,
                                                     ["7A", "6C", ], None, 1.0,
                                                     "Chronic, mild [bodypart] pain which should be monitored to prevent the development of injury")
        self.populate_thresholds_with_soreness()
