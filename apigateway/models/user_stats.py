from models.movement_tags import Gender, RunningDistances, ProficiencyLevel
from serialisable import Serialisable
from models.load_stats import LoadStats
from models.session import HighLoadSession, HighDetailedLoadSession
from models.stats import StandardErrorRange
from models.periodization_plan import TrainingPhaseType, PeriodizationPersona
from models.periodization_goal import PeriodizationGoalType
from models.athlete_capacity import AthleteBaselineCapacities
from utils import parse_date, format_datetime, parse_datetime
from fathomapi.utils.exceptions import InvalidSchemaException


class UserStats(Serialisable):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id
        self.event_date = None
        self.api_version = '4_8'
        self.timezone = '-04:00'
        self.load_stats = LoadStats()
        self.sport_max_load = {}
        self.high_relative_load_sessions = []
        self.high_relative_load_score = 50
        self.eligible_for_high_load_trigger = False
        self.athlete_age = 25
        self.athlete_weight = 60.0
        self.athlete_height = 1.7
        self.athlete_gender = Gender.female

        self.expected_weekly_workouts = 3

        self.vo2_max = None
        self.vo2_max_date_time = None

        self.best_running_time = None
        self.best_running_distance = None
        self.best_running_date = None

        self.functional_threshold_power = None

        self.average_force_5_day = None
        self.average_force_20_day = None
        self.average_power_5_day = None
        self.average_power_20_day = None
        self.average_work_vo2_5_day = None
        self.average_work_vo2_20_day = None
        self.average_rpe_5_day = None
        self.average_rpe_20_day = None

        self.average_tissue_load_5_day = None
        self.average_tissue_load_20_day = None
        self.average_power_load_5_day = None
        self.average_power_load_20_day = None
        self.average_work_vo2_load_5_day = None
        self.average_work_vo2_load_20_day = None
        self.average_rpe_load_5_day = None
        self.average_rpe_load_20_day = None

        self.average_trimp_5_day = None
        self.average_trimp_20_day = None

        self.fitness_provider_cardio_profile = None
        self.strength_proficiency = None
        self.power_proficiency = None

        # training load monitoring
        # internal
        self.internal_ramp = None
        self.internal_monotony = None
        self.historical_internal_strain = []
        self.historical_internal_monotony = []
        self.internal_strain = None
        self.internal_strain_events = None
        self.acute_internal_total_load = None
        self.chronic_internal_total_load = None
        self.internal_acwr = None
        # self.internal_acwr_2 = None
        # self.internal_acwr_3 = None
        self.internal_freshness_index = None

        # power
        self.power_load_ramp = None
        self.power_load_monotony = None
        self.historical_power_load_strain = []
        self.historical_power_load_monotony = []
        self.power_load_strain = None
        self.power_load_strain_events = None
        self.acute_power_total_load = None
        self.chronic_power_total_load = None
        self.power_load_acwr = None
        self.power_load_freshness_index = None

        self.acute_days = 0
        self.chronic_days = 0
        self.total_historical_sessions = 0
        self.average_weekly_internal_load = None
        self.average_weekly_power_load = None
        self.average_session_internal_load = None
        self.average_session_power_load = None

        # periodization
        self.periodization_goals = []
        self.persona = None
        self.training_phase_type = None
        self.athlete_capacities = AthleteBaselineCapacities()

    def __setattr__(self, name, value):
        if name == 'event_date' and value is not None:
            if isinstance(value, str):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        elif name == 'vo2_max_date_time' and value is not None:
            value = parse_datetime(value)
        super().__setattr__(name, value)

    def json_serialise(self):
        ret = {
            'athlete_id': self.athlete_id,
            'event_date': format_datetime(self.event_date),
            'load_stats': self.load_stats.json_serialise() if self.load_stats is not None else None,
            'high_relative_load_sessions': [high_load.json_serialise() for high_load in self.high_relative_load_sessions],
            'eligible_for_high_load_trigger': self.eligible_for_high_load_trigger,
            'sport_max_load': {str(sport_name): sport_max_load.json_serialise() for (sport_name, sport_max_load) in self.sport_max_load.items()},
            'api_version': self.api_version,
            'timezone': self.timezone,
            'vo2_max': self.vo2_max.json_serialise() if self.vo2_max is not None else None,
            'vo2_max_date_time': format_datetime(self.vo2_max_date_time),
            'best_running_time': self.best_running_time,
            'best_running_distance': self.best_running_distance if self.best_running_distance is not None else None,
            'best_running_date': self.best_running_date,
            'athlete_age': self.athlete_age,
            'athlete_weight': self.athlete_weight,
            'athlete_height': self.athlete_height,
            'athlete_gender': self.athlete_gender.value if self.athlete_gender is not None else None,
            'functional_threshold_power': self.functional_threshold_power,
            'average_force_5_day': self.average_force_5_day.json_serialise() if self.average_force_5_day is not None else None,
            'average_force_20_day': self.average_force_20_day.json_serialise() if self.average_force_20_day is not None else None,
            'average_power_5_day': self.average_power_5_day.json_serialise() if self.average_power_5_day is not None else None,
            'average_power_20_day': self.average_power_20_day.json_serialise() if self.average_power_20_day is not None else None,
            'average_work_vo2_5_day': self.average_work_vo2_5_day.json_serialise() if self.average_work_vo2_5_day is not None else None,
            'average_work_vo2_20_day': self.average_work_vo2_20_day.json_serialise() if self.average_work_vo2_20_day is not None else None,
            'average_rpe_5_day': self.average_rpe_5_day.json_serialise() if self.average_rpe_5_day is not None else None,
            'average_rpe_20_day': self.average_rpe_20_day.json_serialise() if self.average_rpe_20_day is not None else None,
            'average_tissue_load_5_day': self.average_tissue_load_5_day.json_serialise() if self.average_tissue_load_5_day is not None else None,
            'average_tissue_load_20_day': self.average_tissue_load_20_day.json_serialise() if self.average_tissue_load_20_day is not None else None,
            'average_power_load_5_day': self.average_power_load_5_day.json_serialise() if self.average_power_load_5_day is not None else None,
            'average_power_load_20_day': self.average_power_load_20_day.json_serialise() if self.average_power_load_20_day is not None else None,
            'average_work_vo2_load_5_day': self.average_work_vo2_load_5_day.json_serialise() if self.average_work_vo2_load_5_day is not None else None,
            'average_work_vo2_load_20_day': self.average_work_vo2_load_20_day.json_serialise() if self.average_work_vo2_load_20_day is not None else None,
            'average_rpe_load_5_day': self.average_rpe_load_5_day.json_serialise() if self.average_rpe_load_5_day is not None else None,
            'average_rpe_load_20_day': self.average_rpe_load_20_day.json_serialise() if self.average_rpe_load_20_day is not None else None,
            'average_trimp_5_day': self.average_trimp_5_day.json_serialise() if self.average_trimp_5_day is not None else None,
            'average_trimp_20_day': self.average_trimp_20_day.json_serialise() if self.average_trimp_20_day is not None else None,
            'high_relative_load_score': self.high_relative_load_score,

            'fitness_provider_cardio_profile': self.fitness_provider_cardio_profile if self.fitness_provider_cardio_profile is not None else None,
            'strength_proficiency': self.strength_proficiency.value if self.strength_proficiency is not None else None,
            'power_proficiency': self.power_proficiency.value if self.power_proficiency is not None else None,

            'internal_ramp': self.internal_ramp.json_serialise() if self.internal_ramp is not None else None,
            'internal_monotony': self.internal_monotony.json_serialise() if self.internal_monotony is not None else None,
            'historical_internal_monotony': [h.json_serialise() for h in self.historical_internal_monotony],
            'internal_strain': self.internal_strain.json_serialise() if self.internal_strain is not None else None,
            'historical_internal_strain': [h.json_serialise() for h in self.historical_internal_strain],
            'internal_strain_events': self.internal_strain_events.json_serialise() if self.internal_strain_events is not None else None,
            'acute_internal_total_load': self.acute_internal_total_load.json_serialise() if self.acute_internal_total_load is not None else None,
            'chronic_internal_total_load': self.chronic_internal_total_load.json_serialise() if self.chronic_internal_total_load is not None else None,
            'internal_acwr': self.internal_acwr.json_serialise() if self.internal_acwr is not None else None,
            # 'internal_acwr_2': self.internal_acwr_2.json_serialise() if self.internal_acwr_2 is not None else None,
            # 'internal_acwr_3': self.internal_acwr_3.json_serialise() if self.internal_acwr_3 is not None else None,

            'power_load_ramp': self.power_load_ramp.json_serialise() if self.power_load_ramp is not None else None,
            'power_load_monotony': self.power_load_monotony.json_serialise() if self.power_load_monotony is not None else None,
            'historical_power_load_monotony': [h.json_serialise() for h in self.historical_power_load_monotony],
            'power_load_strain': self.power_load_strain.json_serialise() if self.power_load_strain is not None else None,
            'historical_power_load_strain': [h.json_serialise() for h in self.historical_power_load_strain],
            'power_load_strain_events': self.power_load_strain_events.json_serialise() if self.power_load_strain_events is not None else None,
            'acute_power_total_load': self.acute_power_total_load.json_serialise() if self.acute_power_total_load is not None else None,
            'chronic_power_total_load': self.chronic_power_total_load.json_serialise() if self.chronic_power_total_load is not None else None,
            'power_load_acwr': self.power_load_acwr.json_serialise() if self.power_load_acwr is not None else None,

            'acute_days': self.acute_days,
            'chronic_days': self.chronic_days,
            'total_historical_sessions': self.total_historical_sessions,

            'average_weekly_internal_load': self.average_weekly_internal_load.json_serialise() if self.average_weekly_internal_load is not None else None,
            'average_weekly_power_load': self.average_weekly_power_load.json_serialise() if self.average_weekly_power_load is not None else None,
            'average_session_internal_load': self.average_session_internal_load.json_serialise() if self.average_session_internal_load is not None else None,
            'average_session_power_load': self.average_session_power_load.json_serialise() if self.average_session_power_load is not None else None,

            'periodization_goals': [p.value for p in self.periodization_goals],
            'demo_persona': self.persona.value if self.persona is not None else None,
            'training_phase_type': self.training_phase_type.value if self.training_phase_type is not None else None,
            'athlete_capacities': self.athlete_capacities.json_serialise() if self.athlete_capacities is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        user_stats = cls(athlete_id=input_dict['athlete_id'])
        user_stats.event_date = input_dict.get('event_date')
        user_stats.api_version = input_dict.get('api_version', '4_8')
        user_stats.timezone = input_dict.get('timezone', '-04:00')
        user_stats.load_stats = LoadStats.json_deserialise(input_dict.get('load_stats', None))
        user_stats.high_relative_load_sessions = [HighLoadSession.json_deserialise(session) if 'sport_name' in session else HighDetailedLoadSession.json_deserialise(session) for session in input_dict.get('high_relative_load_sessions', [])]
        user_stats.eligible_for_high_load_trigger = input_dict.get('eligible_for_high_load_trigger', False)
        user_stats.sport_max_load = {int(sport_name): SportMaxLoad.json_deserialise(sport_max_load) for (sport_name, sport_max_load) in input_dict.get('sport_max_load', {}).items()}
        user_stats.vo2_max = StandardErrorRange.json_deserialise(input_dict.get('vo2_max')) if input_dict.get('vo2_max') is not None else None
        user_stats.best_running_time = input_dict.get('best_running_time')
        user_stats.best_running_distance = input_dict.get('best_running_distance')
        user_stats.best_running_date = input_dict.get('best_running_date')

        user_stats.functional_threshold_power = input_dict.get('functional_threshold_power')
        user_stats.average_force_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_force_5_day') is not None else None
        user_stats.average_force_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_force_20_day') is not None else None
        user_stats.average_power_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_power_5_day') is not None else None
        user_stats.average_power_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_power_20_day') is not None else None
        user_stats.average_work_vo2_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_work_vo2_5_day') is not None else None
        user_stats.average_work_vo2_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_work_vo2_20_day') is not None else None
        user_stats.average_rpe_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_rpe_5_day') is not None else None
        user_stats.average_rpe_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_rpe_20_day') is not None else None
        user_stats.average_force_load_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_force_load_5_day') is not None else None
        user_stats.average_force_load_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_force_load_20_day') is not None else None
        user_stats.average_power_load_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_power_load_5_day') is not None else None
        user_stats.average_power_load_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_power_load_20_day') is not None else None
        user_stats.average_work_vo2_load_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_work_vo2_load_5_day') is not None else None
        user_stats.average_work_vo2_load_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_work_vo2_load_20_day') is not None else None
        user_stats.average_rpe_load_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_rpe_load_5_day') is not None else None
        user_stats.average_rpe_load_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_rpe_load_20_day') is not None else None
        user_stats.average_trimp_5_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_trimp_5_day') is not None else None
        user_stats.average_trimp_20_day = StandardErrorRange.json_deserialise(input_dict) if input_dict.get('average_trimp_20_day') is not None else None
        user_stats.high_relative_load_score = input_dict.get('high_relative_load_score', 50)

        user_stats.fitness_provider_cardio_profile = input_dict.get('fitness_provider_cardio_profile')
        user_stats.strength_proficiency = ProficiencyLevel(input_dict['strength_proficiency']) if input_dict.get('strength_proficiency') is not None else ProficiencyLevel.novice
        user_stats.power_proficiency = ProficiencyLevel(input_dict['power_proficiency']) if input_dict.get('power_proficiency') is not None else ProficiencyLevel.novice

        user_stats.vo2_max_date_time = input_dict.get('vo2_max_date_time')
        user_stats.athlete_age = input_dict.get('athlete_age', 25)
        user_stats.athlete_weight = input_dict.get('athlete_weight', 60.0)
        user_stats.athlete_height = input_dict.get('athlete_height', 1.65)
        user_stats.athlete_gender = input_dict.get('athlete_gender') or Gender.female

        user_stats.acute_internal_total_load = StandardErrorRange.json_deserialise(input_dict.get('acute_internal_total_load', None))
        user_stats.chronic_internal_total_load = StandardErrorRange.json_deserialise(input_dict.get('chronic_internal_total_load', None))
        user_stats.internal_monotony = StandardErrorRange.json_deserialise(input_dict.get('internal_monotony', None))
        user_stats.historical_internal_monotony = [StandardErrorRange.json_deserialise(s)
                                                      for s in input_dict.get('historic_internal_monotony', [])]
        user_stats.internal_strain = StandardErrorRange.json_deserialise(input_dict.get('internal_strain', None))
        user_stats.historical_internal_strain = [StandardErrorRange.json_deserialise(s)
                                                    for s in input_dict.get('historic_internal_strain', [])]
        user_stats.internal_strain_events = StandardErrorRange.json_deserialise(input_dict.get('internal_strain_events', None))
        user_stats.internal_ramp = StandardErrorRange.json_deserialise(input_dict.get('internal_ramp', None))
        user_stats.internal_acwr = StandardErrorRange.json_deserialise(input_dict.get('internal_acwr', None))
        # user_stats.internal_acwr_2 = StandardErrorRange.json_deserialise(input_dict.get('internal_acwr_2', None))
        # user_stats.internal_acwr_3 = StandardErrorRange.json_deserialise(input_dict.get('internal_acwr_3', None))

        user_stats.acute_power_total_load = StandardErrorRange.json_deserialise(
            input_dict.get('acute_power_total_load', None))
        user_stats.chronic_power_total_load = StandardErrorRange.json_deserialise(
            input_dict.get('chronic_power_total_load', None))
        user_stats.power_load_monotony = StandardErrorRange.json_deserialise(input_dict.get('power_load_monotony', None))
        user_stats.historical_power_load_monotony = [StandardErrorRange.json_deserialise(s)
                                                   for s in input_dict.get('historical_power_load_monotony', [])]
        user_stats.power_load_strain = StandardErrorRange.json_deserialise(input_dict.get('power_load_strain', None))
        user_stats.historical_power_load_strain = [StandardErrorRange.json_deserialise(s)
                                                 for s in input_dict.get('historical_power_load_strain', [])]
        user_stats.power_load_strain_events = StandardErrorRange.json_deserialise(
            input_dict.get('power_load_strain_events', None))
        user_stats.power_load_ramp = StandardErrorRange.json_deserialise(input_dict.get('power_load_ramp', None))
        user_stats.power_load_acwr = StandardErrorRange.json_deserialise(input_dict.get('power_load_acwr', None))

        user_stats.acute_days = input_dict.get('acute_days', 0)
        user_stats.chronic_days = input_dict.get('chronic_days', 0)
        user_stats.total_historical_sessions = input_dict.get('total_historical_sessions', 0)
        user_stats.average_weekly_internal_load = StandardErrorRange.json_deserialise(input_dict['average_weekly_internal_load']) if input_dict.get('average_weekly_internal_load') is not None else None
        user_stats.average_weekly_power_load = StandardErrorRange.json_deserialise(
            input_dict['average_weekly_power_load']) if input_dict.get(
            'average_weekly_power_load') is not None else None
        user_stats.average_session_power_load = StandardErrorRange.json_deserialise(
            input_dict['average_session_power_load']) if input_dict.get(
            'average_session_power_load') is not None else None
        user_stats.average_session_internal_load = StandardErrorRange.json_deserialise(
            input_dict['average_session_internal_load']) if input_dict.get(
            'average_session_internal_load') is not None else None

        user_stats.periodization_goals = [PeriodizationGoalType(p) for p in input_dict.get('periodization_goals', [])]
        user_stats.persona = PeriodizationPersona(input_dict['demo_persona']) if input_dict.get('demo_persona') is not None else None
        user_stats.training_phase_type = TrainingPhaseType(input_dict['training_phase_type']) if input_dict.get('training_phase_type') is not None else None
        user_stats.athlete_capacities = AthleteBaselineCapacities().json_deserialise(input_dict['athlete_capacities']) if input_dict.get('athlete_capacities') is not None else None
        return user_stats


class SportMaxLoad(Serialisable):
    def __init__(self, event_date_time, load):
        self.event_date_time = event_date_time
        self.load = load
        self.first_time_logged = False

    def json_serialise(self):
        ret = {
            'event_date_time': format_datetime(self.event_date_time),
            'load': self.load,
            'first_time_logged': self.first_time_logged
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        sport_max_load = cls(parse_datetime(input_dict['event_date_time']), input_dict['load'])
        sport_max_load.first_time_logged = input_dict.get('first_time_logged', False)
        return sport_max_load
