from models.soreness import Soreness, SorenessType
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation
from models.historic_soreness import CoOccurrence, SorenessCause
from datetime import timedelta
from utils import none_max


class SorenessCalculator(object):

    def __init__(self):
        self.surveys = []

    def get_soreness_summary_from_surveys(self, readiness_surveys, post_session_surveys,
                                          trigger_date_time, historic_soreness):
        """
        :param historic_soreness:
        :param readiness_surveys: DailyReadiness
        :param trigger_date_time: datetime
        :param post_session_surveys: PostSurveys
        :return:
        """

        soreness_list = []

        for rs_survey in readiness_surveys:
            if (trigger_date_time.date() - rs_survey.get_event_date().date()).days < 2:
                self.update_soreness_list(soreness_list, rs_survey.soreness)
        # for ps_survey in post_session_surveys:
        #     if (trigger_date_time.date() - ps_survey.event_date_time.date()).days < 2:
        #         self.update_soreness_list(soreness_list, ps_survey.survey.soreness)
        for ps_survey in post_session_surveys:
            if (trigger_date_time.date() - ps_survey.event_date.date()).days < 2:
                self.update_soreness_list(soreness_list, ps_survey.soreness)

        soreness_list = self.merge_current_historic_soreness(soreness_list, historic_soreness)
        return soreness_list

    @classmethod
    def get_severity(cls, severity, movement):

        if severity is None:
            if movement is None:
                return None
            else:
                if movement == 1:
                    return 1
                elif 1 < movement <= 3:
                    return 2
                else:
                    return 3
        elif movement in [None, 0] or severity == 0:
            return severity
        elif severity == 1:
            if movement == 1:
                return 1
            elif 1 < movement <= 3:
                return 2
            elif 3 < movement <= 5:
                return 3
        elif 1 < severity <= 3:
            if movement == 1:
                return 2
            elif 1 < movement <= 3:
                return 3
            elif 3 < movement <= 5:
                return 4
        elif 3 < severity <= 5:
            if movement == 1:
                return 4
            elif 1 < movement <= 3:
                return 4
            elif 3 < movement <= 5:
                return 5

    def update_soreness_list(self, soreness_list, soreness_from_survey):
        for s in soreness_from_survey:
            updated = False
            for r in soreness_list:
                if r.body_part.location.value == s.body_part.location.value and r.side == s.side and r.pain == s.pain:
                    r.severity = none_max([self.get_severity(r.severity, r.movement), self.get_severity(s.severity, s.movement)])
                    r.movement = None
                    r.ache = none_max([r.ache, s.ache])
                    r.knots = none_max([r.knots, s.knots])
                    r.tight = none_max([r.tight, s.tight])
                    r.sharp = none_max([r.sharp, s.sharp])
                    updated = True
            if not updated:
                s.severity = self.get_severity(s.severity, s.movement)
                s.movement = None
                soreness_list.append(s)
        return soreness_list

    @staticmethod
    def merge_current_historic_soreness(soreness_list, historic_soreness):

        for h in range(0, len(historic_soreness)):
            historic_soreness_found = False
            for s in range(0, len(soreness_list)):
                if (soreness_list[s].body_part.location == historic_soreness[h].body_part_location and
                        soreness_list[s].side == historic_soreness[h].side and
                        soreness_list[s].pain == historic_soreness[h].is_pain):
                    soreness_list[s].historic_soreness_status = historic_soreness[h].historic_soreness_status
                    soreness_list[s].first_reported_date_time = historic_soreness[h].first_reported_date_time
                    soreness_list[s].last_reported_date_time = historic_soreness[h].last_reported_date_time
                    soreness_list[s].cleared_date_time = historic_soreness[h].cleared_date_time
                    soreness_list[s].max_severity = historic_soreness[h].max_severity
                    soreness_list[s].max_severity_date_time = historic_soreness[h].max_severity_date_time
                    soreness_list[s].causal_session = historic_soreness[h].causal_session
                    soreness_list[s].status_changed_date_time = historic_soreness[h].status_changed_date_time
                    historic_soreness_found = True
            if not historic_soreness_found:
                new_soreness = Soreness()
                new_soreness.pain = historic_soreness[h].is_pain
                new_soreness.side = historic_soreness[h].side
                new_soreness.severity = historic_soreness[h].average_severity
                new_soreness.max_severity = historic_soreness[h].max_severity
                new_soreness.body_part = BodyPart(historic_soreness[h].body_part_location, None)
                new_soreness.historic_soreness_status = historic_soreness[h].historic_soreness_status
                new_soreness.daily = False
                new_soreness.first_reported_date_time = historic_soreness[h].first_reported_date_time
                new_soreness.last_reported_date_time = historic_soreness[h].last_reported_date_time
                new_soreness.cleared_date_time = historic_soreness[h].cleared_date_time
                new_soreness.max_severity_date_time = historic_soreness[h].max_severity_date_time
                new_soreness.causal_session = historic_soreness[h].causal_session
                new_soreness.status_changed_date_time = historic_soreness[h].status_changed_date_time
                soreness_list.append(new_soreness)

        return soreness_list

    def get_soreness_cause(self, historic_soreness, current_date_time):

        is_symmetric = False
        multiple_muscle_groups = False
        contains_symmetric_groups = False
        current_days_diff = (current_date_time - historic_soreness.first_reported_date_time).days

        if current_days_diff < 14:
            return SorenessCause.overloading

        # don't reset dysfunction, upgrade weakness if the length has increased sufficiently
        if historic_soreness.cause == SorenessCause.dysfunction:
            return SorenessCause.dysfunction
        elif historic_soreness.cause == SorenessCause.weakness and current_days_diff >= 28:
            return SorenessCause.dysfunction

        if len(historic_soreness.co_occurrences) == 0:
            if 14 <= current_days_diff <= 28:
                return SorenessCause.weakness
            elif 28 < current_days_diff:
                return SorenessCause.dysfunction

        matching_co_occurrence = CoOccurrence(historic_soreness.body_part_location,
                                              self.get_reciprocal_side(historic_soreness.side), None, None)

        try:
            c_index = historic_soreness.co_occurrences.index(matching_co_occurrence)
            historic_soreness.co_occurrences[c_index].symmetric_pair = True
            if historic_soreness.co_occurrences[c_index].percentage > .50:
                is_symmetric = True
        except ValueError:
            pass

        if len(historic_soreness.co_occurrences) == 1:
            if is_symmetric:
                if (14 <= current_days_diff <= 28 and
                      (current_date_time - historic_soreness.co_occurrences[0].first_reported_date_time).days <= 28):
                    return SorenessCause.weakness
                elif (28 < current_days_diff and
                      (current_date_time - historic_soreness.co_occurrences[0].first_reported_date_time).days > 28):
                    return SorenessCause.dysfunction
                else:
                    return SorenessCause.overloading
            else:
                if (14 <= current_days_diff <= 28 and
                      (current_date_time - historic_soreness.co_occurrences[0].first_reported_date_time).days <= 28):
                    return SorenessCause.weakness
                elif (28 < current_days_diff and
                      (current_date_time - historic_soreness.co_occurrences[0].first_reported_date_time).days > 28):
                    return SorenessCause.dysfunction
                else:
                    return SorenessCause.overloading

        remaining_parts = list(c for c in historic_soreness.co_occurrences if not c.symmetric_pair)
        symmetric_group_counts, symmetric_group_days_diff = self.get_symmetric_groups(remaining_parts, current_date_time)

        if is_symmetric:
            for b, count in symmetric_group_counts.items():
                if count > 1 and symmetric_group_days_diff[b] >= current_days_diff:
                    # multiple symmetric muscle groups, not as concerned about strength of relationship (i.e., percentage)
                    return SorenessCause.overloading

        else:
            if 14 <= current_days_diff <= 28:
                return SorenessCause.weakness
            elif current_days_diff > 28:
                return SorenessCause.dysfunction
            else:
                return SorenessCause.overloading

        return SorenessCause.unknown

    def get_reciprocal_side(self, side):

        if side == 0:
            return 0
        elif side == 1:
            return 2
        elif side == 2:
            return 1

    def get_symmetric_groups(self, co_occurrence_list, current_date_time):

        body_part_counts = {}
        body_part_days_diff = {}

        for c in co_occurrence_list:
            if c.body_part_location not in body_part_counts:
                body_part_counts[c.body_part_location] = 0
                body_part_days_diff[c.body_part_location] = 0
            body_part_counts[c.body_part_location] += 1
            body_part_diff_time = (current_date_time - c.first_reported_date_time).days
            if body_part_days_diff[c.body_part_location] == 0:
                body_part_days_diff[c.body_part_location] = body_part_diff_time
            else:
                body_part_days_diff[c.body_part_location] = min(body_part_days_diff[c.body_part_location], body_part_diff_time)

        return body_part_counts, body_part_days_diff


class BodyPartMapping(object):
    @staticmethod
    def get_soreness_type(body_part_location):

        if (body_part_location == BodyPartLocation.hip or body_part_location == BodyPartLocation.knee
                or body_part_location == BodyPartLocation.ankle or body_part_location == BodyPartLocation.foot
                or body_part_location == BodyPartLocation.lower_back):
            return SorenessType.joint_related
        else:
            return SorenessType.muscle_related
