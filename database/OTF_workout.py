import os
import json
import pandas as pd

def is_valid(row, name):
    if row.get(name) is not None and row[name] != "" and row[name] != "none":
        return True
    return False

def parse_file(file_name):
    data = pd.read_csv(f'{file_name}.csv')
    data = data.fillna('')
    sections = {}

    for i, row in data.iterrows():
        if is_valid(row, 'movement'):  #row.get('movement') is not None and row['movement'] != "":
            section_name = row['section']
            if row['movement'] == 'section':
                new_section = {
                    'name': section_name,
                    'duration_seconds': row['duration'],
                    'exercises': []
                }
                sections[section_name] = new_section
            else:
                exercise = {}
                exercise['name'] = row['activity']
                exercise['id'] = row['activity']
                exercise['movement_id'] = row['movement']
                if is_valid(row, 'duration'):  #if not np.isnan(row['duration']):
                    exercise['duration'] = row['duration']
                else:
                    if is_valid(row, 'weight'):
                        exercise['weight'] = row['weight']
                    else:
                        exercise['weight'] = 15
                    exercise['weight_measure'] = 2
                if is_valid(row, 'reps'):  #if not np.isnan(row['reps']):
                    exercise['reps_per_set'] = row['reps']
                if is_valid(row, 'incline'):  #if not np.isnan(row['incline']):
                    exercise['grade'] = row['incline']
                if is_valid(row, 'stroke_rate'):  #if not np.isnan(row['incline']):
                    exercise['stroke_rate'] = row['stroke_rate']
                if is_valid(row, 'pace'):  #if not np.isnan(row['pace']):
                    if row['pace'] == 'base':
                        exercise['pace'] = 655  # 5.5mph
                    elif row['pace'] == 'push':
                        exercise['pace'] = 514  # 7mph
                    elif row['pace'] == 'all_out':
                        exercise['pace'] = 450  # 8mph
                if section_name in sections:
                    sections[section_name]['exercises'].append(exercise)
                else:
                    new_section = {
                        'name': section_name,
                        'exercises': [exercise]
                    }
                    sections[section_name] = new_section


    workout = {}
    workout['program_id'] = 'may'
    if file_name == "may1":
        workout['program_module_id'] = 'may_first'
    elif file_name == 'may2':
        workout['program_module_id'] = 'may_second'
    elif file_name == 'at_home1':
        workout['program_module_id'] = 'at_home1'
    elif file_name == 'at_home2':
        workout['program_module_id'] = 'at_home2'

    workout['workout_sections'] = list(sections.values())
    json_string = json.dumps(workout, indent=4)
    file_name = os.path.join(os.path.realpath('..'), f"tests/data/otf/{file_name}.json")
    print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()

# files = ['may1', 'may2']
# files = ['at_home1', 'at_home2']
files = ['may18']
for file_name in files:
    parse_file(file_name)

