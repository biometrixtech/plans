from serialisable import Serialisable


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
            'max_shrz': self.max_shrz
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        load_stats = LoadStats()
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

        return load_stats

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
                min_value = value

        if getattr(self, max_attribute) is None:
            setattr(self, max_attribute, value)
            max_value = value
        else:
            if getattr(self, max_attribute) < value:
                max_value = getattr(self, max_attribute)
            else:
                max_value = value

        if max_value == min_value:
            load = value
        else:
            load = (value - min_value) / (max_value - min_value)

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

