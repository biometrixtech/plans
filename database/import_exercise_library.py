import csv
import pymongo
import exercise
import database_config  # not committed to source code, contains connection string

exercises = []
with open('Exercise_Library.csv', newline='') as csvfile:
    exercise_reader = csv.reader(csvfile, delimiter=',')
    row_count = 0
    for row in exercise_reader:
        if row_count > 0:
            if row[13] != "x":
                exercise_item = exercise.Exercise(row[0])
                exercise_item.name = row[1]
                exercise_item.min_sets = int(row[15])
                exercise_item.max_sets = int(row[16])
                if row[17] == "-" or row[17] == "":
                    exercise_item.min_reps = None
                else:
                    exercise_item.min_reps = int(row[17])
                if row[18] == "-" or row[18] == "":
                    exercise_item.max_reps = None
                else:
                    exercise_item.max_reps = int(row[18])
                exercise_item.bilateral = (row[19] == "Y")
                exercise_item.progression_interval = int(row[20])
                exercise_item.exposure_target = int(row[21])
                exercise_item.unit_of_measure = row[22]
                exercise_item.seconds_rest_between_sets = int(row[23])
                if row[24] == "-" or row[24] == "":
                    exercise_item.seconds_per_set = None
                else:
                    exercise_item.seconds_per_set = int(row[24])
                if row[25] == "-" or row[25] == "":
                    exercise_item.seconds_per_rep = None
                else:
                    exercise_item.seconds_per_rep = int(row[25])
                exercise_item.progresses_to = row[26]
                exercise_item.technical_difficulty = row[28]
                exercise_item.equipment_required = row[29]
                exercises.append(exercise_item)
        row_count = row_count + 1

exercise_count = len(exercises)
client = pymongo.MongoClient(database_config.mongodb_dev)
db = client.movementStats
collection = db.exerciseLibrary
for exercise_item in exercises:
    collection.insert_one({'library_id': exercise_item.id,
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
                           })

