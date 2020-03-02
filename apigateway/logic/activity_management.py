from fathomapi.utils.xray import xray_recorder

# from logic.soreness_processing import SorenessCalculator
from logic.injury_risk_processing import InjuryRiskProcessor
from logic.functional_exercise_mapping import ExerciseAssignmentCalculator
from models.athlete_injury_risk import AthleteInjuryRisk
from utils import parse_date


class ActivityManager(object):
    def __init__(self, athlete_id, datastore_collection, event_date_time, training_sessions=None, symptoms=None, user_stats=None):
        """
        :param athlete_id:
        :param datastore_collection:
        :param training_sessions:
        :param symptoms:
        :param event_date_time: when the request is made
        :param user_stats:
        """
        self.athlete_id = athlete_id
        self.event_date_time = event_date_time
        self.user_stats = user_stats
        self.training_session_datastore = datastore_collection.training_session_datastore
        self.symptom_datastore = datastore_collection.symptom_datastore
        self.user_stats_datastore = datastore_collection.user_stats_datastore
        self.injury_risk_datastore = datastore_collection.injury_risk_datastore
        self.exercise_library_datastore = datastore_collection.exercise_datastore
        self.completed_exercise_datastore = datastore_collection.completed_exercise_datastore
        self.movement_prep_datastore = datastore_collection.movement_prep_datastore
        self.mobility_wod_datastore = datastore_collection.mobility_wod_datastore
        self.responsive_recovery_datastore = datastore_collection.responsive_recovery_datastore
        self.training_sessions = training_sessions if training_sessions is not None else []
        self.symptoms = symptoms if symptoms is not None else []
        self.historical_injury_risk_dict = None
        self.exercise_assignemnt_calculator = None
        self.sessions_to_save_load = [session for session in self.training_sessions if session.session_load_dict is None]
        self.prepare_data()

    @xray_recorder.capture('logic.AcvitityManager.load_data')
    def load_data(self):
        # self.symptoms = self.symptom_datastore.get(self.athlete_id, event_date_time=self.event_date_time)
        if self.user_stats is None:
            self.user_stats = self.user_stats_datastore.get(self.athlete_id)
        self.historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)

    @xray_recorder.capture('logic.AcvitityManager.save_session_dict')
    def save_session_load_dict(self):
        for session in self.sessions_to_save_load:
            self.training_session_datastore.put(session)

    @xray_recorder.capture('logic.AcvitityManager.prepare_data')
    def prepare_data(self):
        self.load_data()
        # self.soreness_list = SorenessCalculator().update_soreness_list(self.soreness_list, self.symptoms)
        date = parse_date(self.event_date_time)

        # process injury risk with new information
        injury_risk_processor = InjuryRiskProcessor(
                date,
                self.symptoms,
                self.training_sessions,
                self.historical_injury_risk_dict,
                self.user_stats,
                self.athlete_id
        )
        consolidated_injury_risk_dict = injury_risk_processor.get_consolidated_dict()

        # initialize exercise assignment calculator
        self.exercise_assignemnt_calculator = ExerciseAssignmentCalculator(
                consolidated_injury_risk_dict,
                self.exercise_library_datastore,
                self.completed_exercise_datastore,
                self.event_date_time,
                injury_risk_processor.relative_load_level
        )
        # write updated injury risk
        athlete_injury_risk = AthleteInjuryRisk(self.athlete_id)
        athlete_injury_risk.items = injury_risk_processor.injury_risk_dict
        self.injury_risk_datastore.put(athlete_injury_risk)

    @xray_recorder.capture('logic.AcvitityManager.create_movement_prep')
    def create_movement_prep(self, force_on_demand=True):
        """
        :param force_on_demand: boolean
        :return movement_prep: MovementPrep
        """
        movement_prep = self.exercise_assignemnt_calculator.get_movement_prep(self.athlete_id, force_on_demand=force_on_demand)
        self.movement_prep_datastore.put(movement_prep)

        return movement_prep

    @xray_recorder.capture('logic.AcvitityManager.create_mobility_wod')
    def create_mobility_wod(self, force_on_demand=True):
        """
        :param force_on_demand: boolean
        :return mobility_wod: MobilityWOD
        """
        mobility_wod = self.exercise_assignemnt_calculator.get_mobility_wod(self.athlete_id, force_on_demand=force_on_demand)
        self.mobility_wod_datastore.put(mobility_wod)

        return mobility_wod

    @xray_recorder.capture('logic.AcvitityManager.create_responsive_recovery')
    def create_responsive_recovery(self, force_on_demand=True):
        """
        :param force_on_demand: boolean
        :return responsive_recovery: ResponsiveRecovery
        """
        responsive_recovery = self.exercise_assignemnt_calculator.get_responsive_recovery(self.athlete_id, force_on_demand=force_on_demand)
        self.responsive_recovery_datastore.put(responsive_recovery)
        self.save_session_load_dict()

        return responsive_recovery
