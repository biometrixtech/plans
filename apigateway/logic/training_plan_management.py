# import datetime

from fathomapi.utils.xray import xray_recorder
from logic.functional_trend_processing import TrendProcessor
from logic.soreness_processing import SorenessCalculator
# from logic.trigger_processing import TriggerFactory

from logic.injury_risk_processing import InjuryRiskProcessor
from logic.exercise_assignment import ExerciseAssignment
from models.daily_plan import DailyPlan
from models.athlete_trend import AthleteTrends
from models.athlete_injury_risk import AthleteInjuryRisk
# from models.functional_movement_stats import FunctionalMovementSummary
from models.functional_movement_modalities import ModalityType, CoolDown, FunctionalStrength
from utils import format_date, parse_datetime, parse_date, format_datetime
# from models.body_parts import BodyPartFactory
import copy


class TrainingPlanManager(object):

    def __init__(self, athlete_id, datastore_collection):
        self.athlete_id = athlete_id
        self.daily_plan_datastore = datastore_collection.daily_plan_datastore
        self.exercise_library_datastore = datastore_collection.exercise_datastore
        self.athlete_stats_datastore = datastore_collection.athlete_stats_datastore
        self.completed_exercise_datastore = datastore_collection.completed_exercise_datastore
        self.injury_risk_datastore = datastore_collection.injury_risk_datastore
        self.trigger_date_time = None
        self.daily_plan = None
        self.readiness_surveys = []
        self.post_session_surveys = []
        self.athlete_stats = None
        self.training_sessions = []
        self.longitudinal_alerts = []
        self.soreness_list = []
        self.symptoms = []
        self.active_training_sessions = []
        self.exercise_assignment = None

    def load_data(self, event_date):
        daily_plans = self.daily_plan_datastore.get(self.athlete_id, event_date, event_date)
        plan_today = [plan for plan in daily_plans if plan.event_date == event_date]

        if len(plan_today) == 0:
            self.daily_plan = DailyPlan(event_date)
            self.daily_plan.user_id = self.athlete_id
        else:
            self.daily_plan = copy.deepcopy(plan_today[0])
        self.readiness_surveys = [plan.daily_readiness_survey for plan in daily_plans if plan.daily_readiness_survey is not None]
        for plan in daily_plans:
            self.post_session_surveys.extend([ts.post_session_survey for ts in plan.training_sessions if ts is not None and ts.post_session_survey is not None])

        if self.athlete_stats is None:
            self.athlete_stats = self.athlete_stats_datastore.get(self.athlete_id)

        for c in plan_today:
            self.training_sessions.extend(c.training_sessions)
            self.symptoms.extend(c.symptoms)

        self.training_sessions.sort(key=lambda x: x.completed_date_time, reverse=True)  #now we can always grab the 0 element

        #self.active_training_sessions = [session for session in self.training_sessions]

    @staticmethod
    def preserve_completed_modality(modalities):
        if isinstance(modalities, list):
            for modality in modalities:
                if modality.completed:
                    modality.active = False
            return [modality for modality in modalities if modality.completed]
        else:
            if modalities is not None:
                if not modalities.completed:
                    modalities = None
                else:
                    modalities.active = False
            return modalities

    def move_completed_modalities(self):
        # copy over completed ones
        for modality in self.daily_plan.modalities:
            if modality.completed:
                self.daily_plan.completed_modalities.append(modality)
        # only retain not-completed
        self.daily_plan.modalities = [m for m in self.daily_plan.modalities if not m.completed]

    def set_active_sessions(self, active_sessions):

        self.active_training_sessions = active_sessions
        self.set_exercise_assignment_session_info()

    def set_exercise_assignment_session_info(self):

        self.exercise_assignment.sport_cardio_plyometrics = self.check_cardio_sport()
        self.exercise_assignment.sport_body_parts = self.get_sport_body_parts()
        self.exercise_assignment.high_intensity_session = self.is_high_intensity_session()

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

    @xray_recorder.capture('logic.TrainingPlanManager.create_daily_plan')
    def create_daily_plan(self, event_date, last_updated, athlete_stats=None, force_data=False, mobilize_only=False, visualizations=True, force_on_demand=False, log_symptoms=False):
        self.athlete_stats = athlete_stats
        self.trigger_date_time = parse_datetime(last_updated)
        self.load_data(event_date)

        date = parse_date(event_date)

        historic_soreness = []

        self.soreness_list = SorenessCalculator().get_soreness_summary_from_surveys(self.readiness_surveys,
                                                                                    self.post_session_surveys,
                                                                                    self.trigger_date_time,
                                                                                    historic_soreness,
                                                                                    self.symptoms)

        historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)

        injury_risk_processor = InjuryRiskProcessor(date, self.soreness_list, self.daily_plan.training_sessions,
                                                    historical_injury_risk_dict, self.athlete_stats,
                                                    self.athlete_stats.athlete_id)
        aggregated_injury_risk_dict = injury_risk_processor.process(aggregate_for_viz=True)

        consolidated_injury_risk_dict = injury_risk_processor.get_consolidated_dict()

        if visualizations:
            trend_processor = TrendProcessor(aggregated_injury_risk_dict, parse_date(event_date),
                                             athlete_trend_categories=self.athlete_stats.trend_categories,
                                             athlete_insight_categories=self.athlete_stats.insight_categories)
            trend_processor.process_triggers()
            self.athlete_stats.trend_categories = trend_processor.athlete_trend_categories
            self.athlete_stats.insight_categories = trend_processor.athlete_insight_categories

        modality_date_time = self.trigger_date_time or date
        self.exercise_assignment = ExerciseAssignment(consolidated_injury_risk_dict, self.exercise_library_datastore,
                                                      self.completed_exercise_datastore,
                                                      modality_date_time, injury_risk_processor.relative_load_level)

        # new modalities
        self.move_completed_modalities()

        if not log_symptoms:
            if not self.daily_plan.train_later:
                if len(self.daily_plan.training_sessions) > 0:
                    self.set_active_sessions([self.training_sessions[0]])

                    responsive_recovery, ice, cold_water_immersion = self.exercise_assignment.get_responsive_recovery_modality(self.training_sessions[0].id, force_data, force_on_demand)

                    if len(responsive_recovery) > 0:
                        # get rid of both possible active recovery and active rest modalities
                        # and go with whatever is responsive to last session
                        self.daily_plan.modalities = [m for m in self.daily_plan.modalities if
                                                      m.type.value not in [ModalityType.active_recovery.value,
                                                                           ModalityType.post_active_rest.value]]

                    self.daily_plan.ice = ice
                    self.daily_plan.cold_water_immersion = cold_water_immersion
                    self.daily_plan.modalities.extend(responsive_recovery)

                else:
                    self.daily_plan.modalities = [m for m in self.daily_plan.modalities if m.type.value != ModalityType.post_active_rest.value]
                    active_rests = self.exercise_assignment.get_active_rest(force_data, force_on_demand)
                    self.daily_plan.modalities.extend(active_rests)
            else:

                if len(self.daily_plan.training_sessions) > 0:
                    self.set_active_sessions([self.training_sessions[0]])

                    responsive_recovery = self.exercise_assignment.get_responsive_recovery_modality(self.training_sessions[0].id, force_data, force_on_demand, ice_cwi=False)[0]

                    if len(responsive_recovery) > 0:
                        # get rid of both possible active recovery and active rest modalities
                        # and go with whatever is responsive to last session
                        self.daily_plan.modalities = [m for m in self.daily_plan.modalities if
                                                      m.type.value not in [ModalityType.active_recovery.value,
                                                                           ModalityType.post_active_rest.value]]

                    # don't assign ice or cwi if they are training later
                    self.daily_plan.ice = None
                    self.daily_plan.cold_water_immersion = None
                    self.daily_plan.modalities.extend(responsive_recovery)

                else:

                    # remove existing movement preps
                    self.daily_plan.modalities = [m for m in self.daily_plan.modalities if m.type.value != ModalityType.movement_integration_prep.value]
                    movement_preps = self.exercise_assignment.get_movement_integration_prep(force_data, force_on_demand)
                    self.daily_plan.modalities.extend(movement_preps)
        else:

            # replace any existing uncompleted active rests so we can add a new, updated one
            self.daily_plan.modalities = [m for m in self.daily_plan.modalities if
                                          m.type.value != ModalityType.post_active_rest.value]
            active_rests = self.exercise_assignment.get_active_rest(force_data, force_on_demand)
            self.daily_plan.modalities.extend(active_rests)

            # update any existing movement preps
            movement_preps = [m for m in self.daily_plan.modalities if
                                          m.type.value == ModalityType.movement_integration_prep.value]

            if len(movement_preps) > 0:
                # remove existing movement preps
                self.daily_plan.modalities = [m for m in self.daily_plan.modalities if
                                              m.type.value != ModalityType.movement_integration_prep.value]
                movement_preps = self.exercise_assignment.get_movement_integration_prep(force_data, force_on_demand)
                self.daily_plan.modalities.extend(movement_preps)

            # update any active recovery in place:
            active_recoveries = [m for m in self.daily_plan.modalities if
                                 m.type.value == ModalityType.active_recovery.value]

            if len(active_recoveries) > 0:
                source_session_id = active_recoveries[0].source_training_session_id

                source_sessions = [t for t in self.training_sessions if t.id == source_session_id]

                if len(source_sessions) > 0:
                    self.set_active_sessions(source_sessions[0])

                    responsive_recovery = self.exercise_assignment.get_responsive_recovery_modality(source_session_id, force_data, force_on_demand,
                                                                                                    ice_cwi=False)[0]

                    if len(responsive_recovery) > 0:
                        if responsive_recovery[0].modality_type == ModalityType.active_recovery.value:
                            self.daily_plan.modalities = [m for m in self.daily_plan.modalities if
                                                          m.type.value != ModalityType.active_recovery.value]

                    self.daily_plan.modalities.append(responsive_recovery[0])

        self.daily_plan.last_updated = last_updated
        self.daily_plan.define_available_modalities()
        if visualizations:
            self.daily_plan.trends = AthleteTrends()
            self.daily_plan.trends.trend_categories = trend_processor.athlete_trend_categories
            self.daily_plan.trends.insight_categories = trend_processor.athlete_insight_categories
            self.daily_plan.trends.dashboard.trend_categories = trend_processor.dashboard_categories
            self.daily_plan.trends.add_trend_data(self.athlete_stats)

        self.daily_plan_datastore.put(self.daily_plan)
        self.athlete_stats_datastore.put(self.athlete_stats)
        athlete_injury_risk = AthleteInjuryRisk(self.athlete_id)
        athlete_injury_risk.items = injury_risk_processor.injury_risk_dict

        self.injury_risk_datastore.put(athlete_injury_risk)

        return self.daily_plan

    def add_modality(self, event_date, modality_type, athlete_stats=None, force_data=False):
        self.athlete_stats = athlete_stats
        self.load_data(format_date(event_date))
        historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)
        injury_risk_processor = InjuryRiskProcessor(event_date, [], [],
                                                    historical_injury_risk_dict, self.athlete_stats,
                                                    self.athlete_id)
        consolidated_injury_risk_dict = injury_risk_processor.get_consolidated_dict()
        injury_risk_processor.set_relative_load_level(event_date.date())
        exercise_assignment = ExerciseAssignment(consolidated_injury_risk_dict, self.exercise_library_datastore,
                                                 self.completed_exercise_datastore,
                                                 event_date, injury_risk_processor.relative_load_level)

        self.move_completed_modalities()

        modality_type = ModalityType(modality_type)
        if modality_type == ModalityType.pre_active_rest or modality_type == ModalityType.post_active_rest:
            new_modality = exercise_assignment.get_active_rest(force_data)
        # elif modality_type == ModalityType.warm_up:
        #     new_modality = calc.get_warm_up()
        elif modality_type == ModalityType.cool_down or modality_type == ModalityType.active_recovery:
            self.set_active_sessions([self.training_sessions[0]])
            new_modality = exercise_assignment.get_responsive_recovery_modality(self.training_sessions[0].id, force_data, ice_cwi=False)[0]
        # elif modality_type == ModalityType.functional_strength:
        #     new_modality = calc.get_functional_strength()
        elif modality_type == ModalityType.movement_integration_prep:
            new_modality = exercise_assignment.get_movement_integration_prep(force_data)
        else:
            new_modality = None

        if new_modality is not None:
            self.daily_plan.modalities.extend(new_modality)
        self.daily_plan.last_updated = format_datetime(event_date)
        self.daily_plan.define_available_modalities()

        self.daily_plan_datastore.put(self.daily_plan)

        return self.daily_plan
