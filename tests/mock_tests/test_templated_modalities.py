from models.daily_plan import DailyPlan
from models.functional_movement_modalities import ModalityType, ActiveRestAfterTraining, MovementIntegrationPrep
from utils import format_date
import datetime


def test_on_demand_pre_active_rest_none():
    event_date = format_date(datetime.datetime.now())
    plan = DailyPlan(event_date)
    plan.define_available_modalities()

    assert len(plan.modalities_available_on_demand) == 2
    assert plan.modalities_available_on_demand[0].type == ModalityType.post_active_rest
    assert plan.modalities_available_on_demand[1].type == ModalityType.movement_integration_prep


def test_on_demand_movement_prep_assigned_active_rest_completed():
    event_date_time = datetime.datetime.now()
    event_date = format_date(event_date_time)
    plan = DailyPlan(event_date)
    active_rest = ActiveRestAfterTraining(event_date_time)
    active_rest.completed = True
    movement_prep = MovementIntegrationPrep(event_date_time)
    plan.modalities = [active_rest, movement_prep]
    plan.define_available_modalities()

    assert len(plan.modalities_available_on_demand) == 1
    assert plan.modalities_available_on_demand[0].type == ModalityType.post_active_rest


def test_on_demand_movement_prep_post_active_rest_assigned():
    event_date_time = datetime.datetime.now()
    event_date = format_date(event_date_time)
    plan = DailyPlan(event_date)
    active_rest = ActiveRestAfterTraining(event_date_time)
    movement_prep = MovementIntegrationPrep(event_date_time)
    plan.modalities = [active_rest, movement_prep]
    plan.define_available_modalities()

    assert len(plan.modalities_available_on_demand) == 0


def test_on_demand_movement_prep_completed_post_active_rest_assigned():
    event_date_time = datetime.datetime.now()
    event_date = format_date(event_date_time)
    plan = DailyPlan(event_date)
    active_rest = ActiveRestAfterTraining(event_date_time)
    movement_prep = MovementIntegrationPrep(event_date_time)
    movement_prep.completed = True
    plan.modalities = [active_rest, movement_prep]
    plan.define_available_modalities()

    assert len(plan.modalities_available_on_demand) == 1
    assert plan.modalities_available_on_demand[0].type == ModalityType.movement_integration_prep
