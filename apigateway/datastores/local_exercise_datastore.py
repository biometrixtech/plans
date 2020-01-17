import os
import json
from aws_xray_sdk.core import xray_recorder

import models.exercise
from utils import get_client


class ExerciseLibraryDatastore(object):
    @xray_recorder.capture('datastores.ExerciseLibraryDatastore.get')
    def get(self, client=None):
        return self._read_json(client)

    @xray_recorder.capture('datastores.ExerciseLibraryDatastore._read_json')
    def _read_json(self, client):
        if client is None:
            client = get_client()
        exercise_list = []
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir,'../models', f'exercise_library_{client}.json')
        with open(file_path, 'r') as f:
            exercises = json.load(f)

        for record in exercises:
            exercise_item = models.exercise.Exercise(record["library_id"])
            exercise_item.min_sets = record["min_sets"]
            exercise_item.seconds_per_rep = record["time_per_rep"]
            exercise_item.min_reps = record["min_reps"]
            exercise_item.unit_of_measure = record["unit_of_measure"]
            exercise_item.equipment_required = record["equipment_required"]
            exercise_item.technical_difficulty = record["technical_difficulty"]
            exercise_item.progresses_to = record["progresses_to"]
            exercise_item.seconds_rest_between_sets = record["seconds_rest_between_sets"]
            exercise_item.exposure_target = record["exposure_target"]
            exercise_item.progression_interval = record["progression_interval"]
            exercise_item.bilateral = record["bilateral"]
            exercise_item.max_reps = record["max_reps"]
            exercise_item.max_sets = record["max_sets"]
            exercise_item.name = record["name"]
            exercise_item.display_name = record["display_name"]
            exercise_item.youtube_id = record["youtube_id"]
            exercise_item.description = record["description"]
            # exercise_item.progressions = record["progressions"]
            # exercise_item.cues = record["cues"]
            # exercise_item.goal = record["goal"]
            # exercise_item.procedure = record["procedure"]
            # exercise_item.program_type = record["programType"]
            exercise_item.seconds_per_set = record["time_per_set"]
            # exercise_item.tempo = record["tempo"]
            exercise_list.append(exercise_item)

        return exercise_list
