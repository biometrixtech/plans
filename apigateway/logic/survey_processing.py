import datetime
from utils import parse_datetime, format_datetime, fix_early_survey_event_date, format_date
from fathomapi.utils.xray import xray_recorder
from models.session import SessionType, SessionFactory, StrengthConditioningType, SessionSource
from models.post_session_survey import PostSurvey
from models.sport import SportName
from models.soreness import BodyPart, BodyPartLocation, HistoricSorenessStatus, Soreness
from models.daily_plan import DailyPlan
from models.heart_rate import SessionHeartRate, HeartRateData
from models.sleep_data import DailySleepData, SleepEvent
from logic.stats_processing import StatsProcessing
from logic.soreness_processing import SorenessCalculator
from datastores.datastore_collection import DatastoreCollection


class SurveyProcessing(object):
    def __init__(self, user_id, event_date, athlete_stats=None):
        self.user_id = user_id
        self.event_date = format_date(event_date)
        self.athlete_stats = athlete_stats
        self.sessions = []
        self.sleep_history = []
        self.heart_rate_data = []
        self.soreness = []
        self.plans = []

    def create_session_from_survey(self, session, historic_health_data=False):
        event_date = parse_datetime(session['event_date'])
        end_date = session.get('end_date', None)
        if end_date is not None:
            end_date = parse_datetime(end_date)
        session_type = session['session_type']
        try:
            sport_name = session['sport_name']
            sport_name = SportName(sport_name)
        except:
            sport_name = SportName(None)
        try:
            strength_and_conditioning_type = session['strength_and_conditioning_type']
            strength_and_conditioning_type = StrengthConditioningType(strength_and_conditioning_type)
        except:
            strength_and_conditioning_type = StrengthConditioningType(None)
        duration = session.get("duration", None)
        description = session.get('description', "")
        session_event_date = format_datetime(event_date)
        session_end_date = format_datetime(end_date)
        calories = session.get("calories", None)
        distance = session.get("distance", None)
        source = session.get("source", None)
        deleted = session.get("deleted", False)
        ignored = session.get("ignored", False)
        if end_date is not None:
            duration_health = round((end_date - event_date).seconds / 60, 2)
        else:
            duration_health = None
        session_data = {"sport_name": sport_name,
                        "strength_and_conditioning_type": strength_and_conditioning_type,
                        "description": description,
                        "duration_minutes": duration,
                        "duration_health": duration_health,
                        "event_date": session_event_date,
                        "end_date": session_end_date,
                        "calories": calories,
                        "distance": distance,
                        "source": source,
                        "deleted": deleted,
                        "ignored": ignored}
        if 'post_session_survey' in session:
            survey = PostSurvey(event_date=session['post_session_survey']['event_date'],
                                survey=session['post_session_survey'])
            # TODO: if the frontend error is fixed, this needs to be removed
            if survey.event_date.hour < 3 and event_date.hour >= 3:
                session_data['event_date'] = format_datetime(event_date - datetime.timedelta(days=1))
            survey.event_date = fix_early_survey_event_date(survey.event_date)
            if "clear_candidates" in session['post_session_survey'] and len(session['post_session_survey']['clear_candidates']) > 0:
                self.process_clear_status_answers(session['post_session_survey']['clear_candidates'],
                                                  event_date,
                                                  survey.soreness)
            session_data['created_date'] = survey.event_date

            # update session_RPE and add post_session_survey to session
            if not historic_health_data and not session_data['deleted'] and not session_data['ignored']:
                session_data['post_session_survey'] = survey
                if self.athlete_stats.session_RPE is not None and survey.RPE is not None:
                    self.athlete_stats.session_RPE = max(survey.RPE, self.athlete_stats.session_RPE)
                    self.athlete_stats.session_RPE_event_date = self.event_date
                elif survey.RPE is not None:
                    self.athlete_stats.session_RPE = survey.RPE
                    self.athlete_stats.session_RPE_event_date = self.event_date
        session_obj = create_session(session_type, session_data)
        if 'hr_data' in session and len(session['hr_data']) > 0:
            self.create_session_hr_data(session_obj, session['hr_data'])

        if session_obj.post_session_survey is not None:
            self.soreness.extend(session_obj.post_session_survey.soreness)
        self.sessions.append(session_obj)
        if historic_health_data:
            return session_obj

    def patch_daily_and_historic_soreness(self, survey='readiness'):
        severe_soreness = [s for s in self.soreness if not s.pain]
        severe_pain = [s for s in self.soreness if s.pain]
        if (len(severe_soreness) + len(severe_pain)) > 0:
            self.athlete_stats.daily_severe_soreness_event_date = self.event_date
            self.athlete_stats.daily_severe_pain_event_date = self.event_date
            if survey == 'post_session':
                self.athlete_stats.update_post_session_soreness(severe_soreness)
                self.athlete_stats.update_post_session_pain(severe_pain)
            else:
                self.athlete_stats.update_readiness_soreness(severe_soreness)
                self.athlete_stats.update_readiness_pain(severe_pain)
            self.athlete_stats.update_daily_soreness()
            self.athlete_stats.update_daily_pain()
            # update historic soreness
            for s in self.soreness:
                self.athlete_stats.update_historic_soreness(s, self.event_date)

    def process_clear_status_answers(self, clear_candidates, event_date, soreness):

        plan_event_date = format_date(event_date)
        stats_processing = StatsProcessing(self.athlete_stats.athlete_id,
                                           plan_event_date,
                                           DatastoreCollection())
        stats_processing.set_start_end_times()
        stats_processing.load_historical_data()
        soreness_list_25 = stats_processing.merge_soreness_from_surveys(
            stats_processing.get_readiness_soreness_list(stats_processing.last_25_days_readiness_surveys),
            stats_processing.get_ps_survey_soreness_list(stats_processing.last_25_days_ps_surveys)
            )
        for q3_response in clear_candidates:
            body_part_location = BodyPartLocation(q3_response['body_part'])
            side = q3_response['side']
            severity = q3_response.get('severity', 0) # don't error out because of mobile bug
            movement = q3_response.get('movement', None)
            pain = q3_response.get('pain', False)
            status = q3_response.get('status', 'dormant_cleared')
            if severity == 0:
                pain = True if "pain" in status else False
            if severity > 0:
                sore_part = Soreness()
                sore_part.body_part = BodyPart(body_part_location, None)
                sore_part.pain = pain
                sore_part.severity = severity
                sore_part.movement = movement
                sore_part.side = side
                sore_part.reported_date_time = event_date
                soreness.append(sore_part)
            if status in ['acute_pain', 'almost_persistent_2_pain_acute']:
                self.athlete_stats.historic_soreness = stats_processing.answer_acute_pain_question(self.athlete_stats.historic_soreness,
                                           soreness_list_25,
                                           body_part_location=body_part_location,
                                           side=side,
                                           is_pain=pain,
                                           question_response_date=plan_event_date,
                                           severity_value=SorenessCalculator().get_severity(severity, movement))
            else:
                self.athlete_stats.historic_soreness = stats_processing.answer_persistent_2_question(self.athlete_stats.historic_soreness,
                                           soreness_list_25,
                                           body_part_location=body_part_location,
                                           side=side,
                                           is_pain=pain,
                                           question_response_date=plan_event_date,
                                           severity_value=SorenessCalculator().get_severity(severity, movement),
                                           current_status=HistoricSorenessStatus[status])

    @xray_recorder.capture('logic.survey_processing.historic_workout_data')
    def process_historic_health_data(self, sessions, event_date):
        days_with_plan = [plan.event_date for plan in self.plans]
        for session in sessions:
            session_event_date = parse_datetime(session['event_date'])
            plan_date = format_date(session_event_date)
            if plan_date in days_with_plan:
                daily_plan = [plan for plan in self.plans if plan.event_date == plan_date][0]
            else:
                daily_plan = DailyPlan(event_date=plan_date)
                daily_plan.user_id = self.user_id
                self.plans.append(daily_plan)
                days_with_plan.append(plan_date)

            stored_health_sessions = [session.event_date for session in daily_plan.training_sessions if session.source in [SessionSource.health, SessionSource.combined]]
            user_sessions = [session for session in daily_plan.training_sessions if session.source == SessionSource.user]
            if session_event_date not in stored_health_sessions:
                session_obj = self.create_session_from_survey(session, historic_health_data=True)
                if len(user_sessions) > 0:
                    session_obj = match_sessions(user_sessions, session_obj)
                daily_plan.training_sessions.append(session_obj)
                daily_plan.last_updated = event_date
                if 'hr_data' in session and len(session['hr_data']) > 0:
                    self.create_session_hr_data(session_obj, session['hr_data'])

        self.plans = [plan for plan in self.plans if plan.last_updated == event_date]

    # @xray_recorder.capture('logic.survey_processing.historic_sleep_data')
    def process_historic_sleep_data(self, sleep_data):
        sleep_events = [SleepEvent(cleanup_sleep_data_from_api(sd)) for sd in sleep_data]
        days_with_sleep_data = set([se.event_date for se in sleep_events])
        for sleep_date in days_with_sleep_data:
            daily_sleep_data = DailySleepData(user_id=self.user_id,
                                              event_date=sleep_date)
            daily_sleep_data.sleep_events = [se for se in sleep_events if se.event_date == sleep_date]
            self.sleep_history.append(daily_sleep_data)

    def create_session_hr_data(self, session, hr_data):
        session_heart_rate = SessionHeartRate(user_id=self.user_id,
                                              session_id=session.id,
                                              event_date=session.event_date)
        session_heart_rate.hr_workout = [HeartRateData(cleanup_hr_data_from_api(hr)) for hr in hr_data]
        self.heart_rate_data.append(session_heart_rate)

def create_session(session_type, data):
    session = SessionFactory().create(SessionType(session_type))
    update_session(session, data)
    return session


def update_session(session, data):
    for key, value in data.items():
        setattr(session, key, value)

def cleanup_hr_data_from_api(hr_data):
    return {
            'start_date': force_datetime_iso(hr_data['startDate']),
            'end_date': force_datetime_iso(hr_data['endDate']),
            'value': hr_data['value']
            }

def cleanup_sleep_data_from_api(sleep_data):
    return {
            'start_date': force_datetime_iso(sleep_data['startDate']),
            'end_date': force_datetime_iso(sleep_data['endDate']),
            'sleep_type': sleep_data['value']
            }

def force_datetime_iso(event_date):
    if len(event_date.split('.')) == 2:
        event_date = event_date.split(".")[0] + 'Z'
    return event_date

def match_sessions(user_sessions, health_session):
    for user_session in user_sessions:
        if user_session.sport_name  == health_session.sport_name:
            if user_session.created_date is None:
                if user_session.post_session_survey is not None:
                    user_session.created_date = user_session.post_session_survey.event_date
            if user_session.created_date is not None and 0. < (user_session.created_date - health_session.end_date).seconds / 60. < 120:
                user_session.event_date = health_session.event_date
                user_session.end_date = health_session.end_date
                user_session.duration_health = health_session.duration_health
                user_session.calories = health_session.calories
                user_session.distance = health_session.distance
                user_session.source = SessionSource.combined
                return user_session
    return health_session
