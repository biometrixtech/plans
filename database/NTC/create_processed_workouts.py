from logic.workout_processing import WorkoutProcessor
from models.session import PlannedSession
from models.movement_tags import Gender
from models.planned_exercise import PlannedWorkout, PlannedWorkoutLoad
from models.session_functional_movement import SessionFunctionalMovement
from models.training_volume import StandardErrorRange
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.body_parts import BodyPart, BodyPartFactory
from datastores.planed_workout_load_datastore import PlannedWorkoutLoadDatastore
from datastores.completed_session_details_datastore import CompletedSessionDetailsDatastore
import datetime
import pickle


def create_planned_workout_load(session, user_profile_id):
    session_functional_movement = SessionFunctionalMovement(session, {})
    session_functional_movement.process(event_date=datetime.datetime.now(), load_stats=None)
    consolidated_dict = get_consolidated_dict(session_functional_movement.session_load_dict)

    workout = PlannedWorkoutLoad(workout_id=session.workout.program_module_id)
    workout.program_id = session.workout.program_id
    workout.program_module_id = session.workout.program_module_id
    workout.user_profile_id = user_profile_id
    workout.projected_session_rpe = StandardErrorRange(observed_value=session.session_RPE)
    workout.projected_rpe_load = session.rpe_load
    workout.projected_power_load = session.power_load
    workout.training_exposures = session.training_exposures
    workout.duration = session.duration_minutes
    workout.projected_training_volume = session.training_volume

    workout.muscle_detailed_load = consolidated_dict

    #session_details = session_functional_movement.completed_session_details

    #workout.duration = session_details.duration
    # workout.session_detailed_load = session_details.session_detailed_load
    # workout.session_training_type_load = session_details.session_training_type_load
    # workout.muscle_detailed_load = session_details.muscle_detailed_load
    # workout.ranked_muscle_detailed_load = session_details.ranked_muscle_load
    PlannedWorkoutLoadDatastore().put(workout)
    # program_id = workout.program_id
    # user_id = session.user_id
    # provider_id = program_id
    # workout_id = workout.program_module_id
    # planned_workout_retrieved = PlannedWorkoutLoadDatastore().get(user_profile_id=user_profile_id, workout_id=workout_id)

    # CompletedSessionDetailsDatastore().put(session_details)
    # session_details_retrieved = CompletedSessionDetailsDatastore().get(user_id=user_id, workout_id=workout_id)
    return workout

def create_planned_session_detail(planned_workout):
    planned_workout_json = planned_workout.json_serialise()

    profiles = get_profiles()
    for profile in profiles:
        session = PlannedSession()
        session.event_date = datetime.datetime.now()
        session.user_id = profile['user_id']
        session.workout = PlannedWorkout.json_deserialise(planned_workout_json)

        proc = WorkoutProcessor(user_weight=profile['user_weight'], user_age=profile['user_age'], gender=profile['user_gender'], vo2_max=profile['vo2_max'])
        proc.process_planned_workout(session)
        planned_workout = create_planned_workout_load(session, profile['user_profile_id'])


def get_consolidated_dict(session_load_dict):

    aggregated_session_load_dict = aggregate_sld(session_load_dict)

    consolidated_session_load_dict = {}

    body_part_factory = BodyPartFactory()

    for body_part_side, body_part_injury_risk in aggregated_session_load_dict.items():
        body_part = body_part_factory.get_body_part(body_part_side)
        if body_part not in consolidated_session_load_dict:
            consolidated_session_load_dict[body_part] = pickle.loads(pickle.dumps(body_part_injury_risk, -1))
        else:
            consolidated_session_load_dict[body_part].merge(pickle.loads(pickle.dumps(body_part_injury_risk, -1)))

    return consolidated_session_load_dict


def aggregate_sld(session_load_dict):

    aggregated_sld = {}

    for body_part_side, body_part_functional_movement in session_load_dict.items():
        if body_part_side not in aggregated_sld:
            muscle_group = BodyPartLocation.get_muscle_group(body_part_side.body_part_location)
            if isinstance(muscle_group, BodyPartLocation):
                new_body_part_side = BodyPartSide(muscle_group, body_part_side.side)
                if new_body_part_side not in aggregated_sld:
                    aggregated_sld[new_body_part_side] = pickle.loads(pickle.dumps(body_part_functional_movement, -1))
                else:
                    existing_body_part_injury_risk = pickle.loads(pickle.dumps(session_load_dict[body_part_side], -1))
                    aggregated_sld[new_body_part_side].merge(existing_body_part_injury_risk)
            else:
                aggregated_sld[body_part_side] = pickle.loads(pickle.dumps(session_load_dict[body_part_side], -1))
        else:
            existing_body_part_injury_risk = pickle.loads(pickle.dumps(session_load_dict[body_part_side], -1))
            aggregated_sld[body_part_side].merge(existing_body_part_injury_risk)

    return aggregated_sld


def get_profiles():
    profile_1 = {
        # Andra
        'user_profile_id': 'andra_profile',
        'user_id': 'test_user_1',
        'user_age': 40,
        'user_gender': Gender.female,
        'user_weight': 55,
        'vo2_max': StandardErrorRange(lower_bound=41.7, observed_value=42.45, upper_bound=43.2),
        'activity_level': 6
    }

    # profile_2 = {
    #     'user_profile_id': 'profile_2',
    #     'user_id': 'test_user_2',
    #     'user_age': 35,
    #     'user_gender': Gender.male,
    #     'user_weight': 75,
    #     'vo2_max': None
    # }
    return [profile_1]

