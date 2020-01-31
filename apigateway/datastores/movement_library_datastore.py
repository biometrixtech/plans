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
        # file_name = Config.get('PROVIDER_INFO')['exercise_library_filename']
        file_name = "movement_library_soflete.json"
        movements = {}
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir,'../models', file_name)
        with open(file_path, 'r') as f:
            all_movements = json.load(f)

        for mov_id, movement_dict in all_movements.items():
            movements[mov_id] = Movement.json_deserialise(movement_dict)

        return movements
