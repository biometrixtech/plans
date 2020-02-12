import os
import json
# from aws_xray_sdk.core import xray_recorder

from models.movement_actions import ExerciseAction
# from fathomapi.api.config import Config


class ActionLibraryDatastore(object):
    # @xray_recorder.capture('datastores.ActionLibraryDatastore.get')
    def get(self):
        return self._read_json()

    # @xray_recorder.capture('datastores.ActionLibraryDatastore._read_json')
    def _read_json(self):
        actions = {}
        file_name = 'action_library.json'
        # try:
        #     file_name = Config.get('PROVIDER_INFO')['movement_library_filename']
        # except KeyError:
        #     print('Movement library not defined or does nto exist for this provider')
        # else:
        try:
            script_dir = os.path.dirname(__file__)
            file_path = os.path.join(script_dir, '../models', file_name)
            with open(file_path, 'r') as f:
                all_actions = json.load(f)

            for action_id, action_dict in all_actions.items():
                actions[action_id] = ExerciseAction.json_deserialise(action_dict)
        except FileNotFoundError:
            print("Movement library does not exist for this provider")

        return actions
