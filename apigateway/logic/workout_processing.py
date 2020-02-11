from datastores.movement_library_datastore import MovementLibraryDatastore
from models.cardio_data import get_cardio_data
from models.movement_tags import AdaptationType, TrainingType
from models.movement_actions import ExternalWeight
from models.exercise import UnitOfMeasure
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
        self.add_action_details_to_exercise(exercise, movement)

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            exercise.convert_reps_to_duration(cardio_data)

    def add_action_details_to_exercise(self, exercise, movement):
        for action_id in movement.primary_actions:
            action = action_library.get(action_id)
            if action is not None:
                self.process_action(action, exercise)
                exercise.primary_actions.append(action)

        for action_id in movement.secondary_actions:
            action = action_library.get(action_id)
            if action is not None:
                self.process_action(action, exercise)
                exercise.secondary_actions.append(action)

        exercise.apply_explosiveness_to_actions()

    def process_action(self, action, exercise):
        external_weight = ExternalWeight(exercise.equipment, exercise.weight_in_lbs)
        action.external_weight = [external_weight]

        # action.reps = exercise.reps_per_set
        if action.training_type == TrainingType.strength_cardiorespiratory:
            action.reps = self.convert_reps_to_duration(exercise.reps_per_set, exercise.unit_of_measure, exercise.cardio_action)
        elif exercise.unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            reps_meters = self.convert_distance_to_meters(exercise.reps_per_set, exercise.unit_of_measure)
            action.reps = int(reps_meters / 5)
        elif exercise.unit_of_measure == UnitOfMeasure.seconds:
            action.reps = self.convert_seconds_to_reps(exercise.reps_per_set)
        else:
            action.reps = exercise.reps_per_set

        action.side = exercise.side
        action.rpe = exercise.rpe
        action.get_training_load()


    def convert_reps_to_duration(self, reps, unit_of_measure, cardio_action):
        # distance to duration
        if unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            reps = self.convert_distance_to_meters(reps, unit_of_measure)
            reps = self.convert_meters_to_seconds(reps, cardio_action)
        elif unit_of_measure == UnitOfMeasure.calories:
            reps = self.convert_calories_to_seconds(reps, cardio_action)
        return reps


    @staticmethod
    def convert_seconds_to_reps(reps):
        # TODO: need this conversion. Is it universal conversion?
        return reps

    @staticmethod
    def convert_distance_to_meters(reps, unit_of_measure):
        if unit_of_measure == UnitOfMeasure.yards:
            reps *= .9144
        elif unit_of_measure == UnitOfMeasure.feet:
            reps *= 0.3048
        elif unit_of_measure == UnitOfMeasure.miles:
            reps *= 1609.34
        elif unit_of_measure == UnitOfMeasure.kilometers:
            reps *= 1000
        return reps

    @staticmethod
    def convert_meters_to_seconds(reps, cardio_action):
        distance_parameters = cardio_data['distance_parameters']
        conversion_ratio = distance_parameters["normalizing_factors"][cardio_action.name]
        time_per_meter = distance_parameters['time_per_unit']
        reps = int(reps * conversion_ratio * time_per_meter)

        return reps

    @staticmethod
    def convert_calories_to_seconds(reps, cardio_action):
        calorie_parameters = cardio_data['calorie_parameters']
        time_per_unit = calorie_parameters['unit'] / calorie_parameters["calories_per_unit"][cardio_action.name]
        reps = int(reps * time_per_unit)

        return reps
