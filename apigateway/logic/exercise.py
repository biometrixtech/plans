import abc
from enum import Enum, IntEnum
import datetime
import soreness_and_injury


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
        self.time_per_set = 0
        self.time_per_rep = 0
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

    def soreness_priority(self):
        return ExercisePriority.neutral


class InhibitExercise(AssignedExercise):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0):
        AssignedExercise.__init__(library_id, body_part_priority, body_part_exercise_priority, body_part_soreness_level)

    def soreness_priority(self):
        if self.body_part_soreness_level is None or self.body_part_soreness_level <= 1:
            return ExercisePriority.present
        elif 2 <= self.body_part_soreness_level < 4:
            return ExercisePriority.high
        else:
            return ExercisePriority.avoid


class LengthenExercise(AssignedExercise):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0):
        AssignedExercise.__init__(library_id, body_part_priority, body_part_exercise_priority, body_part_soreness_level)

    def soreness_priority(self):
        if self.body_part_soreness_level is None or self.body_part_soreness_level <= 1:
            return ExercisePriority.present
        elif 2 <= self.body_part_soreness_level < 4:
            return ExercisePriority.high
        else:
            return ExercisePriority.avoid


class ActivateExercise(AssignedExercise):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0):
        AssignedExercise.__init__(library_id, body_part_priority, body_part_exercise_priority, body_part_soreness_level)

    def soreness_priority(self):
        if self.body_part_soreness_level is None or self.body_part_soreness_level <= 1:
            return ExercisePriority.present
        elif self.body_part_soreness_level == 2:
            return ExercisePriority.high
        else:
            return ExercisePriority.avoid


class IntegrateExercise(AssignedExercise):
    def __init__(self, library_id, body_part_priority=0, body_part_exercise_priority=0, body_part_soreness_level=0):
        AssignedExercise.__init__(library_id, body_part_priority, body_part_exercise_priority, body_part_soreness_level)

    def soreness_priority(self):
        return ExercisePriority.avoid


class CompletedExercise(object):

    def __init__(self, athlete_id, exercise_id):
        self.athlete_id = athlete_id
        self.exercise_id = exercise_id
        self.exposures_completed = 0
        self.last_completed_date = None

    def increment(self):
        self.exposures_completed = self.exposures_completed + 1
        self.last_completed_date = datetime.date.today()


class ExerciseRecommendations(object):

    def __init__(self):
        self.recommended_inhibit_exercises = []
        self.recommended_lengthen_exercises = []
        self.recommended_activate_exercises = []
        self.recommended_integrate_exercises = []

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

    # def create_assigned_exercise(self, target_exercise, body_part_priority, body_part_exercise_priority, body_part_soreness_level):

    def populate_exercise_recommendations(self, exercise_session, soreness_list):

        inhibit_exercise_list = []
        lengthen_exercise_list = []
        activate_exercise_list = []

        completed_exercises = self.athlete_dao.get_completed_exercises()
        body_part_exercises = self.get_exercises_for_body_parts()
        exercise_list = self.exercise_dao.get_exercise_library()

        for soreness in soreness_list:
            body_part = [b for b in body_part_exercises
                         if b.body_part_location == soreness.body_part.body_part_location]
            if exercise_session.inhibit_target_minutes is not None and exercise_session.inhibit_target_minutes > 0:
                for inhibit_exercise in body_part.inhibit_exercises:
                    # get details from library
                    target_exercise = [ex for ex in exercise_list if ex.library_id == inhibit_exercise.library_id]

                    # did athlete already complete this exercise
                    completed_exercise = [ex for ex in completed_exercises if
                                          ex.library_id == target_exercise.library_id]

                    # if completed_exercise is not None:
                    # do stuff

                    # determine reps and sets

                    assigned_exercise = InhibitExercise(target_exercise.library_id,
                                                        inhibit_exercise.body_part_priority,
                                                        inhibit_exercise.body_part_exercise_priority,
                                                        soreness.severity)
                    assigned_exercise.exercise = target_exercise
                    assigned_exercise.reps_assigned = target_exercise.max_reps
                    assigned_exercise.sets_assigned = target_exercise.max_sets

                    inhibit_exercise_list.append(assigned_exercise)

            if exercise_session.lengthen_target_minutes is not None and exercise_session.lengthen_target_minutes > 0:
                lengthen_exercise_list.extend(body_part.lengthen_exercises)
            if exercise_session.activate_target_minutes is not None and exercise_session.activate_target_minutes > 0:
                activate_exercise_list.extend(body_part.activate_exercises)

        exercise_recommendations = ExerciseRecommendations()



    def get_exercises_for_body_parts(self):

        body_parts = []

        # lower back
        lower_back = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.lower_back, 1)
        lower_back.inhibit_exercises.append(InhibitExercise(55, 1))
        lower_back.inhibit_exercises.append(InhibitExercise(54, 2))
        lower_back.inhibit_exercises.append(InhibitExercise(4, 3))
        lower_back.inhibit_exercises.append(InhibitExercise(5, 4))
        lower_back.inhibit_exercises.append(InhibitExercise(48, 5))
        lower_back.inhibit_exercises.append(InhibitExercise(3, 6))

        lower_back.lengthen_exercises.append(LengthenExercise(49, 1))
        lower_back.lengthen_exercises.append(LengthenExercise(57, 2))
        lower_back.lengthen_exercises.append(LengthenExercise(56, 3))
        lower_back.lengthen_exercises.append(LengthenExercise(8, 4))

        posterior_pelvic_tilt = ActivateExercise(79, 1)
        posterior_pelvic_tilt.progressions = [80]

        lower_back.activate_exercises.append(posterior_pelvic_tilt)

        hip_bridge_progression = ActivateExercise(10, 2)
        hip_bridge_progression.progressions = [12, 11, 13]

        lower_back.activate_exercises.append(hip_bridge_progression)

        core_strength_progression = ActivateExercise(85, 3)
        core_strength_progression.progressions = [86, 87, 88, 89, 90, 91, 92]

        lower_back.activate_exercises.append(core_strength_progression)

        body_parts.append(lower_back)

        # hip

        hip = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.hip_flexor, 2)

        hip.inhibit_exercises.append(InhibitExercise(3, 1))
        hip.inhibit_exercises.append(InhibitExercise(48, 2))
        hip.inhibit_exercises.append(InhibitExercise(54, 3))
        hip.inhibit_exercises.append(InhibitExercise(1, 4))
        hip.inhibit_exercises.append(InhibitExercise(44, 5))
        hip.inhibit_exercises.append(InhibitExercise(4, 6))
        hip.inhibit_exercises.append(InhibitExercise(5, 7))
        hip.inhibit_exercises.append(InhibitExercise(2, 8))

        hip.lengthen_exercises.append(LengthenExercise(49, 1))
        hip.lengthen_exercises.append(LengthenExercise(9, 2))
        hip.lengthen_exercises.append(LengthenExercise(46, 3))
        hip.lengthen_exercises.append(LengthenExercise(28, 4))

        posterior_pelvic_tilt = ActivateExercise(79, 1)
        posterior_pelvic_tilt.progressions = [80]

        hip.activate_exercises.append(posterior_pelvic_tilt)

        hip_bridge_progression = ActivateExercise(10, 2)
        hip_bridge_progression.progressions = [12, 11, 13]

        hip.activate_exercises.append(hip_bridge_progression)

        hip.activate_exercises.append(ActivateExercise(50, 3))
        hip.activate_exercises.append(ActivateExercise(84, 4))

        glute_activation = ActivateExercise(34, 5)
        glute_activation.progressions = [35]
        hip.activate_exercises.append(glute_activation)

        body_parts.append(hip)

        # glutes

        glutes = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation.glutes, 3)

        glutes.inhibit_exercises.append(InhibitExercise(44, 1))
        glutes.inhibit_exercises.append(InhibitExercise(3, 2))

        it_band = InhibitExercise(4, 3)
        it_band.progressions = [5]
        glutes.InhibitExercise.append(it_band)

        glutes.inhibit_exercises.append(InhibitExercise(54, 4))
        glutes.inhibit_exercises.append(InhibitExercise(2, 5))

        glutes.lengthen_exercises.append(LengthenExercise(9, 1))
        glutes.lengthen_exercises.append(LengthenExercise(46, 2))

        stretching_erectors = LengthenExercise(103, 3)
        stretching_erectors.progressions = [104]
        glutes.lengthen_exercises.append(stretching_erectors)

        glutes.lengthen_exercises.append(LengthenExercise(28, 4))

        gastroc_soleus = LengthenExercise(25, 5)
        gastroc_soleus.progressions = [26]
        glutes.lengthen_exercises.append(gastroc_soleus)

        hip_bridge_progression = ActivateExercise(10, 1)
        hip_bridge_progression.progressions = [12, 11, 13]

        glutes.activate_exercises.append(hip_bridge_progression)

        glute_activation = ActivateExercise(81, 2)
        glute_activation.progressions = [82, 83]

        glutes.activate_exercises.append(glute_activation)

        glute_activation_2 = ActivateExercise(34, 3)
        glute_activation_2.progressions = [35]
        glutes.activate_exercises.append(glute_activation_2)

        core_strength_progression = ActivateExercise(85, 4)
        core_strength_progression.progressions = [86, 87, 88]

        glutes.activate_exercises.append(core_strength_progression)

        core_strength_progression_2 = ActivateExercise(89, 5)
        core_strength_progression_2.progressions = [90, 91, 92]

        glutes.activate_exercises.append(core_strength_progression_2)

        body_parts.append(glutes)

        '''
        body_parts.append(BodyPart(BodyPartLocation.abdominals), 4)
        body_parts.append(BodyPart(BodyPartLocation.hamstrings), 5)
        body_parts.append(BodyPart(BodyPartLocation.outer_thigh), 6)
        body_parts.append(BodyPart(BodyPartLocation.groin), 7)
        body_parts.append(BodyPart(BodyPartLocation.quads), 8)
        body_parts.append(BodyPart(BodyPartLocation.knee), 9)
        body_parts.append(BodyPart(BodyPartLocation.calves), 10)
        body_parts.append(BodyPart(BodyPartLocation.shin), 11)
        body_parts.append(BodyPart(BodyPartLocation.ankle), 12)
        body_parts.append(BodyPart(BodyPartLocation.foot), 13)
        '''

        return body_parts


