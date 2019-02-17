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

    def create_session_from_survey(self, session, return_dict=False, athlete_stats=None):
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
            if "clear_candidates" in session['post_session_survey'] and len(session['post_session_survey']['clear_candidates']) > 0:
                self.process_clear_status_answers(session['post_session_survey']['clear_candidates'],
                                                  athlete_stats,
                                                  event_date,
                                                  survey.soreness)
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


    def process_clear_status_answers(self, clear_candidates, athlete_stats, event_date, soreness):
        plan_event_date = format_date(event_date)
        stats_processing = StatsProcessing(athlete_stats.athlete_id,
                                           plan_event_date,
                                           DatastoreCollection())
        stats_processing.set_start_end_times()
        stats_processing.load_historical_data()
        soreness_list_25 = stats_processing.merge_soreness_from_surveys(
            stats_processing.get_readiness_soreness_list(stats_processing.last_25_days_readiness_surveys),
            stats_processing.get_ps_survey_soreness_list(stats_processing.last_25_days_ps_surveys)
            )
        # historic_soreness_list = athlete_stats.historic_soreness
        for q3_response in clear_candidates:
            body_part_location = BodyPartLocation(q3_response['body_part'])
            side = q3_response['side']
            severity = q3_response.get('severity', 0) # don't error out because of mobile bug
            pain = q3_response.get('pain', False)
            status = q3_response.get('status', HistoricSorenessStatus.dormant_cleared)
            if severity == 0:
                pain = True if "pain" in status else False
            if severity > 0:
                sore_part = Soreness()
                sore_part.body_part = BodyPart(body_part_location, None)
                sore_part.pain = pain
                sore_part.severity = severity
                sore_part.side = side
                sore_part.reported_date_time = event_date
                soreness.append(sore_part)
            if status in ['acute_pain', 'almost_persistent_2_pain_acute']:
                athlete_stats.historic_soreness = stats_processing.answer_acute_pain_question(athlete_stats.historic_soreness,
                                           soreness_list_25,
                                           body_part_location=body_part_location,
                                           side=side,
                                           is_pain=pain,
                                           question_response_date=plan_event_date,
                                           severity_value=severity)
            else:
                athlete_stats.historic_soreness = stats_processing.answer_persistent_2_question(athlete_stats.historic_soreness,
                                           soreness_list_25,
                                           body_part_location=body_part_location,
                                           side=side,
                                           is_pain=pain,
                                           question_response_date=plan_event_date,
                                           severity_value=severity,
                                           current_status=HistoricSorenessStatus[status])