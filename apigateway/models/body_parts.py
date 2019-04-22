from models.soreness import BodyPart, BodyPartLocation


class BodyPartFactory(object):
    def get_progression_list(self, exercise):

        dict = {}
        #dict["9"] = ["121"]

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

        for e in exercise_list:
            exercise_dict[e] = self.get_progression_list(e)

        return exercise_dict

    def get_body_part(self, body_part_location):

        if body_part_location == BodyPartLocation.knee:
            return self.get_knee()
        elif body_part_location == BodyPartLocation.quads:
            return self.get_quads()
        elif body_part_location == BodyPartLocation.outer_thigh:
            return self.get_outer_thigh()
        elif body_part_location == BodyPartLocation.glutes:
            return self.get_glutes()
        elif body_part_location == BodyPartLocation.calves:
            return self.get_calves()

    def get_general(self):

        general = BodyPart(BodyPartLocation.general, 21)

        inhibit = self.get_exercise_dictionary([48, 3, 4, 54, 2, 44, 55])
        lengthen = self.get_exercise_dictionary([9, 6, 28, 56, 7, 46, 103])
        activate = self.get_exercise_dictionary([81, 108, 10, 85, 89])
        static_integrate = self.get_exercise_dictionary([15, 14, 231])

        general.add_extended_exercise_phases(inhibit, [], [], [], [], static_integrate)

        return general

    def get_knee(self):

        knee = BodyPart(BodyPartLocation.knee, 9)

        knee.add_muscle_groups([11, 6], [15], [16, 8], [14])

        return knee

    def get_quads(self):

        quads = BodyPart(BodyPartLocation.quads, 8)

        inhibit = self.get_exercise_dictionary([48])
        static_stretch = self.get_exercise_dictionary([118])
        active_stretch = self.get_exercise_dictionary([176])
        dynamic_stretch = self.get_exercise_dictionary([81])
        isolated_activation = self.get_exercise_dictionary([10, 11, 12, 13, 15])
        quads.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, [])
        quads.add_muscle_groups([6], [11, 5], [4, 16], [14, 15])
        return quads

    def get_outer_thigh(self):

        outer_thigh = BodyPart(BodyPartLocation.outer_thigh, 6)

        inhibit = self.get_exercise_dictionary([4])
        static_stretch = self.get_exercise_dictionary([28, 46, 49, 56])
        active_stretch = self.get_exercise_dictionary([112, 117])
        dynamic_stretch = []
        isolated_activation = self.get_exercise_dictionary([124, 227])
        outer_thigh.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, [])
        outer_thigh.add_muscle_groups([11], [6], [2], [5, 14])
        return outer_thigh

    def get_glutes(self):

        glutes = BodyPart(BodyPartLocation.glutes, 3)
        inhibit = self.get_exercise_dictionary([44])
        static_stretch = self.get_exercise_dictionary([46, 56])
        active_stretch = self.get_exercise_dictionary([116])
        dynamic_stretch = self.get_exercise_dictionary([81])
        isolated_activation = self.get_exercise_dictionary([10, 11, 12, 13, 230, 233, 108, 15])
        glutes.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, [])
        glutes.add_muscle_groups([14], [5, 6, 15], [11], [4])
        return glutes

    def get_calves(self):
        calves = BodyPart(BodyPartLocation.calves, 10)
        inhibit = self.get_exercise_dictionary([2, 71])
        static_stretch = self.get_exercise_dictionary([7, 26, 59, 61])
        active_stretch = self.get_exercise_dictionary([29, 63, 66, 68])
        dynamic_stretch = []
        isolated_activation = self.get_exercise_dictionary([31, 67, 78])
        calves.add_extended_exercise_phases(inhibit, static_stretch, active_stretch, dynamic_stretch, isolated_activation, [])
        calves.add_muscle_groups([16], [9], [17], [8, 9, 10])
        return calves