import os
import json
import pandas as pd
import numpy as np
import datetime
import zipfile
from utils import parse_datetime, format_datetime


class PerformanceDataParser(object):
    def __init__(self):
        self.rower_data = None
        self.treadmill_data = None
        self.planned_workout = None

    def parse_fileobj(self, fileobj):
        unzipped_files = zipfile.ZipFile(fileobj)
        print('unzipped file')
        names = unzipped_files.namelist()
        for name in names:
            if 'rower' in name:
                self.rower_data = pd.read_csv(unzipped_files.open(name))
                print('rower data read')
            elif 'treadmill' in name:
                self.treadmill_data = pd.read_csv(unzipped_files.open(name))
                print('treadmill data read')
        with open('data/june8_alt.json', 'r') as f:
            self.planned_workout  = json.load(f)
        print(self.planned_workout)

    def get_completed_workout(self, user_id):
        planned_workout = self.planned_workout
        treadmill_sections = self.get_treadmill_section()
        rower_floor_sections = self.get_rowing_floor_sections()
        if treadmill_sections[0]['start_date_time'] < rower_floor_sections[0]['start_date_time']:
            treadmill_first = True
        else:
            treadmill_first = False

        all_sections = np.concatenate([treadmill_sections, rower_floor_sections])
        all_sections = sorted(all_sections, key=lambda x: x['start_date_time'])

        workout = {}
        workout['user_id'] = user_id
        workout['workout_sections'] = all_sections
        workout['event_date_time'] = all_sections[0]['start_date_time']
        # workout_end_date_time = all_sections[-1]['end_date_time']
        # workout['duration'] = (workout_end_date_time - workout['start_date_time']).seconds
        for section in workout['workout_sections']:
            section['elapsed_start_time'] = (section['start_date_time'] - workout['event_date_time']).seconds
            section['elapsed_end_time'] = (section['end_date_time'] - workout['event_date_time']).seconds


        # figure out where the planned sections are relative to start time
        for section in planned_workout['sections']:
            if treadmill_first:
                section['elapsed_start_time'] = section.get('planned_start_time_run_first')
            else:
                section['elapsed_start_time'] = section.get('planned_start_time_rower_first')
            if section.get('duration_seconds') is not None:
                try:
                    section['elapsed_end_time'] = section['elapsed_start_time'] + section['duration_seconds']['assigned_value']
                except:
                    section['elapsed_end_time'] = None
            else:
                section['elapsed_end_time'] = None


        # Great groups of "floor" and "rest" blocks between rowing during rowing portion
        planned_sections_between_row = []
        between_row_sections_group = {'group': 0, 'sections': [], 'duration': 0, 'elapsed_start_time': None, 'elapsed_end_time': None}
        started = False
        counter = 0
        for section in planned_workout['sections']:
            if not started:
                if 'row' in section['name']:
                    non_rowing_exercises = self.extract_ex_from_row_section(section)
                    if len(non_rowing_exercises) > 0:
                        between_row_sections_group['sections'].extend(non_rowing_exercises)
                        between_row_sections_group['elapsed_start_time'] = section['elapsed_start_time']
                        between_row_sections_group['duration'] = sum([section['duration_seconds']['assigned_value'] for section in non_rowing_exercises])
                        between_row_sections_group['elapsed_end_time'] = between_row_sections_group['elapsed_start_time'] + between_row_sections_group['duration']
                        planned_sections_between_row.append(between_row_sections_group)
                        counter += 1
                        between_row_sections_group = {'group': counter, 'sections': [], 'duration': 0, 'elapsed_start_time': None, 'elapsed_end_time': None}
                    started = True
            else:
                if 'row' in section['name']:
                    planned_sections_between_row.append(between_row_sections_group)
                    counter += 1
                    between_row_sections_group = {'group': counter, 'sections': [], 'duration': 0, 'elapsed_start_time': None, 'elapsed_end_time': None}
                    non_rowing_exercises = self.extract_ex_from_row_section(section)
                    if len(non_rowing_exercises) > 0:
                        between_row_sections_group['sections'].extend(non_rowing_exercises)
                        between_row_sections_group['elapsed_start_time'] = section['elapsed_start_time']
                        between_row_sections_group['duration'] = sum([section['duration_seconds']['assigned_value'] for section in non_rowing_exercises])
                        between_row_sections_group['elapsed_end_time'] = between_row_sections_group['elapsed_start_time'] + between_row_sections_group['duration']
                        planned_sections_between_row.append(between_row_sections_group)
                        counter += 1
                        between_row_sections_group = {'group': 0, 'sections': [], 'duration': 0, 'elapsed_start_time': None, 'elapsed_end_time': None}
                else:
                    between_row_sections_group['sections'].append(section)
                    between_row_sections_group['duration'] += section['duration_seconds']['assigned_value']
                    if section.get('elapsed_start_time') is not None:
                        if between_row_sections_group['elapsed_start_time'] is None:
                            between_row_sections_group['elapsed_start_time'] = section['elapsed_start_time']
                            between_row_sections_group['elapsed_end_time'] = section['elapsed_end_time']
                        else:
                            between_row_sections_group['elapsed_start_time'] = min([between_row_sections_group['elapsed_start_time'], section['elapsed_start_time']])
                            between_row_sections_group['elapsed_end_time'] = max([between_row_sections_group['elapsed_end_time'], section['elapsed_end_time']])

        # if len(between_row_sections_group['sections']) > 0:
        #     planned_sections_between_row.append(between_row_sections_group)

        # add in any non-rowing workouts in rowing section
        # insert "floor" and "rest" groups in the gap "floor" section obtained from performance data
        for section in workout['workout_sections']:
            if 'floor' in section['name']:
                section['planned_sections'] = []
                section['available_duration'] = section['duration_seconds']
                for planned_sections in planned_sections_between_row:
                    if not planned_sections.get('used', False):
                        planned_completely_within_actual = section['elapsed_start_time'] <= planned_sections['elapsed_start_time'] and planned_sections['elapsed_end_time'] < section['elapsed_end_time']
                        planned_starts_close_start_of_actual = abs(section['elapsed_start_time'] - planned_sections['elapsed_start_time']) < 100
                        planned_ends_close_end_of_actual = abs(section['elapsed_end_time'] - planned_sections['elapsed_end_time']) < 100
                        duration_is_reasonable = planned_sections['duration'] - section['available_duration'] < 60 or section['available_duration'] > planned_sections['duration']
                        if (planned_completely_within_actual or planned_starts_close_start_of_actual or planned_ends_close_end_of_actual) and duration_is_reasonable:
                            section['planned_sections'].extend(planned_sections['sections'])
                            section['available_duration'] -= planned_sections['duration']
                            planned_sections['used'] = True


        # convert and create "completed" floor sections based on planned sections (detect possible multiple sets)
        new_sections = []
        for section in workout['workout_sections']:
            planned_sections =  section.get('planned_sections', [])
            if len(planned_sections) > 0:
                section['delete'] = True
                start_date_time = section['start_date_time']
                for planned_section in planned_sections:
                    new_section = {'name': planned_section['name']}
                    new_section['duration_seconds'] = planned_section['duration_seconds']['assigned_value']
                    new_section['start_date_time'] = start_date_time
                    start_date_time = start_date_time + datetime.timedelta(seconds=new_section['duration_seconds'])
                    new_section['exercises'] = []
                    for ex in planned_section['exercises']:
                        new_ex = {}
                        new_ex['name'] = ex['name']
                        new_ex['movement_id'] = ex['movement_id']  # TODO: what to do about alternates
                        new_ex['reps_per_set'] = ex.get('reps_per_set')
                        new_ex['duration'] = ex['duration']['assigned_value'] if ex.get('duration') is not None else None
                        new_ex['weight'] = ex.get('weight')  # TODO: get normal weight from OTF?
                        new_ex['weight_measure'] = ex.get('weight_measure')  # TODO: get normal weight from OTF?
                        new_section['exercises'].append(new_ex)
                    if 'floor' in new_section['name']:
                        total_reps = sum([ex['reps_per_set'] for ex in new_section['exercises']])
                        total_duration_measured = total_reps * 3
                        expected_sets = int(new_section['duration_seconds'] / total_duration_measured)
                        if expected_sets > 0:
                            new_section['exercises'] = new_section['exercises'] * expected_sets

                    new_sections.append(new_section)


        # insert and sort the new sections
        workout['workout_sections'].extend(new_sections)
        workout['workout_sections'] = sorted([section for section in workout['workout_sections'] if not section.get('delete', False)], key=lambda x:x['start_date_time'])

        # cleanup unnecessary data from sections
        section_variables = ['name', 'start_date_time', 'duration_seconds', 'exercises']
        for section in workout['workout_sections']:
            for key in list(section):
                if key not in section_variables:
                    del section[key]
                if key == 'start_date_time':
                    section[key] = format_datetime(section[key])
                for ex in section['exercises']:
                    if 'start_date_time' in ex:
                        ex['start_date_time'] = format_datetime(ex['start_date_time'])
                    if 'end_date_time' in ex:
                        ex['end_date_time'] = format_datetime(ex['end_date_time'])
        workout['event_date_time'] = format_datetime(workout['event_date_time'])


        print(workout)

        return workout

    def get_rowing_floor_sections(self):
        rower_data = self.rower_data
        self.sort_data(rower_data)
        timezone = self.get_timezone(rower_data.datecreated[0])

        rower_data = rower_data.loc[:, ['datecreated', 'timestamp', 'speed', 'powerperstroke', 'heartrate', 'distance', 'movingtime']]
        rower_data['has_power'] = 0
        non_zero_power = np.where(rower_data.powerperstroke != 0)[0]
        rower_data.loc[non_zero_power, 'has_power'] = 1
        rower_data['block'] = self.get_block(rower_data.timestamp, min_change=20, min_duration=1) + 1

        groups = int(max(rower_data['block']))
        rower_sections = []
        for i in range(1, groups + 1):
            section_data = rower_data[rower_data.block == i]

            section_data['ex_block'] = self.get_block(section_data.has_power, min_change=1, min_duration=1)
            grouped = section_data.groupby(by=['ex_block'])
            group_aggs = grouped.agg(['mean', 'count', 'sum', 'min', 'max'])
            rower_section = {}
            rower_section['start_date_time'] = self.get_datetime_from_timestamp(min(section_data.timestamp), timezone)
            rower_section['end_date_time'] = self.get_datetime_from_timestamp(max(section_data.timestamp), timezone)
            rower_section['duration_seconds'] = (rower_section['end_date_time'] - rower_section['start_date_time']).seconds
            rower_section['name'] = 'rower'
            rower_section['exercises'] = []
            for i, row in group_aggs.iterrows():
                ex = {}
                ex['start_date_time'] = self.get_datetime_from_timestamp(row['timestamp']['min'], timezone)
                ex['end_date_time'] = self.get_datetime_from_timestamp(row['timestamp']['max'], timezone)
                ex['name'] = 'row'
                ex['movement_id'] = '58459d9ddc2ce90011f93d84'
                ex['speed'] = round(row['speed']['mean'], 2)
                ex['power'] = round(row['powerperstroke']['mean'], 3)
                ex['pace'] = round(1 / ex['speed'], 2)
                # ex['hr'] = int(row['heartrate']['mean'])
                ex['hr'] = list(rower_data.heartrate[(rower_data.timestamp > row['timestamp']['min']) & (rower_data.timestamp < row['timestamp']['max'])])

                ex['distance'] = row['distance']['max'] - row['distance']['min']
                ex['duration'] = row['movingtime']['max'] - row['movingtime']['min']
                if ex['duration'] > 10 and ex['power'] != 0:
                    rower_section['exercises'].append(ex)
                else:
                    ex['name'] = "rest"
                    ex['movement_id'] = ""  # update with id from rest
                    ex['pace'] = None
                    ex['speed'] = None
                    ex['distance'] = None
                    ex['power'] = None
                    ex['duration'] = (ex['end_date_time'] - ex['start_date_time']).seconds
                    rower_section['exercises'].append(ex)
            rower_sections.append(rower_section)
        floor_sections = []
        for i in range(len(rower_sections)):
            if i != 0:
                if (rower_sections[i]['start_date_time'] - rower_sections[i - 1]['end_date_time']).seconds > 30:
                    floor_section = {}
                    floor_section['start_date_time'] = rower_sections[i-1]['end_date_time']
                    floor_section['end_date_time'] = rower_sections[i]['start_date_time']
                    floor_section['duration_seconds'] = (floor_section['end_date_time'] - floor_section['start_date_time']).seconds
                    floor_section['name'] = 'floor'
                    floor_section['exercises'] = []
                    floor_sections.append(floor_section)
        rower_sections.extend(floor_sections)
        rower_floor_sections = sorted(rower_sections, key= lambda x:x['start_date_time'])
        return rower_floor_sections

    def get_treadmill_section(self):
        # treadmill_data = pd.read_csv(f'performance_data_06_08/Anonymous{user}_Treadmill_Detailed.csv')
        treadmill_data = self.treadmill_data
        self.sort_data(treadmill_data)
        treadmill_data.timestamp += treadmill_data.second_marker
        timezone = self.get_timezone(treadmill_data.datecreated[0])

        treadmill_data = treadmill_data.loc[:, ['timestamp', 'speed', 'incline', 'heartrate', 'distance']]
        treadmill_data['speed_mph'] = round(treadmill_data.speed * 3600 / 1609, 1)

        treadmill_data['block_speed'] = self.get_block(treadmill_data.speed_mph, min_change=.15)
        del treadmill_data['speed_mph']
        treadmill_data['block_incline'] = self.get_block(treadmill_data.incline, min_change=1)
        treadmill_data['speed_incline'] = treadmill_data.block_speed + treadmill_data.block_incline
        treadmill_data['block'] = self.get_block(treadmill_data.speed_incline, min_change=1)

        grouped = treadmill_data.groupby(by='block')
        group_aggs = grouped.agg(['mean', 'count', 'sum', 'min', 'max'])
        treadmill_exercises = []
        for i, row in group_aggs.iterrows():
            ex = {}
            ex['start_date_time'] = self.get_datetime_from_timestamp(row['timestamp']['min'], timezone)
            ex['end_date_time'] = self.get_datetime_from_timestamp(row['timestamp']['max'], timezone)
            ex['name'] = 'treadmill run'
            ex['movement_id'] = '5823768d473c06100052ed9a'
            ex['speed'] = round(row['speed']['mean'], 2)
            ex['grade'] = round(row['incline']['mean'] / 100, 3)
            ex['pace'] = round(1 / ex['speed'], 2)
            # ex['hr'] = int(row['heartrate']['mean'])
            ex['hr'] = list(treadmill_data.heartrate[(treadmill_data.timestamp > row['timestamp']['min']) & (treadmill_data.timestamp < row['timestamp']['max'])])

            ex['distance'] = row['distance']['max'] - row['distance']['min']
            ex['duration'] = row['incline']['count']
            if ex['duration'] > 10 and ex['speed'] > 0:
                treadmill_exercises.append(ex)
            else:
                ex['name'] = "rest"
                ex['movement_id'] = ""  # update with id from rest
                ex['pace'] = None
                ex['speed'] = None
                ex['distance'] = None
                ex['grade'] = None
                ex['duration'] = (ex['end_date_time'] - ex['start_date_time']).seconds
                treadmill_exercises.append(ex)
        treadmill_seciton = {}
        treadmill_seciton['start_date_time'] = treadmill_exercises[0]['start_date_time']
        treadmill_seciton['end_date_time'] = treadmill_exercises[-1]['end_date_time']
        treadmill_seciton['duration_seconds'] = (treadmill_seciton['end_date_time'] - treadmill_seciton['start_date_time']).seconds
        treadmill_seciton['name'] = 'treadmill'
        treadmill_seciton['exercises'] = treadmill_exercises
        return [treadmill_seciton]

    @staticmethod
    def extract_ex_from_row_section(section):
        ex_section = {}
        ex_section['name'] = 'non_row_ex_row'
        ex_section['duration_seconds'] = {'assigned_value': 0}
        ex_section['exercises'] = []
        for ex in section['exercises']:
            if ex['movement_id'] != '58459d9ddc2ce90011f93d84':
                ex_section['exercises'].append(ex)
                if 'duration' in ex:
                    ex_section['duration_seconds']['assigned_value'] += ex['duration']['assigned_value']
                elif 'reps_per_set' in ex:
                    ex_section['duration_seconds']['assigned_value'] += ex['reps_per_set'] * 3
        if len(ex_section['exercises']) > 0:
            ex_section['start_date_time'] = section['elapsed_start_time']
            return [ex_section]
        else:
            return []

    @staticmethod
    def sort_data(dataframe):
        _, dataframe['second_marker'] = dataframe.uniqueid.str.split('_').str
        dataframe.second_marker = dataframe.second_marker.astype(int)
        dataframe.sort_values(by=['timestamp', 'second_marker' ], inplace=True, ignore_index=True)
        grouped = dataframe.groupby(by='timestamp')
        group_aggs = grouped.second_marker.agg(['max'])
        prev = 0
        dataframe['total_seconds'] = 60
        for i, row in group_aggs.iterrows():
            if i - prev > 60:
                dataframe.loc[np.where(dataframe.timestamp == i)[0], 'total_seconds'] = row['max']
            prev = i

        dataframe.timestamp = dataframe.timestamp + (dataframe.second_marker + 60 - dataframe.total_seconds)


    @staticmethod
    def get_block(series, min_change, min_duration=10):
        diff = np.ediff1d(series, to_begin=0)
        changes = np.where(abs(diff) >= min_change)[0]
        valid_changes = [changes[0]]
        for i in range(1, len(changes)):
            if changes[i] - changes[i-1] > min_duration:
                valid_changes.append(changes[i])
        blocks = np.zeros(len(series))
        block = 0
        last_value = 0
        for change in valid_changes:
            blocks[last_value:change] = block
            block += 1
            last_value = change
        blocks[last_value:] = block
        return blocks


    # def get_hr_data(user):
    #     hr_data = pd.read_csv(f'performance_data_06_08/Anonymous{user}-Hr-Detailed.csv')
    #     sort_data(hr_data)

    @staticmethod
    def get_datetime_from_timestamp(timestamp, tz_info=None):
        return datetime.datetime.fromtimestamp(timestamp, tz=tz_info)

    @staticmethod
    def get_timezone(datetime_string):
        tz = datetime_string[-6:]
        cleaned_date = parse_datetime(datetime_string.split('.')[0] + tz)
        return cleaned_date.tzinfo
    def write_json(data, user):
        json_string = json.dumps(data, indent=4)
        file_name = os.path.join(os.path.realpath('..'), f"../tests/data/otf/completed_workout_{user}.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()
