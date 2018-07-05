from enum import Enum, IntEnum
import exercise

class SorenessType(Enum):
    muscle_related = 0
    joint_related = 1


class MuscleSorenessSeverity(IntEnum):
    a_little_tight_sore = 1
    sore_can_move_ok = 2
    limits_movement = 3
    struggling_to_move = 4
    painful_to_move = 5


class JointSorenessSeverity(IntEnum):
    discomfort = 1
    dull_ache = 2
    more_severe_dull_ache = 3
    sharp_pain = 4
    inability_to_move = 5

'''Deprecating
class InjuryDescriptor(Enum):
    contusion = 0
    sprain = 1
    strain = 2
    dislocation = 3
    fracture = 4
    pain = 5
    other = 6
'''

class Soreness(object):
    def __init__(self):
        self.type = None  # soreness_type
        self.body_part = None
        self.reported_date_time = None


class DailySoreness(Soreness):

    def __init__(self):
        self.severity = None    # muscle_soreness_severity or joint_soreness_severity

        # self.descriptor = None  # soreness_descriptor


class PostSessionSoreness(Soreness):

    def __init__(self):
        self.discomfort_level = 0
        self.sustained_in_practice = False
        self.limited_performance = 0
        self.limited_how_much_i_could_do = 0


class InjuryStatus(Enum):
    healthy = 0
    healthy_chronically_injured = 1
    returning_from_injury = 2


class BodyPartLocation(Enum):
    head = 0
    shoulder = 1
    chest = 2
    abdominals = 3
    hip_flexor = 4
    groin = 5
    quads = 6
    knee = 7
    shin = 8
    ankle = 9
    foot = 10
    outer_thigh = 11
    lower_back = 12
    glutes = 14
    hamstrings = 15
    calves = 16
    achilles = 17


class BodyPart(object):

    def __init__(self, body_part_location, treatment_priority):
        self.location = body_part_location
        self.treatment_priority = treatment_priority
        self.inhibit_exercises = []
        self.lengthen_exercises = []
        self.activate_exercises = []
        self.integrate_exercises = []


class Injury(object):

    def __init__(self):
        self.body_part = None
        # self.injury_type = None
        # self.injury_descriptor = None
        self.date = None
        # self.days_missed = DaysMissedDueToInjury.less_than_7_days
        self.still_have_symptoms = False
        self.medically_cleared = True


'''Deprecating
class InjuryType(Enum):
    muscle = auto()
    ligament = auto()
    tendon = auto()
    bone = auto()
'''
'''Deprecating
class DaysMissedDueToInjury(IntEnum):
    less_than_7_days = 0
    one_four_weeks = 1
    one_three_months = 2
'''


class DailyReadinessSurvey(object):

    def __init__(self):
        self.report_date_time = None
        self.soreness = []  # dailysoreness object array
        self.sleep_quality = None
        self.readiness = None


class PostSessionSurvey(object):

    def __init__(self):
        self.report_date_time = None
        self.soreness = []  # dailysoreness object array
        self.session_rpe = None


class SorenessCalculator(object):

    def __init__(self):
        self.surveys = []

    def get_body_parts(self):

        body_parts = []

        # lower back
        lower_back = BodyPart(BodyPartLocation.lower_back, 1)
        lower_back.inhibit_exercises.append(exercise.InhibitExercise(55, 1))
        lower_back.inhibit_exercises.append(exercise.InhibitExercise(54, 2))
        lower_back.inhibit_exercises.append(exercise.InhibitExercise(4, 3))
        lower_back.inhibit_exercises.append(exercise.InhibitExercise(5, 4))
        lower_back.inhibit_exercises.append(exercise.InhibitExercise(48, 5))
        lower_back.inhibit_exercises.append(exercise.InhibitExercise(3, 6))

        lower_back.lengthen_exercises.append(exercise.LengthenExercise(49, 1))
        lower_back.lengthen_exercises.append(exercise.LengthenExercise(57, 2))
        lower_back.lengthen_exercises.append(exercise.LengthenExercise(56, 3))
        lower_back.lengthen_exercises.append(exercise.LengthenExercise(8, 4))

        posterior_pelvic_tilt = exercise.ActivateExercise(79, 1)
        posterior_pelvic_tilt.progressions = [80]

        lower_back.activate_exercises.append(posterior_pelvic_tilt)

        hip_bridge_progression = exercise.ActivateExercise(10, 2)
        hip_bridge_progression.progressions = [12, 11, 13]

        lower_back.activate_exercises.append(hip_bridge_progression)

        core_strength_progression = exercise.ActivateExercise(85, 3)
        core_strength_progression.progressions = [86, 87, 88, 89, 90, 91, 92]

        lower_back.activate_exercises.append(core_strength_progression)

        body_parts.append(lower_back)

        # hip

        hip = BodyPart(BodyPartLocation.hip_flexor, 2)

        hip.inhibit_exercises.append(exercise.InhibitExercise(3, 1))
        hip.inhibit_exercises.append(exercise.InhibitExercise(48, 2))
        hip.inhibit_exercises.append(exercise.InhibitExercise(54, 3))
        hip.inhibit_exercises.append(exercise.InhibitExercise(1, 4))
        hip.inhibit_exercises.append(exercise.InhibitExercise(44, 5))
        hip.inhibit_exercises.append(exercise.InhibitExercise(4, 6))
        hip.inhibit_exercises.append(exercise.InhibitExercise(5, 7))
        hip.inhibit_exercises.append(exercise.InhibitExercise(2, 8))

        hip.lengthen_exercises.append(exercise.LengthenExercise(49, 1))
        hip.lengthen_exercises.append(exercise.LengthenExercise(9, 2))
        hip.lengthen_exercises.append(exercise.LengthenExercise(46, 3))
        hip.lengthen_exercises.append(exercise.LengthenExercise(28, 4))

        posterior_pelvic_tilt = exercise.ActivateExercise(79, 1)
        posterior_pelvic_tilt.progressions = [80]

        hip.activate_exercises.append(posterior_pelvic_tilt)

        hip_bridge_progression = exercise.ActivateExercise(10, 2)
        hip_bridge_progression.progressions = [12, 11, 13]

        hip.activate_exercises.append(hip_bridge_progression)

        hip.activate_exercises.append(exercise.ActivateExercise(50, 3))
        hip.activate_exercises.append(exercise.ActivateExercise(84, 4))

        glute_activation = exercise.ActivateExercise(34, 5)
        glute_activation.progressions = [35]
        hip.activate_exercises.append(glute_activation)

        body_parts.append(hip)

        # glutes

        glutes = BodyPart(BodyPartLocation.glutes, 3)

        glutes.inhibit_exercises.append(exercise.InhibitExercise(44, 1))
        glutes.inhibit_exercises.append(exercise.InhibitExercise(3, 2))

        it_band = exercise.InhibitExercise(4, 3)
        it_band.progressions = [5]
        glutes.InhibitExercise.append(it_band)

        glutes.inhibit_exercises.append(exercise.InhibitExercise(54, 4))
        glutes.inhibit_exercises.append(exercise.InhibitExercise(2, 5))

        glutes.lengthen_exercises.append(exercise.LengthenExercise(9, 1))
        glutes.lengthen_exercises.append(exercise.LengthenExercise(46, 2))

        stretching_erectors = exercise.lengthen_exercises(103, 3)
        stretching_erectors.progressions = [104]
        glutes.lengthen_exercises.append(stretching_erectors)

        glutes.lengthen_exercises.append(exercise.LengthenExercise(28, 4))

        gastroc_soleus = exercise.lengthen_exercises(25, 5)
        gastroc_soleus.progressions = [26]
        glutes.lengthen_exercises.append(gastroc_soleus)

        hip_bridge_progression = exercise.ActivateExercise(10, 1)
        hip_bridge_progression.progressions = [12, 11, 13]

        glutes.activate_exercises.append(hip_bridge_progression)

        glute_activation = exercise.ActivateExercise(81, 2)
        glute_activation.progressions = [82, 83]

        glutes.activate_exercises.append(glute_activation)

        glute_activation_2 = exercise.ActivateExercise(34, 3)
        glute_activation_2.progressions = [35]
        glutes.activate_exercises.append(glute_activation_2)

        core_strength_progression = exercise.ActivateExercise(85, 4)
        core_strength_progression.progressions = [86, 87, 88]

        glutes.activate_exercises.append(core_strength_progression)

        core_strength_progression_2 = exercise.ActivateExercise(89, 5)
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

    def get_soreness_summary_from_surveys(self, last_daily_readiness_survey, last_post_session_survey,
                                          trigger_date_time):

        soreness_list = []

        if last_daily_readiness_survey is not None:

            daily_readiness_survey_age = trigger_date_time - last_daily_readiness_survey.report_date_time

            if daily_readiness_survey_age.total_seconds() <= 172800:  # within 48 hours so valid
                for s in last_daily_readiness_survey.soreness:
                    soreness_list.append(s)

        if last_post_session_survey is not None:

            last_post_session_survey_age = trigger_date_time - last_post_session_survey.report_date_time

            if last_post_session_survey_age.total_seconds() <= 172800:  # within 48 hours so valid

                for s in last_post_session_survey.soreness:
                    updated = False
                    for r in range(0, len(soreness_list)):
                        if soreness_list[r].body_part == s.body_part:
                            soreness_list[r].severity = max(soreness_list[r].severity, s.severity)
                            updated = True
                    if not updated:
                        soreness_list.append(s)

        return soreness_list




