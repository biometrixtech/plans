from serialisable import Serialisable
from models.soreness import BodyPart, BodyPartLocation, AssignedExercise, HistoricSorenessStatus
from models.body_parts import BodyPartFactory


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
    def __init__(self):
        self.inhibit_exercises = {}
        self.static_stretch_exercises = {}
        self.isolated_activate_exercises = {}
        self.static_integrate_exercises = {}

    def json_serialise(self):
        ret = {
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises],
        }
        return ret

    def fill_exercises(self, soreness_list, event_date_time):

        body_part_factory = BodyPartFactory()

        for s in soreness_list:

            body_part = body_part_factory.get_body_part(s.body_part_location)

            for a in body_part.agonists:
                for e, progressions_list in a.inhibit_exercises.items():
                    self.update_assigned_exercises(e, self.inhibit_exercises, event_date_time,
                                                   progressions_list, s, "1")

                for e, progressions_list in a.static_stretch_exercises.items():
                    self.update_assigned_exercises(e, self.static_stretch_exercises, event_date_time,
                                                   progressions_list, s, "1")

                for e, progressions_list in a.isolated_activate_exercises.items():
                    self.update_assigned_exercises(e, self.isolated_activate_exercises, event_date_time,
                                                   progressions_list, s, "1")

            for y in body_part.synergists:
                for e, progressions_list in y.inhibit_exercises.items():
                    self.update_assigned_exercises(e, self.inhibit_exercises, event_date_time,
                                                   progressions_list, s, "2")

                # no priority 2 synergist static stretch exercises for Active Rest after training

                for e, progressions_list in y.isolated_activate_exercises.items():
                    self.update_assigned_exercises(e, self.isolated_activate_exercises, event_date_time,
                                                   progressions_list, s, "2")

        # get general for static integrate
        # not sure how to tag general items
        #general_body_part = body_part_factory.get_body_part(BodyPartLocation.general)

        #for e, progressions_list in general_body_part.static_integrate_exercises.items():
        #    self.update_assigned_exercises(e, self.static_integrate_exercises, event_date_time,
        #                                   progressions_list, None, "1")

    def update_assigned_exercises(self, exercise_id, exercise_collection, event_date_time, progressions_list, soreness, priority):

        if exercise_id not in exercise_collection:
            exercise_collection[exercise_id] = AssignedExercise(library_id=exercise_id, progressions=progressions_list)
        if soreness.historic_soreness_status is None:
            if soreness.pain:
                exercise_collection[exercise_id].goals.add("Care")
            else:
                exercise_collection[exercise_id].goals.add("Recovery")
        else:
            days_sore = 0
            if soreness.first_reported is not None:
                days_sore = (event_date_time - soreness.first_reported).days
            if not soreness.pain and 15 <= days_sore < 30:
                exercise_collection[exercise_id].goals.add("Recovery")
            elif not soreness.pain and days_sore >= 30:
                exercise_collection[exercise_id].goals.add("Prevention")
            elif soreness.is_acute_pain() or soreness.is_persistent_pain():
                exercise_collection[exercise_id].goals.add("Prevention")
        exercise_collection[exercise_id].priorities.add(priority)
        exercise_collection[exercise_id].soreness_sources.add(soreness)


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

