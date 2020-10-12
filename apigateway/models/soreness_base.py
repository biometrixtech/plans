from enum import IntEnum, Enum

from models.compensation_source import CompensationSource
from models.styles import LegendColor
from models.training_volume import StandardErrorRange
from serialisable import Serialisable


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
    # lats muscle group
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

    forearm_intrinsic_muscles = 32
    forearm_extrinsic_muscles = 33

    intrinsic_muscles_of_spine = 34
    diaphragm = 35
    pelvic_floor = 36

    latissmus_dorsi = 37

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

    tricep_brachii_medial_head = 130
    tricep_brachii_lateral_head = 131
    tricep_brachii_long_head = 132

    @classmethod
    def get_muscle_group(cls, muscle):
        muscle_groups = cls.muscle_groups()

        if muscle in muscle_groups:  # is a muscle group, return itself
            return muscle
        else:
            for key, value in muscle_groups.items():
                if muscle in value:  # is a muscle, return the group
                    return key
        return False  # joint or ligament

    @classmethod
    def get_muscles_for_group(cls, muscle_group):
        muscle_groups = cls.muscle_groups()
        if muscle_group in muscle_groups:
            return muscle_groups[muscle_group]
        return False

    @classmethod
    def get_viz_muscle_group(cls, muscle):
        muscle_groups = cls.muscle_groups_viz()

        if muscle in muscle_groups:  # is a muscle group, return itself
            return muscle
        else:
            for key, value in muscle_groups.items():
                if muscle in value:  # is a muscle, return the group
                    return key
        return False  # joint or ligament

    @classmethod
    def get_muscle_group_for_viz_group(cls, muscle):
        muscle_groups = cls.viz_groups_to_muscle_groups()

        if muscle in muscle_groups:  # is a muscle group, return itself
            return muscle
        else:
            for key, value in muscle_groups.items():
                if muscle in value:  # is a muscle, return the group
                    return key
        return False  # joint or ligament

    @classmethod
    def get_viz_muscles_for_group(cls, muscle_group):
        muscle_groups = cls.muscle_groups_viz()
        if muscle_group in muscle_groups:
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
            cls.pec_major_minor: [cls.pectoralis_minor, cls.pectoralis_major],
            cls.forearm: [cls.forearm_intrinsic_muscles, cls.forearm_extrinsic_muscles],
            cls.biceps: [cls.brachialis, cls.biceps_brachii, cls.brachioradialis, cls.coracobrachialis],
            cls.triceps: [cls.tricep_brachii_medial_head, cls.tricep_brachii_lateral_head, cls.tricep_brachii_long_head],
            cls.lats: [cls.latissmus_dorsi, cls.teres_major]

        }
        return grouped_muscles

    @classmethod
    def muscle_groups(cls):
        grouped_muscles = {
            cls.shin: [cls.anterior_tibialis, cls.peroneals_longus],
            cls.calves: [cls.posterior_tibialis, cls.soleus, cls.gastrocnemius_medial, cls.gastrocnemius_lateral, cls.popliteus],
            cls.hamstrings: [cls.bicep_femoris_long_head, cls.bicep_femoris_short_head, cls.semimembranosus, cls.semitendinosus],
            cls.groin: [cls.adductor_longus, cls.adductor_magnus_anterior_fibers, cls.adductor_magnus_posterior_fibers, cls.adductor_brevis, cls.gracilis, cls.pectineus],
            cls.quads: [cls.vastus_lateralis, cls.vastus_medialis, cls.vastus_intermedius, cls.rectus_femoris],
            cls.hip_flexor: [cls.tensor_fascia_latae, cls.psoas, cls.iliacus],
            cls.deep_rotators_hip: [cls.piriformis, cls.quadratus_femoris],
            cls.core_stabilizers: [cls.transverse_abdominis, cls.intrinsic_muscles_of_spine, cls.diaphragm, cls.pelvic_floor],
            cls.obliques: [cls.internal_obliques, cls.external_obliques],
            cls.glutes: [cls.gluteus_medius_anterior_fibers, cls.gluteus_medius_posterior_fibers, cls.gluteus_minimus, cls.gluteus_maximus],
            cls.forearm: [cls.forearm_intrinsic_muscles, cls.forearm_extrinsic_muscles],
            cls.biceps: [cls.brachialis, cls.biceps_brachii, cls.brachioradialis, cls.coracobrachialis],
            cls.triceps: [cls.tricep_brachii_medial_head, cls.tricep_brachii_lateral_head, cls.tricep_brachii_long_head],
            cls.deltoid: [cls.anterior_deltoid, cls.medial_deltoid, cls.posterior_deltoid],
            cls.serratus_anterior: [],
            cls.chest: [cls.pectoralis_minor, cls.pectoralis_major],
            cls.upper_back_neck: [cls.upper_trapezius, cls.levator_scapulae, cls.middle_trapezius, cls.lower_trapezius, cls.rhomboids],
            # cls.erector_spinae: [],
            cls.lats: [cls.latissmus_dorsi, cls.teres_major],
            cls.abdominals: [cls.rectus_abdominis],
            cls.lower_back: [cls.erector_spinae, cls.quadratus_lumorum],
            cls.rotator_cuff: [cls.supraspinatus, cls.subscapularis, cls.infraspinatus, cls.teres_minor]
        }
        return grouped_muscles


class BodyPartGeneralLocation(object):
    def __init__(self):
        self.upper_body_muscles = [
            BodyPartLocation.forearm_intrinsic_muscles,
            BodyPartLocation.forearm_extrinsic_muscles,
            BodyPartLocation.brachialis,
            BodyPartLocation.biceps_brachii,
            BodyPartLocation.brachioradialis,
            BodyPartLocation.coracobrachialis,
            BodyPartLocation.tricep_brachii_medial_head,
            BodyPartLocation.tricep_brachii_lateral_head,
            BodyPartLocation.tricep_brachii_long_head,
            BodyPartLocation.anterior_deltoid,
            BodyPartLocation.medial_deltoid,
            BodyPartLocation.posterior_deltoid,
            BodyPartLocation.pectoralis_major,
            BodyPartLocation.pectoralis_minor,
            BodyPartLocation.upper_trapezius,
            BodyPartLocation.levator_scapulae,
            BodyPartLocation.middle_trapezius,
            BodyPartLocation.rhomboids,
            BodyPartLocation.lower_trapezius,
            BodyPartLocation.supraspinatus,
            BodyPartLocation.subscapularis,
            BodyPartLocation.infraspinatus,
            BodyPartLocation.teres_minor,
            BodyPartLocation.erector_spinae,
            BodyPartLocation.quadratus_lumorum,
            BodyPartLocation.latissmus_dorsi,
            BodyPartLocation.teres_major,
            BodyPartLocation.rectus_abdominis,
            BodyPartLocation.transverse_abdominis,
            BodyPartLocation.intrinsic_muscles_of_spine,
            BodyPartLocation.diaphragm,
            BodyPartLocation.pelvic_floor,
            BodyPartLocation.external_obliques,
            BodyPartLocation.internal_obliques
        ]
        self.lower_body_muscles = [
            BodyPartLocation.gluteus_maximus,
            BodyPartLocation.gluteus_medius_anterior_fibers,
            BodyPartLocation.gluteus_medius_posterior_fibers,
            BodyPartLocation.gluteus_minimus,
            BodyPartLocation.quadratus_femoris,
            BodyPartLocation.piriformis,
            BodyPartLocation.psoas,
            BodyPartLocation.iliacus,
            BodyPartLocation.tensor_fascia_latae,
            BodyPartLocation.vastus_lateralis,
            BodyPartLocation.vastus_medialis,
            BodyPartLocation.rectus_femoris,
            BodyPartLocation.gracilis,
            BodyPartLocation.pectineus,
            BodyPartLocation.sartorius,
            BodyPartLocation.adductor_longus,
            BodyPartLocation.adductor_magnus_anterior_fibers,
            BodyPartLocation.adductor_magnus_posterior_fibers,
            BodyPartLocation.adductor_brevis,
            BodyPartLocation.bicep_femoris_long_head,
            BodyPartLocation.bicep_femoris_short_head,
            BodyPartLocation.semimembranosus,
            BodyPartLocation.semitendinosus,
            BodyPartLocation.posterior_tibialis,
            BodyPartLocation.soleus,
            BodyPartLocation.gastrocnemius_medial,
            BodyPartLocation.gastrocnemius_lateral,
            BodyPartLocation.popliteus,
            BodyPartLocation.peroneals_longus,
            BodyPartLocation.anterior_tibialis
        ]
        self.upper_body_joints = [
            BodyPartLocation.elbow,
            BodyPartLocation.wrist,
            BodyPartLocation.shoulder
        ]
        self.lower_body_joints = [
            BodyPartLocation.hip,
            BodyPartLocation.knee,
            BodyPartLocation.ankle,
            BodyPartLocation.foot
        ]
        self.lower_body_ligaments = [
            BodyPartLocation.it_band,
            BodyPartLocation.it_band_lateral_knee,
            BodyPartLocation.achilles
        ]

    def is_lower_body(self, body_part_location):

        if body_part_location in self.lower_body_joints or body_part_location in self.lower_body_ligaments or body_part_location in self.lower_body_muscles:
            return True
        else:
            return False

    def is_upper_body(self, body_part_location):

        if body_part_location in self.upper_body_joints or body_part_location in self.upper_body_muscles:
            return True
        else:
            return False


class BodyPartSystems(object):
    def __init__(self):
        self.local_stabilizer_system = [
            BodyPartLocation.transverse_abdominis,
            BodyPartLocation.internal_obliques,
            BodyPartLocation.intrinsic_muscles_of_spine,
            BodyPartLocation.diaphragm,
            BodyPartLocation.pelvic_floor,
            BodyPartLocation.quadratus_lumorum,
            BodyPartLocation.psoas
        ]
        self.global_stabilization_system = [
            BodyPartLocation.quadratus_lumorum,
            BodyPartLocation.psoas,
            BodyPartLocation.piriformis,
            BodyPartLocation.gluteus_medius_anterior_fibers,
            BodyPartLocation.gluteus_medius_posterior_fibers,
            BodyPartLocation.gluteus_minimus,
            BodyPartLocation.rectus_abdominis,
            BodyPartLocation.external_obliques,
            BodyPartLocation.erector_spinae
        ]
        self.deep_longitudinal_subsystem = [
            BodyPartLocation.erector_spinae,
            BodyPartLocation.rhomboids,
            BodyPartLocation.adductor_magnus_anterior_fibers,
            BodyPartLocation.adductor_magnus_posterior_fibers,
            BodyPartLocation.bicep_femoris_long_head,
            BodyPartLocation.bicep_femoris_short_head,
            BodyPartLocation.piriformis,
            BodyPartLocation.deep_rotators_hip,
            BodyPartLocation.peroneals_longus
        ]
        self.posterior_oblique_subsystem = [
            BodyPartLocation.latissmus_dorsi,
            BodyPartLocation.lower_trapezius,
            BodyPartLocation.gluteus_maximus,
            BodyPartLocation.gluteus_medius_anterior_fibers,
            BodyPartLocation.gluteus_medius_posterior_fibers
        ]
        self.anterior_oblique_subsystem = [
            BodyPartLocation.rectus_abdominis,
            BodyPartLocation.external_obliques,
            #BodyPartLocation.anterior_adductors,
            BodyPartLocation.pectineus,
            BodyPartLocation.adductor_longus,
            BodyPartLocation.adductor_magnus_anterior_fibers,
            BodyPartLocation.serratus_anterior,
            BodyPartLocation.pectoralis_major
        ]
        self.intrinsic_stabilization_subsystem = [
            BodyPartLocation.transverse_abdominis,
            BodyPartLocation.internal_obliques,
            BodyPartLocation.intrinsic_muscles_of_spine,
            BodyPartLocation.diaphragm,
            BodyPartLocation.pelvic_floor,
            BodyPartLocation.quadratus_lumorum,
            BodyPartLocation.psoas
        ]
        self.core_stabilizers = [
            BodyPartLocation.intrinsic_muscles_of_spine,
            BodyPartLocation.diaphragm,
            BodyPartLocation.transverse_abdominis,
            BodyPartLocation.pelvic_floor,
            BodyPartLocation.internal_obliques,
            BodyPartLocation.external_obliques,
            BodyPartLocation.rectus_abdominis,
            BodyPartLocation.erector_spinae
        ]
        self.lateral_subsystem = [
            BodyPartLocation.gluteus_medius_anterior_fibers,
            BodyPartLocation.gluteus_medius_posterior_fibers,
            BodyPartLocation.tensor_fascia_latae,
            BodyPartLocation.adductor_longus,
            BodyPartLocation.adductor_magnus_anterior_fibers,
            BodyPartLocation.adductor_brevis,
            BodyPartLocation.adductor_magnus_posterior_fibers,
            BodyPartLocation.pectineus,
            BodyPartLocation.gracilis,
            BodyPartLocation.quadratus_lumorum
        ]

        self.shoulder_stabilizers = [
            BodyPartLocation.supraspinatus,
            BodyPartLocation.subscapularis,
            BodyPartLocation.infraspinatus,
            BodyPartLocation.teres_minor
        ]

        self.scapula_stabilizers = [
            BodyPartLocation.serratus_anterior,
            BodyPartLocation.levator_scapulae,
            BodyPartLocation.rhomboids
        ]

    def get_movemement_system(self, movement_system_name):

        if movement_system_name is None:
            return None
        elif movement_system_name == "Deep Longitudinal Subsystem (DLS)":
            return self.deep_longitudinal_subsystem
        elif movement_system_name == "Posterior Oblique Subsystem (POS)":
            return self.posterior_oblique_subsystem
        elif movement_system_name == "Lateral Subsystem (LS)":
            return self.lateral_subsystem
        elif movement_system_name == "Anterior Oblique Subsystem (AOS)":
            return self.anterior_oblique_subsystem
        elif movement_system_name == "Core Stabilizers (Bracing)":
            return self.core_stabilizers
        elif movement_system_name == "Intrinsic Stabilization Subsystem (ISS) (Drawing In)":
            return self.intrinsic_stabilization_subsystem
        elif movement_system_name == "Shoulder Stabilizers":
            return self.shoulder_stabilizers
        elif movement_system_name == "Scapula Stabilizers":
            return self.scapula_stabilizers
        else:
            return getattr(self, movement_system_name)

    @classmethod
    def get_functional_movement_type_name(cls, movement_system_name):
        if movement_system_name is not None:
            if movement_system_name == "Deep Longitudinal Subsystem (DLS)":
                return 'deep_longitudinal_subsystem'
            elif movement_system_name == "Posterior Oblique Subsystem (POS)":
                return 'posterior_oblique_subsystem'
            elif movement_system_name == "Lateral Subsystem (LS)":
                return 'lateral_subsystem'
            elif movement_system_name == "Anterior Oblique Subsystem (AOS)":
                return 'anterior_oblique_subsystem'
            elif movement_system_name == "Core Stabilizers (Bracing)":
                return 'core_stabilizers'
            elif movement_system_name == "Intrinsic Stabilization Subsystem (ISS) (Drawing In)":
                return 'intrinsic_stabilization_subsystem'
            elif movement_system_name == "Shoulder Stabilizers":
                return 'shoulder_stabilizers'
            elif movement_system_name == "Scapula Stabilizers":
                return 'scapula_stabilizers'
        return None


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

    def to_string(self):
        return str(self.body_part_location.value) + "_" + str(self.side)

    @staticmethod
    def from_string(body_part_string):
        data = body_part_string.split("_")
        return BodyPartSide(BodyPartLocation(int(data[0])), int(data[1]))



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


class BodyPartFunction(Enum):
    prime_mover = 0
    antagonist = 1
    synergist = 2
    stabilizer = 3
    fixator = 4

    def get_ranking(self):
        rankings = {
            'prime_mover': 0,
            'antagonist': 3,
            'synergist': 2,
            'stabilizer': 1,
            'fixator': 4,
        }
        return rankings[self.name]

    @classmethod
    def merge(cls, function1, function2):
        if function1 is not None and function2 is not None:
            if function1 == function2:
                return function1
            elif function1.get_ranking() < function2.get_ranking():
                return function1
            else:
                return function2
        elif function1 is not None:
            return function1
        elif function2 is not None:
            return function2
        else:
            return None


class BodyPartFunctionalMovement(Serialisable):
    def __init__(self, body_part_side):
        self.body_part_side = body_part_side
        self.concentric_load = StandardErrorRange()
        self.isometric_load = StandardErrorRange()
        self.eccentric_load = StandardErrorRange()
        self.compensated_concentric_load = StandardErrorRange()
        self.compensated_isometric_load = StandardErrorRange()
        self.compensated_eccentric_load = StandardErrorRange()
        self.compensating_causes_load = []
        self.is_compensating = False
        #self.compensation_source_load = None
        self.body_part_function = None
        #self.inhibited = 0
        #self.weak = 0
        #self.tight = 0
        #self.inflamed = 0
        #self.long = 0

        #self.total_normalized_load = StandardErrorRange()

    def total_load(self):

        total_load = StandardErrorRange(observed_value=0)
        total_load.add(self.concentric_load)
        total_load.add(self.isometric_load)
        total_load.add(self.eccentric_load)
        total_load.add(self.compensated_concentric_load)
        total_load.add(self.compensated_isometric_load)
        total_load.add(self.compensated_eccentric_load)

        return total_load

    def total_concentric_load(self):

        total_load = StandardErrorRange(observed_value=0)
        total_load.add(self.concentric_load)
        total_load.add(self.compensated_concentric_load)

        return total_load

    def total_isometric_load(self):

        total_load = StandardErrorRange(observed_value=0)
        total_load.add(self.isometric_load)
        total_load.add(self.compensated_isometric_load)

        return total_load

    def total_eccentric_load(self):

        total_load = StandardErrorRange(observed_value=0)
        total_load.add(self.eccentric_load)
        total_load.add(self.compensated_eccentric_load)

        return total_load

    def __hash__(self):
        return hash((self.body_part_side.body_part_location.value, self.body_part_side.side))

    def __eq__(self, other):
        return self.body_part_side.body_part_location == other.body_part_side.body_part_location and self.body_part_side.side == other.body_part_side.side

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    def json_serialise(self):
        return {
                'body_part_side': self.body_part_side.json_serialise(),
                'concentric_load': self.concentric_load.json_serialise(),
                'isometric_load': self.isometric_load.json_serialise(),
                'eccentric_load': self.eccentric_load.json_serialise(),
                'compensated_concentric_load': self.compensated_concentric_load.json_serialise(),
                'compensated_isometric_load': self.compensated_isometric_load.json_serialise(),
                'compensated_eccentric_load': self.compensated_eccentric_load.json_serialise(),
                'compensating_causes_load': [c.json_serialise() for c in self.compensating_causes_load],
                'is_compensating': self.is_compensating,
                #'compensation_source_load': self.compensation_source_load.value if self.compensation_source_load is not None else None,
                'body_part_function': self.body_part_function.value if self.body_part_function is not None else None,
                #'inhibited': self.inhibited if self.inhibited is not None else None,
                #'weak': self.weak,
                #'tight': self.tight,
                #'inflamed': self.inflamed,
                #'long': self.long,
                #'total_normalized_load': self.total_normalized_load
            }

    @classmethod
    def json_deserialise(cls, input_dict):
        movement = cls(BodyPartSide.json_deserialise(input_dict['body_part_side']))
        movement.concentric_load = StandardErrorRange.json_deserialise(input_dict.get('concentric_load')) if input_dict.get('concentric_load') is not None else StandardErrorRange()
        movement.isometric_load = StandardErrorRange.json_deserialise(
            input_dict.get('isometric_load')) if input_dict.get('isometric_load') is not None else StandardErrorRange()
        movement.eccentric_load = StandardErrorRange.json_deserialise(input_dict.get('eccentric_load')) if input_dict.get('eccentric_load') is not None else StandardErrorRange()
        movement.compensated_concentric_load = StandardErrorRange.json_deserialise(input_dict.get('compensated_concentric_load')) if input_dict.get('compensated_concentric_load') is not None else StandardErrorRange()
        movement.compensated_isometric_load = StandardErrorRange.json_deserialise(
            input_dict.get('compensated_isometric_load')) if input_dict.get(
            'compensated_isometric_load') is not None else StandardErrorRange()
        movement.compensated_eccentric_load = StandardErrorRange.json_deserialise(input_dict.get('compensated_eccentric_load')) if input_dict.get('compensated_eccentric_load') is not None else StandardErrorRange()
        movement.compensating_causes_load = [BodyPartSide.json_deserialise(b) for b in input_dict.get('compensating_causes_load', [])]  # I don't know what gets saved here!
        movement.is_compensating = input_dict.get('is_compensating', False)
        #movement.compensation_source_load = CompensationSource(input_dict['compensation_source_load']) if input_dict.get('compensation_source_load') is not None else None
        movement.body_part_function = BodyPartFunction(input_dict['body_part_function']) if input_dict.get('body_part_function') is not None else None
        #movement.inhibited = input_dict.get('inhibited', 0)
        #movement.weak = input_dict.get('weak', 0)
        #movement.tight = input_dict.get('tight', 0)
        #movement.inflamed = input_dict.get('inflamed', 0)
        #movement.long = input_dict.get('long', 0)
        #movement.total_normalized_load = input_dict.get('total_normalized_load', 0)
        return movement

    def merge(self, target):

        if self.body_part_side == target.body_part_side:

            self.concentric_load.add(target.concentric_load)
            self.isometric_load.add(target.isometric_load)
            self.eccentric_load.add(target.eccentric_load)
            self.compensated_concentric_load.add(target.compensated_concentric_load)
            self.compensated_isometric_load.add(target.compensated_isometric_load)
            self.compensated_eccentric_load.add(target.compensated_eccentric_load)
            self.compensating_causes_load.extend(target.compensating_causes_load)
            self.compensating_causes_load = list(set(self.compensating_causes_load))
            self.is_compensating = max(self.is_compensating, target.is_compensating)
            #self.compensation_source_load = self.merge_with_none(self.compensation_source_load, target.compensation_source_load)
            self.body_part_function = BodyPartFunction.merge(self.body_part_function, target.body_part_function)
            #self.total_normalized_load.add(target.total_normalized_load)

    def merge_with_none(self, value_a, value_b):

        if value_a is None and value_b is None:
            return None
        if value_a is not None and value_b is None:
            return CompensationSource(value_a.value)
        if value_b is not None and value_a is None:
            return CompensationSource(value_b.value)
        if value_a is not None and value_b is not None:
            return CompensationSource(max(value_a.value, value_b.value))