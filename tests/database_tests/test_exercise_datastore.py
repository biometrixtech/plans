from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from fathomapi.api.config import Config
from datastores.local_exercise_datastore import ExerciseLibraryDatastore


def test_read_exercise_fathom():
    Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                                 'body_part_mapping_filename': 'body_part_mapping_fathom.json'})
    ds = ExerciseLibraryDatastore()
    exercises = ds.get()
    assert len(exercises) > 0


# def test_read_exercise_soflete():
#     Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_soflete.json',
#                                  'body_part_mapping_filename': 'body_part_mapping_soflete.json'})
#     ds = ExerciseLibraryDatastore()
#     exercises = ds.get()
#     assert len(exercises) == 0
