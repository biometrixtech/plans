from enum import Enum
#from models.soreness_base import BodyPartSide
import statistics


class DescriptorType(Enum):
    soreness = 0
    pain = 1
    tightness = 2


class DescriptorMeasures(object):
    def __init__(self):
        self.daily = 0
        self.historic_3_7 = 0
        self.historic_7_14 = 0

    def set_values(self, value_list):
        if len(value_list) > 1:
            k=0
        elif len(value_list) == 1:
            self.daily = value_list[0]
        # if len(value_list) > 0:
        #     self.daily = value_list[len(value_list) - 1]
        # if 7 <= len(value_list) < 14:
        #     three_day_average = statistics.mean(value_list[-3:])
        #     seven_day_average = statistics.mean(value_list[-7:])
        #     if seven_day_average > 0:
        #         self.historic_3_7 = three_day_average / seven_day_average
        #     else:
        #         self.historic_3_7 = 0
        # elif len(value_list) >= 14:
        #     if None in value_list:
        #         i=0
        #     three_day_average = statistics.mean(value_list[-3:])
        #     seven_day_average = statistics.mean(value_list[-7:])
        #     fourteen_day_average = statistics.mean(value_list[-14:])
        #     if seven_day_average > 0:
        #         self.historic_3_7 = three_day_average / seven_day_average
        #     if fourteen_day_average > 0:
        #         self.historic_7_14 = seven_day_average / fourteen_day_average


class Descriptor(DescriptorMeasures):
    def __init__(self, descriptor_type):
        super().__init__()
        self.descriptor_type = descriptor_type

    def set_descriptor_measures(self, soreness_date_dictionary, body_part_side):

        values_list = []

        #for s in soreness_date_dictionary:
        if len(soreness_date_dictionary) == 0:
            values_list.append(0)
        if self.descriptor_type == DescriptorType.soreness:
            values = [t.severity for t in soreness_date_dictionary
                      if not t.pain and t.body_part.location == body_part_side.body_part_location
                      and t.side == body_part_side.side if t.severity is not None]
        elif self.descriptor_type == DescriptorType.pain:
            values = [t.severity for t in soreness_date_dictionary
                      if t.pain and t.body_part.location == body_part_side.body_part_location
                      and t.side == body_part_side.side if t.severity is not None]
        else:
            values = [t.movement for t in soreness_date_dictionary
                      if t.body_part.location == body_part_side.body_part_location and t.side == body_part_side.side if t.movement is not None]
        if len(values) > 0:
            values_list.append(values[0])
        # else:
        #     values_list.append(0)

        self.set_values(values_list)


class BodyPartPrediction(object):
    def __init__(self, body_part_side):
        self.body_part_side = body_part_side
        self.pain = 0
        self.soreness = 0
        self.tightness = 0
        self.inflammation_score = 0
        self.muscle_spasm_score = 0

    def set_predictions(self, soreness_list, inflammation_score, muscle_spasm_score):

        for s in soreness_list:
            if s.body_part.location == self.body_part_side.body_part_location and s.side == self.body_part_side.side:
                if s.pain:
                    self.pain = s.severity
                else:
                    self.soreness = s.severity
                self.tightness = s.movement

        self.inflammation_score = inflammation_score
        self.muscle_spasm_score = muscle_spasm_score


class BodyPartDescriptors(object):
    def __init__(self, body_part_side):
        self.body_part_side = body_part_side
        self.pain = Descriptor(DescriptorType.pain)
        self.soreness = Descriptor(DescriptorType.soreness)
        self.tightness = Descriptor(DescriptorType.tightness)

    def set_descriptor_values(self, soreness_date_dictionary):

        self.pain.set_descriptor_measures(soreness_date_dictionary, self.body_part_side)
        self.soreness.set_descriptor_measures(soreness_date_dictionary, self.body_part_side)
        self.tightness.set_descriptor_measures(soreness_date_dictionary, self.body_part_side)


class BodyPartModel(object):
    def __init__(self):
        self.ramp = 0
        self.is_tissue_overload = False
        self.is_inflammation = False
        self.is_muscle_spasm = False
        self.infammation_score = 0
        self.muscle_spasm_score = 0
        self.body_part_descriptors = []
        self.body_part_predictors = []

    def set_descriptors(self, soreness_date_dictionary):

        for b in self.body_part_descriptors:
            b.set_descriptor_values(soreness_date_dictionary)

    def export_to_list(self):
        record = []
        for d in self.body_part_descriptors:
            record.extend([d.pain.daily,
                           #d.pain.historic_3_7,
                           #d.pain.historic_7_14,
                           d.soreness.daily,
                           #d.soreness.historic_3_7,
                           #d.soreness.historic_7_14,
                           d.tightness.daily,
                           #d.tightness.historic_3_7,
                           #d.tightness.historic_7_14,
                           ])

        record.extend([self.ramp, self.is_tissue_overload, self.is_inflammation, self.is_muscle_spasm, self.infammation_score, self.muscle_spasm_score])
        return record

    def export_predictors_to_list(self):
        record = []
        for p in self.body_part_predictors:
            record.extend([0 if p.pain < 1 else 1, 0 if p.soreness <1 else 1, 0 if p.tightness < 1 else 1, 0 if p.inflammation_score < 1 else 1, 0 if p.muscle_spasm_score < 1 else 1])
            #record.extend([0 if p.tightness < 1 else 1])
        return record

    def export_column_names(self):
        record = []
        for d in self.body_part_descriptors:
            column_prefix = d.body_part_side.body_part_location.name + "-" + str(d.body_part_side.side)
            record.extend([column_prefix + "-pain_daily",
                           #column_prefix + "-pain_historic_3_7",
                           #column_prefix + "-pain_historic_7_14",
                           column_prefix + "-soreness_daily",
                           #column_prefix + "-soreness_historic_3_7",
                           #column_prefix + "-soreness_historic_7_14",
                           column_prefix + "-tightness_daily",
                           #column_prefix + "-tightness_historic_3_7",
                           #column_prefix + "-tightness_historic_7_14",
                           ])
        record.extend(["ramp", "is_tissue_overload", "is_inflammation", "is_muscle_spasm", "inflammation_score", "muscle_spasm_score"])

        return record

    def export_predictor_column_names(self):
        record = []
        for p in self.body_part_predictors:
            p_column_prefix = p.body_part_side.body_part_location.name + "-" + str(p.body_part_side.side)
            record.extend([p_column_prefix + "-pain",
                           p_column_prefix + "-soreness",
                           p_column_prefix + "-tightness",
                           p_column_prefix + "-inflammation_score",
                           p_column_prefix + "-muscle_spasm_score",
                           ])
            #record.extend([p_column_prefix + "-tightness"])

        return record

