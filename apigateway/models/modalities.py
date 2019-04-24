from serialisable import Serialisable
from models.soreness import BodyPart, BodyPartLocation, AssignedExercise, HistoricSorenessStatus
from models.body_parts import BodyPartFactory
from models.exercise import ExerciseBuckets
from utils import parse_date


class Heat(Serialisable):
    def __init__(self, minutes=0, body_part_location=None, side=0):
        self.minutes = minutes
        self.body_part_location = body_part_location
        self.side = side

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
            'body_part_location': self.body_part_location.value,
            'side': self.side
        }

        return ret


class ActiveRestBeforeTraining(Serialisable):
    def __init__(self):
        self.inhibit_exercises = {}
        self.static_then_active_stretch_exercises = {}
        self.active_stretch_exercises = {}
        self.isolated_activate_exercises = {}
        self.static_integrate_exercises = {}

    def json_serialise(self):
        ret = {
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises],
            'static_then_active_stretch_exercises': [p.json_serialise() for p in self.static_then_active_stretch_exercises],
            'active_stretch_exercises': [p.json_serialise() for p in self.active_stretch_exercises],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises],
        }
        return ret


class ActiveRestAfterTraining(Serialisable):
    def __init__(self, exercise_library):
        self.inhibit_exercises = {}
        self.static_stretch_exercises = {}
        self.isolated_activate_exercises = {}
        self.static_integrate_exercises = {}
        self.exercise_library = exercise_library
        self.inhibit_minutes = 0
        self.static_stretch_minutes = 0
        self.isolated_activate_minutes = 0
        self.static_integrate_minutes = 0

    def json_serialise(self):
        ret = {
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises],
        }
        return ret

    def fill_exercises(self, soreness_list, event_date_time):

        for s in soreness_list:

            self.check_reactive_recovery(s)
            self.check_reactive_care(s)
            self.check_preemptive_recovery(s, parse_date(event_date_time))
            self.check_preemptive_prevention(s, parse_date(event_date_time))

        # add exercise detail

    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_stretch_exercises)

    def calc_active_time(self, exercise_dictionary):

        active_time = 0

        for id, assigned_excercise in exercise_dictionary.items():
            active_time += assigned_excercise.duration() / 60

        return active_time

    def check_reactive_recovery(self, soreness):

        body_part_factory = BodyPartFactory()

        if soreness.daily and not soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = "Recovery"

            if body_part is not None:
                for a in body_part.agonists:
                    agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                    if agonist is not None:
                        self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness)
                        if soreness.severity < 3.5:
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness)

    def check_preemptive_recovery(self, soreness, event_date_time):

        body_part_factory = BodyPartFactory()

        if soreness.historic_soreness_status is not None and soreness.first_reported is not None:
            days_sore = (event_date_time - soreness.first_reported).days
            if not soreness.pain and 15 <= days_sore < 30:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = "Recovery"

                if body_part is not None:
                    for a in body_part.agonists:
                        agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                        if agonist is not None:
                            self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness)
                            if soreness.severity < 3.5:
                                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness)
                                self.copy_exercises(agonist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "1", soreness)
                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness)
                            if soreness.severity < 3.5:
                                self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "2", soreness)
                    if soreness.severity < 3.5:
                        general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                        self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises, goal, "1", soreness)

    def check_preemptive_prevention(self, soreness, event_date_time):

        body_part_factory = BodyPartFactory()

        if soreness.historic_soreness_status is not None and soreness.first_reported is not None:
            days_sore = (event_date_time - soreness.first_reported).days
            if (not soreness.pain and days_sore >= 30) or soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = "Prevention"

                if body_part is not None:
                    for a in body_part.agonists:
                        agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                        if agonist is not None:
                            self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness)
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness)
                            if soreness.severity < 3.5:
                                self.copy_exercises(agonist.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                                    "1", soreness)
                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness)
                            if soreness.severity < 3.5:
                                self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", soreness)
                    if soreness.severity < 3.5:
                        general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                        self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", soreness)

    def check_reactive_care(self, soreness):

        body_part_factory = BodyPartFactory()

        if soreness.daily and soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = "Care"

            if body_part is not None:
                for a in body_part.agonists:
                    agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                    if agonist is not None:
                        self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness)
                        if soreness.severity < 3.5:
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness)

    def copy_exercises(self, source_collection, target_collection, goal, priority, soreness):

        for s in source_collection:
            if s.exercise.id not in target_collection:
                target_collection[s.exercise.id] = AssignedExercise(library_id=str(s.exercise.id))
                exercise_list = [ex for ex in self.exercise_library if ex.id == str(s.exercise.id)]
                target_collection[s.exercise.id].exercise = exercise_list[0]

            target_collection[s.exercise.id] = self.update_dosage(soreness, target_collection[s.exercise.id])
            target_collection[s.exercise.id].goals.add(goal)
            target_collection[s.exercise.id].priorities.add(priority)
            target_collection[s.exercise.id].soreness_sources.add(soreness)

    def update_dosage(self, soreness, assigned_exercise):

        if soreness.severity < 0.5:
            assigned_exercise.reps_assigned = max(assigned_exercise.reps_assigned, assigned_exercise.exercise.min_reps)
            assigned_exercise.sets_assigned = max(assigned_exercise.sets_assigned, 1)
        elif 0.5 <= soreness.severity < 1.5:
            assigned_exercise.reps_assigned = max(assigned_exercise.reps_assigned, assigned_exercise.exercise.min_reps)
            assigned_exercise.sets_assigned = max(assigned_exercise.sets_assigned, 1)
        elif 1.5 <= soreness.severity < 2.5:
            assigned_exercise.reps_assigned = max(assigned_exercise.reps_assigned, assigned_exercise.exercise.max_reps)
            assigned_exercise.sets_assigned = max(assigned_exercise.sets_assigned, 1)
        elif 2.5 <= soreness.severity < 3.5:
            assigned_exercise.reps_assigned = max(assigned_exercise.reps_assigned, assigned_exercise.exercise.max_reps)
            assigned_exercise.sets_assigned = max(assigned_exercise.sets_assigned, 1)
        elif 3.5 <= soreness.severity < 4.5:
            assigned_exercise.reps_assigned = max(assigned_exercise.reps_assigned, assigned_exercise.exercise.max_reps)
            assigned_exercise.sets_assigned = max(assigned_exercise.sets_assigned, 1)
        elif soreness >= 4.5:
            assigned_exercise.reps_assigned = max(assigned_exercise.reps_assigned, assigned_exercise.exercise.max_reps)
            assigned_exercise.sets_assigned = max(assigned_exercise.sets_assigned, 2)

        return assigned_exercise


class WarmUp(Serialisable):
    def __init__(self):
        self.inhibit_exercises = {}
        self.static_then_active_or_dynamic_stretch_exercises = {}
        self.active_or_dynamic_stretch_exercises = {}
        self.isolated_activate_exercises = {}
        self.dynamic_integrate_exercises = {}
        self.dynamic_integrate_with_speed_exercises = {}

    def json_serialise(self):
        ret = {
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises],
            'static_then_active_or_dynamic_stretch_exercises': [p.json_serialise() for p in self.static_then_active_or_dynamic_stretch_exercises],
            'active_or_dynamic_stretch_exercises': [p.json_serialise() for p in self.active_or_dynamic_stretch_exercises],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises],
            'dynamic_integrate_exercises': [p.json_serialise() for p in self.dynamic_integrate_exercises],
            'dynamic_integrate_with_speed_exercises': [p.json_serialise() for p in self.dynamic_integrate_with_speed_exercises],
        }
        return ret


class CoolDown(Serialisable):
    def __init__(self):
        self.active_or_dynamic_stretch_exercises = {}

    def json_serialise(self):
        ret = {
            'active_or_dynamic_stretch_exercises': [p.json_serialise() for p in self.active_or_dynamic_stretch_exercises],
        }
        return ret


class ActiveRecovery(Serialisable):
    def __init__(self):
        self.dynamic_integrate_exercises = {}
        self.dynamic_integrate_with_speed_exercises = {}

    def json_serialise(self):
        ret = {
            'dynamic_integrate_exercises': [p.json_serialise() for p in self.dynamic_integrate_exercises],
            'dynamic_integrate_with_speed_exercises': [p.json_serialise() for p in
                                                       self.dynamic_integrate_with_speed_exercises],
        }
        return ret


class Ice(Serialisable):
    def __init__(self, minutes=0, body_part_location=None, side=0):
        self.minutes = minutes
        self.body_part_location = body_part_location
        self.side = side

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
            'body_part_location': self.body_part_location.value,
            'side': self.side
        }

        return ret


class ColdWaterImmersion(Serialisable):
    def __init__(self, minutes=0):
        self.minutes = minutes

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
        }

        return ret

