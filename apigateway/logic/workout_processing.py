from datastores.movement_library_datastore import MovementLibraryDatastore
from models.cardio_data import get_cardio_data
from models.movement_tags import AdaptationType
movement_library = MovementLibraryDatastore().get()
cardio_data = get_cardio_data()


class WorkoutProcessor(object):

    def process_workout(self, workout_program):
        for workout_section in workout_program.workout_sections:
            workout_section.should_assess_load(cardio_data['no_load_sections'])
            for workout_exercise in workout_section.exercises:
                self.add_movement_detail_to_exercise(workout_exercise)

    @staticmethod
    def add_movement_detail_to_exercise(exercise):
        movement = movement_library[exercise.movement_id]
        exercise.process_movement(movement)
        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            exercise.convert_reps_to_duration(cardio_data)
