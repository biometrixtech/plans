import models.sport as sport
from models.session import FunctionalStrengthSession
from models.exercise import AssignedExercise, UnitOfMeasure


class FSProgramGenerator(object):

    def __init__(self, exercise_library_datastore):
        self.exercise_library_datastore = exercise_library_datastore
        self.exercise_library = self.exercise_library_datastore.get()

    def populate_exercises(self, session):

        session.warm_up = self.assign_exercises(session.warm_up)
        session.duration_minutes += self.calculate_exercise_length(session.warm_up)

        session.dynamic_movement = self.assign_exercises(session.dynamic_movement)
        session.duration_minutes += self.calculate_exercise_length(session.dynamic_movement)

        session.stability_work = self.assign_exercises(session.stability_work)
        session.duration_minutes += self.calculate_exercise_length(session.stability_work)

        session.victory_lap = self.assign_exercises(session.victory_lap)
        session.duration_minutes += self.calculate_exercise_length(session.victory_lap)

        return session

    def calculate_exercise_length(self, exercise_list):

        minutes = 0

        for ex in exercise_list:
            total = 0
            if ex.exercise.unit_of_measure == 'seconds':
                total = ex.exercise.seconds_per_set * ex.sets_assigned
            elif ex.exercise.unit_of_measure == 'count':
                total = ex.exercise.seconds_per_rep * ex.reps_assigned
            elif ex.exercise.unit_of_measure == 'yards':
                total = ex.exercise.seconds_per_set * ex.sets_assigned
            if ex.exercise.bilateral:
                total = total * 2
            minutes += total / 60

        return minutes

    def assign_exercises(self, exercise_list):

        for ex in range(0, len(exercise_list) - 1):
            mapped_exercises = [x for x in self.exercise_library if x.id == exercise_list[ex].exercise.id]
            exercise_list[ex].exercise = mapped_exercises[0]
            exercise_list[ex].reps_assigned = mapped_exercises[0].max_reps
            exercise_list[ex].sets_assigned = mapped_exercises[0].max_sets

        minutes = self.calculate_exercise_length(exercise_list)

        return exercise_list

    def getFunctionalStrengthForSportPosition(self, sport_name, position=None):

        session = FunctionalStrengthSession()
        session.sport_name = sport_name
        session.position = position

        if sport_name is None and position is None:
            return session

        if sport_name is None:
            if position == sport.NoSportPosition.Power or position == sport.NoSportPosition.Strength:

                session.warm_up.append(AssignedExercise("139", 1, 1))
                session.warm_up.append(AssignedExercise("140", 1, 2))
                session.warm_up.append(AssignedExercise("141", 1, 3))
                session.warm_up.append(AssignedExercise("142", 1, 4))
                session.warm_up.append(AssignedExercise("143", 1, 5))
                session.warm_up.append(AssignedExercise("144", 1, 6))
                session.dynamic_movement.append(AssignedExercise("145", 2, 1))
                session.dynamic_movement.append(AssignedExercise("146", 2, 2))
                session.dynamic_movement.append(AssignedExercise("147", 2, 3))
                session.dynamic_movement.append(AssignedExercise("148", 2, 4))
                session.dynamic_movement.append(AssignedExercise("149", 2, 5))
                session.dynamic_movement.append(AssignedExercise("150", 2, 6))
                session.dynamic_movement.append(AssignedExercise("151", 2, 7))
                session.stability_work.append(AssignedExercise("152", 3, 1))
                session.stability_work.append(AssignedExercise("153", 3, 2))
                session.stability_work.append(AssignedExercise("154", 3, 3))
                session.stability_work.append(AssignedExercise("155", 3, 4))
                session.victory_lap.append(AssignedExercise("156", 4, 1))
                session.victory_lap.append(AssignedExercise("157", 4, 2))
                session.victory_lap.append(AssignedExercise("158", 4, 3))
                session.victory_lap.append(AssignedExercise("159", 4, 4))
                session.victory_lap.append(AssignedExercise("160", 4, 5))

            elif (position == sport.NoSportPosition.Endurance or
                  position == sport.NoSportPosition.Speed or
                  position == sport.NoSportPosition.CrossTraining):

                session.warm_up.append(AssignedExercise("161", 1, 1))
                session.warm_up.append(AssignedExercise("162", 1, 2))
                session.warm_up.append(AssignedExercise("163", 1, 3))
                session.warm_up.append(AssignedExercise("164", 1, 4))
                session.warm_up.append(AssignedExercise("165", 1, 5))

                session.dynamic_movement.append(AssignedExercise("166", 2, 1))
                session.dynamic_movement.append(AssignedExercise("151", 2, 2))
                session.dynamic_movement.append(AssignedExercise("149", 2, 3))
                session.dynamic_movement.append(AssignedExercise("146", 2, 4))
                session.dynamic_movement.append(AssignedExercise("148", 2, 5))

                session.stability_work.append(AssignedExercise("168", 3, 1))
                session.stability_work.append(AssignedExercise("169", 3, 2))
                session.stability_work.append(AssignedExercise("170", 3, 3))
                session.stability_work.append(AssignedExercise("152", 3, 4))
                session.stability_work.append(AssignedExercise("171", 3, 5))

                session.victory_lap.append(AssignedExercise("157", 4, 1))
                session.victory_lap.append(AssignedExercise("172", 4, 2))
                session.victory_lap.append(AssignedExercise("173", 4, 3))
                session.victory_lap.append(AssignedExercise("174", 4, 4))

        if sport_name == sport.SportName.baseball_softball:

            session.warm_up.append(AssignedExercise("161", 1, 1))
            session.warm_up.append(AssignedExercise("162", 1, 2))
            session.warm_up.append(AssignedExercise("163", 1, 3))
            session.warm_up.append(AssignedExercise("164", 1, 4))
            session.warm_up.append(AssignedExercise("165", 1, 5))

            session.dynamic_movement.append(AssignedExercise("166", 2, 1))
            session.dynamic_movement.append(AssignedExercise("151", 2, 2))
            session.dynamic_movement.append(AssignedExercise("149", 2, 3))
            session.dynamic_movement.append(AssignedExercise("146", 2, 4))
            session.dynamic_movement.append(AssignedExercise("148", 2, 5))

            session.stability_work.append(AssignedExercise("168", 3, 1))
            session.stability_work.append(AssignedExercise("169", 3, 2))
            session.stability_work.append(AssignedExercise("170", 3, 3))
            session.stability_work.append(AssignedExercise("152", 3, 4))
            session.stability_work.append(AssignedExercise("171", 3, 5))

            session.victory_lap.append(AssignedExercise("157", 4, 1))
            session.victory_lap.append(AssignedExercise("172", 4, 2))
            session.victory_lap.append(AssignedExercise("173", 4, 3))
            session.victory_lap.append(AssignedExercise("174", 4, 4))

        if sport_name == sport.SportName.basketball:
            if position is not None and position == sport.BasketballPosition.Center:

                session.warm_up.append(AssignedExercise("139", 1, 1))
                session.warm_up.append(AssignedExercise("140", 1, 2))
                session.warm_up.append(AssignedExercise("141", 1, 3))
                session.warm_up.append(AssignedExercise("142", 1, 4))
                session.warm_up.append(AssignedExercise("143", 1, 5))
                session.warm_up.append(AssignedExercise("144", 1, 6))
                session.dynamic_movement.append(AssignedExercise("145", 2, 1))
                session.dynamic_movement.append(AssignedExercise("146", 2, 2))
                session.dynamic_movement.append(AssignedExercise("147", 2, 3))
                session.dynamic_movement.append(AssignedExercise("148", 2, 4))
                session.dynamic_movement.append(AssignedExercise("149", 2, 5))
                session.dynamic_movement.append(AssignedExercise("150", 2, 6))
                session.dynamic_movement.append(AssignedExercise("151", 2, 7))
                session.stability_work.append(AssignedExercise("152", 3, 1))
                session.stability_work.append(AssignedExercise("153", 3, 2))
                session.stability_work.append(AssignedExercise("154", 3, 3))
                session.stability_work.append(AssignedExercise("155", 3, 4))
                session.victory_lap.append(AssignedExercise("156", 4, 1))
                session.victory_lap.append(AssignedExercise("157", 4, 2))
                session.victory_lap.append(AssignedExercise("158", 4, 3))
                session.victory_lap.append(AssignedExercise("159", 4, 4))
                session.victory_lap.append(AssignedExercise("160", 4, 5))

            elif (position is not None and
                  (position == sport.BasketballPosition.Forward or
                   position == sport.BasketballPosition.Guard)):

                session.warm_up.append(AssignedExercise("161", 1, 1))
                session.warm_up.append(AssignedExercise("162", 1, 2))
                session.warm_up.append(AssignedExercise("163", 1, 3))
                session.warm_up.append(AssignedExercise("164", 1, 4))
                session.warm_up.append(AssignedExercise("165", 1, 5))

                session.dynamic_movement.append(AssignedExercise("166", 2, 1))
                session.dynamic_movement.append(AssignedExercise("151", 2, 2))
                session.dynamic_movement.append(AssignedExercise("149", 2, 3))
                session.dynamic_movement.append(AssignedExercise("146", 2, 4))
                session.dynamic_movement.append(AssignedExercise("148", 2, 5))

                session.stability_work.append(AssignedExercise("168", 3, 1))
                session.stability_work.append(AssignedExercise("169", 3, 2))
                session.stability_work.append(AssignedExercise("170", 3, 3))
                session.stability_work.append(AssignedExercise("152", 3, 4))
                session.stability_work.append(AssignedExercise("171", 3, 5))

                session.victory_lap.append(AssignedExercise("157", 4, 1))
                session.victory_lap.append(AssignedExercise("172", 4, 2))
                session.victory_lap.append(AssignedExercise("173", 4, 3))
                session.victory_lap.append(AssignedExercise("174", 4, 4))

        if sport_name == sport.SportName.football:
            if (position is not None and (position == sport.FootballPosition.Kicker or
                                          position == sport.FootballPosition.Lineman or
                                          position == sport.FootballPosition.Linebacker or
                                          position == sport.FootballPosition.DefensiveBack)):

                session.warm_up.append(AssignedExercise("139", 1, 1))
                session.warm_up.append(AssignedExercise("140", 1, 2))
                session.warm_up.append(AssignedExercise("141", 1, 3))
                session.warm_up.append(AssignedExercise("142", 1, 4))
                session.warm_up.append(AssignedExercise("143", 1, 5))
                session.warm_up.append(AssignedExercise("144", 1, 6))
                session.dynamic_movement.append(AssignedExercise("145", 2, 1))
                session.dynamic_movement.append(AssignedExercise("146", 2, 2))
                session.dynamic_movement.append(AssignedExercise("147", 2, 3))
                session.dynamic_movement.append(AssignedExercise("148", 2, 4))
                session.dynamic_movement.append(AssignedExercise("149", 2, 5))
                session.dynamic_movement.append(AssignedExercise("150", 2, 6))
                session.dynamic_movement.append(AssignedExercise("151", 2, 7))
                session.stability_work.append(AssignedExercise("152", 3, 1))
                session.stability_work.append(AssignedExercise("153", 3, 2))
                session.stability_work.append(AssignedExercise("154", 3, 3))
                session.stability_work.append(AssignedExercise("155", 3, 4))
                session.victory_lap.append(AssignedExercise("156", 4, 1))
                session.victory_lap.append(AssignedExercise("157", 4, 2))
                session.victory_lap.append(AssignedExercise("158", 4, 3))
                session.victory_lap.append(AssignedExercise("159", 4, 4))
                session.victory_lap.append(AssignedExercise("160", 4, 5))

            elif (position is not None and
                  (position == sport.FootballPosition.Quarterback or
                   position == sport.FootballPosition.Receiver or
                   position == sport.FootballPosition.RunningBack)):

                session.warm_up.append(AssignedExercise("161", 1, 1))
                session.warm_up.append(AssignedExercise("162", 1, 2))
                session.warm_up.append(AssignedExercise("163", 1, 3))
                session.warm_up.append(AssignedExercise("164", 1, 4))
                session.warm_up.append(AssignedExercise("165", 1, 5))

                session.dynamic_movement.append(AssignedExercise("166", 2, 1))
                session.dynamic_movement.append(AssignedExercise("151", 2, 2))
                session.dynamic_movement.append(AssignedExercise("149", 2, 3))
                session.dynamic_movement.append(AssignedExercise("146", 2, 4))
                session.dynamic_movement.append(AssignedExercise("148", 2, 5))

                session.stability_work.append(AssignedExercise("168", 3, 1))
                session.stability_work.append(AssignedExercise("169", 3, 2))
                session.stability_work.append(AssignedExercise("170", 3, 3))
                session.stability_work.append(AssignedExercise("152", 3, 4))
                session.stability_work.append(AssignedExercise("171", 3, 5))

                session.victory_lap.append(AssignedExercise("157", 4, 1))
                session.victory_lap.append(AssignedExercise("172", 4, 2))
                session.victory_lap.append(AssignedExercise("173", 4, 3))
                session.victory_lap.append(AssignedExercise("174", 4, 4))

        if sport_name == sport.SportName.lacrosse:

            session.warm_up.append(AssignedExercise("161", 1, 1))
            session.warm_up.append(AssignedExercise("162", 1, 2))
            session.warm_up.append(AssignedExercise("163", 1, 3))
            session.warm_up.append(AssignedExercise("164", 1, 4))
            session.warm_up.append(AssignedExercise("165", 1, 5))

            session.dynamic_movement.append(AssignedExercise("166", 2, 1))
            session.dynamic_movement.append(AssignedExercise("151", 2, 2))
            session.dynamic_movement.append(AssignedExercise("149", 2, 3))
            session.dynamic_movement.append(AssignedExercise("146", 2, 4))
            session.dynamic_movement.append(AssignedExercise("148", 2, 5))

            session.stability_work.append(AssignedExercise("168", 3, 1))
            session.stability_work.append(AssignedExercise("169", 3, 2))
            session.stability_work.append(AssignedExercise("170", 3, 3))
            session.stability_work.append(AssignedExercise("152", 3, 4))
            session.stability_work.append(AssignedExercise("171", 3, 5))

            session.victory_lap.append(AssignedExercise("157", 4, 1))
            session.victory_lap.append(AssignedExercise("172", 4, 2))
            session.victory_lap.append(AssignedExercise("173", 4, 3))
            session.victory_lap.append(AssignedExercise("174", 4, 4))

        if sport_name == sport.SportName.soccer:
            if (position is not None and
                    (position == sport.SoccerPosition.Forward or
                     position == sport.SoccerPosition.Midfielder or
                     position == sport.SoccerPosition.Defender)):

                session.warm_up.append(AssignedExercise("139", 1, 1))
                session.warm_up.append(AssignedExercise("140", 1, 2))
                session.warm_up.append(AssignedExercise("141", 1, 3))
                session.warm_up.append(AssignedExercise("142", 1, 4))
                session.warm_up.append(AssignedExercise("143", 1, 5))
                session.warm_up.append(AssignedExercise("144", 1, 6))
                session.dynamic_movement.append(AssignedExercise("145", 2, 1))
                session.dynamic_movement.append(AssignedExercise("146", 2, 2))
                session.dynamic_movement.append(AssignedExercise("147", 2, 3))
                session.dynamic_movement.append(AssignedExercise("148", 2, 4))
                session.dynamic_movement.append(AssignedExercise("149", 2, 5))
                session.dynamic_movement.append(AssignedExercise("150", 2, 6))
                session.dynamic_movement.append(AssignedExercise("151", 2, 7))
                session.stability_work.append(AssignedExercise("152", 3, 1))
                session.stability_work.append(AssignedExercise("153", 3, 2))
                session.stability_work.append(AssignedExercise("154", 3, 3))
                session.stability_work.append(AssignedExercise("155", 3, 4))
                session.victory_lap.append(AssignedExercise("156", 4, 1))
                session.victory_lap.append(AssignedExercise("157", 4, 2))
                session.victory_lap.append(AssignedExercise("158", 4, 3))
                session.victory_lap.append(AssignedExercise("159", 4, 4))
                session.victory_lap.append(AssignedExercise("160", 4, 5))

            elif (position is not None and
                  (position == sport.SoccerPosition.Goalkeeper or
                   position == sport.SoccerPosition.Striker)):

                session.warm_up.append(AssignedExercise("161", 1, 1))
                session.warm_up.append(AssignedExercise("162", 1, 2))
                session.warm_up.append(AssignedExercise("163", 1, 3))
                session.warm_up.append(AssignedExercise("164", 1, 4))
                session.warm_up.append(AssignedExercise("165", 1, 5))

                session.dynamic_movement.append(AssignedExercise("166", 2, 1))
                session.dynamic_movement.append(AssignedExercise("151", 2, 2))
                session.dynamic_movement.append(AssignedExercise("149", 2, 3))
                session.dynamic_movement.append(AssignedExercise("146", 2, 4))
                session.dynamic_movement.append(AssignedExercise("148", 2, 5))

                session.stability_work.append(AssignedExercise("168", 3, 1))
                session.stability_work.append(AssignedExercise("169", 3, 2))
                session.stability_work.append(AssignedExercise("170", 3, 3))
                session.stability_work.append(AssignedExercise("152", 3, 4))
                session.stability_work.append(AssignedExercise("171", 3, 5))

                session.victory_lap.append(AssignedExercise("157", 4, 1))
                session.victory_lap.append(AssignedExercise("172", 4, 2))
                session.victory_lap.append(AssignedExercise("173", 4, 3))
                session.victory_lap.append(AssignedExercise("174", 4, 4))

        if sport_name == sport.SportName.running or sport_name == sport.SportName.tennis:

            session.warm_up.append(AssignedExercise("139", 1, 1))
            session.warm_up.append(AssignedExercise("140", 1, 2))
            session.warm_up.append(AssignedExercise("141", 1, 3))
            session.warm_up.append(AssignedExercise("142", 1, 4))
            session.warm_up.append(AssignedExercise("143", 1, 5))
            session.warm_up.append(AssignedExercise("144", 1, 6))
            session.dynamic_movement.append(AssignedExercise("145", 2, 1))
            session.dynamic_movement.append(AssignedExercise("146", 2, 2))
            session.dynamic_movement.append(AssignedExercise("147", 2, 3))
            session.dynamic_movement.append(AssignedExercise("148", 2, 4))
            session.dynamic_movement.append(AssignedExercise("149", 2, 5))
            session.dynamic_movement.append(AssignedExercise("150", 2, 6))
            session.dynamic_movement.append(AssignedExercise("151", 2, 7))
            session.stability_work.append(AssignedExercise("152", 3, 1))
            session.stability_work.append(AssignedExercise("153", 3, 2))
            session.stability_work.append(AssignedExercise("154", 3, 3))
            session.stability_work.append(AssignedExercise("155", 3, 4))
            session.victory_lap.append(AssignedExercise("156", 4, 1))
            session.victory_lap.append(AssignedExercise("157", 4, 2))
            session.victory_lap.append(AssignedExercise("158", 4, 3))
            session.victory_lap.append(AssignedExercise("159", 4, 4))
            session.victory_lap.append(AssignedExercise("160", 4, 5))

        return self.populate_exercises(session)
