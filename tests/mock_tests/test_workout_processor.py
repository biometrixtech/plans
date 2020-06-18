from logic.workout_processing import WorkoutProcessor
from models.workout_program import WorkoutExercise, WorkoutSection, WorkoutProgramModule
from models.movement_tags import AdaptationType, CardioAction, TrainingType
from models.movement_actions import ExerciseAction, Movement, Explosiveness
from models.exercise import UnitOfMeasure
from models.heart_rate import HeartRateData
from models.session import MixedActivitySession
import datetime
from utils import format_datetime
import random


def get_heart_rate_data(low_value, high_value, observations, single_timestamp=False):

    current_date_time = datetime.datetime.now()

    heart_rate_list = []

    heart_rate = {}
    heart_rate['start_date'] = format_datetime(current_date_time)
    if single_timestamp:
        heart_rate['end_date'] = None
    else:
        heart_rate['end_date'] = format_datetime(current_date_time)
    heart_rate['value'] = low_value

    data = HeartRateData(heart_rate)
    heart_rate_list.append(data)

    next_date_time = current_date_time

    for d in range(1, observations):
        next_date_time = next_date_time + datetime.timedelta(seconds=(4))
        heart_rate = {}
        heart_rate['start_date'] = format_datetime(next_date_time)
        if single_timestamp:
            heart_rate['end_date'] = None
        else:
            heart_rate['end_date'] = format_datetime(next_date_time)
        value = random.randint(low_value, high_value)
        heart_rate['value'] = value
        data = HeartRateData(heart_rate)
        heart_rate_list.append(data)

    return heart_rate_list

def get_exercise(reps=1, sets=1, unit=UnitOfMeasure.seconds, movement_id=""):
    exercise = WorkoutExercise()
    exercise.reps_per_set = reps
    exercise.sets = sets
    exercise.unit_of_measure = unit
    exercise.movement_id = movement_id
    exercise.pace = 120
    exercise.stroke_rate = 22
    if movement_id == "":
        action = ExerciseAction('0', 'test_action')
        action.training_type = TrainingType.strength_cardiorespiratory
        action.reps = reps
        action.lateral_distribution = [0, 0]
        action.apply_resistance = True
        action.eligible_external_resistance = []
        action.lateral_distribution_pattern = None
        exercise.primary_actions = [action]
    return exercise


def get_section(name, exercises, start=None, end=None):
    section = WorkoutSection()
    section.name = name
    section.exercises = exercises
    section.start_date_time = format_datetime(start)
    section.end_date_time = format_datetime(end)
    if section.start_date_time is not None and section.end_date_time is not None:
        section.duration_seconds = (section.end_date_time - section.start_date_time).seconds
    return section


def test_one_load_section_one_no_load():
    workout_exercise1 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459d9ddc2ce90011f93d84")  # row
    workout_exercise2 = get_exercise(reps=180, sets=1, unit=UnitOfMeasure.meters, movement_id="57e2fd3a4c6a031dc777e90c")  # airdyne

    workout_exercise3 = get_exercise(reps=500, sets=1, unit=UnitOfMeasure.meters, movement_id="58459d9ddc2ce90011f93d84")  # row
    workout_exercise4 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.count, movement_id="58459df8dc2ce90011f93d87")  # run

    workout_exercise5 = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, movement_id='57e2fd3a4c6a031dc777e936')

    section1 = get_section('warm up', exercises=[workout_exercise1, workout_exercise2])
    section2 = get_section('stamina', exercises=[workout_exercise3, workout_exercise4])
    section3 = get_section('strength', exercises=[workout_exercise5])

    workout = WorkoutProgramModule()
    workout.workout_sections = [section1, section2, section3]

    processor = WorkoutProcessor()
    session = MixedActivitySession()
    session.workout_program_module = workout
    processor.process_workout(session)
    # total_training_load = workout.get_training_load()

    # assert workout_exercise1.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory
    assert workout_exercise1.cardio_action == CardioAction.row

    # assert workout_exercise3.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory
    assert workout_exercise3.cardio_action == CardioAction.row

    # assert workout_exercise4.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory
    assert workout_exercise4.cardio_action == CardioAction.run
    # assert workout_exercise4.get_training_volume() == 90

    assert section1.assess_load is False
    # assert section1.get_training_load() == 0
    # assert section2.get_training_load() != 0
    # assert section2.get_training_load() == workout_exercise3.get_training_load() + workout_exercise4.get_training_load()
    # assert total_training_load == section2.get_training_load() + section3.get_training_load()

    workout_json = workout.json_serialise()
    workout_2 = WorkoutProgramModule.json_deserialise(workout_json)


def test_apply_explosiveness_to_actions():

    exercise = WorkoutExercise()
    exercise.explosiveness_rating = 8
    action_1 = ExerciseAction("2", "Action1")
    action_1.explosiveness = Explosiveness.high_force
    action_2 = ExerciseAction("3", "Action2")
    action_2.explosiveness = Explosiveness.max_force

    exercise.primary_actions.append(action_1)
    exercise.primary_actions.append(action_2)

    processor = WorkoutProcessor()

    processor.set_action_explosiveness_from_exercise(exercise, exercise.primary_actions)

    assert action_1.explosiveness_rating == 8 * 0.75
    assert action_2.explosiveness_rating == 8 * 1.00


def test_shrz():
    workout_exercise1 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459d9ddc2ce90011f93d84")  # row

    workout_exercise4 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.count, movement_id="58459df8dc2ce90011f93d87")  # run

    workout_exercise5 = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, movement_id='57e2fd3a4c6a031dc777e936')  # bent over row

    start_time = datetime.datetime.now()
    section1_start = start_time + datetime.timedelta(seconds=2)
    section1_end = section1_start + datetime.timedelta(seconds=60)
    section2_start = section1_end + datetime.timedelta(seconds=2)
    section2_end = section2_start + datetime.timedelta(seconds=60)
    section3_start = section2_end + datetime.timedelta(seconds=2)
    section3_end = section3_start + datetime.timedelta(seconds=60)

    heart_rate_data = get_heart_rate_data(130, 170, 300, single_timestamp=True)

    section1 = get_section('warm up', exercises=[workout_exercise1], start=section1_start, end=section1_end)
    section2 = get_section('stamina', exercises=[workout_exercise4], start=section2_start, end=section2_end)
    section3 = get_section('strength', exercises=[workout_exercise5], start=section3_start, end=section3_end)

    workout = WorkoutProgramModule()
    workout.workout_sections = [section1, section2, section3]

    processor = WorkoutProcessor(hr_data=heart_rate_data)
    session = MixedActivitySession()
    session.workout_program_module = workout
    processor.process_workout(session)

    assert not section1.assess_shrz  # no shrz for warmup
    assert section2.assess_shrz  # get shrz
    assert not section3.assess_shrz  # no shrz for strength

    shrz = workout.aggregate_shrz()

    assert shrz == section2.shrz == workout_exercise4.shrz
    for action in workout_exercise4.primary_actions:
        assert action.training_intensity == shrz
    for action in workout_exercise4.secondary_actions:
        assert action.training_intensity == shrz


def test_new_actions():
    workout_exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="5823768d473c06100052ed9a")  # run

    start_time = datetime.datetime.now()
    section1_start = start_time + datetime.timedelta(seconds=2)
    section1_end = section1_start + datetime.timedelta(seconds=3000)

    section1 = get_section('stamina', exercises=[workout_exercise], start=section1_start, end=section1_end)

    workout = WorkoutProgramModule()
    workout.workout_sections = [section1]

    processor = WorkoutProcessor()
    session = MixedActivitySession()
    session.workout_program_module = workout
    processor.process_workout(session)
