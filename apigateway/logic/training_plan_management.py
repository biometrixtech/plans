import datetime

from fathomapi.utils.xray import xray_recorder
from fathomapi.utils.exceptions import NoSuchEntityException
import logic.exercise_mapping as exercise_mapping
from logic.soreness_processing import SorenessCalculator
from logic.functional_strength_mapping import FSProgramGenerator
import models.session as session
from models.soreness import HistoricSorenessStatus
from models.post_session_survey import PostSessionSurvey
from utils import format_date, parse_datetime, parse_date


class TrainingPlanManager(object):

    def __init__(self, athlete_id, datastore_collection):
        self.athlete_id = athlete_id
        self.post_session_survey_datastore = datastore_collection.post_session_survey_datastore
        self.daily_plan_datastore = datastore_collection.daily_plan_datastore
        self.exercise_library_datastore = datastore_collection.exercise_datastore
        self.athlete_stats_datastore = datastore_collection.athlete_stats_datastore
        self.completed_exercise_datastore = datastore_collection.completed_exercise_datastore
        self.trigger_date_time = None
        self.daily_plan = None
        self.readiness_surveys = []
        self.post_session_surveys = []
        self.athlete_stats = None

    def post_session_surveys_today(self, trigger_date):

        try:
            todays_date_time = datetime.datetime.strptime(trigger_date, '%Y-%m-%d')
        except ValueError:
            todays_date_time = datetime.datetime.strptime(trigger_date, '%Y-%m-%dT%H:%M:%SZ')

        todays_date = todays_date_time.strftime("%Y-%m-%d")

        for p in self.post_session_surveys:
            event_date_time = datetime.datetime.strptime(p.event_date, "%Y-%m-%d")
            if event_date_time.strftime("%Y-%m-%d") == todays_date:
                return True

        return False

    def show_post_recovery(self, post_surveys_today):
        if post_surveys_today and not self.daily_plan.session_from_readiness:
            return True
        else:
            if self.daily_plan.sessions_planned_readiness:
                return False
            else:
                return True

    def load_data(self, event_date):
        daily_plans = self.daily_plan_datastore.get(self.athlete_id, format_date(parse_date(event_date) - datetime.timedelta(days=1)), event_date)
        daily_plan = [plan for plan in daily_plans if plan.event_date == event_date]
        if len(daily_plan) == 0:
            raise NoSuchEntityException("Plan not found for the day")
        else:
            self.daily_plan = daily_plan[0]
        self.readiness_surveys = [plan.daily_readiness_survey for plan in daily_plans if plan.daily_readiness_survey is not None]
        for plan in daily_plans:
            post_surveys = \
                [PostSessionSurvey.post_session_survey_from_training_session(ts.post_session_survey, self.athlete_id, ts.id, ts.session_type().value, plan.event_date)
                 for ts in plan.training_sessions if ts is not None]
            self.post_session_surveys.extend([s for s in post_surveys if s is not None])

        if self.athlete_stats is None:
            self.athlete_stats = self.athlete_stats_datastore.get(self.athlete_id)

    @xray_recorder.capture('logic.TrainingPlanManager.create_daily_plan')
    def create_daily_plan(self, event_date, last_updated, target_minutes=15, athlete_stats=None):
        self.athlete_stats = athlete_stats
        self.trigger_date_time = parse_datetime(last_updated)
        self.load_data(event_date)

        historic_soreness_present = False
        if self.athlete_stats is None:
            historic_soreness = []
        else:
            historic_soreness = [hs for hs in self.athlete_stats.historic_soreness if hs.historic_soreness_status is not None and
                                 hs.historic_soreness_status is not HistoricSorenessStatus.dormant_cleared and
                                 hs.historic_soreness_status is not HistoricSorenessStatus.almost_persistent_soreness and
                                 hs.historic_soreness_status is not HistoricSorenessStatus.almost_persistent_pain]
            historic_soreness_present = len(historic_soreness) > 0
            is_functional_strength_eligible(self.athlete_stats, last_updated)

        soreness_list = SorenessCalculator().get_soreness_summary_from_surveys(self.readiness_surveys,
                                                                               self.post_session_surveys,
                                                                               self.trigger_date_time,
                                                                               historic_soreness)

        post_surveys_today = self.post_session_surveys_today(event_date)

        show_post_recovery = self.show_post_recovery(post_surveys_today)
        self.add_recovery_times(show_post_recovery)

        calc = exercise_mapping.ExerciseAssignmentCalculator(self.athlete_id, self.exercise_library_datastore,
                                                             self.completed_exercise_datastore,
                                                             historic_soreness_present)

        soreness_values = [s.severity for s in soreness_list if s.severity is not None and s.daily]

        if soreness_values is not None and len(soreness_values) > 0:
            max_soreness = max(soreness_values)
        else:
            max_soreness = 0

        if self.daily_plan.functional_strength_session is None:
            self.populate_functional_strength(True)

        functional_strength_active = (self.daily_plan.functional_strength_session is not None)

        if not show_post_recovery:
            if self.daily_plan.pre_recovery is not None and not self.daily_plan.pre_recovery.completed:
                self.daily_plan.pre_recovery.set_exercise_target_minutes(soreness_list, target_minutes, max_soreness,
                                                                         historic_soreness_present,
                                                                         functional_strength_active,
                                                                         is_active_prep=True)
                am_exercise_assignments = calc.create_exercise_assignments(self.daily_plan.pre_recovery, soreness_list,
                                                                           self.trigger_date_time, target_minutes)
                self.daily_plan.pre_recovery.update_from_exercise_assignments(am_exercise_assignments)
                self.daily_plan.pre_recovery.display_exercises = True
            else:
                self.daily_plan.pre_recovery.display_exercises = False

        if show_post_recovery:
            if self.daily_plan.post_recovery is not None and not self.daily_plan.post_recovery.completed:
                self.daily_plan.post_recovery.set_exercise_target_minutes(soreness_list, target_minutes, max_soreness,
                                                                          historic_soreness_present,
                                                                          functional_strength_active,
                                                                          is_active_prep=False)
                pm_exercise_assignments = calc.create_exercise_assignments(self.daily_plan.post_recovery, soreness_list,
                                                                           self.trigger_date_time, target_minutes)
                self.daily_plan.post_recovery.update_from_exercise_assignments(pm_exercise_assignments)
                if not self.daily_plan.functional_strength_completed and (pm_exercise_assignments is None or pm_exercise_assignments.duration_minutes() == 0):
                    self.daily_plan.functional_strength_session = None
                    self.daily_plan.functional_strength_eligible = False

                self.daily_plan.post_recovery.display_exercises = True
            else:
                self.daily_plan.post_recovery.display_exercises = False

        self.daily_plan.last_updated = last_updated

        self.daily_plan_datastore.put(self.daily_plan)

        return self.daily_plan

    def populate_functional_strength(self, wants_functional_strength):

        if self.athlete_stats is not None:
            self.daily_plan.functional_strength_eligible = self.athlete_stats.functional_strength_eligible

            if self.daily_plan.functional_strength_eligible and wants_functional_strength:
                if not self.daily_plan.functional_strength_completed:
                    fs_mapping = FSProgramGenerator(self.exercise_library_datastore)
                    self.daily_plan.functional_strength_session = fs_mapping.getFunctionalStrengthForSportPosition(
                        self.athlete_stats.current_sport_name,
                        self.athlete_stats.current_position)

    def add_recovery_times(self, show_post_recovery):

        if not show_post_recovery:
            if self.daily_plan.pre_recovery is None:
                self.daily_plan.pre_recovery = session.RecoverySession()
                self.daily_plan.pre_recovery.display_exercises = True
            self.daily_plan.post_recovery.display_exercises = False
        else:
            self.daily_plan.pre_recovery.display_exercises = False
            if self.daily_plan.post_recovery is not None and self.daily_plan.post_recovery.completed:
                self.daily_plan.completed_post_recovery_sessions.append(self.daily_plan.post_recovery)
            self.daily_plan.post_recovery = session.RecoverySession()
            self.daily_plan.post_recovery.display_exercises = True


def is_functional_strength_eligible(athlete_stats, last_updated):
    if (athlete_stats.functional_strength_eligible and
        not athlete_stats.severe_pain_soreness_today() and  # these are updated from surveys but update doesn't make it to stats until after plan is created
        (athlete_stats.next_functional_strength_eligible_date is None or 
         parse_datetime(athlete_stats.next_functional_strength_eligible_date) < parse_datetime(last_updated))):  # need to check if 24 hours have passed since last completed
        athlete_stats.functional_strength_eligible = True
    else:
        athlete_stats.functional_strength_eligible = False
