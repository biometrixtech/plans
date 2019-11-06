from models.sport import SportName
#from models.functional_anatomy import FunctionalAnatomy
from models.soreness_base import BodyPartLocation


class FunctionalAnatomyProcessor(object):
    def __init__(self):
        self.activity = SportName.distance_running

    # def get_functional_anatomy_for_sport(self, sport_name):
    #
    #     functional_anatomy = FunctionalAnatomy(self.activity)
    #
    #     if sport_name is not None:
    #         if sport_name == SportName.distance_running:
    #             functional_anatomy = FunctionalAnatomy(SportName.distance_running)
    #
    #     return functional_anatomy

    def get_related_muscles_for_joint(self, joint_value):

        if joint_value == BodyPartLocation.foot.value:
            return [40, 41, 42, 43, 44]
        elif joint_value == BodyPartLocation.ankle.value:
            return [41, 43, 44]
        elif joint_value == BodyPartLocation.knee.value:
            return [46, 47, 48, 55, 56, 57, 58, 62]
        elif joint_value == BodyPartLocation.hip.value:
            return [45, 47, 48, 49, 50, 51, 52, 53, 54, 58, 59, 60, 61, 62, 63, 64, 65, 66]
        elif joint_value == BodyPartLocation.shoulder:
            return [83, 81, 22, 23]
        elif joint_value == BodyPartLocation.wrist:
            return [24]
        elif joint_value == BodyPartLocation.elbow:
            return [22, 23, 24]
        # elif joint_value == BodyPartLocation.lower_back.value:
        #     return [45, 47, 48, 49, 50, 51, 52, 53, 54, 58, 59, 60, 61, 62, 63, 64, 65, 66]
        else:
            return []

    def get_related_muscles_for_ligament(self, ligament_value):

        if ligament_value == BodyPartLocation.it_band.value:
            return [59]
        elif ligament_value == BodyPartLocation.it_band_lateral_knee.value:
            return [59]
        elif ligament_value == BodyPartLocation.achilles.value:
            return [43, 44]

    #  This is not used and also became outdated
    # def get_related_joints(self, body_part_value):
    #
    #     if body_part_value == BodyPartLocation.shin.value:
    #         return [9, 10]
    #     elif body_part_value == BodyPartLocation.anterior_tibialis.value:
    #         return [10]
    #     elif body_part_value == BodyPartLocation.peroneals_longus.value:
    #         return [9, 10]
    #     elif body_part_value == BodyPartLocation.posterior_tibialis.value:
    #         return [10]
    #     elif body_part_value in [BodyPartLocation.calves.value, BodyPartLocation.soleus.value, BodyPartLocation.gastrocnemius_medial.value]:
    #         return [9, 10]
    #     elif body_part_value == BodyPartLocation.hamstrings.value:
    #         return [4, 7]
    #     elif body_part_value == BodyPartLocation.bicep_femoris_long_head.value:
    #         return [4]
    #     elif body_part_value == BodyPartLocation.bicep_femoris_short_head.value:
    #         return [7]
    #     elif body_part_value in [BodyPartLocation.semimembranosus.value, BodyPartLocation.semitendinosus.value]:
    #         return [4, 7]
    #     elif body_part_value in [BodyPartLocation.groin.value,
    #                              BodyPartLocation.adductor_longus.value,
    #                              BodyPartLocation.adductor_magnus_anterior_fibers.value,
    #                              BodyPartLocation.adductor_magnus_posterior_fibers.value,
    #                              BodyPartLocation.adductor_brevis.value,
    #                              BodyPartLocation.gracilis.value,
    #                              BodyPartLocation.pectineus.value]:
    #         return [4]
    #     elif body_part_value in [BodyPartLocation.quads.value, BodyPartLocation.rectus_femoris.value]:
    #         return [4, 7]
    #     elif body_part_value in [BodyPartLocation.vastus_lateralis.value,
    #                              BodyPartLocation.vastus_medialis.value,
    #                              BodyPartLocation.vastus_intermedius.value]:
    #         return [7]
    #     elif body_part_value in [BodyPartLocation.hip_flexor.value,
    #                              BodyPartLocation.tensor_fascia_latae.value,
    #                              BodyPartLocation.piriformis.value]:
    #         return [4]
    #     elif body_part_value in [BodyPartLocation.core_stabilizers.value, BodyPartLocation.sartorius.value]:
    #         return [4, 7]
    #     elif body_part_value == BodyPartLocation.iliopsoas.value:
    #         return [4]
    #     elif body_part_value in [BodyPartLocation.glutes.value,
    #                              BodyPartLocation.gluteus_medius_anterior_fibers.value,
    #                              BodyPartLocation.gluteus_medius_posterior_fibers.value,
    #                              BodyPartLocation.gluteus_minimus.value,
    #                              BodyPartLocation.gluteus_maximus.value]:
    #         return [4]
    #     else:
    #         return []