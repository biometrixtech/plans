import database.NTC.set_up_config
import os, string
import json
import pandas as pd
from models.planned_exercise import PlannedExercise, PlannedWorkout, PlannedWorkoutSection
from models.training_volume import StandardErrorRange, Assignment
from models.exercise import WeightMeasure
from models.movement_tags import Equipment
from utils import convert_workout_text_to_id

from datastores.workout_datastore import WorkoutDatastore
from database.NTC.create_processed_workouts import create_planned_session_detail

all_durations = []
all_distances = []
all_reps = []
class WorkoutParser(object):
    def __init__(self):
        self.workout_pd = None
        self.equipment_lookup = {}

        self.weight_measure_lookup = {
            'perc_rep_max': 'percent_rep_max',
            'perc_bodyweight': 'percent_bodyweight'
        }
        self.equipment_name_lookup = {
            'single_dumbbells': 'single_dumbbell'
        }


    def load_data(self, file, write=False):
        """

        :param files: list of files to import
        :return:
        """
        self.workout_pd = pd.read_csv(file, keep_default_na=False)
        if 'workout' in self.workout_pd.columns or 'Workout' in self.workout_pd.columns:
            self.workout_pd = pd.read_csv(file, keep_default_na=False, skiprows=1)
        self.workout_pd.rename(columns={'Unnamed: 0': 'row_type'}, inplace=True)

        workout = PlannedWorkout()
        workout.sections = []
        section = PlannedWorkoutSection()
        for index, row in self.workout_pd.iterrows():
            if self.is_valid(row['row_type']):
                if row['row_type'] == 'workout_name':
                    workout.name = row['description'].replace('w/','with')
                    workout.program_module_id = convert_workout_text_to_id(row['description'])
                    workout.program_id = 'ntc'

                if row['row_type'] == 'average_minutes':
                    if self.is_valid(row['description']):
                        workout.duration = int(row['description']) * 60
                    elif self.is_valid(row['time']):
                        workout.duration = int(row['time']) * 60

                if row['row_type'] == 'intensity':
                    intensity_measure = row.get('intensity_measure_units')
                    if intensity_measure is not None and intensity_measure == 'sRPE':
                        rpe_min = float(row.get('intensity_measure'))
                        rpe_max = float(row.get('max_intensity_measure'))
                        workout.rpe = self.get_assignment(rpe_min, rpe_max)
                if row['row_type'] == 'rest_between_exercises':
                    min_rest = row.get('time')
                    max_rest = row.get('max_time')
                    if self.is_valid(min_rest):
                        min_rest = int(min_rest)
                    else:
                        min_rest = None
                    if self.is_valid(max_rest):
                        max_rest = int(max_rest)
                    else:
                        max_rest = None
                    workout.rest_between_exercises = self.get_assignment(min_rest, max_rest)

                # if row['row_type'] == 'equipment':
                #     equipments = row['description'].lower().split('.')
                #     equipments = [equip.strip() for equip in equipments]
                #     equipments = [equip for equip in equipments if equip != 'none']  # These equipments are not in our enum. Will be text only.
                #     workout.equipments = equipments

                if 'equipment_' in row['row_type']:
                    self.parse_equipment_lookup_row(row)

                if row['row_type'] == 'Block':
                    section = PlannedWorkoutSection()
                    section.name = row['description']
                    section.exercises = []
                    workout.sections.append(section)

                if row['row_type'] == 'Exercise':
                    ex = self.parse_exercise_row(row)
                    section.exercises.append(ex)
        if write:
            # WorkoutDatastore().put(workout)
            workout_json = workout.json_serialise()
            directory = file.split('/')[-2]
            self.write_json(workout_json, workout.name, directory)
        return workout


    def parse_equipment_lookup_row(self, row):
        equip_detail = {
            'external_weight_implement': row['external_weight_implement'],
            'intensity_measure_units': row['intensity_measure_units'],
            'intensity_measure': row['intensity_measure'],
            'max_intensity_measure': row['max_intensity_measure']
        }

        self.equipment_lookup[row['description']] = equip_detail

    def parse_exercise_row(self, row):
        ex = PlannedExercise()
        ex.name = row['description'].strip().lower()
        ex.movement_id = ex.name

        observed_duration = None
        max_duration = None
        observed_distance = None
        max_distance = None
        count = row['count']
        if self.is_valid(count):
            # if 'm' in count:
            #     print('m in count')
            #     raise ValueError
            #     # observed_distance = int(count.replace('m', '').replace(',', ''))
            # else:
                ex.reps_per_set = int(count)

        distance = row.get('distance', None)
        if distance is not None and distance != '':
            observed_distance = int(distance.replace('m', '').replace(',', ''))
        time = row['time']
        max_time = row['max_time']
        if self.is_valid(time):
            # if 'm' in time:
            #     print(f"{time} in time")
            #     raise ValueError
            #     # observed_distance = int(time.replace('m', '').replace(',', ''))
            # else:
                observed_duration = int(row['time'])
        if self.is_valid(max_time):
            if 'm' in max_time:
                pass
                # print(f"{max_time} in max_time")
                # raise ValueError
                # max_distance = int(max_time.replace('m', '').replace(',', ''))
            else:
                max_duration = int(row['max_time'])
        ex.duration = self.get_assignment(observed_duration, max_duration)
        ex.distance = self.get_assignment(observed_distance, max_distance)

        equip = row.get('external_weight_implement')
        if self.is_valid(equip):
            equip_detail = self.equipment_lookup.get(equip)
            if equip_detail is not None:
                min_weight = equip_detail.get('intensity_measure', '')
                if min_weight == '':
                    min_weight = None
                else:
                    min_weight = int(min_weight)
                max_weight = equip_detail.get('max_intensity_measure', '')
                if max_weight == '':
                    max_weight = None
                else:
                    max_weight = int(max_weight)

                ex.weight = self.get_assignment(min_weight, max_weight)
                weight_measure_name = self.weight_measure_lookup.get(equip_detail['intensity_measure_units']) or equip_detail['intensity_measure_units']
                ex.weight_measure = WeightMeasure[weight_measure_name]

                equipment_name = self.equipment_name_lookup.get(equip_detail['external_weight_implement']) or equip_detail['external_weight_implement']
                try:
                    ex.equipments = [Equipment[equipment_name]]
                except:
                    print(equipment_name)
            # else:
            #     pass
                # print(equip)
                # raise ValueError()
        intensity_measure_unit = row.get('intensity_measure_units')
        if self.is_valid(intensity_measure_unit):
            if intensity_measure_unit == 'RPE':
                min_rpe = row.get('intensity_measure')
                max_rpe = row.get('max_intensity_measure')
                min_rpe = int(min_rpe) if min_rpe is not None else None
                max_rpe = int(max_rpe) if min_rpe is not None else None
                if min_rpe is not None and max_rpe is not None:
                    ex.rpe = StandardErrorRange(lower_bound=min_rpe, upper_bound=max_rpe)
                elif min_rpe is not None and max_rpe is None:
                    ex.rpe = StandardErrorRange(observed_value=min_rpe)
                elif min_rpe is None and max_rpe is not None:
                    ex.rpe = StandardErrorRange(observed_value=max_rpe)
            elif intensity_measure_unit == 'normalized_pace':
                pass
            elif intensity_measure_unit == 'perc_rep_max':
                pass
            elif intensity_measure_unit == 'perc_bodyweight':
                pass

        return ex

    @staticmethod
    def get_assignment(min_value, max_value):
        if min_value is not None and max_value is not None:
            assignment = Assignment(min_value=min_value, max_value=max_value)
        elif min_value is not None:
            assignment = Assignment(assigned_value=min_value)
        elif max_value is not None:
            assignment = Assignment(assigned_value=max_value)
        else:
            assignment = None
        return assignment

    def write_json(self, workout, workout_name, directory):
        json_string = json.dumps(workout, indent=4)
        file_name = os.path.join(f"libraries/workouts/{directory}/{workout_name}.json")
        if not os.path.exists(f"libraries/workouts/{directory}"):
            os.makedirs(f"libraries/workouts/{directory}")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

    @staticmethod
    def is_valid(value):
        if value is not None and value != "":
            return True
        return False

def read_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data

def validate_exercises(workout, library_exercise_names):
    for section in workout.sections:
        for exercise in section.exercises:
            ex_name = exercise.name
            if ex_name not in ['rest', 'recover']:
                if ex_name not in library_exercise_names:
                    print(f"missing exercise: {exercise.name}, {section.name}")
                    raise ValueError
            if exercise.duration is not None:
                if exercise.duration.min_value is not None:
                    all_durations.append(exercise.duration.min_value)
                    if exercise.duration.min_value > 150:
                        print(f'duration too long: {exercise.duration.min_value}')
                        raise ValueError()
                    elif exercise.duration.min_value < 10:
                        print(f'duration too short: {exercise.duration.min_value}')
                        raise ValueError()
                if exercise.duration.assigned_value is not None:
                    all_durations.append(exercise.duration.assigned_value)
                    if exercise.duration.assigned_value > 150:
                        print(f'duration too short: {exercise.duration.assigned_value}')
                        raise ValueError()
                    elif exercise.duration.assigned_value < 10:
                        print(f'duration too short: {exercise.duration.assigned_value}')
                        raise ValueError()
                if exercise.duration.max_value is not None:
                    all_durations.append(exercise.duration.max_value)
                    if exercise.duration.max_value > 150:
                        print(f'duration too long: {exercise.duration.max_value}')
                        raise ValueError()
                    elif exercise.duration.max_value < 10:
                        print(f'duration too short: {exercise.duration.max_value}')
                        raise ValueError()
            if exercise.distance is not None:
                if exercise.distance.min_value is not None:
                    all_distances.append(exercise.distance.min_value)
                    if exercise.distance.min_value > 5000:
                        print(f'distance too long: {exercise.distance.min_value}')
                    elif exercise.distance.min_value < 10:
                        print(f'distance too short: {exercise.distance.min_value}')
                if exercise.distance.assigned_value is not None:
                    all_distances.append(exercise.distance.assigned_value)
                    if exercise.distance.assigned_value > 5000:
                        print(f'distance too long: {exercise.distance.assigned_value}')
                    elif exercise.distance.assigned_value < 10:
                        print(f'distance too short: {exercise.distance.assigned_value}')
                if exercise.distance.max_value is not None:
                    all_distances.append(exercise.distance.max_value)
                    if exercise.distance.max_value > 5000:
                        print(f'distance too long: {exercise.distance.max_value}')
                    elif exercise.distance.max_value < 10:
                        print(f'distance too short: {exercise.distance.max_value}')
            if exercise.reps_per_set is not None:
                all_reps.append(exercise.reps_per_set)
                if exercise.reps_per_set > 50:
                    print(f'reps too long: {exercise.reps_per_set}')
                # elif exercise.reps_per_set < 5:
                #     print(f'reps too short: {exercise.reps_per_set}, {exercise.name}')
                #     raise ValueError
            if exercise.duration is not None and exercise.reps_per_set is not None:
                print('here')
            if exercise.duration is not None and exercise.distance is not None:
                print('here')
            if exercise.reps_per_set is not None and exercise.duration is not None:
                print('here')

if __name__ == '__main__':

    exercises = read_json('libraries/nike_exercises.json')
    exercise_names = [ex['name'] for ex in exercises]
    exercise_names.sort()
    dirs = os.listdir('workouts/')
    for dir in dirs:
        if 'DS_Store' not in dir:
            files = os.listdir(f"workouts/{dir}")
            for file in files:
                if 'DS_Store' not in file and 'included in this' not in file  and 'Runner Warm-Up' not in file:
                    try:
                        workout = WorkoutParser().load_data(f"workouts/{dir}/{file}", write=True)
                        # validate_exercises(workout, exercise_names)
                        # workout_json = workout.json_serialise()
                        # workout_2 = PlannedWorkout.json_deserialise(workout_json)
                        create_planned_session_detail(workout)
                    except ValueError as e:
                        print(dir, file)
    # print(f"duration: {min(all_durations), max(all_durations)}")
    # print(f"distance: {min(all_distances), max(all_distances)}")
    # print(f"reps: {min(all_reps), max(all_reps)}")