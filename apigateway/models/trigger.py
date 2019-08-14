from enum import IntEnum

from models.soreness_base import BaseSoreness, BodyPartSide, HistoricSorenessStatus
from models.sport import SportName
from serialisable import Serialisable
from utils import format_datetime, parse_datetime


class TriggerType(IntEnum):
    high_volume_intensity = 0  # "High Relative Volume or Intensity of Logged Session"
    hist_sore_greater_30_high_volume_intensity = 1  # "Pers, Pers-2 Soreness > 30d + High Relative Volume or Intensity of Logged Session"
    hist_pain_high_volume_intensity = 2  # "Acute, Pers, Pers_2 Pain  + High Relative Volume or Intensity of Logged Session"
    hist_sore_greater_30_no_sore_today_high_volume_intensity = 3  # "Pers, Pers-2 Soreness > 30d + No soreness reported today + Logged High Relative Volume or Intensity"
    acute_pain_no_pain_today_high_volume_intensity = 4  # "Acute Pain + No pain reported today + High Relative Volume or Intensity of Logged Session" 
    pers_pers2_pain_no_pain_sore_today_high_volume_intensity = 5  # "Pers, Pers_2 Pain + No pain Reported Today + High Relative Volume or Intensity of Logged Session"
    hist_sore_less_30_no_sport = 6  # "Pers, Pers-2 Soreness < 30d + Not Correlated to Sport"
    hist_sore_less_30 = 7  # "Pers, Pers-2 Soreness < 30d + Correlated to Sport"
    overreaching_high_muscular_strain = 8  # "Overreaching as increasing Muscular Strain (with context for Training Volume)"
    sore_today_no_session = 9  # "Sore reported today + not linked to session"    
    sore_today = 10  # "Sore reported today"
    sore_today_doms = 11  # "Soreness Reported Today as DOMs"
    hist_sore_less_30_sore_today = 12  # "Pers, Pers-2 Soreness < 30d + Soreness reported today"
    hist_sore_greater_30_sore_today = 13  # "Pers, Pers-2 Soreness > 30d + Soreness Reported Today"
    no_hist_pain_pain_today_severity_1_2 = 14  # "Pain reported today"
    no_hist_pain_pain_today_high_severity_3_5 = 15  # "Pain reported today high severity"
    hist_pain = 16  # "Acute, Pers, Pers-2 Pain"
    hist_pain_sport = 17  # "Acute, Pers, Pers_2 Pain + Correlated to Sport"
    pain_injury = 18  # 'Pain - Injury'
    hist_sore_greater_30 = 19  # "Pers, Pers-2 Soreness > 30d"
    hist_sore_greater_30_sport = 20  # "Pers, Pers-2 Soreness > 30d + Correlated to Sport"
    pers_pers2_pain_less_30_no_pain_today = 21
    pers_pers2_pain_greater_30_no_pain_today = 22
    hist_pain_pain_today_severity_1_2 = 23
    hist_pain_pain_today_severity_3_5 = 24
    not_enough_history_for_high_volume_intensity = 25
    response_fatigue_within_a_session_torso_loading_pattern = 101
    response_poor_response_within_a_session_torso_loading_pattern = 102
    biomechanics_fatigue_within_a_session_torso_loading_pattern = 103
    biomechanics_poor_response_within_a_session_torso_loading_pattern = 104
    movement_error_apt_asymmetry = 110
    stress_no_triggers_flagged_based_on_training_volume = 201
    response_no_triggers_flagged_based_on_soreness = 202
    response_no_triggers_flagged_based_on_pain = 203
    response_no_triggers_flagged_based_on_3_sensor = 204
    biomechanics_no_triggers_flagged_based_on_soreness = 205
    biomechanics_no_triggers_flagged_based_on_pain = 206
    biomechanics_no_triggers_flagged_based_on_3_sensor = 207

    def is_grouped_trigger(self):
        if self.value in [0, 1, 2, 7, 8, 14, 15, 16, 19, 23, 24]:
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
            7: 0,
            8: 0,
            14: 2,
            15: 2,
            23: 2,
            24: 2,
            0: 3,
            1: 3,
            2: 3,
            19: 4,
            16: 4,
            101: 5,
            102: 5,
            103: 6,
            104: 6
        }
        if trigger_type.is_grouped_trigger():
            return groups[trigger_type.value]
        else:
            return None

    @classmethod
    def is_same_parent_group(cls, a, b):
        return cls.get_parent_group(a) == cls.get_parent_group(b)


class Trigger(BaseSoreness, Serialisable):
    def __init__(self, trigger_type):
        super().__init__()
        self.trigger_type = trigger_type
        self.body_part = None
        self.agonists = []
        self.antagonists = []
        self.synergists = []
        self.sport_name = None
        self.severity = None
        self.pain = None
        self.historic_soreness_status = None
        self.created_date_time = None
        self.modified_date_time = None
        self.deleted_date_time = None
        self.source_date_time = None
        self.priority = 0  # This doesn't need to be persisted, just used in logic
        self.body_part_priority = 0  # This doesn't need to be persisted, just used in logic

    def json_serialise(self):
        return {
            "trigger_type": self.trigger_type.value,
            "body_part": self.body_part.json_serialise() if self.body_part is not None else None,
            "agonists": [a.json_serialise() for a in self.agonists if self.agonists is not None],
            "antagonists": [a.json_serialise() for a in self.antagonists if self.antagonists is not None],
            "synergists": [s.json_serialise() for s in self.synergists if self.synergists is not None],
            "sport_name": self.sport_name.value if self.sport_name is not None else None,
            "severity": self.severity,
            "pain": self.pain,
            "historic_soreness_status": self.historic_soreness_status.value if self.historic_soreness_status is not None else None,
            "created_date_time" : format_datetime(
                self.created_date_time) if self.created_date_time is not None else None,
            "modified_date_time": format_datetime(
                self.modified_date_time) if self.modified_date_time is not None else None,
            "deleted_date_time": format_datetime(
                self.deleted_date_time) if self.deleted_date_time is not None else None,
            "source_date_time": format_datetime(
                self.source_date_time) if self.source_date_time is not None else None
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        trigger = cls(TriggerType(input_dict['trigger_type']))
        trigger.body_part = BodyPartSide.json_deserialise(input_dict['body_part']) if input_dict['body_part'] is not None else None
        trigger.agonists = [BodyPartSide.json_deserialise(a) for a in input_dict.get('agonists', [])]
        trigger.antagonists = [BodyPartSide.json_deserialise(a) for a in input_dict.get('antagonists',[])]
        trigger.synergists = [BodyPartSide.json_deserialise(s) for s in input_dict.get('synergists',[])]
        trigger.sport_name = input_dict['sport_name']
        trigger.severity = input_dict['severity']
        trigger.pain = input_dict['pain']
        trigger.historic_soreness_status = HistoricSorenessStatus(input_dict['historic_soreness_status']) if input_dict.get('historic_soreness_status') is not None else None
        trigger.created_date_time = parse_datetime(input_dict["created_date_time"]) if input_dict.get("created_date_time") is not None else None
        trigger.modified_date_time = parse_datetime(input_dict["modified_date_time"]) if input_dict.get("modified_date_time") is not None else None
        trigger.deleted_date_time = parse_datetime(input_dict["deleted_date_time"]) if input_dict.get("deleted_date_time") is not None else None
        trigger.source_date_time = parse_datetime(input_dict["source_date_time"]) if input_dict.get("source_date_time") is not None else None
        return trigger

    def __setattr__(self, name, value):
        if name == "sport_name" and not isinstance(value, SportName) and value is not None:
            value = SportName(value)
        super().__setattr__(name, value)