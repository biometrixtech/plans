from aws_xray_sdk.core import xray_recorder
import os
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")


from datastores.local_exercise_datastore import ExerciseLibraryDatastore

def test_read_exercise_fathom():
    os.environ['EXERCISE_LIBRARY_FILENAME'] = 'exercise_library_fathom.json'
    ds = ExerciseLibraryDatastore()
    exercises = ds.get()
    assert len(exercises) > 0

def test_read_exercise_soflete():
    os.environ['EXERCISE_LIBRARY_FILENAME'] = 'exercise_library_soflete.json'
    ds = ExerciseLibraryDatastore()
    exercises = ds.get(client='soflete')
    assert len(exercises) == 0

