from pymongo import MongoClient
import pandas as pd
import re
import json
import copy

cycles_to_remove = ['juno', 'raven', 'cheetah', 'revolution', 'hervor', 'janus', 'ripley', 'eowyn', 'everdeen',
                    'zelda', 'freyr', 'floki', 'odin', 'thor', 'knuckles', 'glaurang', 'thunderbird',
                    'legionnaire', 'viper', 'hermes', 'dreadnaught', 'lazarus', 'thunderdome', 'phoenix', 'tora', 'chimera', 'jester']


def write_json(data, file_name):
    json_string = json.dumps(data, indent=4)
    print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()


def read_json(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)


def get_mongo_database():
    host = "soflete-swift-shard-00-00-ww3r0.gcp.mongodb.net:27017,soflete-swift-shard-00-01-ww3r0.gcp.mongodb.net:27017,soflete-swift-shard-00-02-ww3r0.gcp.mongodb.net:27017"
    replicaset = "Soflete-Swift-shard-0"
    mongo_database = "soflete"
    user = "paul_laforge"
    password = "2Jgtbedi3J4Bs2Pv"

    mongo_client = MongoClient(
            host,
            replicaset=replicaset if replicaset != '---' else None,
            ssl=True,
            serverSelectionTimeoutMS=10000,
    )
    _database = mongo_client[mongo_database]
    _database.authenticate(user, password, mechanism='SCRAM-SHA-1', source='admin')

    return _database


def get_soflete_movements():
    database = get_mongo_database()
    collection = database['movements']
    cursor = list(collection.find())
    all_movements = []
    for mov in cursor:
        movement = {}
        movement['id'] = mov['_id']
        movement['name'] = mov['name']
        movement['youtube_link'] = mov.get('url', '')
        all_movements.append(movement)
    movements_pd = pd.DataFrame(all_movements)
    movements_pd.to_csv('soflete_movements.csv', columns=['id', 'name', 'youtube_link'])


def get_soflete_exercises():
    database = get_mongo_database()
    collection = database['exercises']
    cursor = list(collection.find({},
                                  {'name': 1, "defaultMetricValues": 1, "sets": 1,
                                   "setsAndReps": 1, "metricLabel": 1, "_movement": 1,
                                   'baseYLabel': 1, "baseYValue": 1, "xLabel": 1,
                                   "xValue": 1}))
    all_exercises = []
    metrics_list = []

    for cur in cursor:
        exercise = {}
        exercise['id'] = cur['_id']
        exercise['name'] = cur['name']
        exercise['movement'] = cur.get('_movement')
        exercise['sets'] = cur.get('sets', "")
        exercise['setsAndReps'] = cur.get('setsAndReps', "")
        exercise['metricLabel'] = cur.get('metricLabel', "")
        exercise['baseYLabel'] = cur.get('baseYLabel', "")
        exercise['baseYValue'] = cur.get('baseYValue', "")
        exercise['xLabel'] = cur.get('xLabel', "")
        exercise['xValue'] = cur.get('xValue', "")
        exercise['weighted'] = False
        default_metric_values = cur.get('defaultMetricValues', [])

        if len(default_metric_values) > 0:
            for metric in default_metric_values:
                if "weight" in metric['metricType'].lower():
                    exercise['weighted'] = True
                    continue
            metrics_list = convert_default_metric_values(exercise['id'], exercise['name'], default_metric_values, metrics_list)

        all_exercises.append(exercise)
    exercises_pd = pd.DataFrame(all_exercises)
    exercises_pd.to_csv('soflete_exercises_detailed.csv', index=False, columns=['id', 'name', 'movement', 'xLabel', 'xValue', 'metricLabel',
                                                                                'baseYLabel', 'baseYValue', 'sets', 'setsAndReps', 'weighted'])
    metrics_pd = pd.DataFrame(metrics_list)
    metrics_pd.to_csv('soflete_exercises_metrics.csv', index=False)


def convert_default_metric_values(id, name, default_metric_values_array, metrics_list):

    for m in range(0, len(default_metric_values_array)):

        metrics = {}
        metrics['id'] = id
        metrics['name'] = name
        metrics['default_metrics_type'] = default_metric_values_array[m]["metricType"]
        metrics['default_metrics_value'] = default_metric_values_array[m]["values"][0]

        metrics_list.append(metrics)

    return metrics_list


def get_soflete_sections():
    database = get_mongo_database()
    collection = database['sections']
    cursor = list(collection.find({}, {"name": 1, "_exercises": 1}))
    all_sections = []
    for cur in cursor:
        section = {}
        section['id'] = cur['_id']
        section['name'] = cur['name']
        section['exercises'] = ''
        exercises = []
        for ex in cur.get('_exercises', []):
            exercises.append(str(ex))
        section['exercises'] = ",".join(exercises)
        all_sections.append(section)
    sections_pd = pd.DataFrame(all_sections)
    sections_pd.to_csv('soflete_sections.csv', index=False, columns = ['id', 'name', 'exercises'])


def get_soflete_workouts():
    database = get_mongo_database()

    workout_collection = database['workouts']
    cursor = list(workout_collection.find({}, {"name": 1, "_program": 1, "_sections": 1}))
    all_workouts = []
    for cur in cursor:
        workout = {}
        workout['id'] = cur['_id']
        workout['name'] = cur['name']
        sections = []
        for section in cur.get('_sections', []):
            sections.append(str(section))
        workout['sections'] = ','.join(sections)
        all_workouts.append(workout)
    workouts_pd = pd.DataFrame(all_workouts)
    workouts_pd.to_csv('soflete_workouts.csv', index=False, columns=['id', 'name', 'sections'])


def get_soflete_programs():
    database = get_mongo_database()
    program_collection = database['programs']
    prog_cursor = list(program_collection.find({}, {"name": 1, "_id": 1, "dayMap": 1}))
    all_programs = {}
    for cur in prog_cursor:
        program = {}
        program['id'] = str(cur['_id'])
        program['name'] = cur['name']
        if program['name'].lower().strip() not in cycles_to_remove:
            if cur.get('dayMap') is not None:
                daymap = cur['dayMap']
                program['workouts'] = {}
                for i, workout in daymap.items():
                    i = int(i)
                    if workout['_workout'] is not None:
                        week = ((i - 1) // 7) + 1
                        day = i % 7
                        if day == 0:
                            day = 7
                        day_map = {'id': workout['_workout'],
                                   'week': week,
                                   'day': day}
                        program['workouts'][workout['_workout']] = day_map
                all_programs[str(cur['_id'])] = program

    write_json(all_programs, 'soflete_programs.json')


def get_detailed_programs_with_sections_exercises():
    programs = read_json('soflete_programs.json')
    assigned_workout_ids = []
    for id, program in programs.items():
        assigned_workout_ids.extend(program['workouts'].keys())
    workouts, assigned_section_ids = get_assigned_workouts(assigned_workout_ids)
    sections, assigned_exercise_ids = get_assigned_sections(assigned_section_ids)

    # get eligible exercises
    exercises_pd = pd.read_csv('soflete_exercises_detailed.csv')
    assigned_exercises = exercises_pd.loc[exercises_pd['id'].isin(assigned_exercise_ids), :]
    assigned_exercises.to_csv('soflete_exercises_detailed_assigned.csv', columns=['id', 'name', 'movement', 'xLabel', 'xValue', 'metricLabel',
                                                                                  'baseYLabel', 'baseYValue', 'sets', 'setsAndReps', 'weighted'], index=False)
    assigned_exercise_ids = assigned_exercises['id'].values

    counter = 0
    missing_exercises = []
    for id, program in programs.items():
        counter += 1
        for id, workout in program['workouts'].items():
            workout_sections = {}
            section_ids = workouts[id]
            for section_id in section_ids:
                section = sections[section_id]
                for exercise_id in section['exercises']:
                    if exercise_id not in assigned_exercise_ids:
                        missing_exercise = {'cycle':program['name'],
                                            'week': workout['week'],
                                            'day': workout['day'],
                                            'section': section['name'],
                                            'exercise': exercise_id}
                        missing_exercises.append(missing_exercise)
                workout_sections[section_id] = section
            workout['sections'] = workout_sections
    missing_exercises = pd.DataFrame(missing_exercises)
    missing_exercises.to_csv('soflete_exercises_missing_in_database.csv', columns=['cycle', 'week', 'day', 'section', 'exercise'], index=False)
    write_json(programs, 'soflete_programs_detailed.json')


def get_assigned_workouts(assigned_workout_ids):
    # get assigned workouts
    workouts_pd =  pd.read_csv('soflete_workouts.csv')
    assigned_workouts = workouts_pd.loc[workouts_pd['id'].isin(assigned_workout_ids), :]

    workouts = {}
    assigned_section_ids = []
    for i, row in assigned_workouts.iterrows():
        if isinstance(row['sections'], str):
            sections = row['sections'].split(',')
        else:
            sections = []
        workouts[row['id']] = sections
        assigned_section_ids.extend(sections)

    write_json(workouts, 'soflete_workouts.json')
    return workouts, assigned_section_ids


def get_assigned_sections(assigned_section_ids):
    # get assigned sections
    sections_pd =  pd.read_csv('soflete_sections.csv')
    assigned_sections = sections_pd.loc[sections_pd['id'].isin(assigned_section_ids), :]

    sections = {}
    assigned_exercise_ids = set()
    for i, row in assigned_sections.iterrows():
        if isinstance(row['exercises'], str):
            exercises = row['exercises'].split(',')
        else:
            exercises = []
        sections[row['id']] = {
            'id': row['id'],
            'name': row['name'],
            'exercises': exercises
        }
        assigned_exercise_ids.update(exercises)

    write_json(sections, 'soflete_sections.json')
    return sections, assigned_exercise_ids


def get_exercise_assignments():
    eligible_exercises = pd.read_csv('soflete_exercises_detailed_assigned.csv')
    movements_pd = pd.read_csv('movement_library_soflete.csv', skiprows=1)
    all_movement_ids = movements_pd['id'].values

    programs = read_json('soflete_programs_detailed.json')

    assigned_movement_ids = set()
    exercises = {}
    for i, row in eligible_exercises.iterrows():
        movement = row['movement']
        if isinstance(movement, str):
            assigned_movement_ids.add(movement)
        exercises[row['id']] = {'id': row['id'],
                                'name': row['name'],
                                'movement': row['movement'],
                                'metricLabel': row['metricLabel'],
                                'xLabel': row['xLabel'],
                                'xValue': row['xValue'],
                                'baseYLabel': row['baseYLabel'],
                                'baseYValue': row['baseYValue'],
                                'sets': row['sets'],
                                'setsAndReps': row['setsAndReps'],
                                'weighted': row['weighted'],
                                'assignment': []}

    missing_movements = []
    for prog_id, program in programs.items():
        for workout_id, workout in program['workouts'].items():
            for section_id, section in workout['sections'].items():
                for exercise_id in section['exercises']:
                    try:
                        exercise = exercises[exercise_id]
                        assignment = f"({program['name']}, {workout['week']}, {workout['day']}, {section['name']})"
                        exercise['assignment'].append(assignment)
                        movement_id = exercise['movement']
                        if isinstance(movement_id, str) and movement_id not in all_movement_ids:
                            missing_movement = {'cycle': program['name'],
                                                'week': workout['week'],
                                                'day': workout['day'],
                                                'section': section['name'],
                                                'exercise': exercise['name'],
                                                'exercise_id': exercise_id,
                                                'movement': movement_id}
                            missing_movements.append(missing_movement)
                    except:
                        pass

    # write movements that appear in assigned exercises but are missing from movement library
    missing_movements_pd = pd.DataFrame(missing_movements)
    missing_movements_pd.to_csv('soflete_movements_missing_in_database.csv', columns=['cycle', 'week', 'day', 'section', 'exercise', 'exercise_id', 'movement'], index=False)

    # all assigned exercises in json for further use
    write_json(exercises, 'soflete_exercises.json')

    # csv of all exercises with their assignments
    exercises_assignment_data = list(exercises.values())
    for ex in exercises_assignment_data:
        assignment = '; '.join(ex['assignment'])
        ex['assignment'] = assignment

    exercises_assignment = pd.DataFrame(exercises_assignment_data)
    exercises_assignment.to_csv('soflete_exercises_assignments.csv', columns=['id', 'name', 'movement', 'xLabel', 'xValue', 'metricLabel',
                                                                              'baseYLabel', 'baseYValue', 'sets', 'setsAndReps', 'weighted',
                                                                              'assignment'], index=False)

    # subset of all movements that appear at least once in an assigned exercise
    assigned_movements = movements_pd.loc[movements_pd['id'].isin(assigned_movement_ids), :]
    assigned_movements.to_csv('soflete_movements_assigned.csv', index=False)


def get_movement_assignments():
    # load data
    exercises = read_json('soflete_exercises.json')
    assigned_movements = pd.read_csv('soflete_movements_assigned.csv')

    assigned_movements.set_index('id', drop=False, inplace=True)
    assigned_movements.loc[:, 'assignment'] = ""  # [] * assigned_movements.shape[0]
    assigned_movement_ids = assigned_movements['id'].values

    movement_assignments = {}
    for mov_id in assigned_movement_ids:
        movement_assignments[mov_id] = []

    for ex_id, exercise in exercises.items():
        mov_id = exercise['movement']
        if isinstance(mov_id, str) and mov_id in assigned_movement_ids:
            movement_assignments[mov_id].extend(exercise['assignment'])

    for mov_id, assignment in movement_assignments.items():
        assignment = '; '.join(assignment)
        assigned_movements.loc[mov_id, 'assignment'] = assignment

    assigned_movements.to_csv('soflete_movements_assignment.csv', index=False)


def get_exercise_missing_movement():
    exercises = read_json('soflete_exercises.json')

    missing_movements = []
    for exercise in exercises.values():
        movement = exercise['movement']
        name = exercise['name'].strip().lower()
        if not isinstance(movement, str) or movement == "":
            if name != 'rest':
                missing_movements.append(exercise)
    exercises_with_missing_movement = pd.DataFrame(missing_movements)
    exercises_with_missing_movement.to_csv('soflete_exercises_missing_movement.csv', index=False, columns=['id', 'name', 'movement', 'xLabel', 'xValue', 'metricLabel',
                                                                                                           'baseYLabel', 'baseYValue', 'sets', 'setsAndReps',
                                                                                                           'weighted', 'assignment'])


def get_all_sections():
    programs = read_json('soflete_programs_detailed.json')

    allowed_section_names = ["warm-up/movement prep", "warm-up / movement prep","warmup/movement prep","warmup / movement prep",
                             "strength", "strength 1", "strength 2", "strength 3", "strength 4",
                             "accessory work", "accessory work 1", "accessory work 2", "accessory work 3",
                             "plyometrics", "stamina", "recovery protocol"]
    counter = 0
    sections = []
    for prog_id, program in programs.items():
        counter += 1
        if program['name'] == 'John Hardin':
            continue
        for workout_id, workout in program['workouts'].items():
            for section_id, section in workout['sections'].items():
                if section['name'].strip().lower() not in allowed_section_names:
                    sections.append({'id': section_id,
                                     'name': section['name'],
                                     'cycle': program['name'],
                                     'week': workout['week'],
                                     'day': workout['day']
                                     }
                                    )
    sections_pd = pd.DataFrame(sections)
    sections_pd.to_csv('soflete_sections_cycle_non_standard_names.csv', index=False, columns=['id', 'name', 'cycle', 'week', 'day'])


def get_nonstandard_time_assignment(format='hour'):
    exercises = read_json('soflete_exercises.json')
    non_standard_time = []
    standard_time = []

    if format == 'hour':
        pattern = r'\b[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]*\b'
    else:
        pattern = r'\b[0-9]{2}:[0-9]{2}\.[0-9]*\b'
    for exercise in exercises.values():
        if exercise['baseYLabel'] == 'Time' and exercise['name'].lower().strip() != 'rest':
            if not isinstance(exercise['baseYValue'], str) or (re.match(pattern, exercise['baseYValue']) is None):
                non_standard_time.append(exercise)
            elif re.match(pattern, exercise['baseYValue']) is not None:
                standard_time.append(exercise)
    non_standard_time_ex = pd.DataFrame(non_standard_time)
    non_standard_time_ex.to_csv(f'soflete_exercises_non_standard_time_format_{format}.csv', index=False, columns=['id', 'name', 'movement', 'xLabel', 'xValue', 'metricLabel',
                                                                                                       'baseYLabel', 'baseYValue', 'sets', 'setsAndReps', 'assignment'])


def non_standard_weight(metric_label):
    pattern_rm = r'[0-9]{1,3}[.]{0,1}[0-9]{0,2}% of [0-9]{1,3}RM'
    pattern_weight_0 = r'\b[0-9]{1,3}lbs\b'
    pattern_weight_1 = r'\b[0-9]{1,3} lbs\b'
    pattern_weight_2 = r'\b[0-9]{1,3}/[0-9]{1,3}lbs\b'
    pattern_weight_3 = r'\b[0-9]{1,3}/[0-9]{1,3} lbs\b'
    pattern_bodyweight = r'[0-9]{1,3}% bodyweight'
    patterns = [pattern_rm, pattern_weight_0, pattern_weight_1, pattern_weight_2, pattern_weight_3, pattern_bodyweight]
    # patterns = [pattern_rm, pattern_weight_0, pattern_weight_2, pattern_bodyweight]
    if isinstance(metric_label, str):
        for pattern in patterns:
            if re.match(pattern, metric_label) is not None:
                return False
    return True

def get_weight_dosage_format():
    assigned_exercises = read_json('soflete_exercises.json')
    weighted_exercises_dict = {id: ex for id, ex in assigned_exercises.items() if ex['weighted']}

    # write all weighted exercises with assignments (with exercise as key)
    all_weighted_exercises = copy.deepcopy(list(weighted_exercises_dict.values()))
    for ex in all_weighted_exercises:
        assignment = '; '.join(ex['assignment'])
        ex['assignment'] = assignment
    all_weighted_exercises = pd.DataFrame(all_weighted_exercises)
    all_weighted_exercises.to_csv('soflete_weighted_exercises.csv', columns=['id', 'name', 'movement', 'xLabel', 'xValue', 'metricLabel',
                                                                             'baseYLabel', 'baseYValue', 'sets', 'setsAndReps', 'assignment'], index=False)

    # write subset after filtering out some "good" metricLabels
    weighted_exercises = []
    for ex in weighted_exercises_dict.values():
        ex = copy.deepcopy(ex)
        if non_standard_weight(ex['metricLabel']):
            assignment = '; '.join(ex['assignment'])
            ex['assignment'] = assignment
            weighted_exercises.append(ex)
    weighted_exercises = pd.DataFrame(weighted_exercises)
    weighted_exercises.to_csv('soflete_weighted_exercises_bad_weight.csv', columns=['id', 'name', 'movement', 'xLabel', 'xValue', 'metricLabel',
                                                                                'baseYLabel', 'baseYValue', 'sets', 'setsAndReps', 'assignment'], index=False)

    # write all weighted exercises (with assignment as a row)
    weighted_exercises_cycles = []
    for ex in weighted_exercises_dict.values():
        if non_standard_weight(ex['metricLabel']):
            for assignment in ex['assignment']:
                ex_assignment = {}
                assignment_details = assignment.strip('()').split(', ')
                ex_assignment['cycle'] = assignment_details[0]
                ex_assignment['week'] = assignment_details[1]
                ex_assignment['day'] = assignment_details[2]
                ex_assignment['section'] = assignment_details[3]
                ex_assignment['id'] = ex['id']
                ex_assignment['name'] = ex['name']
                ex_assignment['xLabel'] = ex['xLabel']
                ex_assignment['xValue'] = ex['xValue']
                ex_assignment['metricLabel'] = ex['metricLabel']
                ex_assignment['baseYLabel'] = ex['baseYLabel']
                ex_assignment['baseYValue'] = ex['baseYValue']
                ex_assignment['sets'] = ex['sets']
                ex_assignment['setsAndReps'] = ex['setsAndReps']
                weighted_exercises_cycles.append(ex_assignment)
    weighted_exercises_cycles = pd.DataFrame(weighted_exercises_cycles)
    weighted_exercises_cycles.to_csv('soflete_weighted_exercises_bad_weight_cycles.csv', columns=['cycle', 'week', 'day', 'section',
                                                                                                  'id', 'name', 'xLabel', 'xValue', 'metricLabel',
                                                                                                  'baseYLabel', 'baseYValue', 'sets', 'setsAndReps'], index=False)


def download_data_from_mongo():
    get_soflete_programs()
    get_soflete_exercises()
    get_soflete_movements()
    get_soflete_sections()
    get_soflete_workouts()

if __name__ == '__main__':
    # download_data_from_mongo()

    # get_detailed_programs_with_sections_exercises()
    # get_exercise_assignments()
    # get_movement_assignments()
    # get_exercise_missing_movement()
    # get_all_sections()
    # get_nonstandard_time_assignment(format='minute')
    get_weight_dosage_format()