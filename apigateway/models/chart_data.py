from serialisable import Serialisable
from datetime import datetime, timedelta
from utils import format_date, parse_datetime, parse_date
from fathomapi.utils.exceptions import InvalidSchemaException
from models.soreness import BodyPart, BodyPartSide
from models.sport import SportName
from logic.soreness_processing import SorenessCalculator


class BaseChart(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.data = {}

        self.auto_fill_data()

    def __setattr__(self, name, value):
        if name in ['end_date']:
            if value is not None and not isinstance(value, datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = DataSeriesData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            chart_data.day_of_week = day_of_week
            self.data[chart_data.date] = chart_data

    def get_output_list(self):

        data = sorted(list(self.data.values()), key=lambda x: x.date, reverse=False)

        return data


class BaseChartBoolean(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.data = {}

        self.auto_fill_data()

    def __setattr__(self, name, value):
        if name in ['end_date']:
            if value is not None and not isinstance(value, datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = DataSeriesBooleanData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            chart_data.day_of_week = day_of_week
            self.data[chart_data.date] = chart_data

    def get_output_list(self):

        data = sorted(list(self.data.values()), key=lambda x: x.date, reverse=False)

        return data


class DataSeriesBaseData(Serialisable):
    def __init__(self, default_value):
        self.date = None
        self.day_of_week = ""
        self.value = default_value
        self.default_value = default_value

    def json_serialise(self):
        ret = {
            'date': format_date(self.date),
            'day_of_week': self.day_of_week,
            'value': self.value
        }
        return ret


class DataSeriesData(DataSeriesBaseData):
    def __init__(self):
        super().__init__(0)
        self.date = None
        self.day_of_week = ""

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', '')
        chart_data.value = input_dict.get('value', 0)
        return chart_data


class DataSeriesBooleanData(DataSeriesBaseData):
    def __init__(self):
        super().__init__(False)
        self.date = None
        self.day_of_week = ""

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', '')
        chart_data.value = input_dict.get('value', False)
        return chart_data


class TrainingVolumeChart(BaseChart):
    def __init__(self, end_date):
        super().__init__(end_date)

    def add_training_volume(self, training_session, load_stats):

        training_volume = training_session.training_volume(load_stats)
        if training_volume is not None and training_session.event_date.date() in self.data:
            self.data[training_session.event_date.date()].training_volume += training_volume
            self.data[training_session.event_date.date()].sport_names.add(training_session.sport_name)

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = TrainingVolumeChartData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            chart_data.day_of_week = day_of_week
            self.data[chart_data.date] = chart_data


class TrainingVolumeChartData(Serialisable):
    def __init__(self):
        self.date = None
        self.day_of_week = ""
        self.sport_names = set()
        self.training_volume = 0

    def json_serialise(self):
        ret = {
            'date': format_date(self.date),
            'day_of_week': self.day_of_week,
            'sport_names': [sport_name.value for sport_name in self.sport_names if sport_name is not None],
            'training_volume': self.training_volume
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', '')
        chart_data.sport_names = set(SportName(sport_name) for sport_name in input_dict.get('sport_names', []))
        chart_data.training_volume = input_dict.get('training_volume', 0)
        return chart_data


class MuscularStrainChart(BaseChart):
    def __init__(self, end_date):
        super().__init__(end_date)

    def add_muscular_strain(self, muscular_strain):

        if muscular_strain is not None and muscular_strain.date.date() in self.data:
            self.data[muscular_strain.date.date()].value += muscular_strain.value


class HighRelativeLoadChart(BaseChartBoolean):
    def __init__(self, end_date):
        super().__init__(end_date)

    def add_relative_load(self, relative_load):

        if relative_load is not None and relative_load.date.date() in self.data:
            self.data[relative_load.date.date()].value = True


class BodyPartChartData(Serialisable):
    def __init__(self):
        self.date = None
        self.day_of_week = ""
        self.value = 0

    def json_serialise(self):
        ret = {
            'date': format_date(self.date),
            'day_of_week': self.day_of_week,
            'value': self.value
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        chart_data = cls()
        chart_data.date = input_dict['date']
        chart_data.day_of_week = input_dict.get('day_of_week', "")
        chart_data.value = input_dict.get('value', 0)
        return chart_data


class BodyPartChartCollection(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.body_parts = {}

    def process_soreness_list(self, soreness_list):

        for s in soreness_list:
            body_part_side = BodyPartSide(s.body_part.location, s.side)
            if body_part_side not in self.body_parts:
                self.body_parts[body_part_side] = BodyPartChart(self.end_date)
                self.body_parts[body_part_side].auto_fill_data()
            self.body_parts[body_part_side].add_soreness(s)

    def get_soreness_dictionary(self):

        soreness_dictionary = {}

        for body_part_side, body_part_chart in self.body_parts.items():
            if body_part_chart.contains_soreness_data:
                soreness_dictionary[body_part_side] = body_part_chart.get_soreness_output_list()
            else:
                soreness_dictionary.pop(body_part_side, None)

        return soreness_dictionary

    def get_pain_dictionary(self):

        pain_dictionary = {}

        for body_part_side, body_part_chart in self.body_parts.items():
            if body_part_chart.contains_pain_data:
                pain_dictionary[body_part_side] = body_part_chart.get_pain_output_list()
            else:
                pain_dictionary.pop(body_part_side, None)

        return pain_dictionary


class BodyPartChart(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.soreness_data = {}
        self.pain_data = {}
        self.contains_soreness_data = False
        self.contains_pain_data = False

        self.auto_fill_data()

    def __setattr__(self, name, value):
        if name in ['end_date']:
            if value is not None and not isinstance(value, datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def get_soreness_output_list(self):

        if self.contains_soreness_data:
            data = sorted(list(self.soreness_data.values()), key=lambda x: x.date, reverse=False)
        else:
            data = []

        return data

    def get_pain_output_list(self):

        if self.contains_pain_data:
            data = sorted(list(self.pain_data.values()), key=lambda x: x.date, reverse=False)
        else:
            data = []

        return data

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            soreness_chart_data = BodyPartChartData()
            soreness_chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')
            soreness_chart_data.day_of_week = day_of_week

            pain_chart_data = BodyPartChartData()
            pain_chart_data.date = (start_date + timedelta(days=i)).date()
            pain_chart_data.day_of_week = day_of_week
            self.soreness_data[soreness_chart_data.date] = soreness_chart_data
            self.pain_data[pain_chart_data.date] = pain_chart_data

    def add_soreness(self, soreness):

        if soreness.pain:
            if soreness is not None and soreness.reported_date_time.date() in self.pain_data:
                self.pain_data[soreness.reported_date_time.date()].value = max(
                    SorenessCalculator().get_severity(soreness.severity, soreness.movement),
                    self.pain_data[soreness.reported_date_time.date()].value)
                self.contains_pain_data = True
        else:
            if soreness is not None and soreness.reported_date_time.date() in self.soreness_data:
                self.soreness_data[soreness.reported_date_time.date()].value = max(
                    SorenessCalculator().get_severity(soreness.severity, soreness.movement),
                    self.soreness_data[soreness.reported_date_time.date()].value)
                self.contains_soreness_data = True
