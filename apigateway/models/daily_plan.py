from serialisable import Serialisable
from utils import parse_date
import models.session as session
from models.daily_readiness import DailyReadiness


class DailyPlan(Serialisable):
    
    def __init__(self, event_date):
        self.user_id = ""
        self.event_date = event_date
        self.day_of_week = self.get_event_datetime().weekday()
        self.training_sessions = []
        #self.practice_sessions = []
        self.strength_conditioning_sessions = []  # includes cross training
        #self.games = []
        #self.tournaments = []
        self.heat = []
        self.pre_active_rest = None
        self.warm_up = None
        self.cool_down = None
        self.active_recovery = None
        self.post_active_rest = None
        self.ice = []
        self.cold_water_immersion = None
        self.pre_active_rest_completed = False
        self.post_active_rest_completed = False
        #self.functional_strength_completed = False
        #self.pre_recovery = session.RecoverySession()
        #self.post_recovery = session.RecoverySession()
        # self.completed_post_recovery_sessions = []
        #self.corrective_sessions = []
        #self.bump_up_sessions = []
        self.daily_readiness_survey = None
        self.updated = False
        self.last_updated = None
        self.last_sensor_sync = None
        self.sessions_planned = True
        #self.functional_strength_eligible = False
        #self.completed_functional_strength_sessions = 0
        #self.functional_strength_session = None
        self.session_from_readiness = False
        self.train_later = True
        self.train_later = False

    def get_id(self):
        return self.user_id

    def get_event_datetime(self):
        return parse_date(self.event_date)

    def json_serialise(self):
        if isinstance(self.daily_readiness_survey, DailyReadiness):
            readiness = self.daily_readiness_survey.json_serialise()
            del readiness['sore_body_parts']
            del readiness['user_id']
        else:
            readiness = self.daily_readiness_survey
        ret = {'user_id': self.user_id,
               'date': self.event_date,
               'day_of_week': self.day_of_week,
               'training_sessions': [p.json_serialise() for p in self.training_sessions],
               #'practice_sessions': [p.json_serialise() for p in self.practice_sessions],
               #'bump_up_sessions': [b.json_serialise() for b in self.bump_up_sessions],
               'cross_training_sessions': [c.json_serialise() for c in self.strength_conditioning_sessions],
               #'game_sessions': [g.json_serialise() for g in self.games],
               'pre_active_rest_completed': self.pre_active_rest_completed,
               'post_active_rest_completed': self.post_active_rest_completed,
               #'functional_strength_session': (self.functional_strength_session.json_serialise()
               #                                if self.functional_strength_session is not None else None),
               # 'recovery_am': self.pre_recovery.json_serialise() if self.pre_recovery is not None else None,
               # 'recovery_pm': self.post_recovery.json_serialise() if self.post_recovery is not None else None,
               # 'pre_recovery': self.pre_recovery.json_serialise() if self.pre_recovery is not None else None,
               # 'post_recovery': self.post_recovery.json_serialise() if self.post_recovery is not None else None,
                'heat': [heat.json_serialise() for heat in self.heat],
                'pre_active_rest': self.pre_active_rest.json_serialise() if self.pre_active_rest is not None else None,
                'warm_up': self.warm_up.json_serialise() if self.warm_up is not None else None,
                'cool_down': self.cool_down.json_serialise() if self.cool_down is not None else None,
                'active_recovery': self.active_recovery.json_serialise() if self.active_recovery is not None else None,
                'post_active_rest': self.post_active_rest.json_serialise() if self.post_active_rest is not None else None,
                'ice': [ice.json_serialise() for ice in self.ice],
                'cold_water_immersion': self.cold_water_immersion.json_serialise() if self.cold_water_immersion is not None else None,
               # 'completed_post_recovery_sessions': [c.json_serialise() for c in self.completed_post_recovery_sessions],
               'last_updated': self.last_updated,
               'daily_readiness_survey': readiness,
               'last_sensor_sync': self.last_sensor_sync,
               'sessions_planned': self.sessions_planned,
               #'functional_strength_completed': self.functional_strength_completed,
               #'functional_strength_eligible': self.functional_strength_eligible,
               #'completed_functional_strength_sessions': self.completed_functional_strength_sessions,
               # 'session_from_readiness': self.session_from_readiness,
               # 'train_later': self.train_later,
               'train_later': self.train_later
               }
        return ret

    def daily_readiness_survey_completed(self):
        if self.daily_readiness_survey is not None:
            return True
        else:
            return False

    def define_landing_screen(self):
        if self.post_active_rest is not None:
            return 2.0, None
        elif self.post_active_rest is None and self.pre_active_rest is not None and self.pre_active_rest.completed:
            return 1.0, None
        else:
            return 0.0, None

    def get_past_sessions(self, trigger_date_time):

        sessions = []
        training_sessions = [x for x in self.training_sessions if x.event_date is not None and
                             x.event_date < trigger_date_time]
        #practice_sessions = [x for x in self.practice_sessions if x.event_date is not None and
        #                     x.event_date < trigger_date_time]
        #game_sessions = [x for x in self.games if x.event_date is not None and
        #                 x.event_date < trigger_date_time]
        cross_training_sessions = [x for x in self.strength_conditioning_sessions if x.event_date is not None and
                                   x.event_date < trigger_date_time]

        #sessions.extend(practice_sessions)
        #sessions.extend(game_sessions)
        sessions.extend(cross_training_sessions)
        sessions.extend(training_sessions)

        return sessions

    def get_future_sessions(self, trigger_date_time):

        sessions = []

        training_sessions = [x for x in self.training_sessions if x.event_date is not None and
                             x.event_date > trigger_date_time]
        #practice_sessions = [x for x in self.practice_sessions if x.event_date is not None and
        #                     x.event_date > trigger_date_time]
        #game_sessions = [x for x in self.games if x.event_date is not None and
        #                 x.event_date > trigger_date_time]
        cross_training_sessions = [x for x in self.strength_conditioning_sessions if x.event_date is not None and
                                   x.event_date > trigger_date_time]

        #sessions.extend(practice_sessions)
        #sessions.extend(game_sessions)
        sessions.extend(cross_training_sessions)
        sessions.extend(training_sessions)

        return sessions
