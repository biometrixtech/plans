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
            if ex.exercise.unit_of_measure.name == 'seconds':
                total = ex.exercise.seconds_per_set * ex.sets_assigned
            elif ex.exercise.unit_of_measure.name == 'count':
                total = ex.exercise.seconds_per_rep * ex.reps_assigned
            elif ex.exercise.unit_of_measure.name == 'yards':
                total = ex.exercise.seconds_per_set * ex.sets_assigned
            if ex.exercise.bilateral:
                total = total * 2
            minutes += total / 60

        return minutes

    def assign_exercises(self, exercise_list):

        for ex in range(0, len(exercise_list)):
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

        if sport_name.value is None and position is None:
            return session

        if sport_name.value is None:
            if position == sport.NoSportPosition.strength:

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

            elif position == sport.NoSportPosition.cross_training:

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

            elif position == sport.NoSportPosition.endurance:

                session.warm_up.append(AssignedExercise("176", 1, 1))
                session.warm_up.append(AssignedExercise("139", 1, 2))
                session.warm_up.append(AssignedExercise("161", 1, 3))
                session.warm_up.append(AssignedExercise("193", 1, 4))
                session.warm_up.append(AssignedExercise("144", 1, 5))

                session.dynamic_movement.append(AssignedExercise("151", 2, 1))
                session.dynamic_movement.append(AssignedExercise("147", 2, 2))
                session.dynamic_movement.append(AssignedExercise("149", 2, 3))
                session.dynamic_movement.append(AssignedExercise("145", 2, 4))
                session.dynamic_movement.append(AssignedExercise("194", 2, 5))
                session.dynamic_movement.append(AssignedExercise("184", 2, 6))

                session.stability_work.append(AssignedExercise("185", 3, 1))
                session.stability_work.append(AssignedExercise("195", 3, 2))
                session.stability_work.append(AssignedExercise("196", 3, 3))
                session.stability_work.append(AssignedExercise("197", 3, 4))
                session.stability_work.append(AssignedExercise("198", 3, 5))

                session.victory_lap.append(AssignedExercise("199", 4, 1))
                session.victory_lap.append(AssignedExercise("200", 4, 2))
                session.victory_lap.append(AssignedExercise("201", 4, 3))
                session.victory_lap.append(AssignedExercise("202", 4, 4))

            elif (position == sport.NoSportPosition.speed or
                  position == sport.NoSportPosition.power):

                session.warm_up.append(AssignedExercise("176", 1, 1))
                session.warm_up.append(AssignedExercise("139", 1, 2))
                session.warm_up.append(AssignedExercise("163", 1, 3))
                session.warm_up.append(AssignedExercise("164", 1, 4))
                session.warm_up.append(AssignedExercise("177", 1, 5))

                session.dynamic_movement.append(AssignedExercise("203", 2, 1))
                session.dynamic_movement.append(AssignedExercise("204", 2, 2))
                session.dynamic_movement.append(AssignedExercise("205", 2, 3))
                session.dynamic_movement.append(AssignedExercise("206", 2, 4))
                session.dynamic_movement.append(AssignedExercise("207", 2, 5))

                session.stability_work.append(AssignedExercise("208", 3, 1))
                session.stability_work.append(AssignedExercise("209", 3, 2))
                session.stability_work.append(AssignedExercise("210", 3, 3))
                session.stability_work.append(AssignedExercise("211", 3, 4))

                session.victory_lap.append(AssignedExercise("212", 4, 1))
                session.victory_lap.append(AssignedExercise("159", 4, 2))
                session.victory_lap.append(AssignedExercise("213", 4, 3))

        if sport_name == sport.SportName.running:
            if position == sport.RunnningPosition.long_distance:

                session.warm_up.append(AssignedExercise("176", 1, 1))
                session.warm_up.append(AssignedExercise("139", 1, 2))
                session.warm_up.append(AssignedExercise("161", 1, 3))
                session.warm_up.append(AssignedExercise("193", 1, 4))
                session.warm_up.append(AssignedExercise("144", 1, 5))

                session.dynamic_movement.append(AssignedExercise("151", 2, 1))
                session.dynamic_movement.append(AssignedExercise("147", 2, 2))
                session.dynamic_movement.append(AssignedExercise("149", 2, 3))
                session.dynamic_movement.append(AssignedExercise("145", 2, 4))
                session.dynamic_movement.append(AssignedExercise("194", 2, 5))
                session.dynamic_movement.append(AssignedExercise("184", 2, 6))

                session.stability_work.append(AssignedExercise("185", 3, 1))
                session.stability_work.append(AssignedExercise("195", 3, 2))
                session.stability_work.append(AssignedExercise("196", 3, 3))
                session.stability_work.append(AssignedExercise("197", 3, 4))
                session.stability_work.append(AssignedExercise("198", 3, 5))

                session.victory_lap.append(AssignedExercise("199", 4, 1))
                session.victory_lap.append(AssignedExercise("200", 4, 2))
                session.victory_lap.append(AssignedExercise("201", 4, 3))
                session.victory_lap.append(AssignedExercise("202", 4, 4))

            elif position == sport.RunningPosition.sprinter:

                session.warm_up.append(AssignedExercise("176", 1, 1))
                session.warm_up.append(AssignedExercise("139", 1, 2))
                session.warm_up.append(AssignedExercise("163", 1, 3))
                session.warm_up.append(AssignedExercise("164", 1, 4))
                session.warm_up.append(AssignedExercise("177", 1, 5))

                session.dynamic_movement.append(AssignedExercise("203", 2, 1))
                session.dynamic_movement.append(AssignedExercise("204", 2, 2))
                session.dynamic_movement.append(AssignedExercise("205", 2, 3))
                session.dynamic_movement.append(AssignedExercise("206", 2, 4))
                session.dynamic_movement.append(AssignedExercise("207", 2, 5))

                session.stability_work.append(AssignedExercise("208", 3, 1))
                session.stability_work.append(AssignedExercise("209", 3, 2))
                session.stability_work.append(AssignedExercise("210", 3, 3))
                session.stability_work.append(AssignedExercise("211", 3, 4))

                session.victory_lap.append(AssignedExercise("212", 4, 1))
                session.victory_lap.append(AssignedExercise("159", 4, 2))
                session.victory_lap.append(AssignedExercise("213", 4, 3))

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
            # position doesn't matter

            session.warm_up.append(AssignedExercise("175", 1, 1))
            session.warm_up.append(AssignedExercise("176", 1, 2))
            session.warm_up.append(AssignedExercise("177", 1, 3))
            session.warm_up.append(AssignedExercise("178", 1, 4))
            session.warm_up.append(AssignedExercise("179", 1, 5))
            session.warm_up.append(AssignedExercise("162", 1, 6))
            session.warm_up.append(AssignedExercise("180", 1, 7))
            session.warm_up.append(AssignedExercise("181", 1, 8))
            session.dynamic_movement.append(AssignedExercise("151", 2, 1))
            session.dynamic_movement.append(AssignedExercise("149", 2, 2))
            session.dynamic_movement.append(AssignedExercise("145", 2, 3))
            session.dynamic_movement.append(AssignedExercise("182", 2, 4))
            session.dynamic_movement.append(AssignedExercise("183", 2, 5))
            session.dynamic_movement.append(AssignedExercise("184", 2, 6))

            session.stability_work.append(AssignedExercise("185", 3, 1))
            session.stability_work.append(AssignedExercise("186", 3, 2))
            session.stability_work.append(AssignedExercise("187", 3, 3))
            session.stability_work.append(AssignedExercise("188", 3, 4))
            session.stability_work.append(AssignedExercise("189", 3, 5))

            session.victory_lap.append(AssignedExercise("190", 4, 1))
            session.victory_lap.append(AssignedExercise("191", 4, 2))
            session.victory_lap.append(AssignedExercise("159", 4, 3))
            session.victory_lap.append(AssignedExercise("192", 4, 4))

        if sport_name == sport.SportName.football:
            if (position is not None and (position == sport.FootballPosition.kicker or
                                          position == sport.FootballPosition.lineman or
                                          position == sport.FootballPosition.linebacker or
                                          position == sport.FootballPosition.defensive_back)):

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
                  (position == sport.FootballPosition.quarterback or
                   position == sport.FootballPosition.receiver or
                   position == sport.FootballPosition.running_back)):

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
                    (position == sport.SoccerPosition.striker or
                     position == sport.SoccerPosition.forward or
                     position == sport.SoccerPosition.midfielder or
                     position == sport.SoccerPosition.defender)):

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
                  (position == sport.SoccerPosition.goalkeeper)):

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

        if sport_name == sport.SportName.tennis:

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
