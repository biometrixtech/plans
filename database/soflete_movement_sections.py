import pandas as pd
import numpy as np
# from database.cooccurence import generate_co_occurrence_matrix, get_list_from_name

# words_dict = {}
movements_pd = pd.read_csv('soflete_movements.csv')
sections_pd = pd.read_csv('soflete_sections.csv')
exercises_pd = pd.read_csv('soflete_exercises.csv')

movements_json = {}
for index, row in movements_pd.iterrows():
    movements_json[row['id']] = {'name': row['name'], "sections":set()}

exercises_json = {}
for index, row in exercises_pd.iterrows():
    exercises_json[row['id']] = row['movement']

for index, row in sections_pd.iterrows():
    if row['exercises'] is not np.nan:
        exercises = row['exercises'].split(",")
        for ex_id in exercises:
            mov_id = exercises_json.get(ex_id)
            if mov_id is not None and mov_id is not np.nan and mov_id != "":
                if mov_id in movements_json.keys():
                    movements_json[mov_id]['sections'].add(row['name'])

print('here')

