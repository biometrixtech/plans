from logic.workout_processing import WorkoutProcessor
from models.session import PlannedSession
from models.movement_tags import Gender
from models.planned_exercise import PlannedWorkout, PlannedWorkoutLoad
from models.session_functional_movement import SessionFunctionalMovement
from models.training_volume import StandardErrorRange
import datetime


def create_planned_workout_load(session):
    session_functional_movement = SessionFunctionalMovement(session, {})
    session_functional_movement.process(event_date=datetime.datetime.now(), load_stats=None)


    workout = PlannedWorkoutLoad(workout_id=session.workout.program_module_id)
    workout.projected_session_rpe = StandardErrorRange(observed_value=session.session_RPE)
    workout.projected_rpe_load = session.rpe_load
    workout.projected_power_load = session.power_load

    session_details = session_functional_movement.completed_session_details

    workout.duration = session_details.duration
    workout.session_detailed_load = session_details.session_detailed_load
    workout.session_training_type_load = session_details.session_training_type_load
    workout.muscle_detailed_load = session_details.muscle_detailed_load
    workout.ranked_muscle_detailed_load = session_details.ranked_muscle_load
    return workout

def create_planned_session_detail(planned_workout):
    planned_workout_json = planned_workout.json_serialise()
    session1 = PlannedSession()
    session1.workout = PlannedWorkout.json_deserialise(planned_workout_json)

    proc_1 = WorkoutProcessor(user_weight=55, user_age=25, gender=Gender.male)
    proc_1.process_planned_workout(session1)
    planned_workout_1 = create_planned_workout_load(session1)
    planned_workout_1_json = planned_workout_1.json_serialise()
    planned_workout_1_recreated = PlannedWorkoutLoad.json_deserialise(planned_workout_1_json)

    session2 = PlannedSession()
    session2.workout = PlannedWorkout.json_deserialise(planned_workout_json)

    proc_2 = WorkoutProcessor(user_weight=55, user_age=25, gender=Gender.female)
    proc_2.process_planned_workout(session2)

    planned_workout_2 = create_planned_workout_load(session2)
    planned_workout_2_json = planned_workout_1.json_serialise()
    planned_workout_2_recreated = PlannedWorkoutLoad.json_deserialise(planned_workout_2_json)

    print('here')

