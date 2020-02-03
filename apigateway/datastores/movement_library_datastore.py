import os
import json
from aws_xray_sdk.core import xray_recorder

from models.workout_program import Movement
from fathomapi.api.config import Config


class MovementLibraryDatastore(object):
    @xray_recorder.capture('datastores.MovementLibraryDatastore.get')
    def get(self):
        return self._read_json()

    @xray_recorder.capture('datastores.MovementLibraryDatastore._read_json')
    def _read_json(self):
        movements = {}
        try:
            file_name = Config.get('PROVIDER_INFO')['movement_library_filename']
        except KeyError:
            print('Movement library not defined or does nto exist for this provider')
        else:
            try:
                script_dir = os.path.dirname(__file__)
                file_path = os.path.join(script_dir, '../models', file_name)
                with open(file_path, 'r') as f:
                    all_movements = json.load(f)

                for mov_id, movement_dict in all_movements.items():
                    movements[mov_id] = Movement.json_deserialise(movement_dict)
            except FileNotFoundError:
                print("Movement library does not exist for this provider")

        return movements
