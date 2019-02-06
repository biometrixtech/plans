import datetime
from logic.survey_processing import SurveyProcessing, force_datetime_iso
from models.soreness import  Soreness, BodyPartLocation, BodyPart, HistoricSoreness, HistoricSorenessStatus



def test_force_datetime_iso():
    iso_date = '2019-01-15T01:01:01Z'
    event_date_1 = '2019-01-15T01:01:01.001-0500'
    event_date_2 = '2019-01-15T01:01:01.001Z'
    assert force_datetime_iso(iso_date) == iso_date
    assert force_datetime_iso(event_date_1) == iso_date
    assert force_datetime_iso(event_date_2) == iso_date


def test_cleanup_hr_data_from_api():
    hr_data = {'startDate': '2019-01-15T01:01:01.001-0500',
               'endDate': '2019-01-15T01:01:01.001-0500',
               'value': 63}
    assert SurveyProcessing().cleanup_hr_data_from_api(hr_data) == {'start_date': '2019-01-15T01:01:01Z',
                                                                    'end_date': '2019-01-15T01:01:01Z',
                                                                    'value': 63}

def test_cleanup_sleep_data_from_api():
    hr_data = {'startDate': '2019-01-15T01:01:01.001-0500',
               'endDate': '2019-01-15T09:01:01.001-0500',
               'value': 'INBED'}
    assert SurveyProcessing().cleanup_sleep_data_from_api(hr_data) == {'start_date': '2019-01-15T01:01:01Z',
                                                                       'end_date': '2019-01-15T09:01:01Z',
                                                                       'sleep_type': "INBED"}


def test_process_historic_sleep_data():
    sleep_data = [{"value": "INBED", "startDate": "2019-01-09T00:09:50.212-0500", "endDate": "2019-01-09T07:35:21.256-0500"},
                  {"value": "INBED", "startDate": "2019-01-09T00:10:52.000-0500", "endDate": "2019-01-09T07:30:23.306-0500"},
                  {"value": "INBED", "startDate": "2019-01-09T00:11:00.000-0500", "endDate": "2019-01-09T07:30:14.516-0500"},
                  {"value": "INBED", "startDate": "2019-01-09T09:09:50.212-0500", "endDate": "2019-01-09T11:02:09.754-0500"},
                  {"value": "ASLEEP", "startDate": "2019-01-09T00:29:51.212-0500", "endDate": "2019-01-09T07:19:51.212-0500"},
                  {"value": "ASLEEP", "startDate": "2019-01-09T00:29:51.212-0500", "endDate": "2019-01-09T06:49:51.212-0500"},
                  {"value": "UNKNOWN", "startDate": "2019-01-09T06:49:51.212-0500", "endDate": "2019-01-09T07:02:09.754-0500"},
                  {"value": "UNKNOWN", "startDate": "2019-01-09T00:09:50.212-0500", "endDate": "2019-01-09T00:29:51.212-0500"},
                  {"value": "UNKNOWN", "startDate": "2019-01-09T00:09:50.212-0500", "endDate": "2019-01-09T00:29:51.212-0500"},
                  {"value": "UNKNOWN", "startDate": "2019-01-09T07:19:51.212-0500", "endDate": "2019-01-09T07:35:21.256-0500"}
                 ]
    historic_sleep_data = SurveyProcessing().process_historic_sleep_data(user_id='test_user', sleep_data=sleep_data)

    assert len(historic_sleep_data) == 1
    assert len(historic_sleep_data[0].sleep_events) == 10


def test_process_historic_sleep_data_multi_days():
    sleep_data = [{"value": "INBED", "startDate": "2019-01-25T00:00:00.000-0500", "endDate": "2019-01-25T07:34:09.030-0500"},

                  {"value": "INBED", "startDate": "2019-01-11T01:12:25.249-0500", "endDate": "2019-01-11T07:30:22.717-0500"},

                  {"value": "INBED", "startDate": "2019-01-10T07:37:36.000-0500", "endDate": "2019-01-10T07:39:08.998-0500"},
                  {"value": "INBED", "startDate": "2019-01-10T07:34:20.000-0500", "endDate": "2019-01-10T07:35:24.000-0500"},
                  {"value": "INBED", "startDate": "2019-01-10T00:00:00.000-0500", "endDate": "2019-01-10T07:34:12.000-0500"},

                  {"value": "INBED", "startDate": "2019-01-09T00:09:50.212-0500", "endDate": "2019-01-09T07:35:21.256-0500"},
                  {"value": "ASLEEP", "startDate": "2019-01-09T00:29:51.212-0500", "endDate": "2019-01-09T07:19:51.212-0500"},

                  {"value": "INBED", "startDate": "2019-01-08T00:00:00.000-0500", "endDate": "2019-01-08T07:40:02.673-0500"},

                  {"value": "INBED", "startDate": "2019-01-07T00:00:00.000-0500", "endDate": "2019-01-07T07:30:03.514-0500"},

                  {"value": "INBED", "startDate": "2019-01-04T00:00:00.000-0500", "endDate": "2019-01-04T07:30:15.568-0500"},

                  {"value": "INBED", "startDate": "2019-01-03T06:49:04.000-0500", "endDate": "2019-01-03T06:50:40.000-0500"},
                  {"value": "INBED", "startDate": "2019-01-02T20:16:11.842-0500", "endDate": "2019-01-03T06:49:22.114-0500"},
                  {"value": "UNKNOWN", "startDate": "2019-01-03T06:26:12.842-0500", "endDate": "2019-01-03T06:49:22.114-0500"},
                  {"value": "INBED", "startDate": "2019-01-03T00:00:00.000-0500", "endDate": "2019-01-03T06:49:04.000-0500"},
                  {"value": "ASLEEP", "startDate": "2019-01-03T05:36:12.842-0500", "endDate": "2019-01-03T06:26:12.842-0500"},
                  {"value": "UNKNOWN", "startDate": "2019-01-03T05:26:12.842-0500", "endDate": "2019-01-03T05:36:12.842-0500"},
                  {"value": "ASLEEP", "startDate": "2019-01-02T20:26:12.842-0500", "endDate": "2019-01-03T05:26:12.842-0500"}]
    historic_sleep_data = SurveyProcessing().process_historic_sleep_data(user_id='test_user', sleep_data=sleep_data)

    assert len(historic_sleep_data) == 8
    sleep_109 = [sleep for sleep in historic_sleep_data if sleep.event_date == '2019-01-09'][0]
    assert len(sleep_109.sleep_events) == 2
    sleep_103 = [sleep for sleep in historic_sleep_data if sleep.event_date == '2019-01-03'][0]
    assert len(sleep_103.sleep_events) == 7