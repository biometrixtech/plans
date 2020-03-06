from serialisable import Serialisable
from models.sport import SportName


class LoadStats(Serialisable):
    def __init__(self):
        self.min_duration_health = None
        self.max_duration_health = None
        self.min_duration_minutes = None
        self.max_duration_minutes = None
        self.min_swimming_distance = None
        self.max_swimming_distance = None
        self.min_cycling_distance = None
        self.max_cycling_distance = None
        self.min_walk_run_distance = None
        self.max_walk_run_distance = None
        self.min_trimp = None
        self.max_trimp = None
        self.min_shrz = None
        self.max_shrz = None

        # mixed session
        self.max_not_tracked = None
        self.max_strength_endurance_cardiorespiratory = None
        self.max_strength_endurance_strength = None
        self.max_power_drill = None
        self.max_maximal_strength_hypertrophic = None
        self.max_power_explosive_action = None

    def json_serialise(self):
        ret = {
            'min_duration_health': self.min_duration_health,
            'max_duration_health': self.max_duration_health,
            'min_duration_minutes': self.min_duration_minutes,
            'max_duration_minutes': self.max_duration_minutes,
            'min_swimming_distance': self.min_swimming_distance,
            'max_swimming_distance': self.max_swimming_distance,
            'min_cycling_distance': self.min_cycling_distance,
            'max_cycling_distance': self.max_cycling_distance,
            'min_walk_run_distance': self.min_walk_run_distance,
            'max_walk_run_distance': self.max_walk_run_distance,
            'min_trimp': self.min_trimp,
            'max_trimp': self.max_trimp,
            'min_shrz': self.min_shrz,
            'max_shrz': self.max_shrz,
            'max_not_tracked': self.max_not_tracked,
            'max_strength_endurance_cardiorespiratory': self.max_strength_endurance_cardiorespiratory,
            'max_strength_endurance_strength': self.max_strength_endurance_strength,
            'max_power_drill': self.max_power_drill,
            'max_maximal_strength_hypertrophic': self.max_maximal_strength_hypertrophic,
            'max_power_explosive_action': self.max_power_explosive_action
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        load_stats = cls()
        if input_dict is not None:
            load_stats.min_duration_health = input_dict["min_duration_health"]
            load_stats.max_duration_health = input_dict["max_duration_health"]
            load_stats.min_duration_minutes = input_dict["min_duration_minutes"]
            load_stats.max_duration_minutes = input_dict["max_duration_minutes"]
            load_stats.min_swimming_distance = input_dict["min_swimming_distance"]
            load_stats.max_swimming_distance = input_dict["max_swimming_distance"]
            load_stats.min_cycling_distance = input_dict["min_cycling_distance"]
            load_stats.max_cycling_distance = input_dict["max_cycling_distance"]
            load_stats.min_walk_run_distance = input_dict["min_walk_run_distance"]
            load_stats.max_walk_run_distance = input_dict["max_walk_run_distance"]
            load_stats.min_trimp = input_dict["min_trimp"]
            load_stats.max_trimp = input_dict["max_trimp"]
            load_stats.min_shrz = input_dict["min_shrz"]
            load_stats.max_shrz = input_dict["max_shrz"]
            load_stats.max_not_tracked = input_dict['max_not_tracked']
            load_stats.max_strength_endurance_cardiorespiratory = input_dict['max_strength_endurance_cardiorespiratory']
            load_stats.max_strength_endurance_strength = input_dict['max_strength_endurance_strength']
            load_stats.max_power_drill = input_dict['max_power_drill']
            load_stats.max_maximal_strength_hypertrophic = input_dict['max_maximal_strength_hypertrophic']
            load_stats.max_power_explosive_action = input_dict['max_power_explosive_action']

        return load_stats

    def set_min_max_values(self, training_sessions):

        if training_sessions is not None:
            for t in training_sessions:
                if t.duration_minutes is not None and t.duration_minutes > 0:
                    self.min_duration_minutes = min(self.min_duration_minutes if self.min_duration_minutes is not None else 0, t.duration_minutes)
                    self.max_duration_minutes = max(self.max_duration_minutes if self.max_duration_minutes is not None else 0, t.duration_minutes)
                if t.duration_health is not None and t.duration_health > 0:
                    self.min_duration_health = min(self.min_duration_health if self.min_duration_health is not None else 0, t.duration_health)
                    self.max_duration_health = max(self.max_duration_health if self.max_duration_health is not None else 0, t.duration_health)
                if t.get_distance_training_volume(SportName.walking) is not None and t.get_distance_training_volume(SportName.walking) > 0:
                    self.min_walk_run_distance = min(self.min_walk_run_distance if self.min_walk_run_distance is not None else 0, t.get_distance_training_volume(SportName.walking))
                    self.max_walk_run_distance = max(self.max_walk_run_distance if self.max_walk_run_distance is not None else 0, t.get_distance_training_volume(SportName.walking))
                if t.get_distance_training_volume(SportName.distance_running) is not None and t.get_distance_training_volume(SportName.distance_running) > 0:
                    self.min_walk_run_distance = min(self.min_walk_run_distance if self.min_walk_run_distance is not None else 0, t.get_distance_training_volume(SportName.distance_running))
                    self.max_walk_run_distance = max(self.max_walk_run_distance if self.max_walk_run_distance is not None else 0, t.get_distance_training_volume(SportName.distance_running))
                if t.get_distance_training_volume(SportName.swimming) is not None and t.get_distance_training_volume(SportName.swimming) > 0:
                    self.min_swimming_distance = min(self.min_swimming_distance if self.min_swimming_distance is not None else 0, t.get_distance_training_volume(SportName.swimming))
                    self.max_swimming_distance = max(self.max_swimming_distance if self.max_swimming_distance is not None else 0, t.get_distance_training_volume(SportName.swimming))
                if t.get_distance_training_volume(SportName.cycling) is not None and t.get_distance_training_volume(SportName.cycling) > 0:
                    self.min_cycling_distance = min(self.min_cycling_distance if self.min_cycling_distance is not None else 0, t.get_distance_training_volume(SportName.cycling))
                    self.max_cycling_distance = max(self.max_cycling_distance if self.max_cycling_distance is not None else 0, t.get_distance_training_volume(SportName.cycling))
                if t.not_tracked_load is not None and t.not_tracked_load > 0:
                    self.max_not_tracked = max(self.max_not_tracked if self.max_not_tracked is not None else 0, t.not_tracked_load)
                if t.strength_endurance_cardiorespiratory_load is not None and t.strength_endurance_cardiorespiratory_load > 0:
                    self.max_strength_endurance_cardiorespiratory = max(self.max_strength_endurance_cardiorespiratory if self.max_strength_endurance_cardiorespiratory is not None else 0, t.strength_endurance_cardiorespiratory_load)
                if t.strength_endurance_strength_load is not None and t.strength_endurance_strength_load > 0:
                    self.max_strength_endurance_strength = max(self.max_strength_endurance_strength if self.max_strength_endurance_strength is not None else 0, t.strength_endurance_strength_load)
                if t.power_drill_load is not None and t.power_drill_load > 0:
                    self.max_power_drill = max(self.max_power_drill if self.max_power_drill is not None else 0, t.power_drill_load)
                if t.maximal_strength_hypertrophic_load is not None and t.maximal_strength_hypertrophic_load > 0:
                    self.max_maximal_strength_hypertrophic = max(self.max_maximal_strength_hypertrophic if self.max_maximal_strength_hypertrophic is not None else 0, t.maximal_strength_hypertrophic_load)
                if t.power_explosive_action_load is not None and t.power_explosive_action_load > 0:
                    self.max_power_explosive_action = max(self.max_power_explosive_action if self.max_power_explosive_action is not None else 0, t.power_explosive_action_load)

    def get_attribute_load(self, attribute_name, value):

        if value is None:
            return None

        min_attribute = "min_" + attribute_name
        max_attribute = "max_" + attribute_name

        if getattr(self, min_attribute) is None:
            setattr(self, min_attribute, value)
            min_value = value
        else:
            if getattr(self, min_attribute) < value:
                min_value = getattr(self, min_attribute)
            else:
                setattr(self, min_attribute, value)
                min_value = value

        if getattr(self, max_attribute) is None:
            setattr(self, max_attribute, value)
            max_value = value
        else:
            if getattr(self, max_attribute) > value:
                max_value = getattr(self, max_attribute)
            else:
                setattr(self, max_attribute, value)
                max_value = value

        if max_value == min_value:
            load = value
            if load > 100:
                load = 100
        else:
            load = (value - min_value) / (max_value - min_value)
            load = load * 100

        return load

    def get_duration_health_load(self, load_value):

        return self.get_attribute_load("duration_health", load_value)

    def get_duration_minutes_load(self, load_value):

        return self.get_attribute_load("duration_minutes", load_value)

    def get_swimming_distance_load(self, load_value):

        return self.get_attribute_load("swimming_distance", load_value)

    def get_cycling_distance_load(self, load_value):

        return self.get_attribute_load("duration_health", load_value)

    def get_walking_distance_load(self, load_value):

        return self.get_attribute_load("walk_run_distance", load_value)

    def get_running_distance_load(self, load_value):

        return self.get_attribute_load("walk_run_distance", load_value)
