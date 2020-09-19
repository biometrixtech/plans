from models.exercise import UnitOfMeasure, WeightMeasure
from models.movement_tags import AdaptationType, CardioAction, TrainingType, Equipment, MovementSurfaceStability, WeightDistribution
from models.movement_actions import CompoundAction
from utils import format_datetime, parse_datetime
from models.training_volume import StandardErrorRange, Assignment
from logic.calculators import Calculators

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
        workout_program_module.workout_sections = [CompletedWorkoutSection.json_deserialise(workout_section) for workout_section in input_dict.get('workout_sections', [])]

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


class WorkoutSection(object):
    def __init__(self):
        self.name = ''
        self.start_date_time = None
        self.duration_seconds = None
        self.assess_load = True
        self.exercises = []

    def should_assess_load(self, no_load_sections):
        section = self.name.lower().replace("-", "_")
        for keyword in no_load_sections:
            pat = r'\b' + keyword + r'\b'
            if re.search(pat, section) is not None:
                self.assess_load = False


class CompletedWorkoutSection(WorkoutSection, Serialisable):
    def __init__(self):
        super().__init__()
        self.end_date_time = None
        self.assess_shrz = True
        self.shrz = None

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
                for compound_action in exercise.compound_actions:
                    for action in compound_action.actions:
                        for sub_action in action.sub_actions:
                            sub_action.shrz = None
                # for action in exercise.primary_actions:
                #     action.shrz = None
                # for action in exercise.secondary_actions:
                #     action.shrz = None


class BaseWorkoutExercise(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.movement_id = ""
        self.training_type = None
        self.adaptation_type = None
        self.explosiveness_rating = 0
        self.surface_stability = None

        self.side = 0
        self.weight_measure = None
        self.weight = None
        self.sets = 1
        self.reps_per_set = None
        self.duration = None
        self.unit_of_measure = UnitOfMeasure.count

        self.cardio_action = None
        self.power_action = None
        self.power_drill_action = None
        self.strength_endurance_action = None
        self.strength_resistance_action = None
        self.movement_speed = None
        self.resistance = None
        self.displacement = None
        self.movement_rep_tempo = None

        self.compound_actions = []
        # self.primary_actions = []
        # self.secondary_actions = []

        self.equipments = []  # TODO: do we get this from the api

        self.training_intensity = 0

        self.rpe = None

        self.duration_per_rep = None

        self.tissue_load = None
        self.force_load = None
        self.power_load = None
        self.rpe_load = None

        self.predicted_rpe = None
        self.bilateral_distribution_of_resistance = None

        self.actions_for_power = []

    def initialize_from_movement(self, movement):
        # self.body_position = movement.body_position
        self.bilateral_distribution_of_resistance = movement.bilateral_distribution_of_resistance
        self.cardio_action = movement.cardio_action
        self.power_drill_action = movement.power_drill_action
        self.power_action = movement.power_action
        self.strength_endurance_action = movement.strength_endurance_action
        self.strength_resistance_action = movement.strength_resistance_action
        self.training_type = movement.training_type
        self.explosiveness_rating = movement.explosiveness_rating
        self.surface_stability = movement.surface_stability
        if len(self.equipments) == 0:
            # if none provided from the workout, inherit it from movement
            self.equipments = movement.external_weight_implement
        self.movement_speed = movement.speed
        self.resistance = movement.resistance
        self.displacement = movement.displacement
        self.movement_rep_tempo = movement.rep_tempo
        self.rest_between_reps = movement.rest_between_reps
        self.actions_for_power = movement.actions_for_power
        # self.set_adaption_type(movement)

    def set_adaptation_type(self, percent_rep_max=50):
        if self.training_type == TrainingType.flexibility:
            self.adaptation_type = AdaptationType.not_tracked
        if self.training_type == TrainingType.movement_prep:
            self.adaptation_type = AdaptationType.not_tracked
        if self.training_type == TrainingType.skill_development:
            self.adaptation_type = AdaptationType.not_tracked
        elif self.training_type == TrainingType.strength_cardiorespiratory:
            self.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
        elif self.training_type == TrainingType.strength_endurance:
            self.adaptation_type = AdaptationType.strength_endurance_strength
        elif self.training_type == TrainingType.power_action_plyometrics:
            self.adaptation_type = AdaptationType.power_explosive_action
        elif self.training_type == TrainingType.power_action_olympic_lift:
            self.adaptation_type = AdaptationType.power_explosive_action
        elif self.training_type == TrainingType.power_drills_plyometrics:
            self.adaptation_type = AdaptationType.power_drill
        elif self.training_type == TrainingType.strength_integrated_resistance:
            if percent_rep_max >= 75:
                self.adaptation_type = AdaptationType.maximal_strength_hypertrophic
            else:
                self.adaptation_type = AdaptationType.strength_endurance_strength

    def set_reps_duration(self):
        if self.actions_for_power is not None and len(self.actions_for_power) > 0:
            total_duration = sum([ac.time for ac in self.actions_for_power])
            if self.rest_between_reps is not None:
                total_duration += self.rest_between_reps
            self.duration_per_rep = StandardErrorRange(observed_value=total_duration)
        elif self.movement_rep_tempo is not None and len(self.movement_rep_tempo) > 0:
            total_duration = sum(self.movement_rep_tempo)
            if self.rest_between_reps is not None:
                total_duration += self.rest_between_reps
            self.duration_per_rep = StandardErrorRange(observed_value=total_duration)
        else:
            if self.adaptation_type == AdaptationType.strength_endurance_strength:
                self.duration_per_rep = StandardErrorRange(lower_bound=2, upper_bound=4, observed_value=3)
            elif self.adaptation_type == AdaptationType.power_drill:
                self.duration_per_rep = StandardErrorRange(lower_bound=3.5, upper_bound=7, observed_value=5)
            elif self.adaptation_type == AdaptationType.maximal_strength_hypertrophic:
                self.duration_per_rep = StandardErrorRange(lower_bound=3, upper_bound=5, observed_value=4)
            elif self.adaptation_type == AdaptationType.power_explosive_action:
                self.duration_per_rep = StandardErrorRange(lower_bound=1, upper_bound=2, observed_value=1.5)
            else:
                self.duration_per_rep = StandardErrorRange(lower_bound=2, upper_bound=4, observed_value=3)

    def get_exercise_reps_per_set(self):
        reps = StandardErrorRange(observed_value=0)
        if self.reps_per_set is not None:
            reps.observed_value = self.reps_per_set * self.sets
        elif self.duration is not None:
            possible_reps = []
            if isinstance(self.duration, Assignment):
                durations = [self.duration.min_value, self.duration.max_value, self.duration.assigned_value]
                durations = [dur for dur in durations if dur is not None]
            else:
                durations = [self.duration]
            if self.training_type in [TrainingType.power_action_plyometrics, TrainingType.power_drills_plyometrics]:
                # use a default for these training types so that rep count is not over inflated
                duration_per_reps = [2]
            else:
                duration_per_reps = [self.duration_per_rep.lower_bound, self.duration_per_rep.upper_bound, self.duration_per_rep.observed_value]
                duration_per_reps = [dur for dur in duration_per_reps if dur is not None]
            for dur in durations:
                for dur_per_rep in duration_per_reps:
                    possible_reps.append(dur / dur_per_rep)
            if len(possible_reps) > 0:
                reps.lower_bound = min(possible_reps)
                reps.upper_bound = max(possible_reps)
                reps.observed_value = sum(possible_reps) / len(possible_reps)
        # for unilateral alternating reps are defined as total reps but we need expected reps per side
        if self.bilateral_distribution_of_resistance == WeightDistribution.unilateral_alternating:
            reps.divide(2)
        return reps


class WorkoutExercise(BaseWorkoutExercise, Serialisable):
    def __init__(self):
        super().__init__()

        self.bilateral = True
        self.end_of_workout_hr = None
        self.hr = []
        self.start_date_time = None
        self.end_date_time = None

        # for cardio exercises
        #self.duration = None  # duration in seconds for cardio exercises
        self.distance = None  # distance covered for cardio exercises
        self.speed = None  # in m/s
        self.pace = None  # pace as time(s)/distance. distance is 500m for rowing, 1mile for running
        self.stroke_rate = None  # stroke rate for rowing
        self.cadence = None  # for biking/running
        self.power = None  # power for rowing/other cardio in watts
        self.force = None  # force exerted in Newtons
        self.calories = None  # for rowing/other cardio
        self.grade = None  # for biking/running

        self.rep_tempo = 0

        self.body_position = None

        self.shrz = None
        self.work_vo2 = None

        self.total_volume = None
        self.percent_time_at_65_80_max_hr = 0.0
        self.percent_time_at_80_85_max_hr = 0.0
        self.percent_time_at_85_above_max_hr = 0.0
        self.percent_time_below_vo2max = 0.0
        self.percent_time_above_vo2max = 0.0

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'start_date_time': format_datetime(self.start_date_time),
            'end_date_time': format_datetime(self.end_date_time),
            'weight_measure': self.weight_measure.value if self.weight_measure is not None else None,
            'weight': self.weight,
            'sets': self.sets,
            'reps_per_set': self.reps_per_set,
            'unit_of_measure': self.unit_of_measure.value if self.unit_of_measure is not None else None,
            'rpe': self.rpe.json_serialise() if self.rpe is not None else None,
            'side': self.side,
            'bilateral': self.bilateral,
            'movement_id': self.movement_id,
            'hr': self.hr,
            'end_of_workout_hr': self.end_of_workout_hr,
            'predicted_rpe':self.predicted_rpe.json_serialise() if self.predicted_rpe is not None else None,
            'duration': self.duration,
            'distance': self.distance,
            'speed': self.speed,
            'pace': self.pace,
            'stroke_rate': self.stroke_rate,
            'cadence': self.cadence,
            'power': self.power.json_serialise() if self.power is not None else None,
            'force': self.force.json_serialise() if self.force is not None else None,
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
            'shrz': self.shrz,
            'work_vo2': self.work_vo2.json_serialise() if self.work_vo2 is not None else None,
            'total_volume': self.total_volume,
            'tissue_load': self.tissue_load.json_serialise() if self.tissue_load is not None else None,
            'force_load': self.force_load.json_serialise() if self.tissue_load is not None else None,
            'power_load': self.power_load.json_serialise() if self.power_load is not None else None,
            'rpe_load': self.rpe_load.json_serialise() if self.rpe_load is not None else None,
            'percent_time_at_65_80_max_hr': self.percent_time_at_65_80_max_hr,
            'percent_time_at_80_85_max_hr': self.percent_time_at_80_85_max_hr,
            'percent_time_at_85_above_max_hr': self.percent_time_at_85_above_max_hr,
            'percent_time_below_vo2max': self.percent_time_below_vo2max,
            'percent_time_above_vo2max': self.percent_time_above_vo2max
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        exercise = cls()
        exercise.id = input_dict.get('id', '')
        exercise.name = input_dict.get('name', '')
        exercise.start_date_time = parse_datetime(input_dict['start_date_time']) if input_dict.get('start_date_time') is not None else None
        exercise.end_date_time = parse_datetime(input_dict['end_date_time']) if input_dict.get('end_date_time') is not None else None
        exercise.weight = input_dict.get('weight')
        exercise.equipments = [Equipment(equipment) for equipment in input_dict.get('equipments', [])]
        exercise.weight_measure = WeightMeasure(input_dict['weight_measure']) if input_dict.get('weight_measure') is not None else None
        exercise.sets = input_dict.get('sets', 1)
        exercise.reps_per_set = input_dict.get('reps_per_set')
        exercise.unit_of_measure = UnitOfMeasure(input_dict['unit_of_measure']) if input_dict.get('unit_of_measure') is not None else None
        exercise.movement_id = input_dict.get('movement_id')
        exercise.hr = input_dict.get('hr', [])
        exercise.end_of_workout_hr = input_dict.get('end_of_workout_hr')
        exercise.predicted_rpe = StandardErrorRange.json_deserialise(input_dict.get('predicted_rpe')) if input_dict.get('predicted_rpe') is not None else None
        exercise.intensity_pace = input_dict.get('intensity_pace')
        exercise.adaptation_type = AdaptationType(input_dict['adaptation_type']) if input_dict.get(
            'adaptation_type') is not None else None
        exercise.explosiveness_rating = input_dict.get('explosiveness_rating', 0)
        exercise.side = input_dict.get('side', 0)
        exercise.bilateral = input_dict.get('bilateral', True)

        # not yet sure if these are needed
        # exercise.body_position = BodyPosition(input_dict['body_position']) if input_dict.get(
        #     'body_position') is not None else None
        exercise.cardio_action = CardioAction(input_dict['cardio_action']) if input_dict.get(
            'cardio_action') is not None else None
        exercise.training_type = TrainingType(input_dict['training_type']) if input_dict.get(
            'training_type') is not None else None
        exercise.rpe = StandardErrorRange.json_deserialise(input_dict.get('rpe')) if input_dict.get('rpe') is not None else None
        exercise.duration = input_dict.get('duration')
        exercise.distance = input_dict.get('distance')
        exercise.speed = input_dict.get('speed')
        exercise.pace = input_dict.get('pace')
        exercise.stroke_rate = input_dict.get('stroke_rate')
        exercise.cadence = input_dict.get('cadence')
        exercise.power = StandardErrorRange.json_deserialise(input_dict.get('power')) if input_dict.get('power') is not None else None
        exercise.force = StandardErrorRange.json_deserialise(input_dict.get('force')) if input_dict.get('force') is not None else None
        exercise.calories = input_dict.get('calories')
        exercise.grade = input_dict.get('grade')
        exercise.surface_stability = MovementSurfaceStability(input_dict['surface_stability']) if input_dict.get('surface_stability') is not None else None
        exercise.compound_actions = [CompoundAction.json_deserialise(action) for action in input_dict.get('primary_actions', [])]
        # exercise.primary_actions = [ExerciseAction.json_deserialise(action) for action in input_dict.get('primary_actions', [])]
        # exercise.secondary_actions = [ExerciseAction.json_deserialise(action) for action in input_dict.get('secondary_actions', [])]
        exercise.shrz = input_dict.get('shrz')
        exercise.work_vo2 = StandardErrorRange.json_deserialise(input_dict.get('work_vo2')) if input_dict.get('work_vo2') is not None else None
        exercise.total_volume = input_dict.get('total_volume')
        exercise.tissue_load = StandardErrorRange.json_deserialise(input_dict.get('tissue_load')) if input_dict.get('tissue_load') is not None else None
        exercise.force_load = StandardErrorRange.json_deserialise(input_dict.get('force_load')) if input_dict.get(
            'force_load') is not None else None
        exercise.power_load = StandardErrorRange.json_deserialise(input_dict.get('power_load')) if input_dict.get(
            'power_load') is not None else None
        exercise.rpe_load = StandardErrorRange.json_deserialise(input_dict.get('rpe_load')) if input_dict.get(
            'rpe_load') is not None else None

        exercise.percent_time_at_65_80_max_hr = input_dict.get('percent_time_at_65_80_max_hr', 0.0)
        exercise.percent_time_at_80_85_max_hr = input_dict.get('percent_time_at_80_85_max_hr', 0.0)
        exercise.percent_time_at_85_above_max_hr = input_dict.get('percent_time_at_85_above_max_hr', 0.0)
        exercise.percent_time_below_vo2max = input_dict.get('percent_time_below_vo2max', 0.0)
        exercise.percent_time_above_vo2max = input_dict.get('percent_time_above_vo2max', 0.0)

        return exercise

    def set_intensity(self):
        if self.training_type == TrainingType.strength_cardiorespiratory:
            if self.rpe is None:
                self.rpe = StandardErrorRange(observed_value=4)
            self.training_intensity = self.shrz or self.rpe.observed_value
        elif self.training_type in [TrainingType.strength_endurance, TrainingType.strength_integrated_resistance]:
            self.set_strength_training_intensity()
        else:
            self.set_power_training_intensity()

    def set_power_training_intensity(self):
        self.training_intensity = self.explosiveness_rating

    def set_strength_training_intensity(self):
        self.training_intensity = 8

    def set_training_loads(self):
        if self.power is not None and self.total_volume is not None:
            power_load = self.power.plagiarize()
            power_load.multiply(self.total_volume)
            self.power_load = power_load
        if self.force is not None and self.total_volume is not None:
            force_load = self.force.plagiarize()
            force_load.multiply(self.total_volume)
            self.force_load = force_load
            self.tissue_load = self.force_load.plagiarize()
        if self.predicted_rpe is not None:
            rpe_load = self.predicted_rpe.plagiarize()
            rpe_load.multiply(self.total_volume)
            self.rpe_load = rpe_load

    def set_rep_tempo(self):
        if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            if self.cardio_action == CardioAction.row:
                if self.stroke_rate is None or self.stroke_rate <= 23:
                    self.rep_tempo = 1
                elif self.stroke_rate <= 28:
                    self.rep_tempo = 2
                elif self.stroke_rate <= 36:
                    self.rep_tempo = 3
                else:
                    self.rep_tempo = 4
            elif self.cardio_action == CardioAction.run:
                if self.cadence is None or self.cadence <= 130:
                    self.rep_tempo = 1  # walking
                elif self.cadence <= 165:
                    self.rep_tempo = 2  # jogging
                elif self.cadence <= 195:
                    self.rep_tempo = 3  # running
                else:
                    self.rep_tempo = 4  # sprinting
            elif self.cardio_action == CardioAction.cycle:
                if self.cadence is None or self.cadence <= 70:
                    self.rep_tempo = 1
                elif self.cadence <= 90:
                    self.rep_tempo = 2
                elif self.cadence <= 110:
                    self.rep_tempo = 3
                else:
                    self.rep_tempo = 4
            else:
                self.rep_tempo = 1

    def set_speed_pace(self):
        speed = None
        pace = None
        # get pace
        if self.pace is not None:
            # if self.cardio_action == CardioAction.row:
            #     pace = self.pace / 500  # row pace is s/500m
            # elif self.cardio_action == CardioAction.run:
            #     pace = self.pace / 1609.34  # run pace is s/1mile
            # else:
            pace = self.pace  # all others are s/m
        elif self.speed is not None:
            pace = 1 / self.speed
        elif self.duration is not None and self.distance is not None:
            pace = self.duration / self.distance
        elif self.power is not None:
            if self.cardio_action == CardioAction.row:
                pace = (2.8 / self.power.observed_value) ** (1 / 3)
        elif self.calories is not None and self.duration is not None:
            if self.cardio_action == CardioAction.row:
                self.power = StandardErrorRange()
                self.power.observed_value = (4200 * self.calories - .35 * self.duration) / (4 * self.duration)  # based on formula used by concept2 rower; reps is assumed to be in seconds
                # watts = exercise.calories / exercise.duration * 1000  # approx calculation; reps is assumed to be in seconds
                pace = (2.8 / self.power.observed_value) ** (1 / 3)

        # get speed
        if self.speed is not None:
            speed = self.speed
        elif self.duration is not None and self.distance is not None:
            speed = self.distance / self.duration
        elif pace is not None:
            speed = 1 / pace
        self.speed = speed
        self.pace = pace
        #return speed, pace

    def set_hr_zones(self, user_age):
        if len(self.hr) > 0:
            max_hr = 207 - .7 * user_age
            percent_max_hr = [round(hr / max_hr, 2) for hr in self.hr]
            zone1 = [perc_hr for perc_hr in percent_max_hr if .65 < perc_hr <=.8]
            zone2 = [perc_hr for perc_hr in percent_max_hr if .8 < perc_hr <=.85]
            zone3 = [perc_hr for perc_hr in percent_max_hr if .85 < perc_hr]
            self.percent_time_at_65_80_max_hr = round(len(zone1) / len(self.hr), 2)
            self.percent_time_at_80_85_max_hr = round(len(zone2) / len(self.hr), 2)
            self.percent_time_at_85_above_max_hr = round(len(zone3) / len(self.hr), 2)

            below_vo2max = [perc_hr for perc_hr in percent_max_hr if .5 < perc_hr < .8]
            above_vo2max = [perc_hr for perc_hr in percent_max_hr if perc_hr >=.8]

            self.percent_time_below_vo2max = round(len(below_vo2max) / len(self.hr), 2)
            self.percent_time_above_vo2max = round(len(above_vo2max) / len(self.hr), 2)

        else:
            if self.predicted_rpe is None:  # this should never be the case as we should always have predicted_rpe (here just in case)
                rpe = 4.0
            else:
                # get a single rpe based on presence of lower_bound, observed_value and upper_bound
                if self.predicted_rpe.observed_value is not None:
                    rpe = self.predicted_rpe.observed_value
                elif self.predicted_rpe.lower_bound is not None and self.predicted_rpe.upper_bound is not None:
                    rpe = (self.predicted_rpe.lower_bound + self.predicted_rpe.upper_bound) / 2
                elif self.predicted_rpe.lower_bound is not None:
                    rpe = self.predicted_rpe.lower_bound
                elif self.predicted_rpe.upper_bound is not None:
                    rpe = self.predicted_rpe.upper_bound
                else:
                    rpe = 4.0  # again should never happen

            percent_max_hr = Calculators.get_percent_max_hr_from_rpe(rpe)
            if .65 < percent_max_hr <= .8:
                self.percent_time_at_65_80_max_hr = 1.0
            elif .8 < percent_max_hr <= .85:
                self.percent_time_at_80_85_max_hr = 1.0
            elif .85 < percent_max_hr:
                self.percent_time_at_85_above_max_hr = 1.0
            if .5 < percent_max_hr < .8:
                self.percent_time_below_vo2max = 1.0
            elif percent_max_hr > .8:
                self.percent_time_above_vo2max = 1.0


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
