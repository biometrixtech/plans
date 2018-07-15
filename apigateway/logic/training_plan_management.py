import logic.training as training
import models.session as session
from models.daily_plan import DailyPlan
import datetime
import logic.exercise_mapping as exercise_mapping
from logic.soreness_and_injury import SorenessCalculator
#from datastores.daily_readiness_datastore import DailyReadinessDatastore
#from datastores.daily_schedule_datastore import DailyScheduleDatastore
from utils import format_datetime


class TrainingPlanManager(object):

    def __init__(self, athlete_id, daily_readiness_datastore, daily_schedule_datastore, daily_plan_datastore):
        self.athlete_id = athlete_id
        self.daily_readiness_datastore = daily_readiness_datastore
        self.daily_schedule_datastore = daily_schedule_datastore
        self.daily_plan_datastore = daily_plan_datastore

    def calculate_am_impact_score(self, rpe, readiness, sleep_quality, max_soreness):

        max_soreness_score = min(max_soreness, 5)
        sleep_quality_score = min(((10 - sleep_quality) / 10) * 3, 3)
        readiness_score = min(((10 - readiness) / 10) * 5, 5)
        rpe_score = min((rpe / 10) * 4, 4)

        return max(max_soreness_score, sleep_quality_score, readiness_score, rpe_score)

    def calculate_pm_impact_score(self, rpe, readiness, sleep_quality, max_soreness):

        max_soreness_score = min(max_soreness, 5)
        sleep_quality_score = min(((10 - sleep_quality) / 10) * 3, 3)
        readiness_score = min(((10 - readiness) / 10) * 3, 3)
        rpe_score = min((rpe / 10) * 5, 5)

        return max(max_soreness_score, sleep_quality_score, readiness_score, rpe_score)

    def create_daily_plan(self):
        last_daily_readiness_survey = self.daily_readiness_datastore.get(self.athlete_id)

        last_post_session_surveys = []
        #    self.athlete_dao.get_last_post_session_surveys(last_daily_readiness_survey.get_event_date(),
        #                                                   last_daily_readiness_survey.get_event_date()
        #                                                   - datetime.timedelta(hours=48, minutes=0)
        #                                                   )

        trigger_date_time = last_daily_readiness_survey.get_event_date()

        survey_event_dates = [s.get_event_date() for s in last_post_session_surveys]

        if survey_event_dates is not None and len(survey_event_dates) > 0:
            trigger_date_time = max(trigger_date_time, max(survey_event_dates))

        soreness_list = SorenessCalculator().get_soreness_summary_from_surveys(
            last_daily_readiness_survey,
            last_post_session_surveys,
            trigger_date_time
        )

        scheduled_sessions = self.daily_schedule_datastore.get(self.athlete_id, trigger_date_time)

        trigger_date_time_string = trigger_date_time.date().strftime('%Y-%m-%d')

        daily_plans = self.daily_plan_datastore.get(self.athlete_id, trigger_date_time_string, trigger_date_time_string)

        if daily_plans is None or len(daily_plans) == 0:
            daily_plan = DailyPlan(trigger_date_time_string)
        else:
            daily_plan = daily_plans[len(daily_plans) - 1]

        daily_plan.user_id = self.athlete_id
        daily_plan.daily_readiness_survey = last_daily_readiness_survey.get_event_date().strftime('%Y-%m-%d')

        daily_plan = self.add_recovery_times(trigger_date_time, daily_plan)

        calc = exercise_mapping.ExerciseAssignmentCalculator(self.athlete_id)

        soreness_values = [s.severity for s in soreness_list if s.severity is not None]
        if soreness_values is not None and len(soreness_values) > 0:
            max_soreness = max(soreness_values)
        else:
            max_soreness = 0

        rpe_values = [s.session_rpe for s in last_post_session_surveys if s.session_rpe is not None]

        if rpe_values is not None and len(rpe_values) > 0:
            max_rpe = max(rpe_values)
        else:
            max_rpe = 0

        am_impact_score = self.calculate_am_impact_score(
                            max_rpe,
                            last_daily_readiness_survey.readiness,
                            last_daily_readiness_survey.sleep_quality,
                            max_soreness
                            )

        pm_impact_score = self.calculate_pm_impact_score(
            max_rpe,
            last_daily_readiness_survey.readiness,
            last_daily_readiness_survey.sleep_quality,
            max_soreness
        )

        if daily_plan.recovery_am is not None and am_impact_score >= 0.5:
            daily_plan.recovery_am.set_exercise_target_minutes(soreness_list, 15)
            am_exercise_assignments = calc.create_exercise_assignments(daily_plan.recovery_am,
                                                                       soreness_list)
            daily_plan.recovery_am.update_from_exercise_assignments(am_exercise_assignments)
            daily_plan.recovery_am.impact_score = am_impact_score
        else:
            daily_plan.recovery_am is None

        if pm_impact_score >= 0.5:
            daily_plan.recovery_pm.set_exercise_target_minutes(soreness_list, 15)
            pm_exercise_assignments = calc.create_exercise_assignments(daily_plan.recovery_pm,
                                                                       soreness_list)
            daily_plan.recovery_pm.update_from_exercise_assignments(pm_exercise_assignments)
            daily_plan.recovery_pm.impact_score = pm_impact_score
        else:
            daily_plan.recovery_pm is None

        daily_plan.add_scheduled_sessions(scheduled_sessions)

        daily_plan.last_updated = format_datetime(datetime.datetime.utcnow())

        self.daily_plan_datastore.put(daily_plan)

        return True

    def create_training_cycle(self, athlete_schedule, athlete_injury_history):
        # schedule_manager = schedule.ScheduleManager()
        # athlete_schedule = schedule_manager.get_typical_schedule(athlete_id)
        training_cycle = training.TrainingCycle()
        # TODO set start and end dates of training_cycle
        for s in athlete_schedule.sessions:
            new_session = s.create()
            training_cycle.sessions.extend(new_session)

        # add recovery sessions based on athlete status and history
        training_cycle.recovery_modalities = self.get_recovery_sessions(athlete_injury_history, training_cycle)

    def add_recovery_times(self, trigger_date_time, daily_plan):

        if trigger_date_time.hour < 12:
            daily_plan.recovery_am.start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                                                  trigger_date_time.day, 0, 0, 0)
            daily_plan.recovery_am.end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                                                trigger_date_time.day, 12, 0, 0)
        else:
            daily_plan.recovery_am = None

        daily_plan.recovery_pm.start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                                              trigger_date_time.day, 12, 0, 0)
        next_date = trigger_date_time + datetime.timedelta(days=1)
        daily_plan.recovery_pm.end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                                            next_date.day, 0, 0, 0)
        return daily_plan

    def get_recovery_start_end_times(self, trigger_date_time, recovery_number):

        start_time = None
        end_time = None

        if recovery_number == 0:

            if trigger_date_time.hour < 12:

                start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, trigger_date_time.day,
                                               0, 0, 0)
                end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, trigger_date_time.day,
                                             12, 0, 0)
            if trigger_date_time.hour >= 12:
                start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                               trigger_date_time.day,
                                               12, 0, 0)
                next_date = trigger_date_time + datetime.timedelta(days=1)
                end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                             next_date.day,
                                             0, 0, 0)

        elif recovery_number == 1:

            if trigger_date_time.hour < 12:
                start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                               trigger_date_time.day,
                                               12, 0, 0)
                next_date = trigger_date_time + datetime.timedelta(days=1)
                end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                             next_date.day,
                                             0, 0, 0)
            if trigger_date_time.hour >= 12:
                next_date = trigger_date_time + datetime.timedelta(days=1)
                start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
                                               0, 0, 0)
                end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
                                             12, 0, 0)

        elif recovery_number == 2:
            next_date = trigger_date_time + datetime.timedelta(days=1)
            if trigger_date_time.hour < 12:

                start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
                                               0, 0, 0)
                end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
                                             12, 0, 0)

            if trigger_date_time.hour >= 12:

                start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                               next_date.day,
                                               12, 0, 0)
                next_date = next_date + datetime.timedelta(days=1)
                end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                             next_date.day,
                                             0, 0, 0)

        elif recovery_number == 3:
            next_date = trigger_date_time + datetime.timedelta(days=1)
            if trigger_date_time.hour < 12:
                start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
                                               12, 0, 0)
                next_date = next_date + datetime.timedelta(days=1)
                end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month, next_date.day,
                                             0, 0, 0)

            if trigger_date_time.hour >= 12:
                next_date = trigger_date_time + datetime.timedelta(days=2)
                start_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                               next_date.day,
                                               0, 0, 0)
                end_time = datetime.datetime(trigger_date_time.year, trigger_date_time.month,
                                             next_date.day,
                                             12, 0, 0)

        return start_time, end_time

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

    def recalculate_current_training_cycle(self, training_history):

        calc = training.Calculator()

        training_cycle = training_history.training_cycles[0]

        # update expected load, etc for the week
        self.impute_load()

        # add any training modifications?

        # do we need to add, change or delete long-term recovery modalities?
        # if fatiguing, certainly need to add certain modalities
        if self.is_athlete_fatiguing():
            j = 0

        # do we need to add, change or delete corrective exercises?

        # do we need to add, change or delete bump-up sessions?

        load_gap = self.current_load_gap()
        if load_gap.exists():

            # TODO: what if the user has already seleceted exercises for a bump-up session?  should we preserve?
            bump_up_sessions = self.get_bump_up_sessions(self.training_cycles, load_gap)

            # ^ do we need to replace existing? add to the list or blow out all estimated and redo?

    def get_bump_up_sessions(self, training_history, load_gap):

        bump_up_sessions = []  # returns an array of bump up sessions
        training_sessions = training_history.training_cycles[0].sessions

        # monotony = weekly mean total load/weekly standard deviation of load
        # In order to increase the standard deviation of a set of numbers, you must add a value that is more than
        # one standard deviation away from the mean

        internal_load_available = load_gap.internal_total_load

        if internal_load_available <= 0:
            return None

        internal_external_load_ratio = training_history.weighted_internal_external_load_ratio()

        # we can adjust/replace the existing bump-up session since it hasn't been completed yet
        current_bump_up_count = len(
            [t for t in training_sessions if t.session_type is session.SessionType.bump_up and t.estimated])

        max_sessions = 4 - current_bump_up_count

        internal_load_values = list(x.internal_load() for x in training_sessions if x.internal_load() is not None)
        # internal_load_mean = np.mean(internal_load_values).item()
        # internal_load_median = np.median(internal_load_values).item()
        # internal_load_stddev = np.std(internal_load_values).item()

        for s in range(0, max_sessions):

            # if internal_load_median > internal_load_mean:  # if it's biased toward higher loads
            #    internal_target_value = min(internal_load_mean - (internal_load_stddev * 1.10), internal_load_available)
            # else:
            #    internal_target_value = min(internal_load_stddev * 1.05, internal_load_available)

            bump_up_session = session.BumpUpSession()

            # let's begin with a max RPE allowed of 5
            target_rpe = 5
            target_minutes = internal_target_value / target_rpe

            if target_minutes < 10:
                # scale up the minutes
                target_minutes = 10
                target_rpe = max(internal_target_value / target_minutes, 2)  # we don't want target RPE < 2
                target_rpe = min(target_rpe, 8)  # we don't want target RPE > 8
            elif target_minutes > 30:
                target_minutes = 30
                target_rpe = min(internal_target_value / target_minutes, 8)  # we don't want target RPE > 8

            internal_target_value = target_minutes * target_rpe

            bump_up_session.session_RPE = target_rpe
            bump_up_session.duration_minutes = target_minutes

            bump_up_session.external_load = internal_target_value / internal_external_load_ratio

            bump_up_session.estimated = True
            bump_up_session.internal_load_imputed = False
            bump_up_session.external_load_imputed = True

            bump_up_session = self.adjust_bump_up_session_intensity(bump_up_session, load_gap)

            bump_up_sessions.append(bump_up_session)

            internal_load_values.append(max(internal_target_value, 0))

            internal_load_available = internal_load_available - internal_target_value

            # internal_load_mean = np.mean(internal_load_values).item()
            # internal_load_median = np.median(internal_load_values).item()
            # internal_load_stddev = np.std(internal_load_values).item()
            #monotony = internal_load_mean / internal_load_stddev
            #if monotony < 2 and internal_load_available == 0:
            #    break

        return bump_up_sessions

    def adjust_bump_up_session_intensity(self, bump_up_session, load_gap):

        # assuming RPE and minutes have already been set
        if (load_gap.external_high_intensity_load is None
                and load_gap.external_mod_intensity_load is None
                and load_gap.external_low_intensity_load is None):
            return bump_up_session
        else:
            high_percent = (load_gap.external_high_intensity_load /
                            (load_gap.external_high_intensity_load +
                             load_gap.external_mod_intensity_load +
                             load_gap.external_low_intensity_load))
            mod_percent = (load_gap.external_mod_intensity_load /
                           (load_gap.external_high_intensity_load +
                            load_gap.external_mod_intensity_load +
                            load_gap.external_low_intensity_load))
            low_percent = (load_gap.external_low_intensity_load /
                           (load_gap.external_high_intensity_load +
                            load_gap.external_mod_intensity_load +
                            load_gap.external_low_intensity_load))

            temp_rpe = (high_percent * 8) + (mod_percent * 5) + (low_percent * 2)

            current_internal_load = bump_up_session.session_RPE * bump_up_session.duration_minutes

            bump_up_session.session_RPE = temp_rpe
            bump_up_session.duration_minutes = current_internal_load / temp_rpe

            # TODO: test this math!
            bump_up_session.high_intensity_load = bump_up_session.external_load * high_percent
            bump_up_session.mod_intensity_load = bump_up_session.external_load * mod_percent
            bump_up_session.low_intensity_load = bump_up_session.external_load * low_percent
            bump_up_session.high_intensity_minutes = bump_up_session.duration_minutes * high_percent
            bump_up_session.mod_intensity_minutes = bump_up_session.duration_minutes * mod_percent
            bump_up_session.low_intensity_minutes = bump_up_session.duration_minutes * low_percent
            bump_up_session.high_intensity_RPE = 8
            bump_up_session.mod_intensity_RPE = 5
            bump_up_session.low_intensity_RPE = 2

            return bump_up_session



