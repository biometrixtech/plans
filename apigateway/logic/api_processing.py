from models.session import SessionType, SessionFactory
from models.sport import SportName
from models.symptom import Symptom
from models.heart_rate import SessionHeartRate, HeartRateData
from logic.user_stats_processing import UserStatsProcessing
from logic.activity_management import ActivityManager
from logic.heart_rate_processing import HeartRateProcessing
from logic.workout_processing import WorkoutProcessor
from datastores.datastore_collection import DatastoreCollection
from utils import parse_datetime


class APIProcessing(object):
    def __init__(self, user_id, event_date_time, user_stats=None, datastore_collection=DatastoreCollection()):
        self.user_id = user_id
        self.event_date_time = event_date_time
        self.user_stats = user_stats
        self.datastore_collection = datastore_collection
        self.user_age = None
        self.sessions = []
        self.heart_rate_data = []
        self.workout_programs = []
        self.symptoms = []
        self.user_stats_processor = None

    def create_session_from_survey(self, session):
        session_obj = self.convert_session(session)
        self.sessions.append(session_obj)

    def convert_session(self, session):
        existing_session_id = session.get('session_id') or session.get('id')
        event_date = parse_datetime(session['event_date'])
        session_type = session['session_type']
        end_date = session.get('end_date', None)
        if end_date is not None:
            end_date = parse_datetime(end_date)
        sport_name = session.get('sport_name', None)
        if SportName.has_value(sport_name):
            sport_name = SportName(sport_name)
        else:
            sport_name = SportName(None)

        duration = session.get("duration", None)
        description = session.get('description', "")
        calories = session.get("calories", None)
        distance = session.get("distance", None)
        workout_program_module = session.get("workout_program_module", None)
        session_RPE = session.get('session_RPE', None)

        session_data = {
            "user_id": self.user_id,
            "event_date": event_date,
            "end_date": end_date,
            "sport_name": sport_name,
            "duration_minutes": duration,
            "description": description,
            "calories": calories,
            "distance": distance,
            "session_RPE": session_RPE,
            "workout_program_module": workout_program_module
        }
        session_obj = create_session(session_type, session_data)
        if existing_session_id is not None:
            session_obj.id = existing_session_id  # this is a merge case
        if 'hr_data' in session and len(session['hr_data']) > 0:
            heart_rate_processing = HeartRateProcessing(self.user_age)
            self.create_session_hr_data(session_obj, session['hr_data'])
            # session_obj.shrz = heart_rate_processing.get_shrz(self.heart_rate_data[0].hr_workout)
        if session_obj.workout_program_module is not None:
            session_obj.workout_program_module.session_id = session_obj.id
            session_obj.workout_program_module.user_id = session_obj.user_id
            session_obj.workout_program_module.event_date_time = session_obj.event_date
            hr_workout = self.heart_rate_data[0].hr_workout if len(self.heart_rate_data) > 0 else None
            session_training_load = WorkoutProcessor(hr_data=hr_workout, user_age=self.user_age).process_workout(session_obj.workout_program_module)
            session_obj.update_training_loads(session_training_load)
            self.workout_programs.append(session_obj.workout_program_module)
        if len(self.heart_rate_data) > 0:
            if session_obj.workout_program_module is not None:
                session_obj.shrz = session_obj.workout_program_module.aggregate_shrz()
            else:
                session_obj.shrz = heart_rate_processing.get_shrz(self.heart_rate_data[0].hr_workout)
        return session_obj

    def create_session_hr_data(self, session, hr_data):
        session_heart_rate = SessionHeartRate(user_id=self.user_id,
                                              session_id=session.id,
                                              event_date=session.event_date)
        session_heart_rate.hr_workout = [HeartRateData(cleanup_hr_data_from_api(hr)) for hr in hr_data]
        session_heart_rate.hr_workout = [hr for hr in session_heart_rate.hr_workout if hr.start_date is not None]
        self.heart_rate_data.append(session_heart_rate)

    def create_symptom_from_survey(self, symptom):
        symptom['reported_date_time'] = self.event_date_time
        symptom['user_id'] = self.user_id
        symptom = Symptom.json_deserialise(symptom)
        self.symptoms.append(symptom)

    def create_activity(self, activity_type, update_stats=True, activity_id=None, training_session_id=None):
        if update_stats:
            # update stats
            if self.user_stats_processor is None:
                self.user_stats_processor = UserStatsProcessing(
                        self.user_id,
                        event_date=self.event_date_time,
                        datastore_collection=self.datastore_collection
                )
            user_stats = self.user_stats_processor.process_user_stats(current_user_stats=self.user_stats)

            user_stats_datastore = self.datastore_collection.user_stats_datastore
            user_stats_datastore.put(user_stats)

        # create activity
        activity_manager = ActivityManager(
                self.user_id,
                self.datastore_collection,
                self.event_date_time,
                training_sessions=self.sessions,
                symptoms=self.symptoms,
                user_stats=self.user_stats
        )
        if activity_type == 'mobility_wod':
            activity = activity_manager.create_mobility_wod()
        elif activity_type == 'movement_prep':
            activity = activity_manager.create_movement_prep()
        elif activity_type == 'responsive_recovery':
            activity = activity_manager.create_responsive_recovery(responsive_recovery_id=activity_id, training_session_id=training_session_id)
        else:
            raise ValueError("invalid activity type")
        return activity

    def update_stats_injury_risk(self):
        # update stats
        if self.user_stats_processor is None:
            self.user_stats_processor = UserStatsProcessing(
                    self.user_id,
                    event_date=self.event_date_time,
                    datastore_collection=self.datastore_collection
            )
        user_stats = self.user_stats_processor.process_user_stats(current_user_stats=self.user_stats)

        user_stats_datastore = self.datastore_collection.user_stats_datastore
        user_stats_datastore.put(user_stats)

        # create activity
        activity_manager = ActivityManager(
                self.user_id,
                self.datastore_collection,
                self.event_date_time,
                training_sessions=self.sessions,
                symptoms=self.symptoms,
                user_stats=self.user_stats
        )
        activity_manager.prepare_data(default_rpe=5)
        activity_manager.save_session()


def create_session(session_type, data):
    session = SessionFactory().create(SessionType(session_type))
    update_session(session, data)
    return session


def update_session(session, data):
    for key, value in data.items():
        setattr(session, key, value)


def cleanup_hr_data_from_api(hr_data):
    return {
            'start_date': hr_data.get('startDate') or hr_data.get('event_date_time'),
            'end_date': hr_data.get('endDate') or hr_data.get('end_date_time'),
            'value': hr_data['value']
            }



# def force_datetime_iso(event_date):
#     if len(event_date.split('.')) == 2:
#         event_date = event_date.split(".")[0] + 'Z'
#     return event_date
