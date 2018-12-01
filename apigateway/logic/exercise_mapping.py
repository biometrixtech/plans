import models.soreness
from logic.exercise_generator import ExerciseAssignments
import logic.soreness_processing as soreness_and_injury
from models.exercise import AssignedExercise, Phase
from logic.goal_focus_text_generator import RecoveryTextGenerator
from datetime import  timedelta
from utils import format_datetime
from random import shuffle


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
            target_exercise = self.get_current_exercise(body_part_exercise, exercise_list, completed_exercises)

            # determine reps and sets
            assigned_exercise = AssignedExercise(target_exercise.id,
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
                                                                    format_datetime(trigger_date_time - timedelta(30)),
                                                                    format_datetime(trigger_date_time),
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
                                                                                                 Phase.inhibit,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.inhibit_exercises.extend(new_assignments)

                if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                    new_assignments = self.get_exercise_list_for_body_part(body_part[0].lengthen_exercises, exercise_list,
                                                                           completed_exercises, soreness.severity)

                    for e in range(0, len(new_assignments)):
                        new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(soreness.severity,
                                                                                                 Phase.lengthen,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.lengthen_exercises.extend(new_assignments)
                if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                    new_assignments = self.get_exercise_list_for_body_part(body_part[0].activate_exercises, exercise_list,
                                                                           completed_exercises, soreness.severity)
                    for e in range(0, len(new_assignments)):
                        new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(soreness.severity,
                                                                                                 Phase.activate,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.activate_exercises.extend(new_assignments)

        else:
            body_part = self.get_general_exercises()

            if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part[0].inhibit_exercises, exercise_list,
                                                         completed_exercises, 0)

                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             Phase.inhibit,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.inhibit_exercises.extend(new_assignments)
            if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part[0].lengthen_exercises, exercise_list,
                                                         completed_exercises, 0)
                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             Phase.lengthen,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.lengthen_exercises.extend(new_assignments)
            if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part[0].activate_exercises, exercise_list,
                                                         completed_exercises, 0)

                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             Phase.activate,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.activate_exercises.extend(new_assignments)

        exercise_assignments.scale_to_targets()

        return exercise_assignments

    def get_current_exercise(self, body_part_exercise, exercise_list, completed_exercises):

        target_exercise_list = [ex for ex in exercise_list if ex.id == body_part_exercise.exercise.id]
        target_exercise = target_exercise_list[0]

        if len(body_part_exercise.exercise.progressions) == 0 or completed_exercises is None:
            return target_exercise
        else:
            completed_exercise_list = [ex for ex in completed_exercises if ex.exercise_id is not None and
                                       ex.exercise_id == body_part_exercise.exercise.id]
            if len(completed_exercise_list) == 0:
                return target_exercise
            else:
                if completed_exercise_list[0].exposures >= target_exercise.exposure_target:
                    # now work through progressions...

                    for p in range(len(body_part_exercise.exercise.progressions) - 1, -1, -1):
                        completed_progression_list = [ex for ex in completed_exercises if
                                                      ex.exercise_id == body_part_exercise.exercise.progressions[p]]
                        proposed_exercise_list = [ex for ex in exercise_list
                                                  if ex.id == body_part_exercise.exercise.progressions[p]]
                        proposed_exercise = proposed_exercise_list[0]
                        if len(completed_progression_list) == 0: # haven't done this
                            if p == 0:
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

        return target_exercise

    def get_general_exercises(self):

        body_parts = []

        general = models.soreness.BodyPart(models.soreness.BodyPartLocation.general, 15)

        general.inhibit_exercises.append(AssignedExercise("48", general.treatment_priority, 1))
        general.inhibit_exercises.append(AssignedExercise("3", general.treatment_priority, 2))
        general.inhibit_exercises.append(AssignedExercise("4", general.treatment_priority, 3))
        general.inhibit_exercises.append(AssignedExercise("54", general.treatment_priority, 4))
        general.inhibit_exercises.append(AssignedExercise("2", general.treatment_priority, 5))
        general.inhibit_exercises.append(AssignedExercise("44", general.treatment_priority, 6))
        general.inhibit_exercises.append(AssignedExercise("55", general.treatment_priority, 7))

        hamstring_stretch_progression = AssignedExercise("9", general.treatment_priority, 1)
        hamstring_stretch_progression.exercise.progressions = ["121"]
        general.lengthen_exercises.append(hamstring_stretch_progression)

        general.lengthen_exercises.append(AssignedExercise("6", general.treatment_priority, 2))

        hip_stretch_progression = AssignedExercise("28", general.treatment_priority, 3)
        hip_stretch_progression.exercise.progressions = ["122"]
        general.lengthen_exercises.append(hip_stretch_progression)

        general.lengthen_exercises.append(AssignedExercise("56", general.treatment_priority, 4))

        general.lengthen_exercises.append(AssignedExercise("7", general.treatment_priority, 5))

        glute_stretch_progression = AssignedExercise("46", general.treatment_priority, 6)
        glute_stretch_progression.exercise.progressions = ["117"]
        general.lengthen_exercises.append(glute_stretch_progression)

        spine_stretch_progression = AssignedExercise("103", general.treatment_priority, 7)
        spine_stretch_progression.exercise.progressions = ["104"]
        general.lengthen_exercises.append(spine_stretch_progression)

        hip_activation = AssignedExercise("81", general.treatment_priority, 1)
        hip_activation.exercise.progressions = ["82", "83", "110"]
        general.activate_exercises.append(hip_activation)

        glute_activation = AssignedExercise("108", general.treatment_priority, 2)
        glute_activation.exercise.progressions = ["124"]
        general.activate_exercises.append(glute_activation)

        hip_bridge_progression = AssignedExercise("10", general.treatment_priority, 3)
        hip_bridge_progression.exercise.progressions = ["12", "11", "13", "120"]
        general.activate_exercises.append(hip_bridge_progression)

        core_strength_progression = AssignedExercise("85", general.treatment_priority, 4)
        core_strength_progression.exercise.progressions = ["86", "87", "88"]
        general.activate_exercises.append(core_strength_progression)

        core_strength_progression_2 = AssignedExercise("89", general.treatment_priority, 5)
        core_strength_progression_2.exercise.progressions = ["90", "91", "92"]
        general.activate_exercises.append(core_strength_progression_2)

        body_parts.append(general)

        return body_parts

    def add_exercises_for_body_part(self, exercise_list, exercise_dict, treatment_priority, randomize=False):

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

    def add_exercises(self, body_part, inhibit, lengthen, activate, randomize=False):

        body_part.inhibit_exercises = self.add_exercises_for_body_part(body_part.inhibit_exercises, inhibit,
                                                                       body_part.treatment_priority, randomize)
        body_part.lengthen_exercises = self.add_exercises_for_body_part(body_part.lengthen_exercises, lengthen,
                                                                        body_part.treatment_priority, randomize)
        body_part.activate_exercises = self.add_exercises_for_body_part(body_part.activate_exercises, activate,
                                                                        body_part.treatment_priority, randomize)

        return body_part

    def get_progression_list(self, exercise):

        dict = {}
        dict["9"] = ["121"]
        dict["10"] = ["12", "11", "13", "120"]
        dict["28"] = ["122"]
        dict["46"] = ["117"]
        dict["49"] = ["119"]
        dict["81"] = ["82", "83", "110"]

        dict["85"] = ["86", "87", "88"]
        dict["89"] = ["90", "91", "92"]
        dict["103"] = ["104"]
        dict["108"] = ["124"]
        dict["115"] = ["114", "65", "66", "107"]

        if exercise in dict:
            return dict[exercise]
        else:
            return []

    def get_exercise_dictionary(self, exercise_list):

        exercise_dict = {}

        for e in exercise_list:
            exercise_dict[e] = self.get_progression_list(e)

        return exercise_dict

    def get_exercises_for_body_parts(self):

        body_parts = []

        # lower back

        lower_back = models.soreness.BodyPart(models.soreness.BodyPartLocation.lower_back, 1)

        inhibit = self.get_exercise_dictionary(["55", "54", "4", "48", "3"])
        lengthen = self.get_exercise_dictionary(["49", "57", "56", "103", "8"])
        activate = self.get_exercise_dictionary(["79", "10", "85", "89"])

        lower_back = self.add_exercises(lower_back, inhibit, lengthen, activate)

        body_parts.append(lower_back)

        # hip

        hip = models.soreness.BodyPart(models.soreness.BodyPartLocation.hip_flexor, 2)

        inhibit = self.get_exercise_dictionary(["3", "48", "54", "1", "44", "4", "2"])
        lengthen = self.get_exercise_dictionary(["49", "118", "9", "46", "28"])
        activate = self.get_exercise_dictionary(["79", "10", "14", "50", "84", "108"])

        hip = self.add_exercises(hip, inhibit, lengthen, activate)

        body_parts.append(hip)

        # glutes

        glutes = models.soreness.BodyPart(models.soreness.BodyPartLocation.glutes, 3)

        inhibit = self.get_exercise_dictionary(["44", "3", "4", "54", "2"])
        lengthen = self.get_exercise_dictionary(["9", "46", "116", "103", "28", "7"])
        activate = self.get_exercise_dictionary(["10", "81", "108", "14", "50", "51", "85", "89"])

        glutes = self.add_exercises(glutes, inhibit, lengthen, activate)

        body_parts.append(glutes)

        # abdominals

        abdominals = models.soreness.BodyPart(models.soreness.BodyPartLocation.abdominals, 4)

        inhibit = self.get_exercise_dictionary(["102", "4", "54", "48"])
        lengthen = self.get_exercise_dictionary(["103", "46", "118", "9", "49", "98"])
        activate = self.get_exercise_dictionary(["85", "89", "10", "51", "81"])

        abdominals = self.add_exercises(abdominals, inhibit, lengthen, activate)

        body_parts.append(abdominals)

        # hamstrings

        hamstrings = models.soreness.BodyPart(models.soreness.BodyPartLocation.hamstrings, 5)

        inhibit = self.get_exercise_dictionary(["3","44","4","54","1","2"])
        lengthen = self.get_exercise_dictionary(["9","46","116", "28","49","8","98","7"])
        activate = self.get_exercise_dictionary(["108","77","81","115","85","89"])

        hamstrings = self.add_exercises(hamstrings, inhibit, lengthen, activate)

        body_parts.append(hamstrings)

        # outer_thigh

        outer_thigh = models.soreness.BodyPart(models.soreness.BodyPartLocation.outer_thigh, 6)

        inhibit = self.get_exercise_dictionary(["48","4","1","2"])
        lengthen = self.get_exercise_dictionary(["28","6","118","8","7"])
        activate = self.get_exercise_dictionary(["108","14","81","10"])

        outer_thigh = self.add_exercises(outer_thigh, inhibit, lengthen, activate)

        body_parts.append(outer_thigh)

        # groin

        groin = models.soreness.BodyPart(models.soreness.BodyPartLocation.groin, 7)

        inhibit = self.get_exercise_dictionary(["54", "1", "102", "55", "4", "44", "3", "2"])
        lengthen = self.get_exercise_dictionary(["103", "8", "118", "28", "49", "98", "46", "9", "7"])
        activate = self.get_exercise_dictionary(["50", "84", "14", "79", "81", "85", "89"])

        groin = self.add_exercises(groin, inhibit, lengthen, activate)

        body_parts.append(groin)

        # quads

        quads = models.soreness.BodyPart(models.soreness.BodyPartLocation.quads, 8)

        quads.inhibit_exercises.append(AssignedExercise("54", quads.treatment_priority, 1))
        quads.inhibit_exercises.append(AssignedExercise("1", quads.treatment_priority, 2))
        quads.inhibit_exercises.append(AssignedExercise("4", quads.treatment_priority, 3))
        quads.inhibit_exercises.append(AssignedExercise("44", quads.treatment_priority, 4))
        quads.inhibit_exercises.append(AssignedExercise("3", quads.treatment_priority, 5))
        quads.inhibit_exercises.append(AssignedExercise("2", quads.treatment_priority, 6))

        hip_stretch_progression = AssignedExercise("49", quads.treatment_priority, 1)
        hip_stretch_progression.exercise.progressions = ["119"]
        quads.lengthen_exercises.append(hip_stretch_progression)

        quads.lengthen_exercises.append(AssignedExercise("118", quads.treatment_priority, 2))
        quads.lengthen_exercises.append(AssignedExercise("8", quads.treatment_priority, 3))

        hip_stretch_progression = AssignedExercise("28", quads.treatment_priority, 4)
        hip_stretch_progression.exercise.progressions = ["122"]
        quads.lengthen_exercises.append(hip_stretch_progression)

        quads.lengthen_exercises.append(AssignedExercise("98", quads.treatment_priority, 5))

        glute_stretch_progression = AssignedExercise("46", quads.treatment_priority, 6)
        glute_stretch_progression.exercise.progressions = ["117"]
        quads.lengthen_exercises.append(glute_stretch_progression)

        hamstring_stretch_progression = AssignedExercise("9", quads.treatment_priority, 7)
        hamstring_stretch_progression.exercise.progressions = ["121"]
        quads.lengthen_exercises.append(hamstring_stretch_progression)

        quads.lengthen_exercises.append(AssignedExercise("7", quads.treatment_priority, 8))

        quads.activate_exercises.append(AssignedExercise("84", quads.treatment_priority, 1))

        glute_activation = AssignedExercise("81", quads.treatment_priority, 2)
        glute_activation.exercise.progressions = ["82", "83", "110"]
        quads.activate_exercises.append(glute_activation)

        quads.activate_exercises.append(AssignedExercise("14", quads.treatment_priority, 3))

        glute_activation = AssignedExercise("108", quads.treatment_priority, 4)
        glute_activation.exercise.progressions = ["124"]
        quads.activate_exercises.append(glute_activation)

        quads.activate_exercises.append(AssignedExercise("77", quads.treatment_priority, 5))

        ankle_mobility = AssignedExercise("29", quads.treatment_priority, 6)
        ankle_mobility.exercise.progressions = ["63", "64"]
        quads.activate_exercises.append(ankle_mobility)

        body_parts.append(quads)

        # knee

        knee = models.soreness.BodyPart(models.soreness.BodyPartLocation.knee, 9)

        knee.inhibit_exercises.append(AssignedExercise("4", knee.treatment_priority, 1))
        knee.inhibit_exercises.append(AssignedExercise("71", knee.treatment_priority, 2))
        knee.inhibit_exercises.append(AssignedExercise("2", knee.treatment_priority, 3))
        knee.inhibit_exercises.append(AssignedExercise("48", knee.treatment_priority, 4))
        knee.inhibit_exercises.append(AssignedExercise("72", knee.treatment_priority, 5))
        knee.inhibit_exercises.append(AssignedExercise("73", knee.treatment_priority, 6))

        hip_stretch_progression = AssignedExercise("28", knee.treatment_priority, 1)
        hip_stretch_progression.exercise.progressions = ["122"]
        knee.lengthen_exercises.append(hip_stretch_progression)

        knee.lengthen_exercises.append(AssignedExercise("118", knee.treatment_priority, 2))
        knee.lengthen_exercises.append(AssignedExercise("6", knee.treatment_priority, 3))

        hamstring_stretch_progression = AssignedExercise("9", quads.treatment_priority, 4)
        hamstring_stretch_progression.exercise.progressions = ["121"]
        quads.lengthen_exercises.append(hamstring_stretch_progression)

        knee.lengthen_exercises.append(AssignedExercise("7", knee.treatment_priority, 5))

        ankle_activation = AssignedExercise("115", knee.treatment_priority, 1)
        ankle_activation.exercise.progressions = ["114", "65", "66", "107"]
        knee.activate_exercises.append(ankle_activation)

        knee.activate_exercises.append(AssignedExercise("14", knee.treatment_priority, 2))

        glute_activation = AssignedExercise("81", knee.treatment_priority, 3)
        glute_activation.exercise.progressions = ["82", "83", "110"]
        knee.activate_exercises.append(glute_activation)

        knee.activate_exercises.append(AssignedExercise("77", knee.treatment_priority, 4))

        body_parts.append(knee)

        # calves

        calves = models.soreness.BodyPart(models.soreness.BodyPartLocation.calves, 10)

        calves.inhibit_exercises.append(AssignedExercise("2", calves.treatment_priority, 1))
        calves.inhibit_exercises.append(AssignedExercise("71", calves.treatment_priority, 2))
        calves.inhibit_exercises.append(AssignedExercise("4", calves.treatment_priority, 3))
        calves.inhibit_exercises.append(AssignedExercise("3", calves.treatment_priority, 4))

        calves.lengthen_exercises.append(AssignedExercise("7", calves.treatment_priority, 1))
        calves.lengthen_exercises.append(AssignedExercise("26", calves.treatment_priority, 2))

        hamstring_stretch_progression = AssignedExercise("9", calves.treatment_priority, 3)
        hamstring_stretch_progression.exercise.progressions = ["121"]
        calves.lengthen_exercises.append(hamstring_stretch_progression)

        calf_raise_progression = AssignedExercise("67", calves.treatment_priority, 1)
        calf_raise_progression.exercise.progressions = ["78", "68", "31"]
        calves.activate_exercises.append(calf_raise_progression)

        ankle_activation = AssignedExercise("115", calves.treatment_priority, 2)
        ankle_activation.exercise.progressions = ["114", "65", "66", "107"]
        calves.activate_exercises.append(ankle_activation)

        ankle_mobility_2 = AssignedExercise("106", calves.treatment_priority, 3)
        ankle_mobility_2.exercise.progressions = ["105", "113"]
        calves.activate_exercises.append(ankle_mobility_2)

        body_parts.append(calves)

        # shin

        shin = models.soreness.BodyPart(models.soreness.BodyPartLocation.shin, 11)

        shin.inhibit_exercises.append(AssignedExercise("2", shin.treatment_priority, 1))
        shin.inhibit_exercises.append(AssignedExercise("71", shin.treatment_priority, 2))
        shin.inhibit_exercises.append(AssignedExercise("73", shin.treatment_priority, 3))
        shin.inhibit_exercises.append(AssignedExercise("3", shin.treatment_priority, 4))
        shin.inhibit_exercises.append(AssignedExercise("1", shin.treatment_priority, 5))

        shin.lengthen_exercises.append(AssignedExercise("60", shin.treatment_priority, 1))
        shin.lengthen_exercises.append(AssignedExercise("61", shin.treatment_priority, 2))
        shin.lengthen_exercises.append(AssignedExercise("7", shin.treatment_priority, 3))

        hip_stretch_progression = AssignedExercise("28", shin.treatment_priority, 4)
        hip_stretch_progression.exercise.progressions = ["122"]
        shin.lengthen_exercises.append(hip_stretch_progression)

        hamstring_stretch_progression = AssignedExercise("9", shin.treatment_priority, 5)
        hamstring_stretch_progression.exercise.progressions = ["121"]
        shin.lengthen_exercises.append(hamstring_stretch_progression)

        ankle_activation = AssignedExercise("115", shin.treatment_priority, 1)
        ankle_activation.exercise.progressions = ["114", "65", "66", "107"]
        shin.activate_exercises.append(ankle_activation)

        ankle_mobility_2 = AssignedExercise("106", shin.treatment_priority, 2)
        ankle_mobility_2.exercise.progressions = ["105", "113"]
        shin.activate_exercises.append(ankle_mobility_2)

        shin.activate_exercises.append(AssignedExercise("53", shin.treatment_priority, 3))
        shin.activate_exercises.append(AssignedExercise("75", shin.treatment_priority, 4))

        body_parts.append(shin)

        # ankle

        ankle = models.soreness.BodyPart(models.soreness.BodyPartLocation.ankle, 12)

        ankle.inhibit_exercises.append(AssignedExercise("2", ankle.treatment_priority, 1))
        ankle.inhibit_exercises.append(AssignedExercise("71", ankle.treatment_priority, 2))
        ankle.inhibit_exercises.append(AssignedExercise("72", ankle.treatment_priority, 3))
        ankle.inhibit_exercises.append(AssignedExercise("73", ankle.treatment_priority, 4))
        ankle.inhibit_exercises.append(AssignedExercise("3", ankle.treatment_priority, 5))

        ankle.lengthen_exercises.append(AssignedExercise("59", ankle.treatment_priority, 1))
        ankle.lengthen_exercises.append(AssignedExercise("62", ankle.treatment_priority, 2))
        ankle.lengthen_exercises.append(AssignedExercise("7", ankle.treatment_priority, 3))

        ankle_activation = AssignedExercise("115", ankle.treatment_priority, 1)
        ankle_activation.exercise.progressions = ["114", "65", "66", "107"]
        ankle.activate_exercises.append(ankle_activation)

        ankle_mobility_2 = AssignedExercise("106", ankle.treatment_priority, 2)
        ankle_mobility_2.exercise.progressions = ["105", "113"]
        ankle.activate_exercises.append(ankle_mobility_2)

        body_parts.append(ankle)

        # upper back/neck

        upper_back_neck = models.soreness.BodyPart(models.soreness.BodyPartLocation.upper_back_neck, 13)

        upper_back_neck.inhibit_exercises.append(
            AssignedExercise("102", upper_back_neck.treatment_priority, 1))
        upper_back_neck.inhibit_exercises.append(
            AssignedExercise("55", upper_back_neck.treatment_priority, 2))
        upper_back_neck.inhibit_exercises.append(
            AssignedExercise("125", upper_back_neck.treatment_priority, 3))
        upper_back_neck.inhibit_exercises.append(
            AssignedExercise("126", upper_back_neck.treatment_priority, 4))

        upper_back_neck.lengthen_exercises.append(
            AssignedExercise("127", upper_back_neck.treatment_priority, 1))
        upper_back_neck.lengthen_exercises.append(
            AssignedExercise("128", upper_back_neck.treatment_priority, 2))
        upper_back_neck.lengthen_exercises.append(
            AssignedExercise("129", upper_back_neck.treatment_priority, 3))
        upper_back_neck.lengthen_exercises.append(
            AssignedExercise("130", upper_back_neck.treatment_priority, 4))

        child_pose = AssignedExercise("103", upper_back_neck.treatment_priority, 5)
        child_pose.exercise.progressions = ["104"]
        upper_back_neck.lengthen_exercises.append(child_pose)

        upper_back_neck.activate_exercises.append(
            AssignedExercise("131", upper_back_neck.treatment_priority, 1))
        upper_back_neck.activate_exercises.append(
            AssignedExercise("134", upper_back_neck.treatment_priority, 2))
        upper_back_neck.activate_exercises.append(
            AssignedExercise("132", upper_back_neck.treatment_priority, 3))
        upper_back_neck.activate_exercises.append(
            AssignedExercise("133", upper_back_neck.treatment_priority, 4))

        shoulder_activation = AssignedExercise("135", upper_back_neck.treatment_priority, 5)
        shoulder_activation.exercise.progressions = ["136", "138"]
        upper_back_neck.activate_exercises.append(shoulder_activation)

        upper_back_neck.activate_exercises.append(
            AssignedExercise("137", upper_back_neck.treatment_priority, 6))

        body_parts.append(upper_back_neck)

        # foot

        foot = models.soreness.BodyPart(models.soreness.BodyPartLocation.foot, 14)

        foot.inhibit_exercises.append(AssignedExercise("74", foot.treatment_priority, 1))
        foot.inhibit_exercises.append(AssignedExercise("2", foot.treatment_priority, 2))
        foot.inhibit_exercises.append(AssignedExercise("71", foot.treatment_priority, 3))
        foot.inhibit_exercises.append(AssignedExercise("3", foot.treatment_priority, 4))

        foot.lengthen_exercises.append(AssignedExercise("7", foot.treatment_priority, 1))
        foot.lengthen_exercises.append(AssignedExercise("73", foot.treatment_priority, 2))

        hamstring_stretch_progression = AssignedExercise("9", foot.treatment_priority, 3)
        hamstring_stretch_progression.exercise.progressions = ["121"]
        foot.lengthen_exercises.append(hamstring_stretch_progression)

        foot.activate_exercises.append(AssignedExercise("53", foot.treatment_priority, 1))
        foot.activate_exercises.append(AssignedExercise("75", foot.treatment_priority, 2))

        ankle_activation = AssignedExercise("115", foot.treatment_priority, 3)
        ankle_activation.exercise.progressions = ["114", "65", "66", "107"]
        foot.activate_exercises.append(ankle_activation)

        ankle_mobility_2 = AssignedExercise("106", foot.treatment_priority, 4)
        ankle_mobility_2.exercise.progressions = ["105", "113"]
        foot.activate_exercises.append(ankle_mobility_2)

        body_parts.append(foot)

        # achilles

        achilles = models.soreness.BodyPart(models.soreness.BodyPartLocation.achilles, 15)

        achilles.inhibit_exercises.append(AssignedExercise("2", achilles.treatment_priority, 1))
        achilles.inhibit_exercises.append(AssignedExercise("71", achilles.treatment_priority, 2))
        achilles.inhibit_exercises.append(AssignedExercise("3", achilles.treatment_priority, 3))

        achilles.lengthen_exercises.append(AssignedExercise("7", achilles.treatment_priority, 1))

        hamstring_stretch_progression = AssignedExercise("9", achilles.treatment_priority, 2)
        hamstring_stretch_progression.exercise.progressions = ["121"]
        achilles.lengthen_exercises.append(hamstring_stretch_progression)

        ankle_mobility = AssignedExercise("29", achilles.treatment_priority, 1)
        ankle_mobility.exercise.progressions = ["63", "64"]
        achilles.activate_exercises.append(ankle_mobility)

        calf_raise_progression = AssignedExercise("67", achilles.treatment_priority, 2)
        calf_raise_progression.exercise.progressions = ["78", "68", "31"]
        achilles.activate_exercises.append(calf_raise_progression)

        glute_activation = AssignedExercise("108", achilles.treatment_priority, 3)
        glute_activation.exercise.progressions = ["124"]
        achilles.activate_exercises.append(glute_activation)

        achilles.activate_exercises.append(AssignedExercise("77", achilles.treatment_priority, 4))

        body_parts.append(achilles)

        return body_parts
