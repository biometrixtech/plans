from models.athlete_trend import AthleteTrends, Trend, TrendCategory, TrendData
from models.trigger import Trigger, TriggerType


class TrendProcessor(object):
    def __init__(self, trigger_list):
        self.athlete_trends = None
        self.trigger_list = trigger_list

    def process_triggers(self):

        self.athlete_trends = AthleteTrends()

        trigger_19s = list(t for t in self.trigger_list if t.trigger_type == TriggerType.hist_sore_greater_30)
        antagonists = []
        for t in trigger_19s:
            antagonists.extend(t.antagonists)
        trend_category = TrendCategory(None)
        trend_category.title = "Movement Dysfunction or Compensation"

        trend = Trend(TriggerType.hist_sore_greater_30)
        trend.title = "Overactive & Underactive Muscle"
        trend.text = "Your data suggests several imbalances in muscle activation which can lead to performance inefficiencies...."

        trend_data = TrendData()
        trend_data.data = {'Overactive': [t.body_part.body_part_location.value for t in trigger_19s],
                           'Underactive': [a for a in antagonists]}
        trend_data.text = "This is a specific description of all your sore body parts..."

        trend.data = trend_data
        trend_category.trends.append(trend)
        self.athlete_trends.trend_categories.append(trend_category)





