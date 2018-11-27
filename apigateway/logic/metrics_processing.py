from models.metrics import AthleteMetric, DailyHighLevelInsight, MetricType, WeeklyHighLevelInsight
from models.soreness import HistoricSorenessStatus


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
                    met.color = "Red"

                elif 6.0 <= athlete_stats.session_RPE < 8.0:
                    met.color = "Yellow"

                metrics.append(met)

        if (athlete_stats.daily_severe_soreness is not None and len(athlete_stats.daily_severe_soreness) > 0
                and athlete_stats.daily_severe_soreness_event_date == event_date):

            met_dict = {}

            for t in athlete_stats.daily_severe_soreness:
                if t.severity >= 3.0:

                    met = AthleteMetric("Daily Severe Soreness", MetricType.daily)
                    met.color = "Yellow"
                    met.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"

                    if 3.0 <= athlete_stats.daily_severe_soreness < 4.0:
                        if 0 not in met_dict:
                            met.high_level_insight = DailyHighLevelInsight.monitor_in_training
                            met.specific_insight_recovery = "Elevated [body part] soreness which may impact performance"
                            met.specific_insight_training_volume = ""
                            met.specific_actions.append("6A")
                            met.specific_actions.append("7A")

                            met_dict[0] = met
                        else:
                            met_dict[0].soreness.append(t)

                    elif athlete_stats.daily_severe_soreness >= 4.0:
                        if 1 not in met_dict:
                            met.high_level_insight = DailyHighLevelInsight.limit_time_intensity_of_training

                            met.specific_insight_recovery = ("Severe [bodypart/global] soreness on for the last " + str(t.streak) + " reported days may impact performance & indicate elevated injury risk")
                            met.specific_insight_training_volume = ""
                            met.specific_actions.append("2B")
                            met.specific_actions.append("7A")
                            met.specific_actions.append("6B")
                            met_dict[1] = met
                        else:
                            met_dict[0].soreness.append(t)

            for k, v in met_dict:
                metrics.append(v)

        if (athlete_stats.daily_severe_pain is not None and len(athlete_stats.daily_severe_pain) > 0
                and athlete_stats.daily_severe_pain == event_date):

            met_dict = {}

            for t in athlete_stats.daily_severe_pain:

                rec = AthleteMetric("Daily Severe Pain", MetricType.daily)
                rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"

                if athlete_stats.daily_severe_pain <= 2.0:
                    if 0 not in met_dict:

                        rec.color = "Yellow"
                        rec.high_level_insight = DailyHighLevelInsight.monitor_in_training
                        rec.specific_insight_recovery = ("Low severity [body part] pain which should be monitored to prevent the development of injury")
                        rec.specific_insight_training_volume = ""
                        rec.specific_actions.append("6A")
                        rec.specific_actions.append("7A")

                        met_dict[0] = rec

                    else:
                        met_dict[0].soreness.append(t)

                elif 2.0 < athlete_stats.daily_severe_pain < 4.0:
                    if 1 not in met_dict:

                        rec.color = "Yellow"
                        rec.high_level_insight = DailyHighLevelInsight.limit_time_intensity_of_training
                        rec.specific_insight_recovery = "Elevated [body part] pain which should be monitored to prevent injury"
                        rec.specific_insight_training_volume = ""
                        rec.specific_actions.append("2B")
                        rec.specific_actions.append("7B")
                        rec.specific_actions.append("6A")

                        met_dict[0] = rec

                    else:
                        met_dict[0].soreness.append(t)

                elif athlete_stats.daily_severe_pain >= 4.0:
                    if 2 not in met_dict:

                        rec.color = "Red"
                        rec.high_level_insight = DailyHighLevelInsight.not_cleared_for_training
                        rec.specific_insight_recovery = "[body part] pain severity that is too high to train today and may indicate injury"
                        rec.specific_insight_training_volume = ""
                        rec.specific_actions.append("5A")
                        rec.specific_actions.append("2A")

                        met_dict[0] = rec

                    else:
                        met_dict[0].soreness.append(t)

            for k, v in met_dict:
                metrics.append(v)

        met_dict = {}

        for t in athlete_stats.historic_soreness:
            if t.streak >= 3 and t.is_pain:

                rec = AthleteMetric("3 Day Consecutive Pain", MetricType.daily)

                if t.average_severity >= 3:
                    if 1 not in met_dict:
                        rec.color = "Red"
                        rec.high_level_insight = DailyHighLevelInsight.not_cleared_for_training
                        rec.high_level_action_description = "Pain severity is too high for training today, consult medical staff to evaluate status"
                        rec.specific_insight_recovery = "Consistent reports of significant [Body Part] pain for the last " + str(t.streak) + " days may be a sign of injury"
                        rec.specific_actions.append("5A")
                        rec.specific_actions.append("2A")

                        met_dict[1] = rec
                    else:
                        met_dict[1].soreness.append(t)
                else:
                    if 0 not in met_dict:
                        rec.color = "Yellow"
                        rec.high_level_insight = DailyHighLevelInsight.monitor_in_training
                        rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
                        rec.specific_insight_recovery = "Consistent reports of significant [Body Part] pain for the last " + str(t.streak) + " days may be a sign of injury"
                        rec.specific_actions.append("6A")
                        rec.specific_actions.append("7B")

                        met_dict[0] = rec
                    else:
                        met_dict[0].soreness.append(t)

        for k, v in met_dict:
            metrics.append(v)

        met_dict = {}

        for t in athlete_stats.historic_soreness:
            if t.historic_soreness_status == HistoricSorenessStatus.persistent and not t.is_pain:

                rec = AthleteMetric("Persistent Soreness", MetricType.longitudinal)

                rec.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"

                if t.average_severity>= 4:
                    if 2 not in met_dict:
                        rec.color = "Yellow"
                        rec.high_level_action_description = "Consult medical staff to evaluate status before training"
                        rec.high_level_insight = WeeklyHighLevelInsight.evaluate_health_status
                        rec.specific_insight_recovery = "a "+ str(t.streak) + " day trend of persistent, severe [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")

                        met_dict[2] = rec
                    else:
                        met_dict[2].soreness.append(t)

                elif 2 < t.average_severity < 4:
                    if 1 not in met_dict:
                        rec.color = "Yellow"
                        rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, moderate [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("6C")
                        rec.specific_actions.append("3B")

                        met_dict[1] = rec
                    else:
                        met_dict[1].soreness.append(t)

                else:
                    if 0 not in met_dict:
                        rec.color = "Green"
                        rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, mild [body part] soreness impacting performance & indicating elevated injury risk"
                        # NONE

                        met_dict[0] = rec
                    else:
                        met_dict[0].soreness.append(t)

        for k, v in met_dict:
            metrics.append(v)

        met_dict = {}

        for t in athlete_stats.historic_soreness:

            if t.historic_soreness_status == HistoricSorenessStatus.chronic and not t.is_pain:
                rec = AthleteMetric("Chronic Soreness", MetricType.longitudinal)

                rec.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"

                if t.average_severity >= 4:
                    if 2 not in met_dict:
                        rec.color = "Yellow"
                        rec.high_level_insight = WeeklyHighLevelInsight.evaluate_health_status
                        rec.specific_insight_recovery = "a "+ str(t.streak) + " day trend of chronic, severe [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("3B")
                        rec.specific_actions.append("7A")
                        met_dict[2] = rec

                    else:
                        met_dict[2].soreness.append(t)

                elif 2 < t.average_severity < 4:
                    if 1 not in met_dict:
                        rec.color = "Yellow"
                        rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, moderate [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("6C")
                        rec.specific_actions.append("3B")
                        met_dict[1] = rec

                    else:
                        met_dict[1].soreness.append(t)
                else:
                    if 0 not in met_dict:
                        rec.color = "Green"
                        rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, mild [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        met_dict[0] = rec

                    else:
                        met_dict[0].soreness.append(t)

        for k, v in met_dict:
            metrics.append(v)

        met_dict = {}

        for t in athlete_stats.historic_soreness:
            if t.historic_soreness_status == HistoricSorenessStatus.persistent and t.is_pain:

                rec = AthleteMetric("Persistent Pain", MetricType.longitudinal)

                rec.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
                if t.average_severity >= 4:
                    if 2 not in met_dict:
                        rec.color = "Red"
                        rec.high_level_insight = WeeklyHighLevelInsight.evaluate_health_status
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, severe [body part] pain which may indicate injury"
                        rec.specific_actions.append("5A")
                        rec.specific_actions.append("2A")
                        rec.specific_actions.append("3A")
                        met_dict[2] = rec

                    else:
                        met_dict[2].soreness.append(t)

                elif 2 < t.average_severity < 4:
                    if 1 not in met_dict:
                        rec.color = "Yellow"
                        rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, moderate [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("6B")
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("3B")
                        met_dict[1] = rec

                    else:
                        met_dict[1].soreness.append(t)

                else:
                    if 0 not in met_dict:
                        rec.color = "Green"
                        rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, mild [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        met_dict[0] = rec

                    else:
                        met_dict[0].soreness.append(t)

        for k, v in met_dict:
            metrics.append(v)

        met_dict = {}

        for t in athlete_stats.historic_soreness:
            if t.historic_soreness_status == HistoricSorenessStatus.chronic and t.is_pain:

                rec = AthleteMetric("Chronic Pain", MetricType.longitudinal)

                rec.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
                if t.average_severity >= 4:
                    if 2 not in met_dict:
                        rec.color = "Red"
                        rec.high_level_insight = WeeklyHighLevelInsight.evaluate_health_status
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, severe [body part] pain may indicate injury"
                        rec.specific_actions.append("5A")
                        rec.specific_actions.append("2A")
                        rec.specific_actions.append("3A")
                        met_dict[2] = rec

                    else:
                        met_dict[2].soreness.append(t)

                elif 2 < t.average_severity < 4:
                    if 1 not in met_dict:
                        rec.color = "Yellow"
                        rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, moderate [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("6B")
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("3B")
                        met_dict[1] = rec

                    else:
                        met_dict[1].soreness.append(t)

                else:
                    if 0 not in met_dict:
                        rec.color = "Green"
                        rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, mild [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("6C")

                        met_dict[0] = rec

                    else:
                        met_dict[0].soreness.append(t)

        for k, v in met_dict:
            metrics.append(v)

        return metrics