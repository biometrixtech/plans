from pymongo import MongoClient
import pandas as pd
import csv


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
        # movement['summary'] = mov.get('summary', '')
        movement['youtube_link'] = mov.get('url', '')
        # instructions = []
        # if mov.get('instructions') is not None and mov.get('instructions').get('blocks') is not None:
        #     for block in mov['instructions']['blocks']:
        #         instructions.append(block['text'])
        # movement['instructions'] = ",".join(instructions)
        all_movements.append(movement)
    movements_pd = pd.DataFrame(all_movements)
    movements_pd.to_csv('soflete_movements.csv', columns=['id', 'name', 'youtube_link'])


def get_soflete_exercises():
    database = get_mongo_database()
    collection = database['exercises']
    cursor = list(collection.find({}, {'name': 1, "_movement": 1, 'baseYLabel': 1}))
    all_exercises = []
    for cur in cursor:
        exercise = {}
        exercise['id'] = cur['_id']
        exercise['name'] = cur['name']
        exercise['movement'] = cur.get('_movement')
        exercise['baseYLabel'] = cur.get('baseYLabel', "")
       
        all_exercises.append(exercise)
    exercises_pd = pd.DataFrame(all_exercises)
    exercises_pd.to_csv('soflete_exercises.csv')


def get_soflete_exercises_detailed():
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
    metrics_pd.to_csv('soflete_exercises_metrics.csv')


def get_soflete_user_exercises():
    database = get_mongo_database()
    collection = database['userexercises']
    cursor = list(collection.find({}, {'_exercise': 1, "_movement": 1, "results": 1}).limit(100000))
    all_exercises = []
    results_list = []

    for cur in cursor:
        exercise = {}
        exercise['id'] = cur['_id']
        exercise['exercise'] = cur['_exercise']
        exercise['movement'] = cur.get('_movement')
        results = cur.get('results', [])

        if len(results) > 0:
            results_list = convert_results_values(exercise['id'], exercise['exercise'],
                                                  exercise['movement'], results, results_list)

        all_exercises.append(exercise)
    exercises_pd = pd.DataFrame(all_exercises)
    exercises_pd.to_csv('soflete_userexercises.csv')
    metrics_pd = pd.DataFrame(results_list)
    metrics_pd.to_csv('soflete_userexercise_results.csv')


def convert_results_values(id, exercise, movement, results, results_list):

    for m in range(0, len(results)):
        metrics = {}
        metrics['id'] = id
        metrics['exercise'] = exercise
        metrics['movement'] = movement
        metrics['metric'] = results[m]["metric"]
        values_list = results[m]["values"]
        values_string = ';'.join(map(str, values_list))
        metrics['values'] = values_string

        results_list.append(metrics)

    return results_list


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
    sections_pd.to_csv('soflete_sections.csv')


def analyze_exercises():
    with open('soflete_exercises_detailed.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        lbs_count = 0
        rm_count = 0
        other_count = -1
        total_count = -1
        max_count = 0
        how_set = set()
        lbs_set = set()
        max_set = set()
        rm_set = set()
        for row in csv_reader:
            total_count += 1
            if 'RM' in row[4] or 'Rep Max' in row[4] or 'Rep max' in row[4] or 'rep max' in row[4] or 'rep mx' in row[4]:
                rm_count += 1
                rm_set.add(row[4])
            elif 'lbs' in row[4]:
                lbs_count += 1
                lbs_set.add(row[4])

            elif 'MAX' in row[1]:
                max_count += 1
                max_set.add(row[4])

            else:
                if len(row[4]) > 0:
                    how_set.add(row[4])
                other_count += 1

        how_list = list(how_set)
        lbs_list = list(lbs_set)
        max_list = list(max_set)
        rm_list = list(rm_set)

        how_pd = pd.DataFrame(how_list)
        how_pd.to_csv('soflete_exercises_other.csv')
        lbs_pd = pd.DataFrame(lbs_list)
        lbs_pd.to_csv('soflete_exercises_lbs.csv')
        max_pd = pd.DataFrame(max_list)
        max_pd.to_csv('soflete_exercises_max.csv')
        rep_max_pd = pd.DataFrame(rm_list)
        rep_max_pd.to_csv('soflete_exercises_rep_max.csv')


def find_weighted_exercises_and_movements():

    weight_list = []

    soflete_movement_dictionary = {}
    with open('soflete_movements.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 0
        for row in csv_reader:
            if count > 1:
                soflete_movement_dictionary[row[1]] = row[3]
            count += 1

    exercise_movement_dictionary = {}
    exercise_metric_label_dictionary = {}
    with open('soflete_exercises_detailed.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 0
        for row in csv_reader:
            if count > 1:
                exercise_movement_dictionary[row[3]] = row[5]
                exercise_metric_label_dictionary[row[3]] = row[4]

            count += 1

    with open('soflete_exercises_metrics.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if "Weight" in row[1] or "weight" in row[1]:
                columns = {}
                columns["exercise_id"] = row[3]
                columns["exercise_name"] = row[4]
                if row[3] in exercise_movement_dictionary:
                    columns["movement_id"] = exercise_movement_dictionary[row[3]]
                    if columns["movement_id"] in soflete_movement_dictionary:
                        columns["movement_name"] = soflete_movement_dictionary[columns["movement_id"]]
                    columns["weight_label"] = row[1]
                    columns["weight_value"] = row[2]
                    metric_label = exercise_metric_label_dictionary[row[3]]
                    columns["metric_label"] = metric_label
                    if 'RM' in metric_label or 'Rep Max' in metric_label or 'Rep max' in metric_label or 'rep max' in metric_label or 'rep mx' in metric_label:
                        columns["x_rep_max"] = 1
                    else:
                        columns["x_rep_max"] = 0
                    if 'lbs' in metric_label:
                        columns["x_lbs"] = 1
                    else:
                        columns["x_lbs"] = 0
                    if 'Bodyweight' in metric_label or 'body weight' in metric_label or 'bodyweight' in metric_label:
                        columns["x_body_weight"] = 1
                    else:
                        columns["x_body_weight"] = 0
                    if columns['x_rep_max'] == 0 and columns["x_lbs"] == 0 and columns["x_body_weight"] == 0:
                        columns["x_x_other"] = 1
                    else:
                        columns["x_x_other"] = 0
                    column_sum = columns["x_rep_max"] + columns["x_lbs"] + columns["x_body_weight"]
                    if column_sum > 1:
                        columns["x_x_multiple"] = 1
                    else:
                        columns["x_x_multiple"] = 0
                    if "Actual" in row[1]:
                        columns["y_actual"] = 1
                    else:
                        columns["y_actual"] = 0
                    if "RM" in row[1]:
                        columns["y_rep_max"] = 1
                    else:
                        columns["y_rep_max"] = 0
                    if "%" in row[1]:
                        columns["y_body_weight"] = 1
                    else:
                        columns["y_body_weight"] = 0
                    if row[2] == "0.0" and "Actual" in row[1]:
                        columns["z_unweighted_actual"] = 1
                    else:
                        columns["z_unweighted_actual"] = 0
                    weight_list.append(columns)
                    if row[2] != "0.0" and "Actual" in row[1] and ('lbs' in metric_label or columns["x_rep_max"] == 0):
                        columns["z_weighted_actual_lbs"] = 1
                    else:
                        columns["z_weighted_actual_lbs"] = 0

        weight_pd = pd.DataFrame(weight_list)
        weight_pd.to_csv('soflete_weighted_movements.csv')


def soflete_exercises_movement():
    exercises = pd.read_csv('soflete_exercises_detailed.csv')
    del exercises['Unnamed: 0']

    exercises_without_movement = exercises[exercises.movement.isnull()]
    # exercises_without_movement.to_csv('soflete_exercises_no_movement.csv', index=False)
    exercises_without_movement['sections'] = ''
    exercises_without_movement['assigned'] = False
    print(exercises_without_movement.shape)
    sections = pd.read_csv('soflete_sections.csv')
    sections = sections[-sections.exercises.isnull()]
    sections['exercises'] = [ex.split(',') for ex in sections.exercises]
    all_exercises_without_movement = exercises_without_movement.id.values
    all_assigned_exercises = sections.exercises.values
    assigned_ex_set = set()
    for exercises in all_assigned_exercises:
        assigned_ex_set.update(exercises)

    for index, exercise in exercises_without_movement.iterrows():
        if exercise['id'] in assigned_ex_set:
            exercises_without_movement.loc[index, 'assigned'] = True
    for index_2, section in sections.iterrows():
        for exercise_id in section['exercises']:
            if exercise_id in all_exercises_without_movement:
                exercises_without_movement.loc[exercises_without_movement.id == exercise_id, 'sections'] += f', {section["name"]}'

    assigned_exercises_no_movement =  exercises_without_movement[exercises_without_movement.assigned == True]
    print(assigned_exercises_no_movement.shape)
    # assigned_exercises_no_movement.to_csv('soflete_assigned_exercises_no_movement.csv', index=False)


def soflete_exercises_no_movement_sections():
    assigned_exercises_no_movement = pd.read_csv('soflete_assigned_exercises_no_movement.csv')

    no_load_sections = [
        "prehab", "pre_hab",
        "warm_up", "warm up", "warm_ups", "warm ups", "warmup",
        "cool_down", "cool down", "cool_downs", "cool downs", "cooldown",
        "movement prep", "movement_prep", "movement work",
        "skill development", "skill_development",
        "recovery protocol",
        "blood flow",
        "mobility",
        "recovery",
        "corrective", "correctives",
        "breathing", "breathin"
    ]
    assigned_exercises_no_movement['non_prep_section'] = False
    for index, exercise in assigned_exercises_no_movement.iterrows():
        sections = list(set(exercise['sections'].split(',')))
        non_prep_section = False
        print('here')
        for section in sections:
            if section != "":
                section = section.strip()
                section = section.lower()
                section = section.replace("-", "_")
                is_prep_section = []
                for keyword in no_load_sections:
                    pat = r'\b' + keyword + r'\b'
                    if re.search(pat, section) is not None:
                        is_prep_section.append(True)
                    else:
                        is_prep_section.append(False)
                if not any(is_prep_section):
                    non_prep_section = True
                    break
        if non_prep_section:
            assigned_exercises_no_movement.loc[index, 'non_prep_section'] = True
    assigned_exercises_only_prep_sections = assigned_exercises_no_movement[assigned_exercises_no_movement['non_prep_section'] == False]
    print('here')


def workout_program_exercise():
    exercises = pd.read_csv('soflete_exercises_detailed.csv')
    del exercises['Unnamed: 0']

    exercises_without_movement = exercises[exercises.movement.isnull()]
    exercises_without_movement['sections'] = [[]] * exercises_without_movement.shape[0]
    exercises_without_movement['programs'] = [[]] * exercises_without_movement.shape[0]
    exercises_without_movement['assigned'] = False
    print(exercises_without_movement.shape)
    sections = pd.read_csv('soflete_sections.csv')
    sections = sections[-sections.exercises.isnull()]
    sections['exercises'] = [ex.split(',') for ex in sections.exercises]
    all_exercises_without_movement = exercises_without_movement.id.values
    all_assigned_exercises = sections.exercises.values
    assigned_ex_set = set()
    for exercises in all_assigned_exercises:
        assigned_ex_set.update(exercises)

    for index, exercise in exercises_without_movement.iterrows():
        if exercise['id'] in assigned_ex_set:
            exercises_without_movement.loc[index, 'assigned'] = True
    assigned_exercises_no_movement = exercises_without_movement[exercises_without_movement.assigned == True]
    for index_2, section in sections.iterrows():
        # if index_2 < 1000:
        for exercise_id in section['exercises']:
            if exercise_id in all_exercises_without_movement:
                assigned_exercises_no_movement.loc[assigned_exercises_no_movement.id == exercise_id, 'sections'] += [section["id"]]
        # else:
        #     break
    all_sections_set = set()
    all_sections = assigned_exercises_no_movement.sections.values
    for sections in all_sections:
        all_sections_set.update(sections)


    workouts = pd.read_csv('soflete_workouts.csv')
    workouts_with_program = workouts[-workouts.program.isnull()]
    workouts_with_program = workouts_with_program[-workouts_with_program.sections.isnull()]

    workouts_with_program['sections_2'] = [[]] * workouts_with_program.shape[0]
    all_sections_workouts_set = set()
    for w_index, workout in workouts_with_program.iterrows():
        try:
            all_sections_workouts_set.update(workout['sections'].split(','))
        except Exception as e:
            print(e)
            print(workout)

    intersection = all_sections_set.intersection(all_sections_workouts_set)

    for w_index, workout in workouts_with_program.iterrows():
        workout_sections = workout['sections'].split(',')
        for workout_section in workout_sections:
            if workout_section in all_sections_set:
                for ex_index, exercise in assigned_exercises_no_movement.iterrows():
                    ex_sections = set(exercise['sections'])
                    if len(ex_sections) > 0:
                        for ex_section in ex_sections:
                            if ex_section == workout_section:
                                try:
                                    assigned_exercises_no_movement.loc[assigned_exercises_no_movement.id == exercise['id'], 'programs'] += [workout['program']]
                                    break
                                except Exception as e:
                                    print(e)
                                    print(exercise, workout_section)

    assigned_exercises_no_movement.to_csv('exercise_no_movement_program.csv', index=False)
    print(assigned_exercises_no_movement.shape)


def get_soflete_workouts():
    database = get_mongo_database()
    program_collection = database['programs']
    prog_cursor = list(program_collection.find({}, {"name": 1, "_id": 1, "dayMap": 1}))
    all_programs = {}
    for cur in prog_cursor:
        program = {}
        program['id'] = cur['_id']
        program['name'] = cur['name']
        # program['workouts'] = set()
        # daymap = cur['dayMap']
        # for day, workout in daymap.items():
        #     if workout['_workout'] is not None:
        #         program['workouts'].add(workout['_workout'])
        all_programs[cur['_id']] = program


    workout_collection = database['workouts']
    cursor = list(workout_collection.find({}, {"name": 1, "_program": 1, "_sections": 1}))
    all_workouts = []
    for cur in cursor:
        workout = {}
        workout['id'] = cur['_id']
        workout['name'] = cur['name']
        workout['program'] = ""
        program_id = cur.get('_program')
        if program_id is not None:
            program = all_programs.get(program_id)
            if program is not None:
                workout['program'] = program['name']
        sections = []
        for section in cur.get('_sections', []):
            sections.append(str(section))
        workout['sections'] = ','.join(sections)
        # wrokout['exercises'] = ",".join(exercises)
        all_workouts.append(workout)
    workouts_pd = pd.DataFrame(all_workouts)
    workouts_pd.to_csv('soflete_workouts.csv')


def cleanup_programs():
    ex_program = pd.read_csv('exercise_no_movement_program.csv')

    all_programs = set()
    for index, exercise in ex_program.iterrows():
        programs = exercise['programs']
        programs = programs.strip('[]')
        programs = programs.split(',')
        programs = set([prog.strip() for prog in programs])
        all_programs.update(programs)
        ex_program.ix[index, 'programs'] = ', '.join(programs)
    # ex_program.to_csv('soflete_exercises_no_movement.csv', columns=['id', 'name', 'programs'], index=False)
    print(all_programs)
    print('here')




if __name__ == '__main__':
    get_soflete_movements()
    # get_soflete_sections()
    # get_soflete_exercises()
    # get_soflete_exercises_detailed()
    #get_soflete_user_exercises()
    #analyze_exercises()
    # find_weighted_exercises_and_movements()
    # soflete_exercises_movement()
    # soflete_exercises_no_movement_sections()
    # workout_program_exercise()
    # get_soflete_workouts()
    # cleanup_programs()

