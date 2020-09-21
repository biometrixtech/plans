import pandas as pd
import numpy as np
import datetime, os, json
from utils import format_datetime
import matplotlib.pyplot as plt
from enum import Enum
from scipy.signal import butter, filtfilt

from scipy.signal import find_peaks

# data_series = 'april-june2020'
# data_series = 'july-sept2020'
data_series = 'aug-nov2019'
csv_files_folder = f'csv_data/{data_series}'
workouts_folder = f'workouts/{data_series}_segmented'
if not os.path.exists(workouts_folder):
    os.mkdir(workouts_folder)

if '2020' in data_series:
    all_workouts = pd.read_csv('garmin_data/Activities_2020.csv')
elif '2019' in data_series:
    all_workouts = pd.read_csv('garmin_data/Activities_2019.csv')
else:
    all_workouts = pd.DataFrame()


def write_json(workout, workout_name, directory):
    json_string = json.dumps(workout, indent=4)
    file_name = os.path.join(f"{directory}/{workout_name}.json")
    if not os.path.exists(f"{directory}"):
        os.makedirs(f"{directory}")
    # print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()

def create_workout(file_name):
    if 'None' not in file_name:
        detail_data = pd.read_csv(f'{csv_files_folder}/{file_name}')
        start_time = datetime.datetime.strptime(detail_data.timestamp.values[0], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=4)
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        summary = all_workouts[all_workouts.Date == start_time]

        workout = {}
        exercises = []
        if len(summary) > 0:
            activity_type = summary['Activity Type'].values[0]
            workout['name'] = summary.Title.values[0]
            workout['distance'] = float(summary.Distance) * 1609
            start_time = datetime.datetime.strptime(detail_data.timestamp.values[0], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(detail_data.timestamp.values[-1], "%Y-%m-%d %H:%M:%S")
            duration = summary['Time'].values[0]
            duration = duration.split(":")
            duration = float(duration[0]) * 60 * 60 + float(duration[1]) * 60 + float(duration[2])
            workout['duration_seconds'] = duration
            if activity_type == 'Running':
                workout['name'] = summary.Title.values[0]
                workout['distance'] = float(summary.Distance) * 1609
                start_time = datetime.datetime.strptime(detail_data.timestamp.values[0], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.datetime.strptime(detail_data.timestamp.values[-1], "%Y-%m-%d %H:%M:%S")
                duration = summary['Time'].values[0]
                duration = duration.split(":")
                duration = float(duration[0]) * 60 * 60 + float(duration[1]) * 60 + float(duration[2])
                workout['duration_seconds'] = duration
                exercises = get_exercises(detail_data)

            elif activity_type == 'Cycling':
                exercise = {}
                exercise['name'] = summary.Title.values[0]
                exercise['distance'] = float(summary.Distance) * 1609 # detail_data.distance.values[-1]
                start_time = datetime.datetime.strptime(detail_data.timestamp.values[0], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.datetime.strptime(detail_data.timestamp.values[-1], "%Y-%m-%d %H:%M:%S")
                duration = summary['Time'].values[0]
                duration = duration.split(":")
                duration = float(duration[0]) * 60 * 60 + float(duration[1]) * 60 + float(duration[2])
                exercise['duration'] = duration  # (end_time - start_time).seconds
                exercise['hr'] = list(detail_data.heart_rate.values)
                exercises.append(exercise)
            else:
                print(summary.Title.values[0])
                return None
        else:
            print('no summary found', start_time)

            workout['name'] = f"Unnamed run {start_time.split(' ')[0]}"
            workout['distance'] = detail_data.distance.values[-1]
            start_time = datetime.datetime.strptime(detail_data.timestamp.values[0], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(detail_data.timestamp.values[-1], "%Y-%m-%d %H:%M:%S")
            workout['duration_seconds'] = (end_time - start_time).seconds
            workout['speed'] =  np.mean(detail_data.enhanced_speed)
            exercises = get_exercises(detail_data)

        section = {}
        section['name'] = "workout"
        section['duration_seconds'] = workout['duration_seconds']
        section['exercises'] = exercises
        section['start_date_time'] = format_datetime(start_time)
        section['end_date_time'] = format_datetime(end_time)

        # workout = {}
        # workout['name'] = exercise['name']
        # workout['duration_seconds'] = exercise['duration']
        workout['workout_sections'] = [section]
        # workout['distance'] = exercise['distance']
        workout['event_date_time'] = format_datetime(start_time)
        workout['program_module_id'] = f"{workout['name']}_{format_datetime(start_time)}"
        workout['program_id'] = "garmin_data"
        write_json(workout, file_name.split('.')[0], workouts_folder)



def get_exercises(detail_data):
    detail_data['speed_mph'] = detail_data.enhanced_speed * 3600 / 1609

    detail_data['timestamp'] = [datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S") for time_string in detail_data.timestamp.values]
    detail_data['duration'] = [(ts - detail_data['timestamp'][0]).seconds for ts in detail_data.timestamp.values]
    speed_zones = define_cadence_zone(detail_data)
    speed_blocks = get_block(speed_zones, min_change=1)
    detail_data['speed_blocks'] = speed_blocks
    detail_data['epoch_time'] = [dt.timestamp() for dt in detail_data['timestamp']]
    detail_data['speed_zones'] = speed_zones
    plt.subplot(313)
    plt.plot(speed_zones)

    grouped = detail_data.groupby(by='speed_blocks')

    group_aggs = grouped.agg(['mean', 'count', 'sum', 'min', 'max'])
    running_exercises = []
    for i, row in group_aggs.iterrows():
        ex = dict()
        ex['start_date_time'] = format_datetime(get_datetime_from_timestamp(row['epoch_time']['min']))
        ex['end_date_time'] = format_datetime(get_datetime_from_timestamp(row['epoch_time']['max']))
        ex['speed'] = round(row['enhanced_speed']['mean'], 2)
        speed_zone = _get_speed_zones(ex['speed'])
        if speed_zone.name == 'walking':
            ex['movement_id'] = 'jog'
            ex['name'] = 'jog'
        elif speed_zone.name == 'jogging':
            ex['movement_id'] = 'jog'
            ex['name'] = 'jog'
        elif speed_zone.name == 'running':
            ex['movement_id'] = 'run'
            ex['name'] = 'run'
        elif speed_zone.name == 'sprinting':
            ex['movement_id'] = 'cruising'
            ex['name'] = 'cruising'
        else:
            ex['movement_id'] = 'run'
            ex['name'] = 'run'
        # ex['grade'] = round(row['incline']['mean'] / 100, 3)
        ex['pace'] = round(1 / ex['speed'], 2)
        # ex['hr'] = int(row['heartrate']['mean'])
        ex['hr'] = list(detail_data.heart_rate[(detail_data.epoch_time > row['epoch_time']['min']) & (detail_data.epoch_time < row['epoch_time']['max'])])

        ex['distance'] = row['distance']['max'] - row['distance']['min']
        ex['duration'] = row['duration']['max'] - row['duration']['min']
        if ex['duration'] > 10 and ex['speed'] > 0:
            running_exercises.append(ex)
    return running_exercises

class CadenceZone(Enum):
    walking = 10
    jogging = 20
    running = 30
    sprinting = 40

def define_cadence_zone(data):
    cadence = data['speed_mph']
    duration = data['duration'].values
    start_index = 0
    cadence_zone = np.zeros(len(cadence))
    last_updated_index = 0
    current_zone = _get_speed_zones(cadence[0])
    for i in range(start_index, len(cadence)):
        if i == len(cadence) - 1:  # end of the block
            cadence_zone[last_updated_index:i] = current_zone.value
        elif np.isnan(cadence[i]):
            continue
        elif _get_speed_zones(cadence[i]) == current_zone:
            cadence_zone[last_updated_index:i] = current_zone.value
            last_updated_index = i
        else:
            if duration[i] - duration[last_updated_index] >= 30:
                current_zone = _get_speed_zones(cadence[i])
                cadence_zone[last_updated_index:i] = current_zone.value
                last_updated_index = i
    return cadence_zone
    print('here')


# def _get_cadence_zone(cadence):
#     if cadence <= 130:
#         return CadenceZone.walking
#     elif 130 < cadence <= 165:
#         return CadenceZone.jogging
#     elif 165 < cadence <= 195:
#         return CadenceZone.running
#     else:
#         return CadenceZone.sprinting


def _get_speed_zones(speed):
    if speed <= 4:
        return CadenceZone.walking
    elif 4 < speed <= 5.5:
        return CadenceZone.jogging
    elif 5.5 < speed <= 8:
        return CadenceZone.running
    else:
        return CadenceZone.sprinting


def _get_cadence(peaks):
    peak_diff = np.ediff1d(peaks, to_begin=0).astype(float)
    peak_diff[0] = peak_diff[1]
    peak_diff = pd.Series(peak_diff).rolling(window=3, center=True).mean().values
    peak_diff[np.where(peak_diff > 400)[0]] = np.nan
    peak_diff[0] = peak_diff[1]
    peak_diff[-1] = peak_diff[-2]
    cadence = 100 / peak_diff * 60 * 2
    cadence = pd.Series(cadence).rolling(window=3, center=True).mean().values
    cadence[0] = cadence[1]
    cadence[-1] = cadence[-2]

    return cadence

def interpolate_cadence(peaks, cadence):
    x = [int((peaks[i-1] + peaks[i]) / 2) for i in range(1, len(peaks))]
    x.extend(peaks.tolist())
    x = sorted(x)
    y = np.interp(x, xp=peaks, fp=cadence)
    return x, y



def filter_data(x, filt='band', lowcut=0.1, highcut=40, fs=97.5, order=4):
    """forward-backward bandpass butterworth filter
    defaults:
        lowcut freq: 0.1
        hicut freq: 20
        sampling rage: 100hz
        order: 4"""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    if filt == 'low':
        b, a = butter(order, high, btype='low', analog=False)
    elif filt == 'band':
        b, a = butter(order, [low, high], btype='band', analog=False)
    return filtfilt(b, a, x, axis=0)


def get_ranges(col_data, value, return_length=False):
    """
    For a given categorical data, determine start and end index for the given value
    start: index where it first occurs
    end: index after the last occurrence

    Args:
        col_data
        value: int, value to get ranges for
        return_length: boolean, return the length each range
    Returns:
        ranges: 2d array, start and end index for each occurrence of value
        length: array, length of each range
    """

    # determine where column data is the relevant value
    is_value = np.array(np.array(col_data == value).astype(int)).reshape(-1, 1)

    # if data starts with given value, range starts with index 0
    if is_value[0] == 1:
        t_b = 1
    else:
        t_b = 0

    # mark where column data changes to and from the given value
    absdiff = np.abs(np.ediff1d(is_value, to_begin=t_b))

    # handle the closing edge
    # if the data ends with the given value, if it was the only point, ignore the range,
    # else assign the last index as end of range
    if is_value[-1] == 1:
        if absdiff[-1] == 0:
            absdiff[-1] = 1
        else:
            absdiff[-1] = 0
    # get the ranges where values begin and end
    ranges = np.where(absdiff == 1)[0].reshape((-1, 2))

    if return_length:
        length = ranges[:, 1] - ranges[:, 0]
        return ranges, length
    else:
        return ranges

def get_block(series, min_change, min_duration=1):
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

def get_datetime_from_timestamp(timestamp, tz_info=None):
    return datetime.datetime.fromtimestamp(timestamp, tz=tz_info)

if __name__ == '__main__':
    count = 0
    all_files = os.listdir(csv_files_folder)
    for file_name in all_files:
        # if count > 0:
        #     break
        if '.csv' in file_name:
            create_workout(file_name)
            count += 1
    print('here')