from models.daily_plan import DailyPlan


class DailyPlanDatastore(object):
    mongo_collection = 'dailyplan'

    def __init__(self):
        self.daily_plans = []

    def side_load_plans(self, daily_plans):
        self.daily_plans = daily_plans

    def get(self, user_id=None, start_date=None, end_date=None):
        return self._query_mongodb(user_id, start_date, end_date)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, user_id, start_date, end_date):
        return self.daily_plans

    def _put_mongodb(self, item):

        practice_session_bson = ()
        cross_training_session_bson = ()
        game_session_bson = ()
        bump_up_session_bson = ()
        am_recovery_bson = ()
        pm_recovery_bson = ()

        if item.recovery_am is not None:
            am_recovery_bson = self.get_recovery_bson(item.recovery_am)

        if item.recovery_pm is not None:
            pm_recovery_bson = self.get_recovery_bson(item.recovery_pm)

        for practice_session in item.practice_sessions:
            practice_session_bson += ({'session_id': str(practice_session.id),
                                       'post_session_survey': practice_session.post_session_survey
                                       },)

        for cross_training_session in item.strength_conditioning_sessions:
            cross_training_session_bson += ({'session_id': str(cross_training_session.id),
                                             'post_session_survey': cross_training_session.post_session_survey
                                             },)

        for game_session in item.games:
            game_session_bson += ({'session_id': str(game_session.id),
                                   'post_session_survey': game_session.post_session_survey
                                   },)

        for bump_up_session in item.bump_up_sessions:
            bump_up_session_bson += ({'session_id': str(bump_up_session.id),
                                      'post_session_survey': bump_up_session.post_session_survey
                                      },)

        insert_bson = ({'user_id': item.athlete_id,
                        'date': item.date.strftime('%Y-%m-%d'),
                        'practice_sessions': practice_session_bson,
                        'bump_up_sessions': bump_up_session_bson,
                        'cross_training_sessions': cross_training_session_bson,
                        'game_sessions': game_session_bson,
                        'recovery_am': am_recovery_bson,
                        'recovery_pm': pm_recovery_bson,
                        'last_updated': item.last_updated})

    def get_recovery_bson(self, recovery_session):
        exercise_bson = ()
        for recovery_exercise in recovery_session.recommended_exercises():
            exercise_bson += ({'name': recovery_exercise.exercise.name,
                               'position_order': recovery_exercise.position_order,
                               'reps_assigned': recovery_exercise.reps_assigned,
                               'sets_assigned': recovery_exercise.sets_assigned,
                               'seconds_duration': recovery_exercise.duration()
                               },)
        recovery_bson = ({'minutes_duration': recovery_session.duration_minutes,
                          'start_time': str(recovery_session.start_time),
                          'end_time': str(recovery_session.end_time),
                          'impact_score': recovery_session.impact_score,
                          'exercises': exercise_bson
                          })

        return recovery_bson
