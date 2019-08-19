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
    now_time_2 = now_time - timedelta(days=1)

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time_2
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    assert trend_processor.athlete_trend_categories[0].visible is False

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Muscle Over & Under-Activity"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time_2
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is False


def test_trigger_16():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()
    now_time_2 = now_time - timedelta(days=1)

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.agonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.agonists)
    trigger.created_date_time = now_time_2
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    assert trend_processor.athlete_trend_categories[0].visible is False

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Injury Cycle Risks"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time_2
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is False


def test_pain_view_breaks_tie():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()
    now_time_2 = now_time - timedelta(days=1)

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time_2
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = now_time_2
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Injury Cycle Risks"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time_2
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is True


def test_soreness_beats_pain_if_newer():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()
    now_time_2 = now_time - timedelta(days=1)

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = now_time_2

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Muscle Over & Under-Activity"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is True


def test_no_triggers_clear_all():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()
    now_time_2 = now_time - timedelta(days=1)
    now_time_3 = now_time_2 - timedelta(seconds=1)

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time_2
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = now_time_3
    trigger_2.source_date_time = now_time_3

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Muscle Over & Under-Activity"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time_2
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is True

    # now all the triggers be gone!
    no_triggers = []
    trend_processor_next_day = TrendProcessor(no_triggers, athlete_trend_categories=trend_processor.athlete_trend_categories)
    trend_processor_next_day.process_triggers()

    assert trend_processor_next_day.athlete_trend_categories[0].visible is False
    assert trend_processor_next_day.athlete_trend_categories[0].trends[0].visible is False
    assert trend_processor_next_day.athlete_trend_categories[0].trends[1].visible is False


def test_first_time_experience_doesnt_first():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()
    now_time_2 = now_time - timedelta(days=1)
    now_time_3 = now_time_2 - timedelta(seconds=1)

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time_2
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.agonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.agonists)
    trigger_2.created_date_time = now_time_3
    trigger_2.source_date_time = now_time_3

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].first_time_experience is True
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Muscle Over & Under-Activity"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time_2
    assert trend_processor.athlete_trend_categories[0].trends[1].visible is True

    # now clear first time experience for first view
    trend_processor_next_day = TrendProcessor(trigger_list, athlete_trend_categories=trend_processor.athlete_trend_categories)
    trend_processor_next_day.athlete_trend_categories[0].trends[0].first_time_experience = False
    trend_processor_next_day.athlete_trend_categories[0].first_time_experience = False
    trend_processor_next_day.process_triggers()

    assert trend_processor.athlete_trend_categories[0].visible is True
    assert trend_processor.athlete_trend_categories[0].first_time_experience is False
    assert trend_processor.athlete_trend_categories[0].trends[0].visible is True
    assert trend_processor.athlete_trend_categories[0].trends[0].title == "Muscle Over & Under-Activity"
    assert trend_processor.athlete_trend_categories[0].trends[0].last_date_time == now_time_2
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

    trigger_3 = Trigger(TriggerType.hist_sore_greater_30_sport)
    trigger_3.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_3 = body_part_factory.get_body_part(trigger_3.body_part)
    trigger_3.synergists = trigger_factory.convert_body_part_list(trigger_3.body_part, body_part_3.synergists)
    trigger_3.antagonists = trigger_factory.convert_body_part_list(trigger_3.body_part, body_part_3.antagonists)
    trigger_3.agonists = trigger_factory.convert_body_part_list(trigger_3.body_part, body_part_3.agonists)
    trigger_3.created_date_time = datetime.now() - timedelta(days=1)
    trigger_3.source_date_time = now_time

    trigger_list.append(trigger_3)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.title == "Right Calf & Right Foot may lack strength"


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

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.title == "Left Calf & Left Foot may lack strength"


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

    trigger_3 = Trigger(TriggerType.hist_pain_sport)
    trigger_3.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_3 = body_part_factory.get_body_part(trigger_3.body_part)
    trigger_3.synergists = trigger_factory.convert_body_part_list(trigger_3.body_part, body_part_3.synergists)
    trigger_3.antagonists = trigger_factory.convert_body_part_list(trigger_3.body_part, body_part_3.antagonists)
    trigger_3.agonists = trigger_factory.convert_body_part_list(trigger_3.body_part, body_part_3.agonists)
    trigger_3.created_date_time = datetime.now() - timedelta(days=1)
    trigger_3.source_date_time = now_time

    trigger_list.append(trigger_3)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.title == "Elevated strain on Right Quad"


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

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.title == "Elevated strain on Left Quad"


def test_one_side_body_dashboard_functional_limitation():
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

    assert trend_processor.dashboard_categories[0].title == "Signs of Imbalance"
    assert trend_processor.dashboard_categories[0].body_part.body_part_location == BodyPartLocation.quads
    assert trend_processor.dashboard_categories[0].body_part.side == 1
    assert trend_processor.dashboard_categories[0].body_part_text == "Left Quad"
    assert trend_processor.dashboard_categories[0].text == "Elevated strain on"


def test_one_side_body_dashboard_muscle_overactivity():
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

    assert trend_processor.dashboard_categories[0].title == "Signs of Imbalance"
    assert trend_processor.dashboard_categories[0].body_part.body_part_location == BodyPartLocation.calves
    assert trend_processor.dashboard_categories[0].body_part.side == 1
    assert trend_processor.dashboard_categories[0].body_part_text == "Left Calf"
    assert trend_processor.dashboard_categories[0].text == "Potential weakness in"


def test_two_side_body_dashboard_muscle_overactivity():
    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.dashboard_categories[0].title == "Signs of Imbalance"
    assert trend_processor.dashboard_categories[0].body_part.body_part_location == BodyPartLocation.calves
    assert trend_processor.dashboard_categories[0].body_part.side is None
    assert trend_processor.dashboard_categories[0].body_part_text == "Calves"
    assert trend_processor.dashboard_categories[0].text == "Potential weakness in"


def test_two_side_body_dashboard_muscle_overactivity_and_more():
    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trigger_3 = Trigger(TriggerType.hist_pain)
    trigger_3.body_part = BodyPartSide(body_part_location=BodyPartLocation(12), side=2)
    body_part_3 = body_part_factory.get_body_part(trigger_3.body_part)
    trigger_3.synergists = trigger_factory.convert_body_part_list(trigger_3.body_part, body_part_3.synergists)
    trigger_3.antagonists = trigger_factory.convert_body_part_list(trigger_3.body_part, body_part_3.antagonists)
    trigger_3.created_date_time = now_time - timedelta(days=2)
    trigger_3.source_date_time = now_time

    trigger_list.append(trigger_3)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.dashboard_categories[0].title == "Signs of Imbalance"
    assert trend_processor.dashboard_categories[0].body_part.body_part_location == BodyPartLocation.calves
    assert trend_processor.dashboard_categories[0].body_part.side is None
    assert trend_processor.dashboard_categories[0].body_part_text == "Calves and more..."
    assert trend_processor.dashboard_categories[0].text == "Potential weakness in"
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].text == "Signs of Calf & Foot weakness and other insights in your data. Tap to view more."


def test_cleared_plan_alert():

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

    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].text == 'Signs of Left Calf & Left Foot weakness in your data. Tap to view more.'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].title == 'Signs of Imbalance'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].bold_text[0].text == 'Left Calf & Left Foot weakness'

    trend_processor.athlete_trend_categories[0].plan_alerts[0].cleared_date_time = datetime.now()

    trend_processor_2 = TrendProcessor(trigger_list, athlete_trend_categories=trend_processor.athlete_trend_categories)

    trend_processor_2.process_triggers()

    assert trend_processor_2.athlete_trend_categories[0].plan_alerts[0].cleared_date_time is not None


def test_bilateral_body_parts():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].text == 'Signs of Calf & Foot weakness in your data. Tap to view more.'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].title == 'Signs of Imbalance'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].bold_text[0].text == 'Calf & Foot weakness'


def test_non_duplicating_pain_body_parts():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(12), side=0)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)
    #
    # trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    # trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=2)
    # body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    # trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    # trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    # trigger_2.created_date_time = now_time
    # trigger_2.source_date_time = now_time

    # trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].text == 'Signs of elevated strain on Hamstrings & Lats in your data. Tap to view more.'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].title == 'Signs of Imbalance'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].bold_text[0].text == 'elevated strain on Hamstrings & Lats'


def test_bilateral_body_parts_3_elements():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(14), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(14), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].text == 'Signs of elevated strain on Hamstrings, Quads & Lower Back in your data. Tap to view more.'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].title == 'Signs of Imbalance'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].bold_text[0].text == 'elevated strain on Hamstrings, Quads & Lower Back'



def test_body_part_surrounding_text_singular():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(21), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(21), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.text == ("Patterns in your soreness data suggest that your Lats "+
                                                                                     "may actually be overactive due to a chronic over-compensation for weak Shoulders and Biceps.  "+
                                                                                     "This dysfunction could exacerbate movement imbalances and elevate your risk of chronic injury.")

def test_body_part_surrounding_text_plural():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(22), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(23), side=1)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.text == ("Patterns in your soreness data suggest that your Bicep "+
                                                                                     "may actually be overactive due to a chronic over-compensation for a weak Left Tricep.  "+
                                                                                     "This dysfunction could exacerbate movement imbalances and elevate your risk of chronic injury.")

def test_body_part_surrounding_text_plural_both_sides():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(22), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(22), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.text == ("Patterns in your soreness data suggest that your Biceps "+
                                                                                     "may actually be overactive due to a chronic over-compensation for weak Triceps.  "+
                                                                                     "This dysfunction could exacerbate movement imbalances and elevate your risk of chronic injury.")


def test_body_part_surrounding_text_plural_part_2():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_sore_greater_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(4), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(5), side=1)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.text == ("Patterns in your soreness data suggest that your Hip "+
                                                                                     "may actually be overactive due to a chronic over-compensation for a weak Glute.  "+
                                                                                     "This dysfunction could exacerbate movement imbalances and elevate your risk of chronic injury.")


def test_overlapping_muscle_correct():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(16), side=2)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(11), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].overactive[0].body_part_location == BodyPartLocation.outer_thigh
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].overactive[0].side == 2
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].overactive[1].body_part_location == BodyPartLocation.calves
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].overactive[1].side == 2
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].underactive[0].body_part_location == BodyPartLocation.shin
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].underactive[0].side == 2
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].underactive[1].body_part_location == BodyPartLocation.quads
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].underactive[1].side == 2
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].underactive[2].body_part_location == BodyPartLocation.hip_flexor
    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.data[0].underactive[2].side == 2


def test_agonist_capitalized():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    trigger = Trigger(TriggerType.hist_pain)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(14), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time
    trigger.source_date_time = now_time

    trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(14), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].trends[0].trend_data.text == ("Athletes struggling with recurring Glute pain often develop "
                                                                                     + "misalignments that over-stress their Hamstrings, Quads and Lower Back. "+
                                                                                     "Without proactive measures, this can lead to accumulated micro-trauma in "+
                                                                                     "the tissues and new areas of pain or injury over time.")


def test_partial_bilateral_body_parts_3_elements():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()

    # trigger = Trigger(TriggerType.hist_pain)
    # trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(14), side=1)
    # body_part = body_part_factory.get_body_part(trigger.body_part)
    # trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    # trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    # trigger.created_date_time = now_time
    # trigger.source_date_time = now_time
    #
    # trigger_list.append(trigger)

    trigger_2 = Trigger(TriggerType.hist_pain)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(14), side=2)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time
    trigger_2.source_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].text == 'Signs of elevated strain on Right Hamstring, Right Quad & Lower Back in your data. Tap to view more.'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].title == 'Signs of Imbalance'
    assert trend_processor.athlete_trend_categories[0].plan_alerts[0].bold_text[0].text == 'elevated strain on Right Hamstring, Right Quad & Lower Back'


def test_retriggered_plan_alert():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()
    now_time_2 = datetime.now() - timedelta(days=1)

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

    trend_processor.athlete_trend_categories[0].plan_alerts[0].cleared_date_time = now_time_2

    trend_processor_2 = TrendProcessor(trigger_list, athlete_trend_categories=trend_processor.athlete_trend_categories)

    trend_processor_2.process_triggers()

    assert trend_processor_2.athlete_trend_categories[0].plan_alerts[0].cleared_date_time is None


def test_new_alert_with_progressed_trigger_after_clearing():

    trigger_list = []
    body_part_factory = BodyPartFactory()
    trigger_factory = TriggerFactory(datetime.now(), None, [], [])

    now_time = datetime.now()
    now_time_2 = now_time - timedelta(days=1)
    now_time_5 = now_time - timedelta(days=5)

    trigger = Trigger(TriggerType.hist_sore_less_30)
    trigger.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part = body_part_factory.get_body_part(trigger.body_part)
    trigger.synergists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.synergists)
    trigger.antagonists = trigger_factory.convert_body_part_list(trigger.body_part, body_part.antagonists)
    trigger.created_date_time = now_time_5

    trigger_list.append(trigger)

    trend_processor = TrendProcessor(trigger_list)

    trend_processor.process_triggers()

    trend_processor.athlete_trend_categories[0].plan_alerts[0].cleared_date_time = now_time_2

    trend_processor_2 = TrendProcessor(trigger_list, athlete_trend_categories=trend_processor.athlete_trend_categories)

    trend_processor_2.process_triggers()

    assert trend_processor_2.athlete_trend_categories[0].plan_alerts[0].cleared_date_time is not None

    trigger_2 = Trigger(TriggerType.hist_sore_greater_30)
    trigger_2.body_part = BodyPartSide(body_part_location=BodyPartLocation(8), side=1)
    body_part_2 = body_part_factory.get_body_part(trigger_2.body_part)
    trigger_2.synergists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.synergists)
    trigger_2.antagonists = trigger_factory.convert_body_part_list(trigger_2.body_part, body_part_2.antagonists)
    trigger_2.created_date_time = now_time

    trigger_list.append(trigger_2)

    trend_processor_3 = TrendProcessor(trigger_list, athlete_trend_categories=trend_processor.athlete_trend_categories)

    trend_processor_3.process_triggers()

    assert trend_processor_3.athlete_trend_categories[0].plan_alerts[0].cleared_date_time is None