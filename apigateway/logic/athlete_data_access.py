import pymongo
import database_config
import logic.training as training
import logic.session as session
import config
import logic.soreness_and_injury as soreness_and_injury

class AthleteDataAccess(object):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id
        # self.mongo_client = pymongo.MongoClient(database_config.mongodb_dev)

    def get_last_daily_readiness_survey(self):

        daily_readiness = soreness_and_injury.DailyReadinessSurvey()

        # db = self.mongo_client.movementStats
        collection = config.get_mongo_collection('dailyreadiness')
        readiness_cursor = collection.find({"user_id": self.athlete_id}).limit(1).sort("date_time",
                                                                                              pymongo.DESCENDING)
        for record in readiness_cursor:
            daily_readiness.report_date_time = record["date_time"]
            daily_readiness.sleep_quality = record["sleep_quality"]
            daily_readiness.readiness = record["readiness"]
            for soreness in record["soreness"]:
                daily_soreness = soreness_and_injury.DailySoreness()
                daily_soreness.body_part = soreness["body_part"]
                daily_soreness.severity = soreness["severity"]
                daily_readiness.soreness.append(daily_soreness)

        return daily_readiness

    def get_last_post_session_survey(self):

        post_session_survey = soreness_and_injury.PostSessionSoreness()

        return post_session_survey

    def get_athlete_injury_history(self):

        injury_history = []

        return injury_history

    def get_athlete_current_training_cycle(self):

        training_cycle = training.TrainingCycle()

        return training_cycle

    def get_scheduled_sessions(self, date):

        scheduled_sessions = []

        # TODO convert from day of week to actual date, add UUID

        return scheduled_sessions

    def get_completed_exercises(self):

        completed_exercises = []

        return completed_exercises

    def get_recovery_bson(self, recovery_session):
        exercise_bson = ()
        for recovery_exercise in recovery_session.recommended_exercises():
            exercise_bson += ({'name': recovery_exercise.exercise.name,
                               'repsAssigned': recovery_exercise.reps_assigned,
                               'setsAssigned': recovery_exercise.sets_assigned,
                               'secondsDuration': recovery_exercise.duration()
                               },)
        recovery_bson = ({'minutesDuration': recovery_session.duration_minutes,
                          'startTime': str(recovery_session.start_time),
                          'endTime': str(recovery_session.end_time),
                          'exercises': exercise_bson
                          })

        return  recovery_bson

    def write_daily_plan(self, daily_plan):

        db = self.mongo_client.movementStats

        collection = db.dailyPlan

        practice_session_bson = ()
        am_recovery_bson = ()
        pm_recovery_bson = ()

        if daily_plan.recovery_am is not None:
            am_recovery_bson = self.get_recovery_bson(daily_plan.recovery_am)

        if daily_plan.recovery_pm is not None:
            pm_recovery_bson = self.get_recovery_bson(daily_plan.recovery_pm)

        for practice_session in daily_plan.practice_sessions:
            practice_session_bson += ({'sessionId': str(practice_session.id),
                                       'postSessionSurvey': practice_session.post_session_survey
                                       },)

        collection.insert_one({'userId': self.athlete_id,
                               'date': daily_plan.date.strftime('%Y-%m-%d'),
                               'practiceSessions': practice_session_bson,
                               'recoveryAM': am_recovery_bson,
                               'recoveryPM': pm_recovery_bson,
                               'lastUpdated': daily_plan.last_updated})
