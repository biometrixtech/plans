from logic.trend_processing import TrendProcessor
from models.trigger import Trigger, TriggerType
from models.soreness import BodyPartLocation, BodyPartSide
from models.body_parts import BodyPartFactory


def test_trigger_19():

    trigger_list = []
    body_part_factory = BodyPartFactory()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = body_part.synergists
    trigger.antagonists = body_part.antagonists

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert len(trend_processor.athlete_trends.trend_categories) > 0