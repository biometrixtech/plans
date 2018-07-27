import abc
from enum import Enum
import uuid
import datetime
from serialisable import Serialisable
import logic.exercise_generator as exercise
from utils import format_datetime, parse_datetime


class SessionType(Enum):
    practice = 0
    strength_and_conditioning = 1
    game = 2
    tournament = 3
    bump_up = 4
    corrective = 5


class DayOfWeek(Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class Session(Serialisable, metaclass=abc.ABCMeta):

    def __init__(self):
        self.id = None
        self.duration_sensor = None
        self.external_load = None
        self.high_intensity_load = None
        self.mod_intensity_load = None
        self.low_intensity_load = None
        self.high_intensity_minutes = None
        self.mod_intensity_minutes = None
        self.low_intensity_minutes = None
        self.high_intensity_RPE = None
        self.mod_intensity_RPE = None
        self.low_intensity_RPE = None
        self.post_session_soreness = []     # post_session_soreness object array
        self.date = None
        self.time = None
        self.duration_minutes = None
        self.sensor_start_date_time = None
        self.sensor_end_date_time = None
        self.day_of_week = DayOfWeek.monday
        self.estimated = False
        self.internal_load_imputed = False
        self.external_load_imputed = False
        self.data_transferred = False
        self.movement_limited = False
        self.same_muscle_discomfort_over_72_hrs = False

        # post-session
        self.post_session_survey = None
        self.session_RPE = None
        self.performance_level = 100  # only answered if there is discomfort
        self.completion_percentage = 100    # only answered if there is discomfort
        self.sustained_injury_or_pain = False
        self.description = ""

    def __setattr__(self, name, value):
        if name in ['time', 'sensor_start_date_time', 'sensor_end_date_time']:
            if not isinstance(value, datetime.datetime) and value is not None:
                value = parse_datetime(value)
        super().__setattr__(name, value)

    @abc.abstractmethod
    def session_type(self):
        return SessionType.practice

    @abc.abstractmethod
    def create(self):
        return None

    @abc.abstractmethod
    def missing_post_session_survey(self):
        if self.session_RPE is None:
            return True
        elif self.post_session_soreness is None and (self.movement_limited or self.same_muscle_discomfort_over_72_hrs):
            return True
        else:
            return False

    @abc.abstractmethod
    def in_daily_plan(self, date):
        if self.date == date:
            return True
        else:
            return False

    def json_serialise(self):
        ret = {
            'session_id': self.id,
            'description': self.description,
            'date': self.date,
            'time': format_datetime(self.time),
            'duration_minutes': self.duration_minutes,
            'data_transferred': self.data_transferred,
            'duration_sensor': self.duration_sensor,
            'external_load': self.external_load,
            'high_intensity_minutes': self.high_intensity_minutes,
            'mod_intensity_minutes': self.mod_intensity_minutes,
            'low_intensity_minutes': self.low_intensity_minutes,
            'high_intensity_load': self.high_intensity_load,
            'mod_intensity_load': self.mod_intensity_load,
            'low_intensity_load': self.low_intensity_load,
            'sensor_start_date_time': format_datetime(self.sensor_start_date_time),
            'sensor_end_date_time': format_datetime(self.sensor_end_date_time),
            'post_session_survey': self.post_session_survey
        }
        return ret

    def internal_load(self):
        if self.session_RPE is not None and self.duration_minutes is not None:
            return self.session_RPE * self.duration_minutes
        else:
            return None

    def missing_sensor_data(self):
        if self.data_transferred:
            return False
        else:
            return True


class SessionFactory(object):

    def create(self, session_type: SessionType):

        if session_type == SessionType.practice:
            session_object = PracticeSession()
        elif session_type == SessionType.game:
            session_object = Game()
        elif session_type == SessionType.bump_up:
            session_object = BumpUpSession()
        elif session_type == SessionType.strength_and_conditioning:
            session_object = StrengthConditioningSession()
        elif session_type == SessionType.tournament:
            session_object = Tournament()
        else:
            session_object = CorrectiveSession()

        session_object.id = str(uuid.uuid4())

        return session_object


class BumpUpSession(Session):
    def __init__(self):
        Session.__init__(self)
        self.exercises = []

    def session_type(self):
        return SessionType.bump_up

    def create(self):
        new_session = BumpUpSession()
        new_session.id = str(uuid.uuid4())
        return new_session

    def missing_post_session_survey(self):
        return Session.missing_post_session_survey()

    def in_daily_plan(self, date):
        if self.date >= date:
            return True
        else:
            return False


class PracticeSession(Session):
    def __init__(self):
        Session.__init__(self)

    def session_type(self):
        return SessionType.practice

    def create(self):
        new_session = PracticeSession()
        new_session.id = str(uuid.uuid4())
        return new_session

    def missing_post_session_survey(self):
        return Session.missing_post_session_survey()

    def in_daily_plan(self, date):
        return Session.in_daily_plan(date)


class StrengthConditioningSession(Session):
    def __init__(self):
        Session.__init__(self)

    def session_type(self):
        return SessionType.strength_and_conditioning

    def create(self):
        new_session = StrengthConditioningSession()
        new_session.id = str(uuid.uuid4())
        return new_session

    def missing_post_session_survey(self):
        return Session.missing_post_session_survey()

    def in_daily_plan(self, date):
        return Session.in_daily_plan(date)


class Game(Session):
    def __init__(self):
        Session.__init__(self)

    def session_type(self):
        return SessionType.game

    def create(self):
        new_session = Game()
        new_session.id = str(uuid.uuid4())
        return new_session

    def missing_post_session_survey(self):
        return Session.missing_post_session_survey()

    def in_daily_plan(self, date):
        return Session.in_daily_plan(date)


class Tournament(Session):
    def __init__(self):
        Session.__init__(self)
        self.start_date = None
        self.end_date = None
        self.games = []

    def session_type(self):
        return SessionType.tournament

    def create(self):
        new_session = Tournament()
        new_session.id = str(uuid.uuid4())
        return new_session

    def missing_post_session_survey(self):
        return Session.missing_post_session_survey()

    def in_daily_plan(self, date):
        if self.start_date <= date <= self.end_date:
            return True
        else:
            return False


class CorrectiveSession(Session):
    def __init__(self):
        Session.__init__(self)
        self.exercises = []

    def session_type(self):
        return SessionType.corrective

    def create(self):
        new_session = CorrectiveSession()
        new_session.id = str(uuid.uuid4())
        return new_session

    def missing_post_session_survey(self):
        if self.session_RPE is None:
            return True
        else:
            return False

    def in_daily_plan(self, date):
        if self.date >= date:
            return True
        else:
            return False


class RecoverySession(Serialisable):

    def __init__(self):
        self.inhibit_exercises = []
        self.lengthen_exercises = []
        self.activate_exercises = []
        self.integrate_exercises = []
        self.duration_minutes = 0
        self.inhibit_target_minutes = 0
        self.lengthen_target_minutes = 0
        self.activate_target_minutes = 0
        self.integrate_target_minutes = 0
        self.inhibit_max_percentage = 0
        self.lengthen_max_percentage = 0
        self.activate_max_percentage = 0
        self.integrate_max_percentage = 0
        self.start_time = None
        self.end_time = None
        self.impact_score = 0
        self.why_text = ""
        self.goal_text = ""

    def json_serialise(self):
        ret = {'minutes_duration': self.duration_minutes,
               'why_text': self.why_text,
               'goal_text': self.goal_text,
               'start_time': str(self.start_time),
               'end_time': str(self.end_time),
               'impact_score': self.impact_score,
               'inhibit_exercises': [ex.json_serialise() for ex in self.inhibit_exercises],
               'lengthen_exercises': [ex.json_serialise() for ex in self.lengthen_exercises],
               'activate_exercises': [ex.json_serialise() for ex in self.activate_exercises],
               'integrate_exercises': [ex.json_serialise() for ex in self.integrate_exercises],
               }
        return ret

    def recommended_exercises(self):
        exercise_list = []
        exercise_list.extend(self.inhibit_exercises)
        exercise_list.extend(self.lengthen_exercises)
        exercise_list.extend(self.activate_exercises)
        exercise_list.extend(self.integrate_exercises)

        #for s in range(0, len(exercise_list)):
        #    exercise_list[s].position_order = s

        return exercise_list

    def update_from_exercise_assignments(self, exercise_assignments):
        self.inhibit_exercises = exercise_assignments.inhibit_exercises
        self.lengthen_exercises = exercise_assignments.lengthen_exercises
        self.activate_exercises = exercise_assignments.activate_exercises
        self.integrate_exercises = exercise_assignments.integrate_exercises
        self.duration_minutes = (exercise_assignments.inhibit_minutes +
                                 exercise_assignments.lengthen_minutes +
                                 exercise_assignments.activate_minutes +
                                 exercise_assignments.integrate_minutes)

        num = 0

        for s in range(0, len(self.inhibit_exercises)):
            self.inhibit_exercises[s].position_order = num
            num = num + 1

        for s in range(0, len(self.lengthen_exercises)):
            self.lengthen_exercises[s].position_order = num
            num = num + 1

        for s in range(0, len(self.activate_exercises)):
            self.activate_exercises[s].position_order = num
            num = num + 1

        for s in range(0, len(self.integrate_exercises)):
            self.integrate_exercises[s].position_order = num
            num = num + 1


    def set_exercise_target_minutes(self, soreness_list, total_minutes_target):
        max_severity = 0
        if soreness_list is not None:
            for soreness in soreness_list:
                max_severity = max(max_severity, soreness.severity)

        if max_severity == 3:
            self.integrate_target_minutes = None
            self.activate_target_minutes = None
            self.lengthen_target_minutes = total_minutes_target / 2
            self.inhibit_target_minutes = total_minutes_target / 2
            self.integrate_max_percentage = None
            self.activate_max_percentage = None
            self.lengthen_max_percentage = .6
            self.inhibit_max_percentage = .6
        elif max_severity == 2:
            self.integrate_target_minutes = None
            self.activate_target_minutes = total_minutes_target / 3
            self.lengthen_target_minutes = total_minutes_target / 3
            self.inhibit_target_minutes = total_minutes_target / 3
            self.integrate_max_percentage = None
            self.activate_max_percentage = .4
            self.lengthen_max_percentage = .4
            self.inhibit_max_percentage = .4
        elif max_severity <= 1:
            self.integrate_target_minutes = None
            self.activate_target_minutes = total_minutes_target / 2
            self.lengthen_target_minutes = total_minutes_target / 4
            self.inhibit_target_minutes = total_minutes_target / 4
            self.integrate_max_percentage = None
            self.activate_max_percentage = .6
            self.lengthen_max_percentage = .3
            self.inhibit_max_percentage = .3


class GlobalLoadEstimationParameters(object):

    def __init__(self):
        self.high_intensity_percentage = 0
        self.moderate_intensity_percentage = 0
        self.low_intensity_percentage = 0
        self.total_avg_external_load_per_minute = 0
        self.high_intensity_avg_load_per_minute = 0
        self.moderate_intensity_avg_load_per_minute = 0
        self.low_intensity_avg_load_per_minute = 0


class SessionLoadEstimationParameter(GlobalLoadEstimationParameters):

    def __init__(self):
        GlobalLoadEstimationParameters.__init__()
        self.session_type = SessionType.practice


class Schedule(object):

    def __init__(self):
        self.athlete_id = ""
        self.sessions = []

    def add_sessions(self, sessions):
        for new_session in sessions:
            self.sessions.append(new_session)       # just placeholder logic

    def delete_sessions(self, sessions):
        for session_to_delete in sessions:
            self.sessions.remove(session_to_delete)     # just placeholder logic

    def update_session(self, updated_session):
        self.sessions.remove(updated_session)  # just placeholder logic


class ScheduleManager(object):

    def get_typical_schedule(self, athlete_id, sport_id):
        return Schedule
