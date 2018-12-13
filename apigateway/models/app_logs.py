from serialisable import Serialisable

class AppLogs(Serialisable):
    
    def __init__(self, user_id, event_date):
        self.user_id = user_id
        self.event_date = event_date
        self.app_version = None
        self.device_type = None
        self.device_version = None
        self.users_api_version = None
        self.plans_api_version = None

    def json_serialise(self):
        ret = {
            'user_id': self.user_id,
            'event_date': self.event_date,
            'app_version': self.app_version,
            'device_type': self.device_type,
            'device_version': self.device_version,
            'users_api_version': self.users_api_version,
            'plans_api_version': self.plans_api_version
        }
        return ret

    def get_filter_condition(self):
        return {"user_id": self.user_id,
                "event_date": self.event_date}



