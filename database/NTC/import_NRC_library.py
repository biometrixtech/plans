import os
import json
import pandas as pd
from models.planned_exercise import PlannedExercise, PlannedWorkout, PlannedWorkoutSection
from models.training_volume import StandardErrorRange, Assignment
from models.exercise import UnitOfMeasure
from models.movement_tags import Equipment

all_durations = []
all_distances = []
all_reps = []
class WorkoutParser(object):

    def __init__(self):
        self.workout_pd = None
        self.equipment_lookup = {}

        self.intensity_measure_units = {
            'pace',
            'rpe',
            'effort' #not yet used
        }

        self.intensity_measures_pace = {
            'none': 'none',
            'recovery jogs': 'recovery_jog',
            'long run': 'long_run',
            'comfortable run': 'comfortable_run',
            'easy run': 'easy_run',
            'warm up': 'warm_up',
            'cooldown': 'cooldown',
            'half marathon': 'half_marathon',
            '10k': '10k',
            '5k': '5k',
            'mile': 'mile',
            'speed': 'speed',
            'sprint': 'sprint',
        }

        self.pace_rpe_lookup = {
            'none': (None, 0, None),
            'recovery_jog': (2, None, 3),
            'long_run': (2, None,4),
            'comfortable_run': (3, None,4),
            'easy_run': (2, None, 4),
            'warm_up': (2, None, 4),
            'cooldown': (2, None, 4),
            'steady_state': (None, 5, None),
            'tempo_run': (6, None, 7),
            #'tempo_intervals': (4, None, 7),
            'half_marathon': (3, None, 4),
            '10k': (None, 6, None),
            '5k': (None, 7, None),
            'mile': (None, 9, None),
            'speed': (8, None, 9),
            'sprint': (9, None, 10),
        }

        self.pace_exercise_lookup = {
            "none": "jog",
            "recovery_jog": 'jog',
            "long_run": 'run',
            "comfortable_run": 'run',
            "easy_run": 'run',
            "warm_up": 'jog',
            "cooldown": 'jog',
            "steady_state":'run',
            "tempo_run": 'cruising',
            # "tempo_intervals": 'a',
            "half_marathon": 'run',
            "10k": 'run',
            "5k": 'cruising',
            "mile": 'cruising',
            "speed": 'sprint',
            "sprint": 'sprint'
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
            if self.is_valid(row[0]):
                if row[0] == 'workout_name':
                    workout.name = row['description'].replace('w/','with')
                if row[0] == 'average_minutes':
                    if self.is_valid(row['description']):
                        workout.duration = float(row['description']) * 60
                    elif self.is_valid(row['time']):
                        workout.duration = float(row['time']) * 60

                if row[0] == 'average_distance':
                    if self.is_valid(row['description']):
                        workout.distance = float(row['description'])
                    elif self.is_valid(row['distance']):
                        workout.distance = float(row['distance'])

                if row[0] == 'type':
                    if self.is_valid(row['description']):
                        workout.workout_type = row['description'].lower()

                # if row[0] == 'volume_measure':
                #     if self.is_valid(row['description']):
                #         if 'time' in row['description'].lower():
                #             if workout.distance is not None:
                #                 print('distance provided for time measure')
                #                 # raise ValueError
                #         elif 'distance' in row['description'].lower():
                #             if workout.duration is not None:
                #                 print('duration provided for distance measure')
                #                 raise ValueError

                if row['row_type'] == 'Block':
                    section = PlannedWorkoutSection()
                    section.name = row['description']
                    section.exercises = []
                    workout.sections.append(section)

                if row['row_type'] == 'Exercise':
                    ex = self.parse_exercise_row(row, workout.workout_type)
                    section.exercises.append(ex)

                # if row['row_type'] == 'intensity':
                #     intensity_measure = row.get('intensity_measure_units')
                #     if intensity_measure is not None and intensity_measure == 'sRPE':
                #         rpe_min = row.get('intensity_measure')
                #         rpe_max = row.get('max_intensity_measure')
                #         workout.rpe = self.get_assignment(rpe_min, rpe_max)
                # if row['row_type'] == 'rest_between_exercises':
                #     min_rest = row.get('time')
                #     max_rest = row.get('max_time')
                #     if self.is_valid(min_rest):
                #         min_rest = int(min_rest)
                #     else:
                #         min_rest = None
                #     if self.is_valid(max_rest):
                #         max_rest = int(max_rest)
                #     else:
                #         max_rest = None
                #     workout.rest_between_exercises = self.get_assignment(min_rest, max_rest)

        if write:
            workout_json = workout.json_serialise()
            directory = file.split('/')[-2]
            self.write_json(workout_json, workout.name, directory)
        return workout


    # def parse_equipment_lookup_row(self, row):
    #     equip_detail = {
    #         'external_weight_implement': row['external_weight_implement'],
    #         'intensity_measure_units': row['intensity_measure_units'],
    #         'intensity_measure': row['intensity_measure'],
    #         'max_intensity_measure': row['max_intensity_measure']
    #     }
    #
    #     self.equipment_lookup[row['description']] = equip_detail

    def parse_exercise_row(self, row, workout_type=None):
        ex = PlannedExercise()
        # if workout_type is not None:
        intensity_measure = row.get('intensity_measure_units')
        ex.name = row['description'].strip().lower()
        if self.is_valid(intensity_measure):
            if intensity_measure.lower().strip() == 'pace':
                intensity = row.get('intensity_measure')
                if self.is_valid(intensity):
                    intensity = ('_').join(intensity.lower().split(' '))
                    ex.name = self.pace_exercise_lookup.get(intensity)
                else:
                    intensity = row.get('max_intensity_measure')
                    if self.is_valid(intensity):
                        intensity = ('_').join(intensity.lower().split(' '))
                        ex.name = self.pace_exercise_lookup.get(intensity)

            elif intensity_measure.lower() == 'rpe':
                ex.name = 'run'
        # else:
        #     ex.name = row['description'].strip().lower()
        ex.movement_id = ex.name

        observed_duration = None
        max_duration = None
        observed_distance = None
        max_distance = None

        distance = row.get('distance', None)
        if distance is not None and distance != '':
            observed_distance = float(distance.replace('m', '').replace(',', ''))

        max_distance_val = row.get('max_distance', None)
        if max_distance_val is not None and max_distance_val != '':
            max_distance = float(distance.replace('m', '').replace(',', ''))

        time = row['time']
        max_time = row['max_time']
        if self.is_valid(time):
            # if 'm' in time:
            #     print(f"{time} in time")
            #     raise ValueError
            #     # observed_distance = int(time.replace('m', '').replace(',', ''))
            # else:
                observed_duration = self.get_sec(row['time'])
        if self.is_valid(max_time):
            if 'm' in max_time:
                pass
                # print(f"{max_time} in max_time")
                # raise ValueError
                # max_distance = int(max_time.replace('m', '').replace(',', ''))
            else:
                max_duration = self.get_sec(row['max_time'])

        ex.duration = self.get_assignment(observed_duration, max_duration)
        ex.distance = self.get_assignment(observed_distance, max_distance)

        if ex.duration is not None:
            ex.unit_of_measure = UnitOfMeasure.seconds
        elif ex.distance is not None:
            ex.unit_of_measure = UnitOfMeasure.meters

        incline = row.get('incline')
        if incline is not None and incline != '':
            if '%' in incline:
                incline = incline.replace('%', '')
            incline = float(incline) / 100
            ex.grade = Assignment(assigned_value=incline)

        # intensity_measurement_units = row.get('intensity_measurement_units')
        # if self.is_valid(intensity_measurement_units):
        #     intensity_measurement_units = intensity_measurement_units.lower()
        #     if intensity_measurement_units not in self.intensity_measure_units:
        #         print('invalid intensity measurement unit')
        #         raise ValueError

        intensity_measure_unit = row.get('intensity_measure_units')
        if self.is_valid(intensity_measure_unit):
            if intensity_measure_unit == 'RPE':
                min_rpe = row.get('intensity_measure')
                max_rpe = row.get('max_intensity_measure')
                if self.is_valid(min_rpe):
                    min_rpe = int(min_rpe) if min_rpe is not None else None
                if self.is_valid(max_rpe):
                    max_rpe = int(max_rpe) if min_rpe is not None else None
                if min_rpe is not None and max_rpe is not None:
                    ex.rpe = StandardErrorRange(lower_bound=min_rpe, upper_bound=max_rpe)
                elif min_rpe is not None and max_rpe is None:
                    ex.rpe = StandardErrorRange(observed_value=min_rpe)
                elif min_rpe is None and max_rpe is not None:
                    ex.rpe = StandardErrorRange(observed_value=max_rpe)
            elif intensity_measure_unit.lower() == 'pace':
                min_rpe_tuple = None
                max_rpe_tuple = None
                min_rpe = StandardErrorRange()
                max_rpe = StandardErrorRange()
                ex.rpe = StandardErrorRange()

                min_measure = row.get('intensity_measure')
                if min_measure is not None:
                    if min_measure.lower() in self.intensity_measures_pace:
                        min_pace_value = self.intensity_measures_pace[min_measure.lower()]
                        min_rpe_tuple = self.pace_rpe_lookup[min_pace_value]

                max_measure = row.get('max_intensity_measure')
                if max_measure is not None:
                    if max_measure.lower() in self.intensity_measures_pace:
                        max_pace_value = self.intensity_measures_pace[max_measure.lower()]
                        max_rpe_tuple = self.pace_rpe_lookup[max_pace_value]

                if min_rpe_tuple is not None:
                    min_rpe = StandardErrorRange(lower_bound=min_rpe_tuple[0], observed_value=min_rpe_tuple[1],
                                                 upper_bound=min_rpe_tuple[2])
                if max_rpe_tuple is not None:
                    max_rpe = StandardErrorRange(lower_bound=max_rpe_tuple[0], observed_value=max_rpe_tuple[1],
                                                 upper_bound=max_rpe_tuple[2])

                if min_rpe.lower_bound is not None and max_rpe.lower_bound is not None:
                    ex.rpe.lower_bound = min(min_rpe.lower_bound, max_rpe.lower_bound)
                elif min_rpe.lower_bound is None and max_rpe.lower_bound is not None:
                    ex.rpe.lower_bound = max_rpe.lower_bound
                elif min_rpe.lower_bound is not None and max_rpe.lower_bound is None:
                    ex.rpe.lower_bound = min_rpe.lower_bound

                if min_rpe.observed_value is not None and max_rpe.observed_value is not None:
                    ex.rpe.observed_value = max(min_rpe.observed_value, max_rpe.observed_value)
                elif min_rpe.observed_value is None and max_rpe.observed_value is not None:
                    ex.rpe.observed_value = max_rpe.observed_value
                elif min_rpe.observed_value is not None and max_rpe.observed_value is None:
                    ex.rpe.observed_value = min_rpe.observed_value

                if min_rpe.upper_bound is not None and max_rpe.upper_bound is not None:
                    ex.rpe.upper_bound = max(min_rpe.upper_bound, max_rpe.upper_bound)
                elif min_rpe.upper_bound is None and max_rpe.upper_bound is not None:
                    ex.rpe.upper_bound = max_rpe.upper_bound
                elif min_rpe.upper_bound is not None and max_rpe.upper_bound is None:
                    ex.rpe.upper_bound = min_rpe.upper_bound

                if ex.rpe.upper_bound is not None and ex.rpe.observed_value is not None:
                    if ex.rpe.upper_bound < ex.rpe.observed_value:
                        ex.rpe.upper_bound = ex.rpe.observed_value

                if ex.rpe.upper_bound is not None and ex.rpe.lower_bound is not None:
                    if ex.rpe.upper_bound < ex.rpe.lower_bound:
                        ex.rpe.upper_bound = ex.rpe.lower_bound

                if ex.rpe.observed_value is not None and ex.rpe.lower_bound is not None:
                    if ex.rpe.observed_value < ex.rpe.lower_bound:
                        observed_value = max(ex.rpe.observed_value, ex.rpe.lower_bound)
                        lower_bound = min(ex.rpe.observed_value, ex.rpe.lower_bound)
                        ex.rpe.observed_value = observed_value
                        ex.rpe.lower_bound = lower_bound

        return ex

    def get_sec(self, time_str):
        """Get Seconds from time."""
        if ':' in time_str:
            m, s = time_str.split(':')
            return int(m) * 60 + int(s)
        else:
            return 60 * int(time_str)

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
        file_name = os.path.join(f"libraries/NRC_workouts/{directory}/{workout_name}.json")
        if not os.path.exists(f"libraries/NRC_workouts/{directory}"):
            os.makedirs(f"libraries/NRC_workouts/{directory}")
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
            if ex_name not in ['rest', 'recover', 'warm up']:
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
                    if exercise.duration.assigned_value > 7200:
                        print(f'duration too long: {exercise.duration.assigned_value}')
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
                    if exercise.distance.min_value > 43000:
                        print(f'distance too long: {exercise.distance.min_value}')
                    elif exercise.distance.min_value < 10:
                        print(f'distance too short: {exercise.distance.min_value}')
                if exercise.distance.assigned_value is not None:
                    all_distances.append(exercise.distance.assigned_value)
                    if exercise.distance.assigned_value > 43000:
                        print(f'distance too long: {exercise.distance.assigned_value}')
                    elif exercise.distance.assigned_value < 10:
                        print(f'distance too short: {exercise.distance.assigned_value}')
                if exercise.distance.max_value is not None:
                    all_distances.append(exercise.distance.max_value)
                    if exercise.distance.max_value > 43000:
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
    dirs = os.listdir('NRC_workouts/')
    for dir in dirs:
        if 'DS_Store' not in dir:
            files = os.listdir(f"NRC_workouts/{dir}")
            for file in files:
                if '8K' not in file:
                    continue
                if 'DS_Store' not in file and 'included in this' not in file and 'Workouts in this' not in file:
                    try:
                        workout = WorkoutParser().load_data(f"NRC_workouts/{dir}/{file}", write=False)
                        validate_exercises(workout, exercise_names)
                        workout_json = workout.json_serialise()
                        workout_2 = PlannedWorkout.json_deserialise(workout_json)
                    except ValueError as e:
                        print(e)
                        print(dir, file)
    # print(f"duration: {min(all_durations), max(all_durations)}")
    # print(f"distance: {min(all_distances), max(all_distances)}")
    # print(f"reps: {min(all_reps), max(all_reps)}")