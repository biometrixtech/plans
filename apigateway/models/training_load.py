from models.training_volume import StandardErrorRange
from serialisable import Serialisable
from utils import format_datetime, parse_datetime


class TrainingLoad(object):
    def __init__(self):
        self.tissue_load = None
        self.force_load = None
        self.power_load = None

    def add_tissue_load(self, tissue_load):
        if self.tissue_load is None:
            self.tissue_load = StandardErrorRange(observed_value=0)
        if tissue_load is not None:
            self.tissue_load.add(tissue_load)

    def add_force_load(self, force_load):
        if self.force_load is None:
            self.force_load = StandardErrorRange(observed_value=0)
        if force_load is not None:
            self.force_load.add(force_load)

    def add_power_load(self, power_load):
        if self.power_load is None:
            self.power_load = StandardErrorRange(observed_value=0)
        if power_load is not None:
            self.power_load.add(power_load)


class SessionLoad(Serialisable, TrainingLoad):
    def __init__(self, session_id, user_id, event_date_time):
        super().__init__()
        self.session_id = session_id
        self.user_id = user_id
        self.event_date_time = event_date_time

    def json_serialise(self):
        ret = {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'event_date_time': format_datetime(self.event_date_time),
            'tissue_load': self.tissue_load.json_serialise() if self.tissue_load is not None else None,
            'force_load': self.force_load.json_serialise() if self.force_load is not None else None,
            'power_load': self.power_load.json_serialise() if self.power_load is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        session_load = cls(session_id=input_dict['session_id'], user_id=input_dict['user_id'], event_date_time=parse_datetime(input_dict['event_date_time']))
        session_load.tissue_load.json_deserialise(input_dict['tissue_load'])
        session_load.force_load.json_deserialise(input_dict['force_load'])
        session_load.power_load.json_deserialise(input_dict['power_load'])

        return session_load


