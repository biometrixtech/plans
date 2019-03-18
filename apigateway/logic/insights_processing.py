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
            for s in t.post_session_survey.soreness:
                if not s.pain:
                    self.post_session_survey_tuples.append((parse_date(format_date(t.event_date)), s.severity))

            self.rpe_load_tuples.append((parse_date(format_date(t.event_date)), t.session_RPE * t.duration_minutes))

    def get_contingency_table(self):


        load_values = list(r[1] for r in self.rpe_load_tuples)
        min_load = min(load_values)
        max_load = max(load_values)


        for d in range(1,8):
            contingency_table = ContingencyTable(6, 3)
            category_range = (max_load - min_load) / float(contingency_table.number_columns)
            for t in self.rpe_load_tuples:
                for c in range(1, contingency_table.number_columns + 1):
                    if t[1] >= min_load + (category_range * (c - 1)) and t[1] < min_load + (category_range * c):
                        severity_values = list(s[1] for s in self.daily_readiness_tuples if s[0] == t[0] + timedelta(days=d))
                        if len(severity_values) > 0:
                            for s in severity_values:
                                contingency_table.table[s][c - 1] += 1
                        else:
                            contingency_table.table[0][c - 1] += 1
                    elif t[1] == max_load:
                        severity_values = list(s[1] for s in self.daily_readiness_tuples if s[0] == t[0] + timedelta(days=d))
                        if len(severity_values) > 0:
                            for s in severity_values:
                                contingency_table.table[s][c - 1] += 1
                        else:
                            contingency_table.table[0][c - 1] += 1
            contingency_table.calculate()
            if contingency_table.chi_square_significant:
                k=1

        j = 0


    def get_training_sessions(self, daily_plans):

        training_sessions = []

        for c in daily_plans:
            training_sessions.extend(c.training_sessions)
            training_sessions.extend(c.practice_sessions)
            training_sessions.extend(c.strength_conditioning_sessions)
            training_sessions.extend(c.games)
            training_sessions.extend(c.bump_up_sessions)

        return training_sessions

    def get_session_attributes_product_sum_tuple_list(self, attribute_1_name, attribute_2_name, daily_plan_collection):

        # sum_value = None

        values = []

        for c in daily_plan_collection:

            #sub_values = []

            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.training_sessions))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.practice_sessions))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.strength_conditioning_sessions))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.games))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.bump_up_sessions))
            #if len(sub_values) > 0:
            #    sum_value = sum(sub_values)
            #    values.append(sum_value)

        return values

    def get_tuple_product_of_session_attributes(self, event_date_time, attribute_1_name, attribute_2_name, session_collection):

        values = []
        values_list = list(getattr(c, attribute_1_name) * getattr(c, attribute_2_name) for c in session_collection
                      if getattr(c, attribute_1_name) is not None and getattr(c, attribute_2_name) is not None)
        for v in values_list:
            values.append((event_date_time, v))

        return values