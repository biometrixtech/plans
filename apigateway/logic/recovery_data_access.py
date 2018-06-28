import recovery
import exercise
import soreness_and_injury


class RecoveryDataAccess(object):

    def get_exercises_for_soreness(self, soreness_list):
        exercises = []
        for soreness in soreness_list:
            body_part_exercises = self.get_exericses_for_soreness(soreness)
            exercises.extend(body_part_exercises)
        return exercises

    def get_exercises_for_injury_history(self, injury_history):
        exercises = []
        for injury in injury_history:
            injury_exercises = self.get_exericses_for_injury(injury)
            exercises.extend(injury_exercises)
        return exercises

    def get_exericses_for_injury(self, injury):

        exercises = []

        if (injury.injury_type == soreness_and_injury.InjuryType.ligament
                and injury.body_part == soreness_and_injury.BodyPart.ankle
                and injury.injury_descriptor == soreness_and_injury.InjuryDescriptor.sprain):
            # injury ankle sprain/instability or body part soreness = ankle

            # Follow NASM recommended inhibit -> lengthen -> activate -> integrate
            exercise_1 = exercise.Exercise()
            exercise_1.name = "SMR - Calves"
            exercises.append(exercise_1)

            exercise_2 = exercise.Exercise()
            exercise_2.name = "SMR - Tibialis Anterior"
            exercises.append(exercise_2)

            exercise_3 = exercise.Exercise()    # progression!
            exercise_3.name = "4-way towel isometrics"
            exercises.append(exercise_3)

            exercise_4 = exercise.Exercise()
            exercise_4.name = "Step-Up to Balance"
            exercises.append(exercise_4)

            return exercises
        else:
            return None

    def get_exericses_for_soreness(self, soreness):

        exercises = []

        if (soreness.type == soreness_and_injury.SorenessType.joint_related
                and soreness.body_part == soreness_and_injury.BodyPart.knee):
            # body part soreness = knee

            # Follow NASM recommended inhibit -> lengthen -> activate -> integrate
            exercise_1 = exercise.Exercise()
            exercise_1.name = "SMR - Gastrocnemius/Soleus"
            exercises.append(exercise_1)

            exercise_2 = exercise.Exercise()
            exercise_2.name = "Gastrocnemius Static Stretch"
            exercises.append(exercise_2)

            exercise_3 = exercise.Exercise()
            exercise_3.name = "Resisted Ankle Dorsiflexion"
            exercises.append(exercise_3)

            exercise_4 = exercise.Exercise()
            exercise_4.name = "Ball Squats"    # progression!
            exercises.append(exercise_4)

            return exercises
        else:
            return None
