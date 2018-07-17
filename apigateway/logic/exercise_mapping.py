import logic.exercise as exercise
import logic.soreness_and_injury as soreness_and_injury
import models.exercise
from datastores.exercise_datastore import ExerciseLibraryDatastore


class ExerciseAssignmentCalculator(object):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id
        self.exercise_library = ExerciseLibraryDatastore().get()
        self.exercises_for_body_parts = self.get_exercises_for_body_parts()

    # def create_assigned_exercise(self, target_exercise, body_part_priority, body_part_exercise_priority, body_part_soreness_level):

    def get_exercise_list_for_body_part(self, body_part_exercises, exercise_list, completed_exercises, soreness_severity):

        assigned_exercise_list = []

        for body_part_exercise in body_part_exercises:
            # get details from library
            target_exercise = [ex for ex in exercise_list if ex.id == body_part_exercise.exercise.id]

            # did athlete already complete this exercise
            if completed_exercises is not None:
                completed_exercise = [ex for ex in completed_exercises if
                                      ex.id == target_exercise.id]

            # if completed_exercise is not None:
            # do stuff

            # determine reps and sets
            assigned_exercise = models.exercise.AssignedExercise(target_exercise[0].id,
                                                                 body_part_exercise.body_part_priority,
                                                                 body_part_exercise.body_part_exercise_priority,
                                                                 soreness_severity)
            assigned_exercise.exercise = target_exercise[0]

            assigned_exercise.reps_assigned = target_exercise[0].max_reps
            assigned_exercise.sets_assigned = target_exercise[0].max_sets

            assigned_exercise_list.append(assigned_exercise)

        return assigned_exercise_list

    def create_exercise_assignments(self, exercise_session, soreness_list):

        # TODO: handle progressions

        exercise_assignments = exercise.ExerciseAssignments()
        exercise_assignments.inhibit_max_percentage = exercise_session.inhibit_max_percentage
        exercise_assignments.inhibit_target_minutes = exercise_session.inhibit_target_minutes
        exercise_assignments.activate_max_percentage = exercise_session.activate_max_percentage
        exercise_assignments.activate_target_minutes = exercise_session.activate_target_minutes
        exercise_assignments.lengthen_max_percentage = exercise_session.lengthen_max_percentage
        exercise_assignments.lengthen_target_minutes = exercise_session.lengthen_target_minutes

        completed_exercises = None
        body_part_exercises = self.exercises_for_body_parts
        exercise_list = self.exercise_library

        if soreness_list is not None and len(soreness_list) > 0:
            for soreness in soreness_list:
                body_part = [b for b in body_part_exercises if b.location.value == soreness.body_part.location.value]

                if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                    exercise_assignments.inhibit_exercises.extend(
                        self.get_exercise_list_for_body_part(body_part[0].inhibit_exercises, exercise_list,
                                                             completed_exercises, soreness.severity))
                if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                    exercise_assignments.lengthen_exercises.extend(
                        self.get_exercise_list_for_body_part(body_part[0].lengthen_exercises, exercise_list,
                                                             completed_exercises, soreness.severity))
                if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                    exercise_assignments.activate_exercises.extend(
                        self.get_exercise_list_for_body_part(body_part[0].activate_exercises, exercise_list,
                                                             completed_exercises, soreness.severity))

        else:
            body_part = self.get_general_exercises()

            if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                exercise_assignments.inhibit_exercises.extend(
                    self.get_exercise_list_for_body_part(body_part[0].inhibit_exercises, exercise_list,
                                                         completed_exercises, 0))
            if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                exercise_assignments.lengthen_exercises.extend(
                    self.get_exercise_list_for_body_part(body_part[0].lengthen_exercises, exercise_list,
                                                         completed_exercises, 0))
            if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                exercise_assignments.activate_exercises.extend(
                    self.get_exercise_list_for_body_part(body_part[0].activate_exercises, exercise_list,
                                                         completed_exercises, 0))

        exercise_assignments.scale_to_targets()

        return exercise_assignments

    def get_general_exercises(self):

        body_parts = []

        general = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.general, 15)

        general.inhibit_exercises.append(models.exercise.AssignedExercise("48", general.treatment_priority, 1))
        general.inhibit_exercises.append(models.exercise.AssignedExercise("3", general.treatment_priority, 2))

        it_band = models.exercise.AssignedExercise("4", general.treatment_priority, 3)
        it_band.progressions = ["5"]
        general.inhibit_exercises.append(it_band)

        general.inhibit_exercises.append(models.exercise.AssignedExercise("2", general.treatment_priority, 4))
        general.inhibit_exercises.append(models.exercise.AssignedExercise("44", general.treatment_priority, 5))
        general.inhibit_exercises.append(models.exercise.AssignedExercise("55", general.treatment_priority, 6))

        general.lengthen_exercises.append(models.exercise.AssignedExercise("9", general.treatment_priority, 1))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("6", general.treatment_priority, 2))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("28", general.treatment_priority, 3))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("56", general.treatment_priority, 4))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("103", general.treatment_priority, 5))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("7", general.treatment_priority, 6))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("46", general.treatment_priority, 7))

        glute_activation = models.exercise.AssignedExercise("81", general.treatment_priority, 1)
        glute_activation.progressions = ["82", "83"]
        general.activate_exercises.append(glute_activation)

        hip_bridge_progression = models.exercise.AssignedExercise("10", general.treatment_priority, 2)
        hip_bridge_progression.progressions = ["12", "11", "13"]
        general.activate_exercises.append(hip_bridge_progression)

        core_strength_progression = models.exercise.AssignedExercise("85", general.treatment_priority, 3)
        core_strength_progression.progressions = ["86", "87", "88"]
        general.activate_exercises.append(core_strength_progression)

        posterior_pelvic_tilt = models.exercise.AssignedExercise("79", general.treatment_priority, 4)
        posterior_pelvic_tilt.progressions = ["80"]
        general.activate_exercises.append(posterior_pelvic_tilt)

        core_strength_progression_2 = models.exercise.AssignedExercise("89", general.treatment_priority, 5)
        core_strength_progression_2.progressions = ["90", "91", "92"]
        general.activate_exercises.append(core_strength_progression_2)

        body_parts.append(general)

        return body_parts

    def get_exercises_for_body_parts(self):
        body_parts = []

        # lower back
        lower_back = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.lower_back, 1)
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("55", lower_back.treatment_priority, 1))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("54", lower_back.treatment_priority, 2))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("4", lower_back.treatment_priority, 3))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("5", lower_back.treatment_priority, 4))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("48", lower_back.treatment_priority, 5))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("3", lower_back.treatment_priority, 6))

        lower_back.lengthen_exercises.append(models.exercise.AssignedExercise("49", lower_back.treatment_priority, 1))
        lower_back.lengthen_exercises.append(models.exercise.AssignedExercise("57", lower_back.treatment_priority, 2))
        lower_back.lengthen_exercises.append(models.exercise.AssignedExercise("56", lower_back.treatment_priority, 3))
        lower_back.lengthen_exercises.append(models.exercise.AssignedExercise("8", lower_back.treatment_priority, 4))

        posterior_pelvic_tilt = models.exercise.AssignedExercise("79", lower_back.treatment_priority, 1)
        posterior_pelvic_tilt.progressions = ["80"]

        lower_back.activate_exercises.append(posterior_pelvic_tilt)

        hip_bridge_progression = models.exercise.AssignedExercise("10", lower_back.treatment_priority, 2)
        hip_bridge_progression.progressions = ["12", "11", "13"]

        lower_back.activate_exercises.append(hip_bridge_progression)

        core_strength_progression = models.exercise.AssignedExercise("85", lower_back.treatment_priority, 3)
        core_strength_progression.progressions = ["86", "87", "88", "89", "90", "91", "92"]

        lower_back.activate_exercises.append(core_strength_progression)

        body_parts.append(lower_back)

        # hip

        hip = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.hip_flexor, 2)

        hip.inhibit_exercises.append(models.exercise.AssignedExercise("3", hip.treatment_priority, 1))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("48", hip.treatment_priority, 2))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("54", hip.treatment_priority, 3))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("1", hip.treatment_priority, 4))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("44", hip.treatment_priority, 5))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("4", hip.treatment_priority, 6))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("5", hip.treatment_priority, 7))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("2", hip.treatment_priority, 8))

        hip.lengthen_exercises.append(models.exercise.AssignedExercise("49", hip.treatment_priority, 1))
        hip.lengthen_exercises.append(models.exercise.AssignedExercise("9", hip.treatment_priority, 2))
        hip.lengthen_exercises.append(models.exercise.AssignedExercise("46", hip.treatment_priority, 3))
        hip.lengthen_exercises.append(models.exercise.AssignedExercise("28", hip.treatment_priority, 4))

        posterior_pelvic_tilt = models.exercise.AssignedExercise("79", hip.treatment_priority, 1)
        posterior_pelvic_tilt.progressions = ["80"]

        hip.activate_exercises.append(posterior_pelvic_tilt)

        hip_bridge_progression = models.exercise.AssignedExercise("10", hip.treatment_priority, 2)
        hip_bridge_progression.progressions = ["12", "11", "13"]

        hip.activate_exercises.append(hip_bridge_progression)

        hip.activate_exercises.append(models.exercise.AssignedExercise("50", hip.treatment_priority, 3))
        hip.activate_exercises.append(models.exercise.AssignedExercise("84", hip.treatment_priority, 4))

        glute_activation = models.exercise.AssignedExercise("34", hip.treatment_priority, 5)
        glute_activation.progressions = ["35"]
        hip.activate_exercises.append(glute_activation)

        body_parts.append(hip)

        # glutes

        glutes = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.glutes, 3)

        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("44", glutes.treatment_priority, 1))
        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("3", glutes.treatment_priority, 2))

        it_band = models.exercise.AssignedExercise("4", glutes.treatment_priority, 3)
        it_band.progressions = ["5"]
        glutes.inhibit_exercises.append(it_band)

        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("54", glutes.treatment_priority, 4))
        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("2", glutes.treatment_priority, 5))

        glutes.lengthen_exercises.append(models.exercise.AssignedExercise("9", glutes.treatment_priority, 1))
        glutes.lengthen_exercises.append(models.exercise.AssignedExercise("46", glutes.treatment_priority, 2))

        stretching_erectors = models.exercise.AssignedExercise("103", glutes.treatment_priority, 3)
        stretching_erectors.progressions = ["104"]
        glutes.lengthen_exercises.append(stretching_erectors)

        glutes.lengthen_exercises.append(models.exercise.AssignedExercise("28", glutes.treatment_priority, 4))

        gastroc_soleus = models.exercise.AssignedExercise("25", glutes.treatment_priority, 5)
        gastroc_soleus.progressions = ["26"]
        glutes.lengthen_exercises.append(gastroc_soleus)

        hip_bridge_progression = models.exercise.AssignedExercise("10", glutes.treatment_priority, 1)
        hip_bridge_progression.progressions = ["12", "11", "13"]

        glutes.activate_exercises.append(hip_bridge_progression)

        glute_activation = models.exercise.AssignedExercise("81", glutes.treatment_priority, 2)
        glute_activation.progressions = ["82", "83"]

        glutes.activate_exercises.append(glute_activation)

        glute_activation_2 = models.exercise.AssignedExercise("34", glutes.treatment_priority, 3)
        glute_activation_2.progressions = ["35"]
        glutes.activate_exercises.append(glute_activation_2)

        core_strength_progression = models.exercise.AssignedExercise("85", glutes.treatment_priority, 4)
        core_strength_progression.progressions = ["86", "87", "88"]

        glutes.activate_exercises.append(core_strength_progression)

        core_strength_progression_2 = models.exercise.AssignedExercise("89", glutes.treatment_priority, 5)
        core_strength_progression_2.progressions = ["90", "91", "92"]

        glutes.activate_exercises.append(core_strength_progression_2)

        body_parts.append(glutes)

        # abdominals

        abdominals = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.abdominals, 4)

        abdominals.inhibit_exercises.append(models.exercise.AssignedExercise("102", abdominals.treatment_priority, 1))

        it_band = models.exercise.AssignedExercise("4", abdominals.treatment_priority, 2)
        it_band.progressions = ["5"]
        abdominals.inhibit_exercises.append(it_band)

        abdominals.inhibit_exercises.append(models.exercise.AssignedExercise("54", abdominals.treatment_priority, 3))
        abdominals.inhibit_exercises.append(models.exercise.AssignedExercise("48", abdominals.treatment_priority, 4))

        child_pose = models.exercise.AssignedExercise("103", abdominals.treatment_priority, 1)
        child_pose.progressions = ["104"]
        abdominals.lengthen_exercises.append(child_pose)

        abdominals.lengthen_exercises.append(models.exercise.AssignedExercise("46", glutes.treatment_priority, 2))
        abdominals.lengthen_exercises.append(models.exercise.AssignedExercise("9", glutes.treatment_priority, 3))
        abdominals.lengthen_exercises.append(models.exercise.AssignedExercise("49", glutes.treatment_priority, 4))
        abdominals.lengthen_exercises.append(models.exercise.AssignedExercise("98", glutes.treatment_priority, 5))

        core_strength_progression = models.exercise.AssignedExercise("85", abdominals.treatment_priority, 1)
        core_strength_progression.progressions = ["86", "87", "88"]
        abdominals.activate_exercises.append(core_strength_progression)

        core_strength_progression_2 = models.exercise.AssignedExercise("89", abdominals.treatment_priority, 2)
        core_strength_progression_2.progressions = ["90", "91", "92"]
        abdominals.activate_exercises.append(core_strength_progression_2)

        hip_bridge_progression = models.exercise.AssignedExercise("10", abdominals.treatment_priority, 3)
        hip_bridge_progression.progressions = ["12", "11", "13"]
        abdominals.activate_exercises.append(hip_bridge_progression)

        glute_activation = models.exercise.AssignedExercise("81", abdominals.treatment_priority, 4)
        glute_activation.progressions = ["82", "83"]

        abdominals.activate_exercises.append(glute_activation)

        body_parts.append(abdominals)

        # hamstrings

        hamstrings = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.hamstrings, 5)

        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("3", hamstrings.treatment_priority, 1))
        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("44", hamstrings.treatment_priority, 2))

        it_band = models.exercise.AssignedExercise("4", hamstrings.treatment_priority, 3)
        it_band.progressions = ["5"]
        hamstrings.inhibit_exercises.append(it_band)

        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("54", hamstrings.treatment_priority, 4))
        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("1", hamstrings.treatment_priority, 5))
        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("2", hamstrings.treatment_priority, 6))

        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("9", hamstrings.treatment_priority, 1))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("46", hamstrings.treatment_priority, 2))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("28", hamstrings.treatment_priority, 3))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("49", hamstrings.treatment_priority, 4))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("8", hamstrings.treatment_priority, 5))
        # hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("55", hamstrings.treatment_priority, 6))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("98", hamstrings.treatment_priority, 6))

        gastroc_soleus = models.exercise.AssignedExercise("25", hamstrings.treatment_priority, 7)
        gastroc_soleus.progressions = ["26"]
        hamstrings.lengthen_exercises.append(gastroc_soleus)

        glute_max_activation = models.exercise.AssignedExercise("34", hamstrings.treatment_priority, 1)
        glute_max_activation.progressions = ["35"]
        hamstrings.activate_exercises.append(glute_max_activation)

        glute_activation = models.exercise.AssignedExercise("81", hamstrings.treatment_priority, 2)
        glute_activation.progressions = ["82", "83"]
        hamstrings.activate_exercises.append(glute_activation)

        hamstrings.activate_exercises.append(models.exercise.AssignedExercise("47", hamstrings.treatment_priority, 3))
        hamstrings.activate_exercises.append(models.exercise.AssignedExercise("29", hamstrings.treatment_priority, 4))

        core_strength_progression = models.exercise.AssignedExercise("85", hamstrings.treatment_priority, 5)
        core_strength_progression.progressions = ["86", "87", "88"]
        hamstrings.activate_exercises.append(core_strength_progression)

        core_strength_progression_2 = models.exercise.AssignedExercise("89", hamstrings.treatment_priority, 6)
        core_strength_progression_2.progressions = ["90", "91", "92"]
        hamstrings.activate_exercises.append(core_strength_progression_2)

        body_parts.append(hamstrings)

        # outer_thigh

        outer_thigh = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.outer_thigh, 6)

        outer_thigh.inhibit_exercises.append(models.exercise.AssignedExercise("48", outer_thigh.treatment_priority, 1))

        it_band = models.exercise.AssignedExercise("4", outer_thigh.treatment_priority, 2)
        it_band.progressions = ["5"]
        outer_thigh.inhibit_exercises.append(it_band)

        outer_thigh.inhibit_exercises.append(models.exercise.AssignedExercise("1", outer_thigh.treatment_priority, 3))
        outer_thigh.inhibit_exercises.append(models.exercise.AssignedExercise("2", outer_thigh.treatment_priority, 4))

        outer_thigh.lengthen_exercises.append(models.exercise.AssignedExercise("28", outer_thigh.treatment_priority, 1))
        outer_thigh.lengthen_exercises.append(models.exercise.AssignedExercise("6", outer_thigh.treatment_priority, 2))
        outer_thigh.lengthen_exercises.append(models.exercise.AssignedExercise("8", outer_thigh.treatment_priority, 3))
        outer_thigh.lengthen_exercises.append(models.exercise.AssignedExercise("7", outer_thigh.treatment_priority, 4))

        glute_max_activation = models.exercise.AssignedExercise("34", outer_thigh.treatment_priority, 1)
        glute_max_activation.progressions = ["35"]
        outer_thigh.activate_exercises.append(glute_max_activation)

        outer_thigh.activate_exercises.append(models.exercise.AssignedExercise("32", outer_thigh.treatment_priority, 2))

        hip_bridge_progression = models.exercise.AssignedExercise("10", outer_thigh.treatment_priority, 3)
        hip_bridge_progression.progressions = ["12", "11", "13"]
        outer_thigh.activate_exercises.append(hip_bridge_progression)

        # outer_thigh.activate_exercises.append(models.exercise.AssignedExercise("77", outer_thigh.treatment_priority, 4))

        body_parts.append(outer_thigh)

        # groin

        groin = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.groin, 7)

        groin.inhibit_exercises.append(models.exercise.AssignedExercise("54", groin.treatment_priority, 1))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("1", groin.treatment_priority, 2))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("102", groin.treatment_priority, 3))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("55", groin.treatment_priority, 4))

        it_band = models.exercise.AssignedExercise("4", groin.treatment_priority, 5)
        it_band.progressions = ["5"]
        groin.inhibit_exercises.append(it_band)

        groin.inhibit_exercises.append(models.exercise.AssignedExercise("44", groin.treatment_priority, 6))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("3", groin.treatment_priority, 7))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("2", groin.treatment_priority, 8))

        groin.lengthen_exercises.append(models.exercise.AssignedExercise("103", groin.treatment_priority, 1))
        # groin.lengthen_exercises.append(models.exercise.AssignedExercise("55", groin.treatment_priority, 2))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("8", groin.treatment_priority, 2))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("28", groin.treatment_priority, 3))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("49", groin.treatment_priority, 4))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("98", groin.treatment_priority, 5))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("46", groin.treatment_priority, 6))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("9", groin.treatment_priority, 7))

        gastroc_soleus = models.exercise.AssignedExercise("25", groin.treatment_priority, 8)
        gastroc_soleus.progressions = ["26"]
        groin.lengthen_exercises.append(gastroc_soleus)

        groin.activate_exercises.append(models.exercise.AssignedExercise("50", groin.treatment_priority, 1))
        groin.activate_exercises.append(models.exercise.AssignedExercise("84", groin.treatment_priority, 2))

        posterior_pelvic_tilt = models.exercise.AssignedExercise("79", groin.treatment_priority, 3)
        posterior_pelvic_tilt.progressions = ["80"]
        groin.activate_exercises.append(posterior_pelvic_tilt)

        glute_activation = models.exercise.AssignedExercise("81", groin.treatment_priority, 4)
        glute_activation.progressions = ["82", "83"]
        groin.activate_exercises.append(glute_activation)

        core_strength_progression = models.exercise.AssignedExercise("85", groin.treatment_priority, 5)
        core_strength_progression.progressions = ["86", "87", "88"]
        groin.activate_exercises.append(core_strength_progression)

        core_strength_progression_2 = models.exercise.AssignedExercise("89", groin.treatment_priority, 6)
        core_strength_progression_2.progressions = ["90", "91", "92"]
        groin.activate_exercises.append(core_strength_progression_2)

        body_parts.append(groin)

        # quads

        quads = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.quads, 8)

        quads.inhibit_exercises.append(models.exercise.AssignedExercise("54", quads.treatment_priority, 1))
        quads.inhibit_exercises.append(models.exercise.AssignedExercise("1", quads.treatment_priority, 2))

        it_band = models.exercise.AssignedExercise("4", quads.treatment_priority, 3)
        it_band.progressions = ["5"]
        quads.inhibit_exercises.append(it_band)

        quads.inhibit_exercises.append(models.exercise.AssignedExercise("44", quads.treatment_priority, 4))
        quads.inhibit_exercises.append(models.exercise.AssignedExercise("3", quads.treatment_priority, 5))
        quads.inhibit_exercises.append(models.exercise.AssignedExercise("2", quads.treatment_priority, 6))

        quads.lengthen_exercises.append(models.exercise.AssignedExercise("49", quads.treatment_priority, 1))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("8", quads.treatment_priority, 2))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("28", quads.treatment_priority, 3))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("98", quads.treatment_priority, 4))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("46", quads.treatment_priority, 5))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("9", quads.treatment_priority, 6))

        gastroc_soleus = models.exercise.AssignedExercise("25", quads.treatment_priority, 7)
        gastroc_soleus.progressions = ["26"]
        quads.lengthen_exercises.append(gastroc_soleus)

        quads.activate_exercises.append(models.exercise.AssignedExercise("84", quads.treatment_priority, 1))
        # quads.activate_exercises.append(models.exercise.AssignedExercise("76", quads.treatment_priority, 2))
        quads.activate_exercises.append(models.exercise.AssignedExercise("47", quads.treatment_priority, 3))

        glute_max_activation = models.exercise.AssignedExercise("34", quads.treatment_priority, 4)
        glute_max_activation.progressions = ["35"]
        quads.activate_exercises.append(glute_max_activation)

        quads.activate_exercises.append(models.exercise.AssignedExercise("29", quads.treatment_priority, 5))

        body_parts.append(quads)

        # knee

        knee = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.knee, 9)

        it_band = models.exercise.AssignedExercise("4", knee.treatment_priority, 1)
        it_band.progressions = ["5"]
        knee.inhibit_exercises.append(it_band)

        knee.inhibit_exercises.append(models.exercise.AssignedExercise("54", knee.treatment_priority, 2))
        knee.inhibit_exercises.append(models.exercise.AssignedExercise("1", knee.treatment_priority, 3))

        knee.lengthen_exercises.append(models.exercise.AssignedExercise("28", knee.treatment_priority, 1))
        knee.lengthen_exercises.append(models.exercise.AssignedExercise("6", knee.treatment_priority, 2))
        knee.lengthen_exercises.append(models.exercise.AssignedExercise("9", knee.treatment_priority, 3))

        gastroc_soleus = models.exercise.AssignedExercise("25", knee.treatment_priority, 4)
        gastroc_soleus.progressions = ["26"]
        knee.lengthen_exercises.append(gastroc_soleus)

        knee.activate_exercises.append(models.exercise.AssignedExercise("29", knee.treatment_priority, 1))
        knee.activate_exercises.append(models.exercise.AssignedExercise("30", knee.treatment_priority, 2))
        # knee.activate_exercises.append(models.exercise.AssignedExercise("77", knee.treatment_priority, 3))
        knee.activate_exercises.append(models.exercise.AssignedExercise("32", knee.treatment_priority, 4))

        body_parts.append(knee)

        # calves

        calves = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.calves, 10)

        calves.inhibit_exercises.append(models.exercise.AssignedExercise("2", calves.treatment_priority, 1))
        calves.inhibit_exercises.append(models.exercise.AssignedExercise("71", calves.treatment_priority, 2))
        calves.inhibit_exercises.append(models.exercise.AssignedExercise("3", calves.treatment_priority, 3))

        gastroc_soleus = models.exercise.AssignedExercise("25", calves.treatment_priority, 1)
        gastroc_soleus.progressions = ["26"]
        calves.lengthen_exercises.append(gastroc_soleus)

        calves.lengthen_exercises.append(models.exercise.AssignedExercise("9", calves.treatment_priority, 2))

        ankle_plantarflexion = models.exercise.AssignedExercise("30", calves.treatment_priority, 1)
        ankle_plantarflexion.progressions = ["66"]
        calves.activate_exercises.append(ankle_plantarflexion)

        ankle_dorsiflexion = models.exercise.AssignedExercise("29", calves.treatment_priority, 2)
        ankle_dorsiflexion.progressions = ["65"]
        calves.activate_exercises.append(ankle_dorsiflexion)

        body_parts.append(calves)

        # shin

        shin = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.shin, 11)

        shin.inhibit_exercises.append(models.exercise.AssignedExercise("1", shin.treatment_priority, 1))
        shin.inhibit_exercises.append(models.exercise.AssignedExercise("2", shin.treatment_priority, 2))

        shin.lengthen_exercises.append(models.exercise.AssignedExercise("73", shin.treatment_priority, 1))

        gastroc_soleus = models.exercise.AssignedExercise("25", shin.treatment_priority, 2)
        gastroc_soleus.progressions = ["26"]
        shin.lengthen_exercises.append(gastroc_soleus)

        shin.lengthen_exercises.append(models.exercise.AssignedExercise("28", shin.treatment_priority, 3))
        shin.lengthen_exercises.append(models.exercise.AssignedExercise("9", shin.treatment_priority, 4))

        shin.activate_exercises.append(models.exercise.AssignedExercise("29", shin.treatment_priority, 1))
        shin.activate_exercises.append(models.exercise.AssignedExercise("30", shin.treatment_priority, 2))
        shin.activate_exercises.append(models.exercise.AssignedExercise("31", shin.treatment_priority, 3))

        body_parts.append(shin)

        # ankle

        ankle = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.ankle, 12)

        ankle.inhibit_exercises.append(models.exercise.AssignedExercise("2", ankle.treatment_priority, 1))
        ankle.inhibit_exercises.append(models.exercise.AssignedExercise("71", ankle.treatment_priority, 2))
        ankle.inhibit_exercises.append(models.exercise.AssignedExercise("3", ankle.treatment_priority, 3))

        ankle.lengthen_exercises.append(models.exercise.AssignedExercise("7", ankle.treatment_priority, 1))
        ankle.lengthen_exercises.append(models.exercise.AssignedExercise("72", ankle.treatment_priority, 2))
        ankle.lengthen_exercises.append(models.exercise.AssignedExercise("73", ankle.treatment_priority, 3))

        ankle_progression = models.exercise.AssignedExercise("59", ankle.treatment_priority, 1)
        ankle_progression.progressions = ["60", "61", "62"]
        ankle.activate_exercises.append(ankle_progression)

        ankle_progression_2 = models.exercise.AssignedExercise("29", ankle.treatment_priority, 2)
        ankle_progression_2.progressions = ["30", "63", "64"]
        ankle.activate_exercises.append(ankle_progression_2)

        ankle_progression_3 = models.exercise.AssignedExercise("65", ankle.treatment_priority, 3)
        ankle_progression_3.progressions = ["66"]
        ankle.activate_exercises.append(ankle_progression_3)

        body_parts.append(ankle)

        # foot

        foot = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.foot, 13)

        foot.inhibit_exercises.append(models.exercise.AssignedExercise("74", foot.treatment_priority, 1))
        foot.inhibit_exercises.append(models.exercise.AssignedExercise("2", foot.treatment_priority, 2))
        foot.inhibit_exercises.append(models.exercise.AssignedExercise("71", foot.treatment_priority, 3))
        foot.inhibit_exercises.append(models.exercise.AssignedExercise("3", foot.treatment_priority, 4))

        foot.lengthen_exercises.append(models.exercise.AssignedExercise("7", foot.treatment_priority, 1))
        foot.lengthen_exercises.append(models.exercise.AssignedExercise("73", foot.treatment_priority, 2))
        foot.lengthen_exercises.append(models.exercise.AssignedExercise("9", foot.treatment_priority, 3))

        foot.activate_exercises.append(models.exercise.AssignedExercise("53", foot.treatment_priority, 1))
        foot.activate_exercises.append(models.exercise.AssignedExercise("75", foot.treatment_priority, 2))

        ankle_progression_2 = models.exercise.AssignedExercise("29", foot.treatment_priority, 3)
        ankle_progression_2.progressions = ["30", "63", "64"]
        foot.activate_exercises.append(ankle_progression_2)

        ankle_progression_3 = models.exercise.AssignedExercise("65", foot.treatment_priority, 4)
        ankle_progression_3.progressions = ["66"]
        foot.activate_exercises.append(ankle_progression_3)

        body_parts.append(foot)

        # achilles

        achilles = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.achilles, 14)

        achilles.inhibit_exercises.append(models.exercise.AssignedExercise("2", achilles.treatment_priority, 2))
        achilles.inhibit_exercises.append(models.exercise.AssignedExercise("71", achilles.treatment_priority, 3))
        achilles.inhibit_exercises.append(models.exercise.AssignedExercise("3", achilles.treatment_priority, 3))

        achilles.lengthen_exercises.append(models.exercise.AssignedExercise("7", achilles.treatment_priority, 1))
        achilles.lengthen_exercises.append(models.exercise.AssignedExercise("9", achilles.treatment_priority, 2))

        achilles.activate_exercises.append(models.exercise.AssignedExercise("29", achilles.treatment_priority, 1))
        achilles.activate_exercises.append(models.exercise.AssignedExercise("78", achilles.treatment_priority, 2))

        glute_max_activation = models.exercise.AssignedExercise("34", achilles.treatment_priority, 3)
        glute_max_activation.progressions = ["35"]
        achilles.activate_exercises.append(glute_max_activation)

        # achilles.activate_exercises.append(models.exercise.AssignedExercise("77", achilles.treatment_priority, 4))

        body_parts.append(achilles)

        return body_parts

