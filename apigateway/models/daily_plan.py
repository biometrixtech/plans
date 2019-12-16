from serialisable import Serialisable
from utils import parse_date
# import models.session as session
from models.session import Session
from models.daily_readiness import DailyReadiness
from models.modalities import IceSession, HeatSession, ColdWaterImmersion, WarmUp, CoolDown
from models.insights import AthleteInsight
from models.trigger import TriggerType
from models.athlete_trend import AthleteTrends
from models.soreness import Soreness
from models.modality import Modality, ModalityTypeDisplay, ModalityType
from models.functional_movement_modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining


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
               # 'ice': self.ice.json_serialise() if self.ice is not None else None,
               'ice': fake_ice(),  # TODO: revert this
               'completed_ice': [ice.json_serialise() for ice in self.completed_ice],
               # 'cold_water_immersion': self.cold_water_immersion.json_serialise() if self.cold_water_immersion is not None else None,
               'cold_water_immersion': fake_cwi(),  # TODO: revert this
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
            daily_plan.pre_active_rest = [ActiveRestBeforeTraining.json_deserialise(ar) for ar in input_dict.get('pre_active_rest', [])]
            daily_plan.completed_pre_active_rest = [ActiveRestBeforeTraining.json_deserialise(ar) for ar in input_dict.get('completed_pre_active_rest', [])]
            daily_plan.warm_up = [WarmUp.json_deserialise(warm_up) for warm_up in input_dict.get('warm_up', [])]
            daily_plan.completed_warm_up = [WarmUp.json_deserialise(w) for w in input_dict.get('completed_warm_up', [])]
            daily_plan.cool_down = [CoolDown.json_deserialise(cool_down) for cool_down in input_dict.get('cool_down', [])]
            daily_plan.completed_cool_down = [CoolDown.json_deserialise(cd) for cd in input_dict.get('completed_cool_down', [])]
            daily_plan.post_active_rest = [ActiveRestAfterTraining.json_deserialise(ar) for ar in input_dict.get('post_active_rest', [])]
            daily_plan.completed_post_active_rest = [ActiveRestAfterTraining.json_deserialise(ar) for ar in input_dict.get('completed_post_active_rest', [])]
            daily_plan.ice = IceSession.json_deserialise(input_dict['ice']) if input_dict.get('ice', None) is not None else None
            daily_plan.completed_ice = [IceSession.json_deserialise(ice) for ice in input_dict.get('completed_ice', [])]
            daily_plan.cold_water_immersion = ColdWaterImmersion.json_deserialise(input_dict['cold_water_immersion']) if input_dict.get('cold_water_immersion', None) is not None else None
            daily_plan.completed_cold_water_immersion = [ColdWaterImmersion.json_deserialise(cwi) for cwi in input_dict.get('completed_cold_water_immersion', [])]
            daily_plan.insights = [AthleteInsight.json_deserialise(insight) for insight in input_dict.get('insights', [])]
            daily_plan.trends = AthleteTrends.json_deserialise(input_dict['trends']) if input_dict.get('trends', None) is not None else None
            daily_plan.modalities = [Modality.json_deserialise(m) for m in input_dict.get('modalities', [])]
            daily_plan.completed_modalities = [Modality.json_deserialise(m) for m in input_dict.get('completed_modalities', [])]
            daily_plan.modalities_available_on_demand = [ModalityTypeDisplay.json_deserialise(md) for md in input_dict.get('modalities_available_on_demand', [])]
        # daily_plan.daily_readiness_survey = _daily_readiness_from_mongo(input_dict.get('daily_readiness_survey', None), daily_plan.user_id) # note that this deserialisation is still done in the datastore
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
        if not self.train_later:
            post_active_rest_available = True
            for m in self.modalities:
                if m.type.value == 1 and not m.completed:
                    post_active_rest_available = False
            if post_active_rest_available:
                self.modalities_available_on_demand = [ModalityTypeDisplay(ModalityType(1))]
        else:
            pre_active_rest_available = True
            for m in self.modalities:
                if m.type.value == 0 and not m.completed:
                    pre_active_rest_available = False
            if pre_active_rest_available:
                self.modalities_available_on_demand = [ModalityTypeDisplay(ModalityType(0))]


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
        #return [alert for alert in alerts if alert.goal.trigger_type != TriggerType.sore_today]
        return []

    def sort_insights(self):
        self.insights = sorted(self.insights, key=lambda x: (int(x.read), x.priority, int(x.cleared)))


def fake_cwi():
    return {
            "minutes" : 10,
            "after_training" : True,
            "goals" : [ 
                {
                    "text" : "Care for soreness",
                    "priority" : 1,
                    "goal_type" : 1
                }
            ],
            "start_date_time" : None,
            "completed_date_time" : None,
            "event_date_time" : None,
            "completed" : False,
            "active" : True,
            "alerts" : []
        }


def fake_ice():
    return {
                "minutes" : 15,
                "start_date_time" : None,
                "completed_date_time" : None,
                "event_date_time" : None,
                "completed" : False,
                "active" : True,
                "body_parts" : [ 
                    {
                        "body_part_location" : 12,
                        "goals" : [ 
                            {
                                "text" : "Care for soreness",
                                "priority" : 1,
                                "goal_type" : 1
                            }
                        ],
                        "after_training" : True,
                        "immediately_after_training" : False,
                        "repeat_every_3hrs_for_24hrs" : True,
                        "side" : 0,
                        "completed" : False,
                        "active" : True
                    }
                ],
                "alerts" : []
            }

def fake_modality():
    return [
            {
                "type": 3,
                "title": "Cool Down",
                "when": "Immediately After Workout",
                "when_card": "Immediately After Workout",
                "start_date_time" : None,
                "completed_date_time" : None,
                "event_date_time" : "2019-05-08T00:00:00Z",
                "completed" : False,
                "active" : True,
                "default_plan": "Complete",
                "force_data": False,
                "goal_title": " routine to:",  ## make dynamic based on selected routine
                "display_image": "dynamic_flexibility",
                "goals": {
                            "Recover from Rowing" : {
                                "efficient_active" : True,
                                "complete_active" : True,
                                "comprehensive_active" : True
                            },
                            "Recover from Running" : {
                                "efficient_active" : False,
                                "complete_active" : False,
                                "comprehensive_active" : False
                            }
                        },
                "exercise_phases":[
                    {
                        "type": 0,
                        "name": "Dynamic Stretch Exercises",
                        "title": "Dynamic Stretch",
                        "exercises" : [ 
                            {
                                "name" : "Foam Roller - Hamstrings",
                                "display_name" : "Foam Roll - Hamstrings",
                                "library_id" : "3",
                                "description" : "Place foam roller just before the glute & roll the length of your hamstring. If you find a tender spot, hold for 30 seconds. Don’t have a foam roller? You can use a tennis ball or water bottle. ",
                                "youtube_id" : None,
                                "bilateral" : True,
                                "seconds_per_rep" : None,
                                "seconds_per_set" : 30,
                                "unit_of_measure" : "seconds",
                                "position_order" : 0,
                                "duration_efficient" : 0,
                                "duration_complete" : 60,
                                "duration_comprehensive" : 120,
                                "goal_text" : "",
                                "equipment_required" : [ 
                                    "Foam Roller"
                                ],
                                "dosages" : [ 
                                    {
                                        "goal" : {
                                            "text" : "Recover from Rowing",
                                            "priority" : 1,
                                            "goal_type" : 2
                                        },
                                        "priority" : "2",
                                        "tier" : 2,
                                        "efficient_reps_assigned" : 0,
                                        "efficient_sets_assigned" : 0,
                                        "complete_reps_assigned" : 30,
                                        "complete_sets_assigned" : 1,
                                        "comprehensive_reps_assigned" : 30,
                                        "comprehensive_sets_assigned" : 1,
                                        "default_efficient_reps_assigned" : 0,
                                        "default_efficient_sets_assigned" : 0,
                                        "default_complete_reps_assigned" : 30,
                                        "default_complete_sets_assigned" : 1,
                                        "default_comprehensive_reps_assigned" : 30,
                                        "default_comprehensive_sets_assigned" : 1,
                                        "ranking" : 2
                                    }
                                ]
                            }
                        ]
                     },

                     {
                        "type": 1,
                        "name": "Dynamic Integrate Exercises",
                        "title": "Dynamic Integrate",
                        "exercises" : [ 
                            {
                                "name" : "Foam Roller - Hamstrings",
                                "display_name" : "Foam Roll - Hamstrings",
                                "library_id" : "3",
                                "description" : "Place foam roller just before the glute & roll the length of your hamstring. If you find a tender spot, hold for 30 seconds. Don’t have a foam roller? You can use a tennis ball or water bottle. ",
                                "youtube_id" : None,
                                "bilateral" : True,
                                "seconds_per_rep" : None,
                                "seconds_per_set" : 30,
                                "unit_of_measure" : "seconds",
                                "position_order" : 0,
                                "duration_efficient" : 0,
                                "duration_complete" : 60,
                                "duration_comprehensive" : 120,
                                "goal_text" : "",
                                "equipment_required" : [ 
                                    "Foam Roller"
                                ],
                                "dosages" : [ 
                                    {
                                        "goal" : {
                                            "text" : "Recover from Cycling",
                                            "priority" : 1,
                                            "goal_type" : 2
                                        },
                                        "priority" : "2",
                                        "tier" : 2,
                                        "efficient_reps_assigned" : 0,
                                        "efficient_sets_assigned" : 0,
                                        "complete_reps_assigned" : 30,
                                        "complete_sets_assigned" : 1,
                                        "comprehensive_reps_assigned" : 30,
                                        "comprehensive_sets_assigned" : 1,
                                        "default_efficient_reps_assigned" : 0,
                                        "default_efficient_sets_assigned" : 0,
                                        "default_complete_reps_assigned" : 30,
                                        "default_complete_sets_assigned" : 1,
                                        "default_comprehensive_reps_assigned" : 30,
                                        "default_comprehensive_sets_assigned" : 1,
                                        "ranking" : 2
                                    }
                                ]
                            }
                        ]
                     }
                ]
            }
            ]
