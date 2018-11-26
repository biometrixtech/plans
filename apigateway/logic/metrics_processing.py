from models.metrics import AthleteMetric, AthleteRecommendation, DailyHighLevelInsight, MetricType, WeeklyHighLevelInsight
from models.soreness import HistoricSorenessStatus


class MetricsProcessing(object):

    def get_athlete_metrics_from_stats(self, athlete_stats, event_date):

        metrics = []

        if athlete_stats.session_RPE is not None and athlete_stats.session_RPE_event_date == event_date:
            if athlete_stats.session_RPE >= 5.0:
                met = AthleteMetric()
                met.metric_type = MetricType.daily
                met.metric = "Session RPE"
                met.threshold = athlete_stats.session_RPE

                rec = AthleteRecommendation()
                rec.high_level_insight = DailyHighLevelInsight.limit_time_intensity_of_training
                rec.high_level_action_description = "Shorten training or limit intensity and focus on recovery modalities"
                rec.specific_insight_recovery = ""
                rec.specific_insight_training_volume = (
                            "A spike in workload on " + athlete_stats.session_RPE_event_date +
                            " which should be countered with a recovery day soon for optimal " +
                            "recovery and gains")
                rec.specific_actions.append("2B")
                rec.specific_actions.append("7A")

                if athlete_stats.session_RPE >= 8.0:
                    rec.color = "Red"
                    met.recommendations[0] = rec
                elif 6.0 <= athlete_stats.session_RPE < 8.0:
                    rec.color = "Yellow"
                    met.recommendations[1] = rec

                metrics.append(met)

        if (athlete_stats.daily_severe_soreness is not None and len(athlete_stats.daily_severe_soreness) > 0
                and athlete_stats.daily_severe_soreness_event_date == event_date):

            met = AthleteMetric()
            met.metric_type = MetricType.daily
            met.metric = "Daily Severe Soreness"
            # met.threshold = t.severity

            for t in athlete_stats.daily_severe_soreness:
                if t.severity >= 3.0:

                    # rec.body_part_location = t.body_part.location.value
                    # rec.body_part_side = t.side
                    rec = AthleteRecommendation()

                    rec.color = "Yellow"
                    rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"

                    if 3.0 <= athlete_stats.daily_severe_soreness < 4.0 :
                        if 0 not in met.recommendations:
                            rec.high_level_insight = DailyHighLevelInsight.monitor_in_training
                            rec.specific_insight_recovery = "Elevated [body part] soreness which may impact performance"
                            rec.specific_insight_training_volume = ""
                            rec.specific_actions.append("6A")
                            rec.specific_actions.append("7A")

                            met.recommendations[0] = rec
                        else:
                            met.recommendations[0].soreness.append(t)

                    elif athlete_stats.daily_severe_soreness >= 4.0:
                        if 1 not in met.recommendations:
                            rec.high_level_insight = DailyHighLevelInsight.limit_time_intensity_of_training

                            rec.specific_insight_recovery = ("Severe [bodypart/global] soreness on for the last " + str(t.streak) + " reported days may impact performance & indicate elevated injury risk")
                            rec.specific_insight_training_volume = ""
                            rec.specific_actions.append("2B")
                            rec.specific_actions.append("7A")
                            rec.specific_actions.append("6B")
                            met.recommendations[1] = rec
                        else:
                            met.recommendations[0].soreness.append(t)

            if len(met.recommendations) > 0:
                metrics.append(met)

        if (athlete_stats.daily_severe_pain is not None and len(athlete_stats.daily_severe_pain) > 0
                and athlete_stats.daily_severe_pain == event_date):
            met = AthleteMetric()
            met.metric_type = MetricType.daily
            met.metric = "Daily Severe Pain"
            # rec.threshold = t.severity
            # rec.body_part_location = t.body_part.location.value
            # rec.body_part_side = t.side
            # rec.soreness.append(t)

            for t in athlete_stats.daily_severe_pain:

                rec = AthleteRecommendation()
                rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"

                if athlete_stats.daily_severe_pain <= 2.0:
                    if 0 not in met.recommendations:

                        rec.color = "Yellow"
                        rec.high_level_insight = DailyHighLevelInsight.monitor_in_training
                        rec.specific_insight_recovery = ("Low severity [body part] pain which should be monitored to prevent the development of injury")
                        rec.specific_insight_training_volume = ""
                        rec.specific_actions.append("6A")
                        rec.specific_actions.append("7A")

                        met.recommendations[0] = rec

                    else:
                        met.recommendations[0].soreness.append(t)

                elif 2.0 < athlete_stats.daily_severe_pain < 4.0:
                    if 1 not in met.recommendations:

                        rec.color = "Yellow"
                        rec.high_level_insight = DailyHighLevelInsight.limit_time_intensity_of_training
                        rec.specific_insight_recovery = "Elevated [body part] pain which should be monitored to prevent injury"
                        rec.specific_insight_training_volume = ""
                        rec.specific_actions.append("2B")
                        rec.specific_actions.append("7B")
                        rec.specific_actions.append("6A")

                        met.recommendations[0] = rec

                    else:
                        met.recommendations[0].soreness.append(t)

                elif athlete_stats.daily_severe_pain >= 4.0:
                    if 2 not in met.recommendations:

                        rec.color = "Red"
                        rec.high_level_insight = DailyHighLevelInsight.not_cleared_for_training
                        rec.specific_insight_recovery = "[body part] pain severity that is too high to train today and may indicate injury"
                        rec.specific_insight_training_volume = ""
                        rec.specific_actions.append("5A")
                        rec.specific_actions.append("2A")

                        met.recommendations[0] = rec

                    else:
                        met.recommendations[0].soreness.append(t)

            if len(met.recommendations) > 0:
                metrics.append(met)

        met = AthleteMetric()
        met.metric_type = MetricType.daily
        met.metric = "3 Day Consecutive Pain"

        for t in athlete_stats.historic_soreness:
            if t.streak >= 3 and t.is_pain:

                #rec.threshold = t.average_severity
                #rec.body_part_location = t.body_part.location.value
                #rec.body_part_side = t.side
                rec = AthleteRecommendation()
                #rec.soreness.append(t)
                if t.average_severity >= 3:
                    if 1 not in met.recommendations:
                        rec.color = "Red"
                        rec.high_level_insight = DailyHighLevelInsight.not_cleared_for_training
                        rec.high_level_action_description = "Pain severity is too high for training today, consult medical staff to evaluate status"
                        rec.specific_insight_recovery = "Consistent reports of significant [Body Part] pain for the last " + str(t.streak) + " days may be a sign of injury"
                        rec.specific_actions.append("5A")
                        rec.specific_actions.append("2A")

                        met.recommendations[1] = rec
                    else:
                        met.recommendations[1].soreness.append(t)
                else:
                    if 0 not in met.recommendations:
                        rec.color = "Yellow"
                        rec.high_level_insight = DailyHighLevelInsight.monitor_in_training
                        rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
                        rec.specific_insight_recovery = "Consistent reports of significant [Body Part] pain for the last " + str(t.streak) + " days may be a sign of injury"
                        rec.specific_actions.append("6A")
                        rec.specific_actions.append("7B")

                        met.recommendations[0] = rec
                    else:
                        met.recommendations[0].soreness.append(t)

        if len(met.recommendations) > 0:
            metrics.append(met)

        met = AthleteMetric()
        met.metric_type = MetricType.longitudinal
        met.metric = "Persistent Soreness"

        for t in athlete_stats.historic_soreness:
            if t.historic_soreness_status == HistoricSorenessStatus.persistent and not t.is_pain:

                #rec.threshold = t.average_severity
                #rec.body_part_location = t.body_part.location.value
                #rec.body_part_side = t.side
                #rec.soreness.append(t)
                rec = AthleteRecommendation()
                rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                rec.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
                if t.average_severity>= 4:
                    if 2 not in met.recommendations:
                        rec.color = "Red"
                        rec.specific_insight_recovery = "a "+ str(t.streak) + " day trend of persistent, severe [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")

                        met.recommendations[2] = rec
                    else:
                        met.recommendations[2].soreness.append(t)

                elif 2 < t.average_severity < 4:
                    if 1 not in met.recommendations:
                        rec.color = "Yellow"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, moderate [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("6C")
                        rec.specific_actions.append("3B")

                        met.recommendations[1] = rec
                    else:
                        met.recommendations[1].soreness.append(t)

                else:
                    if 0 not in met.recommendations:
                        rec.color = "Green"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, mild [body part] soreness impacting performance & indicating elevated injury risk"
                        # NONE

                        met.recommendations[0] = rec
                    else:
                        met.recommendations[0].soreness.append(t)

        if len(met.recommendations) > 0:
            metrics.append(met)

        met = AthleteMetric()
        met.metric_type = MetricType.longitudinal
        met.metric = "Chronic Soreness"

        for t in athlete_stats.historic_soreness:

            if t.historic_soreness_status == HistoricSorenessStatus.chronic and not t.is_pain:
                #rec.threshold = t.average_severity
                #rec.body_part_location = t.body_part.location.value
                #rec.body_part_side = t.side
                #rec.soreness.append(t)
                rec = AthleteRecommendation()
                rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                rec.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
                if t.average_severity >= 4:
                    if 2 not in met.recommendations:
                        rec.color = "Red"
                        rec.specific_insight_recovery = "a "+ str(t.streak) + " day trend of chronic, severe [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("3B")
                        rec.specific_actions.append("7A")
                        met.recommendations[2] = rec

                    else:
                        met.recommendations[2].soreness.append(t)

                elif 2 < t.average_severity < 4:
                    if 1 not in met.recommendations:
                        rec.color = "Yellow"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, moderate [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("6C")
                        rec.specific_actions.append("3B")
                        met.recommendations[1] = rec

                    else:
                        met.recommendations[1].soreness.append(t)
                else:
                    if 0 not in met.recommendations:
                        rec.color = "Green"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, mild [body part] soreness impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        met.recommendations[0] = rec

                    else:
                        met.recommendations[0].soreness.append(t)

        if len(met.recommendations) > 0:
            metrics.append(met)

        met = AthleteMetric()
        met.metric_type = MetricType.longitudinal
        met.metric = "Persistent Pain"

        for t in athlete_stats.historic_soreness:
            if t.historic_soreness_status == HistoricSorenessStatus.persistent and t.is_pain:

                #rec.threshold = t.average_severity
                #rec.body_part_location = t.body_part.location.value
                #rec.body_part_side = t.side
                #rec.soreness.append(t)
                rec = AthleteRecommendation()
                rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                rec.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
                if t.average_severity >= 4:
                    if 2 not in met.recommendations:
                        rec.color = "Red"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, severe [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("5A")
                        rec.specific_actions.append("2A")
                        rec.specific_actions.append("3A")
                        met.recommendations[2] = rec

                    else:
                        met.recommendations[2].soreness.append(t)

                elif 2 < t.average_severity < 4:
                    if 1 not in met.recommendations:
                        rec.color = "Yellow"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, moderate [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("6B")
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("3B")
                        met.recommendations[1] = rec

                    else:
                        met.recommendations[1].soreness.append(t)

                else:
                    if 0 not in met.recommendations:
                        rec.color = "Green"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of persistent, mild [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        met.recommendations[0] = rec

                    else:
                        met.recommendations[0].soreness.append(t)

        if len(met.recommendations) > 0:
            metrics.append(met)

        met = AthleteMetric()
        met.metric_type = MetricType.longitudinal
        met.metric = "Chronic Pain"

        for t in athlete_stats.historic_soreness:
            if t.historic_soreness_status == HistoricSorenessStatus.chronic and t.is_pain:

                #rec.threshold = t.average_severity
                #rec.body_part_location = t.body_part.location.value
                #rec.body_part_side = t.side
                #rec.soreness.append(t)
                rec = AthleteRecommendation()
                rec.high_level_insight = WeeklyHighLevelInsight.address_pain_or_soreness
                rec.high_level_action_description = "Prioritize Recovery and consider decreasing upcoming workloads"
                if t.average_severity >= 4:
                    if 2 not in met.recommendations:
                        rec.color = "Red"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, severe [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("5A")
                        rec.specific_actions.append("2A")
                        rec.specific_actions.append("3A")
                        met.recommendations[2] = rec

                    else:
                        met.recommendations[2].soreness.append(t)

                elif 2 < t.average_severity< 4:
                    if 1 not in met.recommendations:
                        rec.color = "Yellow"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, moderate [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("6B")
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("3B")
                        met.recommendations[1] = rec

                    else:
                        met.recommendations[1].soreness.append(t)

                else:
                    if 0 not in met.recommendations:
                        rec.color = "Green"
                        rec.specific_insight_recovery = "a " + str(
                            t.streak) + " day trend of chronic, mild [body part] pain impacting performance & indicating elevated injury risk"
                        rec.specific_actions.append("7A")
                        rec.specific_actions.append("6C")

                        met.recommendations[0] = rec

                    else:
                        met.recommendations[0].soreness.append(t)

        if len(met.recommendations) > 0:
            metrics.append(met)

        return metrics