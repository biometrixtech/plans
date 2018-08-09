from serialisable import Serialisable
from utils import parse_datetime
from datetime import datetime
import models.session as session
from utils import format_datetime


class DailyPlan(Serialisable):
    
    def __init__(self, event_date):
        self.user_id = ""
        self.event_date = event_date
        self.day_of_week = self.get_event_datetime().today().weekday()
        self.training_sessions = []
        self.practice_sessions = []
        self.strength_conditioning_sessions = []  # includes cross training
        self.games = []
        self.tournaments = []
        self.pre_recovery_completed = False
        self.post_recovery_completed = False
        self.pre_recovery = session.RecoverySession()
        self.post_recovery = session.RecoverySession()
        self.completed_post_recovery_sessions = []
        self.corrective_sessions = []
        self.bump_up_sessions = []
        self.daily_readiness_survey = None
        self.updated = False
        self.last_updated = None

    def get_id(self):
        return self.user_id

    def get_event_datetime(self):
        return parse_datetime(self.event_date)

    def json_serialise(self):
        ret = {'user_id': self.user_id,
               'date': self.event_date,
               'day_of_week': self.day_of_week,
               'training_sessions': [p.json_serialise() for p in self.training_sessions],
               'practice_sessions': [p.json_serialise() for p in self.practice_sessions],
               'bump_up_sessions': [b.json_serialise() for b in self.bump_up_sessions],
               'cross_training_sessions': [c.json_serialise() for c in self.strength_conditioning_sessions],
               'game_sessions': [g.json_serialise() for g in self.games],
               'pre_recovery_completed': self.pre_recovery_completed,
               'post_recovery_completed': self.post_recovery_completed,
               'recovery_am': self.pre_recovery.json_serialise() if self.pre_recovery is not None else None,
               'recovery_pm': self.post_recovery.json_serialise() if self.post_recovery is not None else None,
               'pre_recovery': self.pre_recovery.json_serialise() if self.pre_recovery is not None else None,
               'post_recovery': self.post_recovery.json_serialise() if self.post_recovery is not None else None,
               'completed_post_recovery_sessions': [c.json_serialise() for c in self.completed_post_recovery_sessions],
               'last_updated': self.last_updated,
               'daily_readiness_survey': self.daily_readiness_survey
               }
        return ret

    def daily_readiness_survey_completed(self):
        if self.daily_readiness_survey is not None:
            return True
        else:
            return False

    def define_landing_screen(self):
        if self.pre_recovery is None and self.post_recovery is None:
            return 0.0, 0.0
        elif self.pre_recovery is not None:
            if self.pre_recovery_completed:
                return 1.0, 1.0
            else:
                return 0.0, 0.0
        elif self.post_recovery is not None:
            if self.post_recovery.completed:
                return 2.0, None
            else:
                return 2.0, 2.0
        else:
            return 0.0, None

    def get_past_sessions(self, trigger_date_time):

        sessions = []
        training_sessions = [x for x in self.training_sessions if x.event_date is not None and
                             x.event_date < trigger_date_time]
        practice_sessions = [x for x in self.practice_sessions if x.event_date is not None and
                             x.event_date < trigger_date_time]
        game_sessions = [x for x in self.games if x.event_date is not None and
                         x.event_date < trigger_date_time]
        cross_training_sessions = [x for x in self.strength_conditioning_sessions if x.event_date is not None and
                                   x.event_date < trigger_date_time]

        sessions.extend(practice_sessions)
        sessions.extend(game_sessions)
        sessions.extend(cross_training_sessions)
        sessions.extend(training_sessions)

        return sessions

    def get_future_sessions(self, trigger_date_time):

        sessions = []

        training_sessions = [x for x in self.training_sessions if x.event_date is not None and
                             x.event_date > trigger_date_time]
        practice_sessions = [x for x in self.practice_sessions if x.event_date is not None and
                             x.event_date > trigger_date_time]
        game_sessions = [x for x in self.games if x.event_date is not None and
                         x.event_date > trigger_date_time]
        cross_training_sessions = [x for x in self.strength_conditioning_sessions if x.event_date is not None and
                                   x.event_date > trigger_date_time]

        sessions.extend(practice_sessions)
        sessions.extend(game_sessions)
        sessions.extend(cross_training_sessions)
        sessions.extend(training_sessions)

        return sessions

    ''' Deprecated
    def add_scheduled_sessions(self, scheduled_sessions):

        # this will expand in complexity once an athlete can add a new session

        # first add any that are already completed

        practice_sessions = [s for s in self.practice_sessions if isinstance(s, session.PracticeSession)
                             and (s.data_transferred or s.post_session_survey is not None)]
        cross_training_sessions = [s for s in self.strength_conditioning_sessions if isinstance(s, session.StrengthConditioningSession)
                                   and (s.data_transferred or s.post_session_survey is not None)]
        game_sessions = [s for s in self.games if isinstance(s, session.Game)
                         and (s.data_transferred or s.post_session_survey is not None)]
        tournament_sessions = [s for s in self.tournaments if isinstance(s, session.Tournament)
                               and (s.data_transferred or s.post_session_survey is not None)]

        new_practice_sessions = [s for s in scheduled_sessions if isinstance(s, session.PracticeSession)]
        new_cross_training_sessions = [s for s in scheduled_sessions if isinstance(s, session.StrengthConditioningSession)]
        new_game_sessions = [s for s in scheduled_sessions if isinstance(s, session.Game)]
        new_tournament_sessions = [s for s in scheduled_sessions if isinstance(s, session.Tournament)]

        if len(practice_sessions) < len(new_practice_sessions):
            self.practice_sessions = practice_sessions
            for p in range(len(practice_sessions), len(new_practice_sessions)):
                self.practice_sessions.append(new_practice_sessions[p])

        if len(cross_training_sessions) < len(new_cross_training_sessions):
            self.strength_conditioning_sessions = cross_training_sessions
            for p in range(len(cross_training_sessions), len(new_cross_training_sessions)):
                self.strength_conditioning_sessions.append(new_cross_training_sessions[p])

        if len(game_sessions) < len(new_game_sessions):
            self.games = game_sessions
            for p in range(len(game_sessions), len(new_game_sessions)):
                self.games.append(new_game_sessions[p])

        if len(tournament_sessions) < len(new_tournament_sessions):
            self.tournaments = tournament_sessions
            for p in range(len(tournament_sessions), len(new_tournament_sessions)):
                self.tournaments.append(new_tournament_sessions[p])

        #if isinstance(scheduled_session, session.PracticeSession):
        #    self.practice_sessions.append(scheduled_session)
        #elif isinstance(scheduled_session, session.StrengthConditioningSession):
        #    self.strength_conditioning_sessions.append(scheduled_session)
        #elif isinstance(scheduled_session, session.Game):
        #    self.games.append(scheduled_session)
        #elif isinstance(scheduled_session, session.Tournament):
        #    self.tournaments.append(scheduled_session)
    '''

