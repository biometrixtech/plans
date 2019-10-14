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
    hip = 4
    groin = 5
    quads = 6
    knee = 7
    shin = 8
    ankle = 9
    foot = 10
    it_band = 11
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

    it_band_lateral_knee = 27
    hip_flexor = 28
    deltoid = 29

    # shin
    anterior_tibialis = 40
    peroneals_longus = 41

    # calves
    posterior_tibialis = 42
    soleus = 43
    gastrocnemius = 44

    # hamstrings
    bicep_femoris_long_head = 45
    bicep_femoris_short_head = 46
    semimembranosus = 47
    semitendinosus = 48

    # groin
    adductor_longus = 49
    adductor_magnus_anterior_fibers = 50
    adductor_magnus_posterior_fibers = 51
    adductor_brevis = 52
    gracilis = 53
    pectineus = 54

    # quads
    vastus_lateralis = 55
    vastus_medialis = 56
    vastus_intermedius = 57
    rectus_femoris = 58

    # hip_flexor
    tensor_fascia_latae = 59
    piriformis = 60

    # core_stabilizers
    iliopsoas = 61
    sartorius = 62

    # glutes
    gluteus_medius_anterior_fibers = 63
    gluteus_medius_posterior_fibers = 64
    gluteus_minimus = 65
    gluteus_maximus = 66

    quadratus_femoris = 67
    popliteus = 68
    lateral_rotators = 69

    upper_body = 91
    lower_body = 92
    full_body = 93
    

    @classmethod
    def get_muscle_group(cls, muscle):
        muscle_groups = cls.muscle_groups()

        if muscle in muscle_groups.keys():  # is a muscle group, return itself
            return muscle
        else:
            for key, value in muscle_groups.items():
                if muscle in value:  # is a muscle, return the group
                    return key
        return False  # joint or ligament

    @classmethod
    def get_muscles_for_group(cls, muscle_group):
        muscle_groups = cls.muscle_groups()
        if muscle_group in muscle_groups.keys():
            return muscle_groups[muscle_group]
        return False

    @classmethod
    def muscle_groups(cls):
        grouped_muscles = {
            cls.shin: [cls.anterior_tibialis, cls.peroneals_longus],
            cls.calves: [cls.posterior_tibialis, cls.soleus, cls.gastrocnemius],
            cls.hamstrings: [cls.bicep_femoris_long_head, cls.bicep_femoris_short_head, cls.semimembranosus, cls.semitendinosus],
            cls.groin: [cls.adductor_longus, cls.adductor_magnus_anterior_fibers, cls.adductor_magnus_posterior_fibers, cls.adductor_brevis, cls.gracilis, cls.pectineus],
            cls.quads: [cls.vastus_lateralis, cls.vastus_medialis, cls.vastus_intermedius, cls.rectus_femoris],
            cls.hip_flexor: [cls.tensor_fascia_latae, cls.piriformis],
            cls.core_stabilizers: [cls.iliopsoas, cls.soleus, cls.sartorius],
            cls.glutes: [cls.gluteus_medius_anterior_fibers, cls.gluteus_medius_posterior_fibers, cls.gluteus_minimus, cls.gluteus_maximus],
            cls.forearm: [],
            cls.biceps: [],
            cls.triceps: [],
            cls.deltoid: [],
            cls.chest: [],
            cls.upper_back_neck: [],
            cls.erector_spinae: [],
            cls.lats: [],
            cls.abdominals: []
        }
        return grouped_muscles


class BodyPartLocationText(object):
    def __init__(self, body_part_location):
        self.body_part_location = body_part_location

    def value(self):
        body_part_text = {'head': 'head',
                          'shoulder': 'shoulder',
                          'chest': 'pec',
                          'abdominals': 'abdominals',
                          'hip': 'hip',
                          'groin': 'adductor',
                          'quads': 'quad',
                          'knee': 'knee',
                          'shin': 'shin',
                          'ankle': 'ankle',
                          'foot': 'foot',
                          'it_band': 'outer thigh',
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
                          'triceps': 'triceps',
                          'deltoid': 'deltoid',
                          'hip_flexor': 'hip flexor',
                          'forearm': 'forearm',
                          'erector_spinae': 'erector spinae',
                          'core_stabilizers': 'core stabilizers',
                          'it_band_lateral_knee': 'outer knee'}

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