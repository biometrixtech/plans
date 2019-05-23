from serialisable import Serialisable
from utils import parse_date
# import models.session as session
from models.session import Session
from models.daily_readiness import DailyReadiness
from models.modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining, IceSession, HeatSession, ColdWaterImmersion, WarmUp, CoolDown
from models.insights import AthleteInsight
from models.athlete_trend import AthleteTrends


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
        self.pre_active_rest = []
        self.completed_pre_active_rest = []
        self.warm_up = []
        self.completed_warm_up = []
        self.cool_down = []
        self.completed_cool_down = []
        # self.active_recovery = None
        # self.completed_active_recovery = []
        self.post_active_rest = []
        self.completed_post_active_rest = []
        self.ice = None
        self.completed_ice = []
        self.cold_water_immersion = None
        self.completed_cold_water_immersion = []
        self.pre_active_rest_completed = False
        self.post_active_rest_completed = False
        self.daily_readiness_survey = None
        # self.updated = False
        self.last_updated = None
        self.last_sensor_sync = None
        self.sessions_planned = True
        # self.functional_strength_eligible = False
        # self.completed_functional_strength_sessions = 0
        # self.functional_strength_session = None
        self.train_later = True
        self.insights = []
        self.trends = None

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
               #                                 if self.functional_strength_session is not None else None),
               'heat': self.heat.json_serialise() if self.heat is not None else None,
               'completed_heat': [heat.json_serialise() for heat in self.completed_heat],
               'pre_active_rest': [ar.json_serialise() for ar in self.pre_active_rest],
               'completed_pre_active_rest': [ar.json_serialise() for ar in self.completed_pre_active_rest],
               'warm_up': [warm_up.json_serialise() for warm_up in self.warm_up],
               'completed_warm_up': [warm_up.json_serialise() for warm_up in self.completed_warm_up],
               'cool_down': [cool_down.json_serialise() for cool_down in self.cool_down],
               'completed_cool_down': [cool_down.json_serialise() for cool_down in self.completed_cool_down],
               # 'active_recovery': self.active_recovery.json_serialise() if self.active_recovery is not None else None,
               # 'completed_active_recovery': [active_recovery.json_serialise() for active_recovery in self.completed_active_recovery],
               'post_active_rest': [ar.json_serialise() for ar in self.post_active_rest],
               'completed_post_active_rest': [ar.json_serialise() for ar in self.completed_post_active_rest],
               'ice': self.ice.json_serialise() if self.ice is not None else None,
               'completed_ice': [ice.json_serialise() for ice in self.completed_ice],
               'cold_water_immersion': self.cold_water_immersion.json_serialise() if self.cold_water_immersion is not None else None,
               'completed_cold_water_immersion': [cwi.json_serialise() for cwi in self.completed_cold_water_immersion],
               'last_updated': self.last_updated,
               'daily_readiness_survey': readiness,
               'last_sensor_sync': self.last_sensor_sync,
               'sessions_planned': self.sessions_planned,
               # 'functional_strength_completed': self.functional_strength_completed,
               # 'functional_strength_eligible': self.functional_strength_eligible,
               # 'completed_functional_strength_sessions': self.completed_functional_strength_sessions,
               'train_later': self.train_later,
               'insights': [insight.json_serialise() for insight in self.insights],
               'trends': self.trends.json_serialise() if self.trends is not None else None,
               }

        # ret['insights'] = [
        #                     {
        #                     "title": "How Soreness Turns to Strength:",
        #                     "text": "We've added Care for Soreness to your plan today, to help retain mobility and expodite healing of tissue damage indicated by muscle soreness.",
        #                     "goal_targeted": ["Care for Soreness"],
        #                     "start_date": "2019-05-13T11:23:00Z",
        #                     "read": False
        #                     },
        #                     {
        #                     "title": 'Sign of Possible Injury',
        #                     "text": "We added activities to Prevention to your plan because left knee pain for several days could be sign of injury. We'll remove heat to avoid aggrivating the issue and encourage you to ice, rest and see a doctor if the pain worsens.",
        #                     "goal_targeted": ["Prevention"],
        #                     "start_date": "2019-05-10T11:23:00Z",
        #                     "read": False
        #                     },
        #                     {
        #                     "title": "Possible Strength Imbalance",
        #                     "text": "We've added activities to Prevention to your plan. Given your training patterns and persistant right glute soreness response, you may have a strength imbalance or movement dysfuntion which elevates your risk of injury. With these ativities we'll try to address the most likely source given what we've observed.",
        #                     "goal_targeted": ["Prevention"],
        #                     "start_date": "2019-05-13T11:23:00Z",
        #                     "read": False
        #                     },
        #                     {
        #                     "title": "How We Help Mitigate Pain: ",
        #                     "text": "When you report pain we try to provide you with Care for Pain and Personalized Prepare for Sport activities to encourage proper biomechanical alignment & balance mucle tension to help mitigate the pain, but please remember to avoid any activities that hurt. ",
        #                     "goal_targeted": ["Care for Pain", "Personalized Prepare for Sport"],
        #                     "start_date": "2019-05-13T11:23:00Z",
        #                     "read": True
        #                     }
        #                 ]
        return ret

    @classmethod
    def json_deserialise(cls, input_dict, stats_processing):
        daily_plan = cls(event_date=input_dict['date'])
        daily_plan.user_id = input_dict.get('user_id', None)
        daily_plan.training_sessions = [Session.json_deserialise(s) for s in input_dict.get('training_sessions', [])]
        if not stats_processing:
            daily_plan.heat = HeatSession.json_deserialise(input_dict['heat']) if input_dict.get('heat', None) is not None else None
            daily_plan.completed_heat = [HeatSession.json_deserialise(heat) for heat in input_dict.get('completed_heat', [])]
            daily_plan.pre_active_rest = [ActiveRestBeforeTraining.json_deserialise(ar) for ar in input_dict.get('pre_active_rest', [])]
            daily_plan.completed_pre_active_rest = [ActiveRestBeforeTraining.json_deserialise(ar) for ar in input_dict.get('completed_pre_active_rest', [])]
            daily_plan.warm_up = [WarmUp.json_deserialise(warm_up) for warm_up in input_dict.get('warm_up', [])]
            daily_plan.completed_warm_up = [WarmUp.json_deserialise(w) for w in input_dict.get('completed_warm_up', [])]
            daily_plan.cool_down = [CoolDown.json_deserialise(cool_down) for cool_down in input_dict.get('cool_down', [])]
            daily_plan.completed_cool_down = [CoolDown.json_deserialise(cd) for cd in input_dict.get('completed_cool_down', [])]
            # daily_plan.active_recovery = ActiveRecovery.json_deserialise(input_dict['active_recovery']) if input_dict.get('active_recovery', None) is not None else None
            # daily_plan.completed_active_recovery = [ActiveRecovery.json_deserialise(ar) for ar in input_dict.get('completed_active_recovery', [])]
            daily_plan.post_active_rest = [ActiveRestAfterTraining.json_deserialise(ar) for ar in input_dict.get('post_active_rest', [])]
            daily_plan.completed_post_active_rest = [ActiveRestAfterTraining.json_deserialise(ar) for ar in input_dict.get('completed_post_active_rest', [])]
            daily_plan.ice = IceSession.json_deserialise(input_dict['ice']) if input_dict.get('ice', None) is not None else None
            daily_plan.completed_ice = [IceSession.json_deserialise(ice) for ice in input_dict.get('completed_ice', [])]
            daily_plan.cold_water_immersion = ColdWaterImmersion.json_deserialise(input_dict['cold_water_immersion']) if input_dict.get('cold_water_immersion', None) is not None else None
            daily_plan.completed_cold_water_immersion = [ColdWaterImmersion.json_deserialise(cwi) for cwi in input_dict.get('completed_cold_water_immersion', [])]
            daily_plan.insights = [AthleteInsight.json_deserialise(insight) for insight in input_dict.get('insights', [])]
            daily_plan.trends = AthleteTrends.json_deserialise(input_dict['trends']) if input_dict.get('trends', None) is not None else None
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
        if len(self.post_active_rest) > 0 and self.post_active_rest[0].active:
            return 2.0, None
        elif ((len(self.post_active_rest) == 0 or not self.post_active_rest[0].active) and
               len(self.pre_active_rest) > 0 and
               self.pre_active_rest[0].completed):
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

    def get_alerts(self):
        alerts = []
        if self.train_later:
            for active_rest in self.pre_active_rest:
                alerts.extend(active_rest.alerts)
            for warm_up in self.warm_up:
                alerts.extend(warm_up.alerts)
            if self.heat is not None:
                alerts.extend(self.heat.alerts)
        else:
            for active_rest in self.post_active_rest:
                alerts.extend(active_rest.alerts)
            for cool_down in self.cool_down:
                alerts.extend(cool_down.alerts)
            if self.ice is not None:
                alerts.extend(self.ice.alerts)
            if self.cold_water_immersion is not None:
                alerts.extend(self.cold_water_immersion.alerts)
        return alerts

    def sort_insights(self):
        self.insights = sorted(self.insights, key=lambda x: (int(x.read), x.priority, int(x.cleared)))
