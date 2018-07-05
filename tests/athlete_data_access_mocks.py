import datetime
import soreness_and_injury
import session


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

    def get_last_daily_readiness_survey(self, athlete_id):

        daily_readiness = soreness_and_injury.DailyReadinessSurvey()
        daily_readiness.report_date_time = datetime.datetime(2018, 6, 27, 11, 0, 0)

        return daily_readiness

    def get_scheduled_sessions(self, athlete_id, date):

        scheduled_sessions = []

        practice_session = session.PracticeSession()
        practice_session.date = datetime.date(2018, 6, 27)

        scheduled_sessions.append(practice_session)

        return scheduled_sessions
