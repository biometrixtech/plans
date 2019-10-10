from models.sport import SportName
from models.functional_anatomy import FunctionalAnatomy
from models.soreness_base import BodyPartLocation

class FunctionalAnatomyProcessor(object):
    def __init__(self):
        self.activity = SportName.distance_running

    def get_functional_anatomy_for_sport(self, sport_name):

        functional_anatomy = FunctionalAnatomy(self.activity)

        if sport_name is not None:
            if sport_name == SportName.distance_running:
                functional_anatomy = FunctionalAnatomy(SportName.distance_running)

        return functional_anatomy

    def get_related_joints(self, body_part_value):

        if body_part_value == BodyPartLocation.shin.value:
            return [9, 10]
        elif body_part_value == BodyPartLocation.anterior_tibialis.value:
            return [10]
        elif body_part_value == BodyPartLocation.peroneals_longus.value:
            return [9, 10]
        elif body_part_value == BodyPartLocation.posterior_tibialis.value:
            return [10]
        elif body_part_value in [BodyPartLocation.calves.value, BodyPartLocation.soleus.value, BodyPartLocation.gastrocnemius.value]:
            return [9, 10]
        elif body_part_value == BodyPartLocation.hamstrings.value:
            return [4, 7, 12]
        elif body_part_value == BodyPartLocation.bicep_femoris_long_head.value:
            return [4, 12]
        elif body_part_value == BodyPartLocation.bicep_femoris_short_head.value:
            return [7]
        elif body_part_value in [BodyPartLocation.semimembranosus.value, BodyPartLocation.semitendinosus.value]:
            return [4, 7, 12]
        elif body_part_value in [BodyPartLocation.groin.value,
                                 BodyPartLocation.adductor_longus.value,
                                 BodyPartLocation.adductor_magnus_anterior_fibers.value,
                                 BodyPartLocation.adductor_magnus_posterior_fibers.value,
                                 BodyPartLocation.adductor_brevis.value,
                                 BodyPartLocation.gracilis.value,
                                 BodyPartLocation.pectineus.value]:
            return [4, 12]
        elif body_part_value in [BodyPartLocation.quads.value, BodyPartLocation.rectus_femoris.value]:
            return [4, 7, 12]
        elif body_part_value in [BodyPartLocation.vastus_lateralis.value,
                                 BodyPartLocation.vastus_medialis.value,
                                 BodyPartLocation.vastus_intermedius.value]:
            return [7]
        elif body_part_value in [BodyPartLocation.hip_flexor.value,
                                 BodyPartLocation.tensor_fascia_latae.value,
                                 BodyPartLocation.piriformis.value]:
            return [4, 12]
        elif body_part_value in [BodyPartLocation.core_stabilizers.value, BodyPartLocation.sartorius.value]:
            return [4, 7, 12]
        elif body_part_value == BodyPartLocation.iliopsoas.value:
            return [4, 12]
        elif body_part_value in [BodyPartLocation.glutes.value,
                                 BodyPartLocation.gluteus_medius_anterior_fibers.value,
                                 BodyPartLocation.gluteus_medius_posterior_fibers.value,
                                 BodyPartLocation.gluteus_minimus.value,
                                 BodyPartLocation.gluteus_maximus.value]:
            return [4, 12]
        else:
            return []