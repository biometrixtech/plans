from serialisable import Serialisable
from models.soreness import BodyPart, BodyPartLocation, AssignedExercise, HistoricSorenessStatus, AthleteGoal, AthleteGoalType, ExerciseDosage
from models.body_parts import BodyPartFactory
from utils import parse_datetime, format_datetime
import abc
import datetime


class HeatSession(Serialisable):
    def __init__(self):
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = None
        self.completed = False
        self.active = True
        self.body_parts = []

    def json_serialise(self):

        ret = {
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'body_parts': [heat.json_serialise() for heat in self.body_parts]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        heat_session = cls()
        heat_session.start_date_time = input_dict.get('start_date_time', None)
        heat_session.event_date_time = input_dict.get('event_date_time', None)
        heat_session.completed = input_dict.get('completed', False)
        heat_session.active = input_dict.get('active', True)
        heat_session.body_parts = [Heat.json_deserialise(body_part) for body_part in input_dict.get('body_parts', [])]
        if len(heat_session.body_parts) > 0:
            return heat_session
        else:
            return None

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)


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

    @classmethod
    def json_deserialise(cls, input_dict):
        heat = cls(minutes=input_dict['minutes'],
                   body_part_location=BodyPartLocation(input_dict['body_part_location']),
                   side=input_dict['side'])
        heat.before_training = input_dict.get('before_training', True)
        heat.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])
        heat.completed = input_dict.get('completed', False)
        heat.active = input_dict.get('active', True)

        return heat


class ModalityBase(object):
    def __init__(self, event_date_time):
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = event_date_time
        self.completed = False
        self.active = True
        self.default_plan = "Complete"

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)

    @abc.abstractmethod
    def conditions_for_increased_sensitivity_met(self, soreness_list):
        return False

    def set_plan_dosage(self, soreness_list):

        care_for_pain_present = False
        historic_status_present = False
        severity_greater_than_2 = False

        for s in soreness_list:
            if s.pain:
                care_for_pain_present = True
            if s.historic_soreness_status is not None and not s.is_dormant_cleared():
                historic_status_present = True
            if s.severity >= 2:
                severity_greater_than_2 = True

        increased_sensitivity = self.conditions_for_increased_sensitivity_met(soreness_list)

        if care_for_pain_present and not historic_status_present:
            self.default_plan = "Comprehensive"
        elif not severity_greater_than_2 and not care_for_pain_present and not historic_status_present:
            if not increased_sensitivity:
                self.default_plan = "Efficient"
            else:
                self.default_plan = "Complete"
        else:
            if not increased_sensitivity:
                self.default_plan = "Complete"
            else:
                self.default_plan = "Comprehensive"

    def copy_exercises(self, source_collection, target_collection, goal, priority, soreness, exercise_library):

        for s in source_collection:
            if s.exercise.id not in target_collection:
                target_collection[s.exercise.id] = AssignedExercise(library_id=str(s.exercise.id))
                exercise_list = [ex for ex in exercise_library if ex.id == str(s.exercise.id)]
                target_collection[s.exercise.id].exercise = exercise_list[0]
                target_collection[s.exercise.id].equipment_required = target_collection[s.exercise.id].exercise.equipment_required

            dosage = ExerciseDosage()
            dosage.priority = priority
            dosage.soreness_source = soreness
            dosage.goal = goal
            dosage = self.update_dosage(dosage, target_collection[s.exercise.id].exercise)
            target_collection[s.exercise.id].dosages.append(dosage)

    @abc.abstractmethod
    def fill_exercises(self, soreness_list, exercise_library):
        pass

    @staticmethod
    def update_dosage(dosage, exercise):

        if (dosage.goal.goal_type == AthleteGoalType.sore and
                (dosage.soreness_source.historic_soreness_status is None or
                 dosage.soreness_source.historic_soreness_status.is_dormant_cleared()) or
                dosage.goal.goal_type == AthleteGoalType.sport or
                dosage.goal.goal_type == AthleteGoalType.preempt_sport or
                dosage.goal.goal_type == AthleteGoalType.preempt_personalized_sport or
                dosage.goal.goal_type == AthleteGoalType.preempt_corrective):
            if dosage.soreness_source.severity < 0.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                else:
                    dosage.efficient_reps_assigned = 0
                    dosage.efficient_sets_assigned = 0
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                else:
                    dosage.complete_reps_assigned = 0
                    dosage.complete_sets_assigned = 0

                dosage.comprehensive_reps_assigned = exercise.min_reps
                dosage.comprehensive_sets_assigned = 1
            elif 0.5 <= dosage.soreness_source.severity < 1.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                else:
                    dosage.efficient_reps_assigned = 0
                    dosage.efficient_sets_assigned = 0

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                else:
                    dosage.complete_reps_assigned = 0
                    dosage.complete_sets_assigned = 0
                dosage.comprehensive_reps_assigned = exercise.min_reps
                dosage.comprehensive_sets_assigned = 1
            elif 1.5 <= dosage.soreness_source.severity < 2.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                else:
                    dosage.efficient_reps_assigned = 0
                    dosage.efficient_sets_assigned = 0
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.max_reps
                    dosage.complete_sets_assigned = 1
                else:
                    dosage.complete_reps_assigned = 0
                    dosage.complete_sets_assigned = 0
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
            elif 2.5 <= dosage.soreness_source.severity < 3.5:
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                else:
                    dosage.efficient_reps_assigned = 0
                    dosage.efficient_sets_assigned = 0

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2
            elif 3.5 <= dosage.soreness_source.severity < 4.5:
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2
            elif dosage.soreness_source.severity >= 4.5:
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3

        else:
            if dosage.soreness_source.severity < 0.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                else:
                    dosage.efficient_reps_assigned = 0
                    dosage.efficient_sets_assigned = 0
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                else:
                    dosage.complete_reps_assigned = 0
                    dosage.complete_sets_assigned = 0

                dosage.comprehensive_reps_assigned = exercise.min_reps
                dosage.comprehensive_sets_assigned = 1
            elif 0.5 <= dosage.soreness_source.severity < 1.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                else:
                    dosage.efficient_reps_assigned = 0
                    dosage.efficient_sets_assigned = 0

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.max_reps
                    dosage.complete_sets_assigned = 1
                else:
                    dosage.complete_reps_assigned = 0
                    dosage.complete_sets_assigned = 0
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
            elif 1.5 <= dosage.soreness_source.severity < 2.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                else:
                    dosage.efficient_reps_assigned = 0
                    dosage.efficient_sets_assigned = 0

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1

                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1

            elif 2.5 <= dosage.soreness_source.severity < 3.5:

                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2

            elif 3.5 <= dosage.soreness_source.severity < 4.5:
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3
            elif dosage.soreness_source.severity >= 4.5:
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3

        return dosage

    @staticmethod
    def rank_dosages(target_collections):
        for target_collection in target_collections:
            for ex in target_collection.values():
                ex.set_dosage_ranking()


class ActiveRest(ModalityBase):
    def __init__(self, high_relative_load_session, high_relative_intensity_logged, muscular_strain_increasing, event_date_time):
        super().__init__(event_date_time)
        self.high_relative_load_session = high_relative_load_session
        self.high_relative_intensity_logged = high_relative_intensity_logged
        self.muscular_strain_increasing = muscular_strain_increasing
        self.event_date_time = event_date_time
        self.inhibit_exercises = {}
        self.static_integrate_exercises = {}
        self.static_stretch_exercises = {}

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

    '''deprecated
    @abc.abstractmethod
    def calc_durations(self):
        pass
    '''

    def conditions_for_increased_sensitivity_met(self, soreness_list):

        if self.muscular_strain_increasing:
            return True
        else:
            for s in soreness_list:
                if s.first_reported_date is not None and not s.is_dormant_cleared():
                    days_sore = (self.event_date_time - s.first_reported_date).days
                    if not s.pain and days_sore < 30:
                        return True
        return False

    def fill_exercises(self, soreness_list, exercise_library):

        for s in soreness_list:
            self.check_reactive_care_soreness(s, exercise_library)
            self.check_reactive_care_pain(s, exercise_library)
            self.check_prevention_soreness(s, self.event_date_time, exercise_library)
            self.check_prevention_pain(s, self.event_date_time, exercise_library)

    '''dprecated
    def calc_active_time(self, exercise_dictionary):

        active_time = 0

        for id, assigned_excercise in exercise_dictionary.items():
            active_time += assigned_excercise.duration() / 60

        return active_time
    '''


class ActiveRestBeforeTraining(ActiveRest, Serialisable):
    def __init__(self, high_relative_load_session, high_relative_intensity_logged, muscular_strain_increasing, event_date_time):
        super().__init__(high_relative_load_session, high_relative_intensity_logged, muscular_strain_increasing, event_date_time)
        self.active_stretch_exercises = {}
        self.isolated_activate_exercises = {}

    def json_serialise(self):
        ret = {
            'high_relative_load_session': self.high_relative_load_session,
            'high_relative_intensity_logged': self.high_relative_intensity_logged,
            'muscular_strain_increasing': self.muscular_strain_increasing,
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises.values()],
            'active_stretch_exercises': [p.json_serialise() for p in self.active_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'default_plan': self.default_plan
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        pre_active_rest = cls(high_relative_load_session=input_dict.get('high_relative_load_session', False),
                              high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
                              muscular_strain_increasing=input_dict.get('muscular_strain_increasing', False),
                              event_date_time=input_dict.get('event_date_time', None))
        pre_active_rest.active = input_dict.get("active", True)
        pre_active_rest.start_date_time = input_dict.get("start_date_time", None)
        pre_active_rest.completed_date_time = input_dict.get("completed_date_time", None)
        pre_active_rest.completed = input_dict.get("completed", False)
        pre_active_rest.inhibit_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                             for s in input_dict['inhibit_exercises']}
        pre_active_rest.static_stretch_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                                    for s in input_dict['static_stretch_exercises']}
        pre_active_rest.static_integrate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                                      for s in input_dict['static_integrate_exercises']}
        pre_active_rest.active_stretch_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                                    for s in input_dict['active_stretch_exercises']}
        pre_active_rest.isolated_activate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                                       for s in input_dict['isolated_activate_exercises']}
        pre_active_rest.default_plan = input_dict.get('default_plan', 'complete')

        return pre_active_rest

    '''deprecated
    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.active_stretch_minutes = self.calc_active_time(self.active_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_integrate_exercises)
    '''

    def check_reactive_care_soreness(self, soreness, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.daily and not soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = AthleteGoal("Care for Soreness", 1, AthleteGoalType.sore)
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

        if soreness.historic_soreness_status is not None and soreness.first_reported_date is not None and not soreness.is_dormant_cleared():
            days_sore = (event_date_time - soreness.first_reported_date).days
            if not soreness.pain and days_sore > 30:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 1, AthleteGoalType.corrective)
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

        if soreness.historic_soreness_status is not None and soreness.first_reported_date is not None:
            # days_sore = (event_date_time - soreness.first_reported_date).days
            if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 1, AthleteGoalType.corrective)
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

            goal = AthleteGoal("Care for Pain", 1, AthleteGoalType.pain)
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

    def set_exercise_dosage_ranking(self):
        self.rank_dosages([self.inhibit_exercises,
                           self.static_stretch_exercises,
                           self.active_stretch_exercises,
                           self.isolated_activate_exercises,
                           self.static_integrate_exercises])


class ActiveRestAfterTraining(ActiveRest, Serialisable):
    def __init__(self, high_relative_load_session, high_relative_intensity_logged, muscular_strain_increasing, event_date_time):
        super().__init__(high_relative_load_session, high_relative_intensity_logged, muscular_strain_increasing, event_date_time)
        self.isolated_activate_exercises = {}

    def json_serialise(self):
        ret = {
            'high_relative_load_session': self.high_relative_load_session,
            'high_relative_intensity_logged': self.high_relative_intensity_logged,
            'muscular_strain_increasing': self.muscular_strain_increasing,
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'default_plan': self.default_plan
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        post_active_rest = cls(high_relative_load_session=input_dict.get('high_relative_load_session', False),
                               high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
                               muscular_strain_increasing=input_dict.get('muscular_strain_increasing', False),
                               event_date_time=input_dict.get('event_date_time', None))
        post_active_rest.active = input_dict.get("active", True)
        post_active_rest.start_date_time = input_dict.get("start_date_time", None)
        post_active_rest.completed_date_time = input_dict.get("completed_date_time", None)
        post_active_rest.completed = input_dict.get("completed", False)
        post_active_rest.inhibit_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                              for s in input_dict['inhibit_exercises']}
        post_active_rest.static_stretch_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                                     for s in input_dict['static_stretch_exercises']}
        post_active_rest.static_integrate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                                       for s in input_dict['static_integrate_exercises']}
        post_active_rest.isolated_activate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s)
                                                        for s in input_dict['isolated_activate_exercises']}
        post_active_rest.default_plan = input_dict.get('default_plan', 'complete')

        return post_active_rest

    '''deprecated
    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_integrate_exercises)
    '''

    def check_reactive_care_soreness(self, soreness, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.daily and not soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = AthleteGoal("Care for Soreness", 1, AthleteGoalType.sore)
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

        if soreness.historic_soreness_status is not None and soreness.first_reported_date is not None and not soreness.is_dormant_cleared():
            days_sore = (event_date_time - soreness.first_reported_date).days
            if not soreness.pain and days_sore > 30:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 1, AthleteGoalType.corrective)
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

        if soreness.historic_soreness_status is not None and soreness.first_reported_date is not None:
            # days_sore = (event_date_time - soreness.first_reported_date).days
            if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 1, AthleteGoalType.corrective)
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

            goal = AthleteGoal("Care for Pain", 1, AthleteGoalType.pain)
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

    def set_exercise_dosage_ranking(self):
        self.rank_dosages([self.inhibit_exercises,
                           self.static_stretch_exercises,
                           self.isolated_activate_exercises,
                           self.static_integrate_exercises])


class WarmUp(ModalityBase, Serialisable):
    def __init__(self, event_date_time):
        super().__init__(event_date_time)
        self.inhibit_exercises = {}
        self.static_stretch_exercises = {}
        self.active_or_dynamic_stretch_exercises = {}
        self.isolated_activate_exercises = {}
        self.dynamic_integrate_exercises = {}
        self.dynamic_integrate_with_speed_exercises = {}

    def json_serialise(self):
        ret = {
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises.values()],
            'active_or_dynamic_stretch_exercises': [p.json_serialise() for p in self.active_or_dynamic_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'dynamic_integrate_exercises': [p.json_serialise() for p in self.dynamic_integrate_exercises.values()],
            'dynamic_integrate_with_speed_exercises': [p.json_serialise() for p in self.dynamic_integrate_with_speed_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        warmup = cls(input_dict.get('event_date_time', None))
        warmup.inhibit_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['inhibit_exercises']}
        warmup.static_stretch_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['static_stretch_exercises']}
        warmup.active_or_dynamic_stretch_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['active_or_dynamic_stretch_exercises']}
        warmup.isolated_activate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['isolated_activate_exercises']}
        warmup.dynamic_integrate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['dynamic_integrate_exercises']}
        warmup.dynamic_integrate_with_speed_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['dynamic_integrate_with_speed_exercises']}
        warmup.start_date_time = input_dict.get('start_date_time', None)
        warmup.completed_date_time = input_dict.get('completed_date_time', None)
        warmup.completed = input_dict.get('completed', False)
        warmup.active = input_dict.get('active', True)

        return warmup

    def fill_exercises(self, soreness_list, exercise_library):
        for s in soreness_list:
            self.check_corrective_soreness(s, self.event_date_time, exercise_library)
            self.check_preempt_soreness(s, self.event_date_time, exercise_library)

    def check_preempt_soreness(self, soreness, event_date_time, exercise_library):

        if soreness.historic_soreness_status is not None and soreness.first_reported_date is not None and not soreness.is_dormant_cleared():
            days_sore = (event_date_time - soreness.first_reported_date).days
            if not soreness.pain and days_sore < 30:

                goal = AthleteGoal("Personalized Prepare for Training", 1, AthleteGoalType.preempt_personalized_sport)
                goal.trigger = "Pers, Pers-2 Soreness > 30d"

                self.assign_exercises(soreness, goal, exercise_library)

    def check_corrective_soreness(self, soreness, event_date_time, exercise_library):

        if soreness.historic_soreness_status is not None and soreness.first_reported_date is not None and not soreness.is_dormant_cleared():
            days_sore = (event_date_time - soreness.first_reported_date).days
            if soreness.pain or days_sore > 30:
                goal = AthleteGoal("Personalized Prepare for Training (Identified Dysfunction)", 1, AthleteGoalType.preempt_corrective)
                goal.trigger = "Pers, Pers-2 Soreness > 30d"

                self.assign_exercises(soreness, goal, exercise_library)

    def assign_exercises(self, soreness, goal, exercise_library):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part(soreness.body_part)

        if body_part is not None:
            for a in body_part.agonists:
                agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                if agonist is not None:
                    self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness,
                                        exercise_library)
                    if soreness.severity < 3.5:
                        self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                            soreness, exercise_library)
                        self.copy_exercises(agonist.isolated_activate_exercises, self.isolated_activate_exercises,
                                            goal, "1", soreness, exercise_library)
                        self.copy_exercises(agonist.active_or_dynamic_stretch_exercises,
                                            self.active_or_dynamic_stretch_exercises,
                                            goal, "1", soreness, exercise_library)
            for y in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                if synergist is not None:
                    self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", soreness,
                                        exercise_library)
                    if soreness.severity < 3.5:
                        self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                            goal, "2", soreness, exercise_library)
                        self.copy_exercises(synergist.active_or_dynamic_stretch_exercises,
                                            self.active_or_dynamic_stretch_exercises,
                                            goal, "2", soreness, exercise_library)

    def set_exercise_dosage_ranking(self):
        self.rank_dosages([self.inhibit_exercises,
                           self.static_stretch_exercises,
                           self.isolated_activate_exercises,
                           self.active_or_dynamic_stretch_exercises,
                           self.dynamic_integrate_exercises,
                           self.dynamic_integrate_with_speed_exercises])


class CoolDown(ModalityBase, Serialisable):
    def __init__(self, sport_name, high_relative_load_session, high_relative_intensity_logged, muscular_strain_increasing, event_date_time):
        super().__init__(event_date_time)
        self.sport_name = sport_name
        self.high_relative_volume_logged = high_relative_load_session
        self.high_relative_intensity_logged = high_relative_intensity_logged
        self.muscular_strain_increasing = muscular_strain_increasing
        self.dynamic_stretch_integrate_exercises = {}

    def json_serialise(self):
        ret = {
            'sport_name': self.sport_name,
            'high_relative_load_session': self.high_relative_volume_logged,
            'high_relative_intensity_logged': self.high_relative_intensity_logged,
            'muscular_strain_increasing': self.muscular_strain_increasing,
            'dynamic_stretch_integrate_exercises': [p.json_serialise() for p in self.dynamic_stretch_integrate_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        cooldown = cls(sport_name=input_dict.get('sport_name', 0),
                       high_relative_load_session=input_dict.get('high_relative_load_session', False),
                       high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
                       muscular_strain_increasing=input_dict.get('muscular_strain_increasing', False),
                       event_date_time=input_dict.get('event_date_time', None))
        cooldown.dynamic_stretch_integrate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['dynamic_stretch_integrate_exercises']}
        cooldown.start_date_time = input_dict.get('start_date_time', None)
        cooldown.completed_date_time = input_dict.get('completed_date_time', None)
        cooldown.completed = input_dict.get('completed', False)
        cooldown.active = input_dict.get('active', True)

        return cooldown

    def conditions_for_increased_sensitivity_met(self, soreness_list):

        if self.muscular_strain_increasing:
            return True
        else:
            for s in soreness_list:
                if s.first_reported_date is not None and not s.is_dormant_cleared():
                    days_sore = (self.event_date_time - s.first_reported_date).days
                    if (not s.pain and days_sore < 30) or s.pain:
                        return True
        return False

    def set_exercise_dosage_ranking(self):
        self.rank_dosages([self.dynamic_stretch_integrate_exercises])

    def check_recover_from_sport(self, soreness_list, exercise_library):

        if self.high_relative_volume_logged or self.high_relative_intensity_logged:
            goal = AthleteGoal("Recover from Sport", 1, AthleteGoalType.sport)
            goal.trigger = "High Relative Volume or Intensity of Logged Session"

            body_part_factory = BodyPartFactory()

            body_part = body_part_factory.get_body_part_for_sport(self.sport_name)

            prohibiting_soreness = False

            high_severity_list = list(s for s in soreness_list if s.severity >= 3.5)

            if len(high_severity_list) > 0:
                prohibiting_soreness = True

            # Note: this is just returning the primary mover related exercises for sport
            if body_part is not None and not prohibiting_soreness:
                self.copy_exercises(body_part.dynamic_stretch_integrate_exercises,
                                    self.dynamic_stretch_integrate_exercises, goal, "1", None, exercise_library)

    def check_corrective(self, soreness, event_date_time, exercise_library):

        if soreness.historic_soreness_status is not None and soreness.first_reported_date is not None and not soreness.is_dormant_cleared():
            days_sore = (event_date_time - soreness.first_reported_date).days
            if soreness.pain or days_sore > 30:
                goal = AthleteGoal("Personalized Prepare for Training (Identified Dysfunction)", 1, AthleteGoalType.preempt_corrective)
                goal.trigger = "Pers, Pers-2 Soreness > 30d or Historic Pain"

                self.assign_exercises(soreness, goal, exercise_library)

    def fill_exercises(self, soreness_list, exercise_library):

        self.check_recover_from_sport(soreness_list, exercise_library)
        for s in soreness_list:
            self.check_corrective(s, self.event_date_time, exercise_library)

    def assign_exercises(self, soreness, goal, exercise_library):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part(soreness.body_part)

        if body_part is not None:
            for a in body_part.agonists:
                agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                if agonist is not None:
                    if soreness.severity < 3.5:
                        self.copy_exercises(agonist.dynamic_stretch_integrate_exercises, self.dynamic_stretch_integrate_exercises, goal,
                                            "1", soreness,
                                            exercise_library)

            for y in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                if synergist is not None:
                    self.copy_exercises(synergist.dynamic_stretch_integrate_exercises, self.dynamic_stretch_integrate_exercises, goal, "2",
                                        soreness,
                                        exercise_library)


'''Heck NO!
class ActiveRecovery(Serialisable):
    def __init__(self):
        self.dynamic_integrate_exercises = {}
        self.dynamic_integrate_with_speed_exercises = {}
        self.start_date_time = None
        self.event_date_time = None
        self.completed = False
        self.active = True

    def json_serialise(self):
        ret = {
            'dynamic_integrate_exercises': [p.json_serialise() for p in self.dynamic_integrate_exercises.values()],
            'dynamic_integrate_with_speed_exercises': [p.json_serialise() for p in self.dynamic_integrate_with_speed_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        active_recovery = cls()
        active_recovery.dynamic_integrate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['dynamic_integrate_exercises']}
        active_recovery.dynamic_integrate_with_speed_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['dynamic_integrate_with_speed_exercises']}
        active_recovery.start_date_time = input_dict.get('start_date_time', None)
        active_recovery.event_date_time = input_dict.get('event_date_time', None)
        active_recovery.completed = input_dict.get('completed', False)
        active_recovery.active = input_dict.get('active', True)

        return active_recovery

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)

'''


class IceSession(Serialisable):
    def __init__(self):
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = None
        self.completed = False
        self.active = True
        self.body_parts = []

    def json_serialise(self):

        ret = {
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'body_parts': [ice.json_serialise() for ice in self.body_parts]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        ice_session = cls()
        ice_session.start_date_time = input_dict.get('start_date_time', None)
        ice_session.completed_date_time = input_dict.get('completed_date_time', None)
        ice_session.event_date_time = input_dict.get('event_date_time', None)
        ice_session.completed = input_dict.get('completed', False)
        ice_session.active = input_dict.get('active', True)
        ice_session.body_parts = [Ice.json_deserialise(body_part) for body_part in input_dict.get('body_parts', [])]
        if len(ice_session.body_parts) > 0:
            return ice_session
        else:
            return None

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)


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
            'after_training': self.after_training,
            'immediately_after_training': self.immediately_after_training,
            'repeat_every_3hrs_for_24hrs': self.repeat_every_3hrs_for_24hrs,
            'side': self.side,
            'completed': self.completed,
            'active': self.active
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        ice = cls(minutes=input_dict['minutes'],
                  body_part_location=BodyPartLocation(input_dict['body_part_location']),
                  side=input_dict['side'])
        ice.after_training = input_dict.get('after_training', False)
        ice.immediately_after_training = input_dict.get('immediately_after_training', False)
        ice.repeat_every_3hrs_for_24hrs = input_dict.get('repeat_every_3hrs_for_24hrs', False)
        ice.completed = input_dict.get('completed', False)
        ice.active = input_dict.get('active', True)
        ice.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])

        return ice


class ColdWaterImmersion(Serialisable):
    def __init__(self, minutes=10):
        self.minutes = minutes
        self.after_training = True
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = None
        self.completed = False
        self.active = True
        self.goals = set()

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
            'after_training': self.after_training,
            'goals': [goal.json_serialise() for goal in self.goals],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        cold_water_immersion = cls(minutes=input_dict['minutes'])
        cold_water_immersion.after_training = input_dict.get('after_training', True)
        cold_water_immersion.start_date_time = input_dict.get('start_date_time', None)
        cold_water_immersion.completed_date_time = input_dict.get('completed_date_time', None)
        cold_water_immersion.event_date_time = input_dict.get('event_date_time', None)
        cold_water_immersion.completed = input_dict.get('completed', False)
        cold_water_immersion.active = input_dict.get('active', True)
        cold_water_immersion.goals = set([AthleteGoal.json_deserialise(goal) for goal in input_dict.get('goals', [])])

        return cold_water_immersion

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)
