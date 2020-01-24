from pymongo import MongoClient
import pandas as pd


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
        movement['summary'] = mov.get('summary', '')
        instructions = []
        if mov.get('instructions') is not None and mov.get('instructions').get('blocks') is not None:
            for block in mov['instructions']['blocks']:
                instructions.append(block['text'])
        movement['instructions'] = ",".join(instructions)
        all_movements.append(movement)
    movements_pd = pd.DataFrame(all_movements)
    movements_pd.to_csv('soflete_movements.csv')


def get_soflete_exercises():
    database = get_mongo_database()
    collection = database['exercises']
    cursor = list(collection.find({}, {'name': 1, "_movement": 1}))
    all_exercises = []
    for cur in cursor:
        exercise = {}
        exercise['id'] = cur['_id']
        exercise['name'] = cur['name']
        exercise['movement'] = cur.get('_movement')
       
        all_exercises.append(exercise)
    exercises_pd = pd.DataFrame(all_exercises)
    exercises_pd.to_csv('soflete_exercises.csv')

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


if __name__ == '__main__':
    # get_soflete_movements()
    get_soflete_sections()
    # get_soflete_exercises()
