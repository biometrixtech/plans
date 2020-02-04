from enum import IntEnum, Enum
from datetime import datetime
from models.styles import LegendColor


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

    erector_spinae = 26 # lower back

    it_band_lateral_knee = 27
    hip_flexor = 28
    deltoid = 29

    deep_rotators_hip = 30
    obliques = 31

    # shin
    anterior_tibialis = 40
    peroneals_longus = 41

    # calves
    posterior_tibialis = 42
    soleus = 43
    gastrocnemius_medial = 44


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

    tensor_fascia_latae = 59 # hips
    piriformis = 60 # deep rotator of hip

    gastrocnemius_lateral = 61  # calves - was 75 but that was a duplicate
    sartorius = 62  # quads

    # glutes
    gluteus_medius_anterior_fibers = 63
    gluteus_medius_posterior_fibers = 64
    gluteus_minimus = 65
    gluteus_maximus = 66

    # deep rotators of the hip (30)
    quadratus_femoris = 67

    # knee?
    popliteus = 68

    external_obliques = 69  # abdominal

    # lower_back
    quadratus_lumorum = 70

    # hip_flexor
    psoas = 71
    iliacus = 72

    # core_stabilizers
    #iliopsoas = 61  # no longer used
    transverse_abdominis = 73
    internal_obliques = 74

    # abdominals
    rectus_abdominis = 75

    # upper back, traps, neck
    upper_trapezius = 76
    levator_scapulae = 77
    middle_trapezius = 78
    lower_trapezius = 79
    rhomboids = 80

    # chest
    pectoralis_minor = 81
    pectoralis_major = 82

    # deltoid (29)
    anterior_deltoid = 83
    medial_deltoid = 84
    posterior_deltoid = 85

    upper_body = 91
    lower_body = 92
    full_body = 93

    # merge
    semimembranosus_semitendinosus = 100
    anterior_adductors = 101
    rectus_femoris_vastus_intermedius = 102

    glute_med = 103

    upper_traps_levator_scapulae = 105
    middle_traps_rhomboids = 106

    pec_major_minor = 107

    hip_flexor_merge = 108

    rotator_cuff = 119
    teres_major = 120
    supraspinatus = 121
    subscapularis = 122
    infraspinatus = 123
    teres_minor = 124

    serratus_anterior = 125

    brachialis = 126
    biceps_brachii = 127
    brachioradialis = 128
    coracobrachialis = 129

    medial_head = 130
    lateral_head = 131
    long_head = 132

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
    def get_viz_muscle_group(cls, muscle):
        muscle_groups = cls.muscle_groups_viz()

        if muscle in muscle_groups.keys():  # is a muscle group, return itself
            return muscle
        else:
            for key, value in muscle_groups.items():
                if muscle in value:  # is a muscle, return the group
                    return key
        return False  # joint or ligament

    @classmethod
    def get_muscle_group_for_viz_group(cls, muscle):
        muscle_groups = cls.viz_groups_to_muscle_groups()

        if muscle in muscle_groups.keys():  # is a muscle group, return itself
            return muscle
        else:
            for key, value in muscle_groups.items():
                if muscle in value:  # is a muscle, return the group
                    return key
        return False  # joint or ligament

    @classmethod
    def get_viz_muscles_for_group(cls, muscle_group):
        muscle_groups = cls.muscle_groups_viz()
        if muscle_group in muscle_groups.keys():
            return muscle_groups[muscle_group]
        return False

    @classmethod
    def viz_groups_to_muscle_groups(cls):
        grouped_muscles = {
            cls.hamstrings: [cls.semimembranosus_semitendinosus],
            cls.groin: [cls.anterior_adductors],
            cls.quads: [cls.rectus_femoris_vastus_intermedius],
            cls.hip_flexor: [cls.hip_flexor_merge],
            cls.deep_rotators_hip: [cls.quadratus_femoris],
            cls.glutes: [cls.glute_med],
            cls.obliques: [cls.internal_obliques, cls.external_obliques],
            cls.upper_back_neck: [cls.upper_traps_levator_scapulae, cls.middle_traps_rhomboids],
            cls.chest: [cls.pec_major_minor]

        }
        return grouped_muscles

    @classmethod
    def muscle_groups_viz(cls):
        grouped_muscles = {
            cls.semimembranosus_semitendinosus: [cls.semimembranosus, cls.semitendinosus],
            cls.anterior_adductors: [cls.adductor_longus, cls.adductor_magnus_anterior_fibers, cls.adductor_brevis, cls.adductor_magnus_posterior_fibers],
            cls.rectus_femoris_vastus_intermedius: [cls.rectus_femoris, cls.vastus_intermedius],
            cls.hip_flexor_merge: [cls.psoas, cls.iliacus],
            cls.quadratus_femoris: [cls.piriformis, cls.quadratus_femoris], # this is intentional
            cls.glute_med: [cls.gluteus_medius_anterior_fibers, cls.gluteus_medius_posterior_fibers, cls.gluteus_minimus],
            cls.obliques: [cls.internal_obliques, cls.external_obliques],
            cls.upper_traps_levator_scapulae: [cls.upper_trapezius, cls.levator_scapulae],
            cls.middle_traps_rhomboids: [cls.middle_trapezius, cls.rhomboids],
            cls.pec_major_minor: [cls.pectoralis_minor, cls.pectoralis_major]

        }
        return grouped_muscles

    @classmethod
    def muscle_groups(cls):
        grouped_muscles = {
            cls.shin: [cls.anterior_tibialis, cls.peroneals_longus],
            cls.calves: [cls.posterior_tibialis, cls.soleus, cls.gastrocnemius_medial, cls.gastrocnemius_lateral],
            cls.hamstrings: [cls.bicep_femoris_long_head, cls.bicep_femoris_short_head, cls.semimembranosus, cls.semitendinosus],
            cls.groin: [cls.adductor_longus, cls.adductor_magnus_anterior_fibers, cls.adductor_magnus_posterior_fibers, cls.adductor_brevis, cls.gracilis, cls.pectineus],
            cls.quads: [cls.vastus_lateralis, cls.vastus_medialis, cls.vastus_intermedius, cls.rectus_femoris],
            cls.hip_flexor: [cls.tensor_fascia_latae, cls.psoas, cls.iliacus],
            cls.deep_rotators_hip: [cls.piriformis, cls.quadratus_femoris],
            cls.core_stabilizers: [cls.transverse_abdominis],
            cls.obliques: [cls.internal_obliques, cls.external_obliques],
            cls.glutes: [cls.gluteus_medius_anterior_fibers, cls.gluteus_medius_posterior_fibers, cls.gluteus_minimus, cls.gluteus_maximus],
            cls.forearm: [],
            cls.biceps: [],
            cls.triceps: [],
            cls.deltoid: [cls.anterior_deltoid, cls.medial_deltoid, cls.posterior_deltoid],
            cls.chest: [cls.pectoralis_minor, cls.pectoralis_major],
            cls.upper_back_neck: [cls.upper_trapezius, cls.levator_scapulae, cls.middle_trapezius, cls.lower_trapezius, cls.rhomboids],
            # cls.erector_spinae: [],
            cls.lats: [],
            cls.abdominals: [cls.rectus_abdominis],
            cls.lower_back: [cls.erector_spinae, cls.quadratus_lumorum]
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
                          'it_band_lateral_knee': 'outer knee',
                          'obliques': 'obliques',
                          'deep_rotators_hip': 'deep rotators of the hip'}

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


class BodyPartSideViz(object):
    def __init__(self, body_part_location, side, color):
        self.body_part_location = body_part_location
        self.side = side
        self.color = color

    def __hash__(self):
        #return hash((self.body_part_location.value, self.side, self.color))
        return hash((self.body_part_location.value, self.side))

    def __eq__(self, other):
        #return self.body_part_location == other.body_part_location and self.side == other.side and self.color == other.color

        return self.body_part_location == other.body_part_location and self.side == other.side

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    def json_serialise(self):
        return {
            "body_part_location": self.body_part_location.value,
            "side": self.side,
            "color": self.color.value if self.color is not None else None
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        legend_color = input_dict.get('color')
        if legend_color is not None:
            legend_color = LegendColor(legend_color)
        return cls(BodyPartLocation(input_dict['body_part_location']), input_dict['side'], legend_color)