import datetime

from fathomapi.utils.xray import xray_recorder
import logic.exercise_mapping as exercise_mapping
from logic.soreness_processing import SorenessCalculator
from logic.functional_strength_mapping import FSProgramGenerator
import models.session as session
from models.daily_plan import DailyPlan
from models.soreness import HistoricSorenessStatus
from models.post_session_survey import PostSessionSurvey
from utils import format_datetime, format_date, parse_datetime, parse_date


class TrainingPlanManager(object):

    def __init__(self, athlete_id, datastore_collection):
        self.athlete_id = athlete_id
        self.post_session_survey_datastore = datastore_collection.post_session_survey_datastore
        self.daily_plan_datastore = datastore_collection.daily_plan_datastore
        self.exercise_library_datastore = datastore_collection.exercise_datastore
        self.athlete_stats_datastore = datastore_collection.athlete_stats_datastore
        self.completed_exercise_datastore = datastore_collection.completed_exercise_datastore

    @staticmethod
    def post_session_surveys_today(post_session_surveys, trigger_date):

        try:
            todays_date_time = datetime.datetime.strptime(trigger_date, '%Y-%m-%d')
        except ValueError:
            todays_date_time = datetime.datetime.strptime(trigger_date, '%Y-%m-%dT%H:%M:%SZ')

        todays_date = todays_date_time.strftime("%Y-%m-%d")

        for p in post_session_surveys:
            event_date_time = datetime.datetime.strptime(p.event_date, "%Y-%m-%d")
            if event_date_time.strftime("%Y-%m-%d") == todays_date:
                return True

        return False

    @staticmethod
    def show_post_recovery(post_surveys_today, daily_plan):
        if post_surveys_today and not daily_plan.session_from_readiness:
            return True
        else:
            if daily_plan.sessions_planned_readiness:
                return False
            else:
                return True

    @xray_recorder.capture('logic.TrainingPlanManager.create_daily_plan')
    def create_daily_plan(self, event_date=None, target_minutes=15, last_updated=None, athlete_stats=None):

        daily_plans = self.daily_plan_datastore.get(self.athlete_id, format_date(parse_date(event_date) - datetime.timedelta(days=1)), event_date)
        daily_plan = [plan for plan in daily_plans if plan.event_date == event_date]
        if len(daily_plan) == 0:
            daily_plan = DailyPlan(event_date)
        else:
            daily_plan = daily_plan[0]
        readiness_surveys = [plan.daily_readiness_survey for plan in daily_plans]
        readiness_surveys = sorted(readiness_surveys, key=lambda k: k.event_date, reverse=True)
        last_daily_readiness_survey = readiness_surveys[0]
        post_session_surveys = []
        for plan in daily_plans:
            post_surveys = \
                [PostSessionSurvey.post_session_survey_from_training_session(ts.post_session_survey, self.athlete_id, ts.id, ts.session_type().value, plan.event_date)
                 for ts in plan.training_sessions if ts is not None]
            post_session_surveys.extend([s for s in post_surveys if s is not None])

        if last_updated is None:
            last_updated = format_datetime(datetime.datetime.utcnow())
        trigger_date_time = last_daily_readiness_survey.get_event_date()
        if athlete_stats is None:
            athlete_stats = self.athlete_stats_datastore.get(self.athlete_id)

        survey_event_dates = [s.get_event_date() for s in post_session_surveys if s is not None]

        if survey_event_dates is not None and len(survey_event_dates) > 0:
            trigger_date_time = max(trigger_date_time, max(survey_event_dates))

        historic_soreness_present = False
        if athlete_stats is None:
            historic_soreness = []
        else:
            historic_soreness = [hs for hs in athlete_stats.historic_soreness if hs.historic_soreness_status is not None and
                                 hs.historic_soreness_status is not HistoricSorenessStatus.dormant_cleared and
                                 hs.historic_soreness_status is not HistoricSorenessStatus.almost_persistent_soreness and
                                 hs.historic_soreness_status is not HistoricSorenessStatus.almost_persistent_pain]
            historic_soreness_present = len(historic_soreness) > 0
            is_functional_strength_eligible(athlete_stats, last_updated)

        soreness_list = SorenessCalculator().get_soreness_summary_from_surveys(readiness_surveys,
                                                                               post_session_surveys,
                                                                               trigger_date_time,
                                                                               historic_soreness)

        post_surveys_today = self.post_session_surveys_today(post_session_surveys, event_date)

        show_post_recovery = self.show_post_recovery(post_surveys_today, daily_plan)
        daily_plan.user_id = self.athlete_id
        daily_plan.daily_readiness_survey = last_daily_readiness_survey  # .get_event_date().strftime('%Y-%m-%d')

        daily_plan = self.add_recovery_times(show_post_recovery, daily_plan)

        calc = exercise_mapping.ExerciseAssignmentCalculator(self.athlete_id, self.exercise_library_datastore,
                                                             self.completed_exercise_datastore,
                                                             historic_soreness_present)

        soreness_values = [s.severity for s in soreness_list if s.severity is not None and s.daily]

        if soreness_values is not None and len(soreness_values) > 0:
            max_soreness = max(soreness_values)
        else:
            max_soreness = 0

        if daily_plan.functional_strength_session is None:
            daily_plan = self.populate_functional_strength(daily_plan, athlete_stats, True)

        functional_strength_active = (daily_plan.functional_strength_session is not None)

        if not show_post_recovery:
            if daily_plan.pre_recovery is not None and not daily_plan.pre_recovery.completed:
                daily_plan.pre_recovery.set_exercise_target_minutes(soreness_list, target_minutes, max_soreness,
                                                                    historic_soreness_present,
                                                                    functional_strength_active,
                                                                    is_active_prep=True)
                am_exercise_assignments = calc.create_exercise_assignments(daily_plan.pre_recovery, soreness_list,
                                                                           trigger_date_time, target_minutes)
                daily_plan.pre_recovery.update_from_exercise_assignments(am_exercise_assignments)
                daily_plan.pre_recovery.display_exercises = True
            else:
                daily_plan.pre_recovery.display_exercises = False

        if show_post_recovery:
            if daily_plan.post_recovery is not None and not daily_plan.post_recovery.completed:
                daily_plan.post_recovery.set_exercise_target_minutes(soreness_list, target_minutes, max_soreness,
                                                                     historic_soreness_present,
                                                                     functional_strength_active,
                                                                     is_active_prep=False)
                pm_exercise_assignments = calc.create_exercise_assignments(daily_plan.post_recovery, soreness_list,
                                                                           trigger_date_time, target_minutes)
                daily_plan.post_recovery.update_from_exercise_assignments(pm_exercise_assignments)
                if not daily_plan.functional_strength_completed and (pm_exercise_assignments is None or pm_exercise_assignments.duration_minutes() == 0):
                    daily_plan.functional_strength_session = None
                    daily_plan.functional_strength_eligible = False

                daily_plan.post_recovery.display_exercises = True
            else:
                daily_plan.post_recovery.display_exercises = False

        daily_plan.last_updated = last_updated

        self.daily_plan_datastore.put(daily_plan)

        return daily_plan

    def populate_functional_strength(self, daily_plan, athlete_stats, wants_functional_strength):

        if athlete_stats is not None:
            daily_plan.functional_strength_eligible = athlete_stats.functional_strength_eligible

            if daily_plan.functional_strength_eligible and wants_functional_strength:
                if not daily_plan.functional_strength_completed:
                    fs_mapping = FSProgramGenerator(self.exercise_library_datastore)
                    daily_plan.functional_strength_session = fs_mapping.getFunctionalStrengthForSportPosition(
                        athlete_stats.current_sport_name,
                        athlete_stats.current_position)

        return daily_plan

    # def create_training_cycle(self, athlete_schedule, athlete_injury_history):
    #     # schedule_manager = schedule.ScheduleManager()
    #     # athlete_schedule = schedule_manager.get_typical_schedule(athlete_id)
    #     training_cycle = training.TrainingCycle()
    #     # TODO set start and end dates of training_cycle
    #     for s in athlete_schedule.sessions:
    #         new_session = s.create()
    #         training_cycle.sessions.extend(new_session)
    #
    #     # add recovery sessions based on athlete status and history
    #     training_cycle.recovery_modalities = self.get_recovery_sessions(athlete_injury_history, training_cycle)

    @staticmethod
    def add_recovery_times(show_post_recovery, daily_plan):

        if not show_post_recovery:
            if daily_plan.pre_recovery is None:
                daily_plan.pre_recovery = session.RecoverySession()
                daily_plan.pre_recovery.display_exercises = True
            daily_plan.post_recovery.display_exercises = False
        else:
            daily_plan.pre_recovery.display_exercises = False
            if daily_plan.post_recovery is not None and daily_plan.post_recovery.completed:
                daily_plan.completed_post_recovery_sessions.append(daily_plan.post_recovery)
            daily_plan.post_recovery = session.RecoverySession()
            daily_plan.post_recovery.display_exercises = True
        return daily_plan

    # @staticmethod
    # def get_recovery_start_end_times(trigger_date_time, recovery_number):
    #
    #     start_time = None
    #     end_time = None
    #
    #     if recovery_number == 0:
    #
    #         if trigger_date_time.hour < 12:
    #
    #             start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, trigger_date_time.day,
    #                                            0, 0, 0)
    #             end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, trigger_date_time.day,
    #                                          12, 0, 0)
    #         if trigger_date_time.hour >= 12:
    #             start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
    #                                            trigger_date_time.day,
    #                                            12, 0, 0)
    #             next_date = trigger_date_time + datetime.timedelta(days=1)
    #             end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
    #                                          next_date.day,
    #                                          0, 0, 0)
    #
    #     elif recovery_number == 1:
    #
    #         if trigger_date_time.hour < 12:
    #             start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
    #                                            trigger_date_time.day,
    #                                            12, 0, 0)
    #             next_date = trigger_date_time + datetime.timedelta(days=1)
    #             end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
    #                                          next_date.day,
    #                                          0, 0, 0)
    #         if trigger_date_time.hour >= 12:
    #             next_date = trigger_date_time + datetime.timedelta(days=1)
    #             start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
    #                                            0, 0, 0)
    #             end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
    #                                          12, 0, 0)
    #
    #     elif recovery_number == 2:
    #         next_date = trigger_date_time + datetime.timedelta(days=1)
    #         if trigger_date_time.hour < 12:
    #
    #             start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
    #                                            0, 0, 0)
    #             end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
    #                                          12, 0, 0)
    #
    #         if trigger_date_time.hour >= 12:
    #
    #             start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
    #                                            next_date.day,
    #                                            12, 0, 0)
    #             next_date = next_date + datetime.timedelta(days=1)
    #             end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
    #                                          next_date.day,
    #                                          0, 0, 0)
    #
    #     elif recovery_number == 3:
    #         next_date = trigger_date_time + datetime.timedelta(days=1)
    #         if trigger_date_time.hour < 12:
    #             start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
    #                                            12, 0, 0)
    #             next_date = next_date + datetime.timedelta(days=1)
    #             end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
    #                                          0, 0, 0)
    #
    #         if trigger_date_time.hour >= 12:
    #             next_date = trigger_date_time + datetime.timedelta(days=2)
    #             start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
    #                                            next_date.day,
    #                                            0, 0, 0)
    #             end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
    #                                          next_date.day,
    #                                          12, 0, 0)
    #
    #     return start_time, end_time

    '''Deprecated
    def get_recovery_sessions(self, trigger_date_time, soreness_list):

        # daily_readiness_survey = training_cycle.get_last_daily_readiness_survey()
        recommendations = exercise.ExerciseRecommendations()

        # ACTIVE RECOVERY EXERCISES
        # need to treat each soreness report separately because it could have different report dates, etc
        for soreness in soreness_list:
            soreness_exercises = recovery_data_access.RecoveryDataAccess.get_exercises_for_soreness(soreness)
            recommendations.update(soreness.severity, soreness_exercises)

        # post session soreness??

        # injury history
        # injury_exercises = recovery_data_access.RecoveryDataAccess.get_exercises_for_injury_history(injury_history)
        # recovery_exercises.extend(injury_exercises)

        # COMPRESSION

        # COLD THERAPY

        # NUTRITION

        # HYDRATION

        # return recovery_exercises

    '''

    # def recalculate_current_training_cycle(self, training_history):
    #
    #     calc = training.Calculator()
    #
    #     training_cycle = training_history.training_cycles[0]
    #
    #     # update expected load, etc for the week
    #     self.impute_load()
    #
    #     # add any training modifications?
    #
    #     # do we need to add, change or delete long-term recovery modalities?
    #     # if fatiguing, certainly need to add certain modalities
    #     if self.is_athlete_fatiguing():
    #         j = 0
    #
    #     # do we need to add, change or delete corrective exercises?
    #
    #     # do we need to add, change or delete bump-up sessions?
    #
    #     load_gap = self.current_load_gap()
    #     if load_gap.exists():
    #
    #         # TODO: what if the user has already seleceted exercises for a bump-up session?  should we preserve?
    #         bump_up_sessions = self.get_bump_up_sessions(self.training_cycles, load_gap)
    #
    #         # ^ do we need to replace existing? add to the list or blow out all estimated and redo?

    # def get_bump_up_sessions(self, training_history, load_gap):
    #
    #     bump_up_sessions = []  # returns an array of bump up sessions
    #     training_sessions = training_history.training_cycles[0].sessions
    #
    #     # monotony = weekly mean total load/weekly standard deviation of load
    #     # In order to increase the standard deviation of a set of numbers, you must add a value that is more than
    #     # one standard deviation away from the mean
    #
    #     internal_load_available = load_gap.internal_total_load
    #
    #     if internal_load_available <= 0:
    #         return None
    #
    #     internal_external_load_ratio = training_history.weighted_internal_external_load_ratio()
    #
    #     # we can adjust/replace the existing bump-up session since it hasn't been completed yet
    #     current_bump_up_count = len(
    #         [t for t in training_sessions if t.session_type is session.SessionType.bump_up and t.estimated])
    #
    #     max_sessions = 4 - current_bump_up_count
    #
    #     internal_load_values = list(x.internal_load() for x in training_sessions if x.internal_load() is not None)
    #     # internal_load_mean = np.mean(internal_load_values).item()
    #     # internal_load_median = np.median(internal_load_values).item()
    #     # internal_load_stddev = np.std(internal_load_values).item()
    #
    #     for s in range(0, max_sessions):
    #
    #         # if internal_load_median > internal_load_mean:  # if it's biased toward higher loads
    #         #    internal_target_value = min(internal_load_mean - (internal_load_stddev * 1.10), internal_load_available)
    #         # else:
    #         #    internal_target_value = min(internal_load_stddev * 1.05, internal_load_available)
    #
    #         bump_up_session = session.BumpUpSession()
    #
    #         # let's begin with a max RPE allowed of 5
    #         target_rpe = 5
    #         target_minutes = internal_target_value / target_rpe
    #
    #         if target_minutes < 10:
    #             # scale up the minutes
    #             target_minutes = 10
    #             target_rpe = max(internal_target_value / target_minutes, 2)  # we don't want target RPE < 2
    #             target_rpe = min(target_rpe, 8)  # we don't want target RPE > 8
    #         elif target_minutes > 30:
    #             target_minutes = 30
    #             target_rpe = min(internal_target_value / target_minutes, 8)  # we don't want target RPE > 8
    #
    #         internal_target_value = target_minutes * target_rpe
    #
    #         bump_up_session.session_RPE = target_rpe
    #         bump_up_session.duration_minutes = target_minutes
    #
    #         bump_up_session.external_load = internal_target_value / internal_external_load_ratio
    #
    #         bump_up_session.estimated = True
    #         bump_up_session.internal_load_imputed = False
    #         bump_up_session.external_load_imputed = True
    #
    #         bump_up_session = self.adjust_bump_up_session_intensity(bump_up_session, load_gap)
    #
    #         bump_up_sessions.append(bump_up_session)
    #
    #         internal_load_values.append(max(internal_target_value, 0))
    #
    #         internal_load_available = internal_load_available - internal_target_value
    #
    #         # internal_load_mean = np.mean(internal_load_values).item()
    #         # internal_load_median = np.median(internal_load_values).item()
    #         # internal_load_stddev = np.std(internal_load_values).item()
    #         #monotony = internal_load_mean / internal_load_stddev
    #         #if monotony < 2 and internal_load_available == 0:
    #         #    break
    #
    #     return bump_up_sessions

    # def adjust_bump_up_session_intensity(self, bump_up_session, load_gap):
    #
    #     # assuming RPE and minutes have already been set
    #     if (load_gap.external_high_intensity_load is None
    #             and load_gap.external_mod_intensity_load is None
    #             and load_gap.external_low_intensity_load is None):
    #         return bump_up_session
    #     else:
    #         high_percent = (load_gap.external_high_intensity_load /
    #                         (load_gap.external_high_intensity_load +
    #                          load_gap.external_mod_intensity_load +
    #                          load_gap.external_low_intensity_load))
    #         mod_percent = (load_gap.external_mod_intensity_load /
    #                        (load_gap.external_high_intensity_load +
    #                         load_gap.external_mod_intensity_load +
    #                         load_gap.external_low_intensity_load))
    #         low_percent = (load_gap.external_low_intensity_load /
    #                        (load_gap.external_high_intensity_load +
    #                         load_gap.external_mod_intensity_load +
    #                         load_gap.external_low_intensity_load))
    #
    #         temp_rpe = (high_percent * 8) + (mod_percent * 5) + (low_percent * 2)
    #
    #         current_internal_load = bump_up_session.session_RPE * bump_up_session.duration_minutes
    #
    #         bump_up_session.session_RPE = temp_rpe
    #         bump_up_session.duration_minutes = current_internal_load / temp_rpe
    #
    #         # TODO: test this math!
    #         bump_up_session.high_intensity_load = bump_up_session.external_load * high_percent
    #         bump_up_session.mod_intensity_load = bump_up_session.external_load * mod_percent
    #         bump_up_session.low_intensity_load = bump_up_session.external_load * low_percent
    #         bump_up_session.high_intensity_minutes = bump_up_session.duration_minutes * high_percent
    #         bump_up_session.mod_intensity_minutes = bump_up_session.duration_minutes * mod_percent
    #         bump_up_session.low_intensity_minutes = bump_up_session.duration_minutes * low_percent
    #         bump_up_session.high_intensity_RPE = 8
    #         bump_up_session.mod_intensity_RPE = 5
    #         bump_up_session.low_intensity_RPE = 2
    #
    #         return bump_up_session


def is_functional_strength_eligible(athlete_stats, last_updated):
    if (athlete_stats.functional_strength_eligible and
        not athlete_stats.severe_pain_soreness_today() and  # these are updated from surveys but update doesn't make it to stats until after plan is created
        (athlete_stats.next_functional_strength_eligible_date is None or 
         parse_datetime(athlete_stats.next_functional_strength_eligible_date) < parse_datetime(last_updated))):  # need to check if 24 hours have passed since last completed
        athlete_stats.functional_strength_eligible = True
    else:
        athlete_stats.functional_strength_eligible = False
