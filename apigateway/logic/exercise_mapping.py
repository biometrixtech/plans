import models.soreness
from logic.exercise_generator import ExerciseAssignments
import logic.soreness_processing as soreness_and_injury
import models.exercise
from logic.goal_focus_text_generator import RecoveryTextGenerator
from datetime import  timedelta


class ExerciseAssignmentCalculator(object):

    def __init__(self, athlete_id, exercise_library_datastore, completed_exercise_datastore):
        self.athlete_id = athlete_id
        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        self.exercises_for_body_parts = self.get_exercises_for_body_parts()


    # def create_assigned_exercise(self, target_exercise, body_part_priority, body_part_exercise_priority, body_part_soreness_level):

    def get_exercise_list_for_body_part(self, body_part_exercises, exercise_list, completed_exercises, soreness_severity):

        assigned_exercise_list = []

        for body_part_exercise in body_part_exercises:

            #has athlete completed enough exposures for this exercise?
            target_exercise = self.get_current_exercise(body_part_exercise, self.exercise_library, completed_exercises)

            # determine reps and sets
            assigned_exercise = models.exercise.AssignedExercise(target_exercise.id,
                                                                 body_part_exercise.body_part_priority,
                                                                 body_part_exercise.body_part_exercise_priority,
                                                                 soreness_severity
                                                                 )
            assigned_exercise.exercise = target_exercise

            assigned_exercise.reps_assigned = target_exercise.max_reps
            assigned_exercise.sets_assigned = target_exercise.max_sets

            assigned_exercise_list.append(assigned_exercise)

        return assigned_exercise_list

    def create_exercise_assignments(self, exercise_session, soreness_list, trigger_date_time):

        # TODO: handle progressions

        text_generator = RecoveryTextGenerator()

        exercise_assignments = ExerciseAssignments()
        exercise_assignments.inhibit_max_percentage = exercise_session.inhibit_max_percentage
        exercise_assignments.inhibit_target_minutes = exercise_session.inhibit_target_minutes
        exercise_assignments.activate_max_percentage = exercise_session.activate_max_percentage
        exercise_assignments.activate_target_minutes = exercise_session.activate_target_minutes
        exercise_assignments.lengthen_max_percentage = exercise_session.lengthen_max_percentage
        exercise_assignments.lengthen_target_minutes = exercise_session.lengthen_target_minutes

        completed_exercises = self.completed_exercise_datastore.get(self.athlete_id,
                                                                    trigger_date_time - timedelta(30),
                                                                    trigger_date_time,
                                                                    get_summary=True)
        body_part_exercises = self.exercises_for_body_parts
        exercise_list = self.exercise_library

        if soreness_list is not None and len(soreness_list) > 0:
            for soreness in soreness_list:
                body_part = [b for b in body_part_exercises if b.location.value == soreness.body_part.location.value]

                if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                    new_assignments = self.get_exercise_list_for_body_part(body_part[0].inhibit_exercises, exercise_list,
                                                                           completed_exercises, soreness.severity)
                    for e in range(0, len(new_assignments)):
                        new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(soreness.severity,
                                                                                                 models.exercise.Phase.inhibit,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.inhibit_exercises.extend(new_assignments)

                if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                    new_assignments = self.get_exercise_list_for_body_part(body_part[0].lengthen_exercises, exercise_list,
                                                                           completed_exercises, soreness.severity)

                    for e in range(0, len(new_assignments)):
                        new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(soreness.severity,
                                                                                                 models.exercise.Phase.lengthen,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.lengthen_exercises.extend(new_assignments)
                if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                    new_assignments = self.get_exercise_list_for_body_part(body_part[0].activate_exercises, exercise_list,
                                                                           completed_exercises, soreness.severity)
                    for e in range(0, len(new_assignments)):
                        new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(soreness.severity,
                                                                                                 models.exercise.Phase.activate,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.activate_exercises.extend(new_assignments)

        else:
            body_part = self.get_general_exercises()

            if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part[0].inhibit_exercises, exercise_list,
                                                         completed_exercises, 0)

                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             models.exercise.Phase.inhibit,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.inhibit_exercises.extend(new_assignments)
            if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part[0].lengthen_exercises, exercise_list,
                                                         completed_exercises, 0)
                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             models.exercise.Phase.lengthen,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.lengthen_exercises.extend(new_assignments)
            if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part[0].activate_exercises, exercise_list,
                                                         completed_exercises, 0)

                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             models.exercise.Phase.activate,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.activate_exercises.extend(new_assignments)

        exercise_assignments.scale_to_targets()

        return exercise_assignments

    def get_current_exercise(self, body_part_exercise, exercise_list, completed_exercises):

        target_exercise_list = [ex for ex in exercise_list if ex.id == body_part_exercise.exercise.id]
        target_exercise = target_exercise_list[0]

        if len(body_part_exercise.exercise.progressions) == 0:
            return target_exercise
        else:
            completed_exercise_list = [ex for ex in completed_exercises if ex.exercise_id == body_part_exercise.exercise.id]
            if len(completed_exercise_list) == 0:
                return target_exercise
            else:
                if completed_exercise_list[0].exposures >= target_exercise.exposure_target:
                    # now work through progressions...

                    for p in range(len(body_part_exercise.exercise.progressions) - 1, -1, -1):
                        completed_progression_list = [ex for ex in completed_exercises if
                                                      ex.exercise_id == body_part_exercise.exercise.progressions[p]]
                        proposed_exercise_list = [ex for ex in exercise_list if ex.id == body_part_exercise.exercise.progressions[p]]
                        proposed_exercise = proposed_exercise_list[0]
                        if len(completed_progression_list) == 0: # haven't done this
                            if len(body_part_exercise.exercise.progressions) == 1:
                                return proposed_exercise
                            else:
                                # haven't dont anything with this exercise yet, keep working our way down
                                continue
                        elif completed_progression_list[0].exposures >= proposed_exercise.exposure_target:
                            # return next progression
                            if p < (len(body_part_exercise.exercise.progressions) - 1):
                                proposed_exercise_list = [ex for ex in exercise_list if
                                                          ex.id == body_part_exercise.exercise.progressions[p + 1]]
                                proposed_exercise = proposed_exercise_list[0]
                                return proposed_exercise
                            else:
                                return proposed_exercise
                        else:
                            return proposed_exercise
                else:
                    return target_exercise

    def get_general_exercises(self):

        body_parts = []

        general = models.soreness.BodyPart(models.soreness.BodyPartLocation.general, 15)

        general.inhibit_exercises.append(models.exercise.AssignedExercise("48", general.treatment_priority, 1))
        general.inhibit_exercises.append(models.exercise.AssignedExercise("3", general.treatment_priority, 2))
        general.inhibit_exercises.append(models.exercise.AssignedExercise("4", general.treatment_priority, 3))
        general.inhibit_exercises.append(models.exercise.AssignedExercise("54", general.treatment_priority, 4))

        # it_band = models.exercise.AssignedExercise("4", general.treatment_priority, 3)
        # it_band.progressions = ["5"]
        # general.inhibit_exercises.append(it_band)

        general.inhibit_exercises.append(models.exercise.AssignedExercise("2", general.treatment_priority, 5))
        general.inhibit_exercises.append(models.exercise.AssignedExercise("44", general.treatment_priority, 6))
        general.inhibit_exercises.append(models.exercise.AssignedExercise("55", general.treatment_priority, 7))

        general.lengthen_exercises.append(models.exercise.AssignedExercise("9", general.treatment_priority, 1))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("6", general.treatment_priority, 2))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("28", general.treatment_priority, 3))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("56", general.treatment_priority, 4))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("103", general.treatment_priority, 5))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("7", general.treatment_priority, 6))
        general.lengthen_exercises.append(models.exercise.AssignedExercise("46", general.treatment_priority, 7))

        glute_activation = models.exercise.AssignedExercise("81", general.treatment_priority, 1)
        glute_activation.exercise.progressions = ["110", "82", "83"]
        general.activate_exercises.append(glute_activation)

        hip_bridge_progression = models.exercise.AssignedExercise("10", general.treatment_priority, 2)
        hip_bridge_progression.exercise.progressions = ["12", "11", "13"]
        general.activate_exercises.append(hip_bridge_progression)

        core_strength_progression = models.exercise.AssignedExercise("85", general.treatment_priority, 3)
        core_strength_progression.exercise.progressions = ["86", "87", "88", "89", "90", "91", "92"]
        general.activate_exercises.append(core_strength_progression)

        general.activate_exercises.append(models.exercise.AssignedExercise("50", general.treatment_priority, 4))

        posterior_pelvic_tilt = models.exercise.AssignedExercise("79", general.treatment_priority, 5)
        posterior_pelvic_tilt.exercise.progressions = ["80"]
        general.activate_exercises.append(posterior_pelvic_tilt)

        body_parts.append(general)

        return body_parts

    def get_exercises_for_body_parts(self):
        body_parts = []

        # lower back
        lower_back = models.soreness.BodyPart(models.soreness.BodyPartLocation.lower_back, 1)

        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("55", lower_back.treatment_priority, 1))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("54", lower_back.treatment_priority, 2))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("4", lower_back.treatment_priority, 3))
        # lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("5", lower_back.treatment_priority, 4))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("48", lower_back.treatment_priority, 4))
        lower_back.inhibit_exercises.append(models.exercise.AssignedExercise("3", lower_back.treatment_priority, 5))

        lower_back.lengthen_exercises.append(models.exercise.AssignedExercise("49", lower_back.treatment_priority, 1))
        lower_back.lengthen_exercises.append(models.exercise.AssignedExercise("57", lower_back.treatment_priority, 2))
        lower_back.lengthen_exercises.append(models.exercise.AssignedExercise("56", lower_back.treatment_priority, 3))
        lower_back.lengthen_exercises.append(models.exercise.AssignedExercise("8", lower_back.treatment_priority, 4))

        posterior_pelvic_tilt = models.exercise.AssignedExercise("79", lower_back.treatment_priority, 1)
        posterior_pelvic_tilt.exercise.progressions = ["80"]
        lower_back.activate_exercises.append(posterior_pelvic_tilt)

        hip_bridge_progression = models.exercise.AssignedExercise("10", lower_back.treatment_priority, 2)
        hip_bridge_progression.exercise.progressions = ["12", "11", "13"]
        lower_back.activate_exercises.append(hip_bridge_progression)

        core_strength_progression = models.exercise.AssignedExercise("85", lower_back.treatment_priority, 3)
        core_strength_progression.exercise.progressions = ["86", "87", "88", "89", "90", "91", "92"]
        lower_back.activate_exercises.append(core_strength_progression)

        body_parts.append(lower_back)

        # hip

        hip = models.soreness.BodyPart(models.soreness.BodyPartLocation.hip_flexor, 2)

        hip.inhibit_exercises.append(models.exercise.AssignedExercise("3", hip.treatment_priority, 1))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("48", hip.treatment_priority, 2))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("54", hip.treatment_priority, 3))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("1", hip.treatment_priority, 4))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("44", hip.treatment_priority, 5))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("4", hip.treatment_priority, 6))
        # hip.inhibit_exercises.append(models.exercise.AssignedExercise("5", hip.treatment_priority, 7))
        hip.inhibit_exercises.append(models.exercise.AssignedExercise("2", hip.treatment_priority, 7))

        hip.lengthen_exercises.append(models.exercise.AssignedExercise("49", hip.treatment_priority, 1))
        hip.lengthen_exercises.append(models.exercise.AssignedExercise("9", hip.treatment_priority, 2))
        hip.lengthen_exercises.append(models.exercise.AssignedExercise("46", hip.treatment_priority, 3))
        hip.lengthen_exercises.append(models.exercise.AssignedExercise("28", hip.treatment_priority, 4))

        posterior_pelvic_tilt = models.exercise.AssignedExercise("79", hip.treatment_priority, 1)
        posterior_pelvic_tilt.exercise.progressions = ["80"]
        hip.activate_exercises.append(posterior_pelvic_tilt)

        hip_bridge_progression = models.exercise.AssignedExercise("10", hip.treatment_priority, 2)
        hip_bridge_progression.exercise.progressions = ["12", "11", "13"]
        hip.activate_exercises.append(hip_bridge_progression)

        hip.activate_exercises.append(models.exercise.AssignedExercise("50", hip.treatment_priority, 3))
        hip.activate_exercises.append(models.exercise.AssignedExercise("84", hip.treatment_priority, 4))
        hip.activate_exercises.append(models.exercise.AssignedExercise("108", hip.treatment_priority, 5))

        # glute_activation = models.exercise.AssignedExercise("34", hip.treatment_priority, 5)
        # glute_activation.exercise.progressions = ["35"]
        # hip.activate_exercises.append(glute_activation)

        body_parts.append(hip)

        # glutes

        glutes = models.soreness.BodyPart(models.soreness.BodyPartLocation.glutes, 3)

        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("44", glutes.treatment_priority, 1))
        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("3", glutes.treatment_priority, 2))
        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("4", glutes.treatment_priority, 3))

        # it_band = models.exercise.AssignedExercise("4", glutes.treatment_priority, 3)
        # it_band.exercise.progressions = ["5"]
        # glutes.inhibit_exercises.append(it_band)

        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("54", glutes.treatment_priority, 4))
        glutes.inhibit_exercises.append(models.exercise.AssignedExercise("2", glutes.treatment_priority, 5))

        glutes.lengthen_exercises.append(models.exercise.AssignedExercise("9", glutes.treatment_priority, 1))
        glutes.lengthen_exercises.append(models.exercise.AssignedExercise("46", glutes.treatment_priority, 2))

        stretching_erectors = models.exercise.AssignedExercise("103", glutes.treatment_priority, 3)
        stretching_erectors.exercise.progressions = ["104"]
        glutes.lengthen_exercises.append(stretching_erectors)

        glutes.lengthen_exercises.append(models.exercise.AssignedExercise("28", glutes.treatment_priority, 4))
        glutes.lengthen_exercises.append(models.exercise.AssignedExercise("7", glutes.treatment_priority, 5))

        hip_bridge_progression = models.exercise.AssignedExercise("10", glutes.treatment_priority, 1)
        hip_bridge_progression.exercise.progressions = ["12", "11", "13"]
        glutes.activate_exercises.append(hip_bridge_progression)

        glute_activation = models.exercise.AssignedExercise("81", glutes.treatment_priority, 2)
        glute_activation.exercise.progressions = ["110", "82", "83"]
        glutes.activate_exercises.append(glute_activation)

        glutes.activate_exercises.append(models.exercise.AssignedExercise("108", glutes.treatment_priority, 3))
        glutes.activate_exercises.append(models.exercise.AssignedExercise("50", glutes.treatment_priority, 4))

        # glute_activation_2 = models.exercise.AssignedExercise("34", glutes.treatment_priority, 3)
        # glute_activation_2.exercise.progressions = ["35"]
        # glutes.activate_exercises.append(glute_activation_2)

        core_strength_progression = models.exercise.AssignedExercise("85", glutes.treatment_priority, 5)
        core_strength_progression.exercise.progressions = ["86", "87", "88", "89", "90", "91", "92"]
        glutes.activate_exercises.append(core_strength_progression)

        body_parts.append(glutes)

        # abdominals

        abdominals = models.soreness.BodyPart(models.soreness.BodyPartLocation.abdominals, 4)

        abdominals.inhibit_exercises.append(models.exercise.AssignedExercise("102", abdominals.treatment_priority, 1))
        abdominals.inhibit_exercises.append(models.exercise.AssignedExercise("4", abdominals.treatment_priority, 2))

        # it_band = models.exercise.AssignedExercise("4", abdominals.treatment_priority, 2)
        # it_band.exercise.progressions = ["5"]
        # abdominals.inhibit_exercises.append(it_band)

        abdominals.inhibit_exercises.append(models.exercise.AssignedExercise("54", abdominals.treatment_priority, 3))
        abdominals.inhibit_exercises.append(models.exercise.AssignedExercise("48", abdominals.treatment_priority, 4))

        child_pose = models.exercise.AssignedExercise("103", abdominals.treatment_priority, 1)
        child_pose.exercise.progressions = ["104"]
        abdominals.lengthen_exercises.append(child_pose)

        abdominals.lengthen_exercises.append(models.exercise.AssignedExercise("46", glutes.treatment_priority, 2))
        abdominals.lengthen_exercises.append(models.exercise.AssignedExercise("9", glutes.treatment_priority, 3))
        abdominals.lengthen_exercises.append(models.exercise.AssignedExercise("49", glutes.treatment_priority, 4))
        abdominals.lengthen_exercises.append(models.exercise.AssignedExercise("98", glutes.treatment_priority, 5))

        core_strength_progression = models.exercise.AssignedExercise("85", abdominals.treatment_priority, 1)
        core_strength_progression.exercise.progressions = ["86", "87", "88", "89", "90", "91", "92"]
        abdominals.activate_exercises.append(core_strength_progression)

        abdominals.activate_exercises.append(models.exercise.AssignedExercise("50", glutes.treatment_priority, 2))

        hip_bridge_progression = models.exercise.AssignedExercise("10", abdominals.treatment_priority, 3)
        hip_bridge_progression.exercise.progressions = ["12", "11", "13"]
        abdominals.activate_exercises.append(hip_bridge_progression)

        glute_activation = models.exercise.AssignedExercise("81", abdominals.treatment_priority, 4)
        glute_activation.exercise.progressions = ["110", "82", "83"]
        abdominals.activate_exercises.append(glute_activation)

        body_parts.append(abdominals)

        # hamstrings

        hamstrings = models.soreness.BodyPart(models.soreness.BodyPartLocation.hamstrings, 5)

        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("3", hamstrings.treatment_priority, 1))
        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("44", hamstrings.treatment_priority, 2))
        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("4", hamstrings.treatment_priority, 3))

        # it_band = models.exercise.AssignedExercise("4", hamstrings.treatment_priority, 3)
        # it_band.exercise.progressions = ["5"]
        # hamstrings.inhibit_exercises.append(it_band)

        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("54", hamstrings.treatment_priority, 4))
        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("1", hamstrings.treatment_priority, 5))
        hamstrings.inhibit_exercises.append(models.exercise.AssignedExercise("2", hamstrings.treatment_priority, 6))

        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("9", hamstrings.treatment_priority, 1))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("46", hamstrings.treatment_priority, 2))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("28", hamstrings.treatment_priority, 3))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("49", hamstrings.treatment_priority, 4))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("8", hamstrings.treatment_priority, 5))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("98", hamstrings.treatment_priority, 6))
        hamstrings.lengthen_exercises.append(models.exercise.AssignedExercise("7", hamstrings.treatment_priority, 7))

        # glute_max_activation = models.exercise.AssignedExercise("34", hamstrings.treatment_priority, 1)
        # glute_max_activation.exercise.progressions = ["35"]
        # hamstrings.activate_exercises.append(glute_max_activation)

        hamstrings.activate_exercises.append(models.exercise.AssignedExercise("108", hamstrings.treatment_priority, 1))

        glute_activation = models.exercise.AssignedExercise("81", hamstrings.treatment_priority, 2)
        glute_activation.exercise.progressions = ["110", "82", "83"]
        hamstrings.activate_exercises.append(glute_activation)

        # hamstrings.activate_exercises.append(models.exercise.AssignedExercise("47", hamstrings.treatment_priority, 3))
        hamstrings.activate_exercises.append(models.exercise.AssignedExercise("115", hamstrings.treatment_priority, 3))

        core_strength_progression = models.exercise.AssignedExercise("85", hamstrings.treatment_priority, 4)
        core_strength_progression.exercise.progressions = ["86", "87", "88", "89", "90", "91", "92"]
        hamstrings.activate_exercises.append(core_strength_progression)

        body_parts.append(hamstrings)

        # outer_thigh

        outer_thigh = models.soreness.BodyPart(models.soreness.BodyPartLocation.outer_thigh, 6)

        outer_thigh.inhibit_exercises.append(models.exercise.AssignedExercise("48", outer_thigh.treatment_priority, 1))
        outer_thigh.inhibit_exercises.append(models.exercise.AssignedExercise("4", outer_thigh.treatment_priority, 2))

        # it_band = models.exercise.AssignedExercise("4", outer_thigh.treatment_priority, 2)
        # it_band.exercise.progressions = ["5"]
        # outer_thigh.inhibit_exercises.append(it_band)

        outer_thigh.inhibit_exercises.append(models.exercise.AssignedExercise("1", outer_thigh.treatment_priority, 3))
        outer_thigh.inhibit_exercises.append(models.exercise.AssignedExercise("2", outer_thigh.treatment_priority, 4))

        outer_thigh.lengthen_exercises.append(models.exercise.AssignedExercise("28", outer_thigh.treatment_priority, 1))
        outer_thigh.lengthen_exercises.append(models.exercise.AssignedExercise("6", outer_thigh.treatment_priority, 2))
        outer_thigh.lengthen_exercises.append(models.exercise.AssignedExercise("8", outer_thigh.treatment_priority, 3))
        outer_thigh.lengthen_exercises.append(models.exercise.AssignedExercise("7", outer_thigh.treatment_priority, 4))

        # glute_max_activation = models.exercise.AssignedExercise("34", outer_thigh.treatment_priority, 1)
        # glute_max_activation.exercise.progressions = ["35"]
        # outer_thigh.activate_exercises.append(glute_max_activation)

        outer_thigh.activate_exercises.append(
            models.exercise.AssignedExercise("108", outer_thigh.treatment_priority, 1))

        outer_thigh.activate_exercises.append(models.exercise.AssignedExercise("32", outer_thigh.treatment_priority, 2))

        hip_bridge_progression = models.exercise.AssignedExercise("10", outer_thigh.treatment_priority, 3)
        hip_bridge_progression.exercise.progressions = ["12", "11", "13"]
        outer_thigh.activate_exercises.append(hip_bridge_progression)

        # outer_thigh.activate_exercises.append(models.exercise.AssignedExercise("77", outer_thigh.treatment_priority, 4))

        body_parts.append(outer_thigh)

        # groin

        groin = models.soreness.BodyPart(models.soreness.BodyPartLocation.groin, 7)

        groin.inhibit_exercises.append(models.exercise.AssignedExercise("54", groin.treatment_priority, 1))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("1", groin.treatment_priority, 2))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("102", groin.treatment_priority, 3))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("55", groin.treatment_priority, 4))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("4", groin.treatment_priority, 5))

        # it_band = models.exercise.AssignedExercise("4", groin.treatment_priority, 5)
        # it_band.exercise.progressions = ["5"]
        # groin.inhibit_exercises.append(it_band)

        groin.inhibit_exercises.append(models.exercise.AssignedExercise("44", groin.treatment_priority, 6))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("3", groin.treatment_priority, 7))
        groin.inhibit_exercises.append(models.exercise.AssignedExercise("2", groin.treatment_priority, 8))

        groin.lengthen_exercises.append(models.exercise.AssignedExercise("103", groin.treatment_priority, 1))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("8", groin.treatment_priority, 2))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("28", groin.treatment_priority, 3))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("49", groin.treatment_priority, 4))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("98", groin.treatment_priority, 5))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("46", groin.treatment_priority, 6))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("9", groin.treatment_priority, 7))
        groin.lengthen_exercises.append(models.exercise.AssignedExercise("7", groin.treatment_priority, 8))

        groin.activate_exercises.append(models.exercise.AssignedExercise("50", groin.treatment_priority, 1))
        groin.activate_exercises.append(models.exercise.AssignedExercise("84", groin.treatment_priority, 2))

        posterior_pelvic_tilt = models.exercise.AssignedExercise("79", groin.treatment_priority, 3)
        posterior_pelvic_tilt.exercise.progressions = ["80"]
        groin.activate_exercises.append(posterior_pelvic_tilt)

        glute_activation = models.exercise.AssignedExercise("81", groin.treatment_priority, 4)
        glute_activation.exercise.progressions = ["110", "82", "83"]
        groin.activate_exercises.append(glute_activation)

        core_strength_progression = models.exercise.AssignedExercise("85", groin.treatment_priority, 5)
        core_strength_progression.exercise.progressions = ["86", "87", "88", "89", "90", "91", "92"]
        groin.activate_exercises.append(core_strength_progression)

        body_parts.append(groin)

        # quads

        quads = models.soreness.BodyPart(models.soreness.BodyPartLocation.quads, 8)

        quads.inhibit_exercises.append(models.exercise.AssignedExercise("54", quads.treatment_priority, 1))
        quads.inhibit_exercises.append(models.exercise.AssignedExercise("1", quads.treatment_priority, 2))
        quads.inhibit_exercises.append(models.exercise.AssignedExercise("4", quads.treatment_priority, 3))

        # it_band = models.exercise.AssignedExercise("4", quads.treatment_priority, 3)
        # it_band.exercise.progressions = ["5"]
        # quads.inhibit_exercises.append(it_band)

        quads.inhibit_exercises.append(models.exercise.AssignedExercise("44", quads.treatment_priority, 4))
        quads.inhibit_exercises.append(models.exercise.AssignedExercise("3", quads.treatment_priority, 5))
        quads.inhibit_exercises.append(models.exercise.AssignedExercise("2", quads.treatment_priority, 6))

        quads.lengthen_exercises.append(models.exercise.AssignedExercise("49", quads.treatment_priority, 1))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("8", quads.treatment_priority, 2))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("28", quads.treatment_priority, 3))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("98", quads.treatment_priority, 4))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("46", quads.treatment_priority, 5))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("9", quads.treatment_priority, 6))
        quads.lengthen_exercises.append(models.exercise.AssignedExercise("7", quads.treatment_priority, 7))

        quads.activate_exercises.append(models.exercise.AssignedExercise("84", quads.treatment_priority, 1))
        quads.activate_exercises.append(models.exercise.AssignedExercise("81", quads.treatment_priority, 2))
        quads.activate_exercises.append(models.exercise.AssignedExercise("108", quads.treatment_priority, 3))
        quads.activate_exercises.append(models.exercise.AssignedExercise("77", quads.treatment_priority, 4))

        # glute_max_activation = models.exercise.AssignedExercise("34", quads.treatment_priority, 3)
        # glute_max_activation.exercise.progressions = ["35"]
        # quads.activate_exercises.append(glute_max_activation)

        quads.activate_exercises.append(models.exercise.AssignedExercise("115", quads.treatment_priority, 5))

        body_parts.append(quads)

        # knee

        knee = models.soreness.BodyPart(models.soreness.BodyPartLocation.knee, 9)

        # it_band = models.exercise.AssignedExercise("4", knee.treatment_priority, 1)
        # it_band.exercise.progressions = ["5"]
        # knee.inhibit_exercises.append(it_band)

        knee.inhibit_exercises.append(models.exercise.AssignedExercise("4", knee.treatment_priority, 1))
        knee.inhibit_exercises.append(models.exercise.AssignedExercise("71", knee.treatment_priority, 2))
        knee.inhibit_exercises.append(models.exercise.AssignedExercise("2", knee.treatment_priority, 3))
        knee.inhibit_exercises.append(models.exercise.AssignedExercise("48", knee.treatment_priority, 4))
        knee.inhibit_exercises.append(models.exercise.AssignedExercise("72", knee.treatment_priority, 5))
        knee.inhibit_exercises.append(models.exercise.AssignedExercise("73", knee.treatment_priority, 6))

        knee.lengthen_exercises.append(models.exercise.AssignedExercise("28", knee.treatment_priority, 1))
        knee.lengthen_exercises.append(models.exercise.AssignedExercise("6", knee.treatment_priority, 2))
        knee.lengthen_exercises.append(models.exercise.AssignedExercise("9", knee.treatment_priority, 3))
        knee.lengthen_exercises.append(models.exercise.AssignedExercise("7", knee.treatment_priority, 4))

        knee.activate_exercises.append(models.exercise.AssignedExercise("115", knee.treatment_priority, 1))
        # knee.activate_exercises.append(models.exercise.AssignedExercise("29", knee.treatment_priority, 1))
        # knee.activate_exercises.append(models.exercise.AssignedExercise("30", knee.treatment_priority, 2))
        knee.activate_exercises.append(models.exercise.AssignedExercise("32", knee.treatment_priority, 2))
        knee.activate_exercises.append(models.exercise.AssignedExercise("77", knee.treatment_priority, 3))

        body_parts.append(knee)

        # calves

        calves = models.soreness.BodyPart(models.soreness.BodyPartLocation.calves, 10)

        calves.inhibit_exercises.append(models.exercise.AssignedExercise("2", calves.treatment_priority, 1))
        calves.inhibit_exercises.append(models.exercise.AssignedExercise("71", calves.treatment_priority, 2))
        calves.inhibit_exercises.append(models.exercise.AssignedExercise("4", calves.treatment_priority, 3))
        calves.inhibit_exercises.append(models.exercise.AssignedExercise("3", calves.treatment_priority, 4))

        calves.lengthen_exercises.append(models.exercise.AssignedExercise("7", calves.treatment_priority, 1))
        calves.lengthen_exercises.append(models.exercise.AssignedExercise("9", calves.treatment_priority, 2))

        calf_raise_progression = models.exercise.AssignedExercise("67", calves.treatment_priority, 1)
        calf_raise_progression.exercise.progressions = ["78", "68"]
        calves.activate_exercises.append(calf_raise_progression)

        calves.activate_exercises.append(models.exercise.AssignedExercise("115", calves.treatment_priority, 2))
        calves.activate_exercises.append(models.exercise.AssignedExercise("105", calves.treatment_priority, 3))

        # ankle_plantarflexion = models.exercise.AssignedExercise("30", calves.treatment_priority, 2)
        # ankle_plantarflexion.exercise.progressions = ["66"]
        # calves.activate_exercises.append(ankle_plantarflexion)
        #
        # ankle_dorsiflexion = models.exercise.AssignedExercise("29", calves.treatment_priority, 3)
        # ankle_dorsiflexion.exercise.progressions = ["65"]
        # calves.activate_exercises.append(ankle_dorsiflexion)

        body_parts.append(calves)

        # shin

        shin = models.soreness.BodyPart(models.soreness.BodyPartLocation.shin, 11)

        shin.inhibit_exercises.append(models.exercise.AssignedExercise("2", shin.treatment_priority, 1))
        shin.inhibit_exercises.append(models.exercise.AssignedExercise("71", shin.treatment_priority, 2))
        shin.inhibit_exercises.append(models.exercise.AssignedExercise("73", shin.treatment_priority, 3))
        shin.inhibit_exercises.append(models.exercise.AssignedExercise("72", shin.treatment_priority, 4))
        shin.inhibit_exercises.append(models.exercise.AssignedExercise("3", shin.treatment_priority, 5))
        shin.inhibit_exercises.append(models.exercise.AssignedExercise("1", shin.treatment_priority, 6))

        shin.lengthen_exercises.append(models.exercise.AssignedExercise("7", shin.treatment_priority, 1))
        shin.lengthen_exercises.append(models.exercise.AssignedExercise("28", shin.treatment_priority, 2))
        shin.lengthen_exercises.append(models.exercise.AssignedExercise("9", shin.treatment_priority, 3))

        shin.activate_exercises.append(models.exercise.AssignedExercise("115", shin.treatment_priority, 1))
        shin.activate_exercises.append(models.exercise.AssignedExercise("105", shin.treatment_priority, 2))

        # shin.activate_exercises.append(models.exercise.AssignedExercise("30", shin.treatment_priority, 2))
        # shin.activate_exercises.append(models.exercise.AssignedExercise("31", shin.treatment_priority, 3))

        body_parts.append(shin)

        # ankle

        ankle = models.soreness.BodyPart(models.soreness.BodyPartLocation.ankle, 12)

        ankle.inhibit_exercises.append(models.exercise.AssignedExercise("2", ankle.treatment_priority, 1))
        ankle.inhibit_exercises.append(models.exercise.AssignedExercise("71", ankle.treatment_priority, 2))
        ankle.inhibit_exercises.append(models.exercise.AssignedExercise("72", ankle.treatment_priority, 3))
        ankle.inhibit_exercises.append(models.exercise.AssignedExercise("73", ankle.treatment_priority, 4))
        ankle.inhibit_exercises.append(models.exercise.AssignedExercise("3", ankle.treatment_priority, 5))

        ankle.lengthen_exercises.append(models.exercise.AssignedExercise("7", ankle.treatment_priority, 1))

        ankle.activate_exercises.append(models.exercise.AssignedExercise("115", ankle.treatment_priority, 1))
        ankle.activate_exercises.append(models.exercise.AssignedExercise("105", ankle.treatment_priority, 2))

        # ankle_progression = models.exercise.AssignedExercise("59", ankle.treatment_priority, 1)
        # ankle_progression.exercise.progressions = ["60", "61", "62", "29", "30", "63", "64", "65", "66"]
        # ankle.activate_exercises.append(ankle_progression)

        body_parts.append(ankle)

        # foot

        foot = models.soreness.BodyPart(models.soreness.BodyPartLocation.foot, 13)

        foot.inhibit_exercises.append(models.exercise.AssignedExercise("74", foot.treatment_priority, 1))
        foot.inhibit_exercises.append(models.exercise.AssignedExercise("2", foot.treatment_priority, 2))
        foot.inhibit_exercises.append(models.exercise.AssignedExercise("71", foot.treatment_priority, 3))
        foot.inhibit_exercises.append(models.exercise.AssignedExercise("3", foot.treatment_priority, 4))

        foot.lengthen_exercises.append(models.exercise.AssignedExercise("7", foot.treatment_priority, 1))
        foot.lengthen_exercises.append(models.exercise.AssignedExercise("73", foot.treatment_priority, 2))
        foot.lengthen_exercises.append(models.exercise.AssignedExercise("9", foot.treatment_priority, 3))

        foot.activate_exercises.append(models.exercise.AssignedExercise("53", foot.treatment_priority, 1))
        foot.activate_exercises.append(models.exercise.AssignedExercise("75", foot.treatment_priority, 2))
        foot.activate_exercises.append(models.exercise.AssignedExercise("115", foot.treatment_priority, 3))
        foot.activate_exercises.append(models.exercise.AssignedExercise("105", foot.treatment_priority, 4))

        # ankle_progression = models.exercise.AssignedExercise("29", foot.treatment_priority, 3)
        # ankle_progression.exercise.progressions = ["30", "63", "64", "65", "66"]
        # foot.activate_exercises.append(ankle_progression)

        body_parts.append(foot)

        # achilles

        achilles = models.soreness.BodyPart(models.soreness.BodyPartLocation.achilles, 14)

        achilles.inhibit_exercises.append(models.exercise.AssignedExercise("2", achilles.treatment_priority, 1))
        achilles.inhibit_exercises.append(models.exercise.AssignedExercise("71", achilles.treatment_priority, 2))
        achilles.inhibit_exercises.append(models.exercise.AssignedExercise("3", achilles.treatment_priority, 3))

        achilles.lengthen_exercises.append(models.exercise.AssignedExercise("7", achilles.treatment_priority, 1))
        achilles.lengthen_exercises.append(models.exercise.AssignedExercise("9", achilles.treatment_priority, 2))

        achilles.activate_exercises.append(models.exercise.AssignedExercise("29", achilles.treatment_priority, 1))

        calf_raise_progression = models.exercise.AssignedExercise("67", achilles.treatment_priority, 2)
        calf_raise_progression.exercise.progressions = ["78", "68"]
        achilles.activate_exercises.append(calf_raise_progression)

        achilles.activate_exercises.append(models.exercise.AssignedExercise("108", achilles.treatment_priority, 3))
        achilles.activate_exercises.append(models.exercise.AssignedExercise("77", achilles.treatment_priority, 4))

        # glute_max_activation = models.exercise.AssignedExercise("34", achilles.treatment_priority, 3)
        # glute_max_activation.exercise.progressions = ["35"]
        # achilles.activate_exercises.append(glute_max_activation)

        body_parts.append(achilles)

        return body_parts

