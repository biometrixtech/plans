from models.planned_exercise import PlannedWorkout
from models.session import PlannedSession
from models.sport import SportName
from logic.workout_processing import WorkoutProcessor
import os, json
import datetime


def get_workout():
    base_path = '../../database/ntc/libraries/workouts/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    json_data = json.load(f)
                    workout = PlannedWorkout.json_deserialise(json_data)
                    for section in workout.sections:
                        for exercise in section.exercises:
                            exercise.movement_id = '58459de6dc2ce90011f93d86'
                    return workout


def get_session(date, workout, assignment_type='default', movement_option=None):
    session = PlannedSession()
    session.event_date = date
    session.session_RPE = workout.rpe or 5
    session.duration_minutes = workout.duration / 60
    session.sport_name = SportName.high_intensity_interval_training

    session.workout = workout
    WorkoutProcessor(user_weight=70, user_age=30).process_planned_workout(session, assignment_type=assignment_type, movement_option=movement_option)

    return session

def test_1():
    planned_workout = get_workout()
    session = get_session(date=datetime.datetime.now(), workout=planned_workout)
    assert session.power_load is not None
