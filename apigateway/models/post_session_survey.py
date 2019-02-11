from serialisable import Serialisable

from models.soreness import Soreness, BodyPartLocation, BodyPart
from models.session import SessionType
import datetime
from utils import parse_datetime, format_datetime

class PostSessionSurvey(Serialisable):
    
    def __init__(self,
                 event_date_time,
                 user_id,
                 session_id,
                 session_type,
                 survey=None
                 ):
        self.event_date_time = datetime.datetime.strptime(event_date_time, "%Y-%m-%dT%H:%M:%SZ")
        self.event_date = self.event_date_time.strftime("%Y-%m-%d")
        self.user_id = user_id
        self.session_id = session_id
        self.session_type = SessionType(session_type)
        self.survey = PostSurvey(survey, event_date_time)


    def get_id(self):
        return self.user_id

    def get_event_date(self):
        return self.event_date_time

    def json_serialise(self):
        ret = {
            'event_date': self.event_date,
            'user_id': self.user_id,
            'session_type': self.session_type.value,
            'session_id': self.session_id,
            'survey': self.survey.json_serialise()
        }
        return ret


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

    def _soreness_from_dict(self, soreness_dict, event_date):
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(soreness_dict['body_part']), None)
        soreness.pain = soreness_dict.get('pain', False)
        soreness.severity = soreness_dict['severity']
        soreness.movement = soreness_dict.get('movement', None)
        soreness.side = self._key_present('side', soreness_dict)
        soreness.reported_date_time = parse_datetime(event_date)
        return soreness

    def _key_present(self, key_name, dictionary):
        if key_name in dictionary:
            return dictionary[key_name]
        else:
            return None
