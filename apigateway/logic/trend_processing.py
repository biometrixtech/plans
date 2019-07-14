from models.athlete_trend import AthleteTrends, Trend, TrendCategory, TrendData
from models.trigger import Trigger, TriggerType


class TrendProcessor(object):
    def __init__(self, trigger_list):
        self.athlete_trends = None
        self.trigger_list = trigger_list

    def get_antagonists_syngergists(self, triggers):

        antagonists = []
        synergists = []
        for t in triggers:
            antagonists.extend(t.antagonists)
            synergists.extend(t.synergists)

        return antagonists, synergists

    def process_triggers(self):

        self.athlete_trends = AthleteTrends()

        trend_category = TrendCategory(None)
        trend_category.title = "Movement Dysfunction or Compensation"
        tight_muscle_trend = self.get_tight_muscle_view()
        over_under_muscle_trend = self.get_overactive_underactive_muscle_view()
        if tight_muscle_trend is not None:
            trend_category.trends.append(tight_muscle_trend)
        if over_under_muscle_trend is not None:
            trend_category.trends.append(over_under_muscle_trend)

        if len(trend_category.trends) > 0:
            self.athlete_trends.trend_categories.append(trend_category)

    def get_tight_muscle_view(self):

        trigger_type = TriggerType.hist_sore_less_30
        triggers = list(t for t in self.trigger_list if t.trigger_type == trigger_type)
        if len(triggers) > 0:
            antagonists, synergists = self.get_antagonists_syngergists(triggers)
            trend = Trend(trigger_type)
            trend.title = "Tight Muscle"
            trend.text = "Your data suggests tight muscle stuff"
            trend_data = TrendData()
            trend_data.data = {'tight_muscle': [t.body_part.body_part_location.value for t in triggers],
                               'underactive': [s for s in synergists]}
            trend_data.text = "This is a specific description of all your tight muscles..."
            trend.data = trend_data
            return trend
        else:
            return None

    def get_overactive_underactive_muscle_view(self):

        trigger_type = TriggerType.hist_sore_greater_30
        triggers = list(t for t in self.trigger_list if t.trigger_type == trigger_type)
        if len(triggers) > 0:
            antagonists, synergists = self.get_antagonists_syngergists(triggers)
            trend = Trend(trigger_type)
            trend.title = "Overactive & Underactive Muscle"
            trend.text = "Your data suggests several imbalances in muscle activation which can lead to performance inefficiencies...."
            trend_data = TrendData()
            trend_data.data = {'overactive': [t.body_part.body_part_location.value for t in triggers],
                               'underactive': [a for a in antagonists]}
            trend_data.text = "This is a specific description of all your o/u body parts..."
            trend.data = trend_data
            return trend
        else:
            return None





