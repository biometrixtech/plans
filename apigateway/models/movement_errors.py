from enum import Enum
import random
from random import shuffle
from models.soreness_base import BodyPartLocation, BodyPartSide
from models.exercise import AssignedExercise


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
        self.inhibit_exercises = []
        self.static_stretch_exercises = []
        self.active_stretch_exercises = []
        self.dynamic_stretch_exercises = []
        self.isolated_activate_exercises = []
        self.static_integrate_exercises = []
        self.metric = 0

    def add_muscle_groups(self, overactive_tight_first, overactive_tight_second, elevated_stress, underactive_weak):

        self.overactive_tight_first = overactive_tight_first
        self.overactive_tight_second = overactive_tight_second
        self.elevated_stress = elevated_stress
        self.underactive_weak = underactive_weak

    @staticmethod
    def add_exercises(exercise_list, exercise_dict, treatment_priority, randomize=False):

        priority = 1

        keys = list(exercise_dict)

        if randomize:
            shuffle(keys)

        for k in keys:
            if len(exercise_dict[k]) == 0:
                exercise_list.append(AssignedExercise(k, treatment_priority, priority))
            else:
                progression_exercise = AssignedExercise(k, treatment_priority, priority)
                progression_exercise.exercise.progressions = exercise_dict[k]
                exercise_list.append(progression_exercise)
            priority += 1

        return exercise_list

    def add_extended_exercise_phases(self, inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, static_integrate, randomize=False):

        self.inhibit_exercises = self.add_exercises(self.inhibit_exercises, inhibit,
                                                    None, randomize)

        self.static_stretch_exercises = self.add_exercises(self.static_stretch_exercises, static_stretch,
                                                           None, randomize)

        self.active_stretch_exercises = self.add_exercises(self.active_stretch_exercises, active_stretch,
                                                           None, randomize)

        self.dynamic_stretch_exercises = self.add_exercises(self.dynamic_stretch_exercises, dynamic_stretch,
                                                            None, randomize)

        self.isolated_activate_exercises = self.add_exercises(self.isolated_activate_exercises, isolated_activation,
                                                              None, randomize)

        self.static_integrate_exercises = self.add_exercises(self.static_integrate_exercises, static_integrate,
                                                             None, randomize)


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

    def get_movement_error(self, movement_error_type, metric):

        if movement_error_type == MovementErrorType.apt_asymmetry:
            return self.get_apt_asymmetry(metric)

    def get_apt_asymmetry(self, metric):
        movement_error = MovementError(MovementErrorType.apt_asymmetry, BodyPartSide(BodyPartLocation(4), 0))
        movement_error.metric = metric
        static_integrate = self.get_exercise_dictionary([15, 231])
        movement_error.add_extended_exercise_phases({}, {}, {}, {}, {}, static_integrate)
        movement_error.add_muscle_groups([6, 21], [4, 26], [16, 15, 5], [14, 25])
        return movement_error
