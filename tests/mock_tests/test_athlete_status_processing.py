from fathomapi.api.config import Config
Config.set('FILENAMES', {'exercise_library': 'exercise_library_fathom.json',
                           'body_part_mapping': 'body_part_mapping_fathom.json'})

import datetime
from logic.athlete_status_processing import AthleteStatusProcessing
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.body_parts import BodyPart
from models.historic_soreness import HistoricSoreness


def get_soreness(body_part, side, pain=False, severity=0, hist_status=None):
    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(body_part), None)
    soreness.side = side
    soreness.pain = pain
    soreness.severity = severity
    soreness.historic_soreness_status = hist_status
    return soreness

def get_historic_soreness(body_part, side, pain=False, status=HistoricSorenessStatus.dormant_cleared):
    soreness = HistoricSoreness(body_part_location=BodyPartLocation(body_part), is_pain=pain, side=side)
    soreness.historic_soreness_status = status
    return soreness.json_serialise(api=True)

def test_remove_duplicate_sore_body_parts_pain_and_soreness():
    athlete_status_processor = AthleteStatusProcessing(user_id='test', event_date=datetime.datetime.now())
    athlete_status_processor.sore_body_parts = [get_soreness(7, 1, True, 2),
                                                get_soreness(7, 1, False, 3)]
    athlete_status_processor.cleaned_sore_body_parts = athlete_status_processor.remove_duplicate_sore_body_parts()
    assert len(athlete_status_processor.cleaned_sore_body_parts) == 1
    assert athlete_status_processor.cleaned_sore_body_parts == [get_soreness(7, 1, True).json_serialise(api=True)]

def test_remove_duplicate_sore_body_parts_pain_diff_severity():
    athlete_status_processor = AthleteStatusProcessing(user_id='test', event_date=datetime.datetime.now())
    athlete_status_processor.sore_body_parts = [get_soreness(7, 1, True, 2),
                                                get_soreness(7, 1, True, 3)]
    athlete_status_processor.sore_body_parts = athlete_status_processor.remove_duplicate_sore_body_parts()
    assert len(athlete_status_processor.cleaned_sore_body_parts) == 1
    assert athlete_status_processor.cleaned_sore_body_parts == [get_soreness(7, 1, True).json_serialise(api=True)]

def test_remove_duplicate_sore_body_parts_soreness_diff_severity():
    athlete_status_processor = AthleteStatusProcessing(user_id='test', event_date=datetime.datetime.now())
    athlete_status_processor.sore_body_parts = [get_soreness(7, 1, False, 2),
                                                get_soreness(7, 1, False, 3)]
    athlete_status_processor.sore_body_parts = athlete_status_processor.remove_duplicate_sore_body_parts()
    assert len(athlete_status_processor.cleaned_sore_body_parts) == 1
    assert athlete_status_processor.cleaned_sore_body_parts == [get_soreness(7, 1, False).json_serialise(api=True)]

def test_remove_duplicates_sore_body_parts_historic_soreness_clear_candidate():
    athlete_status_processor = AthleteStatusProcessing(user_id='test', event_date=datetime.datetime.now())
    athlete_status_processor.sore_body_parts = [get_soreness(7, 1, True, 2).json_serialise(api=True)]
    athlete_status_processor.clear_candidates = [get_historic_soreness(7, 1, True, status=HistoricSorenessStatus.persistent_2_pain)]
    athlete_status_processor.remove_duplicates_sore_body_parts_historic_soreness()

    assert len(athlete_status_processor.cleaned_sore_body_parts) == 0
    assert len(athlete_status_processor.clear_candidates) == 1
    assert athlete_status_processor.clear_candidates == [get_historic_soreness(7, 1, True, HistoricSorenessStatus.persistent_2_pain)]

def test_remove_duplicates_sore_body_parts_historic_soreness_hist_sore_status():
    athlete_status_processor = AthleteStatusProcessing(user_id='test', event_date=datetime.datetime.now())
    athlete_status_processor.sore_body_parts = [get_soreness(7, 1, True, 2).json_serialise(api=True)]
    athlete_status_processor.hist_sore_status = [get_historic_soreness(7, 1, True, status=HistoricSorenessStatus.persistent_2_pain)]
    athlete_status_processor.remove_duplicates_sore_body_parts_historic_soreness()

    assert len(athlete_status_processor.cleaned_sore_body_parts) == 0
    assert len(athlete_status_processor.hist_sore_status) == 1
    assert athlete_status_processor.hist_sore_status == [get_historic_soreness(7, 1, True, HistoricSorenessStatus.persistent_2_pain)]

def test_remove_duplicates_sore_body_parts_historic_soreness_tipping_candidate():
    athlete_status_processor = AthleteStatusProcessing(user_id='test', event_date=datetime.datetime.now())
    athlete_status_processor.cleaned_sore_body_parts = [get_soreness(7, 1, False, 2).json_serialise(api=True)]
    athlete_status_processor.dormant_tipping_candidates = [get_historic_soreness(7, 1, False, status=HistoricSorenessStatus.almost_persistent_soreness),
                                                           get_historic_soreness(7, 2, False, status=HistoricSorenessStatus.almost_persistent_soreness)]
    athlete_status_processor.remove_duplicates_sore_body_parts_historic_soreness()

    assert len(athlete_status_processor.cleaned_sore_body_parts) == 1
    assert athlete_status_processor.cleaned_sore_body_parts == [get_soreness(7, 1, False, 2, HistoricSorenessStatus.almost_persistent_soreness).json_serialise(api=True)]
    assert len(athlete_status_processor.dormant_tipping_candidates) == 1
    assert athlete_status_processor.dormant_tipping_candidates == [get_historic_soreness(7, 2, False, HistoricSorenessStatus.almost_persistent_soreness)]

