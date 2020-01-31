from models.exercise import UnitOfMeasure
from serialisable import Serialisable
from models.movement_tags import AdaptationType, BodyPosition, MovementAction, TrainingType, Equipment


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


class WorkoutSection(Serialisable):
    def __init__(self):
        self.name = ''
        self.duration_seconds = None
        self.workout_section_type = None
        self.difficulty = None
        self.intensity_pace = None
        self.exercises = []

    def json_serialise(self):
        ret = {
            'name': self.name,
            'duration_seconds': self.duration_seconds,
            'workout_section_type': self.workout_section_type,
            'difficulty': self.difficulty,
            'intensity_pace': self.intensity_pace,
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
        workout_section.exercises = [WorkoutExercise.json_deserialise(workout_exercise) for workout_exercise
                                                   in input_dict.get('exercises', [])]

        return workout_section


class WorkoutExercise(Serialisable):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.weight_in_lbs = None
        self.weight_type = None
        self.sets = 1
        self.reps_per_set = 1
        self.unit_of_measure = None
        self.intensity_pace = None
        self.adaptation_type = None
        self.body_position = None
        self.movement_action = None
        self.training_type = None
        self.explosive = 0

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'weight_in_lbs': self.weight_in_lbs,
            'weight_type': self.weight_type,
            'sets': self.sets,
            'reps_per_set': self.reps_per_set,
            'unit_of_measure': self.unit_of_measure.value,
            'intensity_pace': self.intensity_pace,
            'adaptation_type': self.adaptation_type.value if self.adaptation_type is not None else None,
            'body_position': self.body_position.value if self.body_position is not None else None,
            'movement_action': self.movement_action.value if self.movement_action is not None else None,
            'training_type': self.training_type.value if self.training_type is not None else None,
            'explosive': self.explosive
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        exercise = cls()
        exercise.id = input_dict.get('id', '')
        exercise.name = input_dict.get('name', '')
        exercise.weight_in_lbs = input_dict.get('weight_in_lbs')
        exercise.weight_type = input_dict.get('weight_type')
        exercise.sets = input_dict.get('sets', 0)
        exercise.reps_per_set = input_dict.get('reps_per_set', 0)
        exercise.unit_of_measure = UnitOfMeasure(input_dict['unit_of_measure']) if input_dict.get('unit_of_measure') is not None else None
        exercise.intensity_pace = input_dict.get('intensity_pace')
        exercise.adaptation_type = AdaptationType(input_dict['adaptation_type']) if input_dict.get(
            'adaptation_type') is not None else None
        exercise.explosive = input_dict.get('explosive', False)

        # not yet sure if these are needed
        exercise.body_position = BodyPosition(input_dict['body_position']) if input_dict.get(
            'body_position') is not None else None
        exercise.movement_action = MovementAction(input_dict['movement_action']) if input_dict.get(
            'movement_action') is not None else None
        exercise.training_type = TrainingType(input_dict['training_type']) if input_dict.get(
            'training_type') is not None else None

        return exercise

    def get_training_volume(self):

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

    def process_movement(self, movement):

        self.set_adaption_type(movement)

    def set_adaption_type(self, movement):

        if movement.training_type == TrainingType.flexibility:
            self.adaptation_type = AdaptationType.not_tracked
        elif movement.training_type == TrainingType.cardiorespiratory:
            self.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
        elif movement.training_type == TrainingType.core:
            self.adaptation_type = AdaptationType.strength_endurance_strength
        elif movement.training_type == TrainingType.balance:
            self.adaptation_type = AdaptationType.strength_endurance_strength
        elif movement.training_type == TrainingType.plyometrics:
            self.adaptation_type = AdaptationType.power_explosive_action
        elif movement.training_type == TrainingType.plyometrics_drills:
            self.adaptation_type = AdaptationType.power_drill
        elif movement.training_type == TrainingType.speed_agility_quickness:
            self.adaptation_type = AdaptationType.power_drill
        elif movement.training_type == TrainingType.integrated_resistance:
            if self.intensity_pace >= 75:
                self.adaptation_type = AdaptationType.maximal_strength_hypertrophic
            else:
                self.adaptation_type = AdaptationType.strength_endurance_strength
        elif movement.training_type == TrainingType.olympic_lifting:
            if movement.explosive < 2:
                self.adaptation_type = AdaptationType.maximal_strength_hypertrophic
            else:
                self.adaptation_type = AdaptationType.power_explosive_action


class Movement(Serialisable):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.adaptation_type = None
        self.body_position = None
        self.movement_action = None
        self.training_type = None
        self.equipment = None
        self.explosive = 0

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'body_position': self.body_position.value if self.body_position is not None else None,
            'movement_action': self.movement_action.value if self.movement_action is not None else None,
            'training_type': self.training_type.value if self.training_type is not None else None,
            'equipment': self.equipment.value if self.equipment is not None else None,
            'explosive': self.explosive
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        movement = cls(input_dict.get('id'), input_dict.get('name'))

        movement.body_position = BodyPosition(input_dict['body_position']) if input_dict.get(
            'body_position') is not None else None
        movement.movement_action = MovementAction(input_dict['movement_action']) if input_dict.get(
            'movement_action') is not None else None
        movement.training_type = TrainingType(input_dict['training_type']) if input_dict.get('training_type') is not None else None
        movement.equipment = Equipment(input_dict['equipment']) if input_dict.get('equipment') is not None else None
        movement.explosive = input_dict.get('explosive', 0)

        return movement
