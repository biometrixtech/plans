from models.workout_program import WorkoutExercise
from models.movement_tags import CardioAction
from models.training_volume import StandardErrorRange


def test_set_hr_zones_all_below_50_percent():
    age = 25
    max_hr = 207 - .7 * age
    ex = WorkoutExercise()
    ex.hr = [max_hr * .49] * 100
    ex.set_hr_zones(age)

    assert ex.percent_time_at_85_above_max_hr == 0
    assert ex.percent_time_at_65_80_max_hr == 0
    assert ex.percent_time_at_80_85_max_hr == 0

    assert ex.percent_time_above_vo2max == 0
    assert ex.percent_time_below_vo2max == 0


def test_set_hr_zones_all_between_50_60():
    age = 25
    max_hr = 207 - .7 * age
    ex = WorkoutExercise()
    ex.hr = [max_hr * .55] * 100
    ex.set_hr_zones(age)

    assert ex.percent_time_at_85_above_max_hr == 0
    assert ex.percent_time_at_65_80_max_hr == 0
    assert ex.percent_time_at_80_85_max_hr == 0

    assert ex.percent_time_above_vo2max == 0
    assert ex.percent_time_below_vo2max == 1


def test_set_hr_zones_distributed_beween_zone1_zone2():
    age = 25
    max_hr = 207 - .7 * age
    ex = WorkoutExercise()
    ex.hr = [max_hr * .70] * 100
    ex.hr.extend([max_hr * .82] * 100)
    ex.set_hr_zones(age)

    assert ex.percent_time_at_85_above_max_hr == 0
    assert ex.percent_time_at_80_85_max_hr == .5
    assert ex.percent_time_at_65_80_max_hr == .5

    assert ex.percent_time_above_vo2max == .5
    assert ex.percent_time_below_vo2max == .5


def test_set_hr_zones_distribution_3():
    age = 25
    max_hr = 207 - .7 * age
    ex = WorkoutExercise()
    ex.hr = [max_hr * .70] * 100
    ex.hr.extend([max_hr * .82] * 100)
    ex.hr.extend([max_hr * .86] * 100)
    ex.set_hr_zones(age)

    assert ex.percent_time_at_85_above_max_hr == .33
    assert ex.percent_time_at_80_85_max_hr == .33
    assert ex.percent_time_at_65_80_max_hr == .33

    assert ex.percent_time_above_vo2max == .67
    assert ex.percent_time_below_vo2max == .33


def test_set_speed_pace_speed():
    ex = WorkoutExercise()
    ex.speed = .5
    ex.set_speed_pace()
    assert ex.pace == 2


def test_set_speed_pace_pace():
    ex = WorkoutExercise()
    ex.pace = .5
    ex.set_speed_pace()
    assert ex.speed == 2


def test_set_speed_pace_cardio_power():
    ex = WorkoutExercise()
    ex.cardio_action = CardioAction.row
    ex.power = StandardErrorRange(observed_value=1)
    ex.set_speed_pace()
    assert ex.speed is not None
    assert ex.pace is not None


def test_set_speed_pace_calorie_duration():
    ex = WorkoutExercise()
    ex.cardio_action = CardioAction.row
    ex.calories = 100
    ex.duration = 1000
    ex.set_speed_pace()
    assert ex.speed is not None
    assert ex.pace is not None
