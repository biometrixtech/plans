import database.september_demo.set_up_config
from database.september_demo.user_profiles import profiles

from logic.workout_processing import WorkoutProcessor
from models.session import PlannedSession
from models.movement_tags import Gender, ProficiencyLevel
from models.planned_exercise import PlannedWorkout, PlannedWorkoutLoad
from models.session_functional_movement import SessionFunctionalMovement
from models.training_volume import StandardErrorRange
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.body_parts import BodyPart, BodyPartFactory
from datastores.planed_workout_load_datastore import PlannedWorkoutLoadDatastore
import datetime
import pickle
import json, os
import requests


def login_user(email, password="Fathom123!"):
    body = {"password": password, "personal_data": {"email": email}}
    headers = {"Content-Type": "application/json"}
    url = "http://apis.{env}.fathomai.com/users/2_4/user/login".format(env=os.environ['ENVIRONMENT'])
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response.json()['user']['id'], response.json()['authorization']['jwt']


def create_planned_workout_load(session, user_profile_id):
    session_functional_movement = SessionFunctionalMovement(session, {})
    session_functional_movement.process(event_date=datetime.datetime.now(), load_stats=None)
    consolidated_dict = get_consolidated_dict(session_functional_movement.session_load_dict)

    workout = PlannedWorkoutLoad(workout_id=session.workout.program_module_id)
    workout.name = session.workout.name
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
    # save to mongo
    print(f'completed processing: {session.workout.name}')
    PlannedWorkoutLoadDatastore().put(workout)
    return workout


def create_planned_session_detail(profile, planned_workout):
    # planned_workout_json = planned_workout.json_serialise()

    session = PlannedSession()
    session.event_date = datetime.datetime.now()
    session.user_id = profile['user_id']
    session.workout = PlannedWorkout.json_deserialise(planned_workout)

    proc = WorkoutProcessor(
            user_weight=profile['user_weight'],
            user_age=profile['user_age'],
            gender= Gender[profile['user_gender']],
            vo2_max=StandardErrorRange(observed_value=profile['vo2_max']),
            strength_proficiency=ProficiencyLevel[profile['strength_proficiency']],
            power_proficiency=ProficiencyLevel[profile['power_proficiency']]
    )
    proc.process_planned_workout(session)
    planned_workout_load = create_planned_workout_load(session, profile['user_profile_id'])


def get_consolidated_dict(session_load_dict):

    aggregated_session_load_dict = aggregate_sld(session_load_dict)

    consolidated_session_load_dict = {}

    body_part_factory = BodyPartFactory()

    for body_part_side, body_part_functional_movement in aggregated_session_load_dict.items():
        body_part = body_part_factory.get_body_part(body_part_side)
        new_body_part_side = BodyPartSide(body_part.location, 0)
        if body_part not in consolidated_session_load_dict:
            consolidated_session_load_dict[new_body_part_side] = pickle.loads(pickle.dumps(body_part_functional_movement, -1))
        else:
            consolidated_session_load_dict[new_body_part_side].merge(pickle.loads(pickle.dumps(body_part_functional_movement, -1)))

    return consolidated_session_load_dict


def aggregate_sld(session_load_dict):

    aggregated_sld = {}

    for body_part_side, body_part_functional_movement in session_load_dict.items():
        if body_part_side not in aggregated_sld:
            muscle_group = BodyPartLocation.get_muscle_group(body_part_side.body_part_location)
            if isinstance(muscle_group, BodyPartLocation):
                new_body_part_side = BodyPartSide(muscle_group, body_part_side.side)
                body_part_functional_movement.body_part_side = new_body_part_side
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


def get_planned_workouts(lib):
    all_workouts = {}

    if lib == 'NTC':
        base_path = f'../../database/ntc/libraries/workouts/'
    else:
        base_path = f'../../database/ntc/libraries/NRC_workouts/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    workout = json.load(f)
                    all_workouts[workout['program_module_id']] = workout
    return all_workouts



if __name__ == '__main__':
    for profile in profiles.values():
        user_email = f"{profile['user_profile_id']}@300.com"
        user_id, _ = login_user(user_email)
        profile['user_id'] = user_id
        for lib in ['NTC', 'NRC']:
            all_workouts = get_planned_workouts(lib)
            for workout in all_workouts.values():
                create_planned_session_detail(profile, workout)