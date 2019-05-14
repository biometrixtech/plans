from models.insights import AthleteInsight
from models.soreness import TriggerType, BodyPartSide, BodyPartLocation
from models.sport import SportName


def test_insights_text():
    insight = AthleteInsight(TriggerType(20))
    insight.goal_targeted = ['Recover From Sport']
    insight.parent = False
    insight.first = False
    insight.body_parts = [BodyPartSide(BodyPartLocation(11), 1)]
    insight.sport_names = [SportName(13)]
    insight.get_title_and_text()
    text = insight.text