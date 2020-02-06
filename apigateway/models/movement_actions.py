from enum import Enum
from models.movement_tags import BodyPosition, CardioAction, TrainingType, Equipment, WeightDistribution
from serialisable import Serialisable


class MuscleAction(Enum):
    concentric = 0
    eccentric = 1
    isometric = 2


class ExerciseAction(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.sets = 1
        self.reps_per_set = 1
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


        self.external_weight = {}  # in % body weight. # comes from exercise


    def distribute_weight(self):
        total_weight_0 = 0
        total_weight_1 = 0
        if self.apply_resistance:
            for equipment, weight in self.external_weight.items():
                if equipment in self.eligible_external_resistance:
                    if equipement.distribute:
                        total_weight_0 += weight / 2
                        total_weight_1 += weight / 2
                    else:
                        total_weight_0 += weight
                        total_weight_1 += weight

        if self.bilateral_distribution_of_weight == WeightDistribution.bilateral:
            total_weight_0 += self.percent_body_weight[0] / 2
            total_weight_1 += self.percent_body_weight[0] / 2
        elif self.bilateral_distribution_of_weight == WeightDistribution.bilateral_uneven:
            total_weight_0 += self.percent_body_weight[0]
            total_weight_1 += self.percent_body_weight[1]
        elif self.bilateral_distribution_of_weight == WeightDistribution.unilateral:
            total_weight_0 += self.percent_body_weight[0] / 2
            total_weight_1 += self.percent_body_weight[0] / 2
        elif self.bilateral_distribution_of_weight == WeightDistribution.unilateral_alternating:
            total_weight_0 += self.percent_body_weight[0] / 2
            total_weight_1 += self.percent_body_weight[0] / 2


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