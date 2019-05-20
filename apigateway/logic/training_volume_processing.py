from fathomapi.utils.xray import xray_recorder
from models.training_volume import LoadMonitoringType, StandardErrorRange, StandardErrorRangeMetric
from models.sport import SportName, SportType
from datetime import timedelta
import statistics, math
from utils import format_date, parse_date
from itertools import groupby
from operator import itemgetter, attrgetter
from statistics import stdev, mean


class LoadingEvent(object):
    def __init__(self, loading_date, load, sport_name):
        self.loading_date = loading_date
        self.load = load
        self.sport_name = sport_name
        self.affected_body_parts = []
        self.previous_affected_body_parts = []
        self.days_rest = None
        self.highest_load_in_36_hrs = False

    def has_existing_soreness(self, days=1):

        for a in self.affected_body_parts:
            matched_soreness = list(p for p in self.previous_affected_body_parts if p.body_part == a.body_part
                                    and p.side == a.side and p.days_sore >= days)
            if len(matched_soreness) > 0:
                return True

        return False


class AffectedBodyPart(object):
    def __init__(self, body_part, side, days_sore, max_severity, cleared):
        self.body_part = body_part
        self.side = side
        self.days_sore = days_sore
        self.max_severity = max_severity
        self.cleared = cleared
        self.first_reported_date = None
        self.last_reported_date = None


class TrainingVolumeProcessing(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.a_internal_load_values = []
        self.a_external_load_values = []
        self.a_high_intensity_values = []
        self.a_mod_intensity_values = []
        self.a_low_intensity_values = []

        self.c_internal_load_values = []
        self.c_external_load_values = []
        self.c_high_intensity_values = []
        self.c_mod_intensity_values = []
        self.c_low_intensity_values = []

        self.last_week_external_values = []
        self.previous_week_external_values = []
        self.last_week_internal_values = []
        self.previous_week_internal_values = []

        self.internal_load_tuples = []
        self.external_load_tuples = []
        self.low_internal_load_day_lower_bound = None
        self.mod_internal_load_day_lower_bound = None
        self.high_internal_load_day_lower_bound = None
        self.low_internal_load_day_upper_bound = None
        self.mod_internal_load_day_upper_bound = None
        self.high_internal_load_day_upper_bound = None
        self.load_monitoring_measures = {}

        self.daily_readiness_tuples = []
        self.post_session_survey_tuples = []
        self.no_soreness_load_tuples = []
        self.soreness_load_tuples = []
        self.load_tuples_last_2_weeks = []
        self.load_tuples_last_2_4_weeks = []
        self.no_soreness_load_tuples_last_2_weeks = []
        self.no_soreness_load_tuples_last_2_4_weeks = []
        self.muscular_strain_last_2_weeks = None
        self.muscular_strain_last_2_4_weeks = None
        self.recovery_loads = {}
        self.maintenance_loads = {}
        self.functional_overreaching_loads = {}
        self.functional_overreaching_NFO_loads = {}
        self.high_relative_load_session = False
        self.doms = []
        self.last_week_sport_duration_loads = {}
        self.previous_week_sport_duration_loads = {}

    def muscular_strain_increasing(self):

        if self.muscular_strain_last_2_weeks is not None and self.muscular_strain_last_2_4_weeks is not None:
            if self.muscular_strain_last_2_weeks > self.muscular_strain_last_2_4_weeks:
                return True
            else:
                return False
        else:
            return False

    def calc_high_relative_load_benchmarks(self):

        benchmarks = {}

        for sport, load_list in self.functional_overreaching_loads.items():
            if sport not in benchmarks:
                benchmarks[sport] = mean(load_list)
            else:
                benchmarks[sport] = min(benchmarks[sport], mean(load_list))

        for sport, load_list in self.functional_overreaching_NFO_loads.items():
            if sport not in benchmarks:
                benchmarks[sport] = mean(load_list)
            else:
                benchmarks[sport] = min(benchmarks[sport], mean(load_list))

        return benchmarks

    def fill_load_monitoring_measures(self, load_stats, readiness_surveys, daily_plans, load_end_date):

        swimming_sessions = []
        cycling_sessions = []
        running_sessions = []
        walking_sessions = []
        duration_sessions = []

        training_sessions = self.get_training_sessions(daily_plans)

        for t in training_sessions:
            swimming_sessions.append((t.event_date, t.swimming_load(), t.sport_name))
            cycling_sessions.append((t.event_date, t.cycling_load(), t.sport_name))
            running_sessions.append((t.event_date, t.running_load(), t.sport_name))
            walking_sessions.append((t.event_date, t.walking_load(), t.sport_name))
            training_volume = t.training_volume(load_stats)
            if training_volume is not None:
                duration_sessions.append((t.event_date, training_volume, t.sport_name))

        self.load_monitoring_measures[LoadMonitoringType.RPExSwimmingDistance] = swimming_sessions
        self.load_monitoring_measures[LoadMonitoringType.RPExCyclingDistance] = cycling_sessions
        self.load_monitoring_measures[LoadMonitoringType.RPExRunningDistance] = running_sessions
        self.load_monitoring_measures[LoadMonitoringType.RPExWalkingDistance] = walking_sessions
        self.load_monitoring_measures[LoadMonitoringType.RPExDuration] = duration_sessions

        self.load_surveys(readiness_surveys, training_sessions)

        self.load_adaptation_history(duration_sessions, load_end_date)

        if len(training_sessions) > 0:
            last_training_session = training_sessions[len(training_sessions) - 1]
            benchmarks = self.calc_high_relative_load_benchmarks()
            self.high_relative_load_session = self.is_last_session_high_relative_load(load_end_date,
                                                                                      last_training_session,
                                                                                      benchmarks,
                                                                                      load_stats)

    def is_last_session_high_relative_load(cls, event_date, last_training_session, benchmarks, load_stats):
        if (event_date - last_training_session.event_date).days <= 2:
            if last_training_session.sport_name in benchmarks:
                if last_training_session.training_volume(load_stats) >= benchmarks[last_training_session.sport_name]:
                    return True
        else:
            return False

    @xray_recorder.capture('logic.TrainingVolumeProcessing.load_plan_values')
    def load_plan_values(self, last_7_days_plans, days_8_14_plans, acute_daily_plans, chronic_weeks_plans,
                         chronic_daily_plans, load_stats):

        self.last_week_external_values = []
        self.last_week_internal_values = []
        self.last_week_sport_duration_loads = {}
        self.previous_week_sport_duration_loads = {}
        self.previous_week_external_values = []
        self.previous_week_internal_values = []
        self.a_internal_load_values = []
        self.a_external_load_values = []
        self.a_high_intensity_values = []
        self.a_mod_intensity_values = []
        self.a_low_intensity_values = []
        self.c_external_load_values = []
        self.c_high_intensity_values = []
        self.c_mod_intensity_values = []
        self.c_low_intensity_values = []
        self.internal_load_tuples = []

        last_7_day_training_sessions = self.get_training_sessions(last_7_days_plans)
        previous_7_day_training_sessions = self.get_training_sessions(days_8_14_plans)

        for l in last_7_day_training_sessions:
            if l.sport_name not in self.last_week_sport_duration_loads:
                self.last_week_sport_duration_loads[l.sport_name] = []
                self.previous_week_sport_duration_loads[l.sport_name] = []
            duration_load = l.training_volume(load_stats)
            if duration_load is not None:
                self.last_week_sport_duration_loads[l.sport_name].append(duration_load)

        for p in previous_7_day_training_sessions:
            if p.sport_name not in self.previous_week_sport_duration_loads:
                self.last_week_sport_duration_loads[p.sport_name] = []
                self.previous_week_sport_duration_loads[p.sport_name] = []
            duration_load = p.training_volume(load_stats)
            if duration_load is not None:
                self.previous_week_sport_duration_loads[p.sport_name].append(duration_load)

        self.last_week_external_values.extend(
            x for x in self.get_plan_session_attribute_sum_list("external_load", last_7_days_plans) if x is not None)

        self.last_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                    last_7_days_plans) if x is not None)
        self.previous_week_external_values.extend(
            x for x in self.get_plan_session_attribute_sum_list("external_load", days_8_14_plans) if x is not None)

        self.previous_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                    days_8_14_plans) if x is not None)

        self.a_external_load_values.extend(
            x for x in self.get_plan_session_attribute_sum("external_load", acute_daily_plans) if x is not None)

        self.a_internal_load_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               acute_daily_plans) if x is not None)

        self.a_high_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("high_intensity_load", acute_daily_plans) if
            x is not None)

        self.a_mod_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("mod_intensity_load", acute_daily_plans) if
            x is not None)

        self.a_low_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("low_intensity_load", acute_daily_plans) if
            x is not None)

        for w in chronic_weeks_plans:
            self.c_internal_load_values.extend(
                x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes", w)
                if x is not None)

            self.c_external_load_values.extend(
                x for x in self.get_plan_session_attribute_sum("external_load", w) if x is not None)

            self.c_high_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("high_intensity_load", w)
                                           if x is not None)

            self.c_mod_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("mod_intensity_load", w)
                                          if x is not None)

            self.c_low_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("low_intensity_load", w)
                                          if x is not None)

        self.internal_load_tuples.extend(list(x for x in self.get_session_attributes_product_sum_tuple_list("session_RPE",
                                                                                                 "duration_minutes",
                                                                                                acute_daily_plans)
                                if x is not None))
        self.internal_load_tuples.extend(list(x for x in self.get_session_attributes_product_sum_tuple_list("session_RPE",
                                                                                                 "duration_minutes",
                                                                                                 chronic_daily_plans)
                                if x is not None))

        if len(self.internal_load_tuples) > 0:
            internal_load_values = list(x[1] for x in self.internal_load_tuples if x[1] is not None)
            high_internal = max(internal_load_values)
            low_internal = min(internal_load_values)
            range = (high_internal - low_internal) / 3
            self.low_internal_load_day_lower_bound = low_internal
            self.low_internal_load_day_upper_bound = low_internal + range
            self.mod_internal_load_day_upper_bound = high_internal - range
            self.high_internal_load_day_upper_bound = high_internal

    @xray_recorder.capture('logic.TrainingVolumeProcessing.calc_training_volume_metrics')
    def calc_training_volume_metrics(self, athlete_stats):

        athlete_stats.duration_load_ramp = {}

        for sport_name, load in self.previous_week_sport_duration_loads.items():
            athlete_stats.duration_load_ramp[sport_name] = self.get_ramp(athlete_stats.expected_weekly_workouts,
                                                                         self.last_week_sport_duration_loads[sport_name],
                                                                         self.previous_week_sport_duration_loads[sport_name]
                                                                         )

        athlete_stats.external_ramp = self.get_ramp(athlete_stats.expected_weekly_workouts,
                                                    self.last_week_external_values, self.previous_week_external_values)

        athlete_stats.internal_ramp = self.get_ramp(athlete_stats.expected_weekly_workouts,
                                                    self.last_week_internal_values, self.previous_week_internal_values)

        athlete_stats.external_monotony = self.get_monotony(athlete_stats.expected_weekly_workouts,
                                                            self.last_week_external_values)

        athlete_stats.external_strain = self.get_strain(athlete_stats.expected_weekly_workouts,
                                                        athlete_stats.external_monotony, self.last_week_external_values, athlete_stats.historical_external_strain)

        athlete_stats.internal_monotony = self.get_monotony(athlete_stats.expected_weekly_workouts,
                                                            self.last_week_internal_values)

        historical_internal_monotony = self.get_historical_internal_monotony(self.start_date, self.end_date, athlete_stats.expected_weekly_workouts)

        athlete_stats.historical_internal_monotony = historical_internal_monotony

        historical_internal_strain, strain_events = self.get_historical_internal_strain(self.start_date, self.end_date, athlete_stats.expected_weekly_workouts)

        athlete_stats.internal_strain_events = strain_events

        athlete_stats.internal_strain = self.get_strain(athlete_stats.expected_weekly_workouts,
                                                        athlete_stats.internal_monotony, self.last_week_internal_values,
                                                        historical_internal_strain)

        athlete_stats.acute_internal_total_load = self.get_standard_error_range(athlete_stats.expected_weekly_workouts,
                                                                                self.a_internal_load_values)
        athlete_stats.acute_external_total_load = self.get_standard_error_range(athlete_stats.expected_weekly_workouts,
                                                                                self.a_external_load_values)
        athlete_stats.acute_external_high_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.a_high_intensity_values)
        athlete_stats.acute_external_mod_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.a_mod_intensity_values)
        athlete_stats.acute_external_low_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.a_low_intensity_values)

        athlete_stats.chronic_internal_total_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_internal_load_values)
        athlete_stats.chronic_external_total_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_external_load_values)
        athlete_stats.chronic_external_high_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_high_intensity_values)
        athlete_stats.chronic_external_mod_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_mod_intensity_values)
        athlete_stats.chronic_external_low_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_low_intensity_values)

        athlete_stats.external_acwr = self.get_acwr(athlete_stats.acute_external_total_load,
                                                    athlete_stats.chronic_external_total_load)

        athlete_stats.internal_acwr = self.get_acwr(athlete_stats.acute_internal_total_load,
                                                    athlete_stats.chronic_internal_total_load)

        athlete_stats.internal_freshness_index = self.get_freshness_index(
            athlete_stats.acute_internal_total_load,
            athlete_stats.chronic_internal_total_load)

        athlete_stats.external_freshness_index = self.get_freshness_index(
            athlete_stats.acute_external_total_load,
            athlete_stats.chronic_external_total_load)

        athlete_stats.historical_internal_strain = historical_internal_strain

        return athlete_stats

    def find_doms_causal_sessions(self, athlete_stats, training_sessions):

        # training sessions are all the sessions from all_plans

        for d in athlete_stats.delayed_onset_muscle_soreness:
            if d.causal_session is None:
                end_date_time = d.first_reported_date_time
                mid_point_time = d.first_reported_date_time - timedelta(hours=24)
                start_date_time = d.first_reported_date_time - timedelta(hours=48)
                target_sessions = list(t for t in training_sessions if start_date_time <= t.event_date <= end_date_time)
                high_target_sessions = list(
                    t for t in training_sessions if start_date_time <= t.event_date <= mid_point_time and
                    t.high_intensity())
                high_sessions = list(
                    t for t in target_sessions if t.ultra_high_intensity_session() or t.high_intensity_RPE())
                midpoint_sessions = list(t for t in training_sessions if start_date_time <= t.event_date <= mid_point_time)
                # what to do if there are no sessions? leave it None (will only affect historical analysis)
                if len(high_target_sessions) == 1:
                    d.causal_session = high_target_sessions[0]
                elif len(high_sessions) == 1:
                    d.causal_session = high_sessions[0]
                elif len(midpoint_sessions) == 1:
                    d.causal_session = midpoint_sessions[0]
                elif len(target_sessions) == 1:
                    d.causal_session = target_sessions[0]
                elif len(high_target_sessions) > 1:
                    high_target_sessions.sort(key=self.get_event_date_from_session, reverse=True)
                    d.causal_session = high_target_sessions[0]
                elif len(high_sessions) > 1:
                    high_sessions.sort(key=self.get_event_date_from_session, reverse=True)
                    d.causal_session = high_sessions[0]
                elif len(midpoint_sessions) > 1:
                    midpoint_sessions.sort(key=self.get_event_date_from_session, reverse=True)
                    d.causal_session = midpoint_sessions[0]
                elif len(target_sessions) > 1:
                    # keep searching
                    target_sessions.sort(key=self.get_event_date_from_session,
                                         reverse=False)  # DOMS may need 24 hours to manifest; start with earliest
                    d.causal_session = target_sessions[0]
                # else:  we will do nothing if we can't find anything yet

    def calc_muscular_strain(self):

        last_2_weeks_load_sum = sum(
            list(l[1] for l in self.load_tuples_last_2_weeks if l[1] is not None))
        last_2_4_weeks_load_sum = sum(
            list(l[1] for l in self.load_tuples_last_2_4_weeks if l[1] is not None))
        last_2_weeks_no_soreness_load_sum = sum(
            list(l[1] for l in self.no_soreness_load_tuples_last_2_weeks if l[1] is not None))
        last_2_4_weeks_no_soreness_load_sum = sum(
            list(l[1] for l in self.no_soreness_load_tuples_last_2_4_weeks if l[1] is not None))

        if last_2_weeks_load_sum > 0:
            self.muscular_strain_last_2_weeks = (last_2_weeks_no_soreness_load_sum / last_2_weeks_load_sum) * 100
        if last_2_4_weeks_load_sum > 0:
            self.muscular_strain_last_2_4_weeks = (last_2_4_weeks_no_soreness_load_sum / last_2_4_weeks_load_sum) * 100

    def get_training_sessions(self, daily_plans):

        training_sessions = []

        #due to how these are entered, we may have multiple sessions on one day with the same datetime
        for c in daily_plans:
            training_sessions.extend(c.training_sessions)
            #training_sessions.extend(c.practice_sessions)
            #training_sessions.extend(c.strength_conditioning_sessions)
            #training_sessions.extend(c.games)
            #training_sessions.extend(c.bump_up_sessions)

        training_sessions.sort(key=self.get_event_date_from_session)

        return training_sessions

    def get_event_date_from_session(self, session):

        return session.event_date

    def get_tuple_datetime(self, element):
            return element[0]

    def load_surveys(self, readiness_surveys, training_sessions):

        for r in readiness_surveys:
            for s in r.soreness:
                if not s.pain:
                    self.daily_readiness_tuples.append((r.event_date, (s.body_part.location.value, s.side, s.severity)))

        for t in training_sessions:
            if t.post_session_survey is not None:
                for s in t.post_session_survey.soreness:
                    if not s.pain:
                        self.post_session_survey_tuples.append((t.event_date, (s.body_part.location.value, s.side, s.severity)))

        self.daily_readiness_tuples.sort(key=self.get_tuple_datetime)
        self.post_session_survey_tuples.sort(key=self.get_tuple_datetime)

    def load_adaptation_history(self, load_tuples, load_end_date):

        loading_events = []
        initial_loading_events = []
        last_2_week_date = load_end_date - timedelta(days=14)
        last_2_4_week_date = load_end_date - timedelta(days=28)
        max_load = 0
        self.doms = []

        # create a list of loading events first
        for t in range(0, len(load_tuples) - 1):

            if load_tuples[t][0] <= load_end_date:
                loading_event = LoadingEvent(load_tuples[t][0], load_tuples[t][1], load_tuples[t][2])
                initial_loading_events.append(loading_event)

        # sum load by day
        load_grouper = attrgetter('loading_date')
        for k, g in groupby(sorted(initial_loading_events, key=load_grouper), load_grouper):
            part_list = list(g)
            part_list.sort(key=lambda x: (x.loading_date, x.load))
            load_sum = sum(list(g.load for g in part_list if g.load is not None))
            loading_event = LoadingEvent(k, load_sum, part_list[len(part_list) - 1].sport_name)
            max_load = max(loading_event.load, max_load)
            loading_events.append(loading_event)

        early_soreness_tuples = list(s[0] for s in self.post_session_survey_tuples
                                     if s is not None and s[0] >= loading_events[0].loading_date and
                                     s[0] <= loading_events[0].loading_date + timedelta(hours=36))
        early_soreness_tuples.extend(list(s[0] for s in self.daily_readiness_tuples
                                          if s is not None and s[0] >= loading_events[0].loading_date and
                                          s[0] <= loading_events[0].loading_date + timedelta(hours=36)))
        if len(early_soreness_tuples) > 0:
            early_soreness_history = list(set(early_soreness_tuples))

            # let's reduce this down to only the loading events that can have soreness
            # (the highest load within a rolling 36 hour window)
            for t in range(0, len(loading_events)):

                test_date = loading_events[t].loading_date + timedelta(hours=36)
                if len(early_soreness_history) > t:
                    test_date = min(early_soreness_history[t], loading_events[t].loading_date + timedelta(hours=36))
                window_events = list(d for d in loading_events if
                                     d.loading_date >= loading_events[t].loading_date and d.loading_date <= test_date)
                if len(window_events) > 0:
                    window_events.sort(key=lambda x: x.load, reverse=True)
                    window_events[0].highest_load_in_36_hrs = True

            for t in range(0, len(loading_events) - 1):

                if loading_events[t].loading_date <= load_end_date and loading_events[t].highest_load_in_36_hrs:
                    #loading_event = LoadingEvent(self.rpe_load_tuples[t][0], self.rpe_load_tuples[t][1], self.rpe_load_tuples[t][2], self.rpe_load_tuples[t][3])
                    loading_event = loading_events[t]
                    first_load_date = loading_events[0].loading_date

                    # get all affected body parts that could be attributed to this training session
                    next_highest_load_date = loading_events[t].loading_date + timedelta(hours=36)
                    candidates = list(r for r in loading_events if r.loading_date > loading_events[t].loading_date
                                      #and r.loading_date <= next_highest_load_date
                                      #and r.load > loading_events[t].load
                                      and r.highest_load_in_36_hrs)
                    candidates.sort(key=lambda x: x.loading_date)
                    if len(candidates) > 0:
                        next_highest_load_date = candidates[0].loading_date


                    base_soreness_tuples = list((s[0], s[1]) for s in self.post_session_survey_tuples
                                                if s[0] >= loading_events[t].loading_date and
                                                s[0] <= next_highest_load_date)
                    base_soreness_tuples.extend(list((s[0], s[1]) for s in self.daily_readiness_tuples
                                                     if s[0] >= loading_events[t].loading_date and
                                                     s[0] <= next_highest_load_date))

                    body_parts = list(AffectedBodyPart(b[1][0], b[1][1], 0, 0, False) for b in base_soreness_tuples) # body part, side, days sore, max_severity, cleared
                    affected_body_parts = list(set(body_parts))
                    for d in self.doms:
                        matched_list = list(a for a in affected_body_parts if a.body_part==d.body_part and a.side==d.side)
                        if len(matched_list) > 0:
                            affected_body_parts.remove(matched_list[0])
                        aff_body_part = AffectedBodyPart(d.body_part, d.side, d.days_sore, d.max_severity, d.cleared)
                        aff_body_part.last_reported_date = d.last_reported_date
                        affected_body_parts.append(aff_body_part)
                        d.cleared = True

                    self.doms = list(d for d in self.doms if not d.cleared)

                    all_soreness_tuples = list((s[0], s[1]) for s in self.post_session_survey_tuples
                                                if s[0] >= load_tuples[t][0] and
                                                s[0] < load_tuples[t][0] + timedelta(days=12))
                    all_soreness_tuples.extend(list((s[0], s[1]) for s in self.daily_readiness_tuples
                                                     if s[0] >= load_tuples[t][0] and
                                                     s[0] < load_tuples[t][0] + timedelta(days=12)))

                    if len(all_soreness_tuples) == 0:
                        self.doms = []

                    soreness_history = list((h[0], h[1][0], h[1][1], h[1][2]) for h in all_soreness_tuples)
                    unique_soreness_history = list(set(soreness_history))

                    unique_soreness_history.sort(key=self.get_tuple_datetime)
                    unique_soreness_dates = list(dt[0] for dt in unique_soreness_history)
                    for dt in unique_soreness_dates:
                        unique_soreness_events = list(u for u in unique_soreness_history if u[0] == dt)
                        for a in affected_body_parts:  # looping through only the body parts we care about
                            if not a.cleared:
                                body_parts_present = list(u for u in unique_soreness_events if a.body_part == u[1] and a.side == u[2])
                                if len(body_parts_present) > 0:
                                    if a.last_reported_date is None:
                                        a.last_reported_date = body_parts_present[0][0]
                                        a.days_sore += 1
                                    else:
                                        a.days_sore += (body_parts_present[0][0].date() - a.last_reported_date.date()).days
                                        a.last_reported_date = body_parts_present[0][0]
                                    a.max_severity = max(a.max_severity, body_parts_present[0][3])
                                    # let's look at future loading events and update it's previous affected soreness
                                    future_loading_events = list(f for f in loading_events if f.loading_date > dt)
                                    if len(future_loading_events) > 0:
                                        f = future_loading_events[0]
                                        body_part_in_future = list(g for g in f.previous_affected_body_parts if g.body_part == a.body_part and g.side == a.side)
                                        if len(body_part_in_future) > 0:
                                            for p in body_part_in_future:
                                                if p.first_reported_date is not None:
                                                    p.first_reported_date = min(p.first_reported_date, body_parts_present[0][0])
                                                else:
                                                    p.first_reported_date = body_parts_present[0][0]
                                        else:
                                            previous_affected_part = AffectedBodyPart(a.body_part, a.side, a.days_sore, a.max_severity, a.cleared)
                                            previous_affected_part.first_reported_date = body_parts_present[0][0]
                                            f.previous_affected_body_parts.append(previous_affected_part)
                                elif a.days_sore > 0:
                                    a.cleared = True
                    # close out any soreness not cleared
                    for a in affected_body_parts:
                        if not a.cleared:
                            found = False
                            for d in self.doms:
                                if d.body_part == a.body_part and d.side == a.side:
                                    if loading_events[t].loading_date > d.last_reported_date:
                                        d.days_sore += (loading_events[t].loading_date - d.last_reported_date.date()).days
                                        d.last_reported_date = loading_events[t].loading_date
                                    found = True
                            if not found:
                                self.doms.append(a)
                            #a.cleared = True

                    # need to pick the oldest date for each body part
                    grouped_parts = []
                    grouper = attrgetter('body_part', 'side')
                    for k, g in groupby(sorted(affected_body_parts, key=grouper), grouper):
                        part_list = list(g)
                        part_list.sort(key=lambda x: x.last_reported_date)
                        grouped_parts.append(part_list[0])

                    loading_event.affected_body_parts = grouped_parts

            for loading_event in loading_events:

                level_one_soreness = list(
                    a for a in loading_event.affected_body_parts if a.cleared and a.days_sore <= 1)

                if len(loading_event.affected_body_parts) == len(level_one_soreness): # no soreness
                    self.no_soreness_load_tuples.append((loading_event.loading_date, loading_event.load))
                    if loading_event.loading_date >= last_2_4_week_date:
                        if loading_event.load / max_load <= .10:
                            if loading_event.sport_name not in self.recovery_loads:
                                self.recovery_loads[loading_event.sport_name] = []
                            self.recovery_loads[loading_event.sport_name].append(loading_event.load)
                        else:
                            if loading_event.sport_name not in self.maintenance_loads:
                                self.maintenance_loads[loading_event.sport_name] = []
                            self.maintenance_loads[loading_event.sport_name].append(loading_event.load)

                    if last_2_week_date - timedelta(days=3) > loading_event.loading_date >= last_2_4_week_date - timedelta(days=3):
                        self.no_soreness_load_tuples_last_2_4_weeks.append((loading_event.loading_date, loading_event.load))
                    if 0 <= (loading_event.loading_date - last_2_week_date - timedelta(days=3)).days <= 14:
                        self.no_soreness_load_tuples_last_2_weeks.append((loading_event.loading_date, loading_event.load))

                else:
                    self.soreness_load_tuples.append((loading_event.loading_date, loading_event.load))
                    if loading_event.loading_date >= last_2_4_week_date:
                        fo_soreness_list = list(a for a in loading_event.affected_body_parts if a.cleared and (a.max_severity <= 1 and
                                                             a.days_sore < 3))
                        if len(fo_soreness_list) > 0:
                            if loading_event.sport_name not in self.functional_overreaching_loads:
                                self.functional_overreaching_loads[loading_event.sport_name] = []
                            self.functional_overreaching_loads[loading_event.sport_name].append(loading_event.load)

                        fo_nfo_list = list(a for a in loading_event.affected_body_parts if a.cleared and (1 < a.max_severity or
                                                             a.days_sore > 2))

                        if len(fo_nfo_list) > 0:
                            if loading_event.sport_name not in self.functional_overreaching_NFO_loads:
                                self.functional_overreaching_NFO_loads[loading_event.sport_name] = []
                            self.functional_overreaching_NFO_loads[loading_event.sport_name].append(loading_event.load)

                if last_2_week_date - timedelta(days=3) > loading_event.loading_date >= last_2_4_week_date - timedelta(days=3):
                    self.load_tuples_last_2_4_weeks.append((loading_event.loading_date, loading_event.load))
                if 0 <= (loading_event.loading_date - last_2_week_date - timedelta(days=3)).days <= 14:
                    self.load_tuples_last_2_weeks.append((loading_event.loading_date, loading_event.load))

    def get_acwr(self, acute_load_error, chronic_load_error, factor=1.3):

        #standard_error_range = StandardErrorRangeMetric() not doing this now
        standard_error_range = StandardErrorRangeMetric()

        if acute_load_error.insufficient_data or chronic_load_error.insufficient_data:
            standard_error_range.insufficient_data = True

        if acute_load_error.observed_value is not None and chronic_load_error.observed_value is not None:
            if chronic_load_error.observed_value > 0:
                standard_error_range.observed_value = (acute_load_error.observed_value /
                                                       chronic_load_error.observed_value)
                #not doing this now
                #standard_error_range.observed_value_gap = (factor * chronic_load_error.observed_value) - acute_load_error.observed_value

        acwr_values = []
        # ignore all cases of lower_bound since we know the load could not be lower than observed
        # the following commenting out was for clarity and should be preserved
        #acwr_values = self.get_acwr_value(acwr_values, acute_load_error.lower_bound, chronic_load_error.lower_bound)
        #acwr_values = self.get_acwr_value(acwr_values, acute_load_error.lower_bound, chronic_load_error.observed_value)
        #acwr_values = self.get_acwr_value(acwr_values, acute_load_error.lower_bound, chronic_load_error.upper_bound)
        #acwr_values = self.get_acwr_value(acwr_values, acute_load_error.observed_value, chronic_load_error.lower_bound)
        acwr_values = self.get_acwr_value(acwr_values, acute_load_error.observed_value, chronic_load_error.upper_bound)
        #acwr_values = self.get_acwr_value(acwr_values, acute_load_error.upper_bound, chronic_load_error.lower_bound)
        acwr_values = self.get_acwr_value(acwr_values, acute_load_error.upper_bound, chronic_load_error.observed_value)
        acwr_values = self.get_acwr_value(acwr_values, acute_load_error.upper_bound, chronic_load_error.upper_bound)

        if len(acwr_values) > 0:
            min_value = min(acwr_values)
            max_value = max(acwr_values)
            if (standard_error_range.observed_value is not None
                    and (min_value < standard_error_range.observed_value)):
                standard_error_range.lower_bound = min_value
            if (standard_error_range.observed_value is not None
                    and (max_value > standard_error_range.observed_value)):
                standard_error_range.upper_bound = max_value
            if standard_error_range.observed_value is None:
                standard_error_range.lower_bound = min_value
                standard_error_range.upper_bound = max_value

        '''not doing this now
        gap_values = []
        # ignore all cases of lower_bound since we know the load could not be lower than observed
        # the following commenting out was for clarity and should be preserved
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.lower_bound, chronic_load_error.lower_bound, factor)
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.lower_bound, chronic_load_error.observed_value, factor)
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.lower_bound, chronic_load_error.upper_bound, factor)
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.observed_value, chronic_load_error.lower_bound, factor)
        gap_values = self.get_acwr_gap(gap_values, acute_load_error.observed_value, chronic_load_error.upper_bound, factor)
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.upper_bound, chronic_load_error.lower_bound, factor)
        gap_values = self.get_acwr_gap(gap_values, acute_load_error.upper_bound, chronic_load_error.observed_value, factor)
        gap_values = self.get_acwr_gap(gap_values, acute_load_error.upper_bound, chronic_load_error.upper_bound, factor)

        if len(gap_values) > 0:
            min_acwr = min(gap_values)
            max_acwr = max(gap_values)
            if (standard_error_range.observed_value_gap is not None
                    and (min_acwr < standard_error_range.observed_value_gap)):
                standard_error_range.lower_bound_gap = min_acwr
            if (standard_error_range.observed_value_gap is not None
                    and (max_acwr > standard_error_range.observed_value_gap)):
                standard_error_range.upper_bound_gap = max_acwr
            if standard_error_range.observed_value_gap is None:
                standard_error_range.lower_bound_gap = min_acwr
                standard_error_range.upper_bound_gap = max_acwr

        '''
        return standard_error_range

    def get_acwr_value(self, acwr_values, acute_load_value, chronic_load_value):

        if acute_load_value is not None and chronic_load_value is not None:
            if chronic_load_value > 0:
                acwr_values.append(acute_load_value/float(chronic_load_value))

        return acwr_values

    def get_acwr_gap(self, acwr_values, acute_load_value, chronic_load_value, factor=1.3):

        if acute_load_value is not None and chronic_load_value is not None:
            if chronic_load_value > 0:
                acwr_values.append((factor * chronic_load_value) - acute_load_value)

        return acwr_values

    '''deprecated for now
    def get_lower_training_volume_gap(self, gap_type, gaps):

        if len(gaps) == 0:
            return  None

        lower_training_volume_gap = TrainingVolumeGap(gap_type=gap_type)

        low_optimal_list = list(a.low_optimal_threshold for a in gaps if a.low_optimal_threshold is not None)
        high_optimal_list = list(a.high_optimal_threshold for a in gaps if a.high_optimal_threshold is not None)
        low_overreaching_list = list(
            a.low_overreaching_threshold for a in gaps if a.low_overreaching_threshold is not None)
        high_overreaching_list = list(
            a.high_overreaching_threshold for a in gaps if a.high_overreaching_threshold is not None)
        low_excessive_list = list(
            a.low_excessive_threshold for a in gaps if a.low_excessive_threshold is not None)
        high_excessive_list = list(
            a.high_excessive_threshold for a in gaps if a.high_excessive_threshold is not None)

        if len(low_optimal_list) > 0:
            lower_training_volume_gap.low_optimal_threshold = min(low_optimal_list)
        if len(high_optimal_list) > 0:
            lower_training_volume_gap.high_optimal_threshold = min(high_optimal_list)
        if len(low_overreaching_list) > 0:
            lower_training_volume_gap.low_overreaching_threshold = min(low_overreaching_list)
        if len(high_overreaching_list) > 0:
            lower_training_volume_gap.high_overreaching_threshold = min(high_overreaching_list)
        if len(low_excessive_list) > 0:
            lower_training_volume_gap.low_excessive_threshold = min(low_excessive_list)
        if len(high_excessive_list) > 0:
            lower_training_volume_gap.high_excessive_threshold = min(high_excessive_list)
        return lower_training_volume_gap

    def get_upper_training_volume_gap(self, gap_type, gaps):
        upper_training_volume_gap = TrainingVolumeGap(gap_type=gap_type)

        low_optimal_list = list(a.low_optimal_threshold for a in gaps if a.low_optimal_threshold is not None)
        high_optimal_list = list(a.high_optimal_threshold for a in gaps if a.high_optimal_threshold is not None)
        low_overreaching_list = list(
            a.low_overreaching_threshold for a in gaps if a.low_overreaching_threshold is not None)
        high_overreaching_list = list(
            a.high_overreaching_threshold for a in gaps if a.high_overreaching_threshold is not None)
        low_excessive_list = list(
            a.low_excessive_threshold for a in gaps if a.low_excessive_threshold is not None)
        high_excessive_list = list(
            a.high_excessive_threshold for a in gaps if a.high_excessive_threshold is not None)

        if len(low_optimal_list) > 0:
            upper_training_volume_gap.low_optimal_threshold = max(low_optimal_list)
        if len(high_optimal_list) > 0:
            upper_training_volume_gap.high_optimal_threshold = max(high_optimal_list)
        if len(low_overreaching_list) > 0:
            upper_training_volume_gap.low_overreaching_threshold = max(low_overreaching_list)
        if len(high_overreaching_list) > 0:
            upper_training_volume_gap.high_overreaching_threshold = max(high_overreaching_list)
        if len(low_excessive_list) > 0:
            upper_training_volume_gap.low_excessive_threshold = max(low_excessive_list)
        if len(high_excessive_list) > 0:
            upper_training_volume_gap.high_excessive_threshold = max(high_excessive_list)
        return upper_training_volume_gap
    '''
    def get_freshness_index(self, acute_load_error, chronic_load_error):

        standard_error_range = StandardErrorRange()

        if acute_load_error.insufficient_data or chronic_load_error.insufficient_data:
            standard_error_range.insufficient_data = True

        if acute_load_error.observed_value is not None and chronic_load_error.observed_value is not None:
            if chronic_load_error.observed_value > 0:
                standard_error_range.observed_value = (chronic_load_error.observed_value -
                                                       acute_load_error.observed_value)

        fresh_values = []

        if acute_load_error.observed_value is not None and chronic_load_error.upper_bound is not None:
            if chronic_load_error.upper_bound > 0:
                fresh_values.append(chronic_load_error.upper_bound - acute_load_error.observed_value)
        if acute_load_error.upper_bound is not None and chronic_load_error.upper_bound is not None:
            if chronic_load_error.upper_bound > 0:
                fresh_values.append(chronic_load_error.upper_bound - acute_load_error.upper_bound)
        if acute_load_error.upper_bound is not None and chronic_load_error.observed_value is not None:
            if chronic_load_error.observed_value > 0:
                fresh_values.append(chronic_load_error.observed_value - acute_load_error.upper_bound)

        if len(fresh_values) > 0:
            min_fresh = min(fresh_values)
            max_fresh = max(fresh_values)
            if (standard_error_range.observed_value is not None
                    and (min_fresh < standard_error_range.observed_value)):
                standard_error_range.lower_bound = min_fresh
            if (standard_error_range.observed_value is not None
                    and (max_fresh > standard_error_range.observed_value)):
                standard_error_range.upper_bound = max_fresh
            if standard_error_range.observed_value is None:
                standard_error_range.lower_bound = min_fresh
                standard_error_range.upper_bound = max_fresh

        return standard_error_range

    def get_strain(self, expected_weekly_workouts, monotony_error_range, last_week_values, historical_strain):

        load = self.get_standard_error_range(expected_weekly_workouts, last_week_values)

        #standard_error_range = StandardErrorRangeMetric() not doing this now
        standard_error_range = StandardErrorRange()

        if monotony_error_range.insufficient_data or load.insufficient_data:
            standard_error_range.insufficient_data = True

        if load.observed_value is not None and monotony_error_range.observed_value is not None:
            standard_error_range.observed_value = load.observed_value * monotony_error_range.observed_value

        '''not doing this now
        if len(historical_strain) > 0:

            strain_count = min(7, len(list(x.observed_value for x in historical_strain if x.observed_value is not None)))

            if strain_count > 1:
                strain_sd = statistics.stdev(
                    list(x.observed_value for x in historical_strain[-strain_count:] if x.observed_value is not None))
                strain_avg = statistics.mean(
                    list(x.observed_value for x in historical_strain[-strain_count:] if x.observed_value is not None))

                if historical_strain[len(
                        historical_strain) - 1] is not None and monotony_error_range.observed_value is not None and monotony_error_range.observed_value > 0:

                    # if the athlete strained, this wil be a negative number
                    # if positive, it reports the amount of load they have left without straining for the last practice
                    strain_surplus = (1.2 * strain_sd) + strain_avg - historical_strain[len(historical_strain)-1].observed_value
                    load_change = strain_surplus / monotony_error_range.observed_value
                    
                    standard_error_range.observed_value_gap = load_change
        '''

        strain_values = []
        # ignoring lower bounds since we know the load can't be lower than observed
        #strain_values = self.get_strain_value(strain_values, load.lower_bound, monotony_error_range.lower_bound)
        #strain_values = self.get_strain_value(strain_values, load.lower_bound, monotony_error_range.observed_value)
        #strain_values = self.get_strain_value(strain_values, load.lower_bound, monotony_error_range.upper_bound)
        #strain_values = self.get_strain_value(strain_values, load.observed_value, monotony_error_range.lower_bound)
        strain_values = self.get_strain_value(strain_values, load.observed_value, monotony_error_range.upper_bound)
        #strain_values = self.get_strain_value(strain_values, load.upper_bound, monotony_error_range.lower_bound)
        strain_values = self.get_strain_value(strain_values, load.upper_bound, monotony_error_range.observed_value)
        strain_values = self.get_strain_value(strain_values, load.upper_bound, monotony_error_range.upper_bound)

        if len(strain_values) > 0:
            min_strain_value = min(strain_values)
            max_strain_value = max(strain_values)

            if standard_error_range.observed_value is not None and min_strain_value < standard_error_range.observed_value:
                standard_error_range.lower_bound = min_strain_value
            if standard_error_range.observed_value is not None and max_strain_value > standard_error_range.observed_value:
                standard_error_range.upper_bound = max_strain_value
            if standard_error_range.observed_value is None:
                standard_error_range.lower_bound = min_strain_value
                standard_error_range.upper_bound = max_strain_value

        '''not doing gap analysis now
        gap_values = []
        # ignoring lower bounds since we know the load can't be lower than observed
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "lower_bound", monotony_error_range.lower_bound)
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "lower_bound", monotony_error_range.observed_value)
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "lower_bound", monotony_error_range.upper_bound)
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "observed_value", monotony_error_range.lower_bound)
        gap_values = self.get_strain_gap(gap_values, historical_strain, "observed_value", monotony_error_range.upper_bound)
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "upper_bound", monotony_error_range.lower_bound)
        gap_values = self.get_strain_gap(gap_values, historical_strain, "upper_bound", monotony_error_range.observed_value)
        gap_values = self.get_strain_gap(gap_values, historical_strain, "upper_bound", monotony_error_range.upper_bound)

        if len(gap_values) > 0:
            min_strain = min(gap_values)
            max_strain = max(gap_values)

            if standard_error_range.observed_value_gap is not None and min_strain < standard_error_range.observed_value_gap:
                standard_error_range.lower_bound_gap = min_strain
            if standard_error_range.observed_value_gap is not None and max_strain > standard_error_range.observed_value_gap:
                standard_error_range.upper_bound_gap = max_strain
            if standard_error_range.observed_value_gap is None:
                standard_error_range.lower_bound_gap = min_strain
                standard_error_range.upper_bound_gap = max_strain

        '''
        return standard_error_range

    def get_strain_value(self, strain_values, load_value, monotony_value):

        if load_value is not None and monotony_value is not None:
            strain_values.append(load_value * monotony_value)

        return strain_values

    def get_strain_gap(self, strain_values, historical_strain, strain_variable, monotony_value):

        if len(historical_strain) > 0:

            strain_count = min(7, len(list(getattr(x, strain_variable) for x in historical_strain if getattr(x, strain_variable) is not None)))

            if strain_count > 1:
                strain_sd = statistics.stdev(
                    list(getattr(x, strain_variable) for x in historical_strain[-strain_count:] if getattr(x, strain_variable) is not None))
                strain_avg = statistics.mean(
                    list(getattr(x, strain_variable) for x in historical_strain[-strain_count:] if getattr(x, strain_variable) is not None))

                if historical_strain[len(
                        historical_strain) - 1] is not None and monotony_value is not None and monotony_value > 0:

                    # if the athlete strained, this wil be a negative number
                    # if positive, it reports the amount of load they have left without straining for the last practice
                    strain_surplus = (1.2 * strain_sd) + strain_avg - historical_strain[len(historical_strain) - 1]
                    load_change = strain_surplus / monotony_value
                    strain_values.append(load_change)

        return strain_values

    def update_allowable_loads(self, strain_error_range):

        if strain_error_range.lower_bound is not None:
            strain = strain_error_range.lower_bound
        elif strain_error_range.observed_target is not None:
            strain = strain_error_range.observed_target
        elif strain_error_range.upper_bound is not None:
            strain = strain_error_range.upper_bound
        else:
            strain = None

        if strain is not None:
            if self.high_internal_load_day_upper_bound is not None and self.high_internal_load_day_upper_bound > strain:
                self.high_internal_load_day_upper_bound = strain
            if self.high_internal_load_day_lower_bound is not None and self.high_internal_load_day_lower_bound > strain:
                self.high_internal_load_day_lower_bound = None
                self.high_internal_load_day_upper_bound = None
            if self.mod_internal_load_day_upper_bound is not None and self.mod_internal_load_day_upper_bound > strain:
                self.mod_internal_load_day_upper_bound = strain
                self.high_internal_load_day_lower_bound = None
                self.high_internal_load_day_upper_bound = None

            if self.mod_internal_load_day_lower_bound is not None and self.mod_internal_load_day_lower_bound > strain:
                self.mod_internal_load_day_lower_bound = None
                self.mod_internal_load_day_upper_bound = None
            if self.low_internal_load_day_upper_bound is not None and self.low_internal_load_day_upper_bound > strain:
                self.low_internal_load_day_upper_bound = strain
            if self.low_internal_load_day_lower_bound is not None and self.low_internal_load_day_lower_bound > strain:
                self.low_internal_load_day_lower_bound = None
                self.low_internal_load_day_upper_bound = None

    def get_monotony(self, expected_weekly_workouts, values):

        standard_error_range = StandardErrorRangeMetric()

        if len(values) > 1:

            average_load = self.get_standard_error_range(expected_weekly_workouts, values, return_sum=False)

            stdev_load = statistics.stdev(values)

            if stdev_load > 0:

                if average_load.observed_value is not None:
                    standard_error_range.observed_value = average_load.observed_value / stdev_load

                if average_load.upper_bound is not None:
                    standard_error_range.upper_bound = average_load.upper_bound / stdev_load

                # ignore all cases of lower_bound since we know the load could not be lower than observed
                # the following commenting out was for clarity and should be preserved
                #if average_load.lower_bound is not None:
                #    standard_error_range.lower_bound = average_load.lower_bound / stdev_load

            '''ignoring monotony gaps as they structured differntly
            low_gaps = []
            high_gaps = []
            m3, m4 = self.get_monotony_gaps(average_load.observed_value, stdev_load)
            low_gaps.append(m3)
            high_gaps.append(m4)
            m5, m6 = self.get_monotony_gaps(average_load.upper_bound, stdev_load)
            low_gaps.append(m5)
            high_gaps.append(m6)

            low_gap = self.get_lower_training_volume_gap(TrainingVolumeGapType.monotony,
                                                         list(x for x in low_gaps if x is not None))
            high_gap = self.get_lower_training_volume_gap(TrainingVolumeGapType.monotony,
                                                          list(x for x in high_gaps if x is not None))

            if low_gap is not None:
                standard_error_range.training_volume_gaps.append(low_gap)

            if high_gap is not None:
                standard_error_range.training_volume_gaps.append(high_gap)
            '''
        else:
            standard_error_range.insufficient_data = True

        return standard_error_range

    def get_ramp(self, expected_weekly_workouts, last_week_values, previous_week_values, factor=1.1):

        current_load = self.get_standard_error_range(expected_weekly_workouts, last_week_values)
        previous_load = self.get_standard_error_range(expected_weekly_workouts, previous_week_values)

        #ramp_error_range = StandardErrorRangeMetric() this is for later
        ramp_error_range = StandardErrorRange()

        if current_load.insufficient_data or previous_load.insufficient_data:
            ramp_error_range.insufficient_data = True

        ramp_values = []
        # ignore all cases of lower_bound since we know the load could not be lower than observed
        # the following commenting out was for clarity and should be preserved
        #ramp_values = self.get_ramp_value(ramp_values, current_load.lower_bound, previous_load.lower_bound)
        #ramp_values = self.get_ramp_value(ramp_values, current_load.lower_bound, previous_load.observed_value)
        #ramp_values = self.get_ramp_value(ramp_values, current_load.lower_bound, previous_load.upper_bound)
        #ramp_values = self.get_ramp_value(ramp_values, current_load.observed_value, previous_load.lower_bound)
        ramp_values = self.get_ramp_value(ramp_values, current_load.observed_value, previous_load.upper_bound)
        #ramp_values = self.get_ramp_value(ramp_values, current_load.upper_bound, previous_load.lower_bound)
        ramp_values = self.get_ramp_value(ramp_values, current_load.upper_bound, previous_load.observed_value)
        ramp_values = self.get_ramp_value(ramp_values, current_load.upper_bound, previous_load.upper_bound)

        if (current_load.observed_value is not None and previous_load.observed_value is not None
                and previous_load.observed_value > 0):
            ramp_error_range.observed_value = current_load.observed_value / float(previous_load.observed_value)
            #not doing this now
            #ramp_error_range.observed_value_gap = (factor * previous_load.observed_value) - current_load.observed_value

        if len(ramp_values) > 0:
            min_value = min(ramp_values)
            max_value = max(ramp_values)
            if (ramp_error_range.observed_value is None or (ramp_error_range.observed_value is not None and
                                                            min_value < ramp_error_range.observed_value)):
                ramp_error_range.lower_bound = min_value

            if (ramp_error_range.observed_value is None or (ramp_error_range.observed_value is not None and
                                                            max_value > ramp_error_range.observed_value)):
                ramp_error_range.upper_bound = max_value

        '''not doing gap analysis for now
        gap_values = []
        # ignore all cases of lower_bound since we know the load could not be lower than observed
        # the following commenting out was for clarity and should be preserved
        #gap_values = self.get_ramp_gap(gap_values, current_load.lower_bound, previous_load.lower_bound, factor)
        #gap_values = self.get_ramp_gap(gap_values, current_load.lower_bound, previous_load.observed_value, factor)
        #gap_values = self.get_ramp_gap(gap_values, current_load.lower_bound, previous_load.upper_bound, factor)
        #gap_values = self.get_ramp_gap(gap_values, current_load.observed_value, previous_load.lower_bound, factor)
        gap_values = self.get_ramp_gap(gap_values, current_load.observed_value, previous_load.upper_bound, factor)
        #gap_values = self.get_ramp_gap(gap_values, current_load.upper_bound, previous_load.lower_bound, factor)
        gap_values = self.get_ramp_gap(gap_values, current_load.upper_bound, previous_load.observed_value, factor)
        gap_values = self.get_ramp_gap(gap_values, current_load.upper_bound, previous_load.upper_bound, factor)

        if len(gap_values) > 0:
            min_bound = min(gap_values)
            max_bound = max(gap_values)
            if (ramp_error_range.observed_value_gap is None or (ramp_error_range.observed_value_gap is not None and
                                                            min_bound < ramp_error_range.observed_value_gap)):
                ramp_error_range.lower_bound_gap = min_bound

            if (ramp_error_range.observed_value_gap is None or (ramp_error_range.observed_value_gap is not None and
                                                            max_bound > ramp_error_range.observed_value_gap)):
                ramp_error_range.upper_bound_gap = max_bound

        '''
        return ramp_error_range

    def get_ramp_value(self, values, current_load_value, previous_load_value):

        if (current_load_value is not None and previous_load_value is not None
                and previous_load_value > 0):
            values.append(current_load_value/float(previous_load_value))

        return values

    def get_ramp_gap(self, bound_values, current_load_value, previous_load_value, factor=1.10):

        if (current_load_value is not None and previous_load_value is not None
                and previous_load_value > 0):
            bound_values.append((factor * previous_load_value) - current_load_value)

        return bound_values

    def get_plan_session_attribute_sum(self, attribute_name, daily_plan_collection):

        sum_value = None

        values = []

        for c in daily_plan_collection:

            values.extend(self.get_values_for_session_attribute(attribute_name, c.training_sessions))
            #values.extend(self.get_values_for_session_attribute(attribute_name, c.practice_sessions))
            values.extend(self.get_values_for_session_attribute(attribute_name, c.strength_conditioning_sessions))
            #values.extend(self.get_values_for_session_attribute(attribute_name, c.games))
            #values.extend(self.get_values_for_session_attribute(attribute_name, c.bump_up_sessions))

        if len(values) > 0:
            sum_value = sum(values)

        return [sum_value]

    def get_plan_session_attribute_sum_list(self, attribute_name, daily_plan_collection):

        #sum_value = None

        values = []

        for c in daily_plan_collection:

            sub_values = []

            sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.training_sessions))
            #sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.practice_sessions))
            sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.strength_conditioning_sessions))
            #sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.games))
            #sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.bump_up_sessions))

            if len(sub_values) > 0:
                sum_value = sum(sub_values)
                values.append(sum_value)

        return values

    def get_session_attributes_product_sum_list(self, attribute_1_name, attribute_2_name, daily_plan_collection):

        # sum_value = None

        values = []

        for c in daily_plan_collection:

            sub_values = []

            sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                     c.training_sessions))
            #sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
            #                                                         c.practice_sessions))
            sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                     c.strength_conditioning_sessions))
            #sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
            #                                                         c.games))
            #sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
            #                                                         c.bump_up_sessions))
            if len(sub_values) > 0:
                sum_value = sum(sub_values)
                values.append(sum_value)

        return values

    def get_session_attributes_product_sum_tuple_list(self, attribute_1_name, attribute_2_name, daily_plan_collection):

        # sum_value = None

        values = []

        for c in daily_plan_collection:

            #sub_values = []

            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.training_sessions))
            #values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
            #                                                         c.practice_sessions))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.strength_conditioning_sessions))
            #values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
            #                                                         c.games))
            #values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
            #                                                         c.bump_up_sessions))
            #if len(sub_values) > 0:
            #    sum_value = sum(sub_values)
            #    values.append(sum_value)

        return values

    def get_session_attributes_product_sum(self, attribute_1_name, attribute_2_name, daily_plan_collection):

        sum_value = None

        values = []

        for c in daily_plan_collection:
            values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                 c.training_sessions))
            #values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
            #                                                     c.practice_sessions))
            values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                 c.strength_conditioning_sessions))
            #values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
            #                                                     c.games))
            #values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
            #                                                     c.bump_up_sessions))
        if len(values) > 0:
            sum_value = sum(values)

        return [sum_value]

    def get_values_for_session_attribute(self, attribute_name, session_collection):

        try:
            values = list(getattr(c, attribute_name) for c in session_collection if getattr(c, attribute_name) is not None)
            return values
        except:
            return []

    def get_product_of_session_attributes(self, attribute_1_name, attribute_2_name, session_collection):

        values = list(getattr(c, attribute_1_name) * getattr(c, attribute_2_name) for c in session_collection
                      if getattr(c, attribute_1_name) is not None and getattr(c, attribute_2_name) is not None)
        return values

    def get_tuple_product_of_session_attributes(self, event_date_time, attribute_1_name, attribute_2_name, session_collection):

        values = []
        values_list = list(getattr(c, attribute_1_name) * getattr(c, attribute_2_name) for c in session_collection
                      if getattr(c, attribute_1_name) is not None and getattr(c, attribute_2_name) is not None)
        for v in values_list:
            values.append((event_date_time, v))

        return values

    def get_historical_internal_strain(self, start_date, end_date, expected_weekly_workouts):

        target_dates = []

        weekly_expected_workouts = 5

        if expected_weekly_workouts is not None:
            weekly_expected_workouts = expected_weekly_workouts

        #all_plans.sort(key=lambda x: x.event_date)
        self.internal_load_tuples.sort(key=lambda x: x[0])

        date_diff = parse_date(end_date) - parse_date(start_date) + timedelta(days=1)  # include all days within start/end

        for i in range(0, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        index = 0
        strain_values = []
        strain_events = StandardErrorRange()

        # evaluates a rolling week's worth of values for each day to calculate "daily" strain
        avg_observed = None
        stdev_observed = None
        avg_upper = None
        stdev_upper = None
        obs_events = 0
        up_events = 0

        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_plans = [p for p in self.internal_load_tuples if (parse_date(start_date) + timedelta(index)) <= p[0] <= target_dates[t]]
                load_values.extend(x[1] for x in daily_plans if x is not None)
                strain = self.calculate_daily_strain(load_values, weekly_expected_workouts)

                if strain.observed_value is not None or strain.upper_bound is not None:
                    strain_values.append(strain)

                    if len(strain_values) > 1:
                        observed_values = list(o.observed_value for o in strain_values if o.observed_value is not None)
                        upper_values = list(o.upper_bound for o in strain_values if o.upper_bound is not None)

                        if 1 < len(observed_values):
                            if stdev_observed is not None and avg_observed is not None and strain.observed_value is not None:
                                if strain.observed_value >= ((1.2 * stdev_observed) + avg_observed):
                                    obs_events += 1
                            avg_observed = statistics.mean(observed_values)
                            stdev_observed = statistics.stdev(observed_values)

                            strain_events.observed_value = obs_events

                        if 1 < len(upper_values):
                            if stdev_upper is not None and avg_upper is not None and strain.upper_bound is not None:
                                if strain.upper_bound >= ((1.2 * stdev_upper) + avg_upper):
                                    up_events += 1
                            avg_upper = statistics.mean(upper_values)
                            stdev_upper = statistics.stdev(upper_values)

                            strain_events.upper_bound = up_events
                index += 1

        return strain_values, strain_events

    def get_historical_internal_monotony(self, start_date, end_date, expected_weekly_workouts):

        target_dates = []

        weekly_expected_workouts = 5

        if expected_weekly_workouts is not None:
            weekly_expected_workouts = expected_weekly_workouts

        self.internal_load_tuples.sort(key=lambda x: x[0])

        date_diff = parse_date(end_date) - parse_date(start_date)

        for i in range(1, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        index = 0
        monotony_values = []

        # evaluates a rolling week's worth of values for each day
        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_plans = [p for p in self.internal_load_tuples if (parse_date(start_date) + timedelta(index)) < p[0] <= target_dates[t]]
                load_values.extend(x[1] for x in daily_plans if x is not None)
                monotony = self.get_monotony(weekly_expected_workouts, load_values)

                if monotony.observed_value is not None or monotony.upper_bound is not None:
                    monotony_values.append(monotony)
                index += 1

        return monotony_values

    def calculate_daily_strain(self, load_values, expected_weekly_workouts):

        daily_strain = StandardErrorRange()

        weekly_expected_workouts = 5

        if expected_weekly_workouts is not None:
            weekly_expected_workouts = expected_weekly_workouts

        if len(load_values) > 1:

            current_load = sum(load_values)
            average_load = statistics.mean(load_values)
            stdev_load = statistics.stdev(load_values)
            stdev_load = max(stdev_load, 0.1)

            monotony = average_load / stdev_load
            daily_strain.observed_value = monotony * current_load

            if len(load_values) < weekly_expected_workouts:
                standard_error = (stdev_load / math.sqrt(len(load_values))) * math.sqrt(
                    (weekly_expected_workouts - len(load_values)) / weekly_expected_workouts)  # adjusts for finite population correction
                standard_error_range_factor = 1.96 * standard_error

                standard_error_high = average_load + standard_error_range_factor

                monotony_high = standard_error_high / stdev_load
                daily_strain.upper_bound = monotony_high * current_load

                # unlikely actual load is lower than observed value; ignoring for now
                #standard_error_low = average_load - standard_error_range_factor
                #monotony_low = standard_error_low / stdev_load
                #daily_strain.lower_bound = monotony_low * current_load

        return daily_strain

    '''deprecated
    def get_ramp_gap(self, current_load, previous_load):

        if current_load is None or previous_load is None:
            return None

        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.ramp)

        training_volume_gap.low_optimal_threshold = previous_load - current_load
        training_volume_gap.high_optimal_threshold = (1.10 * previous_load) - current_load
        training_volume_gap.low_overreaching_threshold = (1.11 * previous_load) - current_load
        training_volume_gap.high_overreaching_threshold = (1.15 * previous_load) - current_load
        training_volume_gap.low_excessive_threshold = (1.16 * previous_load) - current_load
        training_volume_gap.high_excessive_threshold = (1.16 * previous_load) - current_load

        return training_volume_gap

    def get_ramp_gap_old(self, current_load_values, previous_load_values, avg_workouts_week=5):

        current_load = 0
        current_load_high = 0
        previous_load = 0
        previous_load_high = 0

        if len(current_load_values) > 1:
            if len(current_load_values) < avg_workouts_week:
                average_load = statistics.mean(current_load_values)
                stdev_load = statistics.stdev(current_load_values)
                standard_error = (stdev_load / math.sqrt(len(current_load_values))) * math.sqrt(
                    (avg_workouts_week - len(current_load_values)) / avg_workouts_week)  # adjusts for finite population correction
                standard_error_range_factor = 1.96 * standard_error
                current_load_high = (average_load + standard_error_range_factor) * len(current_load_values)
            current_load = sum(current_load_values)

        if len(previous_load_values) > 1:
            if len(previous_load_values) < avg_workouts_week:
                average_load = statistics.mean(previous_load_values)
                stdev_load = statistics.stdev(previous_load_values)
                standard_error = (stdev_load / math.sqrt(len(previous_load_values))) * math.sqrt(
                    (avg_workouts_week - len(previous_load_values)) / avg_workouts_week)  # adjusts for finite population correction
                standard_error_range_factor = 1.96 * standard_error
                previous_load_high = (average_load + standard_error_range_factor) * len(previous_load_values)
            previous_load = sum(previous_load_values)

        #1.0 = current_load / previous_load
        #1.1* previous_load = current_load + gap
        #low_load = (1.0 * previous_load) + previous_load - current_load

        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.ramp)

        training_volume_gap.low_optimal_threshold = previous_load - current_load
        training_volume_gap.high_optimal_threshold = (1.10 * previous_load) - current_load
        training_volume_gap.low_overreaching_threshold = (1.11 * previous_load) - current_load
        training_volume_gap.high_overreaching_threshold = (1.15 * previous_load) - current_load
        training_volume_gap.low_excessive_threshold = (1.16 * previous_load) - current_load
        training_volume_gap.high_excessive_threshold = (1.16 * previous_load) - current_load
        if previous_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load_high - current_load)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                             (1.10 * previous_load_high) - current_load)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load_high) - current_load)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.15 * previous_load_high) - current_load)
            training_volume_gap.low_excessive_threshold = min(training_volume_gap.low_excessive_threshold,
                                                                 (1.16 * previous_load_high) - current_load)
            training_volume_gap.high_excessive_threshold = max(training_volume_gap.high_excessive_threshold,
                                                                  (1.16 * previous_load_high) - current_load)
        if current_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load - current_load_high)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                             (1.10 * previous_load) - current_load_high)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load) - current_load_high)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.15 * previous_load) - current_load_high)
            training_volume_gap.low_excessive_threshold = min(training_volume_gap.low_excessive_threshold,
                                                                 (1.16 * previous_load) - current_load_high)
            training_volume_gap.high_excessive_threshold = max(training_volume_gap.high_excessive_threshold,
                                                                  (1.16 * previous_load) - current_load_high)
        if previous_load_high > 0 and current_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load_high - current_load_high)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                             (1.10 * previous_load_high) - current_load_high)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load_high) - current_load_high)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.15 * previous_load_high) - current_load_high)
            training_volume_gap.low_excessive_threshold = min(training_volume_gap.low_excessive_threshold,
                                                                 (1.16 * previous_load_high) - current_load_high)
            training_volume_gap.high_excessive_threshold = max(training_volume_gap.high_excessive_threshold,
                                                                  (1.16 * previous_load_high) - current_load_high)

        return training_volume_gap
    '''
    '''deprecated for now
    def get_acute_chronic_durations(self, training_report, acute_start_date_time, acute_daily_plans, chronic_daily_plans):

        acute_values = []
        chronic_1_values = []
        chronic_2_values = []
        chronic_3_values = []
        chronic_4_values = []

        acute_days = len(acute_daily_plans)
        chronic_days = len(chronic_daily_plans)

        daily_plans = []
        daily_plans.extend(acute_daily_plans)
        daily_plans.extend(chronic_daily_plans)

        all_chronic_values = []
        all_chronic_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes", chronic_daily_plans) if x is not None)

        acute_values.extend(
            x for x in self.get_plan_session_attribute_sum_list("duration_minutes", acute_daily_plans) if x is not None)

        chronic_values = []

        if acute_days == 7 and chronic_days == 28:

            week4_sessions = [d for d in chronic_daily_plans if acute_start_date_time - timedelta(days=28) <=
                              d.get_event_datetime() < acute_start_date_time - timedelta(days=21)]

            chronic_4_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes", week4_sessions) if x is not None)
            chronic_values.append(sum(chronic_4_values))

        if acute_days == 7 and 21 <= chronic_days <= 28:

            week3_sessions = [d for d in chronic_daily_plans if acute_start_date_time
                              - timedelta(days=21) <= d.get_event_datetime() < acute_start_date_time -
                              timedelta(days=14)]

            chronic_3_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes", week3_sessions) if x is not None)
            chronic_values.append(sum(chronic_3_values))

        if acute_days == 7 and 14 <= chronic_days <= 28:

            week2_sessions = [d for d in chronic_daily_plans if acute_start_date_time
                              - timedelta(days=14) <= d.get_event_datetime() < acute_start_date_time -
                              timedelta(days=7)]

            chronic_2_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes", week2_sessions) if x is not None)
            chronic_values.append(sum(chronic_2_values))

        if acute_days <= 7 and 7 <= chronic_days <= 28:

            week1_sessions = [d for d in chronic_daily_plans if acute_start_date_time
                              - timedelta(days=7) <= d.get_event_datetime() < acute_start_date_time]

            chronic_1_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes",
                                                                        week1_sessions) if x is not None)

            chronic_values.append(sum(chronic_1_values))

        chronic_value = 0
        if len(chronic_values) > 0:
            chronic_value = statistics.mean(chronic_values)
            training_report.chronic_min_duration_minutes = min(all_chronic_values)
            training_report.chronic_max_duration_minutes = max(all_chronic_values)
            training_report.chronic_avg_duration_minutes = statistics.mean(all_chronic_values)
        training_report.chronic_duration_minutes = chronic_value

        acute_value = 0
        if len(acute_values) > 0:
            acute_value = sum(acute_values)
            training_report.acute_min_duration_minutes = min(acute_values)
            training_report.acute_max_duration_minutss = max(acute_values)
            training_report.acute_avg_duration_minutes = statistics.mean(acute_values)

        training_report.acute_duration_minutes = acute_value
        if training_report.chronic_duration_minutes > 0:
            training_report.acute_chronic_duration_minutes = training_report.acute_duration_minutes / training_report.chronic_duration_minutes

        return training_report
    '''
    '''deprecated
    def get_acwr_gap(self, acute_value, chronic_value):

        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.acwr)

        if acute_value is not None and chronic_value is not None and chronic_value > 0:

            training_volume_gap.low_optimal_threshold =(0.8 * chronic_value) - acute_value
            training_volume_gap.high_optimal_threshold = (1.3 * chronic_value) - acute_value
            training_volume_gap.low_overreaching_threshold = (1.31 * chronic_value) - acute_value
            training_volume_gap.high_overreaching_threshold = (1.50 * chronic_value) - acute_value
            training_volume_gap.low_excessive_threshold = (1.51 * chronic_value) - acute_value
            training_volume_gap.high_excessive_threshold = (1.51 * chronic_value) - acute_value

        return training_volume_gap

    def get_acwr_gap_old(self, acute_values, chronic_values, chronic_values_high, avg_workouts_week=5):

        chronic_value = 0
        chronic_high_value = 0
        acute_high = 0

        if len(chronic_values) > 0:
            chronic_value = statistics.mean(chronic_values)

        if len(chronic_values_high) > 0:
            chronic_high_value = statistics.mean(chronic_values_high)

        acute_value = 0
        if len(acute_values) > 0 or len(acute_values) >= avg_workouts_week:
            acute_value = sum(acute_values)
        if 1 < len(acute_values) < avg_workouts_week:
            average_load = statistics.mean(acute_values)
            stdev_load = statistics.stdev(acute_values)
            standard_error = (stdev_load / math.sqrt(len(acute_values))) * math.sqrt((avg_workouts_week-len(acute_values))/avg_workouts_week) #adjusts for finite population correction
            standard_error_range_factor = 1.96 * standard_error
            acute_high = (average_load + standard_error_range_factor) * len(acute_values)

        # ideal is 0.8 to 1.3 with 1.3 being ideal
        # low_difference = 0.8 = (acute_value + x) / chronic_value
        # 0.8 * chronic_value = acute_value + x
        # (0.8 * chronic_value) - acute_value = x

        training_volume_gaps = []
        training_volume_gaps.append(TrainingVolumeGap((0.8 * chronic_value) - acute_value,
                                                (1.31 * chronic_value) - acute_value,
                                                (1.51 * chronic_value) - acute_value, TrainingVolumeGapType.acwr))
        training_volume_gaps.append(TrainingVolumeGap((0.8 * chronic_high_value) - acute_value,
                                                  (1.31 * chronic_high_value) - acute_value,
                                                  (1.51 * chronic_high_value) - acute_value, TrainingVolumeGapType.acwr))

        training_volume_gaps.append(TrainingVolumeGap((0.8 * chronic_value) - acute_high,
                                                  (1.31 * chronic_value) - acute_high,
                                                  (1.51 * chronic_value) - acute_high, TrainingVolumeGapType.acwr))

        training_volume_gaps.append(TrainingVolumeGap((0.8 * chronic_high_value) - acute_high,
                                                  (1.31 * chronic_high_value) - acute_high,
                                                  (1.51 * chronic_high_value) - acute_high, TrainingVolumeGapType.acwr))

        optimal_list = list(t.low_optimal_threshold for t in training_volume_gaps if t is not None)
        overreaching_list = list(t.low_overreaching_threshold for t in training_volume_gaps if t is not None)
        excessive_list = list(t.low_excessive_threshold for t in training_volume_gaps if t is not None)
        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.acwr)
        if len(optimal_list) > 0:
            training_volume_gap.low_optimal_threshold = min(optimal_list)
            training_volume_gap.high_optimal_threshold = max(optimal_list)
        if len(overreaching_list) > 0:
            training_volume_gap.low_overreaching_threshold = min(overreaching_list)
            training_volume_gap.high_overreaching_threshold = max(overreaching_list)
        if len(excessive_list) > 0:
            training_volume_gap.low_excessive_threshold = min(excessive_list)
            training_volume_gap.high_excessive_threshold = max(excessive_list)

        return training_volume_gap
    '''
    '''deprecated
    def get_ewacwr_gap(self, acute_plans, chronic_plans):

        acute_value = 0
        chronic_value = 0
        #acute_n = len(acute_plans)
        #chronic_n = len(chronic_plans)
        acute_n = 7
        chronic_n = 28
        acute_value_sd = 0
        chronic_value_sd = 0
        n = 1
        for a in acute_plans:
            acute_value = (2/(acute_n + 1)) * a[1] + ((1 - (2/(acute_n + 1))) * acute_value)
            w = float(2/float((acute_n + 1)))
            acute_value_sd = math.sqrt(w * ((float(a[1]) - float(acute_value))**2) + ((1-w)*(acute_value_sd**2)))
            standard_error = acute_value_sd / math.sqrt(n)
            standard_error_range_factor = 1.96 * standard_error
            acute_low = acute_value - standard_error_range_factor
            acute_high = acute_value + standard_error_range_factor
            n += 1

        n = 1
        for c in chronic_plans:
            chronic_value = (2 / (chronic_n + 1)) * c[1] + ((1 - (2 / (chronic_n + 1))) * chronic_value)
            w = float(2/float((chronic_n + 1)))
            chronic_value_sd = math.sqrt(w * ((float(c[1]) - float(chronic_value))**2) + ((1-w)*(chronic_value**2)))
            standard_error = chronic_value_sd / math.sqrt(n)
            standard_error_range_factor = 1.96 * standard_error
            chronic_low = chronic_value - standard_error_range_factor
            chronic_high = chronic_value + standard_error_range_factor
            n += 1
        # ideal is 0.8 to 1.3 with 1.3 being ideal
        # low_difference = 0.8 = (acute_value + x) / chronic_value
        # 0.8 * chronic_value = acute_value + x
        # (0.8 * chronic_value) - acute_value = x

        ac_1 = acute_low / chronic_high
        ac_2 = acute_high / chronic_low
        ac_3 = acute_low / chronic_low
        ac_4 = acute_high / chronic_high

        training_volume_gap = TrainingVolumeGap((0.8 * chronic_value) - acute_value,
                                                (1.31 * chronic_value) - acute_value,
                                                (1.51 * chronic_value) - acute_value, TrainingVolumeGapType.acwr)

        return training_volume_gap
    '''
    '''deprecated
    def get_training_report(self, athlete_stats, new_stats_processing, avg_workouts_week=5):

        user_id = athlete_stats.athlete_id
        historical_internal_strain = athlete_stats.historical_internal_strain
        acute_days = new_stats_processing.acute_days
        chronic_days = new_stats_processing.chronic_days
        acute_start_date_time = new_stats_processing.acute_start_date_time
        chronic_start_date_time = new_stats_processing.chronic_start_date_time
        end_date_time = new_stats_processing.end_date_time
        daily_plans = new_stats_processing.daily_internal_plans

        report = TrainingReport(user_id=user_id)

        #report.internal_monotony_index = athlete_stats.internal_monotony
        #report = self.calc_need_for_variability(athlete_stats.internal_monotony, report)

        suggested_training_days = []

        target_load = 0

        #for index in range(0, 7):
        for index in range(0, 1): # just doing one day now

            chronic_values = []
            chronic_values_high = []
            #chronic_1_values = []
            #chronic_2_values = []
            #chronic_3_values = []
            #chronic_4_values = []

            #new_acute_start_date_time = acute_start_date_time + timedelta(days=1) + timedelta(days=index)
            #new_chronic_start_date_time = chronic_start_date_time + timedelta(days=1) + timedelta(days=index)

            acute_values = new_stats_processing.get_acute_internal_values()
            chronic_values_by_week = new_stats_processing.get_chronic_daily_values_by_week()

            #new_chronic_daily_plans = sorted([p for p in daily_plans if new_acute_start_date_time > p[0] >=
            #                                  new_chronic_start_date_time], key=lambda x: x[0])

            #week4_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=28)
            #                  <= d[0] < new_acute_start_date_time - timedelta(days=21)]

            #chronic_4_values.extend(x[1] for x in week4_sessions if x[1] is not None)

            se_range_chronic_4 = self.get_standard_error_range(avg_workouts_week, chronic_values_by_week[3])
            if not se_range_chronic_4.insufficient_data and se_range_chronic_4.upper_bound is not None:
                chronic_values_high.append(se_range_chronic_4.upper_bound*len(chronic_values_by_week[3]))
            if se_range_chronic_4.observed_value is not None:
                chronic_values.append(se_range_chronic_4.observed_value)

            #week3_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=21)
            #                  <= d[0] < new_acute_start_date_time - timedelta(days=14)]

            #chronic_3_values.extend(x[1] for x in week3_sessions if x[1] is not None)
            se_range_chronic_3 = self.get_standard_error_range(avg_workouts_week, chronic_values_by_week[2])
            if se_range_chronic_3.observed_value is not None:
                chronic_values.append(se_range_chronic_3.observed_value)
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if not se_range_chronic_3.insufficient_data and se_range_chronic_3.upper_bound is not None:
                chronic_values_high.append(se_range_chronic_3.upper_bound*len(chronic_values_by_week[2]))
            else:
                if len(chronic_values_high) > 0:
                    chronic_values_high.append(0)

            #week2_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=14)
            #                  <= d[0] < new_acute_start_date_time - timedelta(days=7)]

            #chronic_2_values.extend(x[1] for x in week2_sessions if x[1] is not None)
            se_range_chronic_2 = self.get_standard_error_range(avg_workouts_week, chronic_values_by_week[1])
            if se_range_chronic_2.observed_value is not None:
                chronic_values.append(se_range_chronic_2.observed_value)
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if not se_range_chronic_2.insufficient_data and se_range_chronic_2.upper_bound is not None:
                chronic_values_high.append(se_range_chronic_2.upper_bound*len(chronic_values_by_week[1]))
            else:
                if len(chronic_values_high) > 0:
                    chronic_values_high.append(0)

            #week1_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=7)
            #                  <= d[0] < new_acute_start_date_time]

            #chronic_1_values.extend(x[1] for x in week1_sessions if x[1] is not None)

            se_range_chronic_1 = self.get_standard_error_range(avg_workouts_week, chronic_values_by_week[0])
            if se_range_chronic_1.observed_value is not None:
                chronic_values.append(se_range_chronic_1.observed_value)
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if not se_range_chronic_1.insufficient_data and se_range_chronic_1.upper_bound is not None:
                chronic_values_high.append(se_range_chronic_1.upper_bound*len(chronic_values_by_week[0]))
            else:
                if len(chronic_values_high) > 0:
                    chronic_values_high.append(0)

            last_6_internal_load_values = []
            last_7_internal_load_values = []
            last_7_13_internal_load_values = []

            last_six_days = end_date_time - timedelta(days=6 + 1) + timedelta(days=index)
            last_seven_days = end_date_time - timedelta(days=7 + 1) + timedelta(days=index)
            thirteen_days_ago = last_six_days - timedelta(days=7)

            last_6_day_plans = [p for p in daily_plans if p[0] >= last_six_days]
            last_7_day_plans = [p for p in daily_plans if p[0] >= last_seven_days]
            last_7_day_plans.sort(key=lambda x: x[0], reverse=False)

            last_7_13_day_plans = [p for p in daily_plans if thirteen_days_ago <= p[0] < last_six_days]

            last_6_internal_load_values.extend(x[1] for x in last_6_day_plans if x[1] is not None)
            #last_6_internal_load_values.extend(list(x.target_load for x in suggested_training_days))

            last_7_internal_load_values.extend(x[1] for x in last_7_day_plans if x[1] is not None)

            last_7_13_internal_load_values.extend(x[1] for x in last_7_13_day_plans if x[1] is not None)

            #current_load = sum(last_6_internal_load_values)
            #previous_load = sum(last_7_13_internal_load_values)
            #ramp_load = previous_load
            if len(chronic_values) > 0:
                average_chronic_load = statistics.mean(chronic_values)
                #ramp_load = max(average_chronic_load, ramp_load)
            ramp_gap = self.get_ramp_gap(last_6_internal_load_values, last_7_13_internal_load_values, avg_workouts_week)

            low_monotony_gap, high_monotony_gap,  = self.get_monotony_gap(last_6_internal_load_values, avg_workouts_week)

            strain_gap = self.get_strain_gap(historical_internal_strain, last_7_internal_load_values, avg_workouts_week)

            acwr_gap = self.get_acwr_gap(acute_values, chronic_values, chronic_values_high, avg_workouts_week)
            #acwr_gap = self.get_ewacwr_gap(new_acute_daily_plans, new_chronic_daily_plans)

            gap_list = [ramp_gap, strain_gap, acwr_gap]

            suggested_training_day = self.compile_training_report(user_id, end_date_time + timedelta(days=index), gap_list, low_monotony_gap, high_monotony_gap)
            #if min(suggested_training_day.high_threshold - suggested_training_day.low_threshold, target_load) < 30:
            #    suggested_training_day.target_load = 0
            #else:
            #    if target_load > 0:
            #        suggested_training_day.target_load = min(suggested_training_day.high_threshold - suggested_training_day.low_threshold, target_load)
            #    else:
            #        suggested_training_day.target_load = suggested_training_day.high_threshold - suggested_training_day.low_threshold
            suggested_training_day.target_load = 0
            suggested_training_days.append(suggested_training_day)
            matching_workouts = list(d for d in daily_plans if d[1]<suggested_training_day.low_overreaching_threshold)
            matching_workouts.sort(key=lambda x: x[1], reverse=True)
            suggested_training_day.matching_workouts = matching_workouts
            daily_plans.append((suggested_training_day.date_time, suggested_training_day.target_load))
            internal_monotony = 0
            #if chronic_days < 28:
            #    chronic_days += 1
            if len(last_7_internal_load_values) > 0:
                new_strain = self.calculate_daily_strain(last_7_internal_load_values)
                if len(historical_internal_strain) > 0:
                    del historical_internal_strain[0]
                if new_strain is not None:
                    historical_internal_strain.append(new_strain)
                new_average_load = statistics.mean(last_7_internal_load_values)
                if len(last_7_internal_load_values) > 1:
                    new_stdev_load = statistics.stdev(last_7_internal_load_values)

                    if new_stdev_load > 0:
                        internal_monotony = new_average_load / new_stdev_load

        report.suggested_training_days = suggested_training_days


        return report
    '''

    def get_standard_error_range(self, expected_workouts_week, values, return_sum=True):

        standard_error_range = StandardErrorRange()

        expected_workouts = 5

        if expected_workouts_week is not None:
            expected_workouts = expected_workouts_week

        if len(values) > 0:
            standard_error_range.observed_value = sum(values)

        if 1 < len(values) < expected_workouts:
            average_value = statistics.mean(values)
            stdev = statistics.stdev(values)
            standard_error = (stdev / math.sqrt(len(values))) * math.sqrt(
                (expected_workouts - len(values)) / expected_workouts)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            if return_sum:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor) * len(values)
                standard_error_range.lower_bound = (average_value - standard_error_range_factor) * len(values)
            else:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor)
                standard_error_range.lower_bound = (average_value - standard_error_range_factor)
        elif 1 == len(values) < expected_workouts:
            #let'a quick manufacture some data
            fake_values = []
            fake_values.extend(values)
            fake_values.append(values[0] * 1.5)
            average_value = statistics.mean(fake_values)
            stdev = statistics.stdev(fake_values)
            standard_error = (stdev / math.sqrt(len(fake_values))) * math.sqrt(
                (expected_workouts - len(fake_values)) / expected_workouts)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            if return_sum:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor) * len(fake_values)
                standard_error_range.lower_bound = (average_value - standard_error_range_factor) * len(fake_values)
            else:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor)
                standard_error_range.lower_bound = (average_value - standard_error_range_factor)

        elif len(values) == 0:
            standard_error_range.insufficient_data = True

        return standard_error_range
    '''deprecated for now
    def calc_need_for_variability(self, internal_monotony, report):

        if internal_monotony is not None:
            if internal_monotony > 2:
                report.need_for_variability = IndicatorLevel.high
                # report.training_level = TrainingLevel.overreaching - how should we summarize?

            elif 1.3 < internal_monotony <= 2:
                report.need_for_variability = IndicatorLevel.moderate

            elif internal_monotony <= 1.3:
                report.need_for_variability = IndicatorLevel.low

        else:
            report.need_for_variability = IndicatorLevel.low

        return report
    '''
    '''deprecated for now
    def calc_report_stats(self, acute_plans, acute_start_date_time, athlete_stats, chronic_plans, report):
        report.internal_acwr = athlete_stats.internal_acwr
        report.internal_freshness_index = athlete_stats.internal_freshness_index
        report.competition_focused = (report.internal_freshness_index > 0)
        report.performance_focused = (report.internal_freshness_index <= 0)
        if athlete_stats.internal_acwr is not None:
            if athlete_stats.internal_acwr < 0.8:
                report.training_level = TrainingLevel.undertraining
            elif 0.8 <= athlete_stats.internal_acwr <= 1.3:
                report.training_level = TrainingLevel.optimal
            elif 1.3 < athlete_stats.internal_acwr <= 1.5:
                report.training_level = TrainingLevel.overreaching
            elif athlete_stats.internal_acwr > 1.5:
                report.training_level = TrainingLevel.excessive
        report.internal_strain = athlete_stats.internal_strain
        report.internal_ramp = athlete_stats.internal_ramp
        report = self.get_acute_chronic_workout_characteristics(report, acute_plans, chronic_plans)
        report = self.get_acute_chronic_durations(report, acute_start_date_time, acute_plans, chronic_plans)
        report.historic_soreness = list(h for h in athlete_stats.historic_soreness if
                                        h.historic_soreness_status is not HistoricSorenessStatus.dormant_cleared)
        severity_list = list(h.average_severity for h in report.historic_soreness)
        if len(severity_list) > 0:
            report.low_hs_severity = min(severity_list)
            report.high_hs_severity = max(severity_list)
            report.average_hs_severity = statistics.mean(severity_list)
        return report

    def get_acute_chronic_workout_characteristics(self, training_report, acute_plans, chronic_plans):

        acute_rpes = []
        chronic_rpes = []

        acute_rpes.extend(
            x for x in self.get_plan_session_attribute_sum_list("session_RPE", acute_plans) if x is not None)
        chronic_rpes.extend(
            x for x in self.get_plan_session_attribute_sum_list("session_RPE", chronic_plans) if x is not None)

        if len(acute_rpes) > 0:
            training_report.acute_min_rpe = min(acute_rpes)
            training_report.acute_max_rpe = max(acute_rpes)
            training_report.acute_avg_rpe = statistics.mean(acute_rpes)
        if len(chronic_rpes) > 0:
            training_report.chronic_min_rpe = min(chronic_rpes)
            training_report.chronic_max_rpe = max(chronic_rpes)
            training_report.chronic_avg_rpe = statistics.mean(chronic_rpes)

        if training_report.acute_avg_rpe is not None and training_report.chronic_avg_rpe is not None and training_report.chronic_avg_rpe > 0:
            training_report.rpe_acwr = training_report.acute_avg_rpe / training_report.chronic_avg_rpe

        return training_report
    '''
    '''holding off for now; not sure this is the best way to capture monotony
    def get_monotony_gaps(self, average_load, stdev_load):

        if average_load is None or stdev_load is None or stdev_load == 0:
            return None, None

        low_monotony_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.monotony)
        low_monotony_gap.low_optimal_threshold = average_load - (1.10 * stdev_load)
        low_monotony_gap.high_optimal_threshold = average_load - (1.01 * stdev_load)

        high_montony_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.monotony)
        high_montony_gap.low_optimal_threshold = average_load + (1.01 * stdev_load)
        high_montony_gap.high_optimal_threshold = average_load + (1.10 * stdev_load)

        return low_monotony_gap, high_montony_gap

    def get_monotony_gap(self, last_6_internal_load_values, avg_workouts_week=5):

        # what is the monotony if we have a workout with this load?
        average_load = 0
        high_average_load = 0

        if len(last_6_internal_load_values) > 0:
            average_load = statistics.mean(last_6_internal_load_values)
        if len(last_6_internal_load_values) > 1:
            fpc = max(avg_workouts_week, len(last_6_internal_load_values))
            stdev_load = statistics.stdev(last_6_internal_load_values)
            standard_error = (stdev_load / math.sqrt(len(last_6_internal_load_values))) * math.sqrt(
                (fpc - len(last_6_internal_load_values)) / fpc)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            high_average_load = average_load + standard_error_range_factor

        stdev_load = 0
        if len(last_6_internal_load_values) > 1:
            stdev_load = statistics.stdev(last_6_internal_load_values)

        if stdev_load > 0:
            internal_monotony = average_load / stdev_load
            internal_monotony_high = high_average_load / stdev_load
        else:
            internal_monotony = 0
            internal_monotony_high = 0
        # monotony = weekly mean total load/weekly standard deviation of load
        # In order to increase the standard deviation of a set of numbers, you must add a value that is more than
        # one standard deviation away from the mean
        low_overreaching_fix = None
        high_overreaching_fix = None
        low_excessive_fix = None
        high_excessive_fix = None
        if 1.7 < internal_monotony < 2.0:
            low_overreaching_fix = average_load - (1.05 * stdev_load)
            high_overreaching_fix = average_load + (1.05 * stdev_load)
        elif internal_monotony >= 2.0:
            low_excessive_fix = average_load - (1.05 * stdev_load)
            high_excessive_fix = average_load + (1.05 * stdev_load)
        low_monotony_gap_low = TrainingVolumeGap(None, low_overreaching_fix, low_excessive_fix, TrainingVolumeGapType.monotony)
        high_monotony_gap_low = TrainingVolumeGap(None, high_overreaching_fix, high_excessive_fix, TrainingVolumeGapType.monotony)

        low_overreaching_fix = None
        high_overreaching_fix = None
        low_excessive_fix = None
        high_excessive_fix = None
        if 1.7 < internal_monotony_high < 2.0:
            low_overreaching_fix = high_average_load - (1.05 * stdev_load)
            high_overreaching_fix = high_average_load + (1.05 * stdev_load)
        elif internal_monotony_high >= 2.0:
            low_excessive_fix = high_average_load - (1.05 * stdev_load)
            high_excessive_fix = high_average_load + (1.05 * stdev_load)
        low_monotony_gap_high = TrainingVolumeGap(None, low_overreaching_fix, low_excessive_fix,
                                             TrainingVolumeGapType.monotony)
        high_monotony_gap_high = TrainingVolumeGap(None, high_overreaching_fix, high_excessive_fix,
                                              TrainingVolumeGapType.monotony)

        low_monotony_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.monotony)
        low_monotony_gap.low_overreaching_threshold = low_monotony_gap_low.low_overreaching_threshold
        low_monotony_gap.high_overreaching_threshold = low_monotony_gap_high.low_overreaching_threshold
        low_monotony_gap.low_excessive_threshold = low_monotony_gap_low.low_excessive_threshold
        low_monotony_gap.high_excessive_threshold = low_monotony_gap_high.low_excessive_threshold

        high_monotony_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.monotony)
        high_monotony_gap.low_overreaching_threshold = high_monotony_gap_low.low_overreaching_threshold
        high_monotony_gap.high_overreaching_threshold = high_monotony_gap_high.low_overreaching_threshold
        high_monotony_gap.low_excessive_threshold = high_monotony_gap_low.low_excessive_threshold
        high_monotony_gap.high_excessive_threshold = high_monotony_gap_high.low_excessive_threshold

        #low_monotony_gap.training_level = None
        #high_monotony_gap.training_level = None

        return low_monotony_gap, high_monotony_gap
    '''
    '''deprecated for now
    def get_training_recs(self, acwr, ramp):

        # first calc the integrated range between acwr and ramp

        lower_target = self.get_min(acwr.lower_bound, ramp.lower_bound)
        observed_target = self.get_min(acwr.observed_target, ramp.observed_target)
        upper_target = self.get_min(acwr.upper_bound, ramp.upper_bound)

        low_days_resolve = 0
        mod_days_resolve = 0
        high_days_resolve = 0

        if upper_target is not None:
            target = upper_target
            for d in range(0,8):
                if target >= self.low_internal_load_day_lower_bound and target <= self.low_internal_load_day_upper_bound:
                    low_days_resolve += 1
                    target = target - self.get_min(target, self.low_internal_load_day_upper_bound)
                elif target > self.low_internal_load_day_lower_bound and upper_target <= self.mod_internal_load_day_upper_bound:
                    mod_days_resolve += 1
                    target = target - self.get_min(target, self.mod_internal_load_day_upper_bound)
                elif target > self.mod_internal_load_day_upper_bound:
                    high_days_resolve += 1
                    target = target - self.get_min(target, self.high_internal_load_day_upper_bound)
                elif target <= 0:
                    break
    '''

    def get_min(self, value_1, value_2):

        if value_1 is not None and value_2 is None:
            min_val = value_1
        elif value_1 is None and value_2 is not None:
            min_val = value_2
        elif value_1 is not None and value_2 is not None:
            min_val = min(value_1, value_2)
        else:
            min_val = None

        return min_val

    '''deprecated for now
    def get_training_status(self, metrics_list):

        gaps = []
        monotony_gaps = []

        for m in metrics_list:
            for t in m.training_volume_gaps:
                if t.training_volume_gap_type is not TrainingVolumeGapType.monotony:
                    gaps.append(t)
                else:
                    monotony_gaps.append(t)

        opt_low_values = []
        opt_high_values = []
        ovr_low_values = []
        ovr_high_values = []
        exc_low_values = []
        exc_high_values = []

        monotony_gaps.sort(key=lambda x: x.low_optimal_threshold, reverse=False)

        if len(monotony_gaps) > 0:
            low_monotony_gap = monotony_gaps[0]
        else:
            low_monotony_gap = None
        if len(monotony_gaps) > 1:
            high_monotony_gap = monotony_gaps[1]
        else:
            high_monotony_gap = None

        opt_low_values.extend(list(g for g in gaps if g.low_optimal_threshold is not None))
        opt_low_values.sort(key=lambda x: x.low_optimal_threshold, reverse=False)

        opt_high_values.extend(list(g for g in gaps if g.high_optimal_threshold is not None))
        opt_high_values.sort(key=lambda x: x.high_optimal_threshold, reverse=False)

        ovr_low_values.extend(list(g for g in gaps if g.low_overreaching_threshold is not None))
        ovr_low_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)

        ovr_high_values.extend(list(g for g in gaps if g.high_overreaching_threshold is not None))
        ovr_high_values.sort(key=lambda x: x.high_overreaching_threshold, reverse=False)

        exc_low_values.extend(list(g for g in gaps if g.low_excessive_threshold is not None))
        exc_low_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)

        exc_high_values.extend(list(g for g in gaps if g.high_excessive_threshold is not None))
        exc_high_values.sort(key=lambda x: x.high_excessive_threshold, reverse=False)

        # this number needs to be consistent with monotony.  Should we use the low or high?
        if (high_monotony_gap is not None and high_monotony_gap.low_overreaching_threshold is not None and
                ovr_low_values[0].low_overreaching_threshold < high_monotony_gap.low_overreaching_threshold):
            ovr_low_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony

        else:
            if high_monotony_gap is not None and high_monotony_gap.low_overreaching_threshold is not None:
                ovr_low_values.append(high_monotony_gap)

        # this number needs to be consistent with monotony.  Should we use the low or high?
        if (high_monotony_gap is not None and high_monotony_gap.low_excessive_threshold is not None and
                exc_low_values[0].low_excessive_threshold < high_monotony_gap.low_excessive_threshold):
            exc_low_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony
        else:
            if high_monotony_gap is not None and high_monotony_gap.low_excessive_threshold is not None:
                exc_low_values.append(high_monotony_gap)

        # re-sort
        ovr_low_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)
        exc_low_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)

        low_optimal = None
        high_optimal = None
        low_overreaching = None
        high_overreaching = None
        low_excessive = None
        high_excessive = None

        if len(opt_low_values) > 0:
            low_optimal = opt_low_values[0].low_optimal_threshold

        if len(opt_high_values) > 0:
            high_optimal = opt_high_values[0].high_optimal_threshold

        if len(ovr_low_values) > 0:
            low_overreaching = ovr_low_values[0].low_overreaching_threshold

        if len(ovr_high_values) > 0:
            high_overreaching = ovr_high_values[0].high_overreaching_threshold

        if len(exc_low_values) > 0:
            low_excessive = exc_low_values[0].low_excessive_threshold

        if len(exc_high_values) > 0:
            high_excessive = exc_high_values[0].high_excessive_threshold

        training_level = TrainingLevel.insufficient_data
        most_limiting = None

        if (high_optimal is not None and low_optimal is not None and high_optimal > low_optimal and
                high_optimal - low_optimal > 0):
            training_level = TrainingLevel.optimal
            most_limiting = opt_low_values[0]

        if low_optimal is not None and low_optimal > 0:
            training_level = TrainingLevel.undertraining
            most_limiting = opt_low_values[0]

        if high_optimal is not None and low_overreaching is not None and low_overreaching < high_optimal:
            training_level = TrainingLevel.possibly_overreaching
            most_limiting = ovr_low_values[0]

        if high_optimal is not None and high_optimal < 0:
            training_level = TrainingLevel.overreaching
            most_limiting = ovr_low_values[0]

        if high_overreaching is not None and low_excessive is not None and low_excessive < high_overreaching:
            training_level = TrainingLevel.possibly_excessive
            most_limiting = exc_low_values[0]

        if high_overreaching is not None and high_overreaching < 0:
            training_level = TrainingLevel.excessive
            most_limiting = exc_low_values[0]

        status = TrainingStatus(training_level)
        status.limiting_metric = most_limiting

        return status
    '''
    '''deprecated for now
    def compile_training_report(self, user_id, date_time, gap_list, low_monotony_gap, high_monotony_gap):

        #min_values = []
        #max_values = []
        opt_values = []
        opt_high_values = []
        ovr_values = []
        ovr_high_values = []
        exc_values = []
        exc_high_values = []

        # we want the lowest high threshold
        #max_values.extend(list(g for g in gap_list if g.high_threshold is not None))
        #max_values.sort(key=lambda x: x.high_threshold, reverse=False)

        opt_values.extend(list(g for g in gap_list if g.low_optimal_threshold is not None))
        opt_values.sort(key=lambda x: x.low_optimal_threshold, reverse=False)

        opt_high_values.extend(list(g for g in gap_list if g.high_optimal_threshold is not None))
        opt_high_values.sort(key=lambda x: x.high_optimal_threshold, reverse=False)

        ovr_values.extend(list(g for g in gap_list if g.low_overreaching_threshold is not None))
        ovr_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)

        ovr_high_values.extend(list(g for g in gap_list if g.high_overreaching_threshold is not None))
        ovr_high_values.sort(key=lambda x: x.high_overreaching_threshold, reverse=False)

        exc_values.extend(list(g for g in gap_list if g.low_excessive_threshold is not None))
        exc_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)

        exc_high_values.extend(list(g for g in gap_list if g.high_excessive_threshold is not None))
        exc_high_values.sort(key=lambda x: x.high_excessive_threshold, reverse=False)

        # this number needs to be consistent with monotony.  Should we use the low or high?
        if high_monotony_gap.low_overreaching_threshold is not None and ovr_values[0].low_overreaching_threshold < high_monotony_gap.low_overreaching_threshold:
            ovr_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony

        else:
            if high_monotony_gap.low_overreaching_threshold is not None:
                ovr_values.append(high_monotony_gap)

        # this number needs to be consistent with monotony.  Should we use the low or high?
        if high_monotony_gap.low_excessive_threshold is not None and exc_values[0].low_excessive_threshold < high_monotony_gap.low_excessive_threshold:
            exc_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony
        else:
            if high_monotony_gap.low_excessive_threshold is not None:
                exc_values.append(high_monotony_gap)

        # re-sort
        ovr_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)
        exc_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)

        #high_threshold_gap = max_values[0]

        #min_values.extend(list(g for g in gap_list if g.low_threshold is not None and g.low_threshold < high_threshold_gap.high_threshold))

        #min_values.sort(key=lambda x: x.low_threshold,
        #                reverse=True)  # I think we want the highest min value for the tightest band that is lower than the high_threshold

        #if len(min_values) > 0:
            # we want the highest low threshold
        #    low_threshold_gap = min_values[0]
        #else:
        #    low_threshold_gap = max_values[0]

        #report = TrainingReport(user_id, low_threshold_gap.low_threshold, max(0, high_threshold_gap.high_threshold))
        training_day = SuggestedTrainingDay(user_id, date_time, opt_values[0].low_optimal_threshold,
                                            ovr_values[0].low_overreaching_threshold,
                                            exc_values[0].low_excessive_threshold)
        training_day.high_optimal_threshold = opt_high_values[0].high_optimal_threshold
        training_day.high_overreaching_threshold = ovr_high_values[0].high_overreaching_threshold
        training_day.high_excessive_threshold = exc_high_values[0].high_excessive_threshold
        training_day.low_optimal_gap_type = opt_values[0].training_volume_gap_type
        training_day.low_overreaching_gap_type = ovr_values[0].training_volume_gap_type
        training_day.low_excessive_gap_type = exc_values[0].training_volume_gap_type
        training_day.high_optimal_gap_type = opt_high_values[0].training_volume_gap_type
        training_day.high_overreaching_gap_type = ovr_high_values[0].training_volume_gap_type
        training_day.high_excessive_gap_type = exc_high_values[0].training_volume_gap_type
        training_day.training_volume_gaps_opt = opt_values
        training_day.training_volume_gaps_ovr = ovr_values
        training_day.training_volume_gaps_exc = exc_values
        training_day.training_volume_gaps_opt_high = opt_high_values
        training_day.training_volume_gaps_ovr_high = ovr_high_values
        training_day.training_volume_gaps_exc_high = exc_high_values

        #report.training_level = TrainingLevel(max(low_threshold_gap.training_level if low_threshold_gap.training_level is not None else 0,
        #                                                       high_threshold_gap.training_level if high_threshold_gap.training_level is not None else 0))

        return training_day

    '''
    '''deprecated
    def get_strain_gap(self, historical_strain_values, monotony):

        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.strain)

        if len(historical_strain_values) > 0:

            strain_count = min(7, len(list(x for x in historical_strain_values if x is not None)))

            if strain_count > 1:
                strain_sd = statistics.stdev(
                    list(x for x in historical_strain_values[-strain_count:] if x is not None))
                strain_avg = statistics.mean(
                    list(x for x in historical_strain_values[-strain_count:] if x is not None))

                if historical_strain_values[len(
                        historical_strain_values) - 1] is not None and monotony is not None and monotony > 0:

                    strain_sd_load = strain_sd / monotony
                    strain_avg_load = strain_avg / monotony
                    training_volume_gap.high_optimal_threshold = strain_avg_load + strain_sd_load

        return training_volume_gap

    def get_strain_gap_old(self, historical_internal_strain, last_7_internal_load_values, weekly_expected_workouts=5):

        strain_count = min(7, len(historical_internal_strain))
        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.strain)
        max_load = None
        max_load_upper = None

        internal_strain_sd = 0
        internal_strain_avg = 0

        internal_strain_sd_upper = 0
        internal_strain_avg_upper = 0

        internal_monotony, internal_strain = self.calc_monotony_strain(last_7_internal_load_values)
        internal_monotony_upper, internal_strain_upper = self.calc_monotony_strain_se(last_7_internal_load_values, weekly_expected_workouts)

        if strain_count > 1:
            internal_strain_sd = statistics.stdev(list(x.observed_value for x in historical_internal_strain[-strain_count:]))
            internal_strain_avg = statistics.mean(list(x.observed_value for x in historical_internal_strain[-strain_count:]))
            if len(list(x.upper_bound for x in historical_internal_strain[-strain_count:] if x.upper_bound is not None)) > 0:
                internal_strain_sd_upper = statistics.stdev(list(x.upper_bound for x in historical_internal_strain[-strain_count:] if x.upper_bound is not None))
                internal_strain_avg_upper = statistics.mean(list(x.upper_bound for x in historical_internal_strain[-strain_count:] if x.upper_bound is not None))

            # not guaranteed internal_strain has a value today
            if historical_internal_strain[len(historical_internal_strain)-1] is not None and internal_monotony is not None and internal_monotony > 0:

                #strain_surplus = historical_internal_strain[len(historical_internal_strain)-1] - (1.2 * internal_strain_sd) - internal_strain_avg
                #load_change = strain_surplus / internal_monotony

                internal_strain_sd_load = internal_strain_sd / internal_monotony
                internal_strain_avg_load = internal_strain_avg / internal_monotony
                max_load = internal_strain_avg_load + internal_strain_sd_load

                # 1.2 * internal_strain_sd = athlete_stats.internal_strain - x
                # 1.2 * internal_strain_sd - athlete_stats.internal_strain =  - x
                # (-1) * (1.2 * internal_strain_sd - athlete_stats.internal_strain =  - x)

                # add/reduce this load from day 7 so the forecast load will reduce the strain; not perfect but close
                #strain_gap = max(0, last_7_internal_load_values[0] - load_change)

            if historical_internal_strain[len(historical_internal_strain)-1] is not None and internal_monotony_upper is not None and internal_monotony_upper > 0:

                internal_strain_sd_load_upper = internal_strain_sd_upper / internal_monotony_upper
                internal_strain_avg_load_upper = internal_strain_avg_upper / internal_monotony_upper
                max_load_upper = internal_strain_avg_load_upper + internal_strain_sd_load_upper

            training_volume_gap.training_volume_gap_type = TrainingVolumeGapType.strain

        # review the last week of strain and determine and count how many strain spikes occurred

        strain_events = 0
        strain_events_upper = 0

        for s in range(8, 15):
            hist_strain_count = min(s, len(historical_internal_strain))

            if hist_strain_count >= (s + 1):
                start_index = -len(historical_internal_strain) - (s + 1)
                end_index = start_index + 7
                if len(list(x.observed_value for x in historical_internal_strain[-strain_count:])) > 0:
                    internal_strain_sd = statistics.stdev(list(x.observed_value for x in historical_internal_strain[-strain_count:]))
                    internal_strain_avg = statistics.mean(list(x.observed_value for x in historical_internal_strain[-strain_count:]))

                    current_strain = historical_internal_strain[end_index].observed_value

                    if (current_strain - internal_strain_avg) / internal_strain_sd > 1.2:
                        strain_events += 1

                if len(list(x.upper_bound for x in historical_internal_strain[-strain_count:])) > 0:
                    internal_strain_sd_upper = statistics.stdev(
                        list(x.upper_bound for x in historical_internal_strain[-strain_count:]))
                    internal_strain_avg_upper = statistics.mean(
                        list(x.upper_bound for x in historical_internal_strain[-strain_count:]))

                    current_strain_upper = historical_internal_strain[end_index].upper_bound

                    if (current_strain_upper - internal_strain_avg_upper) / internal_strain_sd_upper > 1.2:
                        strain_events_upper += 1

        if strain_events >= 1:
            training_volume_gap.low_excessive_threshold = max_load
            training_volume_gap.low_overreaching_threshold = None
        else:
            training_volume_gap.low_overreaching_threshold = max_load
            training_volume_gap.low_excessive_threshold = None

        if strain_events_upper >= 1:
            training_volume_gap.high_excessive_threshold = max_load_upper
            training_volume_gap.high_overreaching_threshold = None
        else:
            training_volume_gap.high_overreaching_threshold = max_load_upper
            training_volume_gap.high_excessive_threshold = None

        training_volume_gap.low_optimal_threshold = None

        return training_volume_gap
    '''