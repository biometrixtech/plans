from enum import IntEnum, Enum
from datetime import datetime

class HistoricSorenessStatus(IntEnum):
    dormant_cleared = 0
    persistent_pain = 1
    persistent_2_pain = 2
    almost_persistent_pain = 3
    almost_persistent_2_pain = 4
    almost_persistent_2_pain_acute = 5
    persistent_soreness = 6
    persistent_2_soreness = 7
    almost_persistent_soreness = 8
    almost_persistent_2_soreness = 9
    acute_pain = 10
    almost_acute_pain = 11
    doms = 12


class BaseSoreness(object):
    def __init__(self):
        self.historic_soreness_status = HistoricSorenessStatus.dormant_cleared

    def is_acute_pain(self):
        if (self.historic_soreness_status is not None and (self.historic_soreness_status == HistoricSorenessStatus.acute_pain or
                                                           self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain_acute)):
            return True
        else:
            return False

    def is_persistent_soreness(self):
        if (self.historic_soreness_status is not None and (self.historic_soreness_status == HistoricSorenessStatus.persistent_soreness or
                                                           self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_soreness)):
            return True
        else:
            return False

    def is_persistent_pain(self):
        if (self.historic_soreness_status is not None and (self.historic_soreness_status == HistoricSorenessStatus.persistent_pain or
                                                           self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain)):
            return True
        else:
            return False

    def is_dormant_cleared(self):
        if (self.historic_soreness_status is None or
                self.historic_soreness_status == HistoricSorenessStatus.dormant_cleared or
                self.historic_soreness_status == HistoricSorenessStatus.almost_acute_pain or
                self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain or
                self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_soreness):
            return True
        else:
            return False


class BodyPartLocation(Enum):
    head = 0
    shoulder = 1
    chest = 2
    abdominals = 3
    hip_flexor = 4
    groin = 5
    quads = 6
    knee = 7
    shin = 8
    ankle = 9
    foot = 10
    outer_thigh = 11
    lower_back = 12
    general = 13
    glutes = 14
    hamstrings = 15
    calves = 16
    achilles = 17
    upper_back_neck = 18
    elbow = 19
    wrist = 20
    lats = 21
    biceps = 22
    triceps = 23
    forearm = 24
    core_stabilizers = 25
    erector_spinae = 26
    upper_body = 91
    lower_body = 92
    full_body = 93


class BodyPartLocationText(object):
    def __init__(self, body_part_location):
        self.body_part_location = body_part_location

    def value(self):
        body_part_text = {'head': 'head',
                          'shoulder': 'shoulder',
                          'chest': 'pecs',
                          'abdominals': 'abdominal',
                          'hip_flexor': 'hip',
                          'groin': 'groin',
                          'quads': 'quad',
                          'knee': 'knee',
                          'shin': 'shin',
                          'ankle': 'ankle',
                          'foot': 'foot',
                          'outer_thigh': 'IT band',
                          'lower_back': 'lower back',
                          'general': 'general',
                          'glutes': 'glute',
                          'hamstrings': 'hamstring',
                          'calves': 'calf',
                          'achilles': 'achilles',
                          'upper_back_neck': 'upper back',
                          'elbow': 'elbow',
                          'wrist': 'wrist',
                          'lats': 'lat',
                          'biceps': 'biceps',
                          'triceps': 'triceps'}

        return body_part_text[self.body_part_location.name]


class BodyPartSide(object):
    def __init__(self, body_part_location, side):
        self.body_part_location = body_part_location
        self.side = side

    def __hash__(self):
        return hash((self.body_part_location.value, self.side))

    def __eq__(self, other):
        return self.body_part_location == other.body_part_location and self.side == other.side

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    def json_serialise(self):
        return {
            "body_part_location": self.body_part_location.value,
            "side": self.side
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        return cls(BodyPartLocation(input_dict['body_part_location']), input_dict['side'])