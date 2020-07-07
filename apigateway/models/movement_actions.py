from enum import Enum, IntEnum
from models.movement_tags import BodyPosition, CardioAction, TrainingType, Equipment, WeightDistribution,\
    AdaptationType, MovementSurfaceStability, PowerAction, PowerDrillAction, StrengthResistanceAction, StrengthEnduranceAction
from models.functional_movement_type import FunctionalMovementType
from models.training_volume import StandardErrorRange, Assignment
from logic.calculators import Calculators
from serialisable import Serialisable

class MuscleAction(Enum):
    concentric = 0
    eccentric = 1
    isometric = 2


class LowerBodyStance(Enum):
    double_leg = 0
    staggered_leg = 1
    split_leg = 2
    single_leg = 3
    supine = 4
    prone = 5
    side_lying = 6
    quadruped = 7
    bridge = 8
    kneeling = 9
    half_kneeling = 10
    seated = 11
    contralateral_single_leg = 12
    alternating_single_leg = 13
    contralateral_alternating_single_leg = 14


class UpperBodyStance(Enum):
    double_arm = 0
    alternating_arms = 1
    single_arm = 2
    single_arm_with_trunk_rotation = 3
    contralateral_single_arm = 4
    contralateral_alternating_single_arm = 5


class ExerciseAction(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

        # defined per action
        self.training_type = None
        self.eligible_external_resistance = []
        self.lower_body_stance = None
        self.upper_body_stance = None
        self.body_position = None
        self.lateral_distribution_pattern = WeightDistribution.bilateral
        self.percent_bodyweight = 0.0
        self.lateral_distribution = [0, 0]
        self.apply_resistance = False
        self.explosiveness = None
        self.apply_instability = False
        self.speed = None
        self.resistance = None

        self.primary_muscle_action = None
        self.hip_joint_action = []
        self.knee_joint_action = []
        self.ankle_joint_action = []
        self.pelvic_tilt_joint_action = []
        self.trunk_joint_action = []
        self.shoulder_scapula_joint_action = []
        self.elbow_joint_action = []
        self.wrist_joint_action = []

        # self.ancillary_muscle_action = None
        # self.hip_stability_action = []
        # self.ankle_stability_action = []
        # self.trunk_stability_action = []
        # self.pelvis_stability_action = []
        # self.shoulder_stability_action = []
        # self.elbow_stability_action = []
        # self.sij_stability_action = []

        # obtained from exercise
        self.rpe = None
        self.shrz = None
        self.cardio_action = None
        #self.reps = 1
        self.external_weight = []  # list of ExternalWeight objects
        self.bilateral = True
        self.side = 0  # both
        # new variables for tissue intensity
        self.duration = None  # seconds
        self.distance = None  # meters
        self.pace = None  # in seconds/meter
        self.speed = None  # meters/second
        self.power = None  # watts
        self.force = None  # newtons
        self.grade = None  # percentage (decimal)
        self.rep_tempo = None
        self.force = None

        # derived
        self.adaptation_type = None
        self.lower_body_stability_rating = 0
        self.upper_body_stability_rating = 0
        self.explosiveness_rating = 0
        self.total_load_left = StandardErrorRange(observed_value=0)
        self.total_load_right = StandardErrorRange(observed_value=0)
        self.tissue_load_left = StandardErrorRange(observed_value=0)
        self.tissue_load_right = StandardErrorRange(observed_value=0)
        self.force_load_left = StandardErrorRange(observed_value=0)
        self.force_load_right = StandardErrorRange(observed_value=0)
        self.power_load_left = StandardErrorRange(observed_value=0)
        self.power_load_right = StandardErrorRange(observed_value=0)
        # TODO: Remove these once strength-level intensity is implemented
        self.external_weight_left = 0
        self.external_weight_right = 0
        self.body_weight_left = 0
        self.body_weight_right = 0
        self.tissue_intensity = 0
        self.readiness = 1
        self.training_intensity = 0
        self.training_intensity_left = 0
        self.training_intensity_right = 0
        self.training_volume_left = 0
        self.training_volume_right = 0

    def json_serialise(self, initial_read=False):
        ret = {
            "id": self.id,
            "name": self.name,
            "training_type": self.training_type.value if self.training_type is not None else None,
            "eligible_external_resistance": [res.value for res in self.eligible_external_resistance],
            "body_position": self.body_position.value if self.body_position is not None else None,
            "lower_body_stance": self.lower_body_stance.value if self.lower_body_stance is not None else None,
            "upper_body_stance": self.upper_body_stance.value if self.upper_body_stance is not None else None,
            "lateral_distribution_pattern": self.lateral_distribution_pattern.value,
            "percent_bodyweight": self.percent_bodyweight,
            "lateral_distribution": self.lateral_distribution,
            "apply_resistance": self.apply_resistance,
            "explosiveness": self.explosiveness.value if self.explosiveness is not None else None,
            "apply_instability": self.apply_instability,
            'speed': self.speed.value if self.speed is not None else None,
            'resistance': self.resistance.value if self.resistance is not None else None,

            "primary_muscle_action": self.primary_muscle_action.value if self.primary_muscle_action is not None else None,
            "hip_joint_action": [ac.json_serialise() for ac in self.hip_joint_action],
            "knee_joint_action": [ac.json_serialise() for ac in self.knee_joint_action],
            "ankle_joint_action": [ac.json_serialise() for ac in self.ankle_joint_action],
            "pelvic_tilt_joint_action": [ac.json_serialise() for ac in self.pelvic_tilt_joint_action],
            "trunk_joint_action": [ac.json_serialise() for ac in self.trunk_joint_action],
            "shoulder_scapula_joint_action": [ac.json_serialise() for ac in self.shoulder_scapula_joint_action],
            "elbow_joint_action": [ac.json_serialise() for ac in self.elbow_joint_action],
            "wrist_joint_action": [ac.json_serialise() for ac in self.wrist_joint_action],

            # "ancillary_muscle_action": self.ancillary_muscle_action,
            # "hip_stability_action": self.hip_stability_action,
            # "ankle_stability_action": self.ankle_stability_action,
            # "trunk_stability_action": self.trunk_stability_action,
            # "pelvis_stability_action": self.pelvis_stability_action,
            # "shoulder_stability_action": self.shoulder_stability_action,
            # "elbow_stability_action": self.elbow_stability_action,
            # "sij_stability_action": self.sij_stability_action,
        }
        if not initial_read:
            additional_params = {
                # obtained from exercises
                "rpe": self.rpe,
                "shrz": self.shrz,
                "pace": self.pace,
                "rep_tempo": self.rep_tempo,
                "cardio_action": self.cardio_action.value if self.cardio_action is not None else None,
                #"reps": self.reps,
                "side": self.side,
                "external_weight": [ex_weight.json_serialise() for ex_weight in self.external_weight],
                "bilateral": self.bilateral,

                # derived/calculated
                "adaptation_type": self.adaptation_type.value if self.adaptation_type is not None else None,
                "total_load_left": self.total_load_left,
                "total_load_right": self.total_load_right,
                "tissue_load_left": self.tissue_load_left.json_serialise(),
                "tissue_load_right": self.tissue_load_right.json_serialise(),
                "force_load_left": self.force_load_left.json_serialise(),
                "force_load_right": self.force_load_right.json_serialise(),
                "power_load_left": self.power_load_left.json_serialise(),
                "power_load_right": self.power_load_right.json_serialise(),
                # "external_weight_left": self.external_weight_left,
                # "external_weight_right": self.external_weight_right,
                # "body_weight_left": self.body_weight_left,
                # "body_weight_right": self.body_weight_right,
                "training_intensity": self.training_intensity,
                "training_intensity_left": self.training_intensity_left,
                "training_intensity_right": self.training_intensity_right,
                "training_volume_left": self.training_volume_left,
                "training_volume_right": self.training_volume_right
                }
            ret.update(additional_params)
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        action = cls(input_dict.get('id'), input_dict.get('name'))

        # defined per action
        action.training_type = TrainingType(input_dict['training_type']) if input_dict.get('training_type') is not None else None
        action.eligible_external_resistance = [Equipment(equip) for equip in input_dict.get('eligible_external_resistance', [])]
        action.body_position = BodyPosition(input_dict['body_position']) if input_dict.get('body_position') is not None else None
        action.lower_body_stance = LowerBodyStance(input_dict['lower_body_stance']) if input_dict.get('lower_body_stance') is not None else None
        action.upper_body_stance = UpperBodyStance(input_dict['upper_body_stance']) if input_dict.get('upper_body_stance') is not None else None
        action.lateral_distribution_pattern = WeightDistribution(input_dict['lateral_distribution_pattern']) if input_dict.get('lateral_distribution_pattern') is not None else WeightDistribution.bilateral
        action.percent_bodyweight = input_dict.get('percent_bodyweight', 0.0)
        action.lateral_distribution = input_dict.get('lateral_distribution', [0, 0])
        action.apply_resistance = input_dict.get('apply_resistance', False)
        action.explosiveness = Explosiveness(input_dict['explosiveness']) if input_dict.get('explosiveness') is not None else None
        action.apply_instability = input_dict.get('apply_instability', False)

        action.primary_muscle_action = MuscleAction(input_dict['primary_muscle_action']) if input_dict.get('primary_muscle_action') is not None else None
        action.hip_joint_rating = None
        action.hip_joint_action = [PrioritizedJointAction.json_deserialise(joint_action) for joint_action in input_dict.get('hip_joint_action', [])]
        action.knee_joint_action = [PrioritizedJointAction.json_deserialise(joint_action) for joint_action in input_dict.get('knee_joint_action', [])]
        action.ankle_joint_action = [PrioritizedJointAction.json_deserialise(joint_action) for joint_action in input_dict.get('ankle_joint_action', [])]
        action.pelvic_tilt_joint_action = [PrioritizedJointAction.json_deserialise(joint_action) for joint_action in input_dict.get('pelvic_tilt_joint_action', [])]
        action.trunk_joint_action = [PrioritizedJointAction.json_deserialise(joint_action) for joint_action in input_dict.get('trunk_joint_action', [])]
        action.shoulder_scapula_joint_action = [PrioritizedJointAction.json_deserialise(joint_action) for joint_action in input_dict.get('shoulder_scapula_joint_action', [])]
        action.elbow_joint_action = [PrioritizedJointAction.json_deserialise(joint_action) for joint_action in input_dict.get('elbow_joint_action', [])]
        action.wrist_joint_action = [PrioritizedJointAction.json_deserialise(joint_action) for joint_action in input_dict.get('wrist_joint_action', [])]

        # action.ancillary_muscle_action = MuscleAction(input_dict['ancillary_muscle_action']) if input_dict.get('ancillary_muscle_action') is not None else None
        # action.hip_stability_action = []
        # action.ankle_stability_action = []
        # action.trunk_stability_action = []
        # action.pelvis_stability_action = []
        # action.shoulder_stability_action = []
        # action.elbow_stability_action = []
        # action.sij_stability_action = []

        # obtained from exercise
        action.rpe = input_dict.get('rpe')
        action.pace = input_dict.get('pace')
        action.rep_tempo = input_dict.get('rep_tempo')
        action.cardio_action = CardioAction(input_dict.get('cardio_action')) if input_dict.get('cardio_action') is not None else None
        #action.reps = input_dict.get('reps', 1)
        action.side = input_dict.get('side', 0)  # both
        action.external_weight = [ExternalWeight.json_deserialise(ex_weight) for ex_weight in input_dict.get('external_weight', [])]  # list of ExternalWeight objects
        action.bilateral = input_dict.get('bilateral', True)

        # derived
        action.adaptation_type = AdaptationType(input_dict['adaptation_type']) if input_dict.get('adaptation_type') is not None else None
        action.lower_body_stability_rating = input_dict.get('lower_body_stability_rating', 0)
        action.upper_body_stability_rating = input_dict.get('upper_body_stability_rating', 0)
        action.explosiveness_rating = input_dict.get('explosiveness_rating', 0)
        action.total_load_left = input_dict.get('total_load_left', 0)
        action.total_load_right = input_dict.get('total_load_right', 0)
        action.tissue_load_left = StandardErrorRange.json_deserialise(input_dict.get('tissue_load_left')) if input_dict.get('tissue_load_left') is not None else StandardErrorRange()
        action.tissue_load_right = StandardErrorRange.json_deserialise(input_dict.get('tissue_load_right')) if input_dict.get('tissue_load_right') is not None else StandardErrorRange()
        action.power_load_left = StandardErrorRange.json_deserialise(input_dict.get('power_load_left')) if input_dict.get('power_load_left') is not None else StandardErrorRange()
        action.power_load_right = StandardErrorRange.json_deserialise(input_dict.get('power_load_right')) if input_dict.get('power_load_right') is not None else StandardErrorRange()
        action.force_load_left = StandardErrorRange.json_deserialise( input_dict.get('force_load_left')) if input_dict.get('force_load_left') is not None else StandardErrorRange()
        action.force_load_right = StandardErrorRange.json_deserialise( input_dict.get('force_load_right')) if input_dict.get('force_load_right') is not None else StandardErrorRange()
        # action.external_weight_left = input_dict.get('external_weight_left', 0)
        # action.external_weight_right = input_dict.get('external_weight_right', 0)
        # action.body_weight_left = input_dict.get('body_weight_left', 0)
        # action.body_weight_right = input_dict.get('body_weight_right', 0)
        action.training_intensity = input_dict.get('training_intensity', 0)
        action.training_intensity_left = input_dict.get('training_intensity_left', 0)
        action.training_intensity_right = input_dict.get('training_intensity_right', 0)
        action.training_volume_left = input_dict.get('training_volume_left', 0)
        action.training_volume_right = input_dict.get('training_volume_right', 0)

        return action

    # def set_cardio_tissue_intensity(self):
    #     if self.cardio_action == CardioAction.row:
    #         if self.pace is not None:
    #             force = 2.8 / (self.pace ** 2)
    #             self.tissue_intensity = force * self.rep_tempo
    #     elif self.cardio_action == CardioAction.cycle:
    #         if self.power is not None and self.speed is not None:
    #             force = self.power / self.speed
    #             self.tissue_intensity = force * self.rep_tempo
    #     elif self.cardio_action == CardioAction.run:
    #         if self.power is not None and self.speed is not None:
    #             force = self.power / self.speed
    #             self.tissue_intensity = force * self.rep_tempo

    def set_external_weight_distribution(self):
        external_weight_left = 0
        external_weight_right = 0
        if self.apply_resistance:
            for ex_weight in self.external_weight:
                left = 0
                right = 0
                if ex_weight.equipment in self.eligible_external_resistance:
                    if ex_weight.distribute_weight:  # e.g barbell weight is supposed to be total weight
                        if self.lateral_distribution_pattern == WeightDistribution.bilateral:  # each side gets half the load for each rep
                            left = ex_weight.value * self.lateral_distribution[0] / 100
                            right = ex_weight.value * self.lateral_distribution[0] / 100
                        elif self.lateral_distribution_pattern == WeightDistribution.bilateral_uneven:  # first item in percent body weight is the dominant side
                            if self.side == 1:  # left dominant activity
                                left = ex_weight.value * self.lateral_distribution[0] / 100
                                right = ex_weight.value * self.lateral_distribution[1] / 100
                            elif self.side == 2:  # right dominant activity
                                left = ex_weight.value * self.lateral_distribution[1] / 100
                                right = ex_weight.value * self.lateral_distribution[0] / 100
                            else:  # since we don't know which side was loaded more, apply evenly
                                left = ex_weight.value * sum(self.lateral_distribution) / 2 / 100
                                right = ex_weight.value * sum(self.lateral_distribution) / 2 / 100
                        elif self.lateral_distribution_pattern == WeightDistribution.unilateral:
                            if self.side == 1:  # performed left only
                                left = ex_weight.value * self.lateral_distribution[0] / 100
                                right = ex_weight.value * self.lateral_distribution[1] / 100
                            elif self.side == 2:  # performed right only
                                left = ex_weight.value * self.lateral_distribution[1] / 100
                                right = ex_weight.value * self.lateral_distribution[0] / 100
                            else:  # assuming assignment is per side, assign all of the intensity to each side
                                left = ex_weight.value * self.lateral_distribution[0] / 100
                                right = ex_weight.value * self.lateral_distribution[0] / 100
                        elif self.lateral_distribution_pattern == WeightDistribution.unilateral_alternating:  # each side gets all the intensity for each rep
                            left = ex_weight.value * self.lateral_distribution[0] / 100
                            right = ex_weight.value * self.lateral_distribution[1] / 100

                    else:  # dumbbell, weight is supposed to be weight for each side
                        if self.lateral_distribution_pattern == WeightDistribution.unilateral:
                            if self.side == 1:  # performed left only
                                left = ex_weight.value * self.lateral_distribution[0] / 100
                            elif self.side == 2:  # performed right only
                                right = ex_weight.value * self.lateral_distribution[0] / 100
                            else:  # assuming assignment is per side, assign all of the intensity to each side
                                left = ex_weight.value * self.lateral_distribution[0] / 100
                                right = ex_weight.value * self.lateral_distribution[0] / 100
                        elif self.lateral_distribution_pattern == WeightDistribution.bilateral_uneven:  # first item in percent body weight is the dominant side
                            if self.side == 1:  # left dominant activity
                                left = ex_weight.value * 2 * self.lateral_distribution[0] / 100
                                right = ex_weight.value * 2 * self.lateral_distribution[1] / 100
                            elif self.side == 2:  # right dominant activity
                                left = ex_weight.value * 2 * self.lateral_distribution[1] / 100
                                right = ex_weight.value * 2 * self.lateral_distribution[0] / 100
                            else:  # since we don't know which side was loaded more, apply evenly
                                left = ex_weight.value * 2 * sum(self.lateral_distribution) / 2 / 100
                                right = ex_weight.value * 2 * sum(self.lateral_distribution) / 2 / 100
                        elif self.lateral_distribution_pattern == WeightDistribution.unilateral_alternating:  # bilateral and unilateral alternating get full amount for each side
                            left = ex_weight.value * self.lateral_distribution[0] / 100
                            right = ex_weight.value * self.lateral_distribution[1] / 100
                        else:  # both side get reported value
                            left = ex_weight.value * 2 * self.lateral_distribution[0] / 100
                            right = ex_weight.value * 2 * self.lateral_distribution[1] / 100

                    external_weight_left += left
                    external_weight_right += right
        self.external_weight_left = external_weight_left
        self.external_weight_right = external_weight_right

    def set_left_right_distribution(self, attribute_name):
        left = StandardErrorRange(observed_value=0)
        right = StandardErrorRange(observed_value=0)

        object_value = getattr(self, attribute_name)

        if len(self.external_weight) == 0:
            if object_value is None:
                left = StandardErrorRange(observed_value=0)
                right = StandardErrorRange(observed_value=0)
            else:
                left = object_value.plagiarize()
                right = object_value.plagiarize()
        else:
            ex_weight = self.external_weight[0]
            left = object_value.plagiarize()
            right = object_value.plagiarize()
            if ex_weight.distribute_weight:  # e.g barbell weight is supposed to be total weight
                if self.lateral_distribution_pattern == WeightDistribution.bilateral:  # each side gets half the load for each rep
                    left.multiply(self.lateral_distribution[0] / 100)
                    right.multiply(self.lateral_distribution[0] / 100)
                elif self.lateral_distribution_pattern == WeightDistribution.bilateral_uneven:  # first item in percent body weight is the dominant side
                    if self.side == 1:  # left dominant activity
                        left.multiply(self.lateral_distribution[0] / 100)
                        right.multiply(self.lateral_distribution[1] / 100)
                    elif self.side == 2:  # right dominant activity
                        left.multiply(self.lateral_distribution[1] / 100)
                        right.multiply(self.lateral_distribution[0] / 100)
                    else:  # since we don't know which side was loaded more, apply evenly
                        left.multiply(sum(self.lateral_distribution) / 2 / 100)
                        right.multiply(sum(self.lateral_distribution) / 2 / 100)
                elif self.lateral_distribution_pattern == WeightDistribution.unilateral:
                    if self.side == 1:  # performed left only
                        left.multiply(self.lateral_distribution[0] / 100)
                        right.multiply(self.lateral_distribution[1] / 100)
                    elif self.side == 2:  # performed right only
                        left.multiply(self.lateral_distribution[1] / 100)
                        right.multiply(self.lateral_distribution[0] / 100)
                    else:  # assuming assignment is per side, assign all of the intensity to each side
                        left.multiply(self.lateral_distribution[0] / 100)
                        right.multiply(self.lateral_distribution[0] / 100)
                elif self.lateral_distribution_pattern == WeightDistribution.unilateral_alternating:  # each side gets all the intensity for each rep
                    left.multiply(self.lateral_distribution[0] / 100)
                    right.multiply(self.lateral_distribution[1] / 100)

            else:  # dumbbell, weight is supposed to be weight for each side
                if self.lateral_distribution_pattern == WeightDistribution.unilateral:
                    if self.side == 1:  # performed left only
                        left.multiply(self.lateral_distribution[0] / 100)
                    elif self.side == 2:  # performed right only
                        right.multiply(self.lateral_distribution[0] / 100)
                    else:  # assuming assignment is per side, assign all of the intensity to each side
                        left.multiply(self.lateral_distribution[0] / 100)
                        right.multiply(self.lateral_distribution[0] / 100)
                elif self.lateral_distribution_pattern == WeightDistribution.bilateral_uneven:  # first item in percent body weight is the dominant side
                    if self.side == 1:  # left dominant activity
                        left.multiply(2 * self.lateral_distribution[0] / 100)
                        right.multiply(2 * self.lateral_distribution[1] / 100)
                    elif self.side == 2:  # right dominant activity
                        left.multiply(2 * self.lateral_distribution[1] / 100)
                        right.multiply(2 * self.lateral_distribution[0] / 100)
                    else:  # since we don't know which side was loaded more, apply evenly
                        left.multiply(2 * sum(self.lateral_distribution) / 2 / 100)
                        right.multiply(2 * sum(self.lateral_distribution) / 2 / 100)
                elif self.lateral_distribution_pattern == WeightDistribution.unilateral_alternating:  # bilateral and unilateral alternating get full amount for each side
                    left.multiply(self.lateral_distribution[0] / 100)
                    right.multiply(self.lateral_distribution[1] / 100)
                else:  # both side get reported value
                    left.multiply(2 * self.lateral_distribution[0] / 100)
                    right.multiply(2 * self.lateral_distribution[1] / 100)
        return left, right

    def set_body_weight_distribution(self):
        left = 0
        right = 0
        if self.lateral_distribution_pattern == WeightDistribution.bilateral:  # each side gets half the load for each rep (50, 50)
            left = self.percent_bodyweight * self.lateral_distribution[0] / 100
            right = self.percent_bodyweight * self.lateral_distribution[1] / 100
        elif self.lateral_distribution_pattern == WeightDistribution.bilateral_uneven:  # first item in percent body weight is the dominant side (x, y)
            if self.side == 1:
                left = self.percent_bodyweight * self.lateral_distribution[0] / 100
                right = self.percent_bodyweight * self.lateral_distribution[1] / 100
            elif self.side == 2:
                left = self.percent_bodyweight * self.lateral_distribution[1] / 100
                right = self.percent_bodyweight * self.lateral_distribution[0] / 100
            else:  # since we don't know which side was loaded more, apply evenly
                left = self.percent_bodyweight * (sum(self.lateral_distribution) / 2) / 100
                right = self.percent_bodyweight * (sum(self.lateral_distribution) / 2) / 100
        elif self.lateral_distribution_pattern == WeightDistribution.unilateral:  # (100, 0)
            if self.side == 1:  # performed left only
                left = self.percent_bodyweight * self.lateral_distribution[0] / 100
            elif self.side == 2:  # performed right only
                right = self.percent_bodyweight * self.lateral_distribution[0] / 100
            else:  # assuming assignment is per side, assign all of the intensity to each side (same as unilateral_alternating)
                left = self.percent_bodyweight * self.lateral_distribution[0] / 100
                right = self.percent_bodyweight * self.lateral_distribution[0] / 100
        elif self.lateral_distribution_pattern == WeightDistribution.unilateral_alternating:  # each side gets all the intensity for each rep  # (100, 100)
            left = self.percent_bodyweight * self.lateral_distribution[0] / 100
            right = self.percent_bodyweight * self.lateral_distribution[1] / 100
        self.body_weight_left = left
        self.body_weight_right = right

    def set_training_load(self, total_volume):

        self.set_training_volume(total_volume)
        if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            # both sides have same volume (duration) and intensity (rpe)

            power_left = self.power.plagiarize()
            if isinstance(self.training_volume_left, Assignment):
                power_left = Assignment.multiply_range_by_assignment(power_left, self.training_volume_left)
            else:
                power_left.multiply(self.training_volume_left)

            power_right = self.power.plagiarize()
            if isinstance(self.training_volume_right, Assignment):
                power_right = Assignment.multiply_range_by_assignment(power_right, self.training_volume_right)
            else:
                power_right.multiply(self.training_volume_right)

            self.power_load_left.add(power_left)
            self.power_load_right.add(power_right)

            if self.force is not None:
                force_left = self.force.plagiarize()
                if isinstance(self.training_volume_left, Assignment):
                    force_left = Assignment.multiply_range_by_assignment(force_left, self.training_volume_left)
                else:
                    force_left.multiply(self.training_volume_left)

                force_right = self.force.plagiarize()
                if isinstance(self.training_volume_right, Assignment):
                    force_right = Assignment.multiply_range_by_assignment(force_right, self.training_volume_right)
                else:
                    force_right.multiply(self.training_volume_right)
                self.force_load_left.add(force_left)
                self.force_load_right.add(force_right)
                self.tissue_load_left = self.force_load_left
                self.tissue_load_right = self.force_load_right


        else:
            left_dist = 1
            right_dist = 1
            if self.lateral_distribution_pattern == WeightDistribution.unilateral:
                if self.side == 1:
                    left_dist = self.lateral_distribution[0] / 100
                    right_dist = self.lateral_distribution[1] / 100
                elif self.side == 2:
                    left_dist = self.lateral_distribution[1] / 100
                    right_dist = self.lateral_distribution[0] / 100
            elif self.lateral_distribution_pattern == WeightDistribution.bilateral_uneven:
                if self.side == 1:
                    left_dist = self.lateral_distribution[0] / 100 * 2
                    right_dist = self.lateral_distribution[1] / 100 * 2
                elif self.side == 2:
                    left_dist = self.lateral_distribution[1] / 100 * 2
                    right_dist = self.lateral_distribution[0] / 100 * 2
            # self.tissue_load_left.add_value(self.training_volume_left * self.training_intensity * left_dist)
            # self.tissue_load_right.add_value(self.training_volume_right * self.training_intensity * right_dist)
            force_left, force_right = self.set_left_right_distribution("force")
            power_left, power_right = self.set_left_right_distribution("power")

            if force_left is not None:
                #force_left.multiply(self.training_volume_left * left_dist)
                if isinstance(self.training_volume_left, Assignment):
                    force_left = Assignment.multiply_range_by_assignment(force_left, self.training_volume_left)
                    force_left.multiply(left_dist)
                else:
                    force_left.multiply(self.training_volume_left * left_dist)
                self.force_load_left.add(force_left)
                self.tissue_load_left = self.force_load_left

            if force_right is not None:
                #force_right.multiply(self.training_volume_right * right_dist)
                if isinstance(self.training_volume_right, Assignment):
                    force_right = Assignment.multiply_range_by_assignment(force_right, self.training_volume_right)
                    force_right.multiply(right_dist)
                else:
                    force_right.multiply(self.training_volume_right * right_dist)
                self.force_load_right.add(force_right)
                self.tissue_load_right = self.force_load_right

            #power_left.multiply(self.training_volume_left * left_dist)
            if isinstance(self.training_volume_left, Assignment):
                power_left = Assignment.multiply_range_by_assignment(power_left, self.training_volume_left)
                power_left.multiply(left_dist)
            else:
                power_left.multiply(self.training_volume_left * left_dist)

            #power_right.multiply(self.training_volume_right * right_dist)
            if isinstance(self.training_volume_right, Assignment):
                power_right = Assignment.multiply_range_by_assignment(power_right, self.training_volume_right)
                power_right.multiply(right_dist)
            else:
                power_right.multiply(self.training_volume_right * right_dist)

            self.power_load_left.add(power_left)
            self.power_load_right.add(power_right)

    def set_training_volume(self, total_volume):
        if self.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            # both sides are assigned all the reps (already in duration)
            self.training_volume_left = total_volume
            self.training_volume_right = total_volume
        else:
            # use 1 rep = 4s to get volume in seconds
            #total_volume = self.reps * 4
            if self.lateral_distribution_pattern == WeightDistribution.unilateral:
                if self.side == 1:
                    self.training_volume_left = total_volume
                elif self.side == 2:
                    self.training_volume_right = total_volume
                else:
                    if isinstance(total_volume, Assignment):
                        self.training_volume_left = Assignment.divide_assignment_by_scalar(total_volume, 2)
                    else:
                        self.training_volume_left = total_volume / 2
                    if isinstance(total_volume, Assignment):
                        self.training_volume_right = Assignment.divide_assignment_by_scalar(total_volume, 2)
                    else:
                        self.training_volume_right = total_volume / 2
            elif self.lateral_distribution_pattern == WeightDistribution.bilateral_uneven:
                if self.side == 1:
                    if self.lateral_distribution[0] != 0:
                        self.training_volume_left = total_volume
                    if self.lateral_distribution[1] != 0:
                        self.training_volume_right = total_volume
                elif self.side == 2:
                    if self.lateral_distribution[1] != 0:
                        self.training_volume_left = total_volume
                    if self.lateral_distribution[0] != 0:
                        self.training_volume_right = total_volume
                else:
                    self.training_volume_left = total_volume
                    self.training_volume_right = total_volume
            else:
                self.training_volume_left = total_volume
                self.training_volume_right = total_volume


class PrioritizedJointAction(object):
    def __init__(self, priority, joint_action):
        self.priority = priority
        self.joint_action = joint_action

    def json_serialise(self):
        ret = {
            "priority": self.priority,
            "joint_action": self.joint_action.value
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        return cls(input_dict.get('priority'), FunctionalMovementType(input_dict.get('joint_action')))


class ExerciseCompoundAction(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.actions = []


class MovementSpeed(Enum):
    none = 0
    slow = 1
    mod = 2
    fast = 3
    explosive = 4

class MovementResistance(Enum):
    none = 0
    low = 1
    mod = 2
    high = 3
    max = 4


class Explosiveness(IntEnum):
    no_force = 0
    low_force = 1
    mod_force = 2
    high_force = 3
    max_force = 4


class Movement(Serialisable):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.primary_actions = []
        self.secondary_actions = []
        self.surface_stability = None
        self.external_weight_implement = []
        self.resistance = None
        self.speed = None
        self.training_type = None
        self.cardio_action = None
        self.power_drill_action = None
        self.power_action = None
        self.strength_resistance_action = None
        self.strength_endurance_action = None

        # calculated
        self.explosiveness_rating = 0

    def json_serialise(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'training_type': self.training_type.value if self.training_type is not None else None,
            'cardio_action': self.cardio_action.value if self.cardio_action is not None else None,
            'power_drill_action': self.power_drill_action.value if self.power_drill_action is not None else None,
            'power_action': self.power_action.value if self.power_action is not None else None,
            'strength_resistance_action': self.strength_resistance_action.value if self.strength_resistance_action is not None else None,
            'strength_endurance_action': self.strength_endurance_action.value if self.strength_endurance_action is not None else None,
            'external_weight_implement': [equipment.value for equipment in self.external_weight_implement],
            'speed': self.speed.value if self.speed is not None else None,
            'resistance': self.resistance.value if self.resistance is not None else None,
            'surface_stability': self.surface_stability.value if self.surface_stability is not None else None,
            'primary_actions': self.primary_actions,
            'secondary_actions': self.secondary_actions,
            'explosiveness_rating': self.explosiveness_rating
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        movement = cls(input_dict.get('id'), input_dict.get('name'))

        movement.body_position = BodyPosition(input_dict['body_position']) if input_dict.get(
            'body_position') is not None else None
        movement.cardio_action = CardioAction(input_dict['cardio_action']) if input_dict.get(
            'cardio_action') is not None else None
        movement.power_drill_action = PowerDrillAction(input_dict['power_drill_action']) if input_dict.get(
            'power_drill_action') is not None else None
        movement.power_action = PowerAction(input_dict['power_action']) if input_dict.get(
            'power_action') is not None else None
        movement.strength_resistance_action = StrengthResistanceAction(input_dict['strength_resistance_action']) if input_dict.get(
            'strength_resistance_action') is not None else None
        movement.strength_endurance_action = StrengthEnduranceAction(input_dict['strength_endurance_action']) if input_dict.get(
            'strength_endurance_action') is not None else None
        movement.training_type = TrainingType(input_dict['training_type']) if input_dict.get('training_type') is not None else None
        movement.external_weight_implement = [Equipment(equipment) for equipment in input_dict.get('external_weight_implement', [])]
        movement.speed = MovementSpeed(input_dict['speed']) if input_dict.get('speed') is not None else None
        movement.resistance = MovementResistance(input_dict['resistance']) if input_dict.get('resistance') is not None else None
        movement.set_explosiveness_rating()
        movement.surface_stability = MovementSurfaceStability(input_dict['surface_stability']) if input_dict.get('surface_stability') is not None else None
        movement.primary_actions = input_dict.get('primary_actions', [])
        movement.secondary_actions = input_dict.get('secondary_actions', [])

        return movement

    def set_explosiveness_rating(self):

        self.explosiveness_rating = 0

        if self.speed is not None and self.resistance is not None:
            if self.resistance == MovementResistance.low:
                if self.speed == MovementSpeed.explosive:
                    self.explosiveness_rating = 4
                else:
                    self.explosiveness_rating = 3
            elif self.resistance == MovementResistance.mod:
                if self.speed == MovementSpeed.explosive:
                    self.explosiveness_rating = 6
                else:
                    self.explosiveness_rating = 5
            elif self.resistance == MovementResistance.high:
                if self.speed == MovementSpeed.explosive:
                    self.explosiveness_rating = 8
                else:
                    self.explosiveness_rating = 7
            elif self.resistance == MovementResistance.max:
                if self.speed == MovementSpeed.explosive:
                    self.explosiveness_rating = 10
                else:
                    self.explosiveness_rating = 9


class ExternalWeight(object):
    def __init__(self, equipment, value):
        self.equipment = equipment
        self.value = value
        self.distribute_weight = self.equipment.distribute_weights()

    def __setattr__(self, key, value):
        if key == 'equipment' and not isinstance(value, Equipment):
            value = Equipment(value)
        super().__setattr__(key, value)

    def json_serialise(self):
        return {
            'equipment': self.equipment.value,
            'value': self.value,
            'distribute_weight': self.distribute_weight
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        return cls(input_dict.get('equipment'), input_dict.get('value'))
