from enum import IntEnum, Enum
from models.sport import SportName
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.body_parts import BodyPart, BodyPartFactory
from datetime import timedelta


class FunctionalMovementType(Enum):
    ankle_dorsiflexion = 0
    ankle_plantar_flexion = 1
    inversion_of_the_foot = 2
    eversion_of_the_foot = 3
    knee_flexion = 4
    knee_extension = 5
    tibial_external_rotation = 6
    tibial_internal_rotation = 7
    hip_adduction = 8
    hip_abduction = 9
    hip_internal_rotation = 10
    hip_external_rotation = 11
    hip_extension = 12
    hip_flexion = 13


class FunctionalMovement(object):
    def __init__(self, functional_movement_type):
        self.functional_movement_type = functional_movement_type
        self.prime_movers = []
        self.antagonists = []
        self.synergists = []


class BodyPartInjuryRisk(object):
    def __init__(self):
        self.concentric_volume_last_week = 0
        self.concentric_volume_this_week = 0
        self.concentric_volume_today = 0
        self.eccentric_volume_last_week = 0
        self.eccentric_volume_this_week = 0
        self.eccentric_volume_today = 0
        self.max_concentric_intensity_48_hours = 0
        self.max_eccentric_intensity_48_hours = 0

        # ache
        self.ache_count_last_0_10_days = 0
        self.ache_count_last_3_10_days = 0
        self.ache_count_last_3_20_days = 0
        self.last_ache_date = None

        # excessive strain
        self.last_excessive_strain_date = None
        self.last_non_functional_overreaching_date = None
        self.last_functional_overreaching_date = None

        # inflammation
        self.last_inflammation_date = None

        # muscle spasm
        self.last_muscle_spasm_date = None

        # adhesions
        self.last_adhesions_date = None

        # inhibited
        self.last_inhibited_date = None

        # long
        self.last_long_date = None

        # overactive / underactive
        self.last_overactive_date = None
        self.last_underactive_date = None

        # sharp
        self.sharp_count_last_0_10_days = 0
        self.sharp_count_last_3_20_days = 0
        self.last_sharp_date = None

        # short
        self.last_short_date = None

        # tight
        self.tight_count_last_3_20_days = 0
        self.last_tight_date = None

        # weak
        self.last_weak_date = None

    def eccentric_volume_ramp(self):

        this_weeks_volume = 0
        if self.eccentric_volume_this_week is not None:
            this_weeks_volume += self.eccentric_volume_this_week
        if self.eccentric_volume_today is not None:
            this_weeks_volume += self.eccentric_volume_today

        if self.eccentric_volume_last_week is not None and self.eccentric_volume_last_week > 0:
            if this_weeks_volume is not None:
                return this_weeks_volume / self.eccentric_volume_last_week

        return 0

    def total_volume_last_week(self):

        eccentric_volume_last_week = 0
        concentric_volume_last_week = 0

        if self.eccentric_volume_last_week is not None:
            eccentric_volume_last_week = self.eccentric_volume_last_week

        if self.concentric_volume_last_week is not None:
            concentric_volume_last_week = self.concentric_volume_last_week

        return eccentric_volume_last_week + concentric_volume_last_week

    def total_volume_this_week(self):

        eccentric_volume_this_week = 0
        concentric_volume_this_week = 0

        if self.eccentric_volume_this_week is not None:
            eccentric_volume_this_week += self.eccentric_volume_this_week

        if self.concentric_volume_this_week is not None:
            concentric_volume_this_week += self.concentric_volume_this_week

        if self.eccentric_volume_today is not None:
            eccentric_volume_this_week += self.eccentric_volume_today

        if self.concentric_volume_today is not None:
            concentric_volume_this_week += self.concentric_volume_today

        return concentric_volume_this_week + eccentric_volume_this_week

    def total_volume_ramp(self):

        total_volume_last_week = self.total_volume_last_week()

        if total_volume_last_week > 0:
            return self.total_volume_this_week() / total_volume_last_week

        return 0

class BodyPartFunctionalMovement(object):
    def __init__(self, body_part_side):
        self.body_part_side = body_part_side
        self.concentric_volume = 0
        self.eccentric_volume = 0
        self.concentric_intensity = 0
        self.eccentric_intensity = 0
        self.concentric_ramp = 0.0
        self.eccentric_ramp = 0.0
        self.inhibited = 0
        self.weak = 0
        self.tight = 0
        self.inflamed = 0
        self.long = 0

    def total_volume(self):

        return self.concentric_volume + self.eccentric_volume

    def __hash__(self):
        return hash((self.body_part_side.body_part_location.value, self.body_part_side.side))

    def __eq__(self, other):
        return self.body_part_side.body_part_location == other.body_part_side.body_part_location and self.body_part_side.side == other.body_part_side.side

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)


class SessionFunctionalMovement(object):
    def __init__(self, session, injury_risk_dict):
        self.body_parts = []
        self.session = session
        self.functional_movement_mappings = []
        self.injury_risk_dict = injury_risk_dict

    def process(self, event_date_time):
        activity_factory = ActivityFunctionalMovementFactory()
        movement_factory = FunctionalMovementFactory()

        self.functional_movement_mappings = activity_factory.get_functional_movement_mappings(self.session.sport_name)
        concentric_levels = [m.concentric_level for m in self.functional_movement_mappings]
        highest_concentric_level = max(concentric_levels)
        eccentric_levels = [m.eccentric_level for m in self.functional_movement_mappings]
        highest_eccentric_level = max(eccentric_levels)
        highest_concentric_eccentric_level = max(highest_concentric_level, highest_eccentric_level)

        for m in self.functional_movement_mappings:
            functional_movement = movement_factory.get_functional_movement(m.functional_movement_type)
            for p in functional_movement.prime_movers:
                body_part_side_list = self.get_body_part_side_list(p)
                for b in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(b)
                    m.prime_movers.append(functional_movement_body_part_side)

            for a in functional_movement.antagonists:
                body_part_side_list = self.get_body_part_side_list(a)
                for b in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(b)
                    m.antagonists.append(functional_movement_body_part_side)

            # TODO - change with total volume
            m.attribute_training_volume(self.session.duration_minutes * self.session.session_RPE, highest_concentric_eccentric_level, self.injury_risk_dict, event_date_time)
            m.attribute_intensity(self.session.session_RPE, highest_concentric_eccentric_level, self.injury_risk_dict, event_date_time)

        self.aggregate_body_parts()

    def aggregate_body_parts(self):

        body_part_sides = {}

        for m in self.functional_movement_mappings:
            for p in m.prime_movers:
                if p not in body_part_sides:
                    body_part_sides[p] = p
                else:
                    body_part_sides[p].concentric_volume += p.concentric_volume
                    body_part_sides[p].eccentric_volume += p.eccentric_volume
                    body_part_sides[p].concentric_intensity = max(p.concentric_intensity, body_part_sides[p].concentric_intensity)
                    body_part_sides[p].eccentric_intensity = max(p.eccentric_intensity, body_part_sides[p].eccentric_intensity)

        self.body_parts = list(body_part_sides.values())

    def get_body_part_side_list(self, body_part_enum):

        body_part_side_list = []

        body_part_factory = BodyPartFactory()
        body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(body_part_enum), None))
        if not body_part.bilateral:
            sides = [0]
        else:
            sides = [1, 2]
        for side in sides:
            body_part_side = BodyPartSide(BodyPartLocation(body_part_enum), side=side)
            body_part_side_list.append(body_part_side)

        return body_part_side_list


class FunctionalMovementActivityMapping(object):
    def __init__(self, functional_movement_type, is_concentric, concentric_level, is_eccentric, eccentric_level):
        self.functional_movement_type = functional_movement_type
        self.is_concentric = is_concentric
        self.concentric_level = concentric_level
        self.is_eccentric = is_eccentric
        self.eccentric_level = eccentric_level
        self.prime_movers = []
        self.antagonists = []
        self.synergists = []

    def attribute_training_volume(self, training_volume, highest_concentric_eccentric_factor, injury_risk_dict, event_date_time):

        prime_mover_ratio = 0.8

        for p in self.prime_movers:
            compensating_for_others = self.other_body_parts_affected(p, injury_risk_dict, event_date_time)
            if compensating_for_others:
                prime_mover_ratio = 1.0
            # TODO replace with new ratios
            attributed_concentric_volume = training_volume * (self.concentric_level / highest_concentric_eccentric_factor) * prime_mover_ratio
            attributed_eccentric_volume = training_volume * (self.eccentric_level / highest_concentric_eccentric_factor) * prime_mover_ratio
            p.concentric_volume = attributed_concentric_volume
            p.eccentric_volume = attributed_eccentric_volume

    def attribute_intensity(self, intensity, highest_concentric_eccentric_factor, injury_risk_dict, event_date_time):

        prime_mover_ratio = 0.8

        # TODO make sure we implement logic to test for high intensity on processing, esp for eccentric intensity

        for p in self.prime_movers:
            compensating_for_others = self.other_body_parts_affected(p, injury_risk_dict, event_date_time)
            if compensating_for_others:
                prime_mover_ratio = 1.0
            attributed_concentric_intensity = intensity * (self.concentric_level / highest_concentric_eccentric_factor) * prime_mover_ratio
            attributed_eccentric_intensity = intensity * (self.eccentric_level / highest_concentric_eccentric_factor) * prime_mover_ratio
            p.concentric_intensity = attributed_concentric_intensity
            p.eccentric_intensity = attributed_eccentric_intensity

    def other_body_parts_affected(self, target_body_part, injury_risk_dict, event_date_time):

        # we want to look at both the prime movers and synergists
        body_part_list = []
        body_part_list.extend(self.prime_movers)
        body_part_list.extend(self.synergists)

        filtered_list = [b for b in body_part_list if b.body_part_side != target_body_part.body_part_side]

        two_days_ago = event_date_time.date() - timedelta(days=1)

        for f in filtered_list:
            #if f.body_part_side.body_part_location != target_body_part.body_part_side.body_part_location and f.body_part_side.side != target_body_part.body_part_side.side:
            if f.body_part_side in injury_risk_dict:
                if (injury_risk_dict[f.body_part_side].last_weak_date is not None and
                        injury_risk_dict[f.body_part_side].last_weak_date == event_date_time.date()):
                    return True
                if (injury_risk_dict[f.body_part_side].last_tight_date is not None and
                        injury_risk_dict[f.body_part_side].last_tight_date == event_date_time.date()):
                    return True
                if (injury_risk_dict[f.body_part_side].last_long_date is not None and
                        injury_risk_dict[f.body_part_side].last_long_date == event_date_time.date()):
                    return True
                if (injury_risk_dict[f.body_part_side].last_inhibited_date is not None and
                        injury_risk_dict[f.body_part_side].last_inhibited_date >= two_days_ago):
                    return True
                if (injury_risk_dict[f.body_part_side].last_inflammation_date is not None and
                        injury_risk_dict[f.body_part_side].last_inflammation_date >= two_days_ago):
                    return True
        return False


class ActivityFunctionalMovementFactory(object):

    def get_functional_movement_mappings(self, sport_name):

        mapping = []

        if sport_name == SportName.distance_running:
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.ankle_dorsiflexion, True, 1, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.ankle_plantar_flexion, True, 1, True, 1))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.inversion_of_the_foot, True, 1, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.eversion_of_the_foot, False, 0, True, 1))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.knee_flexion, True, 0.5, True, 1))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.knee_extension, True, 1, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.hip_adduction, True, 2, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.hip_abduction, False, 0, True, 1))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.hip_extension, True, 5, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.hip_flexion, True, 2, True, 2))

            return mapping


class FunctionalMovementFactory(object):

    def get_functional_movement(self, movement_type):

        if movement_type == FunctionalMovementType.ankle_dorsiflexion:
            return self.get_ankle_dorsiflexion()
        elif movement_type == FunctionalMovementType.ankle_plantar_flexion:
            return self.get_ankle_plantar_flexion()
        elif movement_type == FunctionalMovementType.inversion_of_the_foot:
            return self.get_inversion_of_the_foot()
        elif movement_type == FunctionalMovementType.eversion_of_the_foot:
            return self.get_eversion_of_the_foot()
        elif movement_type == FunctionalMovementType.knee_flexion:
            return self.get_knee_flexion()
        elif movement_type == FunctionalMovementType.knee_extension:
            return self.get_knee_extension()
        elif movement_type == FunctionalMovementType.tibial_external_rotation:
            return self.get_tibial_external_rotation()
        elif movement_type == FunctionalMovementType.tibial_internal_rotation:
            return self.get_tibial_internal_rotation()
        elif movement_type == FunctionalMovementType.hip_adduction:
            return self.get_hip_adduction()
        elif movement_type == FunctionalMovementType.hip_abduction:
            return self.get_hip_abduction()
        elif movement_type == FunctionalMovementType.hip_internal_rotation:
            return self.get_hip_internal_rotation()
        elif movement_type == FunctionalMovementType.hip_external_rotation:
            return self.get_hip_external_rotation()
        elif movement_type == FunctionalMovementType.hip_extension:
            return self.get_hip_extension()
        elif movement_type == FunctionalMovementType.hip_flexion:
            return self.get_hip_flexion()


    def get_ankle_dorsiflexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_dorsiflexion)
        functional_movement.prime_movers = [40]
        functional_movement.antagonists = [41, 42, 43, 44]
        return functional_movement

    def get_ankle_plantar_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_plantar_flexion)
        functional_movement.prime_movers = [41, 42, 43, 44]
        functional_movement.antagonists = [40]
        return functional_movement

    def get_inversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.inversion_of_the_foot)
        functional_movement.prime_movers = [40, 42]
        functional_movement.antagonists = [41]
        return functional_movement

    def get_eversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.eversion_of_the_foot)
        functional_movement.prime_movers = [41]
        functional_movement.antagonists = [40, 42]
        return functional_movement

    def get_knee_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_flexion)
        functional_movement.prime_movers = [45, 46, 47, 48]
        functional_movement.antagonists = [55, 56, 57, 58]
        return functional_movement

    def get_knee_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_extension)
        functional_movement.prime_movers = [55, 56, 57, 58]
        functional_movement.antagonists = [45, 46, 47, 48]
        return functional_movement

    def get_tibial_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.tibial_external_rotation)
        functional_movement.prime_movers = [45, 46]
        functional_movement.antagonists = [47, 48]
        return functional_movement

    def get_tibial_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.tibial_internal_rotation)
        functional_movement.prime_movers = [47, 48]
        functional_movement.antagonists = [45, 46, 53]
        return functional_movement

    def get_hip_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_extension)
        functional_movement.prime_movers = [45, 47, 48, 51, 60, 66]
        functional_movement.antagonists = [49, 50, 52, 53, 54, 58, 59, 61, 62, 65]
        return functional_movement

    def get_hip_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_flexion)
        functional_movement.prime_movers = [49, 50, 52, 53, 54, 58, 59, 61, 62, 65]
        functional_movement.antagonists = [47, 48, 51, 60, 66]
        return functional_movement

    def get_hip_adduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_adduction)
        functional_movement.prime_movers = [49, 50, 51, 52, 53, 54]
        functional_movement.antagonists = [59, 60, 63, 64, 65]
        return functional_movement

    def get_hip_abduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_abduction)
        functional_movement.prime_movers = [59, 60, 62, 63, 64, 65]
        functional_movement.antagonists = [49, 50, 51, 52, 53, 54]
        return functional_movement

    def get_hip_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_internal_rotation)
        functional_movement.prime_movers = [49, 50, 52, 53, 54, 59, 63, 65]
        functional_movement.antagonists = [51, 60, 61, 64, 66]
        return functional_movement

    def get_hip_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_external_rotation)
        functional_movement.prime_movers = [51, 60, 61, 64, 66]
        functional_movement.antagonists = [49, 50, 52, 53, 54, 59, 62, 63, 65]
        return functional_movement