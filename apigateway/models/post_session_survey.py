from serialisable import Serialisable

from models.soreness import Soreness
from models.body_parts import BodyPart, BodyPartFactory
from models.soreness_base import BodyPartLocation
# from models.session import SessionType
import datetime
from utils import parse_datetime, format_datetime, parse_date


class PostSessionSurvey(Serialisable):
    
    def __init__(self,
                 event_date_time,
                 user_id,
                 session_id,
                 session_type,
                 survey=None
                 ):
        self.event_date_time = parse_datetime(event_date_time)  # datetime.datetime.strptime(event_date_time, "%Y-%m-%dT%H:%M:%SZ")
        self.event_date = self.event_date_time.strftime("%Y-%m-%d")
        self.user_id = user_id
        self.session_id = session_id
        # self.session_type = SessionType(session_type)
        self.survey = PostSurvey(survey, event_date_time)

    def get_id(self):
        return self.user_id

    def get_event_date(self):
        return self.event_date_time

    def json_serialise(self):
        ret = {
            'event_date': self.event_date,
            'user_id': self.user_id,
            # 'session_type': self.session_type.value,
            'session_id': self.session_id,
            'survey': self.survey.json_serialise()
        }
        return ret

    @classmethod
    def post_session_survey_from_training_session(cls, survey, user_id, session_id, session_type, event_date):
        if survey is not None:
            if survey.event_date is not None:
                post_session_survey = cls(format_datetime(survey.event_date), user_id, session_id, session_type)
            else:
                post_session_survey = cls(format_datetime(parse_date(event_date)), user_id, session_id, session_type)
            post_session_survey.survey = survey
            return post_session_survey
        else:
            return None


class PostSurvey(Serialisable):
    def __init__(self, survey=None, event_date=None):
        """
        :param dict survey:
        """
        if survey is not None:
            self.RPE = survey['RPE']
            self.soreness = [self._soreness_from_dict(s, event_date) for s in survey['soreness']]
            self.event_date = parse_datetime(event_date)

    def json_serialise(self):
        ret = {
            'RPE': self.RPE,
            'soreness': [item.json_serialise() for item in self.soreness],
            'event_date': format_datetime(self.event_date)
        }
        return ret

    @staticmethod
    def _soreness_from_dict(soreness_dict, event_date):
        if soreness_dict.get('reported_date_time') is None:
            soreness_dict['reported_date_time'] = event_date
        soreness = Soreness().json_deserialise(soreness_dict)
        # soreness.body_part = BodyPart(BodyPartLocation(soreness_dict['body_part']), None)
        # soreness.pain = soreness_dict.get('pain', False)
        # soreness.severity = soreness_dict['severity']
        # soreness.movement = soreness_dict.get('movement', None)
        # soreness.side = soreness_dict.get('side', None)
        # soreness.reported_date_time = parse_datetime(event_date)
        return soreness
