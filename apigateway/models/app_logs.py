from serialisable import Serialisable
from utils import format_date

class AppLogs(Serialisable):
    
    def __init__(self, user_id, updated_date):
        self.user_id = user_id
        self.updated_date = updated_date
        self.event_date = self.updated_date.split('T')[0]
        self.app_version = None
        self.os_name = None
        self.os_version = None
        self.plans_api_version = None

    def json_serialise(self):
        ret = {
            'user_id': self.user_id,
            'event_date': self.event_date,
            'updated_date': self.updated_date,
            'app_version': self.app_version,
            'os_name': self.os_name,
            'os_version': self.os_version,
            'plans_api_version': self.plans_api_version
        }
        return ret

    def get_filter_condition(self):
        return {"user_id": self.user_id,
                "event_date": self.event_date}



