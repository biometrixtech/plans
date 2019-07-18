from logic.trend_processing import TrendProcessor
from logic.trigger_processing import TriggerFactory
from models.trigger import TriggerType, Trigger
from models.body_parts import BodyPartFactory
from models.soreness_base import BodyPartLocation, BodyPartSide
from datetime import datetime, timedelta


def test_trigger_19():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.modified_date_time = datetime.now()

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert len(trend_processor.athlete_trends.trend_categories) > 0

def test_trigger_16():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.agonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.agonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.modified_date_time = datetime.now()

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert len(trend_processor.athlete_trends.trend_categories) > 0