from models.metrics import AthleteRecommendation

class MetricsProcessing(object):

    def get_athlete_metrics_from_stats(self, athlete_stats):

        recommendations = []



        for t in athlete_stats.three_day_consecutive_pain:
            rec = AthleteRecommendation()
            rec.metric = "3 Day Consecutive Pain"
            rec.threshold = t.severity
            rec.body_part_location = t.body_part.location.value
            rec.body_part_side = t.side
            if rec.threshold >= 3:
                rec.color = "Red"
                rec.high_level_insight = "Not Cleared for Training"
                rec.high_level_action_description = "Pain severity is too high for training today, consult medical staff to evaluate status"
                rec.specific_insight_recovery = "Consistent reports of significant [Body Part] pain for the last three days may be a sign of injury"
                rec.recommendations.append("5A")
                rec.recommendations.append("2A")
            else:
                rec.color = "Yellow"
                rec.high_level_insight = "Monitor in Training, Moderate if Needed"
                rec.high_level_action_description = "Stop training if pain increases and consider reducing workload to facilitate recovery"
                rec.specific_insight_recovery = "Consistent reports of significant [Body Part] pain for the last three days may be a sign of injury"
                rec.recommendations.append("6A")
                rec.recommendations.append("7B")
            recommendations.append(rec)

        return recommendations