import pymongo
import database_config


class ExerciseDataAccess(object):

    def __init__(self):
        self.mongo_client = pymongo.MongoClient(database_config.mongodb_dev)

    def get_exercise_library(self):
        db = self.mongo_client.movementStats
        exercises = list(db.exerciseLibrary.find())
        return exercises

    def get_exercises_by_ids(self, exercise_ids):
        db = self.mongo_client.movementStats
        collection = list(db.exerciseLibrary.find({"$or": [{"libraryId": "2"}, {"libraryId": "3"}]}))
        find_query = '"{"$or": ["'
        # for exercise_id in exercise_ids:
        #    exercise_id =