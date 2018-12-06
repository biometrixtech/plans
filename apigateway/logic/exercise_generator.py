# import numpy as np


class ExerciseAssignments(object):

    def __init__(self):
        self.inhibit_exercises = []
        self.lengthen_exercises = []
        self.activate_exercises = []
        self.integrate_exercises = []
        self.inhibit_minutes = 0
        self.lengthen_minutes = 0
        self.activate_minutes = 0
        self.integrate_minutes = 0
        self.inhibit_iterations = 0
        self.lengthen_iterations = 0
        self.activate_iterations = 0
        self.integrate_iterations = 0
        self.inhibit_percentage = None
        self.lengthen_percentage = None
        self.activate_percentage = None
        self.integrate_percentage = None
        self.inhibit_target_minutes = 0
        self.lengthen_target_minutes = 0
        self.activate_target_minutes = 0
        self.integrate_target_minutes = None
        self.inhibit_max_percentage = None
        self.lengthen_max_percentage = None
        self.activate_max_percentage = None
        self.integrate_max_percentage = None
        self.duration_minutes_target = 0

    def duration_minutes(self):
        return self.inhibit_minutes + self.lengthen_minutes + self.activate_minutes + self.integrate_minutes

    def sort_reverse_priority(self, assigned_exercise_list):
        # rank all exercise by reverse priority, assumes all body parts have same level of severity
        sorted_list = []
        severity_5_list = [a for a in assigned_exercise_list if 4 < a.body_part_soreness_level]
        severity_4_list = [a for a in assigned_exercise_list if 3 < a.body_part_soreness_level <= 4]
        severity_3_list = [a for a in assigned_exercise_list if 2 < a.body_part_soreness_level <= 3]
        severity_2_list = [a for a in assigned_exercise_list if 1 < a.body_part_soreness_level <= 2]
        severity_1_list = [a for a in assigned_exercise_list if a.body_part_soreness_level <= 1]

        sorted_1_list = sorted(severity_1_list,
                               key=lambda x: (x.body_part_exercise_priority, x.body_part_priority),
                               reverse=True)
        sorted_2_list = sorted(severity_2_list,
                               key=lambda x: (x.body_part_exercise_priority, x.body_part_priority),
                               reverse=True)
        sorted_3_list = sorted(severity_3_list,
                               key=lambda x: (x.body_part_exercise_priority, x.body_part_priority),
                               reverse=True)
        sorted_4_list = sorted(severity_4_list,
                               key=lambda x: (x.body_part_exercise_priority, x.body_part_priority),
                               reverse=True)
        sorted_5_list = sorted(severity_5_list,
                               key=lambda x: (x.body_part_exercise_priority, x.body_part_priority),
                               reverse=True)

        sorted_list.extend(sorted_1_list)
        sorted_list.extend(sorted_2_list)
        sorted_list.extend(sorted_3_list)
        sorted_list.extend(sorted_4_list)
        sorted_list.extend(sorted_5_list)

        return sorted_list

    def sort_priority(self, assigned_exercise_list):
        # rank all exercise by priority, assumes all body parts have same level of severity
        sorted_list = sorted(assigned_exercise_list,
                             key=lambda x: (x.body_part_exercise_priority, x.body_part_priority),
                             reverse=False)

        return sorted_list

    def get_reduced_rep_value(self, current_reps_assigned):

        if current_reps_assigned == 15:
            return 3
        elif current_reps_assigned == 12:
            return 2
        else:
            return 0

    def reduce_assigned_exercises(self, seconds_reduction_needed, assigned_exercise_list):
        assigned_exercise_list = self.sort_reverse_priority(assigned_exercise_list)
        iterations = 0
        while seconds_reduction_needed >= 0 and iterations < 100:
            for i in range(0, len(assigned_exercise_list)):
                if assigned_exercise_list[i].reps_assigned > assigned_exercise_list[i].exercise.min_reps:
                    rep_reducer = self.get_reduced_rep_value(assigned_exercise_list[i].reps_assigned)
                    assigned_exercise_list[i].reps_assigned = assigned_exercise_list[i].reps_assigned - rep_reducer
                    if assigned_exercise_list[i].exercise.bilateral:
                        seconds_reduction_needed -= (assigned_exercise_list[i].exercise.seconds_per_rep
                                                     * 2 * rep_reducer)
                    else:
                        seconds_reduction_needed -= assigned_exercise_list[i].exercise.seconds_per_rep * rep_reducer
                elif assigned_exercise_list[i].sets_assigned > assigned_exercise_list[i].exercise.min_sets:
                    assigned_exercise_list[i].sets_assigned = assigned_exercise_list[i].sets_assigned - 1
                    bilateral_factor = 1
                    if assigned_exercise_list[i].exercise.bilateral:
                        bilateral_factor = 2

                    if assigned_exercise_list[i].exercise.unit_of_measure.name == "seconds":
                        seconds_reduction_needed -= (assigned_exercise_list[i].exercise.seconds_per_set *
                                                     bilateral_factor)
                    else:
                        seconds_reduction_needed -= assigned_exercise_list[i].exercise.seconds_per_rep * \
                                                    bilateral_factor * assigned_exercise_list[i].reps_assigned
                else:
                    # set it to zero for deletion later
                    seconds_reduction_needed -= assigned_exercise_list[i].duration()
                    assigned_exercise_list[i].reps_assigned = 0
                    assigned_exercise_list[i].sets_assigned = 0
                iterations = iterations + 1
                if seconds_reduction_needed <= 0:
                    break
            if seconds_reduction_needed <= 0:
                break

        assigned_exercise_list = list(ex for ex in assigned_exercise_list if ex.reps_assigned > 0
                                      and ex.sets_assigned > 0)
        assigned_exercise_list = self.sort_priority(assigned_exercise_list)

        return assigned_exercise_list, iterations

    def remove_duplicate_assigned_exercises(self, assigned_exercise_list):

        unified_list = []

        for a in range(0, len(assigned_exercise_list)):
            updated = False
            for i, ex in enumerate(unified_list):
                if ex.exercise.id == assigned_exercise_list[a].exercise.id:
                    unified_list[i].body_part_priority = min(unified_list[i].body_part_priority,
                                                             assigned_exercise_list[a].body_part_priority)
                    unified_list[i].body_part_exercise_priority = \
                        min(unified_list[i].body_part_exercise_priority,
                            assigned_exercise_list[a].body_part_exercise_priority)
                    unified_list[i].body_part_soreness_level = \
                        max(unified_list[i].body_part_soreness_level,
                            assigned_exercise_list[a].body_part_soreness_level)
                    updated = True
            if not updated:
                unified_list.append(assigned_exercise_list[a])

        return unified_list

    def scale_to_targets(self):

        self.inhibit_exercises = self.remove_duplicate_assigned_exercises(self.inhibit_exercises)
        self.lengthen_exercises = self.remove_duplicate_assigned_exercises(self.lengthen_exercises)
        self.activate_exercises = self.remove_duplicate_assigned_exercises(self.activate_exercises)

        self.calculate_durations()
        if (self.inhibit_max_percentage is not None and
                self.lengthen_max_percentage is not None and
                self.activate_max_percentage is not None and
                self.inhibit_percentage <= self.inhibit_max_percentage and
                self.lengthen_percentage <= self.lengthen_max_percentage and
                self.activate_percentage <= self.activate_max_percentage and
                # self.integrate_percentage <= self.integrate_max_percentage and
                self.duration_minutes() <= self.duration_minutes_target):
            return

        else:
            if self.inhibit_exercises is not None and len(self.inhibit_exercises) > 0:
                self.inhibit_exercises, self.inhibit_iterations = self.reduce_assigned_exercises(
                    (self.inhibit_minutes * 60) - (self.inhibit_target_minutes * 60), self.inhibit_exercises)
                self.calculate_durations()
            if self.lengthen_exercises is not None and len(self.lengthen_exercises) > 0:
                self.lengthen_exercises, self.lengthen_iterations = self.reduce_assigned_exercises(
                    (self.lengthen_minutes * 60) - (self.lengthen_target_minutes * 60), self.lengthen_exercises)
                self.calculate_durations()
            if self.activate_exercises is not None and len(self.activate_exercises) > 0:
                self.activate_exercises, self.activate_iterations = self.reduce_assigned_exercises(
                    (self.activate_minutes * 60) - (self.activate_target_minutes * 60), self.activate_exercises)
                self.calculate_durations()

    def calculate_durations(self):
        self.inhibit_minutes = sum(filter(None, [ex.duration() for ex in self.inhibit_exercises])) / 60
        self.lengthen_minutes = sum(filter(None, [ex.duration() for ex in self.lengthen_exercises])) / 60
        self.activate_minutes = sum(filter(None, [ex.duration() for ex in self.activate_exercises])) / 60
        self.integrate_minutes = 0

        total_minutes = self.inhibit_minutes + self.lengthen_minutes + self.activate_minutes + self.integrate_minutes
        if total_minutes == 0:
            self.inhibit_percentage = self.lengthen_percentage = self.activate_percentage = self.integrate_percentage = 0
        else:
            self.inhibit_percentage = self.inhibit_minutes / total_minutes
            self.lengthen_percentage = self.lengthen_minutes / total_minutes
            self.activate_percentage = self.activate_minutes / total_minutes
            self.integrate_percentage = self.integrate_minutes / total_minutes
    '''
    def update(self, soreness_severity, soreness_exercises):

        for soreness_exercise in soreness_exercises:
            exercise_assignment = AssignedExercise()
            # exercise_assignment.exercise = soreness_exercise
            exercise_assignment.soreness_priority = \
                self.get_exercise_priority_from_soreness_level(soreness_severity, soreness_exercise)

            # TODO expand to accommodate if exercise already exists or if others already exist
            if isinstance(soreness_exercise, InhibitExercise):
                self.inhibit_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, LengthenExercise):
                    self.lengthen_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, ActivateExercise):
                    self.activate_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, IntegrateExercise):
                    self.integrate_exercises.append(exercise_assignment)

    def get_exercise_priority_from_soreness_level(self, soreness_level, soreness_exercise):

        exercise_priority = ExercisePriority

        if isinstance(soreness_exercise, InhibitExercise) or isinstance(soreness_exercise, LengthenExercise):

            if soreness_level is None or soreness_level <= 1:
                return exercise_priority.present
            elif 2 <= soreness_level < 4:
                return exercise_priority.high
            else:
                return exercise_priority.avoid

        elif isinstance(soreness_exercise, ActivateExercise):

            if soreness_level is None or soreness_level <= 1:
                return exercise_priority.present
            elif soreness_level == 2:
                return exercise_priority.high
            else:
                return exercise_priority.avoid

        else:
            return exercise_priority.avoid
    '''


