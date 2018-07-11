import pymongo
import datetime
import logic.training as training
import logic.session as session
import config
from logic.soreness_and_injury import DailySoreness, DailyReadinessSurvey, PostSessionSoreness
import uuid


class AthleteDataAccess(object):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id

    def get_last_daily_readiness_survey(self):

        daily_readiness = DailyReadinessSurvey()

        collection = config.get_mongo_collection('dailyreadiness')
        readiness_cursor = collection.find({"user_id": self.athlete_id}).limit(1).sort("date_time",
                                                                                              pymongo.DESCENDING)
        for record in readiness_cursor:
            daily_readiness.report_date_time = record["date_time"]
            daily_readiness.sleep_quality = record["sleep_quality"]
            daily_readiness.readiness = record["readiness"]
            for soreness in record["soreness"]:
                daily_soreness = DailySoreness()
                daily_soreness.body_part = soreness["body_part"]
                daily_soreness.severity = soreness["severity"]
                daily_readiness.soreness.append(daily_soreness)

        return daily_readiness

    def get_last_post_session_surveys(self, start_date_time, end_date_time):

        post_session_survey = PostSessionSoreness()

        return post_session_survey

    def get_athlete_injury_history(self):

        injury_history = []

        return injury_history

    def get_athlete_current_training_cycle(self):

        training_cycle = training.TrainingCycle()

        return training_cycle

    def get_scheduled_sessions(self, date):

        scheduled_sessions = []

        collection = config.get_mongo_collection('training')
        schedule_cursor = collection.find({"user_id": self.athlete_id})
        day_of_week = date.weekday()

        for schedule in schedule_cursor:

            cross_training = schedule["cross_training"]
            cross_training_days_of_week = cross_training["days_of_week"]
            if cross_training_days_of_week is not None and len(cross_training_days_of_week) > 0:
                if day_of_week in cross_training_days_of_week:
                    cross_training_session = session.StrengthConditioningSession()
                    cross_training_session.day_of_week = session.DayOfWeek(day_of_week)
                    cross_training_session.date = date.strftime('%Y-%m-%d')
                    cross_training_session.id = uuid.uuid4()
                    cross_training_session.duration_minutes = cross_training["duration"]
                    cross_training_session.description = ",".join(cross_training["activities"])
                    scheduled_sessions.append(cross_training_session)

            sports = schedule["sports"]
            for sport in sports:
                practice = sport["practice"]
                competition = sport["competition"]
                practice_days_of_week = practice["days_of_week"]
                if practice_days_of_week is not None and len(practice_days_of_week) > 0:
                    if day_of_week in practice_days_of_week:
                        practice_session = session.PracticeSession()
                        practice_session.day_of_week = session.DayOfWeek(day_of_week)
                        practice_session.date = date.strftime('%Y-%m-%d')
                        practice_session.id = uuid.uuid4()
                        practice_session.duration_minutes = practice["duration"]
                        practice_session.description = "Practice (" + sport["sport"] + ")"
                        scheduled_sessions.append(practice_session)
                competition_days_of_week = competition["days_of_week"]
                if competition_days_of_week is not None and len(competition_days_of_week) > 0:
                    if day_of_week in competition_days_of_week:
                        game_session = session.Game()
                        game_session.day_of_week = session.DayOfWeek(day_of_week)
                        game_session.date = date.strftime('%Y-%m-%d')
                        game_session.id = uuid.uuid4()
                        game_session.duration_minutes = 0   # TODO: look up from internal data
                        game_session.description = "Competition (" + sport["sport"] + ")"
                        scheduled_sessions.append(game_session)

        return scheduled_sessions

    def get_completed_exercises(self):

        completed_exercises = []

        return completed_exercises
