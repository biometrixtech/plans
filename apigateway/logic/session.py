import abc
from enum import Enum
import uuid
import logic.exercise as exercise


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


class Session(metaclass=abc.ABCMeta):

    def __init__(self):
        self.id = None
        self.duration_minutes = None
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

        session_object.id = uuid.uuid4()

        return session_object


class BumpUpSession(Session):
    def __init__(self):
        Session.__init__(self)
        self.exercises = []

    def session_type(self):
        return SessionType.bump_up

    def create(self):
        new_session = BumpUpSession()
        new_session.id = uuid.uuid4()
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
        new_session.id = uuid.uuid4()
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
        new_session.id = uuid.uuid4()
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
        new_session.id = uuid.uuid4()
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
        new_session.id = uuid.uuid4()
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
        new_session.id = uuid.uuid4()
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


class RecoverySession(object):

    def __init__(self):
        self.recommended_inhibit_exercises = []
        self.recommended_lengthen_exercises = []
        self.recommended_activate_exercises = []
        self.recommended_integrate_exercises = []
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

    def recommended_exercises(self):
        exercise_list = []
        exercise_list.extend(self.recommended_inhibit_exercises)
        exercise_list.extend(self.recommended_lengthen_exercises)
        exercise_list.extend(self.recommended_activate_exercises)
        exercise_list.extend(self.recommended_integrate_exercises)

        for s in range(0, len(exercise_list)):
            exercise_list[s].position_order = s

        return exercise_list

    def update_from_exercise_assignments(self, exercise_assignments):
        self.recommended_inhibit_exercises = exercise_assignments.inhibit_exercises
        self.recommended_lengthen_exercises = exercise_assignments.lengthen_exercises
        self.recommended_activate_exercises = exercise_assignments.activate_exercises
        self.recommended_integrate_exercises = exercise_assignments.integrate_exercises
        self.duration_minutes = (exercise_assignments.inhibit_minutes +
                                 exercise_assignments.lengthen_minutes +
                                 exercise_assignments.activate_minutes +
                                 exercise_assignments.integrate_minutes)

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
