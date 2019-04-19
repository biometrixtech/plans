import models.soreness
from logic.exercise_generator import ExerciseAssignments
import logic.soreness_processing as soreness_and_injury
from models.exercise import ExerciseBuckets, Phase
from models.soreness import AssignedExercise, BodyPartLocation, HistoricSorenessStatus
from logic.goal_focus_text_generator import RecoveryTextGenerator
from datetime import  timedelta
from utils import format_datetime
from models.modalities import Heat


class ExerciseAssignmentCalculator(object):

    def __init__(self, athlete_id, exercise_library_datastore, completed_exercise_datastore, is_active_prep):
        self.athlete_id = athlete_id
        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        # self.exercises_for_body_parts = self.get_exercises_for_body_parts()
        self.is_active_prep = is_active_prep
        #  self.injury_history_present = injury_history_present

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
            assigned_exercise.equipment_required = target_exercise.equipment_required

            assigned_exercise_list.append(assigned_exercise)

        return assigned_exercise_list

    def create_exercise_assignments(self, exercise_session, soreness_list, trigger_date_time, duration_minutes_target):

        # TODO: handle progressions

        text_generator = RecoveryTextGenerator()

        exercise_assignments = ExerciseAssignments()
        exercise_assignments.duration_minutes_target = duration_minutes_target
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
        # body_part_exercises = self.exercises_for_body_parts
        #body_part_exercises = self.get_exercises_for_body_parts()
        exercise_list = self.exercise_library

        if soreness_list is not None and len(soreness_list) > 0:
            for soreness in soreness_list:
                # body_part = [b for b in body_part_exercises if b.location.value == soreness.body_part.location.value]
                body_part = self.get_exercises_for_body_parts(soreness)

                if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                    new_assignments = self.get_exercise_list_for_body_part(body_part.inhibit_exercises, exercise_list,
                                                                           completed_exercises, soreness.severity)
                    for e in range(0, len(new_assignments)):
                        new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(soreness.severity,
                                                                                                 Phase.inhibit,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.inhibit_exercises.extend(new_assignments)

                if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                    new_assignments = self.get_exercise_list_for_body_part(body_part.lengthen_exercises, exercise_list,
                                                                           completed_exercises, soreness.severity)

                    for e in range(0, len(new_assignments)):
                        new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(soreness.severity,
                                                                                                 Phase.lengthen,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.lengthen_exercises.extend(new_assignments)
                if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                    new_assignments = self.get_exercise_list_for_body_part(body_part.activate_exercises, exercise_list,
                                                                           completed_exercises, soreness.severity)
                    for e in range(0, len(new_assignments)):
                        new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(soreness.severity,
                                                                                                 Phase.activate,
                                                                                                 soreness.body_part.location.value)

                    exercise_assignments.activate_exercises.extend(new_assignments)

        else:
            body_part = self.get_general_exercises()

            if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part.inhibit_exercises, exercise_list,
                                                         completed_exercises, 0)

                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             Phase.inhibit,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.inhibit_exercises.extend(new_assignments)
            if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part.lengthen_exercises, exercise_list,
                                                         completed_exercises, 0)
                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             Phase.lengthen,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.lengthen_exercises.extend(new_assignments)
            if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part.activate_exercises, exercise_list,
                                                         completed_exercises, 0)

                for e in range(0, len(new_assignments)):
                    new_assignments[e].goal_text = text_generator.get_recovery_exercise_text(0,
                                                                                             Phase.activate,
                                                                                             models.soreness.BodyPartLocation.general.value)

                exercise_assignments.activate_exercises.extend(new_assignments)


        exercise_assignments.inhibit_exercises = exercise_assignments.remove_duplicate_assigned_exercises(exercise_assignments.inhibit_exercises)
        exercise_assignments.lengthen_exercises = exercise_assignments.remove_duplicate_assigned_exercises(exercise_assignments.lengthen_exercises)
        exercise_assignments.activate_exercises = exercise_assignments.remove_duplicate_assigned_exercises(exercise_assignments.activate_exercises)
        exercise_assignments.calculate_durations()
        if exercise_assignments.duration_minutes() < exercise_assignments.duration_minutes_target - 3:
            body_part = self.get_general_exercises()

            if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part.inhibit_exercises, exercise_list,
                                                         completed_exercises, 0)
                exercise_assignments.inhibit_exercises.extend(new_assignments)
            if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part.lengthen_exercises, exercise_list,
                                                         completed_exercises, 0)
                exercise_assignments.lengthen_exercises.extend(new_assignments)
            if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                new_assignments = self.get_exercise_list_for_body_part(body_part.activate_exercises, exercise_list,
                                                         completed_exercises, 0)
                exercise_assignments.activate_exercises.extend(new_assignments)

        exercise_assignments.scale_to_targets(self.exercise_library)

        return exercise_assignments

    def get_current_exercise(self, body_part_exercise, exercise_list, completed_exercises):

        exercise_bucket_list = ExerciseBuckets().get_bucket_for_exercise(body_part_exercise.exercise.id)

        target_exercise_list = [ex for ex in exercise_list if ex.id == body_part_exercise.exercise.id]
        target_exercise = target_exercise_list[0]

        if len(body_part_exercise.exercise.progressions) == 0 or completed_exercises is None:
            return target_exercise
        else:
            completed_exercise_list = [ex for ex in completed_exercises if ex.exercise_id is not None and
                                       ex.exercise_id in exercise_bucket_list]
            if len(completed_exercise_list) == 0:
                return target_exercise
            else:
                exposures = 0
                for c in completed_exercise_list:
                    exposures += c.exposures

                if exposures >= target_exercise.exposure_target:
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
                        elif exposures >= proposed_exercise.exposure_target:
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

        # body_parts = []

        general = models.soreness.BodyPart(models.soreness.BodyPartLocation.general, 21)

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

        #body_parts.append(general)

        return general

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

    def get_exercises_for_body_parts(self, soreness):

        if soreness.body_part.location == BodyPartLocation.lower_back:

            return self.get_lower_back_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.hip_flexor:

            return self.get_hip_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.glutes:

            return self.get_glutes_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.abdominals:

            return self.get_abdominals_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.hamstrings:

            return self.get_hamstrings_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.outer_thigh:

            return self.get_outer_thigh_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.groin:

            return self.get_groin_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.quads:

            return self.get_quads_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.knee:

            return self.get_knee_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.calves:

            return self.get_calves_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.shin:

            return self.get_shin_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.ankle:

            return self.get_ankle_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.upper_back_neck:

            return self.get_upper_back_neck_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.foot:

            return self.get_foot_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.achilles:

            return self.get_achilles_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.elbow:

            return self.get_elbow_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.wrist:

            return self.get_wrist_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.shoulder:

            return self.get_shoulder_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.lats:

            return self.get_lats_exercises(soreness)

        elif soreness.body_part.location == BodyPartLocation.chest:

            return self.get_chest_exercises(soreness)

    def is_soreness_historic(self, soreness):

        if (soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain_acute or
                soreness.historic_soreness_status == HistoricSorenessStatus.acute_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_soreness or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_soreness or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness):
            return True
        else:
            return  False

    def get_wrist_exercises(self, soreness):
        wrist = models.soreness.BodyPart(models.soreness.BodyPartLocation.wrist, self.get_body_part_priority(20, soreness))
        inhibit = self.get_exercise_dictionary(["243", "244", "245"])
        lengthen = self.get_exercise_dictionary(["246", "247", "248"])
        activate = self.get_exercise_dictionary(["249", "250", "251", "252", "253", "254"])
        wrist.add_exercise_phases(inhibit, lengthen, activate)
        return wrist

    def get_elbow_exercises(self, soreness):
        elbow = models.soreness.BodyPart(models.soreness.BodyPartLocation.elbow, self.get_body_part_priority(19, soreness))
        inhibit = self.get_exercise_dictionary(["243", "244", "245"])
        lengthen = self.get_exercise_dictionary(["246", "247", "248"])
        activate = self.get_exercise_dictionary(["249", "250", "251", "252", "253", "254"])
        elbow.add_exercise_phases(inhibit, lengthen, activate)
        return elbow

    def get_achilles_exercises(self, soreness):
        achilles = models.soreness.BodyPart(models.soreness.BodyPartLocation.achilles, self.get_body_part_priority(18, soreness))

        injury_history_present = self.is_soreness_historic(soreness)

        if self.is_daily_or_persistent(soreness):
            inhibit = self.get_exercise_dictionary(["2", "71", "3"])
            lengthen = self.get_exercise_dictionary(["7", "9"])
            activate = self.get_exercise_dictionary(["29", "67", "108", "77"])
            achilles.add_exercise_phases(inhibit, lengthen, activate, injury_history_present)  # randomize if persistent
        if injury_history_present:  #intentionally sending persistent_2_status through both!
            if self.is_active_prep:
                inhibit = self.get_exercise_dictionary(["2", "71", "73", "72"])
                lengthen = self.get_exercise_dictionary(["7", "59", "61", "9"])
                activate = self.get_exercise_dictionary(["67", "106", "108"])
            else:
                inhibit = self.get_exercise_dictionary(["2", "71", "72", "4", "3"])
                lengthen = self.get_exercise_dictionary(["7", "26", "28", "9"])
                activate = self.get_exercise_dictionary(["106"])

            achilles.add_exercise_phases(inhibit, lengthen, activate, True)
        return achilles

    def get_foot_exercises(self, soreness):
        foot = models.soreness.BodyPart(models.soreness.BodyPartLocation.foot, self.get_body_part_priority(17, soreness))
        inhibit = self.get_exercise_dictionary(["74", "2", "71", "73", "3"])
        lengthen = self.get_exercise_dictionary(["7", "9"])
        activate = self.get_exercise_dictionary(["53", "75", "115", "106"])
        foot.add_exercise_phases(inhibit, lengthen, activate)
        return foot


    def get_chest_exercises(self, soreness):
        chest = models.soreness.BodyPart(models.soreness.BodyPartLocation.chest, self.get_body_part_priority(16, soreness))
        inhibit = self.get_exercise_dictionary(["55", "102"])
        lengthen = self.get_exercise_dictionary(["57", "238"])
        activate = self.get_exercise_dictionary(["239", "240", "241"])
        chest.add_exercise_phases(inhibit, lengthen, activate)
        return chest

    def get_lats_exercises(self, soreness):
        lats = models.soreness.BodyPart(models.soreness.BodyPartLocation.lats, self.get_body_part_priority(15, soreness))
        inhibit = self.get_exercise_dictionary(["55", "102"])
        lengthen = self.get_exercise_dictionary(["57", "238"])
        activate = self.get_exercise_dictionary(["239", "240", "241"])
        lats.add_exercise_phases(inhibit, lengthen, activate)
        return lats

    def get_shoulder_exercises(self, soreness):
        shoulder = models.soreness.BodyPart(models.soreness.BodyPartLocation.shoulder, self.get_body_part_priority(14, soreness))
        inhibit = self.get_exercise_dictionary(["55", "102"])
        lengthen = self.get_exercise_dictionary(["57", "238"])
        activate = self.get_exercise_dictionary(["239", "240", "241"])
        shoulder.add_exercise_phases(inhibit, lengthen, activate)
        return shoulder

    def get_upper_back_neck_exercises(self, soreness):
        upper_back_neck = models.soreness.BodyPart(models.soreness.BodyPartLocation.upper_back_neck, self.get_body_part_priority(13, soreness))
        inhibit = self.get_exercise_dictionary(["102", "55", "125", "126"])
        lengthen = self.get_exercise_dictionary(["127", "128", "129", "130", "103", "238"])
        activate = self.get_exercise_dictionary(["131", "134", "132", "133", "135", "137", "242"])
        upper_back_neck.add_exercise_phases(inhibit, lengthen, activate)
        return upper_back_neck

    def get_ankle_exercises(self, soreness):
        ankle = models.soreness.BodyPart(models.soreness.BodyPartLocation.ankle, self.get_body_part_priority(12, soreness))

        injury_history_present = self.is_soreness_historic(soreness)

        if self.is_daily_or_persistent(soreness):
            inhibit = self.get_exercise_dictionary(["2", "71", "72", "73", "3"])
            lengthen = self.get_exercise_dictionary(["59", "62", "7"])
            activate = self.get_exercise_dictionary(["115", "106"])
            ankle.add_exercise_phases(inhibit, lengthen, activate, injury_history_present)  # randomize if persistent
        if injury_history_present:
            if self.is_active_prep:
                inhibit = self.get_exercise_dictionary(["71", "72", "73", "2", "4"])
                lengthen = self.get_exercise_dictionary(["60", "61", "7"])
                activate = self.get_exercise_dictionary(["115", "106", "108"])
            else:
                inhibit = self.get_exercise_dictionary(["71", "72", "73", "2", "4", "44"])
                lengthen = self.get_exercise_dictionary(["60", "61", "59", "62"])
                activate = self.get_exercise_dictionary(["106"])

            ankle.add_exercise_phases(inhibit, lengthen, activate, True)
        return ankle

    def get_shin_exercises(self, soreness):
        shin = models.soreness.BodyPart(models.soreness.BodyPartLocation.shin, self.get_body_part_priority(11, soreness))
        inhibit = self.get_exercise_dictionary(["2", "71", "73", "3", "1"])
        lengthen = self.get_exercise_dictionary(["60", "61", "7", "28", "9"])
        activate = self.get_exercise_dictionary(["115", "114", "106", "53", "75"])
        shin.add_exercise_phases(inhibit, lengthen, activate)
        return shin

    def get_calves_exercises(self, soreness):
        calves = models.soreness.BodyPart(models.soreness.BodyPartLocation.calves, self.get_body_part_priority(10, soreness))
        inhibit = self.get_exercise_dictionary(["2", "71", "4", "3"])
        lengthen = self.get_exercise_dictionary(["7", "26", "9"])
        activate = self.get_exercise_dictionary(["67", "115", "106"])
        calves.add_exercise_phases(inhibit, lengthen, activate)
        return calves

    def get_knee_exercises(self, soreness):
        knee = models.soreness.BodyPart(models.soreness.BodyPartLocation.knee, self.get_body_part_priority(9, soreness))

        injury_history_present = self.is_soreness_historic(soreness)

        if self.is_daily_or_persistent(soreness):
            inhibit = self.get_exercise_dictionary(["4", "71", "2", "48", "72", "73"])
            lengthen = self.get_exercise_dictionary(["28", "118", "6", "9", "7"])
            activate = self.get_exercise_dictionary(["115", "14", "81", "77"])
            knee.add_exercise_phases(inhibit, lengthen, activate, injury_history_present)  # randomize if persistent
        if injury_history_present:
            if self.is_active_prep:
                inhibit = self.get_exercise_dictionary(["48", "4", "44", "2", "102"])
                lengthen = self.get_exercise_dictionary(["49", "46", "9", "56", "7"])
                activate = self.get_exercise_dictionary(["10", "81", "59", "14"])
            else:
                inhibit = self.get_exercise_dictionary(["48", "4", "44", "2", "102"])
                lengthen = self.get_exercise_dictionary(["49", "46", "118", "9", "7"])
                activate = self.get_exercise_dictionary(["115", "75", "67"])

            knee.add_exercise_phases(inhibit, lengthen, activate, True)
        return knee

    def get_quads_exercises(self, soreness):
        quads = models.soreness.BodyPart(models.soreness.BodyPartLocation.quads, self.get_body_part_priority(8, soreness))
        inhibit = self.get_exercise_dictionary(["54", "1", "4", "44", "3", "2"])
        lengthen = self.get_exercise_dictionary(["49", "118", "8", "28", "98", "46", "9", "7"])
        activate = self.get_exercise_dictionary(["84", "81", "14", "108", "77", "29"])
        quads.add_exercise_phases(inhibit, lengthen, activate)
        return quads

    def get_groin_exercises(self, soreness):
        groin = models.soreness.BodyPart(models.soreness.BodyPartLocation.groin, self.get_body_part_priority(7, soreness))

        injury_history_present = self.is_soreness_historic(soreness)

        if self.is_daily_or_persistent(soreness):
            inhibit = self.get_exercise_dictionary(["54", "1", "102", "55", "4", "44", "3", "2"])
            lengthen = self.get_exercise_dictionary(["103", "8", "118", "28", "49", "98", "46", "9", "7"])
            activate = self.get_exercise_dictionary(["50", "84", "14", "79", "81", "85", "89"])
            groin.add_exercise_phases(inhibit, lengthen, activate, injury_history_present)  # randomize if persistent
        if injury_history_present:
            if self.is_active_prep:
                inhibit = self.get_exercise_dictionary(["54", "1", "102", "55", "4", "44", "3", "48"])
                lengthen = self.get_exercise_dictionary(["103", "28", "98", "46", "9", "56"])
                activate = self.get_exercise_dictionary(["50", "81", "10", "51"])
            else:
                inhibit = self.get_exercise_dictionary(["54", "1", "102", "55", "4", "44"])
                lengthen = self.get_exercise_dictionary(["103", "98", "46", "56"])
                activate = self.get_exercise_dictionary(["10", "51"])

            groin.add_exercise_phases(inhibit, lengthen, activate, True)
        return groin

    def get_outer_thigh_exercises(self, soreness):
        outer_thigh = models.soreness.BodyPart(models.soreness.BodyPartLocation.outer_thigh, self.get_body_part_priority(6, soreness))
        inhibit = self.get_exercise_dictionary(["48", "4", "1", "2"])
        lengthen = self.get_exercise_dictionary(["28", "6", "118", "8", "7"])
        activate = self.get_exercise_dictionary(["108", "14", "81", "10"])
        outer_thigh.add_exercise_phases(inhibit, lengthen, activate)
        return outer_thigh

    def get_hamstrings_exercises(self, soreness):
        hamstrings = models.soreness.BodyPart(models.soreness.BodyPartLocation.hamstrings, self.get_body_part_priority(5, soreness))

        injury_history_present = self.is_soreness_historic(soreness)

        if self.is_daily_or_persistent(soreness):
            inhibit = self.get_exercise_dictionary(["3", "44", "4", "54", "1", "2"])
            lengthen = self.get_exercise_dictionary(["9", "46", "116", "28", "49", "8", "98", "7"])
            activate = self.get_exercise_dictionary(["108", "77", "81", "115", "85", "89"])
            hamstrings.add_exercise_phases(inhibit, lengthen, activate, injury_history_present)  # randomize if persistent
        if injury_history_present:
            if self.is_active_prep:
                inhibit = self.get_exercise_dictionary(["3", "44", "4", "54", "48"])
                lengthen = self.get_exercise_dictionary(["9", "46", "103", "28", "49", "118"])
                activate = self.get_exercise_dictionary(["10", "81", "84", "108"])
            else:
                inhibit = self.get_exercise_dictionary(["3", "44", "4", "54", "48"])
                lengthen = self.get_exercise_dictionary(["9", "46", "103", "49"])
                activate = self.get_exercise_dictionary(["10", "81"])

            hamstrings.add_exercise_phases(inhibit, lengthen, activate, True)
        return hamstrings

    def get_abdominals_exercises(self, soreness):
        abdominals = models.soreness.BodyPart(models.soreness.BodyPartLocation.abdominals, self.get_body_part_priority(4, soreness))
        inhibit = self.get_exercise_dictionary(["102", "4", "54", "48"])
        lengthen = self.get_exercise_dictionary(["103", "46", "118", "9", "49", "98"])
        activate = self.get_exercise_dictionary(["85", "89", "10", "51", "81"])
        abdominals.add_exercise_phases(inhibit, lengthen, activate)
        return abdominals

    def get_glutes_exercises(self, soreness):
        glutes = models.soreness.BodyPart(models.soreness.BodyPartLocation.glutes, self.get_body_part_priority(3, soreness))

        injury_history_present = self.is_soreness_historic(soreness)

        if self.is_daily_or_persistent(soreness):
            inhibit = self.get_exercise_dictionary(["44", "3", "4", "54", "2"])
            lengthen = self.get_exercise_dictionary(["9", "46", "116", "103", "28", "7"])
            activate = self.get_exercise_dictionary(["10", "81", "108", "14", "50", "51", "85", "89"])
            glutes.add_exercise_phases(inhibit, lengthen, activate, injury_history_present)  # randomize if persistent
        if injury_history_present:
            if self.is_active_prep:
                inhibit = self.get_exercise_dictionary(["44", "3", "4", "54", "48"])
                lengthen = self.get_exercise_dictionary(["9", "46", "56", "49", "28", "118"])
                activate = self.get_exercise_dictionary(["10", "81", "108", "50"])
            else:
                inhibit = self.get_exercise_dictionary(["44", "3", "4", "48"])
                lengthen = self.get_exercise_dictionary(["9", "46", "49", "118"])
                activate = self.get_exercise_dictionary(["10", "50"])
            glutes.add_exercise_phases(inhibit, lengthen, activate, True)
        return glutes

    def get_hip_exercises(self, soreness):
        hip = models.soreness.BodyPart(models.soreness.BodyPartLocation.hip_flexor, self.get_body_part_priority(2, soreness))

        injury_history_present = self.is_soreness_historic(soreness)

        if self.is_daily_or_persistent(soreness):
            inhibit = self.get_exercise_dictionary(["3", "48", "54", "1", "44", "4", "2"])
            lengthen = self.get_exercise_dictionary(["49", "118", "9", "46", "28"])
            activate = self.get_exercise_dictionary(["79", "10", "14", "50", "84", "108"])
            hip.add_exercise_phases(inhibit, lengthen, activate, injury_history_present) # randomize if persistent
        if injury_history_present:
            if self.is_active_prep:
                inhibit = self.get_exercise_dictionary(["54", "44", "4", "3", "1"])
                lengthen = self.get_exercise_dictionary(["49", "46", "28", "56", "118"])
                activate = self.get_exercise_dictionary(["79", "10", "108", "14", "84"])
            else:
                inhibit = self.get_exercise_dictionary(["54", "44", "1", "4", "3"])
                lengthen = self.get_exercise_dictionary(["49", "46", "56", "118"])
                activate = self.get_exercise_dictionary(["79", "81"])

            hip.add_exercise_phases(inhibit, lengthen, activate, True)
        return hip

    def get_lower_back_exercises(self, soreness):
        lower_back = models.soreness.BodyPart(models.soreness.BodyPartLocation.lower_back, self.get_body_part_priority(1, soreness))

        injury_history_present = self.is_soreness_historic(soreness)

        if self.is_daily_or_persistent(soreness):
            inhibit = self.get_exercise_dictionary(["55", "54", "4", "48", "3"])
            lengthen = self.get_exercise_dictionary(["49", "57", "56", "103", "8"])
            activate = self.get_exercise_dictionary(["79", "10", "85", "89"])
            lower_back.add_exercise_phases(inhibit, lengthen, activate, injury_history_present)
        if injury_history_present:
            if self.is_active_prep:
                inhibit = self.get_exercise_dictionary(["55", "44", "54", "4", "48", "3"])
                lengthen = self.get_exercise_dictionary(["49", "46", "56", "103", "9"])
                activate = self.get_exercise_dictionary(["10", "84", "50", "81"])
            else:
                inhibit = self.get_exercise_dictionary(["55", "44", "54", "4", "3"])
                lengthen = self.get_exercise_dictionary(["46", "56", "103"])
                activate = self.get_exercise_dictionary(["10", "84"])
            lower_back.add_exercise_phases(inhibit, lengthen, activate, True)

        return lower_back

    def get_body_part_priority(self, base_priority, soreness):

        if (soreness.historic_soreness_status == HistoricSorenessStatus.acute_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain_acute or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_soreness or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_soreness):
                return base_priority - 22  # reduces ranking by length of body part enumerations
        else:
            return base_priority

    def is_daily_or_persistent(self, soreness):

        if (soreness.historic_soreness_status is None or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_acute_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_soreness or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain or
                soreness.historic_soreness_status == HistoricSorenessStatus.persistent_soreness or
                soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_soreness or
                soreness.historic_soreness_status == HistoricSorenessStatus.dormant_cleared):
            return True
        else:
            return False

    def get_heat(self, current_date_time, historic_soreness_list):

        heat = None

        for h in historic_soreness_list:
            if h.first_reported is not None and not h.is_dormant_cleared():
                days_diff = (current_date_time - h.first_reported).days
                if days_diff >= 30:
                    heat = Heat(minutes=0)

        return heat
