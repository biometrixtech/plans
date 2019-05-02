from serialisable import Serialisable
from utils import parse_date
# import models.session as session
from models.session import Session
from models.daily_readiness import DailyReadiness
from models.modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining, ActiveRecovery, IceSession, HeatSession, ColdWaterImmersion, WarmUp, CoolDown


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
        self.heat = None
        self.completed_heat = []
        self.pre_active_rest = None
        self.completed_pre_active_rest = []
        self.warm_up = None
        self.completed_warm_up = []
        self.cool_down = None
        self.completed_cool_down = []
        self.active_recovery = None
        self.completed_active_recovery = []
        self.post_active_rest = None
        self.completed_post_active_rest = []
        self.ice = None
        self.completed_ice = []
        self.cold_water_immersion = None
        self.completed_cold_water_immersion = []
        self.pre_active_rest_completed = False
        self.post_active_rest_completed = False
        #self.functional_strength_completed = False
        #self.pre_recovery = session.RecoverySession()
        #self.post_recovery = session.RecoverySession()
        # self.completed_post_recovery_sessions = []
        #self.corrective_sessions = []
        #self.bump_up_sessions = []
        self.daily_readiness_survey = None
        # self.updated = False
        self.last_updated = None
        self.last_sensor_sync = None
        self.sessions_planned = True
        #self.functional_strength_eligible = False
        #self.completed_functional_strength_sessions = 0
        #self.functional_strength_session = None
        self.session_from_readiness = False
        self.train_later = True

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
               'cross_training_sessions': [c.json_serialise() for c in self.strength_conditioning_sessions],
               'pre_active_rest_completed': self.pre_active_rest_completed,
               'post_active_rest_completed': self.post_active_rest_completed,
               # 'functional_strength_session': (self.functional_strength_session.json_serialise()
               # #                                if self.functional_strength_session is not None else None),
               # 'heat': [heat.json_serialise() for heat in self.heat],
               'heat': self.heat.json_serialise() if self.heat is not None else None,
               'completed_heat': [heat.json_serialise() for heat in self.completed_heat],
               'pre_active_rest': self.pre_active_rest.json_serialise() if self.pre_active_rest is not None else None,
               'completed_pre_active_rest': [c.json_serialise() for c in self.completed_pre_active_rest],
               'warm_up': self.warm_up.json_serialise() if self.warm_up is not None else None,
               'completed_warm_up': [warm_up.json_serialise() for warm_up in self.completed_warm_up],
               'cool_down': self.cool_down.json_serialise() if self.cool_down is not None else None,
               'completed_cool_down': [cool_down.json_serialise() for cool_down in self.completed_cool_down],
               'active_recovery': self.active_recovery.json_serialise() if self.active_recovery is not None else None,
               'completed_active_recovery': [active_recovery.json_serialise() for active_recovery in self.completed_active_recovery],
               'post_active_rest': self.post_active_rest.json_serialise() if self.post_active_rest is not None else None,
               'completed_post_active_rest': [c.json_serialise() for c in self.completed_post_active_rest],
               # 'ice': [ice.json_serialise() for ice in self.ice],
               'ice': self.ice.json_serialise() if self.ice is not None else None,
               'completed_ice': [ice.json_serialise() for ice in self.completed_ice],
               'cold_water_immersion': self.cold_water_immersion.json_serialise() if self.cold_water_immersion is not None else None,
               'completed_cold_water_immersion': [c.json_serialise() for c in self.completed_cold_water_immersion],
               # 'completed_post_recovery_sessions': [c.json_serialise() for c in self.completed_post_recovery_sessions],
               'last_updated': self.last_updated,
               'daily_readiness_survey': readiness,
               'last_sensor_sync': self.last_sensor_sync,
               'sessions_planned': self.sessions_planned,
               # 'functional_strength_completed': self.functional_strength_completed,
               # 'functional_strength_eligible': self.functional_strength_eligible,
               # 'completed_functional_strength_sessions': self.completed_functional_strength_sessions,
               # 'session_from_readiness': self.session_from_readiness,
               'train_later': self.train_later
               }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict, stats_processing):
        daily_plan = cls(event_date=input_dict['date'])
        daily_plan.user_id = input_dict.get('user_id', None)
        daily_plan.training_sessions = [Session.json_deserialise(s) for s in input_dict.get('training_sessions', [])]
        if not stats_processing:
            # daily_plan.heat = [Heat.json_deserialise(heat) for heat in input_dict.get('heat', [])]
            daily_plan.ice = HeatSession.json_deserialise(input_dict['heat']) if input_dict.get('heat', None) is not None else None
            daily_plan.completed_heat = [Heat.json_deserialise(heat) for heat in input_dict.get('completed_heat', [])]
            daily_plan.pre_active_rest = ActiveRestBeforeTraining.json_deserialise(input_dict['pre_active_rest']) if input_dict.get('pre_active_rest', None) is not None else None
            daily_plan.completed_pre_active_rest = [ActiveRestBeforeTraining.json_deserialise(ar) for ar in input_dict.get('completed_pre_active_rest', [])]
            daily_plan.warm_up = WarmUp.json_deserialise(input_dict['warm_up']) if input_dict.get('warm_up', None) is not None else None
            daily_plan.completed_warm_up = [WarmUp.json_deserialise(w) for w in input_dict.get('completed_warm_up', [])]
            daily_plan.cool_down = CoolDown.json_deserialise(input_dict['cool_down']) if input_dict.get('cool_down', None) is not None else None
            daily_plan.completed_cool_down = [CoolDown.json_deserialise(cd) for cd in input_dict.get('completed_cool_down', [])]
            daily_plan.active_recovery = ActiveRecovery.json_deserialise(input_dict['active_recovery']) if input_dict.get('active_recovery', None) is not None else None
            daily_plan.completed_active_recovery = [ActiveRecovery.json_deserialise(ar) for ar in input_dict.get('completed_active_recovery', [])]
            daily_plan.post_active_rest = ActiveRestAfterTraining.json_deserialise(input_dict['post_active_rest']) if input_dict.get('post_active_rest', None) is not None else None
            daily_plan.completed_post_active_rest = [ActiveRestAfterTraining.json_deserialise(ar) for ar in input_dict.get('completed_post_active_rest', [])]
            # daily_plan.ice = [Ice.json_deserialise(ice) for ice in input_dict.get('ice', [])]
            daily_plan.ice = IceSession.json_deserialise(input_dict['ice']) if input_dict.get('ice', None) is not None else None
            daily_plan.completed_ice = [Ice.json_deserialise(ice) for ice in input_dict.get('completed_ice', [])]
            daily_plan.cold_water_immersion = ColdWaterImmersion.json_deserialise(input_dict['cold_water_immersion']) if input_dict.get('cold_water_immersion', None) is not None else None
            daily_plan.completed_cold_water_immersion = [ColdWaterImmersion.json_deserialise(cwi) for cwi in input_dict.get('completed_cold_water_immersion', [])]
        # daily_plan.daily_readiness_survey = _daily_readiness_from_mongo(input_dict.get('daily_readiness_survey', None), daily_plan.user_id)
        # daily_plan.updated = input_dict.get('updated', False)
        daily_plan.last_updated = input_dict.get('last_updated', None)
        daily_plan.pre_active_rest_completed = input_dict.get('pre_active_rest_completed', False)
        daily_plan.post_active_rest_completed = input_dict.get('post_active_rest_completed', False)
        daily_plan.last_sensor_sync = input_dict.get('last_sensor_sync', None)
        daily_plan.sessions_planned = input_dict.get('sessions_planned', True)
        daily_plan.train_later = input_dict.get('train_later', True)

        return daily_plan

    def daily_readiness_survey_completed(self):
        if self.daily_readiness_survey is not None:
            return True
        else:
            return False

    def define_landing_screen(self):
        if self.post_active_rest is not None and self.post_active_rest.active:
            return 2.0, None
        elif ((self.post_active_rest is None or not self.post_active_rest.active) and
               self.warm_up is not None and
               self.warm_up.completed):
            return 1.0, None
        else:
            return 0.0, None

    def get_past_sessions(self, trigger_date_time):

        sessions = []
        training_sessions = [x for x in self.training_sessions if x.event_date is not None and
                             x.event_date < trigger_date_time]
        cross_training_sessions = [x for x in self.strength_conditioning_sessions if x.event_date is not None and
                                   x.event_date < trigger_date_time]
        sessions.extend(cross_training_sessions)
        sessions.extend(training_sessions)

        return sessions

    def get_future_sessions(self, trigger_date_time):

        sessions = []

        training_sessions = [x for x in self.training_sessions if x.event_date is not None and
                             x.event_date > trigger_date_time]
        cross_training_sessions = [x for x in self.strength_conditioning_sessions if x.event_date is not None and
                                   x.event_date > trigger_date_time]
        sessions.extend(cross_training_sessions)
        sessions.extend(training_sessions)

        return sessions
