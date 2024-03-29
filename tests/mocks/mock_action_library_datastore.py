import os
import json

from models.movement_actions import ExerciseAction
from fathomapi.api.config import Config


class ActionLibraryDatastore(object):
    def get(self):
        return self._read_json()

    def _read_json(self):
        actions = {}
        try:
            file_name = Config.get('PROVIDER_INFO')['action_library_filename']
        except KeyError:
            print('Action library not defined or does not exist for this provider, using default')
            file_name = 'actions_library.json'
        try:
            curpath = os.path.abspath(os.curdir)
            if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
                file_path = os.path.join(curpath, 'apigateway/models', file_name)
            else:
                file_path = os.path.join(curpath, '../../apigateway/models', file_name)
            with open(file_path, 'r') as f:
                all_actions = json.load(f)
            for action_id, action_dict in all_actions.items():
                actions[action_id] = ExerciseAction.json_deserialise(action_dict)

        except FileNotFoundError:
            print("Action library does not exist")

        return actions
