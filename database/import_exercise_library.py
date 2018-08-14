import csv
#import exercise_generator
#import database_config  # not committed to source code, contains connection string
from config import get_mongo_collection
import models.exercise

exercise_descriptions = {}
with open('Exercise_Descriptions.csv', newline='') as csvfile:
  exercise_reader = csv.reader(csvfile, delimiter='\t')
  row_count = 0
  for row in exercise_reader:
    if row_count >0:
      exercise_descriptions[row[0]] = row[3]
    row_count = row_count + 1
csvfile.close()

exercises = []
with open('Exercise_Library.csv', newline='') as csvfile:
    exercise_reader = csv.reader(csvfile, delimiter=',')
    row_count = 0
    for row in exercise_reader:
        if row_count > 0:
            if row[8] != "x" and row[26] != "x":
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
                    exercise_item.minimum_exposure_stage = 0
                else:
                    exercise_item.minimum_exposure_stage = int(row[17])
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
                exercise_item.equipment_required = row[25]
                print(exercise_item.equipment_required)
                exercise_item.youtube_id = None
                try:
                    exercise_item.description = exercise_descriptions[exercise_item.id]
                except KeyError:
                    exercise_item.description = ""
                exercises.append(exercise_item)
        row_count = row_count + 1

import sys
sys.exit()
exercise_count = len(exercises)
collection = get_mongo_collection('exerciselibrary')
for exercise_item in exercises:
    collection.replace_one({'library_id': exercise_item.id},
                           {'library_id': exercise_item.id,
                           'name': exercise_item.name,
                           'display_name': exercise_item.display_name,
                           'description': exercise_item.description,
                           'youtube_id': exercise_item.youtube_id,
                           'min_sets': exercise_item.min_sets,
                           'max_sets': exercise_item.max_sets,
                           'min_reps': exercise_item.min_reps,
                           'max_reps': exercise_item.max_reps,
                           'bilateral': exercise_item.bilateral,
                           'progression_interval': exercise_item.progression_interval,
                           'exposure_target': exercise_item.exposure_target,
                           'minimum_exposure_stage': exercise_item.minimum_exposure_stage,
                           'unit_of_measure': exercise_item.unit_of_measure,
                           'seconds_rest_between_sets': exercise_item.seconds_rest_between_sets,
                           'time_per_set': exercise_item.seconds_per_set,
                           'time_per_rep': exercise_item.seconds_per_rep,
                           'progresses_to': exercise_item.progresses_to,
                           'technical_difficulty': exercise_item.technical_difficulty,
                           'equipment_required': exercise_item.equipment_required
                           },
                           upsert=True)
