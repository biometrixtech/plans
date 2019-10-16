import os
os.environ['ENVIRONMENT'] = 'dev'
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from models.session import SportTrainingSession
from datetime import datetime
from datastores.injury_risk_datastore import InjuryRiskDatastore
from models.sport import SportName
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation
from models.athlete_injury_risk import AthleteInjuryRisk
from logic.injury_risk_processing import InjuryRiskProcessor

def get_sessions(dates, rpes, durations, sport_names):

    if len(dates) != len(rpes) != len(durations) != len(sport_names):
        raise Exception("dates, rpes, durations must match in length")

    sessions = []

    for d in range(0, len(dates)):
        session = SportTrainingSession()
        session.event_date = dates[d]
        session.session_RPE = rpes[d]
        session.duration_minutes = durations[d]
        session.sport_name = sport_names[d]
        sessions.append(session)

    return sessions

def test_write_injury_risk_dict():
    user_id = 'test'
    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.tight = 1
    soreness.reported_date_time = dates[0]

    proc = InjuryRiskProcessor(dates[0], [soreness], sessions, {})
    injury_risk_dict = proc.process(update_historical_data=True)
    athlete_injury_risk = AthleteInjuryRisk(user_id)
    athlete_injury_risk.items = injury_risk_dict
    InjuryRiskDatastore().put(athlete_injury_risk)

    injury_risk_dict_from_mongo = InjuryRiskDatastore().get(user_id)
    assert len(injury_risk_dict) == len(injury_risk_dict_from_mongo)