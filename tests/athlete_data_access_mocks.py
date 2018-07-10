import datetime
import logic.soreness_and_injury as soreness_and_injury
import logic.session as session
import uuid


class AthleteDataAccessMorning(object):

    def get_last_daily_readiness_survey(self, athlete_id):

        daily_readiness = soreness_and_injury.DailyReadinessSurvey()
        daily_readiness.report_date_time = datetime.datetime(2018, 6, 27, 11, 0, 0)

        return daily_readiness

    def get_athlete_injury_history(self, athlete_id):

        injury_history = []

        injury1 = soreness_and_injury.Injury()
        injury1.body_part = soreness_and_injury.BodyPartLocation.ankle
        injury1.injury_type = soreness_and_injury.InjuryType.ligament
        injury1.injury_descriptor = soreness_and_injury.InjuryDescriptor.sprain
        injury1.date = datetime.date(2017, 10, 1)
        injury1.days_missed = soreness_and_injury.DaysMissedDueToInjury.less_than_7_days

        injury2 = soreness_and_injury.Injury()
        injury2.body_part = soreness_and_injury.BodyPartLocation.ankle
        injury2.injury_type = soreness_and_injury.InjuryType.ligament
        injury2.injury_descriptor = soreness_and_injury.InjuryDescriptor.sprain
        injury2.date = datetime.date(2018, 3, 1)
        injury2.days_missed = soreness_and_injury.DaysMissedDueToInjury.less_than_7_days

        injury_history.append(injury1)
        injury_history.append(injury2)

    def get_scheduled_sessions(self, athlete_id, date):

        scheduled_sessions = []

        return scheduled_sessions


class AthleteDataAccessAfternoon(object):

    def get_last_daily_readiness_survey(self, athlete_id):

        daily_readiness = soreness_and_injury.DailyReadinessSurvey()
        daily_readiness.report_date_time = datetime.datetime(2018, 6, 27, 15, 0, 0)

        return daily_readiness

    def get_scheduled_sessions(self, athlete_id, date):

        scheduled_sessions = []

        return scheduled_sessions


class AthleteDataAccessMorningPractice(object):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id

    def get_last_daily_readiness_survey(self):

        daily_readiness = soreness_and_injury.DailyReadinessSurvey()
        daily_readiness_soreness = soreness_and_injury.DailySoreness()
        daily_readiness_soreness.body_part = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation(12), 1)
        daily_readiness_soreness.severity = 2
        daily_readiness.soreness.append(daily_readiness_soreness)

        daily_readiness.report_date_time = datetime.datetime(2018, 6, 27, 11, 0, 0)

        return daily_readiness

    def get_last_post_session_survey(self):

        post_session_survey = soreness_and_injury.PostSessionSurvey()
        post_session_soreness = soreness_and_injury.PostSessionSoreness()
        post_session_soreness.body_part = soreness_and_injury.BodyPart(soreness_and_injury.BodyPartLocation(12), 1)
        post_session_soreness.severity = 2
        post_session_survey.soreness.append(post_session_soreness)
        post_session_survey.report_date_time = datetime.datetime(2018, 6, 26, 17, 0, 0)

        return post_session_survey

    def get_scheduled_sessions(self, date):

        scheduled_sessions = []

        practice_session = session.PracticeSession()
        practice_session.date = datetime.date(2018, 6, 27)
        practice_session.id = uuid.uuid4()

        scheduled_sessions.append(practice_session)

        return scheduled_sessions
