from models.exercise import Exercise
from pathlib import Path
import csv

class ExerciseLibraryDatastore(object):

    def __init__(self):
        self.exercise_list = []

    def side_load_exercise_list(self, exercise_list):
        self.exercise_list = exercise_list

    def side_load_exericse_list_from_csv(self):
        exercise_descriptions = {}
        with open(Path(__file__).resolve().parent.parent.parent / 'database/Exercise_Descriptions.csv', newline='') as csvfile:
            exercise_reader = csv.reader(csvfile, delimiter='\t')
            row_count = 0
            for row in exercise_reader:
                if row_count > 0:
                    exercise_descriptions[row[0]] = row[3]
                row_count = row_count + 1
        csvfile.close()

        exercises = []
        with open(Path(__file__).resolve().parent.parent.parent / 'database/Exercise_Library.csv', newline='') as csvfile:
            exercise_reader = csv.reader(csvfile, delimiter=',')
            row_count = 0
            for row in exercise_reader:
                if row_count > 0:
                    if row[14] != "x":
                        exercise_item = Exercise(row[0])
                        print(row[0])
                        exercise_item.display_name = row[1]
                        exercise_item.name = row[2]
                        if row[16] == "-" or row[16] == "":
                            exercise_item.min_sets = 0
                        else:
                            exercise_item.min_sets = int(row[16])
                        if row[17] == "-" or row[17] == "":
                            exercise_item.max_sets = 0
                        else:
                            exercise_item.max_sets = int(row[17])
                        if row[18] == "-" or row[18] == "":
                            exercise_item.min_reps = None
                        else:
                            exercise_item.min_reps = int(row[18])
                        if row[19] == "-" or row[19] == "":
                            exercise_item.max_reps = None
                        else:
                            exercise_item.max_reps = int(row[19])
                        exercise_item.bilateral = (row[20] == "Y")
                        if row[21] == "-" or row[21] == "":
                            exercise_item.progression_interval = 0
                        else:
                            exercise_item.progression_interval = int(row[21])
                        if row[22] == "-" or row[22] == "":
                            exercise_item.exposure_target = 0
                        else:
                            exercise_item.exposure_target = int(row[22])
                        exercise_item.unit_of_measure = row[23]
                        if row[24] == "-" or row[24] == "":
                            exercise_item.seconds_rest_between_sets = 0
                        else:
                            exercise_item.seconds_rest_between_sets = int(row[24])
                        if row[25] == "-" or row[25] == "":
                            exercise_item.seconds_per_set = None
                        else:
                            exercise_item.seconds_per_set = int(row[25])
                        if row[26] == "-" or row[26] == "":
                            exercise_item.seconds_per_rep = None
                        else:
                            exercise_item.seconds_per_rep = int(row[26])
                        exercise_item.progresses_to = row[27]
                        exercise_item.technical_difficulty = row[29]
                        exercise_item.equipment_required = row[30]
                        exercise_item.youtube_id = row[32]
                        exercise_item.description = exercise_descriptions[exercise_item.id]
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

