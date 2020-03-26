import datetime
from logic.activities_processing import ActivitiesProcessing
from models.functional_movement_activities import MobilityWOD, MovementPrep, ResponsiveRecovery, MovementIntegrationPrep, ActiveRest, ActiveRecovery, IceSession, ColdWaterImmersion, ActivityType
from tests.mocks.mock_datastore_collection import DatastoreCollection

def test_mobility_wod_complete_active_rest():
    event_date_time = datetime.datetime.now()
    mobility_wod = MobilityWOD('tester', event_date_time)
    mobility_wod.active_rest = ActiveRest(event_date_time)
    completed_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_completed(mobility_wod, completed_date_time, ActivityType.active_rest.value, 'tester', [])

    assert mobility_wod.active_rest.completed
    assert mobility_wod.active_rest.completed_date_time == completed_date_time


def test_movement_prep_complete_movement_integration_prep():
    event_date_time = datetime.datetime.now()
    movement_prep = MovementPrep('tester', event_date_time)
    movement_prep.movement_integration_prep = MovementIntegrationPrep(event_date_time)
    completed_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_completed(movement_prep, completed_date_time, ActivityType.movement_integration_prep.value, 'tester', [])

    assert movement_prep.movement_integration_prep.completed
    assert movement_prep.movement_integration_prep.completed_date_time == completed_date_time


def test_responsive_recovery_complete_active_rest():
    event_date_time = datetime.datetime.now()
    responsive_recovery = ResponsiveRecovery('tester', event_date_time)
    responsive_recovery.active_rest = ActiveRest(event_date_time)
    completed_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_completed(responsive_recovery, completed_date_time, ActivityType.active_rest.value, 'tester', [])

    assert responsive_recovery.active_rest.completed
    assert responsive_recovery.active_rest.completed_date_time == completed_date_time


def test_responsive_recovery_complete_active_recovery():
    event_date_time = datetime.datetime.now()
    responsive_recovery = ResponsiveRecovery('tester', event_date_time)
    responsive_recovery.active_recovery = ActiveRecovery(event_date_time)
    completed_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_completed(responsive_recovery, completed_date_time, ActivityType.active_recovery.value, 'tester', ['1', '2'])

    assert responsive_recovery.active_recovery.completed
    assert responsive_recovery.active_recovery.completed_date_time == completed_date_time


def test_responsive_recovery_complete_ice():
    event_date_time = datetime.datetime.now()
    responsive_recovery = ResponsiveRecovery('tester', event_date_time)
    responsive_recovery.ice = IceSession(event_date_time)
    completed_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_completed(responsive_recovery, completed_date_time, ActivityType.ice.value, 'tester', [])

    assert responsive_recovery.ice.completed
    assert responsive_recovery.ice.completed_date_time == completed_date_time


def test_responsive_recovery_complete_cwi():
    event_date_time = datetime.datetime.now()
    responsive_recovery = ResponsiveRecovery('tester', event_date_time)
    responsive_recovery.cold_water_immersion = ColdWaterImmersion(event_date_time)
    completed_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_completed(responsive_recovery, completed_date_time, ActivityType.cold_water_immersion.value, 'tester', [])

    assert responsive_recovery.cold_water_immersion.completed
    assert responsive_recovery.cold_water_immersion.completed_date_time == completed_date_time


def test_mobility_wod_start_active_rest():
    event_date_time = datetime.datetime.now()
    mobility_wod = MobilityWOD('tester', event_date_time)
    mobility_wod.active_rest = ActiveRest(event_date_time)
    start_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_started(mobility_wod, start_date_time, ActivityType.active_rest.value)

    assert mobility_wod.active_rest.start_date_time == start_date_time


def test_movement_prep_start_movement_integration_prep():
    event_date_time = datetime.datetime.now()
    movement_prep = MovementPrep('tester', event_date_time)
    movement_prep.movement_integration_prep = MovementIntegrationPrep(event_date_time)
    start_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_started(movement_prep, start_date_time, ActivityType.movement_integration_prep.value)

    assert movement_prep.movement_integration_prep.start_date_time == start_date_time


def test_responsive_recovery_start_active_rest():
    event_date_time = datetime.datetime.now()
    responsive_recovery = ResponsiveRecovery('tester', event_date_time)
    responsive_recovery.active_rest = ActiveRest(event_date_time)
    start_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_started(responsive_recovery, start_date_time, ActivityType.active_rest.value)

    assert responsive_recovery.active_rest.start_date_time == start_date_time


def test_responsive_recovery_start_active_recovery():
    event_date_time = datetime.datetime.now()
    responsive_recovery = ResponsiveRecovery('tester', event_date_time)
    responsive_recovery.active_recovery = ActiveRecovery(event_date_time)
    start_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_started(responsive_recovery, start_date_time, ActivityType.active_recovery.value)

    assert responsive_recovery.active_recovery.start_date_time == start_date_time


def test_responsive_recovery_start_ice():
    event_date_time = datetime.datetime.now()
    responsive_recovery = ResponsiveRecovery('tester', event_date_time)
    responsive_recovery.ice = IceSession(event_date_time)
    start_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_started(responsive_recovery, start_date_time, ActivityType.ice.value)

    assert responsive_recovery.ice.start_date_time == start_date_time


def test_responsive_recovery_start_cwi():
    event_date_time = datetime.datetime.now()
    responsive_recovery = ResponsiveRecovery('tester', event_date_time)
    responsive_recovery.cold_water_immersion = ColdWaterImmersion(event_date_time)
    start_date_time = event_date_time + datetime.timedelta(hours=1)
    ActivitiesProcessing(DatastoreCollection()).mark_activity_started(responsive_recovery, start_date_time, ActivityType.cold_water_immersion.value)

    assert responsive_recovery.cold_water_immersion.start_date_time == start_date_time
