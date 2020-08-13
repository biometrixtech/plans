import os
import json

from models.planned_exercise import PlannedWorkoutLoad
from fathomapi.api.config import Config


class PlannedWorkoutLibraryDatastore(object):
    def get(self):
        return self._read_json()

    def _read_json(self):
        workouts = {}
        # try:
        #     file_name = Config.get('PROVIDER_INFO')['action_library_filename']
        # except KeyError:
        #     print('Action library not defined or does not exist for this provider, using default')
        file_name = 'planned_workout_library.json'
        try:
            curpath = os.path.abspath(os.curdir)
            if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
                file_path = os.path.join(curpath, 'apigateway/models', file_name)
            else:
                file_path = os.path.join(curpath, '../../apigateway/models', file_name)
            with open(file_path, 'r') as f:
                all_workouts = json.load(f)
            for workout_id, workout_dict in all_workouts.items():
                workouts[workout_id] = PlannedWorkoutLoad.json_deserialise(workout_dict)

        except FileNotFoundError:
            print("Planned Workout library does not exist")

        return workouts
