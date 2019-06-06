import models.exercise
from pathlib import Path
import csv

class ExerciseLibraryDatastore(object):

    def __init__(self):
        self.exercise_list = []

    def side_load_exercise_list(self, exercise_list):
        self.exercise_list = exercise_list

    def side_load_exericse_list_from_csv(self, library_file='database/Exercise_Library.csv',
                                         desc_file='database/Exercise_Descriptions.tsv'):
        exercise_descriptions = {}
        with open(Path(__file__).resolve().parent.parent.parent / desc_file, newline='') as csvfile:
            exercise_reader = csv.reader(csvfile, delimiter='\t')
            row_count = 0
            for row in exercise_reader:
                if row_count > 0:
                    exercise_descriptions[row[0]] = row[3]
                row_count = row_count + 1
        csvfile.close()

        exercises = []
        with open(Path(__file__).resolve().parent.parent.parent / library_file, newline='') as csvfile:
            exercise_reader = csv.reader(csvfile, delimiter=',')
            row_count = 0
            for row in exercise_reader:
                if row_count > 0:
                    #if row[8] != "x" and row[26] == "x":  #now allowing integrate exercises
                    try:
                        exercise_item = models.exercise.Exercise(row[0])
                        exercise_item.display_name = row[1]
                        exercise_item.name = row[2]
                        if row[10] in ["-", ""]:
                            exercise_item.min_sets = 0
                        else:
                            exercise_item.min_sets = int(row[10])
                        if row[11] in ["-", ""]:
                            exercise_item.max_sets = 0
                        else:
                            exercise_item.max_sets = int(row[11])
                        if row[12] in ["-", ""]:
                            exercise_item.min_reps = None
                        else:
                            exercise_item.min_reps = int(row[12])
                        if row[13] in ["-", ""]:
                            exercise_item.max_reps = None
                        else:
                            exercise_item.max_reps = int(row[13])
                        exercise_item.bilateral = (row[14] == "Y")
                        if row[15] in ["-", ""]:
                            exercise_item.progression_interval = 0
                        else:
                            exercise_item.progression_interval = int(row[15])
                        if row[16] in ["-", ""]:
                            exercise_item.exposure_target = 0
                        else:
                            exercise_item.exposure_target = int(row[16])
                        if row[17] in ["-", ""]:
                            exercise_item.exposure_minimum = 0
                        else:
                            exercise_item.exposure_minimum = int(row[17])
                        exercise_item.unit_of_measure = row[18]
                        if row[19] in ["-", ""]:
                            exercise_item.seconds_rest_between_sets = 0
                        else:
                            exercise_item.seconds_rest_between_sets = int(row[19])
                        if row[20] in ["-", ""]:
                            exercise_item.seconds_per_set = None
                        else:
                            exercise_item.seconds_per_set = int(row[20])
                        if row[21] in ["-", ""]:
                            exercise_item.seconds_per_rep = None
                        else:
                            exercise_item.seconds_per_rep = int(row[21])
                        exercise_item.progresses_to = row[22]
                        exercise_item.technical_difficulty = row[24]
                        exercise_item.equipment_required = [row[25]]
                        exercise_item.youtube_id = None
                    except KeyError:
                        pass # just an empty line
                    try:
                        exercise_item.description = exercise_descriptions[exercise_item.id]
                    except KeyError:
                        print("no description")
                        exercise_item.description = ""
                    exercises.append(exercise_item)
                row_count = row_count + 1
        self.exercise_list = exercises

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

    def _query_mongodb(self, collection):

        return self.exercise_list

    # @xray_recorder.capture('datastores.ExerciseLibraryDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        item = self.item_to_mongodb(item)
        #mongo_collection = get_mongo_collection(collection)
        query = {'library_id': item['library_id']}
        #mongo_collection.replace_one(query, item, upsert=True)

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

