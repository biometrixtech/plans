# from abc import abstractmethod, ABCMeta
from aws_xray_sdk.core import xray_recorder

import models.exercise
from config import get_mongo_collection
import logic.exercise as exercise


class ExerciseLibraryDatastore(object):
    # @xray_recorder.capture('datastores.ExerciseLibraryDatastore.get')
    def get(self, collection='exerciselibrary'):
        return self._query_mongodb(collection)

    def put(self, items, collection):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item, collection)
        except Exception as e:
            raise e

    # @xray_recorder.capture('datastores.ExerciseLibraryDatastore._query_mongodb')
    def _query_mongodb(self, collection):

        exercise_list = []

        mongo_collection = get_mongo_collection(collection)

        exercise_cursor = mongo_collection.find()

        for record in exercise_cursor:
            exercise_item = models.exercise.Exercise(record["library_id"])
            exercise_item.min_sets = record["min_sets"]
            exercise_item.seconds_per_rep = record["time_per_rep"]
            exercise_item.min_reps = record["min_reps"]
            exercise_item.unit_of_measure = record["unit_of_measure"]
            exercise_item.equipment_required = record["equipment_required"]
            exercise_item.technical_difficulty = record["technical_difficulty"]
            exercise_item.progresses_to = record["progresses_to"]
            exercise_item.seconds_rest_between_sets = record["seconds_rest_between_sets"]
            exercise_item.exposure_target = record["exposure_target"]
            exercise_item.progression_interval = record["progression_interval"]
            exercise_item.bilateral = record["bilateral"]
            exercise_item.max_reps = record["max_reps"]
            exercise_item.max_sets = record["max_sets"]
            exercise_item.name = record["name"]
            # exercise_item.progressions = record["progressions"]
            # exercise_item.cues = record["cues"]
            # exercise_item.goal = record["goal"]
            # exercise_item.procedure = record["procedure"]
            # exercise_item.program_type = record["programType"]
            exercise_item.seconds_per_set = record["time_per_set"]
            # exercise_item.tempo = record["tempo"]
            exercise_list.append(exercise_item)

        return exercise_list

    # @xray_recorder.capture('datastores.ExerciseLibraryDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        item = self.item_to_mongodb(item)
        mongo_collection = get_mongo_collection(collection)
        query = {'library_id': item['library_id']}
        mongo_collection.replace_one(query, item, upsert=True)

    @staticmethod
    def item_to_mongodb(exercise_item):

        ''' Deprecated
        item = {'library_id': exercise_item.id,
                'name': exercise_item.name,
                'min_sets': exercise_item.min_sets,
                'max_sets': exercise_item.max_sets,
                'min_reps': exercise_item.min_reps,
                'max_reps': exercise_item.max_reps,
                'bilateral': exercise_item.bilateral,
                'progression_interval': exercise_item.progression_interval,
                'exposure_target': exercise_item.exposure_target,
                'unit_of_measure': exercise_item.unit_of_measure,
                'seconds_rest_between_sets': exercise_item.seconds_rest_between_sets,
                'time_per_set': exercise_item.seconds_per_set,
                'time_per_rep': exercise_item.seconds_per_rep,
                'progresses_to': exercise_item.progresses_to,
                'technical_difficulty': exercise_item.technical_difficulty,
                'equipment_required': exercise_item.equipment_required
                }
        '''

        item = exercise_item.json_deserialise()

        return {k: v for k, v in item.items() if v}

