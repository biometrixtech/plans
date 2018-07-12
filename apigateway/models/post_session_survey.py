from serialisable import Serialisable

from logic.soreness_and_injury import BodyPart, DailySoreness, BodyPartLocation

class PostSessionSurvey(Serialisable):
    
    def __init__(self,
                 event_date,
                 user_id,
                 session_id,
                 session_type,
                 survey=None
                 ):
        self.event_date = event_date
        self.user_id = user_id
        self.session_id = session_id
        self.session_type = session_type
        self.survey = PostSurvey(survey)


    def get_id(self):
        return self.user_id

    def get_event_date(self):
        return self.event_date

    def json_serialise(self):
        ret = {
            'event_date': self.event_date,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'session_id': self.session_id,
            'survey': self.survey.json_serialise()
        }
        return ret


class PostSurvey(Serialisable):
    def __init__(self, survey):
        """
        :param dict survey:
        """
        self.RPE = survey['RPE']
        self.soreness = []
        for sore in survey['soreness']:
            soreness = DailySoreness()
            soreness.body_part = BodyPart(BodyPartLocation(sore['body_part']), None)
            soreness.severity = sore['severity']
            self.soreness.append(soreness)

    def json_serialise(self):
        ret = {
            'RPE': self.RPE,
            'sorness': [self.soreness_to_dict(item) for item in self.soreness]
        }
        return ret

    def soreness_to_dict(self, soreness):
        return  {
                 "body_part": soreness.body_part.location.value,
                 "severity": soreness.severity
                 }