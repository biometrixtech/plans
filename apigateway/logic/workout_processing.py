from datastores.movement_library_datastore import MovementLibraryDatastore
from models.cardio_data import get_cardio_data
# from models.workout_program import WorkoutProgramModule, WorkoutSection, WorkoutExercise

movement_library = MovementLibraryDatastore().get()
cardio_data = get_cardio_data()

class WorkoutProcessor(object):

    def process_workout(self, workout_program):
        for workout_section in workout_program.workout_sections():
            workout_section.should_track_load(cardio_data['no_rpe_sections'])
            for workout_exercise in workout_section.exercises:
                self.add_movement_detail_to_exercise(workout_exercise)

    def add_movement_detail_to_exercise(self, exercise):
        movement = movement_library[exercise.movement_id]
        exercise.process_movement(movement)
        exercise.distance_params = cardio_data['distance_conversion']
        exercise.calorie_params = cardio_data['calorie_conversion']
        exercise.convert_to_duration()
