from serialisable import Serialisable
from utils import parse_date
from models.session import Session
from models.daily_readiness import DailyReadiness
from models.athlete_trend import AthleteTrends
from models.soreness import Soreness
from models.functional_movement_modalities import Modality, ModalityTypeDisplay, ModalityType, IceSessionModalities, HeatSession, ColdWaterImmersionModality


class DailyPlan(Serialisable):
    
    def __init__(self, event_date):
        self.user_id = ""
        self.event_date = event_date
        self.day_of_week = self.get_event_datetime().weekday()
        self.training_sessions = []
        self.heat = None
        self.completed_heat = []
        self.pre_active_rest = []
        self.completed_pre_active_rest = []
        self.warm_up = []
        self.completed_warm_up = []
        self.cool_down = []
        self.completed_cool_down = []
        self.post_active_rest = []
        self.completed_post_active_rest = []
        self.ice = None
        self.completed_ice = []
        self.cold_water_immersion = None
        self.completed_cold_water_immersion = []
        self.pre_active_rest_completed = False
        self.post_active_rest_completed = False
        self.daily_readiness_survey = None
        self.last_updated = None
        self.last_sensor_sync = None
        self.sessions_planned = True
        self.train_later = True
        self.insights = []
        self.trends = None
        self.symptoms = []
        self.modalities = []
        self.completed_modalities = []
        self.modalities_available_on_demand = []

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
               'pre_active_rest_completed': self.pre_active_rest_completed,
               'post_active_rest_completed': self.post_active_rest_completed,
               'heat': self.heat.json_serialise() if self.heat is not None else None,
               'completed_heat': [heat.json_serialise() for heat in self.completed_heat],
               'pre_active_rest': [ar.json_serialise() for ar in self.pre_active_rest],
               'completed_pre_active_rest': [ar.json_serialise() for ar in self.completed_pre_active_rest],
               'warm_up': [warm_up.json_serialise() for warm_up in self.warm_up],
               'completed_warm_up': [warm_up.json_serialise() for warm_up in self.completed_warm_up],
               'cool_down': [cool_down.json_serialise() for cool_down in self.cool_down],
               'completed_cool_down': [cool_down.json_serialise() for cool_down in self.completed_cool_down],
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
               'train_later': self.train_later,
               'insights': [insight.json_serialise() for insight in self.insights],
               'trends': self.trends.json_serialise(plan=True) if self.trends is not None else None,
               'symptoms': [soreness.json_serialise() for soreness in self.symptoms],
               'modalities': [m.json_serialise() for m in self.modalities],
               'completed_modalities': [m.json_serialise() for m in self.completed_modalities],
               'modalities_available_on_demand': [m.json_serialise() for m in self.modalities_available_on_demand]
               }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict, stats_processing):
        daily_plan = cls(event_date=input_dict['date'])
        daily_plan.user_id = input_dict.get('user_id', None)
        daily_plan.training_sessions = [Session.json_deserialise(s) for s in input_dict.get('training_sessions', [])]
        if not stats_processing:
            daily_plan.heat = HeatSession.json_deserialise(input_dict['heat']) if input_dict.get('heat', None) is not None else None
            daily_plan.completed_heat = [HeatSession.json_deserialise(heat) for heat in input_dict.get('completed_heat', [])]
            daily_plan.ice = IceSessionModalities.json_deserialise(input_dict['ice']) if input_dict.get('ice', None) is not None else None
            daily_plan.completed_ice = [IceSessionModalities.json_deserialise(ice) for ice in input_dict.get('completed_ice', [])]
            daily_plan.cold_water_immersion = ColdWaterImmersionModality.json_deserialise(input_dict['cold_water_immersion']) if input_dict.get('cold_water_immersion', None) is not None else None
            daily_plan.completed_cold_water_immersion = [ColdWaterImmersionModality.json_deserialise(cwi) for cwi in input_dict.get('completed_cold_water_immersion', [])]
            daily_plan.trends = AthleteTrends.json_deserialise(input_dict['trends']) if input_dict.get('trends', None) is not None else None
            daily_plan.modalities = [Modality.json_deserialise(m) for m in input_dict.get('modalities', [])]
            daily_plan.completed_modalities = [Modality.json_deserialise(m) for m in input_dict.get('completed_modalities', [])]
            daily_plan.modalities_available_on_demand = [ModalityTypeDisplay.json_deserialise(md) for md in input_dict.get('modalities_available_on_demand', [])]
        daily_plan.last_updated = input_dict.get('last_updated', None)
        daily_plan.pre_active_rest_completed = input_dict.get('pre_active_rest_completed', False)
        daily_plan.post_active_rest_completed = input_dict.get('post_active_rest_completed', False)
        daily_plan.last_sensor_sync = input_dict.get('last_sensor_sync', None)
        daily_plan.sessions_planned = input_dict.get('sessions_planned', True)
        daily_plan.train_later = input_dict.get('train_later', True)
        daily_plan.symptoms = [Soreness.json_deserialise(soreness) for soreness in input_dict.get('symptoms', [])]

        return daily_plan

    def daily_readiness_survey_completed(self):
        if self.daily_readiness_survey is not None:
            return True
        else:
            return False

    def define_landing_screen(self):
        if len(self.post_active_rest) > 0 and self.post_active_rest[0].active:
            return 2.0, None
        elif ((len(self.post_active_rest) == 0 or
               not self.post_active_rest[0].active) and
              len(self.pre_active_rest) > 0 and
              self.pre_active_rest[0].completed):
            return 1.0, None
        else:
            return 0.0, None

    def define_available_modalities(self):
        self.modalities_available_on_demand = []
        active_rest_available_on_demand = True
        movement_prep_available = True
        for m in self.modalities:
            if m.type.value == 1 and not m.completed and m.active:
                active_rest_available_on_demand = False
            if m.type.value == 5 and not m.completed and m.active:
                movement_prep_available = False
        if active_rest_available_on_demand:
            self.modalities_available_on_demand.append(ModalityTypeDisplay(ModalityType(1)))
        if movement_prep_available:
            self.modalities_available_on_demand.append(ModalityTypeDisplay(ModalityType(5)))

    def get_past_sessions(self, trigger_date_time):

        sessions = []
        training_sessions = [x for x in self.training_sessions if x.event_date is not None and
                             x.event_date < trigger_date_time]
        sessions.extend(training_sessions)

        return sessions

    def get_future_sessions(self, trigger_date_time):

        sessions = []

        training_sessions = [x for x in self.training_sessions if x.event_date is not None and
                             x.event_date > trigger_date_time]
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
        return []

    def sort_insights(self):
        self.insights = sorted(self.insights, key=lambda x: (int(x.read), x.priority, int(x.cleared)))
