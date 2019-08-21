import abc
from enum import Enum
import uuid
import datetime
from serialisable import Serialisable
from utils import format_datetime, parse_datetime
from models.sport import SportName, SportType, BaseballPosition, BasketballPosition, FootballPosition, LacrossePosition, SoccerPosition, SoftballPosition, TrackAndFieldPosition, FieldHockeyPosition, VolleyballPosition
from models.post_session_survey import PostSurvey
from models.load_stats import LoadStats
from models.asymmetry import Asymmetry


class SessionType(Enum):
    practice = 0
    strength_and_conditioning = 1
    game = 2
    tournament = 3
    bump_up = 4
    corrective = 5
    sport_training = 6

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class StrengthConditioningType(Enum):
    "sub-type for session_type=1"
    endurance = 0
    power = 1
    speed_agility = 2
    strength = 3
    cross_training = 4
    none = None

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class DayOfWeek(Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class SessionSource(Enum):
    user = 0
    health = 1
    user_health = 2
    three_sensor = 3


class Session(Serialisable, metaclass=abc.ABCMeta):

    def __init__(self):
        self.id = None
        self.sport_name = None
        self.sport_type = None
        self.strength_and_conditioning_type = None
        self.duration_sensor = None
        self.external_load = None
        self.high_intensity_load = None
        self.mod_intensity_load = None
        self.low_intensity_load = None
        self.inactive_load = None
        self.high_intensity_minutes = None
        self.mod_intensity_minutes = None
        self.low_intensity_minutes = None
        self.inactive_minutes = None
        #self.high_intensity_RPE = None
        #self.mod_intensity_RPE = None
        #self.low_intensity_RPE = None
        self.post_session_soreness = []     # post_session_soreness object array
        self.duration_minutes = None
        self.created_date = None
        self.event_date = None
        self.end_date = None
        self.sensor_start_date_time = None
        self.sensor_end_date_time = None
        self.day_of_week = DayOfWeek.monday
        self.estimated = False
        self.internal_load_imputed = False
        self.external_load_imputed = False
        self.data_transferred = False
        self.movement_limited = False
        self.same_muscle_discomfort_over_72_hrs = False
        self.deleted = False
        self.ignored = False
        self.duration_health = None
        self.calories = None
        self.distance = None
        self.source = SessionSource.user
        self.shrz = None

        # post-session
        self.post_session_survey = None
        self.session_RPE = None
        self.performance_level = 100  # only answered if there is discomfort
        self.completion_percentage = 100    # only answered if there is discomfort
        self.sustained_injury_or_pain = False
        self.description = ""

        # three sensor
        self.asymmetry = None

    def __setattr__(self, name, value):
        if name in ['event_date', 'end_date', 'created_date', 'sensor_start_date_time', 'sensor_end_date_time']:
            if not isinstance(value, datetime.datetime) and value is not None:
                value = parse_datetime(value)
        elif name == "sport_name" and not isinstance(value, SportName):
            if value == '':
                value = SportName(None)
            else:
                try:
                    value = SportName(value)
                    self.sport_type = self.get_sport_type(value)
                except ValueError:
                    value = SportName(None)
        elif name == "sport_name" and isinstance(value, SportName):
            self.sport_type = self.get_sport_type(value)
        elif name == "strength_and_conditioning_type" and not isinstance(value, StrengthConditioningType):
            if value == '':
                value = StrengthConditioningType(None)
            else:
                value = StrengthConditioningType(value)
        elif name in "source":
            value = SessionSource(value) if value is not None else SessionSource.user
        elif name == ["deleted", "ignored"]:
            value = value if value is not None else False

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

    def cycling_load(self):
        return self.get_distance_load(SportName.cycling)

    def running_load(self):
        return self.get_distance_load(SportName.distance_running)

    def swimming_load(self):
        return self.get_distance_load(SportName.swimming)

    def walking_load(self):
        return self.get_distance_load(SportName.walking)

    def duration_minutes_load(self):
        return self.duration_minutes

        # distance_sports = [SportName.swimming, SportName.cycling, SportName.distance_running, SportName.walking]

        # if (self.sport_type == SportType.sport_endurance and self.duration_minutes is not None and
        #       self.session_RPE is not None and self.sport_name not in distance_sports):
        #     return self.duration_minutes
        # else:
        #     return None

    def duration_health_load(self):
        return self.duration_health

        # distance_sports = [SportName.swimming, SportName.cycling, SportName.distance_running, SportName.walking]
        #
        # if (self.sport_type == SportType.sport_endurance and self.duration_health is not None and
        #         self.duration_minutes is None and self.session_RPE is not None and
        #         self.sport_name not in distance_sports):
        #     return self.duration_health
        # else:
        #     return None

    def training_volume(self, load_stats):

        normalized_intensity = self.normalized_intensity()
        normalized_load = self.normalized_load(load_stats)

        if normalized_intensity is not None and normalized_load is not None:
            return normalized_intensity * normalized_load
        else:
            return None

    def normalized_intensity(self):

        if self.session_RPE is not None:
            return self.session_RPE
        elif self.shrz is not None:
            return self.shrz
        else:
            return 0

    def normalized_load(self, load_stats):

        duration_minutes_load = self.duration_minutes_load()
        duration_health_load = self.duration_health_load()
        walking_load = self.walking_load()
        swimming_load = self.swimming_load()
        running_load = self.running_load()
        cycling_load = self.cycling_load()

        load = 0

        duration_minutes_load = load_stats.get_duration_minutes_load(duration_minutes_load)
        duration_health_load = load_stats.get_duration_health_load(duration_health_load)
        walking_load = load_stats.get_walking_distance_load(walking_load)
        swimming_load = load_stats.get_swimming_distance_load(swimming_load)
        running_load = load_stats.get_running_distance_load(running_load)
        cycling_load = load_stats.get_cycling_distance_load(cycling_load)

        loads = []

        if duration_minutes_load is not None:
            loads.append(duration_minutes_load)
        if duration_health_load is not None:
            loads.append(duration_health_load)
        if walking_load is not None:
            loads.append(walking_load)
        if swimming_load is not None:
            loads.append(swimming_load)
        if running_load is not None:
            loads.append(running_load)
        if cycling_load is not None:
            loads.append(cycling_load)

        if len(loads) > 0:
            load = max(loads)

        return  load

    def get_distance_load(self, sport_name):
        if self.sport_name == sport_name is not None and self.distance is not None:
            return self.distance
        else:
            return None

    def get_sport_type(self, sport_name):

        ultra_high = [SportName.diving, SportName.jumps, SportName.throws, SportName.weightlifting, SportName.strength,
                      SportName.functional_strength_training, SportName.traditional_strength_training,
                      SportName.core_training, SportName.high_intensity_interval_training, SportName.pilates]

        unique_activites = [SportName.archery, SportName.bowling]

        load_not_managed = [SportName.fishing, SportName.mind_and_body, SportName.preparation_and_recovery,
                            SportName.flexibility]

        if sport_name in ultra_high:
            return SportType.ultra_high_intensity
        elif sport_name in unique_activites:
            return SportType.unique_activity
        elif sport_name in load_not_managed:
            return SportType.load_not_managed
        else:
            return SportType.sport_endurance

    def json_serialise(self):
        session_type = self.session_type()
        ret = {
            'session_id': self.id,
            'description': self.description,
            'session_type': session_type.value,
            'sport_name': self.sport_name.value,
            'strength_and_conditioning_type': self.strength_and_conditioning_type.value,
            'created_date': format_datetime(self.created_date),
            'event_date': format_datetime(self.event_date),
            'end_date': format_datetime(self.end_date),
            'duration_minutes': self.duration_minutes,
            'data_transferred': self.data_transferred,
            'duration_sensor': self.duration_sensor,
            'external_load': self.external_load,
            'high_intensity_minutes': self.high_intensity_minutes,
            'mod_intensity_minutes': self.mod_intensity_minutes,
            'low_intensity_minutes': self.low_intensity_minutes,
            'inactive_minutes': self.inactive_minutes,
            'high_intensity_load': self.high_intensity_load,
            'mod_intensity_load': self.mod_intensity_load,
            'low_intensity_load': self.low_intensity_load,
            'inactive_load': self.inactive_load,
            'sensor_start_date_time': format_datetime(self.sensor_start_date_time),
            'sensor_end_date_time': format_datetime(self.sensor_end_date_time),
            'post_session_survey': self.post_session_survey.json_serialise() if self.post_session_survey is not None else self.post_session_survey,
            'deleted': self.deleted,
            'ignored': self.ignored,
            'duration_health': self.duration_health,
            'shrz': self.shrz if self.shrz is not None else None,
            'calories': self.calories,
            'distance': self.distance,
            'source': self.source.value if self.source is not None else SessionSource.user.value,
            'asymmetry': self.asymmetry.json_serialise() if self.asymmetry is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        session = SessionFactory().create(SessionType(input_dict['session_type']))
        session.id = input_dict["session_id"]
        attrs_from_mongo = ["description",
                            "sport_name",
                            "strength_and_conditioning_type",
                            "created_date",
                            "event_date",
                            "end_date",
                            "duration_minutes",
                            "data_transferred",
                            "duration_sensor",
                            "external_load",
                            "high_intensity_minutes",
                            "mod_intensity_minutes",
                            "low_intensity_minutes",
                            "inactive_minutes",
                            "high_intensity_load",
                            "mod_intensity_load",
                            "low_intensity_load",
                            "inactive_load",
                            "sensor_start_date_time",
                            "sensor_end_date_time",
                            "deleted",
                            "ignored",
                            "duration_health",
                            "shrz",
                            "calories",
                            "distance",
                            "source"]
        for key in attrs_from_mongo:
            setattr(session, key, input_dict.get(key, None))
        if "post_session_survey" in input_dict and input_dict["post_session_survey"] is not None:
            session.post_session_survey = PostSurvey(input_dict["post_session_survey"], input_dict["post_session_survey"]["event_date"])
            session.session_RPE = session.post_session_survey.RPE if session.post_session_survey.RPE is not None else None
        else:
            session.post_session_survey = None
        session.asymmetry = Asymmetry.json_deserialise(input_dict['asymmetry']) if input_dict.get('asymmetry') is not None else None

        return session

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

        #if session_type == SessionType.practice:
        #    session_object = PracticeSession()
        if session_type == SessionType.game:
            session_object = Game()
        elif session_type == SessionType.bump_up:
            session_object = BumpUpSession()
        elif session_type == SessionType.strength_and_conditioning:
            session_object = StrengthConditioningSession()
        elif session_type == SessionType.tournament:
            session_object = Tournament()
        elif session_type == SessionType.sport_training:
            session_object = SportTrainingSession()
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

'''Deprecated
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
'''


class SportTrainingSession(Session):
    def __init__(self):
        Session.__init__(self)
        self.leads_to_soreness = False
        self.atypical_session_type = False
        self.atypical_high_load = False

    def session_type(self):
        return SessionType.sport_training

    def create(self):
        new_session = SportTrainingSession()
        new_session.id = str(uuid.uuid4())
        return new_session

    def missing_post_session_survey(self):
        return Session.missing_post_session_survey()

    def ultra_high_intensity_session(self):

        ultra_high_intensity_sports = [SportName.diving, SportName.jumps, SportName.throws, SportName.weightlifting,
                                       SportName.strength, SportName.functional_strength_training,
                                       SportName.traditional_strength_training, SportName.core_training,
                                       SportName.high_intensity_interval_training, SportName.pilates]

        if self.sport_name in ultra_high_intensity_sports:
            return True
        else:
            return False

    def high_intensity_RPE(self):

        if self.session_RPE is not None and self.session_RPE > 5:
            return True
        else:
            return False

    def high_intensity(self):

        if self.session_RPE is not None and self.session_RPE > 5 and self.ultra_high_intensity_session():
            return True
        elif self.session_RPE is not None and self.session_RPE >= 7 and not self.ultra_high_intensity_session():
            return True
        else:
            return False


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


class HighLoadSession(Serialisable):
    def __init__(self, date, sport_name):
        self.date = date
        self.sport_name = sport_name

    @classmethod
    def json_deserialise(cls, input_dict):

        session = HighLoadSession(parse_datetime(input_dict["date"]),  SportName(int(input_dict["sport_name"])))

        return session

    def json_serialise(self):
        ret = {
            'date': format_datetime(self.date),
            'sport_name': self.sport_name.value
        }

        return ret

'''deprecated
class FunctionalStrengthSession(Serialisable):

    def __init__(self):
        self.equipment_required = []
        self.warm_up = []
        self.dynamic_movement = []
        self.stability_work = []
        self.victory_lap = []
        self.duration_minutes = 0
        self.warm_up_target_minutes = 0
        self.dynamic_movement_target_minutes = 0
        self.stability_work_target_minutes = 0
        self.victory_lap_target_minutes = 0
        self.warm_up_max_percentage = 0
        self.dynamic_movement_max_percentage = 0
        self.stability_work_max_percentage = 0
        self.victory_lap_max_percentage = 0
        self.completed = False
        self.start_date = None
        self.event_date = None
        self.sport_name = None
        self.position = None

    def __setattr__(self, name, value):
        if name == "sport_name":
            try:
                value = SportName(value)
            except ValueError:
                value = SportName(None)
        elif name == "position":
            if self.sport_name == SportName.no_sport and value is not None:
                value = StrengthConditioningType(value)
            elif self.sport_name == SportName.soccer:
                value = SoccerPosition(value)
            elif self.sport_name == SportName.basketball:
                value = BasketballPosition(value)
            elif self.sport_name == SportName.baseball:
                value = BaseballPosition(value)
            elif self.sport_name == SportName.softball:
                value = SoftballPosition(value)
            elif self.sport_name == SportName.football:
                value = FootballPosition(value)
            elif self.sport_name == SportName.lacrosse:
                value = LacrossePosition(value)
            elif self.sport_name == SportName.track_field:
                value = TrackAndFieldPosition(value)
            elif self.sport_name == SportName.field_hockey:
                value = FieldHockeyPosition(value)
            elif self.sport_name == SportName.volleyball:
                value = VolleyballPosition(value)
        elif name in ['start_date', 'event_date']:
            if not isinstance(value, datetime.datetime) and value is not None:
                value = parse_datetime(value)
        super().__setattr__(name, value)

    def json_serialise(self):
            ret = {'equipment_required':  [e for e in self.equipment_required],
                   'minutes_duration': self.duration_minutes,
                   'completed': self.completed,
                   'start_date': format_datetime(self.start_date),
                   'event_date': format_datetime(self.event_date),
                   'warm_up': [ex.json_serialise() for ex in self.warm_up],
                   'dynamic_movement': [ex.json_serialise() for ex in self.dynamic_movement],
                   'stability_work': [ex.json_serialise() for ex in self.stability_work],
                   'victory_lap': [ex.json_serialise() for ex in self.victory_lap],
                   'sport_name': self.sport_name.value,
                   'position': self.position.value if self.position is not None else None
                   }
            return ret
'''

# class CompletedFunctionalStrengthSession(Serialisable):

#     def __init__(self, user_id, event_date, sport_name, position=None):
#         self.user_id = user_id
#         self.event_date = event_date
#         self.sport_name = sport_name,
#         self.position = position

#     def json_serialise(self):
#         ret = {'user_id': self.user_id,
#                'sport_name': self.sport_name,
#                'position': self.position,
#                'event_date': format_datetime(self.event_date),
#                }
#         return ret


# class CompletedFunctionalStrengthSummary(Serialisable):

#     def __init__(self, user_id, completed_count):
#         self.user_id = user_id
#         self.completed_count = completed_count

#     def json_serialise(self):
#         ret = {'user_id': self.user_id,
#                'completed_count': self.completed_count,
#                }
#         return ret


# class RecoverySession(Serialisable):

#     def __init__(self):
#         self.inhibit_exercises = []
#         self.lengthen_exercises = []
#         self.activate_exercises = []
#         self.integrate_exercises = []
#         self.duration_minutes = 0
#         self.inhibit_target_minutes = 0
#         self.lengthen_target_minutes = 0
#         self.activate_target_minutes = 0
#         self.integrate_target_minutes = 0

#         # new modalities
#         self.static_stretch_exercises = []
#         self.static_then_active_stretch_exercises = []
#         self.static_then_active_or_dynamic_stretch_exercises = []
#         self.active_stretch_exercises = []
#         self.active_or_dynamic_stretch_exercises = []
#         self.isolated_activation_exercises = []
#         self.dynamic_integrate_exercises = []
#         self.dynamic_integrate_with_speed_exercises = []
#         self.static_integrate_exercises = []
#         self.heat_minutes = 0
#         self.ice_minutes = 0
#         self.cold_water_immersion_minutes = 0
#         self.dynamic_movement_minutes = 0
#         self.dynamic_flexibility_minutes = 0
#         self.static_stretch_minutes = 0
#         self.active_stretch_minutes = 0

#         self.inhibit_iterations = 0
#         self.lengthen_iterations = 0
#         self.activate_iterations = 0
#         self.integrate_iterations = 0
#         self.inhibit_max_percentage = 0
#         self.lengthen_max_percentage = 0
#         self.activate_max_percentage = 0
#         self.integrate_max_percentage = 0
#         self.start_date = None
#         self.event_date = None
#         self.impact_score = 0
#         self.why_text = ""
#         self.goal_text = ""
#         self.completed = False
#         self.display_exercises = False

#     def __setattr__(self, name, value):
#         if name in ['start_date', 'event_date']:
#             if not isinstance(value, datetime.datetime) and value is not None:
#                 value = parse_datetime(value)
#         super().__setattr__(name, value)

#     def json_serialise(self):
#         ret = {'minutes_duration': self.duration_minutes,
#                'why_text': self.why_text,
#                'goal_text': self.goal_text,
#                'start_date': format_datetime(self.start_date),
#                'event_date': format_datetime(self.event_date),
#                'impact_score': self.impact_score,
#                'completed': self.completed,
#                'display_exercises': self.display_exercises,
#                'inhibit_exercises': [ex.json_serialise() for ex in self.inhibit_exercises],
#                'lengthen_exercises': [ex.json_serialise() for ex in self.lengthen_exercises],
#                'activate_exercises': [ex.json_serialise() for ex in self.activate_exercises],
#                'integrate_exercises': [ex.json_serialise() for ex in self.integrate_exercises],
#                'inhibit_iterations': self.inhibit_iterations,
#                'lengthen_iterations': self.lengthen_iterations,
#                'activate_iterations': self.activate_iterations,
#                'integrate_iterations': self.integrate_iterations,
#                }
#         return ret

#     def recommended_exercises(self):
#         exercise_list = []
#         exercise_list.extend(self.inhibit_exercises)
#         exercise_list.extend(self.lengthen_exercises)
#         exercise_list.extend(self.activate_exercises)
#         exercise_list.extend(self.integrate_exercises)

#         #for s in range(0, len(exercise_list)):
#         #    exercise_list[s].position_order = s

#         return exercise_list

#     def update_from_exercise_assignments(self, exercise_assignments):
#         self.inhibit_exercises = exercise_assignments.inhibit_exercises
#         self.lengthen_exercises = exercise_assignments.lengthen_exercises
#         self.activate_exercises = exercise_assignments.activate_exercises
#         self.integrate_exercises = exercise_assignments.integrate_exercises
#         self.duration_minutes = exercise_assignments.duration_minutes_target
#         # self.duration_minutes = (exercise_assignments.inhibit_minutes +
#         #                          exercise_assignments.lengthen_minutes +
#         #                          exercise_assignments.activate_minutes +
#         #                          exercise_assignments.integrate_minutes)

#         self.inhibit_iterations = exercise_assignments.inhibit_iterations
#         self.lengthen_iterations = exercise_assignments.lengthen_iterations
#         self.activate_iterations = exercise_assignments.activate_iterations
#         self.integrate_iterations = exercise_assignments.integrate_iterations

#         num = 0

#         for s in range(0, len(self.inhibit_exercises)):
#             self.inhibit_exercises[s].position_order = num
#             num = num + 1

#         for s in range(0, len(self.lengthen_exercises)):
#             self.lengthen_exercises[s].position_order = num
#             num = num + 1

#         for s in range(0, len(self.activate_exercises)):
#             self.activate_exercises[s].position_order = num
#             num = num + 1

#         for s in range(0, len(self.integrate_exercises)):
#             self.integrate_exercises[s].position_order = num
#             num = num + 1

#     #def set_exercise_target_minutes(self, soreness_list, total_minutes_target, max_severity, historic_soreness_present=False, functional_strength_active=False, is_active_prep=True):
#     def set_exercise_target_minutes(self, soreness_list, total_minutes_target, max_severity, historic_soreness_present=False, is_active_prep=True):
#         max_severity_and_historic_soreness = False
#         high_severity_is_pain = False

#         if soreness_list is not None:
#             for soreness in [s for s in soreness_list if s.daily]:
#                 if (not soreness.is_dormant_cleared() and
#                     soreness.severity == max_severity and
#                     soreness.severity > 0):
#                     max_severity_and_historic_soreness = True
#                 if soreness.severity > 3 and soreness.pain:
#                     high_severity_is_pain = True

#         if (max_severity > 3 and high_severity_is_pain) or (max_severity > 4 and not high_severity_is_pain):
#             self.integrate_target_minutes = 0
#             self.activate_target_minutes = 0
#             self.lengthen_target_minutes = 0
#             self.inhibit_target_minutes = 0
#             self.integrate_max_percentage = 0
#             self.activate_max_percentage = 0
#             self.lengthen_max_percentage = 0
#             self.inhibit_max_percentage = 0
#         elif total_minutes_target == 5:
#             self.integrate_target_minutes = 0
#             self.activate_target_minutes = 0
#             self.lengthen_target_minutes = 0
#             self.inhibit_target_minutes = total_minutes_target
#             self.integrate_max_percentage = 0
#             self.activate_max_percentage = 0
#             self.lengthen_max_percentage = 0
#             self.inhibit_max_percentage = 1.0
#         elif 3 < max_severity <= 4 and not high_severity_is_pain:
#             self.integrate_target_minutes = 0
#             self.activate_target_minutes = 0
#             self.lengthen_target_minutes = 0
#             self.inhibit_target_minutes = total_minutes_target
#             self.integrate_max_percentage = 0
#             self.activate_max_percentage = 0
#             self.lengthen_max_percentage = 0
#             self.inhibit_max_percentage = 1.0
#         elif max_severity == 3:
#             if max_severity_and_historic_soreness:
#                 #if not functional_strength_active:
#                 self.set_70_30_time_split(total_minutes_target)
#                 #else:
#                 #    self.set_50_50_time_split(total_minutes_target)
#             elif historic_soreness_present:
#                 #if not functional_strength_active:
#                 self.set_60_40_time_split(total_minutes_target)
#                 #else:
#                 #    self.set_50_50_time_split(total_minutes_target)
#             else:
#                 self.set_50_50_time_split(total_minutes_target)
#         elif max_severity == 2:
#             if max_severity_and_historic_soreness:
#                 #if not functional_strength_active:
#                 if is_active_prep:
#                     self.set_35_35_30_time_split(total_minutes_target)
#                 else:
#                     self.set_40_40_20_time_split(total_minutes_target)
#                 #else:
#                 #    self.set_40_60_time_split(total_minutes_target)
#             elif historic_soreness_present:
#                 #if not functional_strength_active:
#                 if is_active_prep:
#                     self.set_30_30_40_time_split(total_minutes_target)
#                 else:
#                     self.set_40_40_20_time_split(total_minutes_target)
#                 #else:
#                 #    self.set_50_50_time_split(total_minutes_target)
#             else:
#                 self.set_33_33_33_time_split(total_minutes_target)
#         elif 0 < max_severity <= 1:
#             if max_severity_and_historic_soreness:
#                 #if not functional_strength_active:
#                 if is_active_prep:
#                     self.set_30_30_40_time_split(total_minutes_target)
#                 else:
#                     self.set_40_40_20_time_split(total_minutes_target)
#                 #else:
#                 #    # no difference between AP/AR
#                 #    self.set_40_60_time_split(total_minutes_target)
#             elif historic_soreness_present:
#                 #if not functional_strength_active:
#                 if is_active_prep:
#                     self.set_35_35_30_time_split(total_minutes_target)
#                 else:
#                     self.set_40_40_20_time_split(total_minutes_target)
#                 #else:
#                 # no difference between AP/AR
#                 #self.set_50_50_time_split(total_minutes_target)
#             else:
#                 self.set_25_25_50_time_split(total_minutes_target)

#         elif max_severity == 0:
#             if historic_soreness_present:
#                 #if not functional_strength_active:
#                 if is_active_prep:
#                     self.set_25_25_50_time_split(total_minutes_target)
#                 else:
#                     self.set_35_35_30_time_split(total_minutes_target)
#                 #else:
#                     # no difference between AP/AR
#                 #    self.set_50_50_time_split(total_minutes_target)
#             else:
#                 self.set_25_25_50_time_split(total_minutes_target)

#         if total_minutes_target == 10:
#             lengthen_percentage = self.lengthen_target_minutes / (self.lengthen_target_minutes + self.inhibit_target_minutes)
#             inhibit_percentage = self.inhibit_target_minutes / (self.lengthen_target_minutes + self.inhibit_target_minutes)
#             self.integrate_target_minutes = None
#             self.activate_target_minutes = None
#             self.lengthen_target_minutes = total_minutes_target * lengthen_percentage
#             self.inhibit_target_minutes = total_minutes_target * inhibit_percentage
#             self.integrate_max_percentage = None
#             self.activate_max_percentage = None
#             self.lengthen_max_percentage = lengthen_percentage + .1
#             self.inhibit_max_percentage = inhibit_percentage + .1

#     def set_70_30_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = None
#         self.lengthen_target_minutes = total_minutes_target / 3.3
#         self.inhibit_target_minutes = total_minutes_target / 1.43
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = None
#         self.lengthen_max_percentage = .4
#         self.inhibit_max_percentage = .8


#     def set_60_40_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = None
#         self.lengthen_target_minutes = total_minutes_target / 2.5
#         self.inhibit_target_minutes = total_minutes_target / 1.67
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = None
#         self.lengthen_max_percentage = .5
#         self.inhibit_max_percentage = .7


#     def set_40_60_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = None
#         self.lengthen_target_minutes = total_minutes_target / 1.67
#         self.inhibit_target_minutes = total_minutes_target / 2.5
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = None
#         self.lengthen_max_percentage = .7
#         self.inhibit_max_percentage = .5

#     def set_30_30_40_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = total_minutes_target / 2.5
#         self.lengthen_target_minutes = total_minutes_target / 3.3
#         self.inhibit_target_minutes = total_minutes_target / 3.3
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = .45
#         self.lengthen_max_percentage = .35
#         self.inhibit_max_percentage = .35

#     def set_33_33_33_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = total_minutes_target / 3
#         self.lengthen_target_minutes = total_minutes_target / 3
#         self.inhibit_target_minutes = total_minutes_target / 3
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = .4
#         self.lengthen_max_percentage = .4
#         self.inhibit_max_percentage = .4

#     def set_25_25_50_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = total_minutes_target / 2
#         self.lengthen_target_minutes = total_minutes_target / 4
#         self.inhibit_target_minutes = total_minutes_target / 4
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = .6
#         self.lengthen_max_percentage = .3
#         self.inhibit_max_percentage = .3

#     def set_50_50_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = None
#         self.lengthen_target_minutes = total_minutes_target / 2
#         self.inhibit_target_minutes = total_minutes_target / 2
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = None
#         self.lengthen_max_percentage = .6
#         self.inhibit_max_percentage = .6

#     def set_40_40_20_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = total_minutes_target / 5
#         self.lengthen_target_minutes = total_minutes_target / 2.5
#         self.inhibit_target_minutes = total_minutes_target / 2.5
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = .3
#         self.lengthen_max_percentage = .5
#         self.inhibit_max_percentage = .5

#     def set_35_35_30_time_split(self, total_minutes_target):
#         self.integrate_target_minutes = None
#         self.activate_target_minutes = total_minutes_target / 3.3
#         self.lengthen_target_minutes = total_minutes_target / 2.85
#         self.inhibit_target_minutes = total_minutes_target / 2.85
#         self.integrate_max_percentage = None
#         self.activate_max_percentage = .4
#         self.lengthen_max_percentage = .4
#         self.inhibit_max_percentage = .4


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
