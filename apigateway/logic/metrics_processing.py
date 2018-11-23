from models.metrics import AthleteRecommendation

class MetricsProcessing(object):

    def get_athlete_metrics_from_stats(self, athlete_stats, event_date):

        recommendations = []

        if athlete_stats.session_RPE is not None and athlete_stats.session_RPE_event_date == event_date:
            if athlete_stats.session_RPE >= 5.0:
                rec = AthleteRecommendation()
                rec.metric = "Session RPE"
                rec.threshold = athlete_stats.session_RPE
                rec.body_part_location = None
                rec.body_part_side = None
                if athlete_stats.session_RPE >= 8.0:
                    rec.color = "Red"
                elif 6.0 <= athlete_stats.session_RPE < 8.0:
                    rec.color = "Yellow"
                rec.high_level_insight = "Limit Time & Intensity of Training"
                rec.high_level_action_description = "Shorten training or limit intensity and focus on recovery modalities"
                rec.specific_insight_recovery = ""
                rec.specific_insight_training_volume = ("A spike in workload on "+athlete_stats.session_RPE_event_date +
                                                        " which should be countered with a recovery day soon for optimal " +
                                                        "recovery and gains")
                rec.recommendations.append("2B")
                rec.recommendations.append("7A")
                recommendations.append(rec)

        if (athlete_stats.daily_severe_soreness is not None and len(athlete_stats.daily_severe_soreness) > 0
                and athlete_stats.daily_severe_soreness_event_date == event_date):
            for t in athlete_stats.daily_severe_soreness:
                if t.severity >= 3.0:
                    rec = AthleteRecommendation()
                    rec.metric = "Daily Severe Soreness"
                    rec.threshold = t.severity
                    rec.body_part_location = t.body_part.location.value
                    rec.body_part_side = t.side
                    rec.color = "Yellow"
                    rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
                    if athlete_stats.daily_severe_soreness >= 4.0:
                        rec.high_level_insight = "Limit Time & Intensity of Training"

                        rec.specific_insight_recovery = ("Severe [bodypart/global] soreness on for the last " + str(t.streak) + " reported days may impact performance & indicate elevated injury risk")
                        rec.specific_insight_training_volume = ""
                        rec.recommendations.append("2B")
                        rec.recommendations.append("7A")
                        rec.recommendations.append("6B")
                    elif 3.0 <= athlete_stats.daily_severe_soreness < 4.0 :
                        rec.high_level_insight = "Monitor in Training, Moderate if Needed"
                        rec.specific_insight_recovery = "Elevated [body part] soreness which may impact performance"
                        rec.specific_insight_training_volume = ""
                        rec.recommendations.append("6A")
                        rec.recommendations.append("7A")

                    recommendations.append(rec)

        if (athlete_stats.daily_severe_pain is not None and len(athlete_stats.daily_severe_pain) > 0
                and athlete_stats.daily_severe_pain == event_date):
            for t in athlete_stats.daily_severe_pain:
                rec = AthleteRecommendation()
                rec.metric = "Daily Severe Pain"
                rec.threshold = t.severity
                rec.body_part_location = t.body_part.location.value
                rec.body_part_side = t.side

                rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
                if athlete_stats.daily_severe_pain <= 2.0:
                    rec.color = "Yellow"
                    rec.high_level_insight = "Monitor in Training, Moderate if Needed"
                    rec.specific_insight_recovery = ("Low severity [body part] pain which should be monitored to prevent the development of injury")
                    rec.specific_insight_training_volume = ""
                    rec.recommendations.append("6A")
                    rec.recommendations.append("7A")

                elif 2.0 < athlete_stats.daily_severe_pain < 4.0:
                    rec.color = "Yellow"
                    rec.high_level_insight = "Limit Time & Intensity of Training"
                    rec.specific_insight_recovery = "Elevated [body part] pain which should be monitored to prevent injury"
                    rec.specific_insight_training_volume = ""
                    rec.recommendations.append("2B")
                    rec.recommendations.append("7B")
                    rec.recommendations.append("6A")
                elif athlete_stats.daily_severe_pain >= 4.0:
                    rec.color = "Red"
                    rec.high_level_insight = "Not cleared for Training"
                    rec.specific_insight_recovery = "[body part] pain severity that is too high to train today and may indicate injury"
                    rec.specific_insight_training_volume = ""
                    rec.recommendations.append("5A")
                    rec.recommendations.append("2A")
                recommendations.append(rec)

        for t in athlete_stats.historic_soreness:
            if t.streak >= 3 and t.is_pain:
                rec = AthleteRecommendation()
                rec.metric = "3 Day Consecutive Pain"
                rec.threshold = t.average_severity
                rec.body_part_location = t.body_part.location.value
                rec.body_part_side = t.side
                if rec.threshold >= 3:
                    rec.color = "Red"
                    rec.high_level_insight = "Not Cleared for Training"
                    rec.high_level_action_description = "Pain severity is too high for training today, consult medical staff to evaluate status"
                    rec.specific_insight_recovery = "Consistent reports of significant [Body Part] pain for the last " + str(t.streak) + " days may be a sign of injury"
                    rec.recommendations.append("5A")
                    rec.recommendations.append("2A")
                else:
                    rec.color = "Yellow"
                    rec.high_level_insight = "Monitor in Training, Moderate if Needed"
                    rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
                    rec.specific_insight_recovery = "Consistent reports of significant [Body Part] pain for the last " + str(t.streak) + " days may be a sign of injury"
                    rec.recommendations.append("6A")
                    rec.recommendations.append("7B")
                recommendations.append(rec)

        return recommendations