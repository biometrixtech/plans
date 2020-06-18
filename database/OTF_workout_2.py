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
                new_duration_assignment = {
                    'assigned_value': row['duration_value'],
                    'min_value': row['duration_min'],
                    'max_value': row['duration_max'],
                }
                new_section = {
                    'name': section_name,
                    'duration_seconds': new_duration_assignment,
                    'exercises': []
                }
                sections[section_name] = new_section
            else:
                exercise = {}
                exercise['name'] = row['activity']
                exercise['id'] = row['activity']
                exercise['movement_id'] = row['movement']
                if is_valid(row, 'duration_value') or is_valid(row, 'duration_min') or is_valid(row, 'duration_max'):  #if not np.isnan(row['duration']):
                    duration_assignment = {
                        'assigned_value': row['duration_value'],
                        'min_value': row['duration_min'],
                        'max_value': row['duration_max'],
                    }
                    exercise['duration'] = duration_assignment
                else:
                    if is_valid(row, 'weight'):
                        exercise['weight'] = row['weight']
                    else:
                        exercise['weight'] = 15
                    exercise['weight_measure'] = 2
                if is_valid(row, 'reps'):  #if not np.isnan(row['reps']):
                    exercise['reps_per_set'] = row['reps']
                if is_valid(row, 'incline'):  #if not np.isnan(row['incline']):
                    exercise['grade'] = {
                        'assignment_value': row['incline']
                    }
                if is_valid(row, 'stroke_rate'):  #if not np.isnan(row['incline']):
                    exercise['stroke_rate'] = row['stroke_rate']
                if is_valid(row, 'pace'):  #if not np.isnan(row['pace']):
                    if row['pace'] == 'base':

                        pw_pace = {
                            'assignment_type': "power_walker",
                            'min_value': 1028,
                            'max_value': 800,
                        }
                        jog_pace = {
                            'assignment_type': "jogger",
                            'min_value': 801,
                            'max_value': 655,
                        }
                        run_pace = {
                            'assignment_type': "runner",
                            'min_value': 656
                        }
                        pace_alternatives = [pw_pace, jog_pace, run_pace]
                        # pw: 1028 - 800 (3.5 - 4.5)
                        # jog: 801 - 655 (4.5 - 5.5)
                        # run: 656 - x (5.5 +)
                        exercise['alternate_pace'] = pace_alternatives
                    elif row['pace'] == 'push':
                        jog_pace = {
                            'assignment_type': "jogger",
                            'min_value': 553,
                            'max_value': 480,
                        }
                        run_pace = {
                            'assignment_type': "runner",
                            'min_value': 481
                        }
                        pace_alternatives = [jog_pace, run_pace]
                        exercise['alternate_pace'] = pace_alternatives
                    elif row['pace'] == 'all_out':
                        jog_pace = {
                            'assignment_type': "jogger",
                            'min_value': 480
                        }
                        run_pace = {
                            'assignment_type': "runner",
                            'min_value': 481
                        }
                        pace_alternatives = [jog_pace, run_pace]
                        exercise['alternate_pace'] = pace_alternatives
                incline_alternatives = []

                if is_valid(row, 'pw_incline_min') or is_valid(row, 'pw_incline_max'):  #if not np.isnan(row['duration']):
                    pw_assignment = {
                        'assignment_type': "power_walker",
                        'min_value': row['pw_incline_min'],
                        'max_value': row['pw_incline_max'],
                    }
                    incline_alternatives.append(pw_assignment)
                exercise['alternate_grade'] = incline_alternatives
                distance_alternatives = []
                if is_valid(row, 'pw_distance'):
                    pw_assignment = {
                        'assignment_type': "power_walker",
                        'assigned_value': row['pw_distance'],
                    }
                    distance_alternatives.append(pw_assignment)
                if is_valid(row, 'jog_distance'):
                    jog_assignment = {
                        'assignment_type': "jogger",
                        'assigned_value': row['jog_distance'],
                    }
                    distance_alternatives.append(jog_assignment)
                if is_valid(row, 'run_distance'):
                    run_assignment = {
                        'assignment_type': "runner",
                        'assigned_value': row['run_distance'],
                    }
                    distance_alternatives.append(run_assignment)
                if is_valid(row, 'bike_distance'):
                    bike_assignment = {
                        'assignment_type': "biker",
                        'assigned_value': row['bike_distance'],
                    }
                    distance_alternatives.append(bike_assignment)
                if is_valid(row, 'strider_distance'):
                    strider_assignment = {
                        'assignment_type': "strider",
                        'assigned_value': row['strider_distance'],
                    }
                    distance_alternatives.append(strider_assignment)
                exercise['alternate_distance'] = distance_alternatives
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
    elif file_name == 'may1_alt':
        workout['program_module_id'] = 'may_first_alt'
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


# for file_name in ['may1', 'may2']:
#for file_name in ['at_home1', 'at_home2']:
for file_name in ['may1_alt']:
    parse_file(file_name)

