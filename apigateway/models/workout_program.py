from models.exercise import UnitOfMeasure, WeightMeasure
from models.movement_tags import AdaptationType, CardioAction, TrainingType, Equipment, MovementSurfaceStability
from models.movement_actions import ExerciseAction
from utils import format_datetime, parse_datetime

import re
import datetime
from serialisable import Serialisable


class WorkoutProgramModule(Serialisable):
    def __init__(self):
        self.session_id = None
        self.user_id = None
        self.event_date_time = None
        self.program_id = None
        self.program_module_id = None
        self.workout_sections = []

    def json_serialise(self):
        ret = {
            'session_id': self.session_id,
            'use_id': self.user_id,
            'event_date_time': format_datetime(self.event_date_time),
            'program_id': self.program_id,
            'program_module_id': self.program_module_id,
            'workout_sections': [w.json_serialise() for w in self.workout_sections]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout_program_module = cls()
        workout_program_module.session_id = input_dict.get('session_id')
        workout_program_module.user_id = input_dict.get('user_id')
        workout_program_module.event_date_time = input_dict.get('event_date_time')
        workout_program_module.program_id = input_dict.get('program_id')
        workout_program_module.program_module_id = input_dict.get('program_module_id')
        workout_program_module.workout_sections = [WorkoutSection.json_deserialise(workout_section) for workout_section in input_dict.get('workout_sections', [])]

        return workout_program_module

    def __setattr__(self, key, value):
        if key in ['event_date']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)

        super().__setattr__(key, value)

    def aggregate_shrz(self):
        weighted_sum = 0
        duration = 0
        shrz = 1
        for section in self.workout_sections:
            if section.shrz is not None:
                weighted_sum += section.shrz * section.duration_seconds
                duration += section.duration_seconds
        if duration > 0:
            shrz = round(weighted_sum / duration, 2)
        return max(1, shrz)



    # def get_training_load(self):
    #     total_load = 0
    #
    #     for section in self.workout_sections:
    #         total_load += section.get_training_load()
    #
    #     return total_load


class WorkoutSection(Serialisable):
    def __init__(self):
        self.name = ''
        self.start_date_time = None
        self.end_date_time = None
        self.duration_seconds = None
        self.assess_load = True
        self.assess_shrz = True
        self.shrz = None
        self.exercises = []

    def json_serialise(self):
        ret = {
            'name': self.name,
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'end_date_time': format_datetime(self.end_date_time) if self.end_date_time is not None else None,
            'duration_seconds': self.duration_seconds,
            'assess_load': self.assess_load,
            'assess_shrz': self.assess_shrz,
            'shrz': self.shrz,
            'exercises': [e.json_serialise() for e in self.exercises]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        workout_section = cls()
        workout_section.name = input_dict.get('name')
        workout_section.start_date_time = parse_datetime(input_dict['start_date_time']) if input_dict.get('start_date_time') is not None else None
        workout_section.end_date_time = parse_datetime(input_dict['end_date_time']) if input_dict.get('end_date_time') is not None else None
        workout_section.duration_seconds = input_dict.get('duration_seconds')
        workout_section.shrz = input_dict.get('shrz')
        workout_section.assess_load = input_dict.get('assess_load', True)
        workout_section.assess_shrz = input_dict.get('assess_shrz', True)
        workout_section.exercises = [WorkoutExercise.json_deserialise(workout_exercise) for workout_exercise in input_dict.get('exercises', [])]

        return workout_section

    def __setattr__(self, key, value):
        if key in ['start_date_time', 'end_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)

        super().__setattr__(key, value)

    def should_assess_load(self, no_load_sections):
        section = self.name.lower().replace("-", "_")
        for keyword in no_load_sections:
            pat = r'\b' + keyword + r'\b'
            if re.search(pat, section) is not None:
                self.assess_load = False

    def should_assess_shrz(self):
        if not self.assess_load:
            self.assess_shrz = False
        else:
            for exercise in self.exercises:
                # TODO: validate the filtering here
                if exercise.training_type in [TrainingType.power_action_plyometrics, TrainingType.power_drills_plyometrics,
                                              TrainingType.strength_integrated_resistance
                                              ]:
                    self.assess_shrz = False
                    break
        if not self.assess_shrz:
            self.shrz = None
            for exercise in self.exercises:
                exercise.shrz = None
                for action in exercise.primary_actions:
                    action.shrz = None
                for action in exercise.secondary_actions:
                    action.shrz = None

    # def get_training_load(self):
    #
    #     total_load = 0
    #
    #     if self.assess_load:
    #         for exercise in self.exercises:
    #             total_load += exercise.get_training_load()
    #
    #     return total_load


class WorkoutExercise(Serialisable):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.weight_measure = None
        self.weight = None
        self.sets = 1
        self.reps_per_set = 1
        self.unit_of_measure = UnitOfMeasure.count
        self.rpe = None
        self.side = 0
        self.bilateral = True
        self.movement_id = ""

        # for cardio exercises
        self.duration = None  # duration in seconds for cardio exercises
        self.distance = None  # distance covered for cardio exercises
        self.speed = None  # in m/s
        self.pace = None  # pace as time(s)/distance. distance is 500m for rowing, 1mile for running
        self.stroke_rate = None  # stroke rate for rowing
        self.cadence = None  # for biking/running
        self.power = None  # power for rowing/other cardio in watts
        self.force = None  # force exerted in Newtons
        self.calories = None  # for rowing/other cardio
        self.grade = None  # for biking/running
        self.force = None

        self.training_type = None
        self.explosiveness_rating = 0
        self.equipments = []   # TODO: do we get this from the api
        self.adaptation_type = None
        self.body_position = None
        self.cardio_action = None
        self.power_action = None
        self.power_drill_action = None
        self.strength_endurance_action = None
        self.strength_resistance_action = None
        self.surface_stability = None
        self.primary_actions = []
        self.secondary_actions = []
        self.shrz = None

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'weight_measure': self.weight_measure.value if self.weight_measure is not None else None,
            'weight': self.weight,
            'sets': self.sets,
            'reps_per_set': self.reps_per_set,
            'unit_of_measure': self.unit_of_measure.value if self.unit_of_measure is not None else None,
            'rpe': self.rpe,
            'side': self.side,
            'bilateral': self.bilateral,
            'movement_id': self.movement_id,
            'duration': self.duration,
            'distance': self.distance,
            'speed': self.speed,
            'pace': self.pace,
            'stroke_rate': self.stroke_rate,
            'cadence': self.cadence,
            'power': self.power,
            'force': self.force,
            'calories': self.calories,
            'grade': self.grade,
            'equipments': [equipment.value for equipment in self.equipments],
            'adaptation_type': self.adaptation_type.value if self.adaptation_type is not None else None,
            'cardio_action': self.cardio_action.value if self.cardio_action is not None else None,
            'power_action': self.power_action.value if self.power_action is not None else None,
            'power_drill_action': self.power_drill_action.value if self.power_drill_action is not None else None,
            'strength_endurance_action': self.strength_endurance_action.value if self.strength_endurance_action is not None else None,
            'strength_resistance_action': self.strength_resistance_action.value if self.strength_resistance_action is not None else None,
            'training_type': self.training_type.value if self.training_type is not None else None,
            'explosiveness_rating': self.explosiveness_rating,
            'surface_stability': self.surface_stability.value if self.surface_stability is not None else None,
            # 'primary_actions': [action.json_serialise() for action in self.primary_actions],
            # 'secondary_actions': [action.json_serialise() for action in self.secondary_actions],
            'shrz': self.shrz
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        exercise = cls()
        exercise.id = input_dict.get('id', '')
        exercise.name = input_dict.get('name', '')
        exercise.weight = input_dict.get('weight')
        exercise.equipments = [Equipment(equipment) for equipment in input_dict.get('equipments', [])]
        exercise.weight_measure = WeightMeasure(input_dict['weight_measure']) if input_dict.get('weight_measure') is not None else None
        exercise.sets = input_dict.get('sets', 0)
        exercise.reps_per_set = input_dict.get('reps_per_set', 0)
        exercise.unit_of_measure = UnitOfMeasure(input_dict['unit_of_measure']) if input_dict.get('unit_of_measure') is not None else None
        exercise.movement_id = input_dict.get('movement_id')
        exercise.intensity_pace = input_dict.get('intensity_pace')
        exercise.adaptation_type = AdaptationType(input_dict['adaptation_type']) if input_dict.get(
            'adaptation_type') is not None else None
        exercise.explosiveness_rating = input_dict.get('explosiveness_rating', False)
        exercise.side = input_dict.get('side', 0)
        exercise.bilateral = input_dict.get('bilateral', True)

        # not yet sure if these are needed
        # exercise.body_position = BodyPosition(input_dict['body_position']) if input_dict.get(
        #     'body_position') is not None else None
        exercise.cardio_action = CardioAction(input_dict['cardio_action']) if input_dict.get(
            'cardio_action') is not None else None
        exercise.training_type = TrainingType(input_dict['training_type']) if input_dict.get(
            'training_type') is not None else None
        exercise.rpe = input_dict.get('rpe')
        exercise.duration = input_dict.get('duration')
        exercise.distance = input_dict.get('distance')
        exercise.speed = input_dict.get('speed')
        exercise.pace = input_dict.get('pace')
        exercise.stroke_rate = input_dict.get('stroke_rate')
        exercise.cadence = input_dict.get('cadence')
        exercise.power = input_dict.get('power')
        exercise.force = input_dict.get('force')
        exercise.calories = input_dict.get('calories')
        exercise.grade = input_dict.get('grade')
        exercise.surface_stability = MovementSurfaceStability(input_dict['surface_stability']) if input_dict.get('surface_stability') is not None else None
        exercise.primary_actions = [ExerciseAction.json_deserialise(action) for action in input_dict.get('primary_actions', [])]
        exercise.secondary_actions = [ExerciseAction.json_deserialise(action) for action in input_dict.get('secondary_actions', [])]
        exercise.shrz = input_dict.get('shrz')

        return exercise

    # def get_training_volume(self):
    #     if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
    #         # cardiorespiratory should always be stored in seconds as unit of measure
    #         # self.convert_to_duration()
    #         # self.unit_of_measure = UnitOfMeasure.seconds
    #         return self.reps_per_set * self.sets
    #     else:
    #         if self.unit_of_measure == UnitOfMeasure.count:
    #             return self.reps_per_set * self.sets
    #         elif self.unit_of_measure == UnitOfMeasure.yards:
    #             return (self.reps_per_set * self.sets) / 5
    #         elif self.unit_of_measure == UnitOfMeasure.meters:
    #             return (self.reps_per_set * self.sets) / 5
    #         elif self.unit_of_measure == UnitOfMeasure.feet:
    #             return (self.reps_per_set * self.sets) / 15
    #         else:
    #             return 0
    #
    # def get_training_intensity(self):
    #     if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
    #         if self.rpe is None:
    #             return 4  # default of 4 if no RPE provided
    #         else:
    #             return self.rpe  # able to take RPE value, if provided
    #     else:
    #         return 0
    #
    # def get_training_load(self):
    #     training_load = 0
    #     for action in self.primary_actions:
    #         action.get_training_load()
    #         training_load += action.total_load_left
    #         training_load += action.total_load_right
    #     for action in self.secondary_actions:
    #         action.get_training_load()
    #         training_load += action.total_load_left
    #         training_load += action.total_load_right
    #     return training_load
    #
    #     # training_volume = self.get_training_volume()
    #     # training_intensity = self.get_training_intensity()
    #
    #     # return training_volume * training_intensity

    def initialize_from_movement(self, movement):
        # self.body_position = movement.body_position
        self.cardio_action = movement.cardio_action
        self.power_drill_action = movement.power_drill_action
        self.power_action = movement.power_action
        self.strength_endurance_action = movement.strength_endurance_action
        self.strength_resistance_action = movement.strength_resistance_action
        self.training_type = movement.training_type
        self.explosiveness_rating = movement.explosiveness_rating
        self.surface_stability = movement.surface_stability
        self.equipments = movement.external_weight_implement  # TODO: do we get it from the api
        # self.set_adaption_type(movement)

    # def set_adaption_type(self, movement):
    #
    #     if movement.training_type == TrainingType.flexibility:
    #         self.adaptation_type = AdaptationType.not_tracked
    #     if movement.training_type == TrainingType.movement_prep:
    #         self.adaptation_type = AdaptationType.not_tracked
    #     if movement.training_type == TrainingType.skill_development:
    #         self.adaptation_type = AdaptationType.not_tracked
    #     elif movement.training_type == TrainingType.strength_cardiorespiratory:
    #         self.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    #     elif movement.training_type == TrainingType.strength_endurance:
    #         self.adaptation_type = AdaptationType.strength_endurance_strength
    #     elif movement.training_type == TrainingType.power_action_plyometrics:
    #         self.adaptation_type = AdaptationType.power_explosive_action
    #     elif movement.training_type == TrainingType.power_action_olympic_lift:
    #         self.adaptation_type = AdaptationType.power_explosive_action
    #     elif movement.training_type == TrainingType.power_drills_plyometrics:
    #         self.adaptation_type = AdaptationType.power_drill
    #     elif movement.training_type == TrainingType.strength_integrated_resistance:
    #         self.adaptation_type = AdaptationType.strength_endurance_strength
    #
    # def convert_reps_to_duration(self, cardio_data):
    #     # distance to duration
    #     if self.unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
    #         distance_parameters = cardio_data['distance_parameters']
    #         self.convert_distance_to_meters()
    #         self.convert_meters_to_seconds(distance_parameters)
    #     elif self.unit_of_measure == UnitOfMeasure.calories:
    #         calorie_parameters = cardio_data['calorie_parameters']
    #         self.convert_calories_to_seconds(calorie_parameters)
    #
    #     self.unit_of_measure = UnitOfMeasure.seconds
    #
    # def convert_distance_to_meters(self):
    #     if self.unit_of_measure == UnitOfMeasure.yards:
    #         self.reps_per_set *= .9144
    #     elif self.unit_of_measure == UnitOfMeasure.feet:
    #         self.reps_per_set *= 0.3048
    #     elif self.unit_of_measure == UnitOfMeasure.miles:
    #         self.reps_per_set *= 1609.34
    #     elif self.unit_of_measure == UnitOfMeasure.kilometers:
    #         self.reps_per_set *= 1000
    #
    # def convert_meters_to_seconds(self, distance_parameters):
    #     conversion_ratio = distance_parameters["normalizing_factors"][self.cardio_action.name]
    #     time_per_meter = distance_parameters['time_per_unit']
    #     self.reps_per_set = int(self.reps_per_set * conversion_ratio * time_per_meter)
    #
    # def convert_calories_to_seconds(self, calorie_parameters):
    #     time_per_unit = calorie_parameters['unit'] / calorie_parameters["calories_per_unit"][self.cardio_action.name]
    #     self.reps_per_set = int(self.reps_per_set * time_per_unit)
