from fathomapi.api.config import Config
Config.set('FILENAMES', {'exercise_library': 'exercise_library_fathom.json',
                           'body_part_mapping': 'body_part_mapping_fathom.json'})

from models.modalities import ModalityBase
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.body_parts import BodyPart
from datetime import datetime, timedelta


def test_complete_plan():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Complete"


def test_comprehensive_plan():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.pain = True

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Comprehensive"


def test_efficient_plan():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 1.5
    soreness.side = 1

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Efficient"


def test_efficient_sensitivity_pers_soreness_today_plan():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 1.5
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    soreness.daily = True

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Complete"


def test_efficient_sensitivity_pers_pain_today_plan():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 1.5
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    soreness.daily = False

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Complete"


def test_efficient_sensitivity_pers_soreness_plan():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 1.5
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=15)
    soreness.first_reported_date_time = historic_date_time
    soreness.daily = False

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Complete"


def test_complete_sensitivity_pers_soreness_today_plan():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    soreness.daily = True

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Complete"


def test_complete_sensitivity_pers_pain_today_plan():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    soreness.daily = False

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Complete"


def test_complete_sensitivity_pers_soreness_plan():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=15)
    soreness.first_reported_date_time = historic_date_time
    soreness.daily = False

    base = ModalityBase(current_date_time)
    base.set_plan_dosage([soreness], False)

    assert base.default_plan == "Complete"