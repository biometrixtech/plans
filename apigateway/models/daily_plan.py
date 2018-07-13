from serialisable import Serialisable
from utils import parse_datetime
import models.session as session


class DailyPlan(Serialisable):
    
    def __init__(self, event_date):
        self.user_id = ""
        self.event_date = event_date
        self.practice_sessions = []
        self.strength_conditioning_sessions = []  # includes cross training
        self.games = []
        self.tournaments = []
        self.recovery_am = session.RecoverySession()
        self.recovery_pm = session.RecoverySession()
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
               'practice_sessions': [p.json_serialise() for p in self.practice_sessions],
               'bump_up_sessions': [b.json_serialise() for b in self.bump_up_sessions],
               'cross_training_sessions': [c.json_serialise() for c in self.strength_conditioning_sessions],
               'game_sessions': [g.json_serialise() for g in self.games],
               'recovery_am': self.recovery_am.json_serialise(),
               'recovery_pm': self.recovery_pm.json_serialise(),
               'last_updated': self.last_updated,
               'daily_readiness_survey': self.daily_readiness_survey
               }
        return ret

    def daily_readiness_survey_completed(self):
        if self.daily_readiness_survey is not None:
            return True
        else:
            return False

    def add_scheduled_sessions(self, scheduled_sessions):

        # this will expand in complexity once an athlete can add a new session

        # first add any that are already completed

        practice_sessions = [s for s in scheduled_sessions if isinstance(s, session.PracticeSession)]
        cross_training_sessions = [s for s in scheduled_sessions if isinstance(s, session.StrengthConditioningSession)]
        game_sessions = [s for s in scheduled_sessions if isinstance(s, session.Game)]
        tournament_sessions = [s for s in scheduled_sessions if isinstance(s, session.Tournament)]

        self.practice_sessions = practice_sessions
        self.strength_conditioning_sessions = cross_training_sessions
        self.games = game_sessions
        self.tournaments = tournament_sessions

        #if isinstance(scheduled_session, session.PracticeSession):
        #    self.practice_sessions.append(scheduled_session)
        #elif isinstance(scheduled_session, session.StrengthConditioningSession):
        #    self.strength_conditioning_sessions.append(scheduled_session)
        #elif isinstance(scheduled_session, session.Game):
        #    self.games.append(scheduled_session)
        #elif isinstance(scheduled_session, session.Tournament):
        #    self.tournaments.append(scheduled_session)


