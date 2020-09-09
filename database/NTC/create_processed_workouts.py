from logic.workout_processing import WorkoutProcessor
from models.session import PlannedSession
from models.movement_tags import Gender
from models.planned_exercise import PlannedWorkout, PlannedWorkoutLoad
from models.session_functional_movement import SessionFunctionalMovement
from models.training_volume import StandardErrorRange
from datastores.planed_workout_load_datastore import PlannedWorkoutLoadDatastore
from datastores.completed_session_details_datastore import CompletedSessionDetailsDatastore
import datetime


def create_planned_workout_load(session, user_profile_id):
    session_functional_movement = SessionFunctionalMovement(session, {})
    session_functional_movement.process(event_date=datetime.datetime.now(), load_stats=None)


    workout = PlannedWorkoutLoad(workout_id=session.workout.program_module_id)
    workout.program_id = session.workout.program_id
    workout.program_module_id = session.workout.program_module_id
    workout.user_profile_id = user_profile_id
    workout.projected_session_rpe = StandardErrorRange(observed_value=session.session_RPE)
    workout.projected_rpe_load = session.rpe_load
    workout.projected_power_load = session.power_load

    session_details = session_functional_movement.completed_session_details

    workout.duration = session_details.duration
    workout.session_detailed_load = session_details.session_detailed_load
    workout.session_training_type_load = session_details.session_training_type_load
    workout.muscle_detailed_load = session_details.muscle_detailed_load
    workout.ranked_muscle_detailed_load = session_details.ranked_muscle_load
    PlannedWorkoutLoadDatastore().put(workout)
    program_id = workout.program_id
    user_id = session.user_id
    provider_id = program_id
    workout_id = workout.program_module_id
    planned_workout_retrieved = PlannedWorkoutLoadDatastore().get(user_profile_id=user_profile_id, workout_id=workout_id)

    CompletedSessionDetailsDatastore().put(session_details)
    session_details_retrieved = CompletedSessionDetailsDatastore().get(user_id=user_id, workout_id=workout_id)
    return workout

def create_planned_session_detail(planned_workout):
    planned_workout_json = planned_workout.json_serialise()
    session1 = PlannedSession()
    session1.event_date = datetime.datetime.now()
    session1.user_id = 'test_user1'
    session1.workout = PlannedWorkout.json_deserialise(planned_workout_json)

    proc_1 = WorkoutProcessor(user_weight=55, user_age=25, gender=Gender.male)
    proc_1.process_planned_workout(session1)
    planned_workout_1 = create_planned_workout_load(session1, 'profile_1')
    planned_workout_1_json = planned_workout_1.json_serialise()
    planned_workout_1_recreated = PlannedWorkoutLoad.json_deserialise(planned_workout_1_json)

    session2 = PlannedSession()
    session2.user_id = 'test_user2'
    session1.event_date = datetime.datetime.now()
    session2.workout = PlannedWorkout.json_deserialise(planned_workout_json)

    proc_2 = WorkoutProcessor(user_weight=55, user_age=25, gender=Gender.female)
    proc_2.process_planned_workout(session2)

    planned_workout_2 = create_planned_workout_load(session2, 'profile_2')
    planned_workout_2_json = planned_workout_1.json_serialise()
    planned_workout_2_recreated = PlannedWorkoutLoad.json_deserialise(planned_workout_2_json)

    print('here')

