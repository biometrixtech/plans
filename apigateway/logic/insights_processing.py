from models.contingency_table import ContingencyTable
from utils import format_date, parse_date
from datetime import timedelta

class InsightsProcessing(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.daily_readiness_tuples = []
        self.post_session_survey_tuples = []
        self.rpe_load_tuples = []

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
                self.rpe_load_tuples.append((t.event_date, t.session_RPE * t.duration_minutes, t.sport_name, t.strength_and_conditioning_type))

        self.daily_readiness_tuples.sort(key=self.get_tuple_datetime)
        self.post_session_survey_tuples.sort(key=self.get_tuple_datetime)
        self.rpe_load_tuples.sort(key=self.get_tuple_datetime)

    def get_tuple_datetime(self, element):
            return element[0]

    def get_contingency_tables(self, load_start_date, load_end_date, columns):

        contingency_tables = []
        loading_events = []

        load_values = list(r[1] for r in self.rpe_load_tuples if r is not None)
        if len(load_values) > 0:
            min_load = min(load_values)
            max_load = max(load_values)

            contingency_table = ContingencyTable(6, columns)
            category_range = (max_load - min_load) / float(contingency_table.number_columns)
            for t in range(0, len(self.rpe_load_tuples) - 1):
                response_tuples = []
                if self.rpe_load_tuples[t][0] <= load_end_date:
                    loading_event = LoadingEvent(self.rpe_load_tuples[t][0], self.rpe_load_tuples[t][1], self.rpe_load_tuples[t][2], self.rpe_load_tuples[t][3])
                    # get all affected body parts that could be attributed to this training session
                    base_soreness_tuples = list((s[0], s[1]) for s in self.post_session_survey_tuples
                                           if s[0] >= self.rpe_load_tuples[t][0] and
                                           s[0] < self.rpe_load_tuples[t + 1][0])
                    base_soreness_tuples.extend(list((s[0], s[1]) for s in self.daily_readiness_tuples
                                                if s[0] >= self.rpe_load_tuples[t][0] and
                                                s[0] < self.rpe_load_tuples[t + 1][0]))
                    body_parts = list(AffectedBodyPart(b[1][0], b[1][1], 0, 0, False) for b in base_soreness_tuples) # body part, side, days sore, max_severity, cleared
                    affected_body_parts = list(set(body_parts))
                    all_soreness_tuples = list((s[0], s[1]) for s in self.post_session_survey_tuples
                                                if s[0] >= self.rpe_load_tuples[t][0] and
                                                s[0] < self.rpe_load_tuples[t][0] + timedelta(days=9))
                    all_soreness_tuples.extend(list((s[0], s[1]) for s in self.daily_readiness_tuples
                                                     if s[0] >= self.rpe_load_tuples[t][0] and
                                                     s[0] < self.rpe_load_tuples[t][0] + timedelta(days=9)))
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
                                    a.max_severity = max(a.max_severity, body_parts_present[0][3]) # first element which contains a tuple... :(
                                elif a.days_sore > 0:
                                    a.cleared = True
                    loading_event.affected_body_parts = affected_body_parts
                    loading_events.append(loading_event)
            j=0

            contingency_table.calculate()
            contingency_tables.append(contingency_table)

        return contingency_tables

    def get_dates(self, start_date, end_date):

        dates = []

        delta = end_date - start_date

        for i in range(delta.days + 1):
            dates.append(start_date + timedelta(i))

        return dates

    def get_event_date_from_session(self, session):
        return session.event_date

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
        self.last_reported_date = None


class LoadingEvent(object):
    def __init__(self, loading_date, load, sport_name, strength_conditioning_type):
        self.loading_date = loading_date
        self.load = load
        self.sport_name = sport_name
        self.strength_conditioning_type = strength_conditioning_type
        self.affected_body_parts = []
