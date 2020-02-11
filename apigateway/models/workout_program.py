from models.exercise import UnitOfMeasure
from serialisable import Serialisable
from models.movement_tags import AdaptationType, BodyPosition, CardioAction, TrainingType, Equipment, MovementSurfaceStability
import re


class WorkoutProgramModule(Serialisable):
    def __init__(self):
        self.provider_id = None
        self.program_id = None
        self.program_module_id = None
        self.workout_sections = []

    def json_serialise(self):
        ret = {
            'provider_id': self.provider_id,
            'program_id': self.program_id,
            'program_module_id': self.program_module_id,
            'workout_sections': [w.json_serialise() for w in self.workout_sections]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout_program_module = cls()
        workout_program_module.provider_id = input_dict.get('provider_id')
        workout_program_module.program_id = input_dict.get('program_id')
        workout_program_module.program_module_id = input_dict.get('program_module_id')
        workout_program_module.workout_sections = [WorkoutSection.json_deserialise(workout_section) for workout_section in input_dict.get('workout_sections', [])]

        return workout_program_module

    def get_training_load(self):
        total_load = 0

        for section in self.workout_sections:
            total_load += section.get_training_load()

        return total_load


class WorkoutSection(Serialisable):
    def __init__(self):
        self.name = ''
        self.duration_seconds = None
        self.workout_section_type = None
        self.difficulty = None
        self.intensity_pace = None
        self.assess_load = True
        self.exercises = []

    def json_serialise(self):
        ret = {
            'name': self.name,
            'duration_seconds': self.duration_seconds,
            'workout_section_type': self.workout_section_type,
            'difficulty': self.difficulty,
            'intensity_pace': self.intensity_pace,
            'assess_load': self.assess_load,
            'exercises': [e.json_serialise() for e in self.exercises]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout_section = cls()
        workout_section.name = input_dict.get('name')
        workout_section.duration_seconds = input_dict.get('duration_seconds')
        workout_section.workout_section_type = input_dict.get('workout_section_type')
        workout_section.difficulty = input_dict.get('difficulty')
        workout_section.intensity_pace = input_dict.get('intensity_pace')
        workout_section.assess_load = input_dict.get('assess_load', True)
        workout_section.exercises = [WorkoutExercise.json_deserialise(workout_exercise) for workout_exercise
                                                   in input_dict.get('exercises', [])]

        return workout_section

    def should_assess_load(self, no_load_sections):
        section = self.name.lower().replace("-", "_")
        for keyword in no_load_sections:
            pat = r'\b' + keyword + r'\b'
            if re.search(pat, section) is not None:
                self.assess_load = False

    def get_training_load(self):

        total_load = 0

        if self.assess_load:
            for exercise in self.exercises:
                total_load += exercise.get_training_load()

        return total_load


class WorkoutExercise(Serialisable):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.weight_in_lbs = None
        self.equipment = None
        self.sets = 1
        self.reps_per_set = 1
        self.unit_of_measure = None
        self.movement_id = ""
        self.rpe = None
        self.side = 0

        self.intensity_pace = None

        self.adaptation_type = None
        self.body_position = None
        self.cardio_action = None
        self.training_type = None
        self.explosiveness_rating = 0
        self.surface_stability = None
        self.primary_actions = []
        self.secondary_actions = []

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'weight_in_lbs': self.weight_in_lbs,
            'equipment': self.equipment.value if self.equipment is not None else None,
            'sets': self.sets,
            'reps_per_set': self.reps_per_set,
            'unit_of_measure': self.unit_of_measure.value,
            'intensity_pace': self.intensity_pace,
            'adaptation_type': self.adaptation_type.value if self.adaptation_type is not None else None,
            'body_position': self.body_position.value if self.body_position is not None else None,
            'cardio_action': self.cardio_action.value if self.cardio_action is not None else None,
            'training_type': self.training_type.value if self.training_type is not None else None,
            'explosiveness_rating': self.explosiveness_rating,
            'surface_stability': self.surface_stability.value if self.surface_stability is not None else None,
            'rpe': self.rpe,
            'primary_actions': self.primary_actions,
            'secondary_actions': self.secondary_actions
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        exercise = cls()
        exercise.id = input_dict.get('id', '')
        exercise.name = input_dict.get('name', '')
        exercise.weight_in_lbs = input_dict.get('weight_in_lbs')
        exercise.equipment = Equipment(input_dict['equipment']) if input_dict.get('equipment') is not None else None
        exercise.sets = input_dict.get('sets', 0)
        exercise.reps_per_set = input_dict.get('reps_per_set', 0)
        exercise.unit_of_measure = UnitOfMeasure(input_dict['unit_of_measure']) if input_dict.get('unit_of_measure') is not None else None
        exercise.intensity_pace = input_dict.get('intensity_pace')
        exercise.adaptation_type = AdaptationType(input_dict['adaptation_type']) if input_dict.get(
            'adaptation_type') is not None else None
        exercise.explosiveness_rating = input_dict.get('explosiveness_rating', False)

        # not yet sure if these are needed
        exercise.body_position = BodyPosition(input_dict['body_position']) if input_dict.get(
            'body_position') is not None else None
        exercise.cardio_action = CardioAction(input_dict['cardio_action']) if input_dict.get(
            'cardio_action') is not None else None
        exercise.training_type = TrainingType(input_dict['training_type']) if input_dict.get(
            'training_type') is not None else None
        exercise.rpe = input_dict.get('rpe')
        exercise.surface_stability = MovementSurfaceStability(input_dict['surface_stability']) if input_dict.get('surface_stability') is not None else None
        exercise.primary_actions = input_dict.get('primary_actions', [])
        exercise.secondary_actions = input_dict.get('secondary_actions', [])

        return exercise

    def get_training_volume(self):
        if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            # cardiorespiratory should always be stored in seconds as unit of measure
            # self.convert_to_duration()
            # self.unit_of_measure = UnitOfMeasure.seconds
            return self.reps_per_set * self.sets
        else:
            if self.unit_of_measure == UnitOfMeasure.count:
                return self.reps_per_set * self.sets
            elif self.unit_of_measure == UnitOfMeasure.yards:
                return (self.reps_per_set * self.sets) / 5
            elif self.unit_of_measure == UnitOfMeasure.meters:
                return (self.reps_per_set * self.sets) / 5
            elif self.unit_of_measure == UnitOfMeasure.feet:
                return (self.reps_per_set * self.sets) / 15
            else:
                return 0

    def get_training_intensity(self):
        if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            if self.rpe is None:
                return 4  # default of 4 if no RPE provided
            else:
                return self.rpe  # able to take RPE value, if provided
        else:
            return 0

    def get_training_load(self):
        training_load = 0
        for action in self.primary_actions:
            action.get_training_load()
            training_load += action.total_load_left
            training_load += action.total_load_right
        for action in self.secondary_actions:
            action.get_training_load()
            training_load += action.total_load_left
            training_load += action.total_load_right
        return training_load

        # training_volume = self.get_training_volume()
        # training_intensity = self.get_training_intensity()

        # return training_volume * training_intensity

    def process_movement(self, movement):
        self.body_position = movement.body_position
        self.cardio_action = movement.cardio_action
        self.training_type = movement.training_type
        self.explosiveness_rating = movement.explosiveness_rating
        self.surface_stability = movement.surface_stability
        self.set_adaption_type(movement)

    def set_adaption_type(self, movement):

        if movement.training_type == TrainingType.flexibility:
            self.adaptation_type = AdaptationType.not_tracked
        if movement.training_type == TrainingType.movement_prep:
            self.adaptation_type = AdaptationType.not_tracked
        if movement.training_type == TrainingType.skill_development:
            self.adaptation_type = AdaptationType.not_tracked
        elif movement.training_type == TrainingType.strength_cardiorespiratory:
            self.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
        elif movement.training_type == TrainingType.strength_endurance:
            self.adaptation_type = AdaptationType.strength_endurance_strength
        elif movement.training_type == TrainingType.power_action_plyometrics:
            self.adaptation_type = AdaptationType.power_explosive_action
        elif movement.training_type == TrainingType.power_action_olympic_lift:
            self.adaptation_type = AdaptationType.power_explosive_action
        elif movement.training_type == TrainingType.power_drills_plyometrics:
            self.adaptation_type = AdaptationType.power_drill
        elif movement.training_type == TrainingType.strength_integrated_resistance:
            if self.intensity_pace >= 75:
                self.adaptation_type = AdaptationType.maximal_strength_hypertrophic
            else:
                self.adaptation_type = AdaptationType.strength_endurance_strength

    def convert_reps_to_duration(self, cardio_data):
        # distance to duration
        if self.unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            distance_parameters = cardio_data['distance_parameters']
            self.convert_distance_to_meters()
            self.convert_meters_to_seconds(distance_parameters)
        elif self.unit_of_measure == UnitOfMeasure.calories:
            calorie_parameters = cardio_data['calorie_parameters']
            self.convert_calories_to_seconds(calorie_parameters)

        self.unit_of_measure = UnitOfMeasure.seconds

    def convert_distance_to_meters(self):
        if self.unit_of_measure == UnitOfMeasure.yards:
            self.reps_per_set *= .9144
        elif self.unit_of_measure == UnitOfMeasure.feet:
            self.reps_per_set *= 0.3048
        elif self.unit_of_measure == UnitOfMeasure.miles:
            self.reps_per_set *= 1609.34
        elif self.unit_of_measure == UnitOfMeasure.kilometers:
            self.reps_per_set *= 1000

    def convert_meters_to_seconds(self, distance_parameters):
        conversion_ratio = distance_parameters["normalizing_factors"][self.cardio_action.name]
        time_per_meter = distance_parameters['time_per_unit']
        self.reps_per_set = int(self.reps_per_set * conversion_ratio * time_per_meter)

    def convert_calories_to_seconds(self, calorie_parameters):
        time_per_unit = calorie_parameters['unit'] / calorie_parameters["calories_per_unit"][self.cardio_action.name]
        self.reps_per_set = int(self.reps_per_set * time_per_unit)

