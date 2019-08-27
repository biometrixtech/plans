from enum import Enum
import random
from models.soreness_base import BodyPartLocation, BodyPartSide


class MovementErrorType(Enum):
    apt_asymmetry = 0


class MovementError(object):
    def __init__(self, movement_error_type, body_part_side):
        self.movement_error_type = movement_error_type
        self.body_part_side = body_part_side
        self.overactive_tight_first = []
        self.overactive_tight_second = []
        self.elevated_stress = []
        self.underactive_weak = []
        self.left_apt = 0
        self.right_apt = 0

    def add_muscle_groups(self, overactive_tight_first, overactive_tight_second, elevated_stress, underactive_weak):

        self.overactive_tight_first = overactive_tight_first
        self.overactive_tight_second = overactive_tight_second
        self.elevated_stress = elevated_stress
        self.underactive_weak = underactive_weak


class MovementErrorFactory(object):
    def get_exercise_dictionary(self, exercise_list):

        exercise_dict = {}

        # pick on exercise from the list:
        if len(exercise_list) > 0:
            position = random.randint(0, len(exercise_list) - 1)

            # ignoring progressions for now
            #for e in exercise_list:
            #    exercise_dict[e] = self.get_progression_list(e)

            exercise_dict[exercise_list[position]] = []

        return exercise_dict

    def get_full_exercise_dictionary(self, exercise_list):

        exercise_dict = {}

        sampled_list = random.sample(exercise_list, 4)

        # ignoring progressions for now
        for e in sampled_list:
            exercise_dict[e] = []

        return exercise_dict

    def get_movement_error(self, movement_error_type, left_apt, right_apt):

        if movement_error_type == MovementErrorType.apt_asymmetry:
            return self.get_apt_asymmetry(left_apt, right_apt)

    def get_apt_asymmetry(self, left_apt, right_apt):
        movement_error = MovementError(MovementErrorType.apt_asymmetry, BodyPartSide(BodyPartLocation(4), 0))
        movement_error.left_apt = left_apt
        movement_error.right_apt = right_apt
        movement_error.add_muscle_groups([6, 21], [4, 26], [16, 15, 5], [14, 25])
        return movement_error
