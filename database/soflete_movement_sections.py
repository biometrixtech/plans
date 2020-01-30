import pandas as pd
import numpy as np

movements_pd = pd.read_csv('soflete_movements_tagged.csv')
sections_pd = pd.read_csv('soflete_sections.csv')
exercises_pd = pd.read_csv('soflete_exercises.csv')

movements_json = {}
for index, row in movements_pd.iterrows():
    movements_json[row['id']] = {'id': row['id'],
                                 'name': row['name'],
                                 'youtube_link': row['youtube_link'],
                                 'tags': row['tags'],
                                 'sections': set(),
                                 'metrics': set()
                                 }

exercises_json = {}
for index, row in exercises_pd.iterrows():
    exercises_json[row['id']] = {'movement': row['movement'],
                                 'base_y_label': row['base_y_label']}

for index, row in sections_pd.iterrows():
    if row['exercises'] is not np.nan:
        exercises = row['exercises'].split(",")
        for ex_id in exercises:
            ex = exercises_json.get(ex_id)
            if ex is not None:
                mov_id = exercises_json.get(ex_id)['movement']
                metric = exercises_json.get(ex_id)['base_y_label']
                if mov_id is not np.nan and mov_id != "":
                    if mov_id in movements_json.keys():
                        section_name = row['name'].strip().lower()
                        # section_name = section_name.translate(str.maketrans('', '', '!"#$%&\'()*+,.:;<=>?@[\\]^_`{|}~'))
                        movements_json[mov_id]['sections'].add(section_name)
                        movements_json[mov_id]['metrics'].add(metric)

for mov_id, mov in movements_json.items():
    mov['sections'] = "; ".join(list(mov['sections']))
    mov['metrics'] = "; ".join(list(mov['metrics']))
soflete_movements_tags_sections = pd.DataFrame(list(movements_json.values()))
soflete_movements_tags_sections.to_csv('soflete_movements_tags_sections.csv', columns=['id', 'name', 'youtube_link', 'tags', 'sections', 'metrics'])

print('here')
