from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from models.session import SportTrainingSession
from datetime import datetime, timedelta
from models.sport import SportName
from models.functional_movement import ActivityFunctionalMovementFactory, FunctionalMovementFactory, FunctionalMovementBodyPartSide, SessionFunctionalMovement
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor



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

def test_first_session_no_3s():

    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    for s in sessions:
        session_functional_movement = SessionFunctionalMovement(s)
        session_functional_movement.process()


    j=0


