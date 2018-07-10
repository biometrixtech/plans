import pymongo
import database_config
import logic.exercise as exercise
import config

class ExerciseDataAccess(object):

    # def __init__(self):
    # self.mongo_client = pymongo.MongoClient(database_config.mongodb_dev)

    def get_exercise_library(self):
        exercise_list = []

        # db = self.mongo_client.movementStats
        collection = config.get_mongo_collection('dailyplan')
        exercise_cursor = collection.find()

        for record in exercise_cursor:
            exercise_item = exercise.Exercise(record["libraryId"])
            exercise_item.min_sets = record["minSets"]
            exercise_item.seconds_per_rep = record["timePerRep"]
            exercise_item.min_reps = record["minReps"]
            exercise_item.unit_of_measure = record["unitOfMeasure"]
            exercise_item.equipment_required = record["equipmentRequired"]
            exercise_item.technical_difficulty = record["technicalDifficulty"]
            exercise_item.progresses_to = record["progressesTo"]
            exercise_item.seconds_rest_between_sets = record["secondsRestBetweenSets"]
            exercise_item.exposure_target = record["exposureTarget"]
            exercise_item.progression_interval = record["progressionInterval"]
            exercise_item.bilateral = record["bilateral"]
            exercise_item.max_reps = record["maxReps"]
            exercise_item.max_sets = record["maxSets"]
            exercise_item.name = record["name"]
            # exercise_item.progressions = record["progressions"]
            # exercise_item.cues = record["cues"]
            # exercise_item.goal = record["goal"]
            # exercise_item.procedure = record["procedure"]
            # exercise_item.program_type = record["programType"]
            exercise_item.seconds_per_set = record["timePerSet"]
            # exercise_item.tempo = record["tempo"]
            exercise_list.append(exercise_item)

        return exercise_list

    def get_exercises_by_ids(self, exercise_ids):
        db = self.mongo_client.movementStats
        collection = list(db.exerciseLibrary.find({"$or": [{"libraryId": "2"}, {"libraryId": "3"}]}))
        find_query = '"{"$or": ["'
        # for exercise_id in exercise_ids:
        #    exercise_id =