from random import shuffle

from models.exercise import AssignedExercise
from models.soreness_base import BodyPartLocation, BodyPartSide
from models.sport import SportName
import random


class BodyPartFactory(object):

    def is_joint(self, body_part):

        location = self.get_body_part_location(body_part)

        if (location == BodyPartLocation.shoulder or
                location == BodyPartLocation.hip_flexor or
                location == BodyPartLocation.knee or
                location == BodyPartLocation.ankle or
                location == BodyPartLocation.foot or
                location == BodyPartLocation.lower_back or
                location == BodyPartLocation.elbow or
                location == BodyPartLocation.wrist):
            return True
        else:
            return False

    def is_muscle(self, body_part):

        location = self.get_body_part_location(body_part)

        if (
                location == BodyPartLocation.chest or
                location == BodyPartLocation.abdominals or
                location == BodyPartLocation.groin or
                location == BodyPartLocation.quads or
                location == BodyPartLocation.shin or
                location == BodyPartLocation.outer_thigh or
                location == BodyPartLocation.glutes or
                location == BodyPartLocation.hamstrings or
                location == BodyPartLocation.calves or
                location == BodyPartLocation.achilles or
                location == BodyPartLocation.upper_back_neck or
                location == BodyPartLocation.lats or
                location == BodyPartLocation.biceps or
                location == BodyPartLocation.triceps):
            return True
        else:
            return False

    def get_body_part_location(self, body_part):

        location = None

        if isinstance(body_part, BodyPart):
            location = body_part.location
        elif isinstance(body_part, BodyPartSide):
            location = body_part.body_part_location
        elif isinstance(body_part, BodyPartLocation):
            location = body_part
        return location

    def get_progression_list(self, exercise):

        dict = {}
        #dict["9"] = ["121"]zz

        dict["10"] = ["12", "11", "13", "120"]

        dict["29"] = ["63", "64"]

        dict["6"] = ["117"]
        dict["46"] = ["117"]

        # 28 and 49 are in the same bucket, and 119 and 122 are in the same bucket.  This should be ok
        dict["28"] = ["122"]
        dict["49"] = ["119"]

        dict["67"] = ["78", "68", "31"]
        dict["81"] = ["82", "83", "110"]

        dict["85"] = ["86", "87", "88"]
        dict["89"] = ["90", "91", "92"]
        dict["103"] = ["104"]
        dict["106"] = ["105", "113"]
        dict["108"] = ["124"]
        dict["115"] = ["114", "65", "66", "107"]
        dict["135"] = ["136", "138"]

        if exercise in dict:
            return dict[exercise]
        else:
            return []

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

    def get_body_part_for_sports(self, sport_list):

        full_body_list = [SportName.basketball, SportName.football, SportName.general_fitness, SportName.gymnastics,
                          SportName.rugby, SportName.pool_sports, SportName.volleyball, SportName.wrestling,
                          SportName.weightlifting, SportName.track_field, SportName.australian_football,
                          SportName.cricket, SportName.dance, SportName.equestrian_sports, SportName.fencing,
                          SportName.martial_arts, SportName.swimming, SportName.water_polo,SportName.kick_boxing,
                          SportName.endurance, SportName.power, SportName.strength, SportName.cross_training,
                          SportName.functional_strength_training, SportName.mind_and_body, SportName.play,
                          SportName.preparation_and_recovery, SportName.traditional_strength_training,
                          SportName.water_fitness, SportName.yoga, SportName.barre, SportName.core_training,
                          SportName.flexibility, SportName.high_intensity_interval_training,
                          SportName.pilates, SportName.taichi, SportName.mixed_cardio, SportName.climbing,
                          SportName.other, SportName.no_sport]

        lower_body_list = [SportName.cycling, SportName.field_hockey, SportName.skate_sports, SportName.lacrosse,
                           SportName.diving, SportName.soccer, SportName.distance_running, SportName.sprints,
                           SportName.jumps, SportName.curling, SportName.hockey, SportName.snow_sports,
                           SportName.surfing_sports, SportName.cross_country_skiing, SportName.downhill_skiing,
                           SportName.snowboarding, SportName.speed_agility, SportName.elliptical,
                           SportName.hiking, SportName.stair_climbing, SportName.walking, SportName.jump_rope,
                           SportName.stairs, SportName.step_training]

        use_full = False
        use_lower = False
        use_upper = False

        for sport in sport_list:
            if sport in full_body_list:
                use_full = True
                break
            elif sport in lower_body_list:
                use_lower = True
            elif sport not in full_body_list and sport not in lower_body_list:
                use_upper = True

        if use_full:
            return self.get_body_part(BodyPart(BodyPartLocation.full_body, None))
        elif use_lower and not use_upper:
            return self.get_body_part(BodyPart(BodyPartLocation.lower_body, None))
        elif not use_lower and use_upper:
            return self.get_body_part(BodyPart(BodyPartLocation.upper_body, None))
        elif use_lower and use_upper:
            return self.get_body_part(BodyPart(BodyPartLocation.full_body, None))
        else:
            return self.get_body_part(BodyPart(BodyPartLocation.full_body, None))

    def get_body_part(self, body_part):

        location = self.get_body_part_location(body_part)

        if location == BodyPartLocation.general:
            return self.get_general()
        elif location == BodyPartLocation.abdominals:
            return self.get_abdominals()
        elif location == BodyPartLocation.achilles:
            return self.get_achilles()
        elif location == BodyPartLocation.ankle:
            return self.get_ankle()
        elif location == BodyPartLocation.biceps:
            return self.get_biceps()
        elif location == BodyPartLocation.calves:
            return self.get_calves()
        elif location == BodyPartLocation.chest:
            return self.get_chest()
        elif location == BodyPartLocation.elbow:
            return self.get_elbow()
        elif location == BodyPartLocation.foot:
            return self.get_foot()
        elif location == BodyPartLocation.glutes:
            return self.get_glutes()
        elif location == BodyPartLocation.groin:
            return self.get_groin()
        elif location == BodyPartLocation.hamstrings:
            return self.get_hamstrings()
        elif location == BodyPartLocation.hip_flexor:
            return self.get_hip()
        elif location == BodyPartLocation.knee:
            return self.get_knee()
        elif location == BodyPartLocation.lats:
            return self.get_lats()
        elif location == BodyPartLocation.lower_back:
            return self.get_lower_back()
        elif location == BodyPartLocation.outer_thigh:
            return self.get_outer_thigh()
        elif location == BodyPartLocation.quads:
            return self.get_quads()
        elif location == BodyPartLocation.shin:
            return self.get_shin()
        elif location == BodyPartLocation.triceps:
            return self.get_triceps()
        elif location == BodyPartLocation.shoulder:
            return self.get_shoulder()
        elif location == BodyPartLocation.upper_back_neck:
            return self.get_upper_back_traps_neck()
        elif location == BodyPartLocation.wrist:
            return self.get_wrist()

        elif location == BodyPartLocation.lower_body:
            return self.get_lower_body()
        elif location == BodyPartLocation.upper_body:
            return self.get_upper_body()
        elif location == BodyPartLocation.full_body:
            return self.get_full_body()

    def get_constituent_exercises(self, primary_body_part, constituent_body_parts, soreness):

        for c in constituent_body_parts:
            body_part = self.get_body_part(BodyPart(BodyPartLocation(c), None))
            primary_body_part.inhibit_exercises.extend(body_part.inhibit_exercises)
            primary_body_part.static_stretch_exercises.extend(body_part.static_stretch_exercises)
            primary_body_part.active_stretch_exercises.extend(body_part.active_stretch_exercises)
            primary_body_part.dynamic_stretch_exercises.extend(body_part.dynamic_stretch_exercises)
            primary_body_part.isolated_activation_exercises.extend(body_part.isolated_activate_exercises)
            primary_body_part.static_integrate_exercises.extend(body_part.static_integrate_exercises)

        return primary_body_part

    def get_general(self):

        #############
        # WARNING: If you change anything here ALSO change full body
        ##############

        general = BodyPart(BodyPartLocation.general, 21)
        general.bilateral = False

        #inhibit = self.get_exercise_dictionary([48, 3, 4, 54, 2, 44, 55])
        #lengthen = self.get_exercise_dictionary([9, 6, 28, 56, 7, 46, 103])
        #activate = self.get_exercise_dictionary([81, 108, 10, 85, 89])
        static_integrate = self.get_exercise_dictionary([15, 14, 231])

        general.add_extended_exercise_phases({}, {}, {}, {}, {}, static_integrate)
        general.add_muscle_groups([12, 6, 4], [5, 15], [21, 11], [3, 14])
        return general

    def get_upper_body(self):

        upper_body = BodyPart(BodyPartLocation.upper_body, 22)
        upper_body.bilateral = False

        dynamic_stretch = self.get_full_exercise_dictionary([164, 165, 179, 180, 181])
        dynamic_integrate = self.get_full_exercise_dictionary([145, 148, 149, 162, 169])
        dynamic_integrate_with_speed = {}

        static_integrate = self.get_exercise_dictionary([240])

        upper_body.add_extended_exercise_phases({}, {}, {}, {}, {}, static_integrate)

        upper_body.add_dynamic_exercise_phases(dynamic_stretch, dynamic_integrate, dynamic_integrate_with_speed)

        upper_body.add_muscle_groups([1, 18], [2], [], [21, 18])
        return upper_body

    def get_lower_body(self):

        lower_body = BodyPart(BodyPartLocation.lower_body, 23)
        lower_body.bilateral = False
        dynamic_stretch = self.get_full_exercise_dictionary([139, 140, 141, 142, 143, 144, 161, 163, 164, 165, 176, 193])
        dynamic_integrate = self.get_full_exercise_dictionary([145, 146, 147, 148, 149, 150, 151, 182, 183, 203, 204])
        dynamic_integrate_with_speed = {}

        static_integrate = self.get_exercise_dictionary([15, 14])

        lower_body.add_extended_exercise_phases({}, {}, {}, {}, {}, static_integrate)

        lower_body.add_dynamic_exercise_phases(dynamic_stretch, dynamic_integrate, dynamic_integrate_with_speed)

        lower_body.add_muscle_groups([16, 15], [5, 11], [], [14])

        return lower_body

    def get_full_body(self):

        full_body = BodyPart(BodyPartLocation.full_body, 24)
        full_body.bilateral = False
        dynamic_stretch = self.get_full_exercise_dictionary([139, 140, 141, 144, 164, 165, 177, 178, 179, 180, 193])
        dynamic_integrate = self.get_full_exercise_dictionary([145, 146, 148, 149, 150, 151, 162, 169, 203, 204])
        dynamic_integrate_with_speed = {}

        # just copied over from general

        static_integrate = self.get_exercise_dictionary([15, 14, 231])

        full_body.add_extended_exercise_phases({}, {}, {}, {}, {}, static_integrate)

        full_body.add_dynamic_exercise_phases(dynamic_stretch, dynamic_integrate, dynamic_integrate_with_speed)

        full_body.add_muscle_groups([12, 6, 4], [5, 15], [21, 11], [3, 14])

        return full_body

    def get_achilles(self):

        part = BodyPart(BodyPartLocation.achilles, 18)

        inhibit = self.get_exercise_dictionary([2])
        static_stretch = self.get_exercise_dictionary([7, 26])
        active_stretch = self.get_exercise_dictionary([267, 268])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([31, 67, 78, 68])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation,
                                          {})
        part.add_muscle_groups([17], [10], [15], [8])
        return part

    def get_abdominals(self):

        part = BodyPart(BodyPartLocation.abdominals, 4)
        part.bilateral = False

        inhibit = self.get_exercise_dictionary([54])
        static_stretch = self.get_exercise_dictionary([98])
        active_stretch = self.get_exercise_dictionary([265])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([79, 234, 84, 50])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation,
                                          {})
        part.add_muscle_groups([3], [4], [12, 5], [18, 4])
        return part

    def get_ankle(self):

        part = BodyPart(BodyPartLocation.ankle, 12)

        inhibit = self.get_exercise_dictionary([])
        static_stretch = self.get_exercise_dictionary([])
        active_stretch = self.get_exercise_dictionary([])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation,
                                          {})
        part.add_muscle_groups([16], [8], [10], [])
        return part

    def get_biceps(self):

        part = BodyPart(BodyPartLocation.biceps, None)

        inhibit = self.get_exercise_dictionary([243, 244])
        static_stretch = self.get_exercise_dictionary([246])
        active_stretch = self.get_exercise_dictionary([264])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([249, 250])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation,
                                          {})
        part.add_muscle_groups([22], [], [], [23])
        return part

    def get_calves(self):
        calves = BodyPart(BodyPartLocation.calves, 10)
        inhibit = self.get_exercise_dictionary([2, 71])
        static_stretch = self.get_exercise_dictionary([7, 26, 214, 215, 216, 219])
        active_stretch = self.get_exercise_dictionary([267, 268, 270, 271])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([31, 78, 67, 68])
        calves.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        calves.add_muscle_groups([16], [11], [8], [8, 10])
        return calves

    def get_chest(self):

        part = BodyPart(BodyPartLocation.chest, 16)

        inhibit = self.get_exercise_dictionary([260])
        static_stretch = self.get_exercise_dictionary([238, 98, 246])
        active_stretch = self.get_exercise_dictionary([276])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([201])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        part.add_muscle_groups([2], [1, 21], [2], [18])
        return part

    def get_elbow(self):

        part = BodyPart(BodyPartLocation.elbow, 19)

        inhibit = self.get_exercise_dictionary([245])
        static_stretch = self.get_exercise_dictionary([247, 246])
        active_stretch = self.get_exercise_dictionary([261, 262])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([249, 250, 251, 252])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation,
                                          {})
        part.add_muscle_groups([19, 22, 23], [1], [19, 20], [22, 23])
        return part

    def get_foot(self):

        part = BodyPart(BodyPartLocation.foot, 17)

        inhibit = self.get_exercise_dictionary([74])
        static_stretch = self.get_exercise_dictionary([59, 60])
        active_stretch = self.get_exercise_dictionary([269])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([53, 63, 64, 66, 106, 114])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation,
                                          {})
        part.add_muscle_groups([10], [16], [8], [])
        return part

    def get_glutes(self):

        glutes = BodyPart(BodyPartLocation.glutes, 3)
        inhibit = self.get_exercise_dictionary([44])
        static_stretch = self.get_exercise_dictionary([46, 56, 221, 222, 223, 225])
        active_stretch = self.get_exercise_dictionary([272, 273, 274])
        dynamic_stretch = self.get_exercise_dictionary([53, 63, 64])
        isolated_activation = self.get_exercise_dictionary([10, 81, 119, 226, 230, 232, 233])
        glutes.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        glutes.add_muscle_groups([14], [6, 5, 12], [11], [4, 5])
        return glutes

    def get_groin(self):

        groin = BodyPart(BodyPartLocation.groin, 7)
        inhibit = self.get_exercise_dictionary([1])
        static_stretch = self.get_exercise_dictionary([8])
        active_stretch = self.get_exercise_dictionary([122])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([232, 142, 143, 227, 226])
        groin.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        groin.add_muscle_groups([5], [4], [3, 6], [14])
        return groin

    def get_hamstrings(self):

        hamstrings = BodyPart(BodyPartLocation.hamstrings, 5)
        inhibit = self.get_exercise_dictionary([3])
        static_stretch = self.get_exercise_dictionary([215, 9, 121, 216, 218, 219])
        active_stretch = self.get_exercise_dictionary([271])
        dynamic_stretch = self.get_exercise_dictionary([139, 177])
        isolated_activation = self.get_exercise_dictionary([230])
        hamstrings.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        hamstrings.add_muscle_groups([15], [16, 14], [11, 12], [6])
        return hamstrings

    def get_hip(self):

        hip = BodyPart(BodyPartLocation.hip_flexor, 2)
        inhibit = self.get_exercise_dictionary([54])
        static_stretch = self.get_exercise_dictionary([6, 28, 49, 217, 224])
        active_stretch = self.get_exercise_dictionary([277])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([142, 143, 229, 228, 236, 232])
        hip.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        hip.add_muscle_groups([4], [15, 6], [5, 11], [14])
        return hip

    def get_knee(self):

        knee = BodyPart(BodyPartLocation.knee, 9)
        inhibit = self.get_exercise_dictionary([])
        static_stretch = self.get_exercise_dictionary([])
        active_stretch = {}
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([])
        knee.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        knee.add_muscle_groups([15], [16, 4], [11, 8], [6])

        return knee

    def get_lats(self):

        part = BodyPart(BodyPartLocation.lats, 15)
        inhibit = self.get_exercise_dictionary([55])
        static_stretch = self.get_exercise_dictionary([57, 103, 104])
        active_stretch = self.get_exercise_dictionary([263])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([241, 239])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        part.add_muscle_groups([21], [3, 18], [12, 2], [1, 22])

        return part

    def get_lower_back(self):

        part = BodyPart(BodyPartLocation.lower_back, 1)
        part.bilateral = False
        inhibit = self.get_exercise_dictionary([44])
        static_stretch = self.get_exercise_dictionary([56, 103, 104])
        active_stretch = self.get_exercise_dictionary([266])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([51, 79])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        part.add_muscle_groups([12, 14], [21, 15], [11, 5, 6], [3])

        return part

    def get_outer_thigh(self):

        outer_thigh = BodyPart(BodyPartLocation.outer_thigh, 6)

        inhibit = self.get_exercise_dictionary([4])
        static_stretch = self.get_exercise_dictionary([46, 56, 225, 224])
        active_stretch = self.get_exercise_dictionary([272, 273, 274])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([142, 143, 226, 227, 228, 232, 236])
        outer_thigh.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        outer_thigh.add_muscle_groups([11], [6, 4], [15], [5, 14])
        return outer_thigh

    def get_quads(self):

        quads = BodyPart(BodyPartLocation.quads, 8)

        inhibit = self.get_exercise_dictionary([48])
        static_stretch = self.get_exercise_dictionary([118])
        active_stretch = self.get_exercise_dictionary([275])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([10, 119, 234])
        quads.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        quads.add_muscle_groups([6], [11, 5], [4, 14], [15])
        return quads

    def get_shin(self):

        shin = BodyPart(BodyPartLocation.shin, 11)

        inhibit = self.get_exercise_dictionary([72, 73])
        static_stretch = self.get_exercise_dictionary([60])
        active_stretch = self.get_exercise_dictionary([269])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([75, 29, 64, 65])
        shin.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        shin.add_muscle_groups([8], [6], [5, 11], [16, 10])
        return shin

    def get_shoulder(self):

        part = BodyPart(BodyPartLocation.shoulder, 14)

        inhibit = self.get_exercise_dictionary([259])
        static_stretch = self.get_exercise_dictionary([130, 246, 215])
        active_stretch = self.get_exercise_dictionary([276])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([239, 135, 136, 137, 241, 242])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        part.add_muscle_groups([1], [21], [22], [2, 18])
        return part

    def get_triceps(self):

        part = BodyPart(BodyPartLocation.triceps, None)

        inhibit = self.get_exercise_dictionary([258])
        static_stretch = self.get_exercise_dictionary([57, 103, 104])
        active_stretch = self.get_exercise_dictionary([263])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([199])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, {})
        part.add_muscle_groups([23], [], [], [22])
        return part

    def get_upper_back_traps_neck(self):

        part = BodyPart(BodyPartLocation.upper_back_neck, 13)
        part.bilateral = False

        inhibit = self.get_exercise_dictionary([102, 125, 126])
        static_stretch = self.get_exercise_dictionary([127, 129, 128, 103, 104, 246, 215])
        active_stretch = self.get_exercise_dictionary([131, 132, 133])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([51, 136, 137, 242, 135, 134])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation,
                                          {})
        part.add_muscle_groups([18], [2], [12, 21], [1])
        return part

    def get_wrist(self):

        part = BodyPart(BodyPartLocation.wrist, 20)

        inhibit = self.get_exercise_dictionary([245])
        static_stretch = self.get_exercise_dictionary([247, 248])
        active_stretch = self.get_exercise_dictionary([261, 262])
        dynamic_stretch = {}
        isolated_activation = self.get_exercise_dictionary([253, 254, 255])
        part.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation,
                                          {})
        part.add_muscle_groups([20], [22, 23], [19], [20])
        return part


class BodyPart(object):

    def __init__(self, body_part_location, treatment_priority):
        self.bilateral = True
        self.location = body_part_location
        self.treatment_priority = treatment_priority
        self.inhibit_exercises = []
        self.lengthen_exercises = []
        self.activate_exercises = []
        self.integrate_exercises = []

        self.static_stretch_exercises = []
        self.active_stretch_exercises = []
        self.dynamic_stretch_exercises = []
        self.active_or_dynamic_stretch_exercises = []
        self.isolated_activate_exercises = []
        self.static_integrate_exercises = []
        self.dynamic_integrate_exercises = []
        self.dynamic_stretch_integrate_exercises = []
        self.dynamic_integrate_with_speed_exercises = []

        self.agonists = []
        self.synergists = []
        self.stabilizers = []
        self.antagonists = []

    @staticmethod
    def add_exercises(exercise_list, exercise_dict, treatment_priority, randomize=False):

        priority = 1

        keys = list(exercise_dict.keys())

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

    def add_exercise_phases(self, inhibit, lengthen, activate, randomize=False):

        self.inhibit_exercises = self.add_exercises(self.inhibit_exercises, inhibit,
                                                    self.treatment_priority, randomize)
        self.lengthen_exercises = self.add_exercises(self.lengthen_exercises, lengthen,
                                                     self.treatment_priority, randomize)
        self.activate_exercises = self.add_exercises(self.activate_exercises, activate,
                                                     self.treatment_priority, randomize)

    def add_dynamic_exercise_phases(self, dynamic_stretch, dynamic_integrate, dynamic_integrate_with_speed):

        self.dynamic_stretch_exercises = self.add_exercises(self.dynamic_stretch_exercises, dynamic_stretch, self.treatment_priority, False)
        self.dynamic_integrate_exercises = self.add_exercises(self.dynamic_integrate_exercises, dynamic_integrate, self.treatment_priority, False)
        self.dynamic_integrate_with_speed_exercises = self.add_exercises(self.dynamic_integrate_with_speed_exercises, dynamic_integrate_with_speed, self.treatment_priority, False)

    def add_extended_exercise_phases(self, inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, static_integrate, randomize=False):

        self.inhibit_exercises = self.add_exercises(self.inhibit_exercises, inhibit,
                                                    self.treatment_priority, randomize)

        self.static_stretch_exercises = self.add_exercises(self.static_stretch_exercises, static_stretch,
                                                           self.treatment_priority, randomize)

        self.active_stretch_exercises = self.add_exercises(self.active_stretch_exercises, active_stretch,
                                                           self.treatment_priority, randomize)

        self.dynamic_stretch_exercises = self.add_exercises(self.dynamic_stretch_exercises, dynamic_stretch,
                                                            self.treatment_priority, randomize)

        self.isolated_activate_exercises = self.add_exercises(self.isolated_activate_exercises, isolated_activation,
                                                              self.treatment_priority, randomize)

        self.static_integrate_exercises = self.add_exercises(self.static_integrate_exercises, static_integrate,
                                                             self.treatment_priority, randomize)

    def add_muscle_groups(self, agonists, synergists, stabilizers, antagonists):

        self.agonists = agonists
        self.synergists = synergists
        self.stabilizers = stabilizers
        self.antagonists = antagonists


