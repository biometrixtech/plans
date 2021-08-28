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
from models.session import SessionFactory, SessionType
import datetime
import pickle
import json, os


def create_completed_session_details(profile, workout):

    session_json = create_session_only(workout, session_RPE=None)
    session = create_session(SessionType.mixed_activity, session_json)

    proc = WorkoutProcessor(
            user_weight=profile['user_weight'],
            user_age=profile['user_age'],
            gender= profile['user_gender'],
            vo2_max=profile['vo2_max'],
            strength_proficiency=ProficiencyLevel(profile['strength_proficiency']),
            power_proficiency=ProficiencyLevel(profile['power_proficiency'])
    )
    proc.process_workout(session)
    session_string = get_session_string(session)
    return session_string
    # session = create_completed_workout_load(session, profile['user_profile_id'])


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


def get_workouts():
    all_workouts = {}
    print(os.getcwd())
    # base_path = '../../database/andra_garmin/workouts/aug-nov2019_segmented/'
    base_path = 'workouts/aug-nov2019_segmented'
    files = os.listdir(base_path)
    # for dir in dirs:
    #     if '.DS_' in dir:
    #         continue
    #     files = os.listdir(f"{base_path}/{dir}")
    for file in files:
        if '.json' in file:
            with open(f'{base_path}/{file}', 'r') as f:
                workout = json.load(f)
                all_workouts[workout['program_module_id']] = workout
    return all_workouts



def get_session_string(session):
    # workout_header_line = (
    #     "event_date_time, id,description, distance, duration_minutes, power_load_highest, rpe_load_highest, training_volume, target_training_exposures")
    session_string = str(session.event_date) + "," + session.id + "," + session.description + "," + str(session.distance) + "," + str(session.duration_minutes) + ","
    session_string += str(session.session_RPE) + "," + str(session.power_load.highest_value()) + "," + str(session.rpe_load.highest_value()) + "," + str(session.training_volume) + ","
    session_string += get_training_exposure_string(session)

    return session_string

def get_training_exposure_string(session):
    training_string = ""
    exposure_count = 0
    for training_exposure in session.training_exposures:
        training_string += training_exposure.detailed_adaptation_type.name + "; " + str(training_exposure.rpe.highest_value()) + ";" + str(training_exposure.volume.highest_value()) + ";"
        exposure_count += 1
        if exposure_count < len(session.training_exposures):
            training_string += "||"

    return training_string


def create_session_only(workout, session_RPE):
    # workout = read_json(file_name, user_name)
    data = {
        "event_date": workout['event_date_time'],
        "session_type": 7,
        "duration_minutes": workout['duration_seconds'] / 60,
        "description": workout['program_module_id'],
        # "calories": 100,
        "distance": workout['distance'],
        "session_RPE": session_RPE,
        "end_date": workout['workout_sections'][0]['end_date_time'],
        # "hr_data": {{hr_data}},
        "workout_program_module": workout
    }
    return data


def create_session(session_type, data):
    session = SessionFactory().create(SessionType(session_type))
    update_session(session, data)
    return session


def update_session(session, data):
    for key, value in data.items():
        setattr(session, key, value)


if __name__ == '__main__':
    profile_1 = {
        # Andra
        'user_profile_id': 'andra_profile',
        'user_id': 'test_user_1',
        'user_age': 42,
        'user_gender': Gender.female,
        'user_weight': 55,  # 125 lbs
        'height': 1.7,
        'vo2_max': StandardErrorRange(lower_bound=41.7, observed_value=42.45, upper_bound=43.2),
        'activity_level': 6,
        'strength_proficiency': 2,
        'power_proficiency': 3
    }
    workout_output = open('outputs/workouts' + ".csv", 'w')
    workout_header_line = ("event_date_time, id,description, distance, duration_minutes, session_rpe, "
                           "power_load_highest, rpe_load_highest,  training_volume, target_training_exposures")
    workout_output.write(workout_header_line + '\n')
    all_workouts = get_workouts()
    all_workouts = list(all_workouts.values())
    all_workouts = sorted(all_workouts, key=lambda x: x['event_date_time'])

    for workout in all_workouts:
        session_string = create_completed_session_details(profile_1, workout)
        workout_output.write(session_string + '\n')

    workout_output.close()
