from serialisable import Serialisable
from models.soreness import BodyPart, BodyPartLocation, AssignedExercise, HistoricSorenessStatus
from models.body_parts import BodyPartFactory
from models.exercise import ExerciseBuckets
from utils import parse_date
import abc


class AthleteGoal(object):
    def __init__(self, text, priority):
        self.text = text
        self.priority = priority
        self.trigger = ''

    def json_serialise(self):
        ret = {
            'text': self.text,
            'priority': self.priority,
            'trigger': self.trigger
        }
        return ret


class Heat(Serialisable):
    def __init__(self, minutes=0, body_part_location=None, side=0):
        self.minutes = minutes
        self.body_part_location = body_part_location
        self.side = side
        self.before_training = True
        self.goals = set()
        self.completed = False
        self.active = True

    def json_serialise(self):

        ret = {
            'minutes': self.minutes,
            'body_part_location': self.body_part_location.value,
            'side': self.side,
            'before_training': self.before_training,
            'goals': [goal.json_serialise() for goal in self.goals],
            'completed': self.completed,
            'active': self.active
        }

        return ret


class ActiveRest(object):
    def __init__(self):
        self.inhibit_exercises = {}
        self.inhibit_minutes = 0
        self.static_integrate_exercises = {}
        self.static_integrate_minutes = 0
        self.static_stretch_exercises = {}
        self.static_stretch_minutes = 0
        self.completed = False
        self.active = True

    @abc.abstractmethod
    def check_reactive_care_soreness(self, soreness, exercise_library):
        pass

    @abc.abstractmethod
    def check_reactive_care_pain(self, soreness, exercise_library):
        pass

    @abc.abstractmethod
    def check_prevention_soreness(self, soreness, event_date_time, exercise_library):
        pass

    @abc.abstractmethod
    def check_prevention_pain(self, soreness, event_date_time, exercise_library):
        pass

    @abc.abstractmethod
    def calc_durations(self):
        pass

    def fill_exercises(self, soreness_list, event_date_time, exercise_library):

        for s in soreness_list:
            self.check_reactive_care_soreness(s, exercise_library)
            self.check_reactive_care_pain(s, exercise_library)
            self.check_prevention_soreness(s, parse_date(event_date_time), exercise_library)
            self.check_prevention_pain(s, parse_date(event_date_time), exercise_library)

    def copy_exercises(self, source_collection, target_collection, goal, priority, soreness, exercise_library):

        for s in source_collection:
            if s.exercise.id not in target_collection:
                target_collection[s.exercise.id] = AssignedExercise(library_id=str(s.exercise.id))
                exercise_list = [ex for ex in exercise_library if ex.id == str(s.exercise.id)]
                target_collection[s.exercise.id].exercise = exercise_list[0]

            target_collection[s.exercise.id] = self.update_dosage(soreness, target_collection[s.exercise.id])
            target_collection[s.exercise.id].goals.add(goal)
            target_collection[s.exercise.id].priorities.add(priority)
            target_collection[s.exercise.id].soreness_sources.add(soreness)

    def update_dosage(self, soreness, assigned_exercise):

        if soreness.severity < 0.5:
            assigned_exercise.complete_reps_assigned = max(assigned_exercise.complete_reps_assigned,
                                                  assigned_exercise.exercise.min_reps)
            assigned_exercise.complete_sets_assigned = max(assigned_exercise.complete_sets_assigned, 1)
        elif 0.5 <= soreness.severity < 1.5:
            assigned_exercise.complete_reps_assigned = max(assigned_exercise.complete_reps_assigned,
                                                  assigned_exercise.exercise.min_reps)
            assigned_exercise.complete_sets_assigned = max(assigned_exercise.complete_sets_assigned, 1)
        elif 1.5 <= soreness.severity < 2.5:
            assigned_exercise.complete_reps_assigned = max(assigned_exercise.complete_reps_assigned,
                                                  assigned_exercise.exercise.max_reps)
            assigned_exercise.complete_sets_assigned = max(assigned_exercise.complete_sets_assigned, 1)
        elif 2.5 <= soreness.severity < 3.5:
            assigned_exercise.complete_reps_assigned = max(assigned_exercise.complete_reps_assigned,
                                                  assigned_exercise.exercise.max_reps)
            assigned_exercise.complete_sets_assigned = max(assigned_exercise.complete_sets_assigned, 1)
        elif 3.5 <= soreness.severity < 4.5:
            assigned_exercise.complete_reps_assigned = max(assigned_exercise.complete_reps_assigned,
                                                  assigned_exercise.exercise.max_reps)
            assigned_exercise.complete_sets_assigned = max(assigned_exercise.complete_sets_assigned, 1)
        elif soreness >= 4.5:
            assigned_exercise.complete_reps_assigned = max(assigned_exercise.complete_reps_assigned,
                                                  assigned_exercise.exercise.max_reps)
            assigned_exercise.complete_sets_assigned = max(assigned_exercise.complete_sets_assigned, 2)

        return assigned_exercise

    def calc_active_time(self, exercise_dictionary):

        active_time = 0

        for id, assigned_excercise in exercise_dictionary.items():
            active_time += assigned_excercise.duration() / 60

        return active_time


class ActiveRestBeforeTraining(ActiveRest, Serialisable):
    def __init__(self):
        super().__init__()
        self.active_stretch_exercises = {}
        self.isolated_activate_exercises = {}
        self.active_stretch_minutes = 0
        self.isolated_activate_minutes = 0

    def json_serialise(self):
        ret = {
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises.values()],
            'active_stretch_exercises': [p.json_serialise() for p in self.active_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises.values()],
            'completed': self.completed,
            'active': self.active
        }
        return ret

    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.active_stretch_minutes = self.calc_active_time(self.active_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_integrate_exercises)

    def check_reactive_care_soreness(self, soreness, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.daily and not soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = AthleteGoal("Care for Soreness", 1)
            goal.trigger = "Sore reported today"

            if body_part is not None:
                for a in body_part.agonists:
                    agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                    if agonist is not None:
                        self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)
                            self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1", soreness, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal, "2", soreness,
                                                exercise_library)

                for t in body_part.stabilizers:
                    stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                    if stabilizer is not None:
                        self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(stabilizer.active_stretch_exercises, self.active_stretch_exercises, goal, "3", soreness,
                                                exercise_library)

    def check_prevention_soreness(self, soreness, event_date_time, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.historic_soreness_status is not None and soreness.first_reported is not None and not soreness.is_dormant_cleared():
            days_sore = (event_date_time - soreness.first_reported).days
            if not soreness.pain and days_sore > 30:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 1)
                goal.trigger = "Pers, Pers-2 Soreness > 30d"

                if body_part is not None:
                    for a in body_part.agonists:
                        agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                        if agonist is not None:
                            self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)

                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", soreness, exercise_library)

                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            if soreness.severity < 2.5:
                                self.copy_exercises(antagonist.isolated_activate_exercises,
                                                    self.isolated_activate_exercises, goal,
                                                    "1", soreness, exercise_library)

                    if soreness.severity < 2.5:
                        general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                        self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", soreness, exercise_library)

    def check_prevention_pain(self, soreness, event_date_time, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.historic_soreness_status is not None and soreness.first_reported is not None:
            days_sore = (event_date_time - soreness.first_reported).days
            if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 1)
                goal.trigger = "Acute, Pers, Pers-2 Pain"

                if body_part is not None:
                    for a in body_part.agonists:
                        agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                        if agonist is not None:
                            self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)

                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", soreness, exercise_library)

                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            if soreness.severity < 2.5:
                                self.copy_exercises(antagonist.isolated_activate_exercises,
                                                    self.isolated_activate_exercises, goal,
                                                    "1", soreness, exercise_library)

                    if soreness.severity < 2.5:
                        general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                        self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", soreness, exercise_library)

    def check_reactive_care_pain(self, soreness, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.daily and soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = AthleteGoal("Care for Pain", 1)
            goal.trigger = "Pain reported today"

            if body_part is not None:
                for a in body_part.agonists:
                    agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                    if agonist is not None:
                        self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)
                            self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1", soreness, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal, "2", soreness,
                                                exercise_library)

                for t in body_part.stabilizers:
                    stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                    if stabilizer is not None:
                        self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(stabilizer.active_stretch_exercises, self.active_stretch_exercises, goal, "3", soreness,
                                                exercise_library)


class ActiveRestAfterTraining(ActiveRest, Serialisable):
    def __init__(self):
        super().__init__()
        self.isolated_activate_exercises = {}
        self.isolated_activate_minutes = 0

    def json_serialise(self):
        ret = {
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises.values()],
            'completed': self.completed,
            'active': self.active
        }
        return ret

    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_integrate_exercises)

    def check_reactive_care_soreness(self, soreness, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.daily and not soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = AthleteGoal("Care for Soreness", 1)
            goal.trigger = "Sore reported today"

            if body_part is not None:
                for a in body_part.agonists:
                    agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                    if agonist is not None:
                        self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, "2", soreness, exercise_library)

                for t in body_part.stabilizers:
                    stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                    if stabilizer is not None:
                        self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(stabilizer.static_stretch_exercises, self.static_stretch_exercises, goal, "3", soreness, exercise_library)


    def check_prevention_soreness(self, soreness, event_date_time, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.historic_soreness_status is not None and soreness.first_reported is not None and not soreness.is_dormant_cleared():
            days_sore = (event_date_time - soreness.first_reported).days
            if not soreness.pain and days_sore > 30:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 1)
                goal.trigger = "Pers, Pers-2 Soreness > 30d"

                if body_part is not None:
                    for a in body_part.agonists:
                        agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                        if agonist is not None:
                            self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)

                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", soreness, exercise_library)

                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            if soreness.severity < 2.5:
                                self.copy_exercises(antagonist.isolated_activate_exercises,
                                                    self.isolated_activate_exercises, goal,
                                                    "1", soreness, exercise_library)

                    if soreness.severity < 2.5:
                        general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                        self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", soreness, exercise_library)

    def check_prevention_pain(self, soreness, event_date_time, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.historic_soreness_status is not None and soreness.first_reported is not None:
            days_sore = (event_date_time - soreness.first_reported).days
            if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 1)
                goal.trigger = "Acute, Pers, Pers-2 Pain"

                if body_part is not None:
                    for a in body_part.agonists:
                        agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                        if agonist is not None:
                            self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)

                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", soreness, exercise_library)

                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            if soreness.severity < 2.5:
                                self.copy_exercises(antagonist.isolated_activate_exercises,
                                                    self.isolated_activate_exercises, goal,
                                                    "1", soreness, exercise_library)

                    if soreness.severity < 2.5:
                        general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                        self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", soreness, exercise_library)

    def check_reactive_care_pain(self, soreness, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.daily and soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = AthleteGoal("Care for Pain", 1)
            goal.trigger = "Pain reported today"

            if body_part is not None:
                for a in body_part.agonists:
                    agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                    if agonist is not None:
                        self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, "2", soreness, exercise_library)

                for t in body_part.stabilizers:
                    stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                    if stabilizer is not None:
                        self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(stabilizer.static_stretch_exercises, self.static_stretch_exercises, goal, "3", soreness, exercise_library)


class WarmUp(Serialisable):
    def __init__(self):
        self.inhibit_exercises = {}
        self.static_then_active_or_dynamic_stretch_exercises = {}
        self.active_or_dynamic_stretch_exercises = {}
        self.isolated_activate_exercises = {}
        self.dynamic_integrate_exercises = {}
        self.dynamic_integrate_with_speed_exercises = {}
        self.completed = False
        self.active = True

    def json_serialise(self):
        ret = {
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_then_active_or_dynamic_stretch_exercises': [p.json_serialise() for p in self.static_then_active_or_dynamic_stretch_exercises.values()],
            'active_or_dynamic_stretch_exercises': [p.json_serialise() for p in self.active_or_dynamic_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'dynamic_integrate_exercises': [p.json_serialise() for p in self.dynamic_integrate_exercises.values()],
            'dynamic_integrate_with_speed_exercises': [p.json_serialise() for p in self.dynamic_integrate_with_speed_exercises.values()],
            'completed': self.completed,
            'active': self.active
        }
        return ret


class CoolDown(Serialisable):
    def __init__(self):
        self.active_or_dynamic_stretch_exercises = {}
        self.completed = False
        self.active = True

    def json_serialise(self):
        ret = {
            'active_or_dynamic_stretch_exercises': [p.json_serialise() for p in self.active_or_dynamic_stretch_exercises.values()],
            'completed': self.completed,
            'active': self.active
        }
        return ret


class ActiveRecovery(Serialisable):
    def __init__(self):
        self.dynamic_integrate_exercises = {}
        self.dynamic_integrate_with_speed_exercises = {}
        self.completed = False
        self.active = True

    def json_serialise(self):
        ret = {
            'dynamic_integrate_exercises': [p.json_serialise() for p in self.dynamic_integrate_exercises.values()],
            'dynamic_integrate_with_speed_exercises': [p.json_serialise() for p in
                                                       self.dynamic_integrate_with_speed_exercises.values()],
            'completed': self.completed,
            'active': self.active
        }
        return ret


class Ice(Serialisable):
    def __init__(self, minutes=0, body_part_location=None, side=0):
        self.minutes = minutes
        self.body_part_location = body_part_location
        self.side = side
        self.after_training = True
        self.immediately_after_training = False
        self.repeat_every_3hrs_for_24hrs = False
        self.completed = False
        self.active = True
        self.goals = set()

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
            'body_part_location': self.body_part_location.value,
            'goals': [goal.json_serialise() for goal in self.goals],
            'side': self.side,
            'completed': self.completed,
            'active': self.active
        }

        return ret


class ColdWaterImmersion(Serialisable):
    def __init__(self, minutes=10):
        self.minutes = minutes
        self.after_training = True
        self.completed = False
        self.active = True
        self.goals = set()

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
            'after_training': self.after_training,
            'goals': [goal.json_serialise() for goal in self.goals],
            'completed': self.completed,
            'active': self.active
        }

        return ret

