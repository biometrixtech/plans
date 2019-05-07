import datetime

from fathomapi.utils.xray import xray_recorder
import logic.exercise_mapping as exercise_mapping
from logic.soreness_processing import SorenessCalculator
from models.daily_plan import DailyPlan
from utils import format_date, parse_datetime, parse_date


class TrainingPlanManager(object):

    def __init__(self, athlete_id, datastore_collection):
        self.athlete_id = athlete_id
        self.daily_plan_datastore = datastore_collection.daily_plan_datastore
        self.exercise_library_datastore = datastore_collection.exercise_datastore
        self.athlete_stats_datastore = datastore_collection.athlete_stats_datastore
        self.completed_exercise_datastore = datastore_collection.completed_exercise_datastore
        self.trigger_date_time = None
        self.daily_plan = None
        self.readiness_surveys = []
        self.post_session_surveys = []
        self.athlete_stats = None

    # def post_session_surveys_today(self):
    #     for ps_survey in self.post_session_surveys:
    #         if format_date(ps_survey.event_date) == format_date(self.trigger_date_time):
    #             return True
    #     return False
    #
    # def show_post_recovery(self, surveys_today):
    #     if surveys_today and not self.daily_plan.session_from_readiness:
    #         return True
    #     else:
    #         if self.daily_plan.train_later:
    #             return False
    #         else:
    #             return True

    def load_data(self, event_date):
        daily_plans = self.daily_plan_datastore.get(self.athlete_id, format_date(parse_date(event_date) - datetime.timedelta(days=1)), event_date)
        plan_today = [plan for plan in daily_plans if plan.event_date == event_date]
        if len(plan_today) == 0:
            self.daily_plan = DailyPlan(event_date)
            self.daily_plan.user_id = self.athlete_id
        else:
            self.daily_plan = plan_today[0]
        self.readiness_surveys = [plan.daily_readiness_survey for plan in daily_plans if plan.daily_readiness_survey is not None]
        for plan in daily_plans:
            self.post_session_surveys.extend([ts.post_session_survey for ts in plan.training_sessions if ts is not None and ts.post_session_survey is not None])

        if self.athlete_stats is None:
            self.athlete_stats = self.athlete_stats_datastore.get(self.athlete_id)

    @staticmethod
    def preserve_completed_modality(modalities):
        if isinstance(modalities, list):
            for modality in modalities:
                if not modality.completed:
                    modality.delete = True
                else:
                    modality.active = False
            return [modality for modality in modalities if not modality.delete]
        else:
            if modalities is not None:
                if not modalities.completed:
                    modalities = None
                else:
                    modalities.active = False
            return modalities

    @xray_recorder.capture('logic.TrainingPlanManager.create_daily_plan')
    def create_daily_plan(self, event_date, last_updated, target_minutes=15, athlete_stats=None):
        self.athlete_stats = athlete_stats
        self.trigger_date_time = parse_datetime(last_updated)
        self.load_data(event_date)

        historic_soreness_present = False
        if self.athlete_stats is None:
            historic_soreness = []
        else:
            historic_soreness = [hs for hs in self.athlete_stats.historic_soreness if not hs.is_dormant_cleared()]
            historic_soreness_present = len(historic_soreness) > 0
            # self.is_functional_strength_eligible()

        soreness_list = SorenessCalculator().get_soreness_summary_from_surveys(self.readiness_surveys,
                                                                               self.post_session_surveys,
                                                                               self.trigger_date_time,
                                                                               historic_soreness)
        # show_post_recovery = self.show_post_recovery(self.post_session_surveys_today())
        # self.add_recovery_times(show_post_recovery)

        calc = exercise_mapping.ExerciseAssignmentCalculator(self.athlete_id, self.exercise_library_datastore,
                                                             self.completed_exercise_datastore,
                                                             historic_soreness_present)

        # soreness_values = [s.severity for s in soreness_list if s.severity is not None and s.daily]

        # new modalities
        if not self.daily_plan.train_later:
            # if any completed post-training modalities exist, preserve them
            for cool_down in self.daily_plan.cool_down:
                if cool_down.completed:
                    self.daily_plan.completed_cool_down.append(cool_down)
            for post_active_rest in self.daily_plan.post_active_rest:
                if post_active_rest.completed:
                    self.daily_plan.completed_post_active_rest.append(post_active_rest)
            if self.daily_plan.ice is not None and self.daily_plan.ice.completed:
                self.daily_plan.completed_ice.append(self.daily_plan.ice)
            if self.daily_plan.cold_water_immersion is not None and self.daily_plan.cold_water_immersion.completed:
                self.daily_plan.completed_cold_water_immersion.append(self.daily_plan.cold_water_immersion)
            # make pre-training modalities inactive
            if self.daily_plan.heat is not None:
                self.daily_plan.heat.active = False
            for pre_active_rest in self.daily_plan.pre_active_rest:
                pre_active_rest.active = False
            for warm_up in self.daily_plan.warm_up:
                warm_up.active = False
            # create new post-training modalitiesathlete_stats, soreness_list, event_date_time
            self.daily_plan.cool_down = calc.get_cool_down(athlete_stats, soreness_list, parse_date(event_date))
            self.daily_plan.post_active_rest = calc.get_post_active_rest(athlete_stats, soreness_list, parse_date(event_date))
            self.daily_plan.ice = calc.get_ice(soreness_list, parse_date(event_date))
            self.daily_plan.cold_water_immersion = calc.get_cold_water_immersion(soreness_list, parse_date(event_date))
            if self.daily_plan.cold_water_immersion is not None:
                self.daily_plan.ice = calc.adjust_ice_session(self.daily_plan.ice, self.daily_plan.cold_water_immersion)
        else:
            # if any post-training modalities are present and complete, preserve the completed ones
            self.daily_plan.cool_down = self.preserve_completed_modality(self.daily_plan.cool_down)
            self.daily_plan.post_active_rest = self.preserve_completed_modality(self.daily_plan.post_active_rest)
            self.daily_plan.ice = self.preserve_completed_modality(self.daily_plan.ice)
            self.daily_plan.cold_water_immersion = self.preserve_completed_modality(self.daily_plan.cold_water_immersion)
            # if any completed pre-training modalities exist, preserve them
            if self.daily_plan.heat is not None and self.daily_plan.heat.completed:
                self.daily_plan.completed_heat.append(heat)
            for pre_active_rest in self.daily_plan.pre_active_rest:
                if pre_active_rest.completed:
                    self.daily_plan.completed_pre_active_rest.append(pre_active_rest)
            for warm_up in self.daily_plan.warm_up:
                if warm_up.completed:
                    self.daily_plan.completed_warm_up.append(warm_up)
            # create new pre-training modalities
            self.daily_plan.heat = calc.get_heat(soreness_list, parse_date(event_date))
            self.daily_plan.pre_active_rest = calc.get_pre_active_rest(athlete_stats, soreness_list, parse_date(event_date))
            # self.daily_plan.warm_up = calc.get_warm_up(athlete_stats, soreness_list, parse_date(event_date))
        #
        # if soreness_values is not None and len(soreness_values) > 0:
        #    max_soreness = max(soreness_values)
        # else:
        #    max_soreness = 0
        #
        # if self.daily_plan.functional_strength_session is None:
        #    self.populate_functional_strength(True)
        #
        # functional_strength_active = (self.daily_plan.functional_strength_session is not None)
        #
        # if not show_post_recovery:
        #    if self.daily_plan.pre_recovery is not None and not self.daily_plan.pre_recovery.completed:
        #         self.daily_plan.pre_recovery.set_exercise_target_minutes(soreness_list, target_minutes, max_soreness,
        #                                                                 historic_soreness_present,
        #                                                                  functional_strength_active,
        #                                                                 is_active_prep=True)
        #         am_exercise_assignments = calc.create_exercise_assignments(self.daily_plan.pre_recovery, soreness_list,
        #                                                                   self.trigger_date_time, target_minutes)
        #         self.daily_plan.pre_recovery.update_from_exercise_assignments(am_exercise_assignments)
        #        self.daily_plan.pre_recovery.display_exercises = True
        #    else:
        #        self.daily_plan.pre_recovery.display_exercises = False
        #
        # if show_post_recovery:
        #    if self.daily_plan.post_recovery is not None and not self.daily_plan.post_recovery.completed:
        #         self.daily_plan.post_recovery.set_exercise_target_minutes(soreness_list, target_minutes, max_soreness,
        #                                                                  historic_soreness_present,
        #                                                                   functional_strength_active,
        #                                                                  is_active_prep=False)
        #         pm_exercise_assignments = calc.create_exercise_assignments(self.daily_plan.post_recovery, soreness_list,
        #                                                                   self.trigger_date_time, target_minutes)
        #         self.daily_plan.post_recovery.update_from_exercise_assignments(pm_exercise_assignments)
        #         if not self.daily_plan.functional_strength_completed and (pm_exercise_assignments is None or pm_exercise_assignments.duration_minutes() == 0):
        #            self.daily_plan.functional_strength_session = None
        #            self.daily_plan.functional_strength_eligible = False
        #
        #        self.daily_plan.post_recovery.display_exercises = True
        #    else:
        #        self.daily_plan.post_recovery.display_exercises = False

        self.daily_plan.last_updated = last_updated

        self.daily_plan_datastore.put(self.daily_plan)

        return self.daily_plan

    '''deprecated
    def populate_functional_strength(self, wants_functional_strength):

        if self.athlete_stats is not None:
            self.daily_plan.functional_strength_eligible = self.athlete_stats.functional_strength_eligible

            if self.daily_plan.functional_strength_eligible and wants_functional_strength:
                if not self.daily_plan.functional_strength_completed:
                    fs_mapping = FSProgramGenerator(self.exercise_library_datastore)
                    self.daily_plan.functional_strength_session = fs_mapping.getFunctionalStrengthForSportPosition(
                        self.athlete_stats.current_sport_name,
                        self.athlete_stats.current_position)
    '''

    # def add_recovery_times(self, show_post_recovery):
    #
    #     if not show_post_recovery:
    #         if self.daily_plan.pre_recovery is None:
    #             self.daily_plan.pre_recovery = session.RecoverySession()
    #             self.daily_plan.pre_recovery.display_exercises = True
    #         self.daily_plan.post_recovery.display_exercises = False
    #     else:
    #         self.daily_plan.pre_recovery.display_exercises = False
    #         if self.daily_plan.post_recovery is not None and self.daily_plan.post_recovery.completed:
    #             self.daily_plan.completed_post_recovery_sessions.append(self.daily_plan.post_recovery)
    #         self.daily_plan.post_recovery = session.RecoverySession()
    #         self.daily_plan.post_recovery.display_exercises = True

    '''deprecated
    def is_functional_strength_eligible(self):
        if (self.athlete_stats.functional_strength_eligible and
            not self.athlete_stats.severe_pain_soreness_today() and  # these are updated from surveys but update doesn't make it to stats until after plan is created
            (self.athlete_stats.next_functional_strength_eligible_date is None or
             parse_datetime(self.athlete_stats.next_functional_strength_eligible_date) < self.trigger_date_time)):  # need to check if 24 hours have passed since last completed
            self.athlete_stats.functional_strength_eligible = True
        else:
            self.athlete_stats.functional_strength_eligible = False
    '''