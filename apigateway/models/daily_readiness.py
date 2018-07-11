from serialisable import Serialisable


class DailyReadiness(Serialisable):
    
    def __init__(self,
                 date_time,
                 user_id,
                 soreness,
                 sleep_quality,
                 readiness
                 ):
        self.date_time = date_time
        self.user_id = user_id
        self.soreness = soreness
        self.sleep_quality = int(sleep_quality)
        self.readiness = int(readiness)

    def get_id(self):
        return self.user_id

    def get_date(self):
        return self.date_time

    def json_serialise(self):
        ret = {
            'date_time': self.date_time,
            'user_id': self.user_id,
            'soreness': self.soreness,
            'sleep_quality': self.sleep_quality,
            'readiness': self.readiness,
            'sore_body_parts': [s['body_part'] for s in self.soreness if s['severity'] > 1]
        }
        return ret

    def get_soreness(self):
        soreness = []
        for body_part in self.soreness:
            body_part_filt = {'body_part': body_part['body_part'],
                              'severity': body_part['severity']}
            soreness.append(body_part_filt)
        return soreness

