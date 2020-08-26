from models.planned_exercise import PlannedExercise
from models.training_volume import Assignment
from models.movement_tags import CardioAction


def get_planned_exercise(speed=None, pace=None, distance=None, duration=None):
    ex = PlannedExercise()
    ex.speed = speed
    ex.pace = pace
    ex.distance = distance
    ex.duration = duration

    return ex


def test_set_speed_pace_nothing_defined():
    ex = get_planned_exercise()
    ex.set_speed_pace()
    ex.speed = None
    ex.pace = None


def test_set_speed_pace_speed_min_value():
    ex = get_planned_exercise(speed=Assignment(min_value=1))
    ex.set_speed_pace()
    assert ex.pace.min_value is not None
    assert ex.pace.assigned_value is None
    assert ex.pace.max_value is None


def test_set_speed_pace_speed_assigned_value():
    ex = get_planned_exercise(speed=Assignment(assigned_value=1))
    ex.set_speed_pace()
    assert ex.pace.min_value is None
    assert ex.pace.assigned_value is not None
    assert ex.pace.max_value is None


def test_set_speed_pace_speed_min_max():
    ex = get_planned_exercise(speed=Assignment(min_value=1, max_value=2))
    ex.set_speed_pace()
    assert ex.pace.min_value is not None
    assert ex.pace.assigned_value is None
    assert ex.pace.max_value is not None

    assert ex.pace.max_value > ex.pace.min_value


def test_set_speed_pace_pace_min_max():
    ex = get_planned_exercise(pace=Assignment(min_value=1, max_value=2))
    ex.set_speed_pace()
    assert ex.speed.min_value is not None
    assert ex.speed.assigned_value is None
    assert ex.speed.max_value is not None

    assert ex.speed.max_value > ex.speed.min_value


def test_set_speed_pace_row_power_min_max():
    ex = get_planned_exercise()
    ex.power_goal = Assignment(min_value=1, max_value=2)
    ex.cardio_action = CardioAction.row
    ex.set_speed_pace()

    assert ex.pace.max_value > ex.pace.min_value


def test_set_speed_pace_row_power_assigned_value_only():
    ex = get_planned_exercise()
    ex.power_goal = Assignment(assigned_value=2)
    ex.cardio_action = CardioAction.row
    ex.set_speed_pace()

    assert ex.pace.max_value is None
    assert ex.pace.min_value is None
    assert ex.pace.assigned_value is not None


def test_set_speed_pace_row_power_min_max_speed():
    ex = get_planned_exercise()
    ex.power_goal = Assignment(min_value=1, max_value=2)
    ex.cardio_action = CardioAction.row
    ex.set_speed_pace()

    assert ex.speed.max_value > ex.speed.min_value


def test_set_speed_pace_distance_min_max_and_duration_assigned():
    ex = get_planned_exercise(duration=Assignment(assigned_value=10), distance=Assignment(min_value=1, max_value=2))
    ex.set_speed_pace()

    assert ex.speed.min_value < ex.speed.max_value
    assert ex.pace.min_value  < ex.pace.max_value

def test_set_speed_pace_distance_assigned_and_duration_assigned():
    ex = get_planned_exercise(duration=Assignment(assigned_value=10), distance=Assignment(assigned_value=1))
    ex.set_speed_pace()

    assert ex.speed.min_value is None
    assert ex.speed.max_value is None
    assert ex.speed.assigned_value is not None
    assert ex.pace.assigned_value is not None


def test_set_training_loads_nothing_present():
    ex = get_planned_exercise()
    ex.set_training_loads()
    assert ex.power_load is None
    assert ex.rpe_load is None


# def test_set_training_loads_power():
#     ex = get_planned_exercise()
#     ex.power =