from enum import Enum
from models.movement_tags import BodyPosition, CardioAction, TrainingType, Equipment, WeightDistribution, AdaptationType
from serialisable import Serialisable


class MuscleAction(Enum):
    concentric = 0
    eccentric = 1
    isometric = 2


class ExerciseAction(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.rpe = None
        self.sets = 1
        self.reps = 1
        self.side = 0  # both
        self.training_type = None
        self.adaptation_type = None
        self.body_position = None
        self.body_weight = 0.0
        self.apply_resistance = False
        self.explosiveness = None
        self.muscle_action = None
        self.bilateral_distribution_of_weight = WeightDistribution.bilateral
        self.eligible_external_resistance = []
        self.percent_body_weight = []
        self.hip_joint_action = None
        self.knee_joint_action = None
        self.ankle_joint_action = None
        self.trunk_joint_action = None
        self.shoulder_scapula_joint_action = None
        self.elbow_joint_action = None
        self.total_load_left = 0
        self.total_load_right = 0
        self.external_intensity_left = 0
        self.external_intensity_right = 0
        self.bodyweight_intensity_left = 0
        self.bodyweight_intensity_right = 0
        self.training_volume_left = 0
        self.training_volume_right = 0

        self.external_weight = []  # list of ExternalWeight objects, weight is in %bodyweight

    def get_external_intensity(self):
        external_weight_left = 0
        external_weight_right = 0
        if self.apply_resistance:
            for ex_weight in self.external_weight:
                left = 0
                right = 0
                if ex_weight.equipment in self.eligible_external_resistance:
                    if ex_weight.distribute_weight:  # e.g barbell weight is supposed to be total weight
                        if self.bilateral_distribution_of_weight == WeightDistribution.bilateral:  # each side gets half the load for each rep
                            left = ex_weight.value / 2
                            right = ex_weight.value / 2
                        elif self.bilateral_distribution_of_weight == WeightDistribution.bilateral_uneven:  # first item in percent body weight is the dominant side
                            if self.side == 1:  # left dominant activity
                                if self.percent_body_weight[0] != 0:  # dominant action
                                    left = ex_weight.value / 2
                                else:  # non-dominant action
                                    right = ex_weight.value / 2
                            elif self.side == 2:  # right dominant activity
                                if self.percent_body_weight[0] != 0:  # dominant action
                                    right = ex_weight.value / 2
                                else:  # non-dominant action
                                    left = ex_weight.value / 2
                            else:
                                left = ex_weight.value / 4
                                right = ex_weight.value / 4
                        elif self.bilateral_distribution_of_weight == WeightDistribution.unilateral:
                            if self.side == 1:  # performed left only
                                left = ex_weight.value
                            elif self.side == 2:  # performed right only
                                right = ex_weight.value
                            else:  # assuming assignment is per side, assign all of the intensity to each side
                                left = ex_weight.value
                                right = ex_weight.value
                        elif self.bilateral_distribution_of_weight == WeightDistribution.unilateral_alternating:  # each side gets all the intensity for each rep
                            left = ex_weight.value
                            right = ex_weight.value

                    else:  # dumbbell, weight is supposed to be weight for each side
                        if self.bilateral_distribution_of_weight == WeightDistribution.unilateral:
                            if self.side == 1:  # performed left only
                                left = ex_weight.value
                            elif self.side == 2:  # performed right only
                                right = ex_weight.value
                            else:  #   # assuming assignment is per side, assign all of the intensity to each side
                                left = ex_weight.value
                                right = ex_weight.value
                        elif self.bilateral_distribution_of_weight == WeightDistribution.bilateral_uneven:  # first item in percent body weight is the dominant side
                            if self.side == 1:  # left dominant activity
                                if self.percent_body_weight[0] != 0:  # dominant action
                                    left = ex_weight.value
                                else:  # non-dominant action
                                    right = ex_weight.value
                            elif self.side == 2:  # right dominant activity
                                if self.percent_body_weight[0] != 0:  # dominant action
                                    right = ex_weight.value
                                else:  # non-dominant action
                                    left = ex_weight.value
                            else:
                                left = ex_weight.value / 2
                                right = ex_weight.value / 2
                        else:  # bilateral and unilateral alternating get full amount for each side
                            left = ex_weight.value
                            right = ex_weight.value
                    external_weight_left += left
                    external_weight_right += right
        self.external_intensity_left = external_weight_left
        self.external_intensity_right = external_weight_right

    def get_body_weight_intensity(self):
        if len(self.percent_body_weight) == 1:
            bilateral_body_weight = [self.percent_body_weight[0], self.percent_body_weight[0]]
        else:
            bilateral_body_weight = self.percent_body_weight
        self.bodyweight_intensity_left, self.bodyweight_intensity_right = self.distribute_bilateral_weights(bilateral_body_weight)

    def distribute_bilateral_weights(self, bilateral_weights):
        left = 0
        right = 0
        if self.bilateral_distribution_of_weight == WeightDistribution.bilateral:  # each side gets half the load for each rep
            left = bilateral_weights[0] / 2
            right = bilateral_weights[1] / 2
        elif self.bilateral_distribution_of_weight == WeightDistribution.bilateral_uneven:  # first item in percent body weight is the dominant side
            if self.side == 1:
                left = bilateral_weights[0]
                right = bilateral_weights[1]
            elif self.side == 2:
                left = bilateral_weights[1]
                right = bilateral_weights[0]
            else:
                left = sum(bilateral_weights) / 2
                right = sum(bilateral_weights) / 2
        elif self.bilateral_distribution_of_weight == WeightDistribution.unilateral:
            if self.side == 1:  # performed left only
                left = bilateral_weights[0]
            elif self.side == 2:  # performed right only
                right = bilateral_weights[0]
            else:  # assuming assignment is per side, assign all of the intensity to each side
                left = bilateral_weights[0]
                right = bilateral_weights[0]
        elif self.bilateral_distribution_of_weight == WeightDistribution.unilateral_alternating:  # each side gets all the intensity for each rep
            left = bilateral_weights[0]
            right = bilateral_weights[0]
        return left, right

    def get_training_load(self):
        self.get_training_intensity()
        self.set_adaption_type()
        self.get_training_volume()
        if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            # both sides have same volume (duration) and intensity (rpe)
            if self.rpe is None:
                self.rpe = 4
            self.total_load_left = self.training_volume_left * self.rpe
            self.total_load_right = self.training_volume_right * self.rpe
        else:
            # TODO: Currently only capturing external load. update based on decision of what to do with body_weight + external_weight.
            self.total_load_left = self.training_volume_left * self.external_intensity_left
            self.total_load_right = self.training_volume_right * self.external_intensity_right

    def get_training_volume(self):
        if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            # both sides are assigned all the reps (duration)
            self.training_volume_left = self.reps
            self.training_volume_right = self.reps
        else:
            if self.bilateral_distribution_of_weight == WeightDistribution.unilateral:
                if self.side == 1:
                    self.training_volume_left = self.reps
                elif self.side == 2:
                    self.training_volume_right = self.reps
                else:
                    self.training_volume_left = self.reps
                    self.training_volume_right = self.reps
            elif self.bilateral_distribution_of_weight == WeightDistribution.bilateral_uneven:
                if self.side == 1:
                    if self.percent_body_weight[0] != 0:
                        self.training_volume_left = self.reps
                    else:
                        self.training_volume_right = self.reps
                elif self.side == 2:
                    if self.percent_body_weight[0] != 0:
                        self.training_volume_right = self.reps
                    else:
                        self.training_volume_left = self.reps
                else:
                    self.training_volume_left = self.reps
                    self.training_volume_right = self.reps
            else:
                self.training_volume_left = self.reps
                self.training_volume_right = self.reps

    def get_training_intensity(self):
        self.get_external_intensity()
        self.get_body_weight_intensity()

    def set_adaption_type(self):
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
            if max([self.external_intensity_left, self.external_intensity_right]) >= 100:
                self.adaptation_type = AdaptationType.maximal_strength_hypertrophic
            else:
                self.adaptation_type = AdaptationType.strength_endurance_strength


class PrioritizedJointAction(object):
    def __init__(self):
        self.priority = 0
        self.joint_action = None


class ExerciseCompoundAction(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.actions = []


class Movement(Serialisable):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.body_position = None
        self.cardio_action = None
        self.training_type = None
        self.equipment = None
        self.explosive = 0
        self.primary_actions = []
        self.secondary_actions = []

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'body_position': self.body_position.value if self.body_position is not None else None,
            'cardio_action': self.cardio_action.value if self.cardio_action is not None else None,
            'training_type': self.training_type.value if self.training_type is not None else None,
            'equipment': self.equipment.value if self.equipment is not None else None,
            'explosive': self.explosive,
            'primary_actions': self.primary_actions,
            'secondary_actions': self.secondary_actions
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        movement = cls(input_dict.get('id'), input_dict.get('name'))

        movement.body_position = BodyPosition(input_dict['body_position']) if input_dict.get(
            'body_position') is not None else None
        movement.cardio_action = CardioAction(input_dict['cardio_action']) if input_dict.get(
            'cardio_action') is not None else None
        movement.training_type = TrainingType(input_dict['training_type']) if input_dict.get('training_type') is not None else None
        movement.equipment = Equipment(input_dict['equipment']) if input_dict.get('equipment') is not None else None
        movement.explosive = input_dict.get('explosive', 0)
        movement.primary_actions = input_dict.get('primary_actions', [])
        movement.secondary_actions = input_dict.get('secondary_actions', [])

        return movement


class ExternalWeight(object):
    def __init__(self, equipment, value):
        self.equipment = equipment
        self.value = value
        self.distribute_weight = self.equipment.distribute_weights()
