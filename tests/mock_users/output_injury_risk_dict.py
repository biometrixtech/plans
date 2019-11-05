from datastores.injury_risk_datastore import InjuryRiskDatastore
from models.soreness_base import BodyPartSide, BodyPartLocation
import os


class InjuryRiskDictOutputProcessor(object):
    def __init__(self, file_location, user_id, user_name='test'):
        self.file_location = file_location
        self.file = None
        #self.body_part_enum = body_part_enum
        self.injury_risk_datastore = InjuryRiskDatastore()
        #self.side = side
        self.user_id = user_id
        self.user_name = user_name
        self.injury_risk_dict = {}
        self.attribute_list = ['concentric_volume_last_week', 'concentric_volume_this_week', 'prime_mover_concentric_volume_last_week',
                'prime_mover_concentric_volume_this_week', 'synergist_concentric_volume_last_week',
                'synergist_concentric_volume_this_week', 'synergist_compensating_concentric_volume_last_week',
                'synergist_compensating_concentric_volume_this_week', 'eccentric_volume_last_week',
                'eccentric_volume_this_week', 'prime_mover_eccentric_volume_last_week', 'prime_mover_eccentric_volume_this_week',
                'synergist_eccentric_volume_last_week', 'synergist_eccentric_volume_this_week',
                'synergist_compensating_eccentric_volume_last_week','synergist_compensating_eccentric_volume_this_week',
                'prime_mover_concentric_volume_today','prime_mover_eccentric_volume_today', 'synergist_concentric_volume_today',
                'synergist_eccentric_volume_today', 'synergist_compensating_concentric_volume_today',
                'synergist_compensating_eccentric_volume_today','total_volume_ramp_today', 'eccentric_volume_ramp_today',
                'total_compensation_percent','eccentric_compensation_percent','total_compensation_percent_tier',
                'eccentric_compensation_percent_tier','total_volume_percent_tier','eccentric_volume_percent_tier',
                'compensating_causes_volume_today', 'last_compensation_date', 'compensation_count_last_0_20_days',
                'last_movement_dysfunction_stress_date','last_dysfunction_cause_date',
                'ache_count_last_0_10_days','ache_count_last_0_20_days','last_ache_level',
                'last_ache_date','last_excessive_strain_date','last_non_functional_overreaching_date',
                'last_functional_overreaching_date','last_inflammation_date','knots_count_last_0_20_days','last_knots_level',
                'last_knots_date','last_muscle_spasm_date','last_adhesions_date','last_inhibited_date','last_long_date',
                'long_count_last_0_20_days','last_overactive_short_date','last_overactive_long_date','last_underactive_short_date',
                'last_underactive_long_date','overactive_short_count_last_0_20_days','overactive_long_count_last_0_20_days',
                'underactive_short_count_last_0_20_days','underactive_long_count_last_0_20_days','sharp_count_last_0_10_days',
                'sharp_count_last_0_20_days','last_sharp_level','last_sharp_date','last_short_date','short_count_last_0_20_days',
                'tight_count_last_0_20_days','last_tight_level','last_tight_date','last_weak_date','weak_count_last_0_20_days',
                'last_muscle_imbalance_date','last_tendinopathy_date','last_tendinosis_date','last_altered_joint_arthokinematics_date',
                'overactive_short_vote_count','overactive_long_vote_count','underactive_short_vote_count',
                'underactive_long_vote_count', 'weak_vote_count', 'last_vote_updated_date_time']

    def write_headers(self):
        #if not os.path.exists(self.file_location+'/user_'+self.user_id):
        #    os.mkdir(self.file_location+'/user_'+self.user_id)
        self.file_location = self.file_location + '/user_'+self.user_name

        #self.file = open(self.file_location + "/" + str(self.body_part_enum) + "_" + str(self.side) + '_injury_risk_dict.csv', 'w')
        self.file = open(
            self.file_location + "_" + 'injury_risk_dict.csv', 'w')
        columns = ",".join(self.attribute_list)
        line = ('date,body_part,side,'+ columns)
        self.file.write(line + '\n')

    def write_day(self, date):

        injury_risk_dict = self.injury_risk_datastore.get(self.user_id)

        #body_part_side = BodyPartSide(BodyPartLocation(self.body_part_enum), self.side)

        for body_part_side, body_part_injury_risk in injury_risk_dict.items():
            #body_part_injury_risk = injury_risk_dict[body_part_side]
            line = str(date) + ',' + body_part_side.body_part_location.name + ',' + str(body_part_side.side) + ',' + self.get_attribute_string(body_part_injury_risk)
            self.file.write(line + '\n')

    def close(self):

        self.file.close()

    def get_attribute_string(self, body_part_injury_risk):

        attribute_value_list = []

        for attribute in self.attribute_list:
            val = getattr(body_part_injury_risk, attribute)
            if isinstance(val, list):
                new_list = []
                for v in val:
                    if isinstance(v, BodyPartSide):
                        new_val = str(v.body_part_location.value) + '_' + str(v.side)
                        new_list.append(new_val)
                val = ";".join(new_list)
            elif not isinstance(val, str):
                val = str(val)
            attribute_value_list.append(val)

        return ",".join(attribute_value_list)

