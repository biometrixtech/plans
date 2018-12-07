import datetime
from utils import parse_datetime, format_datetime, fix_early_survey_event_date
from fathomapi.utils.exceptions import InvalidSchemaException
from models.session import SessionType, SessionFactory, StrengthConditioningType
from models.post_session_survey import PostSurvey
from models.sport import SportName

class SurveyProcessing(object):

    def create_session_from_survey(self, session):
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
            survey.event_date == fix_early_survey_event_date(survey.event_date)
            session_data['post_session_survey'] = survey
        return self._create_session(session_type, session_data)


    def _create_session(self, session_type, data):
        session = SessionFactory().create(SessionType(session_type))
        self._update_session(session, data)
        return session


    def _update_session(self, session, data):
        for key, value in data.items():
            setattr(session, key, value)