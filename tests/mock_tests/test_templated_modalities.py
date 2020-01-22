from fathomapi.api.config import Config
Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                             'body_part_mapping_filename': 'body_part_mapping_fathom.json'})

from models.daily_plan import DailyPlan
from models.functional_movement_modalities import ModalityType, ActiveRestBeforeTraining, ActiveRestAfterTraining
from utils import format_date
import datetime


def test_on_demand_pre_active_rest_none():
    event_date = format_date(datetime.datetime.now())
    plan = DailyPlan(event_date)
    plan.define_available_modalities()

    assert len(plan.modalities_available_on_demand) == 1
    assert plan.modalities_available_on_demand[0].type == ModalityType.pre_active_rest


def test_on_demand_pre_active_rest_completed():
    event_date_time = datetime.datetime.now()
    event_date = format_date(event_date_time)
    plan = DailyPlan(event_date)
    pre_active_rest = ActiveRestBeforeTraining(event_date_time)
    pre_active_rest.completed = True
    plan.modalities = [pre_active_rest]
    plan.define_available_modalities()

    assert len(plan.modalities_available_on_demand) == 1
    assert plan.modalities_available_on_demand[0].type == ModalityType.pre_active_rest


def test_on_demand_post_active_rest_none():
    event_date = format_date(datetime.datetime.now())
    plan = DailyPlan(event_date)
    plan.train_later = False
    plan.define_available_modalities()

    assert len(plan.modalities_available_on_demand) == 1
    assert plan.modalities_available_on_demand[0].type == ModalityType.post_active_rest


def test_on_demand_post_active_rest_completed():
    event_date_time = datetime.datetime.now()
    event_date = format_date(event_date_time)
    plan = DailyPlan(event_date)
    plan.train_later = False
    pre_active_rest = ActiveRestAfterTraining(event_date_time)
    pre_active_rest.completed = True
    plan.modalities = [pre_active_rest]
    plan.define_available_modalities()

    assert len(plan.modalities_available_on_demand) == 1
    assert plan.modalities_available_on_demand[0].type == ModalityType.post_active_rest
