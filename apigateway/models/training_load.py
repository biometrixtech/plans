from enum import Enum
from fathomapi.utils.xray import xray_recorder
from models.soreness_base import BodyPartSide
from serialisable import Serialisable
from models.training_volume import StandardErrorRange
from models.movement_tags import DetailedAdaptationType, RankedAdaptationType, AdaptationDictionary, SubAdaptationType, AdaptationTypeMeasure, TrainingType


class TrainingLoad(object):
    def __init__(self):
        self.power_load = StandardErrorRange()
        self.rpe_load = StandardErrorRange()


class LoadType(Enum):
    rpe = 0
    power = 1


class TrainingTypeLoad(Serialisable):
    def __init__(self):
        self.load = {}
        self.training_types = []

    def json_serialise(self):

        ret = {
            'load': [{"training_type": key.value,
                      "training_load": value.json_serialise()} for key, value in self.load.items()],
            'training_types': [t.json_serialise() for t in self.training_types]

        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):

        training_type_load = TrainingTypeLoad()

        for load in input_dict.get('load', []):
            training_type_load.load[
                TrainingType(load['training_type'])] = StandardErrorRange.json_deserialise(load['training_load'])
        training_type_load.training_types = [RankedAdaptationType.json_deserialise(r) for r in
                                             input_dict['training_types'] if
                                             input_dict.get('training_types') is not None]

        return training_type_load

    def add_load(self, training_type, load_range):

        if training_type not in self.load:
            self.load[training_type] = load_range
        else:
            self.load[training_type].add(load_range)

    def add(self, training_type_load):

        training_types = list(TrainingTypeLoad)

        for training_type in training_types:
            load_value = getattr(self, training_type.name)
            source_load_value = getattr(training_type_load, training_type.name)
            if source_load_value is not None:
                if load_value is None:
                    setattr(self, training_type.name, source_load_value)
                else:
                    setattr(self, training_type.name, load_value.add(source_load_value))

    def rank_types(self):
        sorted_training = {k: v for k, v in
                           sorted(self.load.items(), key=lambda item: item[1].lowest_value(),
                                  reverse=True)}
        training_rank = 1
        last_value = None
        for training_type, load in sorted_training.items():

            if last_value is None:
                last_value = load.plagiarize()
            if load.highest_value() < last_value.highest_value():
                training_rank += 1
                last_value = load.plagiarize()

            self.training_types.append(RankedAdaptationType(AdaptationTypeMeasure.training_type, training_type, training_rank, None))  # TODO: need actual duration
            # training_rank += 1


class DetailedTrainingLoad(Serialisable):
    def __init__(self):
        self.mobility = None
        self.corrective = None
        self.base_aerobic_training = None
        self.anaerobic_threshold_training = None
        self.high_intensity_anaerobic_training = None
        self.stabilization_endurance = None
        self.stabilization_strength = None
        self.stabilization_power = None
        self.functional_strength = None
        self.muscular_endurance = None
        self.strength_endurance = None
        self.hypertrophy = None
        self.maximal_strength = None
        self.speed = None
        self.sustained_power = None
        self.power = None
        self.maximal_power = None

        self.detailed_adaptation_types = []
        self.sub_adaptation_types = []
        self.total_load = None

    def json_serialise(self):
        ret = {
            'mobility': self.mobility.json_serialise() if self.mobility is not None else None,
            'corrective': self.corrective.json_serialise() if self.corrective is not None else None,
            'base_aerobic_training': self.base_aerobic_training.json_serialise() if self.base_aerobic_training is not None else None,
            'anaerobic_threshold_training': self.anaerobic_threshold_training.json_serialise() if self.anaerobic_threshold_training is not None else None,
            'high_intensity_anaerobic_training': self.high_intensity_anaerobic_training.json_serialise() if self.high_intensity_anaerobic_training is not None else None,
            'stabilization_endurance': self.stabilization_endurance.json_serialise() if self.stabilization_endurance is not None else None,
            'stabilization_strength': self.stabilization_strength.json_serialise() if self.stabilization_strength is not None else None,
            'stabilization_power': self.stabilization_power.json_serialise() if self.stabilization_power is not None else None,
            'functional_strength': self.functional_strength.json_serialise() if self.functional_strength is not None else None,
            'muscular_endurance': self.muscular_endurance.json_serialise() if self.muscular_endurance is not None else None,
            'strength_endurance': self.strength_endurance.json_serialise() if self.strength_endurance is not None else None,
            'hypertrophy': self.hypertrophy.json_serialise() if self.hypertrophy is not None else None,
            'maximal_strength': self.maximal_strength.json_serialise() if self.maximal_strength is not None else None,
            'speed': self.speed.json_serialise() if self.speed is not None else None,
            'sustained_power': self.sustained_power.json_serialise() if self.sustained_power is not None else None,
            'power': self.power.json_serialise() if self.power is not None else None,
            'maximal_power': self.maximal_power.json_serialise() if self.maximal_power is not None else None,
            'detailed_adaptation_types': [d.json_serialise() for d in self.detailed_adaptation_types],
            'sub_adaptation_types': [s.json_serialise() for s in self.sub_adaptation_types]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):

        load = DetailedTrainingLoad()
        load.mobility = StandardErrorRange.json_deserialise(input_dict['mobility']) if input_dict.get('mobility') is not None else None
        load.corrective = StandardErrorRange.json_deserialise(input_dict['corrective']) if input_dict.get(
            'corrective') is not None else None
        load.base_aerobic_training = StandardErrorRange.json_deserialise(input_dict['base_aerobic_training']) if input_dict.get(
            'base_aerobic_training') is not None else None
        load.anaerobic_threshold_training = StandardErrorRange.json_deserialise(input_dict['anaerobic_threshold_training']) if input_dict.get(
            'anaerobic_threshold_training') is not None else None
        load.high_intensity_anaerobic_training = StandardErrorRange.json_deserialise(input_dict['high_intensity_anaerobic_training']) if input_dict.get(
            'high_intensity_anaerobic_training') is not None else None
        load.stabilization_endurance = StandardErrorRange.json_deserialise(input_dict['stabilization_endurance']) if input_dict.get(
            'stabilization_endurance') is not None else None
        load.stabilization_strength = StandardErrorRange.json_deserialise(input_dict['stabilization_strength']) if input_dict.get(
            'stabilization_strength') is not None else None
        load.stabilization_power = StandardErrorRange.json_deserialise(input_dict['stabilization_power']) if input_dict.get(
            'stabilization_power') is not None else None
        load.functional_strength = StandardErrorRange.json_deserialise(input_dict['functional_strength']) if input_dict.get(
            'functional_strength') is not None else None
        load.muscular_endurance = StandardErrorRange.json_deserialise(input_dict['muscular_endurance']) if input_dict.get(
            'muscular_endurance') is not None else None
        load.strength_endurance = StandardErrorRange.json_deserialise(input_dict['strength_endurance']) if input_dict.get(
            'strength_endurance') is not None else None
        load.hypertrophy = StandardErrorRange.json_deserialise(input_dict['hypertrophy']) if input_dict.get(
            'hypertrophy') is not None else None
        load.maximal_strength = StandardErrorRange.json_deserialise(input_dict['maximal_strength']) if input_dict.get(
            'maximal_strength') is not None else None
        load.speed = StandardErrorRange.json_deserialise(input_dict['speed']) if input_dict.get(
            'speed') is not None else None
        load.sustained_power = StandardErrorRange.json_deserialise(input_dict['sustained_power']) if input_dict.get(
            'sustained_power') is not None else None
        load.power = StandardErrorRange.json_deserialise(input_dict['power']) if input_dict.get(
            'power') is not None else None
        load.maximal_power = StandardErrorRange.json_deserialise(input_dict['maximal_power']) if input_dict.get(
            'maximal_power') is not None else None

        load.detailed_adaptation_types = [RankedAdaptationType.json_deserialise(r) for r in input_dict['detailed_adaptation_types'] if input_dict.get('detailed_adaptation_types') is not None]
        load.sub_adaptation_types = [RankedAdaptationType.json_deserialise(r) for r in
                                          input_dict['sub_adaptation_types'] if
                                          input_dict.get('sub_adaptation_types') is not None]

        return load

    def add(self, detailed_training_load):

        detailed_types = list(DetailedAdaptationType)

        for detailed_type in detailed_types:
            load_value = getattr(self, detailed_type.name)
            source_load_value = getattr(detailed_training_load, detailed_type.name)
            if source_load_value is not None:
                if load_value is None:
                    setattr(self, detailed_type.name, source_load_value)
                else:
                    load_value.add(source_load_value)
                    setattr(self, detailed_type.name, load_value)

    def add_load(self, detailed_adaptation_type: DetailedAdaptationType, load_range):

        attribute_name = detailed_adaptation_type.name

        if getattr(self, attribute_name) is None:
            setattr(self, attribute_name, StandardErrorRange())
        self_load_range = getattr(self, attribute_name)
        self_load_range.add(load_range)

        if self.total_load is None:
            self.total_load = StandardErrorRange()
        self.total_load.add(load_range)

    def rank_adaptation_types(self):

        adaptation_dictionary = AdaptationDictionary()
        detailed_types = list(DetailedAdaptationType)

        detailed_rank = {}
        sub_adaptation_rank = {}

        for detailed_type in detailed_types:
            load_value = getattr(self, detailed_type.name)
            if load_value is not None and load_value.lowest_value() > 0:
                detailed_rank[detailed_type] = load_value
                sub_adaptation_type = adaptation_dictionary.detailed_types[detailed_type]
                if sub_adaptation_type not in sub_adaptation_rank:
                    sub_adaptation_rank[sub_adaptation_type] = load_value
                else:
                    sub_adaptation_rank[sub_adaptation_type].add(load_value)

        sorted_details = {k: v for k, v in sorted(detailed_rank.items(), key=lambda item: item[1].lowest_value(), reverse=True)}
        sorted_subs = {k: v for k, v in sorted(sub_adaptation_rank.items(), key=lambda item: item[1].lowest_value(), reverse=True)}

        rank = 1

        last_value = None
        for detailed_type, load in sorted_details.items():
            if last_value is None:
                last_value = load.plagiarize()
            if load.highest_value() < last_value.highest_value():
                rank += 1
                last_value = load.plagiarize()
            self.detailed_adaptation_types.append(RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, detailed_type, rank, None))  # TODO: need actual duration
            # rank += 1

        sub_rank = 1
        last_value = None

        for sub_type, load in sorted_subs.items():
            if last_value is None:
                last_value = load.plagiarize()
            if load.highest_value() < last_value.highest_value():
                sub_rank += 1
                last_value = load.plagiarize()
            self.sub_adaptation_types.append(RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type, sub_type, sub_rank, None))  # TODO: need actual duration
            # sub_rank += 1

    def get_total_load(self):
        detailed_types = list(DetailedAdaptationType)
        total_load = StandardErrorRange()
        for detailed_type in detailed_types:
            load_value = getattr(self, detailed_type.name)
            if load_value is not None:
                total_load.add(load_value)
        return total_load


class MuscleDetailedLoad(object):
    def __init__(self, provider_id, program_id):
        self.provider_id = provider_id
        self.program_id = program_id
        self.items = {}

    def json_serialise(self):
        ret = {
            'provider_id': self.provider_id,
            'program_id': self.program_id,
            'items': [{"body_part": key.json_serialise(),
                       "detailed_load": value.json_serialise()} for key, value in self.items.items()]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        detailed_load = cls(input_dict['provider_id'], input_dict['program_id'])
        for item in input_dict.get('items', []):
            detailed_load.items[BodyPartSide.json_deserialise(item['body_part'])] = DetailedTrainingLoad.json_deserialise(item['detailed_load'])

        return detailed_load


class CompletedSessionDetails(Serialisable):
    def __init__(self, event_date_time, provider_id, workout_id):
        self.event_date_time = event_date_time
        self.provider_id = provider_id
        self.workout_id = workout_id
        self.session_detailed_load = DetailedTrainingLoad()
        self.session_training_type_load = TrainingTypeLoad()
        #self.muscle_detailed_load = {}
        self.ranked_muscle_load = []
        #self.ranked_training_types = []
        self.duration = 0
        self.session_RPE = None
        self.rpe_load = None
        self.power_load = None

    def json_serialise(self):
        ret = {
            'event_date_time': self.event_date_time,
            'provider_id': self.provider_id,
            'workout_id': self.workout_id,
            'session_detailed_load': self.session_detailed_load.json_serialise(),
            #'muscle_detailed_load': self.muscle_detailed_load.json_serialise(),
            'duration': self.duration,
            'session_rpe': self.session_RPE.json_serialise(),
            'rpe_load': self.rpe_load.joson_serialise(),
            'power_load': self.power_load.json_serialise()
        }

        return ret


# TODO need some easy way to see the summary so we can easily rank the workouts
class MuscleDetailedLoadSummary(object):
    def __init__(self, provider_id):
        self.provider_id = provider_id

