import pymongo
# import database_config
import datetime
import logic.training as training
import logic.session as session
import config
import logic.soreness_and_injury as soreness_and_injury
import uuid

class AthleteDataAccess(object):

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id

    def get_last_daily_readiness_survey(self):

        daily_readiness = soreness_and_injury.DailyReadinessSurvey()

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

        collection = config.get_mongo_collection('training')
        schedule_cursor = collection.find({"user_id": self.athlete_id})
        day_of_week = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()

        for schedule in schedule_cursor:

            cross_training = schedule["cross_training"]
            cross_training_days_of_week = cross_training["days_of_week"]
            if cross_training_days_of_week is not None and len(cross_training_days_of_week) > 0:
                if day_of_week in cross_training_days_of_week:
                    cross_training_session = session.StrengthConditioningSession()
                    cross_training_session.day_of_week = session.DayOfWeek(day_of_week)
                    cross_training_session.date = date
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
                        practice_session.date = date
                        practice_session.id = uuid.uuid4()
                        practice_session.duration_minutes = practice["duration"]
                        practice_session.description = "Practice (" + sport["sport"] + ")"
                        scheduled_sessions.append(practice_session)
                competition_days_of_week = competition["days_of_week"]
                if competition_days_of_week is not None and len(competition_days_of_week) > 0:
                    if day_of_week in competition_days_of_week:
                        game_session = session.Game()
                        game_session.day_of_week = session.DayOfWeek(day_of_week)
                        game_session.date = date
                        game_session.id = uuid.uuid4()
                        game_session.duration_minutes = 0   # TODO: look up from internal data
                        game_session.description = "Competition (" + sport["sport"] + ")"
                        scheduled_sessions.append(game_session)

        return scheduled_sessions

    def get_completed_exercises(self):

        completed_exercises = []

        return completed_exercises
'''moved to athlete_datastore
    def get_recovery_bson(self, recovery_session):
        exercise_bson = ()
        for recovery_exercise in recovery_session.recommended_exercises():
            exercise_bson += ({'name': recovery_exercise.exercise.name,
                               'reps_assigned': recovery_exercise.reps_assigned,
                               'sets_assigned': recovery_exercise.sets_assigned,
                               'seconds_duration': recovery_exercise.duration()
                               },)
        recovery_bson = ({'minutes_duration': recovery_session.duration_minutes,
                          'start_time': str(recovery_session.start_time),
                          'end_time': str(recovery_session.end_time),
                          'exercises': exercise_bson
                          })

        return  recovery_bson

    def write_daily_plan(self, daily_plan):

        # db = self.mongo_client.movementStats

        # collection = db.dailyPlan
        collection = config.get_mongo_collection('dailyplan')

        practice_session_bson = ()
        cross_training_session_bson = ()
        game_session_bson = ()
        bump_up_session_bson = ()
        am_recovery_bson = ()
        pm_recovery_bson = ()

        if daily_plan.recovery_am is not None:
            am_recovery_bson = self.get_recovery_bson(daily_plan.recovery_am)

        if daily_plan.recovery_pm is not None:
            pm_recovery_bson = self.get_recovery_bson(daily_plan.recovery_pm)

        for practice_session in daily_plan.practice_sessions:
            practice_session_bson += ({'session_id': str(practice_session.id),
                                       'post_session_survey': practice_session.post_session_survey
                                       },)

        for cross_training_session in daily_plan.strength_conditioning_sessions:
            cross_training_session_bson += ({'session_id': str(cross_training_session.id),
                                            'post_session_survey': cross_training_session.post_session_survey
                                            },)

        for game_session in daily_plan.games:
            game_session_bson += ({'session_id': str(game_session.id),
                                   'post_session_survey': game_session.post_session_survey
                                   },)

        for bump_up_session in daily_plan.bump_up_sessions:
            bump_up_session_bson += ({'session_id': str(bump_up_session.id),
                                     'post_session_survey': bump_up_session.post_session_survey
                                     },)

        collection.insert_one({'user_id': self.athlete_id,
                               'date': daily_plan.date.strftime('%Y-%m-%d'),
                               'practice_sessions': practice_session_bson,
                               'bump_up_sessions': bump_up_session_bson,
                               'cross_training_sessions': cross_training_session_bson,
                               'game_sessions': game_session_bson,
                               'recovery_am': am_recovery_bson,
                               'recovery_pm': pm_recovery_bson,
                               'last_updated': daily_plan.last_updated})
'''
