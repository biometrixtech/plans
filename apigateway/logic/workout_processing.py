from datastores.movement_library_datastore import MovementLibraryDatastore
from models.cardio_data import get_cardio_data
from models.movement_tags import AdaptationType
from models.movement_actions import ExternalWeight
movement_library = MovementLibraryDatastore().get()
cardio_data = get_cardio_data()
action_library = {}


class WorkoutProcessor(object):

    def process_workout(self, workout_program):
        for workout_section in workout_program.workout_sections:
            workout_section.should_assess_load(cardio_data['no_load_sections'])
            for workout_exercise in workout_section.exercises:
                self.add_movement_detail_to_exercise(workout_exercise)

    def add_movement_detail_to_exercise(self, exercise):
        movement = movement_library[exercise.movement_id]
        exercise.process_movement(movement)
        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            exercise.convert_reps_to_duration(cardio_data)
        self.add_action_details_to_exercise(exercise, movement)

    @staticmethod
    def add_action_details_to_exercise(exercise, movement):
        for action_id in movement.primary_actions:
            action = action_library.get(action_id)
            if action is not None:
                external_weight = ExternalWeight(exercise.equipment, exercise.weight_in_lbs)
                action.external_weight = [external_weight]

                action.reps = exercise.reps_per_set
                action.side = exercise.side
                action.get_external_intensity()
                action.get_body_weight_intensity()
                action.get_training_volume()
                action.get_training_load()

                exercise.primary_actions.append(action)

        for action_id in movement.secondary_actions:
            action = action_library.get(action_id)
            if action is not None:
                external_weight = ExternalWeight(exercise.equipment, exercise.weight_in_lbs)
                action.external_weight = [external_weight]

                action.reps = exercise.reps_per_set
                action.side = exercise.side
                action.get_external_intensity()
                action.get_body_weight_intensity()
                action.get_training_volume()
                action.get_training_load()

                exercise.secondary_actions.append(action)
