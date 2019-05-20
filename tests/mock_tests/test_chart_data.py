from models.chart_data import TrainingVolumeChartData, TrainingVolumeChart
from utils import parse_date


def test_14_days_empty_data():

    chart = TrainingVolumeChart(parse_date("2019-01-31"))

    chart_data = chart.get_output_list()

    assert len(chart_data) == 14
    assert chart_data[13].date == parse_date("2019-01-31").date()
    assert chart_data[0].date == parse_date("2019-01-18").date()
