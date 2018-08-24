from models.soreness import BodyPartLocation, SorenessType


class SorenessCalculator(object):

    def __init__(self):
        self.surveys = []

    def get_soreness_summary_from_surveys(self, last_daily_readiness_survey, last_post_session_surveys,
                                          trigger_date_time):
        """
        :param last_daily_readiness_survey: DailyReadiness
        :param last_post_session_survey:
        :param trigger_date_time: datetime
        :return:
        """

        soreness_list = []

        if last_daily_readiness_survey is not None:

            daily_readiness_survey_age = trigger_date_time - last_daily_readiness_survey.get_event_date()

            if daily_readiness_survey_age.total_seconds() <= 172800:  # within 48 hours so valid

                for s in last_daily_readiness_survey.soreness:
                    s.reported_date_time = last_daily_readiness_survey.get_event_date()
                    soreness_list.append(s)

        if last_post_session_surveys is not None:

            for last_post_session_survey in last_post_session_surveys:

                last_post_session_survey_age = trigger_date_time - last_post_session_survey.get_event_date()

                if last_post_session_survey_age.total_seconds() <= 172800:  # within 48 hours so valid

                    last_post_session_survey_datetime = last_post_session_survey.event_date_time

                    if (last_post_session_survey.survey.soreness is not None and
                            len(last_post_session_survey.survey.soreness) > 0):

                        for s in last_post_session_survey.survey.soreness:
                            updated = False
                            for r in range(0, len(soreness_list)):

                                post_soreness_within_24_hours = False
                                soreness_list_item_within_24_hours = False

                                post_soreness_age = trigger_date_time - last_post_session_survey_datetime
                                soreness_list_age = trigger_date_time - soreness_list[r].reported_date_time

                                if post_soreness_age.total_seconds() <= 86400: # within 24 hours
                                    post_soreness_within_24_hours = True

                                if soreness_list_age.total_seconds() <= 86400: # within 24 hours
                                    soreness_list_item_within_24_hours = True

                                if (soreness_list[r].body_part.location.value == s.body_part.location.value and
                                        soreness_list[r].side == s.side):
                                        if soreness_list_item_within_24_hours and post_soreness_within_24_hours:
                                            if soreness_list[r].severity <= s.severity:
                                                soreness_list[r].severity = s.severity
                                                soreness_list[r].reported_date_time = last_post_session_survey_datetime
                                            else:
                                                # keep existing soreness
                                                soreness_list[r].severity = soreness_list[r].severity
                                                soreness_list[r].reported_date_time = soreness_list[r].reported_date_time
                                        elif not soreness_list_item_within_24_hours and post_soreness_within_24_hours:
                                            soreness_list[r].severity = s.severity
                                            soreness_list[r].reported_date_time = last_post_session_survey_datetime
                                        elif soreness_list_item_within_24_hours and not post_soreness_within_24_hours:
                                            # keep existing soreness
                                            soreness_list[r].severity = soreness_list[r].severity
                                            soreness_list[r].reported_date_time = soreness_list[r].reported_date_time
                                        elif not soreness_list_item_within_24_hours and not post_soreness_within_24_hours:
                                            if soreness_list[r].reported_date_time < last_post_session_survey_datetime:
                                                soreness_list[r].severity = s.severity
                                                soreness_list[r].reported_date_time = last_post_session_survey_datetime

                                        updated = True
                            if not updated:
                                soreness_list.append(s)
                    #else:
                        # clear out any soreness to date
                    #    soreness_list = [s for s in soreness_list if s.reported_date_time >=
                    #                     last_post_session_survey_datetime]

        return soreness_list


class BodyPartMapping(object):

    def get_soreness_type(self, body_part_location):

        if (body_part_location == BodyPartLocation.hip_flexor or body_part_location == BodyPartLocation.knee
                or body_part_location == BodyPartLocation.ankle or body_part_location == BodyPartLocation.foot
                or body_part_location == BodyPartLocation.lower_back):
            return SorenessType.joint_related
        else:
            return SorenessType.muscle_related