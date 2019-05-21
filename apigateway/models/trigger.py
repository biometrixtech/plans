from enum import IntEnum


class TriggerType(IntEnum):
    high_volume_intensity = 0  # "High Relative Volume or Intensity of Logged Session"
    hist_sore_greater_30_sore_today_high_volume_intensity = 1  # "Pers, Pers-2 Soreness > 30d + High Relative Volume or Intensity of Logged Session"
    hist_pain_pain_today_high_volume_intensity = 2  # "Acute, Pers, Pers_2 Pain  + High Relative Volume or Intensity of Logged Session"
    hist_sore_greater_30_no_sore_today_high_volume_intensity = 3  # "Pers, Pers-2 Soreness > 30d + No soreness reported today + Logged High Relative Volume or Intensity"
    acute_pain_no_pain_today_high_volume_intensity = 4  # "Acute Pain + No pain reported today + High Relative Volume or Intensity of Logged Session" 
    pers_pers2_pain_no_pain_sore_today_high_volume_intensity = 5  # "Pers, Pers_2 Pain + No pain Reported Today + High Relative Volume or Intensity of Logged Session"
    hist_sore_less_30_sport = 6  # "Pers, Pers-2 Soreness < 30d + Correlated to Sport"
    hist_sore_less_30_no_sport = 7  # "Pers, Pers-2 Soreness < 30d + Not Correlated to Sport"  
    overreaching_high_muscular_strain = 8  # "Overreaching as increasing Muscular Strain (with context for Training Volume)"
    sore_today_no_session = 9  # "Sore reported today + not linked to session"    
    sore_today = 10  # "Sore reported today"
    sore_today_doms = 11  # "Soreness Reported Today as DOMs"
    hist_sore_less_30_sore_today = 12  # "Pers, Pers-2 Soreness < 30d + Soreness reported today"
    hist_sore_greater_30_sore_today = 13  # "Pers, Pers-2 Soreness > 30d + Soreness Reported Today"
    pain_today = 14  # "Pain reported today"
    pain_today_high = 15  # "Pain reported today high severity"
    hist_pain = 16  # "Acute, Pers, Pers-2 Pain"
    hist_pain_sport = 17  # "Acute, Pers, Pers_2 Pain + Correlated to Sport"
    pain_injury = 18  # 'Pain - Injury'
    hist_sore_greater_30 = 19  # "Pers, Pers-2 Soreness > 30d"
    hist_sore_greater_30_sport = 20  # "Pers, Pers-2 Soreness > 30d + Correlated to Sport"
    pers_pers2_pain_less_30_no_pain_today = 21
    pers_pers2_pain_greater_30_no_pain_today = 22

    def is_grouped_trigger(self):
        if self.value in [6, 7, 8, 10, 11, 14, 15]:
            return True
        else:
            return False

    @classmethod
    def parent_group_exists(cls, trigger_type, existing_triggers):
        if trigger_type.is_grouped_trigger():
            for e in existing_triggers:
                if cls.is_same_parent_group(trigger_type, e):
                    return True
        return False

    @classmethod
    def is_in(cls, trigger_type, existing_types):
        """
        check if exactly match or is in same parent group for any in the list
        """
        for e in existing_types:
            if cls.is_equivalent(trigger_type, e):
                return True
        return False

    @classmethod
    def is_equivalent(cls, trigger1, trigger2):
        if not trigger1.is_grouped_trigger():
            return trigger1 == trigger2
        else:
            return cls.is_same_parent_group(trigger1, trigger2)

    @classmethod
    def get_parent_group(cls, trigger_type):
        groups = {
            6: 0,
            7: 0,
            8: 0,
            10: 1,
            11: 1,
            14: 2,
            15: 2
        }
        if trigger_type.is_grouped_trigger():
            return groups[trigger_type.value]
        else:
            return None

    @classmethod
    def is_same_parent_group(cls, a, b):
        return cls.get_parent_group(a) == cls.get_parent_group(b)

    @classmethod
    def get_insight_type(cls, trigger_type):
        insight_type_dict = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 1,
            7: 1,
            8: 1,
            9: 1,
            10: 1,
            11: 1,
            12: 1,
            13: 1,
            14: 1,
            15: 1,
            16: 2,
            17: 2,
            18: 2,
            19: 2,
            20: 2,
            21: 1,
            22: 1,
        }
        return insight_type_dict[trigger_type.value]
