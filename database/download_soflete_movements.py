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
        exercise['base_y_label'] = cur.get('baseYLabel', "")
       
        all_exercises.append(exercise)
    exercises_pd = pd.DataFrame(all_exercises)
    exercises_pd.to_csv('soflete_exercises.csv')


def get_soflete_exercises_detailed():
    database = get_mongo_database()
    collection = database['exercises']
    cursor = list(collection.find({}, {'name': 1, "defaultMetricValues": 1, "sets": 1, "setsAndReps": 1, "metricLabel": 1, "_movement": 1, 'baseYLabel': 1, "baseYValue": 1, "xLabel": 1, "xValue": 1}))
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
        exercise['base_y_label'] = cur.get('baseYLabel', "")
        exercise['baseYValue'] = cur.get('baseYValue', "")
        exercise['xLabel'] = cur.get('xLabel', "")
        exercise['xValue'] = cur.get('xValue', "")
        default_metric_values = cur.get('defaultMetricValues', [])

        if len(default_metric_values) > 0:
            metrics_list = convert_default_metric_values(exercise['id'], exercise['name'], default_metric_values, metrics_list)

        all_exercises.append(exercise)
    exercises_pd = pd.DataFrame(all_exercises)
    exercises_pd.to_csv('soflete_exercises_detailed.csv')
    metrics_pd = pd.DataFrame(metrics_list)
    metrics_pd.to_csv('soflete_exercise_metrics.csv')


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
        for row in csv_reader:
            total_count += 1
            if 'MAX' in row[1]:
                max_count += 1
            elif 'lbs' in row[4]:
                lbs_count += 1
            elif 'RM' in row[4] or 'Rep Max' in row[4] or 'Rep max' in row[4] or 'rep max' in row[4] or 'rep mx' in row[4]:
                rm_count += 1
            else:
                if len(row[4]) > 0:
                    how_set.add(row[4])
                other_count += 1

        how_list = list(how_set)

        j=0

if __name__ == '__main__':
    # get_soflete_movements()
    # get_soflete_sections()
    # get_soflete_exercises()
    #get_soflete_exercises_detailed()
    #get_soflete_user_exercises()
    analyze_exercises()
