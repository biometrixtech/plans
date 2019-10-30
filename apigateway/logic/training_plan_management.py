import datetime

from fathomapi.utils.xray import xray_recorder
# import logic.exercise_mapping as exercise_mapping
#from logic.trend_processing import TrendProcessor
from logic.functional_trend_processing import TrendProcessor
from logic.soreness_processing import SorenessCalculator
from logic.alerts_processing import AlertsProcessing
from logic.trigger_processing import TriggerFactory

from logic.injury_risk_processing import InjuryRiskProcessor
from logic.functional_exercise_mapping import ExerciseAssignmentCalculator
from models.daily_plan import DailyPlan
from models.athlete_trend import AthleteTrends
from models.athlete_injury_risk import AthleteInjuryRisk
from models.functional_movement_stats import FunctionalMovementSummary
from utils import format_date, parse_datetime, parse_date
from models.body_parts import BodyPartFactory
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

    @xray_recorder.capture('logic.TrainingPlanManager.create_daily_plan')
    def create_daily_plan(self, event_date, last_updated, athlete_stats=None, force_data=False, mobilize_only=False, visualizations=True):
        self.athlete_stats = athlete_stats
        self.trigger_date_time = parse_datetime(last_updated)
        self.load_data(event_date)
        date = parse_date(event_date)

        # historic_soreness_present = False
        # if self.athlete_stats is None:
        #     historic_soreness = []
        # else:
        #     historic_soreness = copy.deepcopy([hs for hs in self.athlete_stats.historic_soreness if not hs.is_dormant_cleared()])
            # historic_soreness_present = len(historic_soreness) > 0
        historic_soreness = []

        self.soreness_list = SorenessCalculator().get_soreness_summary_from_surveys(self.readiness_surveys,
                                                                               self.post_session_surveys,
                                                                               self.trigger_date_time,
                                                                               historic_soreness,
                                                                               self.symptoms)

        # trigger_factory = TriggerFactory(parse_date(event_date), self.athlete_stats, self.soreness_list, self.training_sessions)
        # trigger_factory.load_triggers()
        # self.athlete_stats.triggers = trigger_factory.triggers
        historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)

        relative_load_level = 3
        two_days_ago = (parse_date(event_date) - datetime.timedelta(days=1)).date()

        # check workload for relative load level
        if len(athlete_stats.high_relative_load_sessions) > 0:

            max_percent = 49.9

            relevant_high_load_sessions = [s for s in athlete_stats.high_relative_load_sessions if s.date.date()
                                           >= two_days_ago]
            if len(relevant_high_load_sessions) > 0:

                for r in relevant_high_load_sessions:
                    if r.percent_of_max is not None:
                        max_percent = max(r.percent_of_max, max_percent)

            if max_percent >= 75.0:
                relative_load_level = 1
            elif max_percent >= 50.0:
                relative_load_level = 2

         # check RPE for relative load level
        # Low
        # RPE <= 1 and self.ultra_high_intensity_session
        # RPE <= 3 and not self.ultra_high_intensity_session():
        # Mod
        # RPE >= 3 and self.ultra_high_intensity_session
        # RPE >= 5 and not self.ultra_high_intensity_session():
        # High
        # RPE >= 5 and self.ultra_high_intensity_session
        # RPE >= 7 and not self.ultra_high_intensity_session():
        relevant_training_sessions = [s for s in self.daily_plan.training_sessions if s.event_date.date()
                                           >= two_days_ago]

        for r in relevant_training_sessions:
            high_intensity_session = r.ultra_high_intensity_session()
            if r.session_RPE is not None:
                if (r.session_RPE >= 5 and high_intensity_session) or (r.session_RPE >= 7 and not high_intensity_session):
                    relative_load_level = 1
                elif (r.session_RPE >= 3 and high_intensity_session) or (r.session_RPE >= 5 and not high_intensity_session):
                    relative_load_level = 2

        injury_risk_processor = InjuryRiskProcessor(date, self.soreness_list, self.daily_plan.training_sessions,
                                                    historical_injury_risk_dict, self.athlete_stats.load_stats,
                                                    self.athlete_stats.athlete_id, relative_load_level)
        aggregated_injury_risk_dict = injury_risk_processor.process(aggregate_results=True)

        consolidated_injury_risk_dict = {}

        body_part_factory = BodyPartFactory()

        for body_part_side, body_part_injury_risk in aggregated_injury_risk_dict.items():
            body_part = body_part_factory.get_body_part(body_part_side)
            if body_part not in consolidated_injury_risk_dict:
                consolidated_injury_risk_dict[body_part] = body_part_injury_risk
            else:
                consolidated_injury_risk_dict[body_part].merge(body_part_injury_risk)

        # save this for later
        #
        # detailed_dict = injury_risk_processor.injury_risk_dict
        #
        # functional_movement_stats = {}
        #
        # for body_part_side, body_part_inury_risk in detailed_dict.items():
        #     functional_movement_stats[body_part_side] = FunctionalMovementSummary()
        #
        # for body_part_side, body_part_inury_risk in detailed_dict.items():
        #     today_volume_today = detailed_dict[body_part_side].total_volume_today()
        #     if today_volume_today > 0:
        #         functional_movement_stats[body_part_side].percent_total_volume_compensating = detailed_dict[body_part_side].compensating_volume_today() / today_volume_today
        #     eccentric_volume_today = detailed_dict[body_part_side].eccentric_volume_today()
        #     if eccentric_volume_today > 0:
        #         functional_movement_stats[body_part_side].percent_eccentric_volume_compensating = detailed_dict[
        #                                                                                           body_part_side].compensating_volume_today() / eccentric_volume_today
        #     for c in detailed_dict[body_part_side].compensating_causes_volume_today:
        #         functional_movement_stats[c].caused_compensation_count += 1
        #
        # percent_total_compensating_list = sorted(functional_movement_stats.items(), key=lambda x:x[1].percent_total_volume_compensating, reverse=True)
        # percent_eccentric_compensating_list = sorted(functional_movement_stats.items(), key=lambda x:x[1].percent_eccentric_volume_compensating, reverse=True)
        # compensation_count = sorted(functional_movement_stats.items(),
        #                                              key=lambda x: x[1].caused_compensation_count,
        #                                              reverse=True)
        # compensation_count_eccentric = sorted(functional_movement_stats.items(),
        #                             key=lambda x: (x[1].caused_compensation_count, x[1].percent_eccentric_volume_compensating),
        #                             reverse=True)
        #
        # body_part_ranking = sorted(functional_movement_stats.items(),
        #                             key=lambda x: (x[0].body_part_location.value,x[0].side),
        #                             reverse=False)

        if visualizations:
                trend_processor = TrendProcessor(aggregated_injury_risk_dict, parse_date(event_date), athlete_trend_categories=self.athlete_stats.trend_categories)
                trend_processor.process_triggers()
                self.athlete_stats.trend_categories = trend_processor.athlete_trend_categories

            # calc = exercise_mapping.ExerciseAssignmentCalculator(trigger_factory, self.exercise_library_datastore,
            #                                                      self.completed_exercise_datastore,
            #                                                      self.training_sessions, self.soreness_list,
            #                                                      parse_date(event_date), historic_soreness)

        calc = ExerciseAssignmentCalculator(consolidated_injury_risk_dict, self.exercise_library_datastore, self.completed_exercise_datastore,
                                            date, relative_load_level)


        # new modalities
        if not self.daily_plan.train_later:
            if mobilize_only:
                # if any completed post_active rest exists, preserve it
                for post_active_rest in self.daily_plan.post_active_rest:
                    if post_active_rest.completed:
                        self.daily_plan.completed_post_active_rest.append(post_active_rest)
                # create a new post active rest
                self.daily_plan.post_active_rest = calc.get_post_active_rest(force_data)
            else:
                # if any completed post-training modalities exist, preserve them
                # for cool_down in self.daily_plan.cool_down:
                #     if cool_down.completed:
                #         self.daily_plan.completed_cool_down.append(cool_down)
                for post_active_rest in self.daily_plan.post_active_rest:
                    if post_active_rest.completed:
                        self.daily_plan.completed_post_active_rest.append(post_active_rest)
                # if self.daily_plan.ice is not None and self.daily_plan.ice.completed:
                #     self.daily_plan.completed_ice.append(self.daily_plan.ice)
                # if self.daily_plan.cold_water_immersion is not None and self.daily_plan.cold_water_immersion.completed:
                    # self.daily_plan.completed_cold_water_immersion.append(self.daily_plan.cold_water_immersion)

                # make pre-training modalities inactive
                # if self.daily_plan.heat is not None:
                #     self.daily_plan.heat.active = False
                for pre_active_rest in self.daily_plan.pre_active_rest:
                    pre_active_rest.active = False
                # for warm_up in self.daily_plan.warm_up:
                #     warm_up.active = False

                # create new post-training modalities
                # self.daily_plan.cool_down = calc.get_cool_down()
                self.daily_plan.post_active_rest = calc.get_post_active_rest(force_data)
                # self.daily_plan.ice = calc.get_ice()
                # self.daily_plan.cold_water_immersion = calc.get_cold_water_immersion()
                # if self.daily_plan.cold_water_immersion is not None:
                #     self.daily_plan.ice = calc.adjust_ice_session(self.daily_plan.ice, self.daily_plan.cold_water_immersion)
        else:
            if mobilize_only:
                # if any completed pre active rest is present, preserve it
                for pre_active_rest in self.daily_plan.pre_active_rest:
                    if pre_active_rest.completed:
                        self.daily_plan.completed_pre_active_rest.append(pre_active_rest)
                # create new pre active rest
                self.daily_plan.pre_active_rest = calc.get_pre_active_rest(force_data)
            else:
                # if any post-training modalities are present and complete, preserve the completed ones
                # self.daily_plan.cool_down = self.preserve_completed_modality(self.daily_plan.cool_down)
                self.daily_plan.post_active_rest = self.preserve_completed_modality(self.daily_plan.post_active_rest)
                # self.daily_plan.ice = self.preserve_completed_modality(self.daily_plan.ice)
                # self.daily_plan.cold_water_immersion = self.preserve_completed_modality(self.daily_plan.cold_water_immersion)
                # if any completed pre-training modalities exist, preserve them
                # if self.daily_plan.heat is not None and self.daily_plan.heat.completed:
                #     self.daily_plan.completed_heat.append(self.daily_plan.heat)
                for pre_active_rest in self.daily_plan.pre_active_rest:
                    if pre_active_rest.completed:
                        self.daily_plan.completed_pre_active_rest.append(pre_active_rest)
                # for warm_up in self.daily_plan.warm_up:
                #     if warm_up.completed:
                #         self.daily_plan.completed_warm_up.append(warm_up)
                # create new pre-training modalities
                # self.daily_plan.heat = calc.get_heat()
                self.daily_plan.pre_active_rest = calc.get_pre_active_rest(force_data)
                # self.daily_plan.warm_up = calc.get_warm_up(athlete_stats, soreness_list, parse_date(event_date))

        self.daily_plan.last_updated = last_updated
        # alerts = self.daily_plan.get_alerts()
        # alerts.extend(calc.generate_alerts())
        # alerts_processing = AlertsProcessing(daily_plan=self.daily_plan,
        #                                      athlete_stats=self.athlete_stats,
        #                                      trigger_date_time=self.trigger_date_time,)
        # alerts_processing.aggregate_alerts(alerts=alerts)
        if visualizations:
            self.daily_plan.trends = AthleteTrends()
            self.daily_plan.trends.trend_categories = trend_processor.athlete_trend_categories
            self.daily_plan.trends.dashboard.trend_categories = trend_processor.dashboard_categories
            self.daily_plan.trends.add_trend_data(self.athlete_stats)

        self.daily_plan_datastore.put(self.daily_plan)
        self.athlete_stats_datastore.put(self.athlete_stats)
        athlete_injury_risk = AthleteInjuryRisk(self.athlete_id)
        athlete_injury_risk.items = injury_risk_processor.injury_risk_dict

        self.injury_risk_datastore.put(athlete_injury_risk)

        return self.daily_plan
