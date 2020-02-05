# from aws_xray_sdk.core import xray_recorder
# xray_recorder.configure(sampling=False)
# xray_recorder.begin_segment(name="test")
import datetime
from logic.survey_processing import SurveyProcessing, force_datetime_iso, cleanup_sleep_data_from_api, cleanup_hr_data_from_api, create_session
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.body_parts import BodyPart
from models.historic_soreness import HistoricSoreness
from models.stats import AthleteStats
from tests.mocks.mock_datastore_collection import DatastoreCollection
from utils import format_date

def get_soreness(body_part, side, pain=False, severity=0, hist_status=None, reported_date_time=datetime.datetime.now()):
    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(body_part), None)
    soreness.side = side
    soreness.pain = pain
    soreness.severity = severity
    soreness.historic_soreness_status = hist_status
    soreness.reported_date_time = reported_date_time
    return soreness

def get_historic_soreness(body_part, side, pain=False, status=HistoricSorenessStatus.dormant_cleared):
    soreness = HistoricSoreness(body_part_location=BodyPartLocation(body_part), is_pain=pain, side=side)
    soreness.historic_soreness_status = status
    return soreness.json_serialise(api=True)

def test_force_datetime_iso():
    iso_date = '2019-01-15T01:01:01Z'
    event_date_1 = '2019-01-15T01:01:01.001-0500'
    event_date_2 = '2019-01-15T01:01:01.001Z'
    assert force_datetime_iso(iso_date) == iso_date
    assert force_datetime_iso(event_date_1) == iso_date
    assert force_datetime_iso(event_date_2) == iso_date

def get_session_data():
    session_data = {"event_date": "2019-01-12T10:23:08Z",
                    "end_date": "2019-01-12T10:43:08Z",
                    "session_type": 6,
                    "apple_health_kit_id": "5324-AB-54HH-34T",
                    "apple_health_kit_source_name": "Garmin",
                    "sport_name": 52,
                    "duration": 90.5,
                    "calories": 50,
                    "distance": 100,
                    "source": 1,
                    "hr_data": [
                                 {"value": 153, "startDate": "2019-01-12T10:43:08.490-0500", "endDate": "2019-01-12T10:43:08.490-0500"},
                                 {"value": 156, "startDate": "2019-01-12T10:43:03.490-0500", "endDate": "2019-01-12T10:43:03.490-0500"},
                                 {"value": 161, "startDate": "2019-01-12T10:42:58.490-0500", "endDate": "2019-01-12T10:42:58.490-0500"},
                                 {"value": 163, "startDate": "2019-01-12T10:42:56.490-0500", "endDate": "2019-01-12T10:42:56.490-0500"},
                                 {"value": 167, "startDate": "2019-01-12T10:42:50.490-0500", "endDate": "2019-01-12T10:42:50.490-0500"},
                                 {"value": 163, "startDate": "2019-01-12T10:42:47.490-0500", "endDate": "2019-01-12T10:42:47.490-0500"},
                                 {"value": 127, "startDate": "2019-01-12T10:41:23.490-0500", "endDate": "2019-01-12T10:41:23.490-0500"}
                             ],
                     "post_session_survey": {
                                             "event_date": "2019-01-12T10:53:08Z",
                                             "RPE": 3,
                                             "soreness": [{
                                                            "body_part": 16,
                                                            "severity": 2,
                                                            "pain": False,
                                                            "side": 1
                                                        }]
                                            }
                     }
    return session_data

def test_cleanup_hr_data_from_api():
    hr_data = {'startDate': '2019-01-15T01:01:01.001-0500',
               'endDate': '2019-01-15T01:01:01.001-0500',
               'value': 63}
    assert cleanup_hr_data_from_api(hr_data) == {'start_date': '2019-01-15T01:01:01Z',
                                                 'end_date': '2019-01-15T01:01:01Z',
                                                 'value': 63}

def test_cleanup_sleep_data_from_api():
    hr_data = {'startDate': '2019-01-15T01:01:01.001-0500',
               'endDate': '2019-01-15T09:01:01.001-0500',
               'value': 'INBED'}
    assert cleanup_sleep_data_from_api(hr_data) == {'start_date': '2019-01-15T01:01:01Z',
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
    survey_processor = SurveyProcessing('test', datetime.datetime.now())
    survey_processor.process_historic_sleep_data(sleep_data=sleep_data)

    assert len(survey_processor.sleep_history) == 1
    assert len(survey_processor.sleep_history[0].sleep_events) == 10


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
    survey_processor = SurveyProcessing('test', datetime.datetime.now())
    survey_processor.process_historic_sleep_data(sleep_data=sleep_data)

    assert len(survey_processor.sleep_history) == 8
    sleep_109 = [sleep for sleep in survey_processor.sleep_history if sleep.event_date == '2019-01-09'][0]
    assert len(sleep_109.sleep_events) == 2
    sleep_103 = [sleep for sleep in survey_processor.sleep_history if sleep.event_date == '2019-01-03'][0]
    assert len(sleep_103.sleep_events) == 7


def test_create_session_hr_data():
    hr_data = [
               {"value": 153, "startDate": "2019-01-12T10:43:08.490-0500", "endDate": "2019-01-12T10:43:08.490-0500"},
               {"value": 156, "startDate": "2019-01-12T10:43:03.490-0500", "endDate": "2019-01-12T10:43:03.490-0500"},
               {"value": 161, "startDate": "2019-01-12T10:42:58.490-0500", "endDate": "2019-01-12T10:42:58.490-0500"},
               {"value": 163, "startDate": "2019-01-12T10:42:56.490-0500", "endDate": "2019-01-12T10:42:56.490-0500"},
               {"value": 167, "startDate": "2019-01-12T10:42:50.490-0500", "endDate": "2019-01-12T10:42:50.490-0500"},
               {"value": 163, "startDate": "2019-01-12T10:42:47.490-0500", "endDate": "2019-01-12T10:42:47.490-0500"},
               {"value": 127, "startDate": "2019-01-12T10:41:23.490-0500", "endDate": "2019-01-12T10:41:23.490-0500"}
              ]
    survey_processor = SurveyProcessing('test', datetime.datetime.now())
    session = create_session(6, {'event_date': datetime.datetime.now()})
    survey_processor.create_session_hr_data(session, hr_data)

    assert len(survey_processor.heart_rate_data) == 1
    assert len(survey_processor.heart_rate_data[0].hr_workout) == 7


def test_patch_daily_and_historic_soreness_higher_soreness():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    athlete_stats.readiness_soreness = [get_soreness(7, 1, False, 2)]
    athlete_stats.daily_severe_soreness = [get_soreness(7, 1, False, 2)]

    survey_processor = SurveyProcessing('test', datetime.datetime.now(), athlete_stats)
    survey_processor.soreness = [get_soreness(7, 1, False, 3)]
    survey_processor.patch_daily_and_historic_soreness(survey='readiness')

    assert len(survey_processor.athlete_stats.readiness_soreness) == 2
    survey_processor.athlete_stats.update_daily_soreness()
    assert len(survey_processor.athlete_stats.daily_severe_soreness) == 1
    assert survey_processor.athlete_stats.daily_severe_soreness[0].severity == 3


def test_patch_daily_and_historic_soreness_lower_soreness():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    athlete_stats.readiness_soreness = [get_soreness(7, 1, False, 3, reported_date_time=current_time - datetime.timedelta(days=1))]
    athlete_stats.daily_severe_soreness = [get_soreness(7, 1, False, 3, reported_date_time=current_time - datetime.timedelta(days=1))]

    survey_processor = SurveyProcessing('test', datetime.datetime.now(), athlete_stats)
    survey_processor.soreness = [get_soreness(7, 1, False, 2, reported_date_time=current_time)]
    survey_processor.patch_daily_and_historic_soreness(survey='readiness')

    assert len(survey_processor.athlete_stats.readiness_soreness) == 2
    survey_processor.athlete_stats.update_daily_soreness()
    assert len(survey_processor.athlete_stats.daily_severe_soreness) == 1
    assert survey_processor.athlete_stats.daily_severe_soreness[0].severity == 3


def test_session_from_survey():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    session_data = get_session_data()
    del session_data['hr_data']
    del session_data['end_date']
    session_data['source'] = 0
    survey_processor.create_session_from_survey(session_data)

    assert len(survey_processor.sessions) == 1
    assert len(survey_processor.heart_rate_data) == 0
    assert len(survey_processor.soreness) == 1
    assert survey_processor.athlete_stats.session_RPE == 3
    assert survey_processor.sessions[0].duration_health is None
    assert survey_processor.sessions[0].created_date is not None


def test_session_from_survey_hr_data():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.user_age = 25
    session_data = get_session_data()
    survey_processor.create_session_from_survey(session_data)

    assert len(survey_processor.sessions) == 1
    assert len(survey_processor.heart_rate_data) == 1
    assert len(survey_processor.soreness) == 1
    assert survey_processor.athlete_stats.session_RPE == 3
    assert survey_processor.sessions[0].duration_health is not None
    assert survey_processor.sessions[0].created_date is not None
    assert survey_processor.sessions[0].post_session_survey is not None


def test_session_from_survey_no_ps_survey():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.user_age = 25
    session_data = get_session_data()
    del session_data['post_session_survey']
    survey_processor.create_session_from_survey(session_data)

    assert len(survey_processor.sessions) == 1
    assert len(survey_processor.heart_rate_data) == 1
    assert len(survey_processor.soreness) == 0
    assert survey_processor.athlete_stats.session_RPE is None
    assert survey_processor.sessions[0].duration_health is not None
    assert survey_processor.sessions[0].created_date is None
    assert survey_processor.sessions[0].post_session_survey is None


def test_session_from_survey_historic_health_data():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.user_age = 25
    session_data = get_session_data()
    session_obj = survey_processor.create_session_from_survey(session_data, historic_health_data=True)

    assert session_obj.sport_name.value == 52
    assert len(survey_processor.sessions) == 1
    assert len(survey_processor.heart_rate_data) == 1
    assert len(survey_processor.soreness) == 0
    assert survey_processor.athlete_stats.session_RPE is None
    assert session_obj == survey_processor.sessions[0]
    assert session_obj.duration_health is not None
    assert session_obj.post_session_survey is None


def test_session_from_survey_hk_id_and_source():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.user_age = 25
    session_data = get_session_data()
    session_obj = survey_processor.create_session_from_survey(session_data, historic_health_data=True)

    assert session_obj.sport_name.value == 52
    assert len(survey_processor.sessions) == 1
    assert len(survey_processor.heart_rate_data) == 1
    assert len(survey_processor.soreness) == 0
    assert survey_processor.athlete_stats.session_RPE is None
    assert session_obj == survey_processor.sessions[0]
    assert session_obj.apple_health_kit_id == "5324-AB-54HH-34T"
    assert session_obj.apple_health_kit_source_name == "Garmin"


def test_patch_daily_and_historic_soreness_no_existing_doms():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    athlete_stats.historic_soreness = []

    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.soreness = [get_soreness(3, 1, False, 2, reported_date_time=current_time)]
    survey_processor.patch_daily_and_historic_soreness()

    assert len(survey_processor.athlete_stats.historic_soreness) == 1
    doms = survey_processor.athlete_stats.historic_soreness[0]
    assert doms.first_reported_date_time == current_time
    assert doms.max_severity_date_time == current_time
    assert len(doms.historic_severity) == 1


def test_patch_daily_and_historic_soreness_existing_doms_higher_severity():
    event_date_time = datetime.datetime.now() - datetime.timedelta(days=1)
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = event_date_time
    athlete_stats.historic_soreness = []

    survey_processor = SurveyProcessing('test', event_date_time, athlete_stats)
    survey_processor.soreness = [get_soreness(2, 1, False, 2, reported_date_time=event_date_time)]
    survey_processor.patch_daily_and_historic_soreness()
    assert len(survey_processor.athlete_stats.historic_soreness) == 1

    current_time = datetime.datetime.now()
    new_soreness = get_soreness(2, 1, False, 3, reported_date_time=current_time)
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.soreness = [new_soreness]
    survey_processor.patch_daily_and_historic_soreness()

    assert len(survey_processor.athlete_stats.historic_soreness) == 1
    doms = survey_processor.athlete_stats.historic_soreness[0]
    assert doms.max_severity_date_time == current_time
    assert doms.max_severity == new_soreness.severity
    assert doms.first_reported_date_time == event_date_time
    assert len(doms.historic_severity) == 2


def test_patch_daily_and_historic_soreness_existing_doms_same_severity():
    event_date_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = event_date_time
    athlete_stats.historic_soreness = []

    survey_processor = SurveyProcessing('test', event_date_time, athlete_stats)
    survey_processor.soreness = [get_soreness(2, 1, False, 2, reported_date_time=event_date_time )]
    survey_processor.patch_daily_and_historic_soreness()
    assert len(survey_processor.athlete_stats.historic_soreness) == 1

    current_time = datetime.datetime.now()
    new_soreness = get_soreness(2, 1, False, 2, reported_date_time=current_time)
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.soreness = [new_soreness]
    survey_processor.patch_daily_and_historic_soreness()

    assert len(survey_processor.athlete_stats.historic_soreness) == 1
    doms = survey_processor.athlete_stats.historic_soreness[0]
    assert doms.max_severity_date_time == event_date_time
    assert doms.max_severity == new_soreness.severity
    assert doms.first_reported_date_time == event_date_time
    assert len(doms.historic_severity) == 2


def test_patch_daily_and_historic_soreness_existing_doms_pain_reported():
    event_date_time = datetime.datetime.now() - datetime.timedelta(days=1)
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = event_date_time
    athlete_stats.historic_soreness = []

    survey_processor = SurveyProcessing('test', event_date_time, athlete_stats)
    survey_processor.soreness = [get_soreness(2, 1, False, 3, reported_date_time=event_date_time)]
    survey_processor.patch_daily_and_historic_soreness()
    assert len(survey_processor.athlete_stats.historic_soreness) == 1

    current_time = datetime.datetime.now()
    new_soreness = get_soreness(2, 1, True, 3, reported_date_time=current_time)
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.soreness = [new_soreness]
    survey_processor.patch_daily_and_historic_soreness()

    assert len(survey_processor.athlete_stats.historic_soreness) == 1
    doms = survey_processor.athlete_stats.historic_soreness[0]
    assert doms.max_severity_date_time == event_date_time
    assert doms.max_severity == 3
    assert doms.first_reported_date_time == event_date_time
    assert len(doms.historic_severity) == 1


def test_patch_daily_and_historic_soreness_existing_doms_new_body_part():
    event_date_time = datetime.datetime.now() - datetime.timedelta(days=1)
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = event_date_time
    athlete_stats.historic_soreness = []

    survey_processor = SurveyProcessing('test', event_date_time, athlete_stats)
    survey_processor.soreness = [get_soreness(2, 1, False, 3, reported_date_time=event_date_time)]
    survey_processor.patch_daily_and_historic_soreness()
    assert len(survey_processor.athlete_stats.historic_soreness) == 1

    current_time = datetime.datetime.now()
    new_soreness = get_soreness(16, 1, False, 3, reported_date_time=current_time)
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.soreness = [new_soreness]
    survey_processor.patch_daily_and_historic_soreness()

    assert len(survey_processor.athlete_stats.historic_soreness) == 2
    doms_0 = survey_processor.athlete_stats.historic_soreness[0]
    assert doms_0.max_severity_date_time == event_date_time
    assert doms_0.first_reported_date_time == event_date_time
    assert len(doms_0.historic_severity) == 1

    doms_1 = survey_processor.athlete_stats.historic_soreness[1]
    assert doms_1.body_part_location.value == new_soreness.body_part.location.value
    assert doms_1.max_severity_date_time == current_time
    assert doms_1.first_reported_date_time == current_time
    assert len(doms_1.historic_severity) == 1

def test_patch_daily_and_historic_soreness_existing_doms_new_body_part_clear_old():
    event_date_time = datetime.datetime.now() - datetime.timedelta(days=1) + datetime.timedelta(seconds=120)
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = event_date_time
    athlete_stats.historic_soreness = []

    survey_processor = SurveyProcessing('test', event_date_time, athlete_stats)
    survey_processor.soreness = [get_soreness(2, 1, False, 2, reported_date_time=event_date_time)]
    survey_processor.patch_daily_and_historic_soreness()
    survey_processor.datastore_collection = DatastoreCollection()
    assert len(survey_processor.athlete_stats.historic_soreness) == 1

    current_time = datetime.datetime.now()
    new_soreness = get_soreness(16, 1, False, 2, reported_date_time=current_time)
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    datastore_collection = DatastoreCollection()
    survey_processor.datastore_collection = datastore_collection
    survey_processor.soreness = [new_soreness]
    survey_processor.patch_daily_and_historic_soreness()

    assert len(survey_processor.athlete_stats.historic_soreness) == 1



def test_patch_daily_and_historic_soreness_joint():
    current_time = datetime.datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    athlete_stats.historic_soreness = []

    survey_processor = SurveyProcessing('test', datetime.datetime.now(), athlete_stats)
    survey_processor.soreness = [get_soreness(7, 1, False, 2, reported_date_time=current_time)]
    survey_processor.patch_daily_and_historic_soreness()

    assert len(survey_processor.athlete_stats.historic_soreness) == 0
