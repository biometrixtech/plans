from serialisable import Serialisable
from utils import format_date


class DataSeries(Serialisable):
    def __init__(self, date, value):
        self.date = date
        self.value = value

    def json_serialise(self):
        ret ={
            'date': format_date(self.date),
            'value': self.value
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):

        data_series = DataSeries(input_dict["date"], input_dict["value"])

        return data_series