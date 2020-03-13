import abc
from enum import Enum
import uuid
import datetime
from serialisable import Serialisable
from utils import format_datetime, parse_datetime
from models.sport import SportName, SportType, BaseballPosition, BasketballPosition, FootballPosition, LacrossePosition, SoccerPosition, SoftballPosition, TrackAndFieldPosition, FieldHockeyPosition, VolleyballPosition
from models.post_session_survey import PostSurvey
# from models.load_stats import LoadStats
from models.asymmetry import Asymmetry
from models.movement_patterns import MovementPatterns
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.workout_program import WorkoutProgramModule
from models.functional_movement import BodyPartFunctionalMovement, BodyPartFunction
from models.movement_tags import TrainingType, AdaptationType


class SessionType(Enum):
    practice = 0
    strength_and_conditioning = 1
    game = 2
    tournament = 3
    bump_up = 4
    corrective = 5
    sport_training = 6
    mixed_activity = 7

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
        self.user_id = None
        self.id = None
        self.apple_health_kit_id = None
        self.apple_health_kit_source_name = None
        self.source_session_ids = []
        self.merged_apple_health_kit_ids = []
        self.merged_apple_health_kit_source_names = []
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
        self.completed_date_time = None
        self.event_date = None
        self.end_date = None
        self.last_updated = None
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
        self.movement_patterns = None
        # self.overactive_body_parts = []
        # self.underactive_inhibited_body_parts = []
        # self.underactive_weak_body_parts = []
        # self.compensating_body_parts = []
        # self.short_body_parts = []
        # self.long_body_parts = []

        # workout content provider
        self.workout_program_module = None

        self.session_load_dict = None

        self.not_tracked_load = None
        self.strength_endurance_cardiorespiratory_load = None
        self.strength_endurance_strength_load = None
        self.power_drill_load = None
        self.maximal_strength_hypertrophic_load = None
        self.power_explosive_action_load = None

    def __setattr__(self, name, value):
        if name in ['event_date', 'end_date', 'created_date', 'completed_date_time', 'sensor_start_date_time', 'sensor_end_date_time', 'last_updated']:
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
        elif name == "workout_program_module" and not isinstance(value, WorkoutProgramModule):
            value = WorkoutProgramModule.json_deserialise(value) if value is not None else None
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

    # @abc.abstractmethod
    # def missing_post_session_survey(self):
    #     if self.session_RPE is None:
    #         return True
    #     elif self.post_session_soreness is None and (self.movement_limited or self.same_muscle_discomfort_over_72_hrs):
    #         return True
    #     else:
    #         return False

    def cycling_training_volume(self):
        return self.get_distance_training_volume(SportName.cycling)

    def running_training_volume(self):
        return self.get_distance_training_volume(SportName.distance_running)

    def swimming_training_volume(self):
        return self.get_distance_training_volume(SportName.swimming)

    def walking_training_volume(self):
        return self.get_distance_training_volume(SportName.walking)

    def duration_minutes_training_volume(self):
        return self.duration_minutes

        # distance_sports = [SportName.swimming, SportName.cycling, SportName.distance_running, SportName.walking]

        # if (self.sport_type == SportType.sport_endurance and self.duration_minutes is not None and
        #       self.session_RPE is not None and self.sport_name not in distance_sports):
        #     return self.duration_minutes
        # else:
        #     return None

    def duration_health_training_volume(self):
        return self.duration_health

        # distance_sports = [SportName.swimming, SportName.cycling, SportName.distance_running, SportName.walking]
        #
        # if (self.sport_type == SportType.sport_endurance and self.duration_health is not None and
        #         self.duration_minutes is None and self.session_RPE is not None and
        #         self.sport_name not in distance_sports):
        #     return self.duration_health
        # else:
        #     return None

    def training_load(self, load_stats):

        normalized_intensity = self.normalized_intensity()
        normalized_training_volume = self.normalized_training_volume(load_stats)

        if normalized_intensity is not None and normalized_training_volume is not None:
            return normalized_intensity * normalized_training_volume
        else:
            return None

    def normalized_intensity(self):

        if self.session_RPE is not None:
            return self.session_RPE
        elif self.shrz is not None:
            return self.shrz
        else:
            return 0

    def normalized_training_volume(self, load_stats):

        duration_minutes_load = self.duration_minutes_training_volume()
        duration_health_load = self.duration_health_training_volume()
        walking_load = self.walking_training_volume()
        swimming_load = self.swimming_training_volume()
        running_load = self.running_training_volume()
        cycling_load = self.cycling_training_volume()

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

    def get_distance_training_volume(self, sport_name):
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
            'user_id': self.user_id,
            'session_id': self.id,
            'apple_health_kit_id': self.apple_health_kit_id,
            'apple_health_kit_source_name': self.apple_health_kit_source_name,
            'merged_apple_health_kit_ids': [a for a in self.merged_apple_health_kit_ids],
            'source_session_ids': [a for a in self.source_session_ids],
            'merged_apple_health_kit_source_names': [a for a in self.merged_apple_health_kit_source_names],
            'description': self.description,
            'session_type': session_type.value,
            'sport_name': self.sport_name.value,
            'strength_and_conditioning_type': self.strength_and_conditioning_type.value,
            'created_date': format_datetime(self.created_date),
            'completed_date_time': format_datetime(self.completed_date_time),
            'event_date': format_datetime(self.event_date),
            'end_date': format_datetime(self.end_date),
            'last_updated': format_datetime(self.last_updated),
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
            'asymmetry': self.asymmetry.json_serialise() if self.asymmetry is not None else None,
            'movement_patterns': self.movement_patterns.json_serialise() if self.movement_patterns is not None else None,
            # 'workout_program_module': self.workout_program_module.json_serialise() if self.workout_program_module is not None else None,
            'session_RPE': self.session_RPE,
            'session_load_dict': [{"body_part": key.json_serialise(),
                                   "injury_risk": value.json_serialise()} for key, value in self.session_load_dict.items()] if self.session_load_dict is not None else None,

            'not_tracked_load': self.not_tracked_load if self.not_tracked_load is not None else None,
            'strength_endurance_cardiorespiratory_load': self.strength_endurance_cardiorespiratory_load if self.strength_endurance_cardiorespiratory_load is not None else None,
            'strength_endurance_strength_load': self.strength_endurance_strength_load if self.strength_endurance_strength_load is not None else None,
            'power_drill_load': self.power_drill_load if self.power_drill_load is not None else None,
            'maximal_strength_hypertrophic_load': self.maximal_strength_hypertrophic_load if self.maximal_strength_hypertrophic_load is not None else None,
            'power_explosive_action_load': self.power_explosive_action_load if self.power_explosive_action_load is not None else None

            # 'overactive_body_parts': [o.json_serialise() for o in self.overactive_body_parts],
            # 'underactive_inhibited_body_parts': [u.json_serialise() for u in self.underactive_inhibited_body_parts],
            # 'underactive_weak_body_parts': [u.json_serialise() for u in self.underactive_weak_body_parts],
            # 'compensating_body_parts': [c.json_serialise() for c in self.compensating_body_parts],
            # 'short_body_parts': [c.json_serialise() for c in self.short_body_parts],
            # 'long_body_parts': [c.json_serialise() for c in self.long_body_parts],
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        session = SessionFactory().create(SessionType(input_dict['session_type']))
        session.id = input_dict["session_id"]
        session.user_id = input_dict.get("user_id")
        session.apple_health_kit_id = input_dict.get("apple_health_kit_id")
        session.apple_health_kit_source_name = input_dict.get("apple_health_kit_source_name")
        session.merged_apple_health_kit_ids = input_dict.get("merged_apple_health_kit_ids", [])
        session.source_session_ids = input_dict.get("source_session_ids", [])
        session.merged_apple_health_kit_source_names = input_dict.get("merged_apple_health_kit_source_names", [])
        attrs_from_mongo = ["description",
                            "sport_name",
                            "strength_and_conditioning_type",
                            "created_date",
                            "completed_date_time",
                            "event_date",
                            "end_date",
                            "last_updated",
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
                            "source",
                            "session_RPE"]
        for key in attrs_from_mongo:
            setattr(session, key, input_dict.get(key, None))
        if "post_session_survey" in input_dict and input_dict["post_session_survey"] is not None:
            session.post_session_survey = PostSurvey(input_dict["post_session_survey"], input_dict["post_session_survey"]["event_date"])
            if session.post_session_survey.RPE is not None:
                session.session_RPE = session.post_session_survey.RPE
        else:
            session.post_session_survey = None
        session.asymmetry = Asymmetry.json_deserialise(input_dict['asymmetry']) if input_dict.get('asymmetry') is not None else None
        session.movement_patterns = MovementPatterns.json_deserialise(input_dict['movement_patterns']) if input_dict.get(
            'movement_patterns') is not None else None
        # session.workout_program_module = WorkoutProgramModule.json_deserialise(input_dict['workout_program_module']) if input_dict.get('workout_program_module') is not None else None
        if input_dict.get('session_load_dict') is not None:
            session.session_load_dict = {}
            for item in input_dict.get('session_load_dict', []):
                session.session_load_dict[BodyPartSide.json_deserialise(item['body_part'])] = BodyPartFunctionalMovement.json_deserialise(item['injury_risk'])
        else:
            session.session_load_dict = None

        session.not_tracked_load = input_dict.get('not_tracked_load')
        session.strength_endurance_cardiorespiratory_load = input_dict.get('strength_endurance_cardiorespiratory_load')
        session.strength_endurance_strength_load = input_dict.get('strength_endurance_strength_load')
        session.power_drill_load = input_dict.get('power_drill_load')
        session.maximal_strength_hypertrophic_load = input_dict.get('maximal_strength_hypertrophic_load')
        session.power_explosive_action_load = input_dict.get('power_explosive_action_load')

        # session.overactive_body_parts = [BodyPartSide.json_deserialise(o) for o in input_dict.get('overactive_body_parts', [])]
        # session.underactive_inhibited_body_parts = [BodyPartSide.json_deserialise(u) for u in input_dict.get('underactive_inhibited_body_parts',[])]
        # session.underactive_weak_body_parts = [BodyPartSide.json_deserialise(u) for u in
        #                                             input_dict.get('underactive_weak_body_parts',[])]
        # session.compensating_body_parts = [BodyPartSide.json_deserialise(c) for c in input_dict.get('compensating_body_parts',[])]
        # session.short_body_parts = [BodyPartSide.json_deserialise(c) for c in input_dict.get('short_body_parts',[])]
        # session.long_body_parts = [BodyPartSide.json_deserialise(c) for c in input_dict.get('long_body_parts',[])]
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

    def get_load_body_parts(self):
        body_parts = {}

        if self.session_load_dict is not None:
            for body_part_side, body_part_functional_movement in self.session_load_dict.items():
                muscle_group = BodyPartLocation.get_muscle_group(body_part_side.body_part_location)
                body_part_function = body_part_functional_movement.body_part_function
                if isinstance(muscle_group, BodyPartLocation):
                    body_part_location = muscle_group
                else:
                    body_part_location = body_part_side.body_part_location
                if body_part_location in body_parts:
                    body_part_function = BodyPartFunction.merge(body_part_function, body_parts[body_part_location])
                body_parts[body_part_location] = body_part_function

        return body_parts

    def is_cardio_plyometrics(self):
        return False

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
        elif session_type == SessionType.mixed_activity:
            session_object = MixedActivitySession()
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

    # def missing_post_session_survey(self):
    #     return Session.missing_post_session_survey()


class MixedActivitySession(Session):
    def __init__(self):
        Session.__init__(self)
        self.leads_to_soreness = False
        self.atypical_session_type = False
        self.atypical_high_load = False
        self.sport_name = SportName.other

    def session_type(self):
        return SessionType.mixed_activity

    def create(self):
        new_session = MixedActivitySession()
        new_session.id = str(uuid.uuid4())
        return new_session

    # def missing_post_session_survey(self):
    #     return Session.missing_post_session_survey()

    def ultra_high_intensity_session(self):
        if self.workout_program_module is not None:
            for section in self.workout_program_module.workout_sections:
                if section.assess_load:
                    for exercise in section.exercises:
                        for action in exercise.primary_actions:
                            if action.training_type in [TrainingType.power_action_plyometrics, TrainingType.power_drills_plyometrics] or action.adaptation_type == AdaptationType.maximal_strength_hypertrophic:
                                return True
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

    def training_load(self, load_stats):

        #training_load = self.workout_program_module.get_training_load()

        #return training_load
        return None

    def is_cardio_plyometrics(self):
        # TODO: Validate/Update this logic
        if self.workout_program_module is not None:
            for section in self.workout_program_module.workout_sections:
                if section.assess_load:
                    for exercise in section.exercises:
                        if exercise.training_type in [TrainingType.strength_cardiorespiratory, TrainingType.power_drills_plyometrics, TrainingType.power_action_plyometrics]:
                            return True
        return False


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

    # def missing_post_session_survey(self):
    #     return Session.missing_post_session_survey()

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

    def is_cardio_plyometrics(self):
        # TODO: Validate list/approach
        cardio_sports = [
            SportName.cycling, SportName.rowing, SportName.distance_running,
            SportName.dance, SportName.swimming, SportName.endurance,
            SportName.elliptical, SportName.hiking, SportName.stair_climbing,
            SportName.walking, SportName.water_fitness, SportName.yoga,
            SportName.barre, SportName.high_intensity_interval_training, SportName.jump_rope,
            SportName.pilates, SportName.stairs, SportName.step_training,
            SportName.wheelchair_walk_pace, SportName.wheelchair_run_pace, SportName.mixed_cardio,
            SportName.taichi, SportName.hand_cycling, SportName.climbing,
        ]
        if self.sport_name is not None:
            if self.sport_name in cardio_sports:
                return True
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

    # def missing_post_session_survey(self):
    #     return Session.missing_post_session_survey()


class Game(Session):
    def __init__(self):
        Session.__init__(self)

    def session_type(self):
        return SessionType.game

    def create(self):
        new_session = Game()
        new_session.id = str(uuid.uuid4())
        return new_session

    # def missing_post_session_survey(self):
    #     return Session.missing_post_session_survey()


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

    # def missing_post_session_survey(self):
    #     return Session.missing_post_session_survey()


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

    # def missing_post_session_survey(self):
    #     if self.session_RPE is None:
    #         return True
    #     else:
    #         return False


class HighDetailedLoadSession(Serialisable):
    def __init__(self, date):
        self.date = date
        self.percent_of_max = None

    @classmethod
    def json_deserialise(cls, input_dict):

        session = HighDetailedLoadSession(parse_datetime(input_dict["date"]))
        session.percent_of_max = input_dict['percent_of_max'] if input_dict.get('percent_of_max') is not None else None
        return session

    def json_serialise(self):
        ret = {
            'date': format_datetime(self.date),
            'percent_of_max': self.percent_of_max if self.percent_of_max is not None else None
        }

        return ret


class HighLoadSession(Serialisable):
    def __init__(self, date, sport_name):
        self.date = date
        self.sport_name = sport_name
        self.percent_of_max = None

    @classmethod
    def json_deserialise(cls, input_dict):

        session = HighLoadSession(parse_datetime(input_dict["date"]),  SportName(int(input_dict["sport_name"])))
        session.percent_of_max = input_dict['percent_of_max'] if input_dict.get('percent_of_max') is not None else None
        return session

    def json_serialise(self):
        ret = {
            'date': format_datetime(self.date),
            'sport_name': self.sport_name.value,
            'percent_of_max': self.percent_of_max if self.percent_of_max is not None else None
        }

        return ret


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
