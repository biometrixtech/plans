from models.soreness import BodyPart, BodyPartLocation, HistoricSoreness, Soreness, SorenessType


class SorenessCalculator(object):

    def __init__(self):
        self.surveys = []

    def get_soreness_summary_from_surveys(self, readiness_surveys, post_session_surveys,
                                          trigger_date_time, historic_soreness):
        """
        :param historic_soreness:
        :param readiness_surveys: DailyReadiness
        :param post_session_survey:
        :param trigger_date_time: datetime
        :return:
        """

        soreness_list = []

        for rs_survey in readiness_surveys:
            if (trigger_date_time.date() - rs_survey.get_event_date().date()).days < 2:
                self.update_soreness_list(soreness_list, rs_survey.soreness)
        for ps_survey in post_session_surveys:
            if (trigger_date_time.date() - ps_survey.event_date_time.date()).days < 2:
                self.update_soreness_list(soreness_list, ps_survey.survey.soreness)

        soreness_list = self.merge_current_historic_soreness(soreness_list, historic_soreness)
        return soreness_list

    def update_soreness_list(self, soreness_list, soreness_from_survey):
        for s in soreness_from_survey:
            updated = False
            for r in soreness_list:
                if (r.body_part.location.value == s.body_part.location.value and r.side == s.side and r.pain == s.pain):
                    r.severity = max([r.severity, s.severity])
                    updated = True
            if not updated:
                soreness_list.append(s)
        return soreness_list

    def merge_current_historic_soreness(self, soreness_list, historic_soreness):

        for h in range(0, len(historic_soreness)):
            historic_soreness_found = False
            for s in range(0, len(soreness_list)):
                if (soreness_list[s].body_part.location == historic_soreness[h].body_part_location and
                        soreness_list[s].side == historic_soreness[h].side and
                        soreness_list[s].pain == historic_soreness[h].is_pain):
                    soreness_list[s].historic_soreness_status = historic_soreness[h].historic_soreness_status
                    historic_soreness_found = True
            if not historic_soreness_found:
                new_soreness = Soreness()
                new_soreness.pain = historic_soreness[h].is_pain
                new_soreness.side = historic_soreness[h].side
                new_soreness.severity = historic_soreness[h].average_severity
                new_soreness.body_part = BodyPart(historic_soreness[h].body_part_location, None)
                new_soreness.historic_soreness_status = historic_soreness[h].historic_soreness_status
                new_soreness.daily = False
                soreness_list.append(new_soreness)

        return soreness_list


class BodyPartMapping(object):

    def get_soreness_type(self, body_part_location):

        if (body_part_location == BodyPartLocation.hip_flexor or body_part_location == BodyPartLocation.knee
                or body_part_location == BodyPartLocation.ankle or body_part_location == BodyPartLocation.foot
                or body_part_location == BodyPartLocation.lower_back):
            return SorenessType.joint_related
        else:
            return SorenessType.muscle_related