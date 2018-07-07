import soreness_and_injury
import training
import session


class AthleteDataAccess(object):


    def __init__(self, athlete_id):
        self.athlete_id = athlete_id


    def get_last_daily_readiness_survey(self):

        daily_readiness = soreness_and_injury.DailyReadinessSurvey()

        return daily_readiness

    def get_athlete_injury_history(self):

        injury_history = []

        return injury_history

    def get_athlete_current_training_cycle(self):

        training_cycle = training.TrainingCycle()

        return training_cycle

    def get_scheduled_sessions(self, date):

        scheduled_sessions = []

        return scheduled_sessions

    def get_completed_exercises(self):

        completed_exercises = []

        return completed_exercises