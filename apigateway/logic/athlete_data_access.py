import soreness_and_injury
import training
import session


class AthleteDataAccess(object):


    def get_last_daily_readiness_survey(self, athlete_id):

        daily_readiness = soreness_and_injury.DailyReadinessSurvey()

        return daily_readiness

    def get_athlete_injury_history(self, athlete_id):

        injury_history = []

        return injury_history

    def get_athlete_current_training_cycle(self, athlete_id):

        training_cycle = training.TrainingCycle()

        return training_cycle

    def get_scheduled_sessions(self, athlete_id, date):

        scheduled_sessions = []

        return scheduled_sessions