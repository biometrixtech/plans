from models.contingency_table import ContingencyTable
from utils import format_date, parse_date
from datetime import timedelta
from itertools import groupby
from operator import itemgetter, attrgetter
from statistics import stdev, mean

class InsightsProcessing(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.daily_readiness_tuples = []
        self.post_session_survey_tuples = []
        self.rpe_load_tuples = []
        self.no_soreness_load_tuples = {}
        self.no_soreness_rpe_tuples = {}
        self.soreness_load_tuples = {}
        self.soreness_rpe_tuples = {}
        self.last_14_max_no_soreness_load_tuples = {}
        self.last_14_max_no_soreness_rpe_tuples = {}
        self.last_14_max_soreness_load_tuples = {}
        self.last_14_max_soreness_rpe_tuples = {}

    def load_surveys(self, readiness_surveys, plans):

        for r in readiness_surveys:
            for s in r.soreness:
                if not s.pain:
                    self.daily_readiness_tuples.append((r.event_date, (s.body_part.location.value, s.side, s.severity)))

        training_sessions = self.get_training_sessions(plans)

        for t in training_sessions:
            if t.post_session_survey is not None:
                for s in t.post_session_survey.soreness:
                    if not s.pain:
                        self.post_session_survey_tuples.append((t.event_date, (s.body_part.location.value, s.side, s.severity)))

            if t.session_RPE is not None and t.duration_minutes is not None:
                self.rpe_load_tuples.append((t.event_date, t.session_RPE, t.duration_minutes, t.sport_name, t.strength_and_conditioning_type))

        self.daily_readiness_tuples.sort(key=self.get_tuple_datetime)
        self.post_session_survey_tuples.sort(key=self.get_tuple_datetime)
        self.rpe_load_tuples.sort(key=self.get_tuple_datetime)

    def get_tuple_datetime(self, element):
            return element[0]

    def get_contingency_tables(self, load_start_date, load_end_date, columns):

        contingency_tables = []
        loading_events = []
        initial_loading_events = []

        # create a list of loading events first
        for t in range(0, len(self.rpe_load_tuples) - 1):

            if self.rpe_load_tuples[t][0] <= load_end_date:
                loading_event = LoadingEvent(self.rpe_load_tuples[t][0], self.rpe_load_tuples[t][1], self.rpe_load_tuples[t][2], self.rpe_load_tuples[t][3], self.rpe_load_tuples[t][4])
                initial_loading_events.append(loading_event)

        # sum load by day, type
        load_grouper = attrgetter('loading_date', 'sport_name.name', 'strength_conditioning_type.name')
        for k, g in groupby(sorted(initial_loading_events, key=load_grouper), load_grouper):
            part_list = list(g)
            part_list.sort(key=lambda x: x.loading_date)
            #load_sum = sum(list(g.load for g in part_list))
            avg_rpe = mean(list(g.RPE for g in part_list))
            avg_duration = sum(list(g.duration for g in part_list))
            loading_event = LoadingEvent(k[0], avg_rpe, avg_duration, k[1], k[2])
            loading_events.append(loading_event)


        early_soreness_tuples = list(s[0] for s in self.post_session_survey_tuples
                                   if s[0] >= loading_events[0].loading_date and
                                   s[0] <= loading_events[0].loading_date + timedelta(hours=36))
        early_soreness_tuples.extend(list(s[0] for s in self.daily_readiness_tuples
                                        if s[0] >= loading_events[0].loading_date and
                                        s[0] <= loading_events[0].loading_date + timedelta(hours=36)))
        early_soreness_history = list(set(early_soreness_tuples))

        # let's reduce this down to only the loading events that can have soreness (the highest RPE within a rolling 72 hour window)
        for t in range(0, len(loading_events)):

            test_date = loading_events[t].loading_date + timedelta(hours=36)
            if len(early_soreness_history) > t:
                test_date = min(early_soreness_history[t], loading_events[t].loading_date + timedelta(hours=36))
            window_events = list(d for d in loading_events if d.loading_date >= loading_events[t].loading_date and d.loading_date <= test_date)
            if len(window_events) > 0:
                window_events.sort(key=lambda x: x.RPE, reverse=True)
                window_events[0].highest_rpe_in_72_hrs = True
                #for w in range(1, len(window_events)):
                #    window_events[w].highest_rpe_in_72_hrs = False

        for t in range(0, len(loading_events) - 1):

            if loading_events[t].loading_date <= load_end_date and loading_events[t].highest_rpe_in_72_hrs:
                #loading_event = LoadingEvent(self.rpe_load_tuples[t][0], self.rpe_load_tuples[t][1], self.rpe_load_tuples[t][2], self.rpe_load_tuples[t][3])
                loading_event = loading_events[t]
                first_load_date = loading_events[0].loading_date

                if (loading_event.loading_date.date() - first_load_date.date()).days >= 4:
                    chronic_load = list(v.load for v in loading_events if v.load is not None and 4 >= (loading_event.loading_date.date() - v.loading_date.date()).days >= 2)
                    acute_load = list(v.load for v in loading_events if v.load is not None and 1 >= (loading_event.loading_date.date() - v.loading_date.date()).days >= 0)
                    acute_sum = 0
                    chronic_sum = 0
                    if len(acute_load) > 0:
                        acute_sum = sum(acute_load)
                    if len(chronic_load) > 0:
                        chronic_sum = sum(chronic_load)
                    if chronic_sum > 0:
                        loading_event.acwr_2_3 = acute_sum / float(chronic_sum)

                load_values = list(l.load for l in loading_events if l.load is not None)
                load_values.append(loading_event.load)
                if len(load_values) >= 7:
                    std_dev = stdev(load_values[-7:])
                    avg = mean(load_values[-7:])
                    if std_dev != 0:
                        loading_event.z_score = (loading_event.load - avg) / std_dev
                if len(loading_events) > 0:
                    loading_event.lagged_load = loading_events[len(loading_events) - 1].load
                    loading_event.lagged_load_z_score = loading_events[len(loading_events) - 1].z_score
                    loading_event.days_rest = (loading_event.loading_date.date() - loading_events[len(loading_events) - 1].loading_date.date()).days

                # get all affected body parts that could be attributed to this training session
                #base_soreness_tuples = list((s[0], s[1]) for s in self.post_session_survey_tuples
                #                       if s[0] >= self.rpe_load_tuples[t][0] and
                #                       s[0] < self.rpe_load_tuples[t + 1][0])
                next_highest_rpe_date = loading_events[t].loading_date + timedelta(hours=36)
                candidates = list(r for r in loading_events if r.loading_date > loading_events[t].loading_date
                                  and r.loading_date <= next_highest_rpe_date and r.RPE > loading_events[t].RPE and r.highest_rpe_in_72_hrs)
                candidates.sort(key=lambda x: x.loading_date)
                if len(candidates) > 0:
                    next_highest_rpe_date = candidates[0].loading_date


                base_soreness_tuples = list((s[0], s[1]) for s in self.post_session_survey_tuples
                                            if s[0] >= loading_events[t].loading_date and
                                            s[0] <= next_highest_rpe_date)
                #base_soreness_tuples.extend(list((s[0], s[1]) for s in self.daily_readiness_tuples
                #                            if s[0] >= self.rpe_load_tuples[t][0] and
                #                            s[0] < self.rpe_load_tuples[t + 1][0]))
                base_soreness_tuples.extend(list((s[0], s[1]) for s in self.daily_readiness_tuples
                                                 if s[0] >= loading_events[t].loading_date and
                                                 s[0] <= next_highest_rpe_date))

                body_parts = list(AffectedBodyPart(b[1][0], b[1][1], 0, 0, False) for b in base_soreness_tuples) # body part, side, days sore, max_severity, cleared
                affected_body_parts = list(set(body_parts))
                all_soreness_tuples = list((s[0], s[1]) for s in self.post_session_survey_tuples
                                            if s[0] >= self.rpe_load_tuples[t][0] and
                                            s[0] < self.rpe_load_tuples[t][0] + timedelta(days=12))
                all_soreness_tuples.extend(list((s[0], s[1]) for s in self.daily_readiness_tuples
                                                 if s[0] >= self.rpe_load_tuples[t][0] and
                                                 s[0] < self.rpe_load_tuples[t][0] + timedelta(days=12)))
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
                                    a.days_sore = 1
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
                # need to pick the oldest date for each body part
                grouped_parts = []
                grouper = attrgetter('body_part', 'side')
                for k, g in groupby(sorted(affected_body_parts, key=grouper), grouper):
                    part_list = list(g)
                    part_list.sort(key=lambda x: x.last_reported_date)
                    grouped_parts.append(part_list[0])

                loading_event.affected_body_parts = grouped_parts
                #loading_events.append(loading_event)

        for loading_event in loading_events:
            level_one_soreness = list(a for a in loading_event.affected_body_parts if a.max_severity <= 1 and a.cleared and a.days_sore <= 1)

            if len(loading_event.affected_body_parts) == len(level_one_soreness): # no soreness
                if loading_event.sport_name not in self.no_soreness_load_tuples:
                    self.no_soreness_load_tuples[loading_event.sport_name] = []
                    self.no_soreness_rpe_tuples[loading_event.sport_name] = []
                    self.last_14_max_no_soreness_load_tuples[loading_event.sport_name] = []
                    self.last_14_max_no_soreness_rpe_tuples[loading_event.sport_name] = []
                self.no_soreness_load_tuples[loading_event.sport_name].append((loading_event.loading_date, loading_event.load))
                self.no_soreness_rpe_tuples[loading_event.sport_name].append((loading_event.loading_date, loading_event.RPE))

                '''who cares nothing matters
                for k in self.no_soreness_load_tuples.keys():
                    no_soreness_list = self.no_soreness_load_tuples[k]
                    if len(no_soreness_list) > 0:
                        sore_values = list(s[1] for s in no_soreness_list)
                        if len(sore_values) > 0:
                            self.last_14_max_no_soreness_load_tuples[k].append((no_soreness_list[len(no_soreness_list) - 1][0], max(sore_values[-min(3, len(sore_values)):])))
                for k in self.no_soreness_rpe_tuples.keys():
                    no_soreness_RPE_list = self.no_soreness_rpe_tuples[k]
                    if len(no_soreness_RPE_list) > 0:
                        sore_values = list(s[1] for s in no_soreness_RPE_list)
                        if len(sore_values) > 0:
                            self.last_14_max_no_soreness_rpe_tuples[k].append((no_soreness_RPE_list[len(no_soreness_RPE_list) - 1][0], max(sore_values[-min(3, len(sore_values)):])))
                '''

            else:
                if loading_event.sport_name not in self.soreness_load_tuples:
                    self.soreness_load_tuples[loading_event.sport_name] = []
                    self.soreness_rpe_tuples[loading_event.sport_name] = []
                    self.last_14_max_soreness_load_tuples[loading_event.sport_name] = []
                    self.last_14_max_soreness_rpe_tuples[loading_event.sport_name] = []
                self.soreness_load_tuples[loading_event.sport_name].append((loading_event.loading_date, loading_event.load))
                self.soreness_rpe_tuples[loading_event.sport_name].append((loading_event.loading_date, loading_event.RPE))

                '''deprecate this!
                for k in self.soreness_load_tuples.keys():
                    soreness_list = self.soreness_load_tuples[k]
                    if len(soreness_list) > 0:
                        sore_values = list(s[1] for s in soreness_list)
                        if len(sore_values) > 0:
                            self.last_14_max_soreness_load_tuples[k].append((soreness_list[len(soreness_list) - 1][0], min(sore_values[-min(3, len(sore_values)):])))
                for k in self.soreness_rpe_tuples.keys():
                    soreness_RPE_list = self.soreness_rpe_tuples[k]
                    if len(soreness_RPE_list) > 0:
                        sore_values = list(s[1] for s in soreness_RPE_list)
                        if len(sore_values) > 0:
                            self.last_14_max_soreness_rpe_tuples[k].append((soreness_RPE_list[len(soreness_RPE_list) - 1][0], min(sore_values[-min(3, len(sore_values)):])))
                '''

        self.get_adaptation_history()

        # all loading events
        contingency_table = self.populate_contingency_table(loading_events, columns)

        contingency_table.calculate()
        contingency_tables.append(contingency_table)

        # loading events by activity
        event_parts = []
        grouper = attrgetter('sport_name')
        for k, g in groupby(sorted(loading_events, key=grouper), grouper):
            part_list = list(g)
            part_list.sort(key=lambda x: x.loading_date)
            contingency_table = self.populate_contingency_table(part_list, columns)
            contingency_table.descriptor = k
            contingency_table.calculate()
            contingency_tables.append(contingency_table)

        return contingency_tables


    def get_adaptation_history(self):

        all_sesssion_types = []
        #all_sesssion_types.extend(self.last_14_max_soreness_load_tuples.keys())
        all_sesssion_types.extend(self.soreness_load_tuples.keys())
        #all_sesssion_types.extend(self.last_14_max_no_soreness_load_tuples.keys())
        all_sesssion_types.extend(self.no_soreness_load_tuples.keys())
        session_types = list(set(all_sesssion_types))

        all_dates = []
        #for k in self.last_14_max_soreness_load_tuples.keys():
        for k in self.soreness_load_tuples.keys():
            #all_dates.extend(list(x[0] for x in self.last_14_max_soreness_load_tuples[k]))
            all_dates.extend(list(x[0] for x in self.soreness_load_tuples[k]))

        #for k in self.last_14_max_no_soreness_load_tuples.keys():
        for k in self.no_soreness_load_tuples.keys():
            #all_dates.extend(list(x[0] for x in self.last_14_max_no_soreness_load_tuples[k]))
            all_dates.extend(list(x[0] for x in self.no_soreness_load_tuples[k]))

        dates = list(set(all_dates))
        dates.sort()

        history = {}

        for s in session_types:
            last_min_load = None
            last_min_load_date = None
            last_max_load = None
            last_max_load_date = None
            load_capacity = None
            load_capacity_date = None

            history[s] = []
            for d in dates:
                # get all the min values for this session for this date
                min_vals = []
                max_vals = []
                #if s in self.last_14_max_no_soreness_load_tuples.keys():
                if s in self.no_soreness_load_tuples.keys():
                    #min_vals = list(x[1] for x in self.last_14_max_no_soreness_load_tuples[s] if x[0] == d)
                    min_vals = list(x[1] for x in self.no_soreness_load_tuples[s] if x[0] == d)
                    if len(min_vals) > 0:
                        max_min_vals = max(min_vals)
                        if last_min_load is None:
                            last_min_load = max_min_vals
                            last_min_load_date = d
                        else:
                            if last_min_load_date > load_capacity_date:
                                last_min_load = max(last_min_load, max_min_vals)
                            else:
                                last_min_load = max_min_vals
                                last_min_load_date = d
                        load_capacity = max(load_capacity if load_capacity is not None else 0, last_min_load if last_min_load is not None else 0)
                        load_capacity_date = d

                #if s in self.last_14_max_soreness_load_tuples.keys():
                if s in self.soreness_load_tuples.keys():
                    #max_vals = list(x[1] for x in self.last_14_max_soreness_load_tuples[s] if x[0] == d)
                    max_vals = list(x[1] for x in self.soreness_load_tuples[s] if x[0] == d)

                    if len(max_vals) > 0:
                        min_max_vals = min(max_vals)
                        if last_max_load is None:
                            last_max_load = min_max_vals
                            last_max_load_date = d
                        else:
                            if last_max_load_date > load_capacity_date:
                                last_max_load = min(last_max_load, min_max_vals)
                            else:
                                last_max_load = min_max_vals
                                last_max_load_date = d

                        if load_capacity is None or load_capacity >= last_max_load:
                            load_capacity = .90 * last_max_load
                            load_capacity_date = d

                history[s].append((d, tuple(min_vals), tuple(max_vals), load_capacity))
        i=0

    def populate_contingency_table(self, loading_events, columns):

        load_values = list(r.load for r in loading_events if r.load is not None)

        if len(load_values) > 0:
            min_load = min(load_values)
            max_load = max(load_values)

            contingency_table = ContingencyTable(3, columns)
            category_range = (max_load - min_load) / float(contingency_table.number_columns)

            for le in loading_events:
                for c in range(1, contingency_table.number_columns + 1):
                    if le.load is not None:
                        if ((le.load >= min_load + (category_range * (c - 1)) and le.load < min_load + (
                                category_range * c)) or
                                le.load == max_load):
                            if len(le.affected_body_parts) == 0:
                                contingency_table.table[0][c - 1] += 1
                            for a in le.affected_body_parts:
                                if a.days_sore <= 1:
                                    contingency_table.table[0][c - 1] += 1
                                elif 2 <= a.days_sore <= 3:
                                    contingency_table.table[1][c - 1] += 1
                                elif 4 < a.days_sore:
                                    contingency_table.table[2][c - 1] += 1

        return contingency_table

    def get_dates(self, start_date, end_date):

        dates = []

        delta = end_date - start_date

        for i in range(delta.days + 1):
            dates.append(start_date + timedelta(i))

        return dates

    def get_event_date_from_session(self, session):
        return session.event_date

    def update_load_thresholds(self):

        #TODO
        return True

    def is_acute_fatigue_FO_soreness(self, soreness_list):

        #TODO
        return True

    def is_possible_non_functional_overreaching_soreness(self, soreness_list):

        #TODO
        return True

    def is_recovery_load(self, loading_event):

        #TODO: look at low RPE, low volume, low perceived fatigue
        #TODO: look at self.thresholds to determine if it's in the threshold for recovery
        return True

    def is_maintenance_load(self, loading_event):

        # TODO: look at self.thresholds to determine if it's in the threshold for maintenance
        return True

    def is_acute_fatigue_FO_load(self, loading_event):

        # TODO: look at self.thresholds to determine if it's in the threshold for acute_fatigue/FO
        return True

    def is_FO_Possible_NFO_load(self, loading_event):

        # TODO: look at self.thresholds to determine if it's in the threshold for FO/Possible NFO
        return True

    def get_near_term_status(self, loading_event, soreness_list):

        # if all we have is load, we may not know much
        # TODO: need to make decision based purely on intensity and volume ?

        # only interested in the soreness that came after that load
        filtered_soreness_list = list(s for s in soreness_list if s.event_date >= loading_event.loading_date)

        if self.is_recovery_load(loading_event) and len(filtered_soreness_list) == 0:
            return "Recovery"
        elif self.is_maintenance_load(loading_event) and len(filtered_soreness_list) == 0:
            return "Maintenance"
        elif (self.is_recovery_load(loading_event) or self.is_maintenance_load(loading_event)) and len(filtered_soreness_list) > 0:
            self.update_load_thresholds()
            return "Failed"
        elif self.is_acute_fatigue_FO_load(loading_event) and self.is_acute_fatigue_FO_soreness(filtered_soreness_list):
            return "Acute Fatigue - Functional Overreaching"
        elif self.is_acute_fatigue_FO_load(loading_event) and not self.is_acute_fatigue_FO_soreness(filtered_soreness_list):
            return "FAILED!"
        elif self.is_FO_Possible_NFO_load(loading_event) and self.is_possible_non_functional_overreaching_soreness(filtered_soreness_list):
            return "FO Potential NFO"
        elif self.is_FO_Possible_NFO_load(loading_event) and not self.is_possible_non_functional_overreaching_soreness(filtered_soreness_list):
            return "FAILED!"

        # if all we have is soreness, we need the last load - or if the last load is too long ago, we need to know what to do with this soreness
        # at which point should we predict the future - and does that affect status?
        # how/when do we identify positive/negative adaptation to load? does it come into play here?


    def get_training_sessions(self, daily_plans):

        training_sessions = []

        #due to how these are entered, we may have multiple sessions on one day with the same datetime
        for c in daily_plans:
            training_sessions.extend(c.training_sessions)
            training_sessions.extend(c.practice_sessions)
            training_sessions.extend(c.strength_conditioning_sessions)
            training_sessions.extend(c.games)
            training_sessions.extend(c.bump_up_sessions)

        training_sessions.sort(key=self.get_event_date_from_session)

        return training_sessions


class AffectedBodyPart(object):
    def __init__(self, body_part, side, days_sore, max_severity, cleared):
        self.body_part = body_part
        self.side = side
        self.days_sore = days_sore
        self.max_severity = max_severity
        self.cleared = cleared
        self.first_reported_date = None
        self.last_reported_date = None


class LoadingEvent(object):
    def __init__(self, loading_date, rpe, duration, sport_name, strength_conditioning_type):
        self.loading_date = loading_date
        self.RPE = rpe
        self.duration = duration
        self.load = rpe * duration
        self.sport_name = sport_name
        self.strength_conditioning_type = strength_conditioning_type
        self.affected_body_parts = []
        self.previous_affected_body_parts = []
        self.z_score = None
        self.lagged_load = None
        self.lagged_load_z_score = None
        self.acwr_2_3 = None
        self.days_rest = None
        self.highest_rpe_in_72_hrs = False

    def has_existing_soreness(self, days=1):

        for a in self.affected_body_parts:
            matched_soreness = list(p for p in self.previous_affected_body_parts if p.body_part == a.body_part
                                    and p.side == a.side and p.days_sore >= days)
            if len(matched_soreness) > 0:
                return True

        return False
