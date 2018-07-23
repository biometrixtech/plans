from enum import Enum, IntEnum
from utils import parse_datetime
import datetime

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
        self.side = None


class DailySoreness(Soreness):

    def __init__(self):
        self.severity = None    # muscle_soreness_severity or joint_soreness_severity

        # self.descriptor = None  # soreness_descriptor

    def json_serialise(self):
        ret = {
            'body_part': self.body_part.location.value,
            'severity': self.severity,
            'side': self.side
        }
        return ret

class PostSessionSoreness(Soreness):

    def __init__(self):
        self.severity = 0
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
    general = 13
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

''' Deprecated
class DailyReadinessSurvey(object):

    def __init__(self):
        self.report_date_time = None
        self.soreness = []  # dailysoreness object array
        self.sleep_quality = None
        self.readiness = None

    def get_event_date(self):
        return datetime.datetime.strptime(self.report_date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
'''

class PostSessionSurvey(object):

    def __init__(self):
        self.report_date_time = None
        self.soreness = []  # dailysoreness object array
        self.session_rpe = None


class BodyPartMapping(object):

    def get_soreness_type(self, body_part_location):

        if (body_part_location == BodyPartLocation.hip_flexor or body_part_location == BodyPartLocation.knee
                or body_part_location == BodyPartLocation.ankle or body_part_location == BodyPartLocation.foot
                or body_part_location == BodyPartLocation.lower_back):
            return SorenessType.joint_related
        else:
            return SorenessType.muscle_related

class SorenessCalculator(object):

    def __init__(self):
        self.surveys = []

    def get_soreness_summary_from_surveys(self, last_daily_readiness_survey, last_post_session_surveys,
                                          trigger_date_time):
        """
        :param last_daily_readiness_survey: DailyReadiness
        :param last_post_session_survey:
        :param trigger_date_time: datetime
        :return:
        """

        soreness_list = []

        if last_daily_readiness_survey is not None:

            daily_readiness_survey_age = trigger_date_time - last_daily_readiness_survey.get_event_date()

            if daily_readiness_survey_age.total_seconds() <= 172800:  # within 48 hours so valid
                for s in last_daily_readiness_survey.soreness:
                    s.reported_date_time = last_daily_readiness_survey.get_event_date()
                    soreness_list.append(s)

        if last_post_session_surveys is not None:

            for last_post_session_survey in last_post_session_surveys:

                last_post_session_survey_age = trigger_date_time - last_post_session_survey.get_event_date()

                if last_post_session_survey_age.total_seconds() <= 172800:  # within 48 hours so valid

                    last_post_session_survey_datetime = last_post_session_survey.event_date_time

                    if (last_post_session_survey.survey.soreness is not None and
                            len(last_post_session_survey.survey.soreness) > 0):

                        for s in last_post_session_survey.survey.soreness:
                            updated = False
                            for r in range(0, len(soreness_list)):

                                if (soreness_list[r].body_part.location.value == s.body_part.location.value and
                                        soreness_list[r].side == s.side and
                                        soreness_list[r].reported_date_time < last_post_session_survey_datetime):
                                    # soreness_list[r].severity = max(soreness_list[r].severity, s.severity)
                                    soreness_list[r].severity = s.severity
                                    soreness_list[r].reported_date_time = last_post_session_survey_datetime
                                updated = True
                            if not updated:
                                soreness_list.append(s)
                        else:
                            # clear out any soreness to date
                            soreness_list = [s for s in soreness_list if s.reported_date_time >=
                                             last_post_session_survey_datetime]

        return soreness_list




