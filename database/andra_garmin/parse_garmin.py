from fitparse import FitFile
import pandas as pd
import zipfile
import os

# data_series = 'april-june2020'
# data_series = 'july-sept2020'
data_series = 'aug-nov2019'

zipped_data_folder = f'garmin_data/{data_series}_zipped'
fit_files_folder = f'garmin_data/{data_series}'
csv_files_folder = f'csv_data/{data_series}'


# To start need to download the zipped files to garmin_data folder
# make sure all the directories exist
if not os.path.exists(zipped_data_folder):
    os.mkdir(zipped_data_folder)
if not os.path.exists(fit_files_folder):
    os.mkdir(fit_files_folder)
if not os.path.exists(csv_files_folder):
    os.mkdir(csv_files_folder)


with zipfile.ZipFile(f"garmin_data/{data_series}.zip", 'r') as zip_ref:
    zip_ref.extractall(zipped_data_folder)

all_zipped_files = os.listdir(f"garmin_data/{data_series}_zipped")
for file in all_zipped_files:
    if "DS_Store" not in file and ".zip" in file:
        with zipfile.ZipFile(f"{zipped_data_folder}/{file}", 'r') as zip_ref:
            zip_ref.extractall(fit_files_folder)
fit_files = os.listdir(fit_files_folder)

for fit_file in fit_files:
    if "DS_Store" not in fit_file and ".fit" in fit_file:

        try:
            fitfile = FitFile(f"{fit_files_folder}/{fit_file}")
            fit_data = pd.DataFrame()
            fitfile.parse()
            # Get all data messages that are of type record
            counter = 0
            date = None
            for record in fitfile.get_messages('record'):
                if counter == 0:
                    date = record.get_value('timestamp').strftime("%Y-%m-%d")
                    counter += 1
                fit_data = fit_data.append(record.get_values(), ignore_index=True)
            fit_data.to_csv(f"{csv_files_folder}/{date}-{fit_file.split('.')[0]}.csv", index=False)
        except Exception as e:
            print(fit_file)
            print(e)
