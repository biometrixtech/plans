from serialisable import Serialisable
from models.soreness import BodyPart, BodyPartLocation, AssignedExercise
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

    def fill_exercises(self, soreness_list, historic_soreness_list):

        body_part_factory = BodyPartFactory()

        for s in soreness_list:

            body_part = body_part_factory.get_body_part(s.body_part_location)

            for a in body_part.agonists:
                for e, progressions_list in a.inhibit_exercises.items():
                    if e not in self.inhibit_exercises:
                        self.inhibit_exercises[e] = AssignedExercise(library_id=e, progressions=progressions_list)

                    if s.pain:
                        self.inhibit_exercises[e].goals.add("Care")
                    else:
                        self.inhibit_exercises[e].goals.add("Recovery")
                    self.inhibit_exercises[e].priorities.add("1")
                    self.inhibit_exercises[e].soreness_sources.add(s)

                for e, progressions_list in a.static_stretch_exercises.items():
                    if e not in self.inhibit_exercises:
                        self.static_stretch_exercises[e] = AssignedExercise(library_id=e, progressions=progressions_list)

                    if s.pain:
                        self.static_stretch_exercises[e].goals.add("Care")
                    else:
                        self.static_stretch_exercises[e].goals.add("Recovery")
                    self.static_stretch_exercises[e].priorities.add("1")
                    self.static_stretch_exercises[e].soreness_sources.add(s)

            for y in body_part.synergists:
                for e, progressions_list in y.inhibit_exercises.items():
                    if e not in self.inhibit_exercises:
                        self.inhibit_exercises[e] = AssignedExercise(library_id=e, progressions=progressions_list)

                    if s.pain:
                        self.inhibit_exercises[e].goals.add("Care")
                    else:
                        self.inhibit_exercises[e].goals.add("Recovery")
                    self.inhibit_exercises[e].priorities.add("2")
                    self.inhibit_exercises[e].soreness_sources.add(s)

                for e, progressions_list in y.static_stretch_exercises.items():
                    if e not in self.inhibit_exercises:
                        self.static_stretch_exercises[e] = AssignedExercise(library_id=e,
                                                                            progressions=progressions_list)

                    if s.pain:
                        self.static_stretch_exercises[e].goals.add("Care")
                    else:
                        self.static_stretch_exercises[e].goals.add("Recovery")
                    self.static_stretch_exercises[e].priorities.add("2")
                    self.static_stretch_exercises[e].soreness_sources.add(s)


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

