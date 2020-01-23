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


def get_soflete_exercises():
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

if __name__ == '__main__':
    get_soflete_exercises()