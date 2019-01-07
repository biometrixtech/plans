import datetime
from utils import parse_datetime, format_datetime, fix_early_survey_event_date, format_date
from fathomapi.utils.exceptions import InvalidSchemaException
from models.session import SessionType, SessionFactory, StrengthConditioningType
from models.post_session_survey import PostSurvey
from models.sport import SportName
from models.soreness import BodyPart, BodyPartLocation, HistoricSorenessStatus, Soreness
from logic.stats_processing import StatsProcessing
from datastores.datastore_collection import DatastoreCollection

class SurveyProcessing(object):

    def create_session_from_survey(self, session, return_dict=False):
        event_date = parse_datetime(session['event_date'])
        session_type = session['session_type']
        try:
            sport_name = session['sport_name']
            sport_name = SportName(sport_name)
        except:
            sport_name = SportName(None)
        try:
            strength_and_conditioning_type = session['strength_and_conditioning_type']
            strength_and_conditioning_type = StrengthConditioningType(strength_and_conditioning_type)
        except:
            strength_and_conditioning_type = StrengthConditioningType(None)
        try:
            duration = session["duration"]
        except:
            raise InvalidSchemaException("Missing required parameter duration")
        description = session.get('description', "")
        session_event_date = format_datetime(event_date)
        session_data = {"sport_name": sport_name,
                        "strength_and_conditioning_type": strength_and_conditioning_type,
                        "description": description,
                        "duration_minutes": duration,
                        "event_date": session_event_date}
        if 'post_session_survey' in session:
            survey = PostSurvey(event_date=session['post_session_survey']['event_date'],
                                survey=session['post_session_survey'])
            # TODO: if the frontend error is fixed, this needs to be removed
            if survey.event_date.hour < 3 and event_date.hour >= 3:
                session_data['event_date'] = format_datetime(event_date - datetime.timedelta(days=1))
            survey.event_date = fix_early_survey_event_date(survey.event_date)
            session_data['post_session_survey'] = survey
        if return_dict:
            return session_data
        else:
            return self._create_session(session_type, session_data)


    def _create_session(self, session_type, data):
        session = SessionFactory().create(SessionType(session_type))
        self._update_session(session, data)
        return session


    def _update_session(self, session, data):
        for key, value in data.items():
            setattr(session, key, value)


    def _process_clear_status_answers(self, clear_candidates, athlete_stats, event_date, daily_readiness):
        stats_processing = StatsProcessing(athlete_stats.athlete_id,
                                           format_date(event_date),
                                           DatastoreCollection())
        soreness_list_25 = stats_processing.merge_soreness_from_surveys(
            stats_processing.get_readiness_soreness_list(stats_processing.last_25_days_readiness_surveys),
            stats_processing.get_ps_survey_soreness_list(stats_processing.last_25_days_ps_surveys)
            )
        historic_soreness_list = athlete_stats.historic_soreness
        for q3_response in clear_candidates:
            if q3_response['severity'] > 0:
                sore_part = Soreness()
                sore_part.body_part = BodyPart(BodyPartLocation(q3_response['body_part']), None)
                sore_part.pain = q3_response.get('pain', False)
                sore_part.severity = q3_response['severity']
                sore_part.side = q3_response['side']
                sore_part.reported_date_time = event_date
                daily_readiness.soreness.append(sore_part)
            if "acute" in q3_response['status']:
                if not q3_response['pain'] or q3_response['severity'] == 0:
                    hist_soreness = [h for h in athlete_stats.historic_soreness if h.body_part_location == q3_response['body_part'] and
                                                                                   h.side == q3_response['side'] and
                                                                                   h.ask_acute_pain_question][0]
                    athlete_stats.historic_soreness.remove(hist_soreness)
                    hist_soreness.ask_acute_pain_question = False
                    hist_soreness.historic_soreness_status = HistoricSorenessStatus.dormant_cleared
                    athlete_stats.historic_soreness.append(hist_soreness)
                else:
                    athlete_stats.historic_soreness = stats_processing.answer_acute_pain_question(athlete_stats.historic_soreness,
                                           soreness_list_25,
                                           body_part_location=q3_response['body_part'],
                                           side=q3_response['side'],
                                           question_response_date=format_date(event_date),
                                           severity_value=q3_response['severity'])
            elif "persistent" in q3_response['status']:
                if ("pain" in q3_response['status'] and not q3_response["pain"]) or ("soreness" in q3_response['status'] and q3_response["pain"]) or q3_response['severity'] == 0:
                    hist_soreness = [h for h in athlete_stats.historic_soreness if h.body_part_location == q3_response['body_part'] and
                                                                                   h.side == q3_response['side'] and
                                                                                   h.historic_soreness_status.name == q3_response['status'] and
                                                                                   h.ask_persistent_2_question][0]
                    athlete_stats.historic_soreness.remove(hist_soreness)
                    hist_soreness.ask_acute_pain_question = False
                    hist_soreness.historic_soreness_status = HistoricSorenessStatus.dormant_cleared
                    athlete_stats.historic_soreness.append(hist_soreness)
                else:
                    athlete_stats.historic_soreness = stats_processing.answer_persistent_2_question(athlete_stats.historic_soreness,
                                           soreness_list_25,
                                           body_part_location=q3_response['body_part'],
                                           side=q3_response['side'],
                                           is_pain=q3_response['pain'],
                                           question_response_date=format_date(event_date),
                                           severity_value=q3_response['severity'])