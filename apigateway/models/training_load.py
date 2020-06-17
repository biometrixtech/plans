from models.training_volume import StandardErrorRange
from serialisable import Serialisable
from utils import format_datetime, parse_datetime


class TrainingLoad(object):
    def __init__(self):
        self.tissue_load = None
        self.force_load = None
        self.power_load = None
        self.rpe_load = None
        self.strength_endurance_cardiorespiratory_load = None
        self.strength_endurance_strength_load = None
        self.power_drill_load = None
        self.maximal_strength_hypertrophic_load = None
        self.power_explosive_action_load = None
        self.not_tracked_load = None

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

    def add_rpe_load(self, rpe_load):
        if self.rpe_load is None:
            self.rpe_load = StandardErrorRange(observed_value=0)
        if rpe_load is not None:
            self.rpe_load.add(rpe_load)

    def add_strength_endurance_cardiorespiratory_load(self, load):
        if self.strength_endurance_cardiorespiratory_load is None:
            self.strength_endurance_cardiorespiratory_load = StandardErrorRange(observed_value=0)
        if self.strength_endurance_cardiorespiratory_load is not None:
            self.strength_endurance_cardiorespiratory_load.add(load)

    def add_strength_endurance_strength_load(self, load):
        if self.strength_endurance_strength_load is None:
            self.strength_endurance_strength_load = StandardErrorRange(observed_value=0)
        if self.strength_endurance_strength_load is not None:
            self.strength_endurance_strength_load.add(load)

    def add_power_drill_load(self, load):
        if self.power_drill_load is None:
            self.power_drill_load = StandardErrorRange(observed_value=0)
        if self.power_drill_load is not None:
            self.power_drill_load.add(load)

    def add_maximal_strength_hypertrophic_load(self, load):
        if self.maximal_strength_hypertrophic_load is None:
            self.maximal_strength_hypertrophic_load = StandardErrorRange(observed_value=0)
        if self.maximal_strength_hypertrophic_load is not None:
            self.maximal_strength_hypertrophic_load.add(load)

    def add_power_explosive_action_load(self, load):
        if self.power_explosive_action_load is None:
            self.power_explosive_action_load = StandardErrorRange(observed_value=0)
        if self.power_explosive_action_load is not None:
            self.power_explosive_action_load.add(load)

    def add_not_tracked_load(self, load):
        if self.not_tracked_load is None:
            self.not_tracked_load = StandardErrorRange(observed_value=0)
        if self.not_tracked_load is not None:
            self.not_tracked_load.add(load)


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
            'power_load': self.power_load.json_serialise() if self.power_load is not None else None,
            'rpe_load': self.rpe_load.json_serialise() if self.rpe_load is not None else None,
            'strength_endurance_cardiorespiratory_load': self.strength_endurance_cardiorespiratory_load.json_serialise() if self.strength_endurance_cardiorespiratory_load is not None else None,
            'strength_endurance_strength_load': self.strength_endurance_strength_load.json_serialise() if self.strength_endurance_strength_load is not None else None,
            'power_drill_load': self.power_drill_load.json_serialise() if self.power_drill_load is not None else None,
            'maximal_strength_hypertrophic_load': self.maximal_strength_hypertrophic_load.json_serialise() if self.maximal_strength_hypertrophic_load is not None else None,
            'power_explosive_action_load': self.power_explosive_action_load.json_serialise() if self.power_explosive_action_load is not None else None,
            'not_tracked_load': self.not_tracked_load.json_serialise() if self.not_tracked_load is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        session_load = cls(session_id=input_dict['session_id'], user_id=input_dict['user_id'], event_date_time=parse_datetime(input_dict['event_date_time']))
        session_load.tissue_load = StandardErrorRange.json_deserialise(input_dict['tissue_load'])
        session_load.force_load = StandardErrorRange.json_deserialise(input_dict['force_load'])
        session_load.power_load = StandardErrorRange.json_deserialise(input_dict['power_load'])
        session_load.rpe_load = StandardErrorRange.json_deserialise(input_dict['rpe_load'])
        session_load.strength_endurance_cardiorespiratory_load = StandardErrorRange.json_deserialise(input_dict['strength_endurance_cardiorespiratory_load'])
        session_load.strength_endurance_strength_load = StandardErrorRange.json_deserialise(input_dict['strength_endurance_strength_load'])
        session_load.power_drill_load = StandardErrorRange.json_deserialise(input_dict['power_drill_load'])
        session_load.maximal_strength_hypertrophic_load = StandardErrorRange.json_deserialise(input_dict['maximal_strength_hypertrophic_load'])
        session_load.power_explosive_action_load = StandardErrorRange.json_deserialise(input_dict['power_explosive_action_load'])
        session_load.not_tracked_load = StandardErrorRange.json_deserialise(input_dict['not_tracked_load'])

        return session_load


