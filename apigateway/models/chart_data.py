from serialisable import Serialisable
from datetime import datetime, timedelta
from utils import format_date, parse_datetime, parse_date
from fathomapi.utils.exceptions import InvalidSchemaException
from models.sport import SportName

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

        training_volume_data = sorted(list(self.data.values()), key=lambda x: x.date, reverse=False)

        return training_volume_data

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
        if training_volume is not None:
            self.data[training_session.event_date.date()].training_volume += training_volume
            self.data[training_session.event_date.date()].sport_names.add(training_session.sport_name)
