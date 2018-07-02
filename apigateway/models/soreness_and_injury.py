from serialisable import Serialisable
#import uuid


class SorenessAndInjury(Serialisable):
    
    def __init__(self,
                 date,
                 user_id,
                 soreness,
                 sleep_quality,
                 readiness
                 ):
        self.date = date
        self.user_id = user_id
        self.soreness = soreness
        self.sleep_quality = sleep_quality
        self.readiness = readiness

        # self.s3_files = s3_files
        # self.sensor_ids = set()
    def get_id(self):
        return self.user_id

    def json_serialise(self):
        ret = {
            'date': self.date,
            'user_id': self.user_id,
            'soreness': self.soreness,
            'sleep_quality': self.sleep_quality,
            'readiness': self.readiness,
        }
        return ret
