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

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    assert trend_processor.athlete_trend_categories[0].visible is False

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Muscle Over & Under Activity"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is False


def test_trigger_16():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.agonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.agonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    assert trend_processor.athlete_trend_categories[0].visible is False

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Functional Limitation"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is False


def test_pain_view_breaks_tie():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = datetime.now() - timedelta(days=1)
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Functional Limitation"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is True


def test_no_triggers_clear_all():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = datetime.now() - timedelta(days=1)
    trigger_2.source_date_time = now_time - timedelta(seconds=1)

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Muscle Over & Under Activity"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is True

    # now all the triggers be gone!
    no_triggers = []
    trend_processor_next_day = TrendProcessor(no_triggers, athlete_trend_categories=trend_processor.athlete_trend_categories)
    trend_processor_next_day.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is False
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is False
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is False


def test_first_time_experience_sorts_first():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = datetime.now() - timedelta(days=1)
    trigger_2.source_date_time = now_time - timedelta(seconds=1)

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].first_time_experience is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Muscle Over & Under Activity"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is True

    # now clear first time experience for first view
    trend_processor_next_day = TrendProcessor(trigger_list, athlete_trend_categories=trend_processor.athlete_trend_categories)
    trend_processor_next_day.athlete_trend_categories[0].trends[0].first_time_experience = False
    trend_processor_next_day.athlete_trend_categories[0].first_time_experience = False
    trend_processor_next_day.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].first_time_experience is False
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Functional Limitation"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time - timedelta(seconds=1)
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is True


def test_both_sides_body_text_overactive():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = datetime.now() - timedelta(days=1)
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.title == "Your Shins Are Overactive"


def test_one_side_body_text_overactive():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.title == "Your Left Shin Is Overactive"

def test_both_sides_body_text_functional_limitation():
    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = datetime.now() - timedelta(days=1)
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.title == "Your Shins Are Functionally Limited"

def test_one_side_body_text_functional_limitation():
    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = datetime.now() - timedelta(days=1)
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.title == "Your Left Shin Is Functionally Limited"
