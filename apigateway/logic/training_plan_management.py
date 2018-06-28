import training
import schedule
import session


class TrainingPlanManager(object):

    def create_training_cycle(self, athlete_id):
        schedule_manager = schedule.ScheduleManager()
        athlete_schedule = schedule_manager.get_typical_schedule(athlete_id)
        training_cycle = training.TrainingCycle()
        # TODO set start and end dates of training_cycle
        for s in athlete_schedule.sessions:
            new_session = s.create()
            training_cycle.sessions.extend(new_session)

    def recalculate_current_training_cycle(self):

        calc = training.Calculator()

        training_cycle = self.training_cycles[0]

        # update expected load, etc for the week
        self.impute_load()

        # add any training modifications?

        # do we need to add, change or delete long-term recovery modalities?
        # if fatiguing, certainly need to add certain modalities
        if self.is_athlete_fatiguing():
            j = 0

        # do we need to add, change or delete corrective exercises?

        # do we need to add, change or delete bump-up sessions?

        load_gap = self.current_load_gap()
        if load_gap.exists():

            # TODO: what if the user has already seleceted exercises for a bump-up session?  should we preserve?
            bump_up_sessions = calc.get_bump_up_sessions(self.training_cycles, load_gap)

            # ^ do we need to replace existing? add to the list or blow out all estimated and redo?

