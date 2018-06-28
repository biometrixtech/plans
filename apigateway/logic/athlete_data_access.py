import soreness_and_injury
import datetime
import training

class AtheleteDataAccess(object):

    def get_athlete_injury_history(self, athlete_id):

        injury_history = []

        injury1 = soreness_and_injury.Injury()
        injury1.body_part = soreness_and_injury.BodyPart.ankle
        injury1.injury_type = soreness_and_injury.InjuryType.ligament
        injury1.injury_descriptor = soreness_and_injury.InjuryDescriptor.sprain
        injury1.date = datetime.date(2017, 10, 1)
        injury1.days_missed = soreness_and_injury.DaysMissedDueToInjury.less_than_7_days

        injury2 = soreness_and_injury.Injury()
        injury2.body_part = soreness_and_injury.BodyPart.ankle
        injury2.injury_type = soreness_and_injury.InjuryType.ligament
        injury2.injury_descriptor = soreness_and_injury.InjuryDescriptor.sprain
        injury2.date = datetime.date(2018, 3, 1)
        injury2.days_missed = soreness_and_injury.DaysMissedDueToInjury.less_than_7_days

        injury_history.append(injury1)
        injury_history.append(injury2)

        return injury_history

    def get_athlete_current_training_cycle(self, athlete_id):

        training_cycle = training.TrainingCycle()

        return training_cycle