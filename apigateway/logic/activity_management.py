from fathomapi.utils.xray import xray_recorder

# from logic.soreness_processing import SorenessCalculator
from logic.injury_risk_processing import InjuryRiskProcessor
#from logic.functional_exercise_mapping import ExerciseAssignmentCalculator
from logic.exercise_assignment import ExerciseAssignment
from models.athlete_injury_risk import AthleteInjuryRisk


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
        self.exercise_assignment_calculator = None
        self.active_training_sessions = [session for session in self.training_sessions]
        self.load_data()

    @xray_recorder.capture('logic.ActivityManager.load_data')
    def load_data(self):
        # self.symptoms = self.symptom_datastore.get(self.athlete_id, event_date_time=self.event_date_time)
        if self.user_stats is None:
            self.user_stats = self.user_stats_datastore.get(self.athlete_id)
        self.historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)
        training_sessions_from_mongo = self.training_session_datastore.get(user_id=self.athlete_id, event_date_time=self.event_date_time)
        current_training_session_ids = [session.id for session in self.training_sessions]
        training_sessions_to_add = [session for session in training_sessions_from_mongo if session.id not in current_training_session_ids]
        self.training_sessions.extend(training_sessions_to_add)

    @xray_recorder.capture('logic.ActivityManager.save_session_dict')
    def save_session(self):
        for session in self.active_training_sessions:
            self.training_session_datastore.put(session)

    def get_session_details(self):
        self.exercise_assignment_calculator.sport_cardio_plyometrics = self.check_cardio_sport()
        self.exercise_assignment_calculator.sport_body_parts = self.get_sport_body_parts()
        self.exercise_assignment_calculator.high_intensity_session = self.is_high_intensity_session()

    def is_high_intensity_session(self):
        for session in self.active_training_sessions:
            if session.ultra_high_intensity_session() and session.high_intensity_RPE():
                return True
        return False

    def get_sport_body_parts(self):
        sport_body_parts = {}
        for session in self.active_training_sessions:
            sport_body_parts.update(session.get_load_body_parts())
        return sport_body_parts

    def check_cardio_sport(self):
        sport_cardio_plyometrics = False
        for session in self.active_training_sessions:
            if session.is_cardio_plyometrics():
                sport_cardio_plyometrics = True
        return sport_cardio_plyometrics

    @xray_recorder.capture('logic.ActivityManager.prepare_data')
    def prepare_data(self, default_rpe=None):

        # self.soreness_list = SorenessCalculator().update_soreness_list(self.soreness_list, self.symptoms)
        if default_rpe is not None:
            for t in self.training_sessions:
                if t.session_RPE is None:
                    t.session_RPE = default_rpe

        # process injury risk with new information
        injury_risk_processor = InjuryRiskProcessor(
                self.event_date_time,
                self.symptoms,
                self.training_sessions,
                self.historical_injury_risk_dict,
                self.user_stats,
                self.athlete_id
        )
        injury_risk_processor.process()
        consolidated_injury_risk_dict = injury_risk_processor.get_consolidated_dict()

        # initialize exercise assignment calculator
        self.exercise_assignment_calculator = ExerciseAssignment(
                injury_risk_dict=consolidated_injury_risk_dict,
                exercise_library_datastore=self.exercise_library_datastore,
                completed_exercise_datastore=self.completed_exercise_datastore,
                event_date_time=self.event_date_time,
                relative_load_level=injury_risk_processor.relative_load_level,
                aggregated_injury_risk_dict=injury_risk_processor.aggregated_injury_risk_dict
        )
        # write updated injury risk
        athlete_injury_risk = AthleteInjuryRisk(self.athlete_id)
        athlete_injury_risk.items = injury_risk_processor.injury_risk_dict
        self.injury_risk_datastore.put(athlete_injury_risk)

    @xray_recorder.capture('logic.ActivityManager.create_movement_prep')
    def create_movement_prep(self, force_on_demand=True):
        """
        :param force_on_demand: boolean
        :return movement_prep: MovementPrep
        """
        self.prepare_data(8)  # we don't want to persist this RPE
        self.get_session_details()
        movement_prep = self.exercise_assignment_calculator.get_movement_prep(self.athlete_id, force_on_demand=force_on_demand)
        movement_prep.training_session_id = self.active_training_sessions[0].id
        self.movement_prep_datastore.put(movement_prep)
        self.save_session()

        return movement_prep

    @xray_recorder.capture('logic.ActivityManager.create_mobility_wod')
    def create_mobility_wod(self, force_on_demand=True):
        """
        :param force_on_demand: boolean
        :return mobility_wod: MobilityWOD
        """
        self.prepare_data(5)  # we don't want to persist this RPE
        mobility_wod = self.exercise_assignment_calculator.get_mobility_wod(self.athlete_id, force_on_demand=force_on_demand)
        mobility_wod.training_session_ids = [session.id for session in self.active_training_sessions]
        self.mobility_wod_datastore.put(mobility_wod)
        self.save_session()

        return mobility_wod

    @xray_recorder.capture('logic.ActivityManager.create_responsive_recovery')
    def create_responsive_recovery(self, force_on_demand=True, responsive_recovery_id=None, training_session_id=None):
        """
        :param force_on_demand: boolean
        :param responsive_recovery_id: uuid
        :param training_session_id: uuid
        :return responsive_recovery: ResponsiveRecovery
        """
        if training_session_id is not None:
            self.active_training_sessions = [session for session in self.training_sessions if session.id == training_session_id]
        self.prepare_data(None)
        self.get_session_details()
        responsive_recovery = self.exercise_assignment_calculator.get_responsive_recovery(self.athlete_id, force_on_demand=force_on_demand)
        if responsive_recovery_id is not None:
            responsive_recovery.responsive_recovery_id = responsive_recovery_id
        responsive_recovery.training_session_id = self.active_training_sessions[0].id
        self.responsive_recovery_datastore.put(responsive_recovery)
        self.save_session()

        return responsive_recovery
