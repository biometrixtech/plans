from serialisable import Serialisable


class Elasticity(Serialisable):
    def __init__(self):
        self.elasticity = 0.0
        self.y_adf = 0.0

    def json_serialise(self):
        ret = {
            'elasticity': self.elasticity,
            'y_adf': self.y_adf
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        elasticity_data = cls()
        elasticity_data.elasticity = input_dict.get("elasticity", 0.0)
        elasticity_data.y_adf = input_dict.get("y_adf", 0.0)
        return elasticity_data


class LeftRightElasticity(Serialisable):
    def __init__(self):
        self.left = None
        self.right = None

    def json_serialise(self):
        ret = {
            'left': self.left.json_serialise() if self.left is not None else None,
            'right': self.right.json_serialise() if self.right is not None else None
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        left_right = cls()
        left_right.left = Elasticity.json_deserialise(input_dict["left"]) if input_dict.get("left") is not None else None
        left_right.right = Elasticity.json_deserialise(input_dict["right"]) if input_dict.get("right") is not None else None
        return left_right


class MovementPatterns(Serialisable):
    def __init__(self):
        self.apt_ankle_pitch = None
        self.hip_drop_apt = None
        self.hip_drop_pva = None
        self.knee_valgus_hip_drop = None
        self.knee_valgus_pva = None
        self.knee_valgus_apt = None
        self.hip_rotation_ankle_pitch = None
        self.hip_rotation_apt = None

    def json_serialise(self):
        ret = {
            'apt_ankle_pitch': self.apt_ankle_pitch.json_serialise() if self.apt_ankle_pitch is not None else None,
            'hip_drop_apt': self.hip_drop_apt.json_serialise() if self.hip_drop_apt is not None else None,
            'hip_drop_pva': self.hip_drop_pva.json_serialise() if self.hip_drop_pva is not None else None,
            'knee_valgus_hip_drop': self.knee_valgus_hip_drop.json_serialise() if self.knee_valgus_hip_drop is not None else None,
            'knee_valgus_pva': self.knee_valgus_pva.json_serialise() if self.knee_valgus_pva is not None else None,
            'knee_valgus_apt': self.knee_valgus_apt.json_serialise() if self.knee_valgus_apt is not None else None,
            'hip_rotation_ankle_pitch': self.hip_rotation_ankle_pitch.json_serialise() if self.hip_rotation_ankle_pitch is not None else None,
            'hip_rotation_apt': self.hip_rotation_apt.json_serialise() if self.hip_rotation_apt is not None else None,
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        movement_patterns = cls()
        movement_patterns.apt_ankle_pitch = LeftRightElasticity.json_deserialise(
            input_dict['apt_ankle_pitch']) if input_dict.get('apt_ankle_pitch') is not None else None
        movement_patterns.hip_drop_apt = LeftRightElasticity.json_deserialise(
            input_dict['hip_drop_apt']) if input_dict.get('hip_drop_apt') is not None else None
        movement_patterns.hip_drop_pva = LeftRightElasticity.json_deserialise(
            input_dict['hip_drop_pva']) if input_dict.get('hip_drop_pva') is not None else None
        movement_patterns.knee_valgus_hip_drop = LeftRightElasticity.json_deserialise(
            input_dict['knee_valgus_hip_drop']) if input_dict.get('knee_valgus_hip_drop') is not None else None
        movement_patterns.knee_valgus_pva = LeftRightElasticity.json_deserialise(
            input_dict['knee_valgus_pva']) if input_dict.get('knee_valgus_pva') is not None else None
        movement_patterns.knee_valgus_apt = LeftRightElasticity.json_deserialise(
            input_dict['knee_valgus_apt']) if input_dict.get('knee_valgus_apt') is not None else None
        movement_patterns.hip_rotation_ankle_pitch = LeftRightElasticity.json_deserialise(
            input_dict['hip_rotation_ankle_pitch']) if input_dict.get('hip_rotation_ankle_pitch') is not None else None
        movement_patterns.hip_rotation_apt = LeftRightElasticity.json_deserialise(
            input_dict['hip_rotation_apt']) if input_dict.get('hip_rotation_apt') is not None else None
        return movement_patterns