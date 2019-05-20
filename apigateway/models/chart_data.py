from serialisable import Serialisable
from datetime import datetime, timedelta
from utils import format_date, parse_datetime, parse_date
from fathomapi.utils.exceptions import InvalidSchemaException
from models.soreness import BodyPart, BodyPartSide


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


class TrainingVolumeChart(object):
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

    def get_output_list(self):

        data = sorted(list(self.data.values()), key=lambda x: x.date, reverse=False)

        return data

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            chart_data = TrainingVolumeChartData()
            chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')[0]
            chart_data.day_of_week = day_of_week
            self.data[chart_data.date] = chart_data

    def add_training_volume(self, training_session, load_stats):

        training_volume = training_session.training_volume(load_stats)
        if training_volume is not None and training_session.event_date.date() in self.data:
            self.data[training_session.event_date.date()].training_volume += training_volume
            self.data[training_session.event_date.date()].sport_names.add(training_session.sport_name)


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
            soreness_dictionary[body_part_side] = body_part_chart.get_soreness_output_list()

        return soreness_dictionary

    def get_pain_dictionary(self):

        pain_dictionary = {}

        for body_part_side, body_part_chart in self.body_parts.items():
            pain_dictionary[body_part_side] = body_part_chart.get_pain_output_list()

        return pain_dictionary


class BodyPartChart(object):
    def __init__(self, end_date):
        self.end_date = end_date
        self.soreness_data = {}
        self.pain_data = {}

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

        data = sorted(list(self.soreness_data.values()), key=lambda x: x.date, reverse=False)

        return data

    def get_pain_output_list(self):

        data = sorted(list(self.pain_data.values()), key=lambda x: x.date, reverse=False)

        return data

    def auto_fill_data(self):

        start_date = self.end_date - timedelta(days=14)

        for i in range(1, 15):
            soreness_chart_data = BodyPartChartData()
            soreness_chart_data.date = (start_date + timedelta(days=i)).date()
            day_of_week = (start_date + timedelta(days=i)).strftime('%a')[0]
            soreness_chart_data.day_of_week = day_of_week

            pain_chart_data = BodyPartChartData()
            pain_chart_data.date = (start_date + timedelta(days=i)).date()
            pain_chart_data.day_of_week = day_of_week
            self.soreness_data[soreness_chart_data.date] = soreness_chart_data
            self.pain_data[pain_chart_data.date] = pain_chart_data

    def add_soreness(self, soreness):

        if soreness.pain:
            if soreness is not None and soreness.reported_date_time.date() in self.pain_data:
                self.pain_data[soreness.reported_date_time.date()].value = max(soreness.severity, self.pain_data[soreness.reported_date_time.date()].value)
        else:
            if soreness is not None and soreness.reported_date_time.date() in self.soreness_data:
                self.soreness_data[soreness.reported_date_time.date()].value = max(soreness.severity, self.soreness_data[soreness.reported_date_time.date()].value)

