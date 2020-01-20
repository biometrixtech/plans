from fathomapi.api.config import Config
Config.set('FILENAMES', {'exercise_library': 'exercise_library_fathom.json',
                           'body_part_mapping': 'body_part_mapping_fathom.json'})

import pytest
from datetime import datetime
from models.stats import AthleteStats
from logic.survey_processing import SurveyProcessing
from logic.session_processing import merge_sessions
from models.session import SessionSource


def get_hk_session_data():
    session_data = [{"event_date": "2019-01-12T10:23:08Z",
                    "end_date": "2019-01-12T10:43:08Z",
                    "session_type": 6,
                    "apple_health_kit_id": "5324-AB-54HH-34T",
                    "apple_health_kit_source_name": "Garmin",
                    "sport_name": 52,
                    "duration": 75,
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
                             ]
                     }]
    return session_data

def get_manual_session():
    session_data = {"event_date": "2019-01-12T10:23:08Z",
                         "end_date": "2019-01-12T10:43:08Z",
                         "session_type": 6,
                         "sport_name": 52,
                         "duration": 90.5,
                         "source": 0,
                         "hr_data": [],
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

def get_3s_session():
    session_data = {"event_date": "2019-01-12T10:23:08Z",
                         "end_date": "2019-01-12T10:43:08Z",
                         "session_type": 6,
                         "sport_name": 52,
                         "duration": 105,
                         "source": 2,
                         "hr_data": [],
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


def test_merge_new_hk_and_new_manual_session():
    current_time = datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.user_age = 25
    sessions = get_hk_session_data()
    destination_session = get_manual_session()
    for s in sessions:
        survey_processor.create_session_from_survey(s, historic_health_data=False)

    destination_session = survey_processor.convert_session(destination_session, historic_health_data=False)

    plan_training_sessions = merge_sessions(["5324-AB-54HH-34T"],[],None,destination_session, survey_processor.sessions,[])

    assert len(plan_training_sessions) == 2
    assert plan_training_sessions[0].deleted is True
    assert plan_training_sessions[1].deleted is False
    assert plan_training_sessions[1].apple_health_kit_id is None
    assert plan_training_sessions[1].apple_health_kit_source_name is None
    assert plan_training_sessions[1].source_session_ids == [plan_training_sessions[0].id]
    assert plan_training_sessions[1].merged_apple_health_kit_ids == [plan_training_sessions[0].apple_health_kit_id]
    assert plan_training_sessions[1].merged_apple_health_kit_source_names == [plan_training_sessions[0].apple_health_kit_source_name]
    assert plan_training_sessions[1].duration_minutes == 90.5
    assert plan_training_sessions[1].duration_health == plan_training_sessions[0].duration_health
    assert plan_training_sessions[1].calories == plan_training_sessions[0].calories
    assert plan_training_sessions[1].distance == plan_training_sessions[0].distance
    assert plan_training_sessions[1].source == plan_training_sessions[0].source


def test_merge_new_hk_and_existing_manual_session():
    current_time = datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.user_age = 25
    sessions = get_hk_session_data()
    destination_session = get_manual_session()
    for s in sessions:
        survey_processor.create_session_from_survey(s, historic_health_data=False)

    destination_session = survey_processor.convert_session(destination_session, historic_health_data=False)
    destination_session_id = destination_session.id
    plan_training_sessions = [destination_session]

    plan_training_sessions = merge_sessions(["5324-AB-54HH-34T"],[],destination_session_id,None, survey_processor.sessions,plan_training_sessions)

    assert len(plan_training_sessions) == 2
    assert plan_training_sessions[0].deleted is True
    assert plan_training_sessions[1].deleted is False
    assert plan_training_sessions[1].apple_health_kit_id is None
    assert plan_training_sessions[1].apple_health_kit_source_name is None
    assert plan_training_sessions[1].source_session_ids == [plan_training_sessions[0].id]
    assert plan_training_sessions[1].merged_apple_health_kit_ids == [plan_training_sessions[0].apple_health_kit_id]
    assert plan_training_sessions[1].merged_apple_health_kit_source_names == [plan_training_sessions[0].apple_health_kit_source_name]
    assert plan_training_sessions[1].duration_minutes == 90.5
    assert plan_training_sessions[1].duration_health == plan_training_sessions[0].duration_health
    assert plan_training_sessions[1].calories == plan_training_sessions[0].calories
    assert plan_training_sessions[1].distance == plan_training_sessions[0].distance
    assert plan_training_sessions[1].source == plan_training_sessions[0].source


def test_merge_new_hk_and_3s_session():
    current_time = datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.user_age = 25
    sessions = get_hk_session_data()
    destination_session = get_3s_session()
    for s in sessions:
        survey_processor.create_session_from_survey(s, historic_health_data=False)

    destination_session = survey_processor.convert_session(destination_session, historic_health_data=False)
    destination_session_id = destination_session.id
    plan_training_sessions = [destination_session]

    plan_training_sessions = merge_sessions(["5324-AB-54HH-34T"],[],destination_session_id,None, survey_processor.sessions,plan_training_sessions)

    assert len(plan_training_sessions) == 2
    assert plan_training_sessions[0].deleted is True
    assert plan_training_sessions[1].deleted is False
    assert plan_training_sessions[1].apple_health_kit_id is None
    assert plan_training_sessions[1].apple_health_kit_source_name is None
    assert plan_training_sessions[1].source_session_ids == [plan_training_sessions[0].id]
    assert plan_training_sessions[1].merged_apple_health_kit_ids == [plan_training_sessions[0].apple_health_kit_id]
    assert plan_training_sessions[1].merged_apple_health_kit_source_names == [plan_training_sessions[0].apple_health_kit_source_name]
    assert plan_training_sessions[1].duration_minutes == 105
    assert plan_training_sessions[1].duration_health == plan_training_sessions[0].duration_health
    assert plan_training_sessions[1].calories == plan_training_sessions[0].calories
    assert plan_training_sessions[1].distance == plan_training_sessions[0].distance
    assert plan_training_sessions[1].source == SessionSource.user_health

def test_raise_exception_id_and_session():
    current_time = datetime.now()
    athlete_stats = AthleteStats('test')
    athlete_stats.event_date = current_time
    survey_processor = SurveyProcessing('test', current_time, athlete_stats)
    survey_processor.user_age = 25
    sessions = get_hk_session_data()
    destination_session = get_manual_session()
    for s in sessions:
        survey_processor.create_session_from_survey(s, historic_health_data=False)

    destination_session = survey_processor.convert_session(destination_session, historic_health_data=False)
    destination_session_id = destination_session.id
    plan_training_sessions = [destination_session]

    with pytest.raises(Exception):
        assert merge_sessions(["5324-AB-54HH-34T"],[],destination_session_id,destination_session, survey_processor.sessions,plan_training_sessions)
