import abc
from enum import Enum, IntEnum
import datetime
# import numpy as np
import logic.soreness_and_injury as soreness_and_injury


class TechnicalDifficulty(IntEnum):
    beginner = 0
    intermediate = 1
    advanced = 2


class ProgramType(Enum):
    comprehensive_warm_up = 0
    targeted_warm_up = 1
    comprehensive_recovery = 2
    targeted_recovery = 3
    long_term_recovery = 4
    corrective_exercises = 5


class Phase(IntEnum):
    inhibit = 0
    lengthen = 1
    activate = 2
    integrate = 3


class UnitOfMeasure(Enum):
    seconds = 0
    count = 1


class Tempo(Enum):
    controlled = 0


class ExercisePriority(IntEnum):
    present = 0
    high = 1
    avoid = 2


class Exercise(object):
    def __init__(self, library_id):
        self.id = library_id
        self.name = ""
        # self.body_parts_targeted = []
        self.min_reps = None
        self.max_reps = None
        self.min_sets = None
        self.max_sets = None
        self.bilateral = False
        self.progression_interval = 0
        self.exposure_target = 0
        self.unit_of_measure = UnitOfMeasure.seconds
        self.seconds_rest_between_sets = 0
        self.seconds_per_set = 0
        self.seconds_per_rep = 0
        self.progressions = []
        self.progresses_to = None
        self.technical_difficulty = TechnicalDifficulty.beginner
        self.program_type = ProgramType.comprehensive_warm_up

        self.tempo = Tempo.controlled
        self.cues = ""
        self.procedure = ""
        self.goal = ""
        self.equipment_required = None


class AssignedExercise(object):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0):
        self.exercise = Exercise(library_id)
        self.body_part_priority = body_part_priority
        self.body_part_exercise_priority = body_part_exercise_priority
        self.body_part_soreness_level = body_part_soreness_level

        self.athlete_id = ""
        self.reps_assigned = 0
        self.sets_assigned = 0
        self.expire_date_time = None
        self.position_order = 0

    '''
    def soreness_priority(self):
        return ExercisePriority.neutral
    '''
    def duration(self):
        if self.exercise.unit_of_measure == "count":
            return self.exercise.seconds_per_rep * self.reps_assigned * self.sets_assigned
        elif self.exercise.unit_of_measure == "seconds":
            return self.exercise.seconds_per_set * self.sets_assigned
        else:
            return None


class CompletedExercise(object):

    def __init__(self, athlete_id, exercise_id):
        self.athlete_id = athlete_id
        self.exercise_id = exercise_id
        self.exposures_completed = 0
        self.last_completed_date = None

    def increment(self):
        self.exposures_completed = self.exposures_completed + 1
        self.last_completed_date = datetime.date.today()


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
        self.duration_minutes_target = None

    def duration_minutes(self):
        return self.inhibit_minutes + self.lengthen_minutes + self.activate_minutes + self.integrate_minutes

    def sort_reverse_priority(self, assigned_exercise_list):
        # rank all exercise by reverse priority, assumes all body parts have same level of severity
        sorted_list = sorted(assigned_exercise_list,
                             key=lambda x: (x.body_part_exercise_priority, x.body_part_priority),
                             reverse=True)

        return sorted_list

    def sort_priority(self, assigned_exercise_list):
        # rank all exercise by priority, assumes all body parts have same level of severity
        sorted_list = sorted(assigned_exercise_list,
                             key=lambda x: (x.body_part_exercise_priority, x.body_part_priority),
                             reverse=False)

        return sorted_list

    def reduce_assigned_exercises(self, seconds_reduction_needed, assigned_exercise_list):
        assigned_exercise_list = self.sort_reverse_priority(assigned_exercise_list)
        while seconds_reduction_needed >= 0:
            for i in range(0, len(assigned_exercise_list)):
                if assigned_exercise_list[i].reps_assigned > assigned_exercise_list[i].exercise.min_reps:
                    assigned_exercise_list[i].reps_assigned = assigned_exercise_list[i].reps_assigned -1
                    seconds_reduction_needed -= assigned_exercise_list[i].exercise.seconds_per_rep
                elif assigned_exercise_list[i].sets_assigned > assigned_exercise_list[i].exercise.min_sets:
                    assigned_exercise_list[i].sets_assigned = assigned_exercise_list[i].sets_assigned - 1
                    seconds_reduction_needed -= assigned_exercise_list[i].exercise.seconds_per_set
                else:
                    # set it to zero for deletion later
                    seconds_reduction_needed -= assigned_exercise_list[i].duration()
                    assigned_exercise_list[i].reps_assigned = 0
                    assigned_exercise_list[i].sets_assigned = 0
                if seconds_reduction_needed <= 0:
                    break
            if seconds_reduction_needed <= 0:
                break

        assigned_exercise_list = list(ex for ex in assigned_exercise_list if ex.reps_assigned > 0
                                      and ex.sets_assigned > 0)
        assigned_exercise_list = self.sort_priority(assigned_exercise_list)

        return assigned_exercise_list

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

            self.inhibit_exercises = self.reduce_assigned_exercises(
                (self.inhibit_minutes * 60) - (self.inhibit_target_minutes * 60), self.inhibit_exercises)
            self.calculate_durations()
            self.lengthen_exercises = self.reduce_assigned_exercises(
                (self.lengthen_minutes * 60) - (self.lengthen_target_minutes * 60), self.lengthen_exercises)
            self.calculate_durations()
            self.activate_exercises = self.reduce_assigned_exercises(
                (self.activate_minutes * 60) - (self.activate_target_minutes * 60), self.activate_exercises)
            self.calculate_durations()

    def calculate_durations(self):
        inhibit_duration_list = list(ex.duration() for ex in self.inhibit_exercises if ex.duration() is not None)
        self.inhibit_minutes = sum(inhibit_duration_list) / 60

        lengthen_duration_list = list(ex.duration() for ex in self.lengthen_exercises if ex.duration() is not None)
        self.lengthen_minutes = sum(lengthen_duration_list) / 60

        activate_duration_list = list(ex.duration() for ex in self.activate_exercises if ex.duration() is not None)
        self.activate_minutes = sum(activate_duration_list) / 60

        self.integrate_minutes = 0

        self.inhibit_percentage = self.inhibit_minutes / (self.inhibit_minutes + self.lengthen_minutes +
                                                          self.activate_minutes + self.integrate_minutes)
        self.lengthen_percentage = self.lengthen_minutes / (self.inhibit_minutes + self.lengthen_minutes +
                                                            self.activate_minutes + self.integrate_minutes)
        self.activate_percentage = self.activate_minutes / (self.inhibit_minutes + self.lengthen_minutes +
                                                            self.activate_minutes + self.integrate_minutes)
        self.integrate_percentage = self.integrate_minutes / (self.inhibit_minutes + self.lengthen_minutes +
                                                              self.activate_minutes + self.integrate_minutes)
    '''
    def update(self, soreness_severity, soreness_exercises):

        for soreness_exercise in soreness_exercises:
            exercise_assignment = AssignedExercise()
            # exercise_assignment.exercise = soreness_exercise
            exercise_assignment.soreness_priority = \
                self.get_exercise_priority_from_soreness_level(soreness_severity, soreness_exercise)

            # TODO expand to accommodate if exercise already exists or if others already exist
            if isinstance(soreness_exercise, InhibitExercise):
                self.recommended_inhibit_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, LengthenExercise):
                    self.recommended_lengthen_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, ActivateExercise):
                    self.recommended_activate_exercises.append(exercise_assignment)
            elif isinstance(soreness_exercise, IntegrateExercise):
                    self.recommended_integrate_exercises.append(exercise_assignment)

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


class ExerciseAssignmentCalculator(object):

    def __init__(self, athlete_id, athlete_data_access, exercise_data_access):
        self.athlete_id = athlete_id
        self.athlete_dao = athlete_data_access
        self.exercise_dao = exercise_data_access
        self.exercise_library = exercise_data_access.get_exercise_library()
        self.exercises_for_body_parts = exercise_data_access.get_exercises_for_body_parts()

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

            assigned_exercise = AssignedExercise(target_exercise[0].id,
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

        exercise_assignments = ExerciseAssignments()
        exercise_assignments.inhibit_max_percentage = exercise_session.inhibit_max_percentage
        exercise_assignments.inhibit_target_minutes = exercise_session.inhibit_target_minutes
        exercise_assignments.activate_max_percentage = exercise_session.activate_max_percentage
        exercise_assignments.activate_target_minutes = exercise_session.activate_target_minutes
        exercise_assignments.lengthen_max_percentage = exercise_session.lengthen_max_percentage
        exercise_assignments.lengthen_target_minutes = exercise_session.lengthen_target_minutes

        # completed_exercises = self.athlete_dao.get_completed_exercises()
        completed_exercises = None
        body_part_exercises = self.exercises_for_body_parts()
        exercise_list = self.exercise_library

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
        exercise_assignments.scale_to_targets()

        return exercise_assignments


