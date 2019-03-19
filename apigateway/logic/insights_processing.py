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
                    self.daily_readiness_tuples.append((parse_date(format_date(r.event_date)), s.severity))

        training_sessions = self.get_training_sessions(plans)

        for t in training_sessions:
            if t.post_session_survey is not None:
                for s in t.post_session_survey.soreness:
                    if not s.pain:
                        self.post_session_survey_tuples.append((parse_date(format_date(t.event_date)), s.severity))

            if t.session_RPE is not None and t.duration_minutes is not None:
                self.rpe_load_tuples.append((parse_date(format_date(t.event_date)), t.session_RPE * t.duration_minutes))

    def get_contingency_tables(self, load_end_date, columns):

        contingency_tables = []

        load_values = list(r[1] for r in self.rpe_load_tuples if r is not None)
        if len(load_values) > 0:
            min_load = min(load_values)
            max_load = max(load_values)

            for d in range(1, 8):
                contingency_table = ContingencyTable(6, columns)
                category_range = (max_load - min_load) / float(contingency_table.number_columns)
                for t in self.rpe_load_tuples:
                    if t[0] <= load_end_date:
                        for c in range(1, contingency_table.number_columns + 1):
                            if t[1] >= min_load + (category_range * (c - 1)) and t[1] < min_load + (category_range * c):
                                severity_values = list(s[1] for s in self.daily_readiness_tuples if s[0] == t[0] + timedelta(days=d))
                                severity_values.extend(
                                    list(s[1] for s in self.post_session_survey_tuples if s[0] == t[0] + timedelta(days=d)))
                                if len(severity_values) > 0:
                                    for s in severity_values:
                                        contingency_table.table[s][c - 1] += 1
                                else:
                                    contingency_table.table[0][c - 1] += 1
                            elif t[1] == max_load:
                                severity_values = list(s[1] for s in self.daily_readiness_tuples if s[0] == t[0] + timedelta(days=d))
                                severity_values.extend(
                                    list(s[1] for s in self.post_session_survey_tuples if s[0] == t[0] + timedelta(days=d)))
                                if len(severity_values) > 0:
                                    for s in severity_values:
                                        contingency_table.table[s][c - 1] += 1
                                else:
                                    contingency_table.table[0][c - 1] += 1
                contingency_table.calculate()
                contingency_tables.append(contingency_table)

        return contingency_tables

    def get_training_sessions(self, daily_plans):

        training_sessions = []

        for c in daily_plans:
            training_sessions.extend(c.training_sessions)
            training_sessions.extend(c.practice_sessions)
            training_sessions.extend(c.strength_conditioning_sessions)
            training_sessions.extend(c.games)
            training_sessions.extend(c.bump_up_sessions)

        return training_sessions
