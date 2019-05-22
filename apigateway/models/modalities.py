from serialisable import Serialisable
from models.soreness import BodyPart, BodyPartLocation, AssignedExercise, HistoricSorenessStatus, AthleteGoal, AthleteGoalType, ExerciseDosage, Soreness, Alert, BodyPartSide
from models.trigger import TriggerType
from models.body_parts import BodyPartFactory
from models.sport import SportName
from utils import parse_datetime, format_datetime
import abc
import datetime


class DosageDuration(object):
    def __init__(self, efficient_duration, complete_duration, comprehensive_duration):
        self.efficient_duration = efficient_duration
        self.complete_duration = complete_duration
        self.comprehensive_duration = comprehensive_duration


class HeatSession(Serialisable):
    def __init__(self, minutes=0):
        self.minutes = minutes
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = None
        self.completed = False
        self.active = True
        self.body_parts = []
        self.alerts = []

    def json_serialise(self):

        ret = {
            'minutes': self.minutes,
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'body_parts': [heat.json_serialise() for heat in self.body_parts],
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        heat_session = cls(input_dict.get('minutes', 0))
        heat_session.start_date_time = input_dict.get('start_date_time', None)
        heat_session.completed_date_time = input_dict.get('completed_date_time', None)
        heat_session.event_date_time = input_dict.get('event_date_time', None)
        heat_session.completed = input_dict.get('completed', False)
        heat_session.active = input_dict.get('active', True)
        heat_session.body_parts = [Heat.json_deserialise(body_part) for body_part in input_dict.get('body_parts', [])]
        heat_session.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
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
    def __init__(self, body_part_location=None, side=0):
        self.body_part_location = body_part_location
        self.side = side
        self.before_training = True
        self.goals = set()
        self.completed = False
        self.active = True

    def json_serialise(self):

        ret = {
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
        heat = cls(body_part_location=BodyPartLocation(input_dict['body_part_location']),
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
        self.alerts = []
        self.dosage_durations = {}
        self.initialize_dosage_durations()

    def initialize_dosage_durations(self):

        self.dosage_durations[0.5] = DosageDuration(0, 0, 0)
        self.dosage_durations[1.5] = DosageDuration(0, 0, 0)
        self.dosage_durations[2.5] = DosageDuration(0, 0, 0)
        self.dosage_durations[3.5] = DosageDuration(0, 0, 0)
        self.dosage_durations[4.5] = DosageDuration(0, 0, 0)
        self.dosage_durations[5.0] = DosageDuration(0, 0, 0)

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        elif name == 'sport_name':
            try:
                value = SportName(value)
            except ValueError:
                value = SportName(None)
        super().__setattr__(name, value)

    @abc.abstractmethod
    def conditions_for_increased_sensitivity_met(self, soreness_list, muscular_strain_high):
        return False

    def set_plan_dosage(self, soreness_list, muscular_strain_high):

        care_for_pain_present = False
        historic_status_present = False
        severity_greater_than_2 = False

        for s in soreness_list:
            if s.pain:
                care_for_pain_present = True
            if (s.historic_soreness_status is not None and not s.is_dormant_cleared() and
                    s.historic_soreness_status is not HistoricSorenessStatus.doms):
                historic_status_present = True
            if s.severity >= 2:
                severity_greater_than_2 = True

        increased_sensitivity = self.conditions_for_increased_sensitivity_met(soreness_list, muscular_strain_high)

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

    def copy_exercises(self, source_collection, target_collection, goal, priority, soreness, exercise_library, sport_name=None):

        for s in source_collection:
            if s.exercise.id not in target_collection:
                target_collection[s.exercise.id] = AssignedExercise(library_id=str(s.exercise.id))
                exercise_list = [ex for ex in exercise_library if ex.id == str(s.exercise.id)]
                target_collection[s.exercise.id].exercise = exercise_list[0]
                target_collection[s.exercise.id].equipment_required = target_collection[s.exercise.id].exercise.equipment_required

            dosage = ExerciseDosage()
            dosage.priority = priority
            dosage.soreness_source = soreness
            dosage.sport_name = sport_name
            dosage.goal = goal
            dosage = self.update_dosage(dosage, target_collection[s.exercise.id].exercise)
            target_collection[s.exercise.id].dosages.append(dosage)

    def aggregate_dosages(self):
        pass

    def aggregate_dosage_by_severity_exercise_collection(self, assigned_exercises):

        for ex, a in assigned_exercises.items():
            if len(a.dosages) > 0:
                a.dosages = sorted(a.dosages, key=lambda x: (x.severity(),
                                                             x.comprehensive_sets_assigned,
                                                             x.comprehensive_reps_assigned,
                                                             x.complete_sets_assigned,
                                                             x.complete_reps_assigned,
                                                             x.efficient_sets_assigned,
                                                             x.efficient_reps_assigned), reverse=True)

                dosage = a.dosages[0]

                if dosage.severity() < 0.5:
                    self.calc_dosage_durations(0.5, a, dosage)
                elif 0.5 <= dosage.severity() < 1.5:
                        self.calc_dosage_durations(1.5, a, dosage)
                elif 1.5 <= dosage.severity() < 2.5:
                        self.calc_dosage_durations(2.5, a, dosage)
                elif 2.5 <= dosage.severity() < 3.5:
                        self.calc_dosage_durations(3.5, a, dosage)
                elif 3.5 <= dosage.severity() < 4.5:
                        self.calc_dosage_durations(4.5, a, dosage)
                elif 4.5 <= dosage.severity() <= 5.0:
                        self.calc_dosage_durations(5.0, a, dosage)

        # key off efficient as the guide
        total_efficient = 0
        total_complete = 0
        total_comprehensive = 0
        benchmarks = [5.0, 4.5, 3.5, 2.5, 1.5, 0.5]

        efficient_winner = None
        complete_winner = None
        comprehensive_winner = None

        for b in range(0, len(benchmarks) - 1):
            total_efficient += self.dosage_durations[benchmarks[b]].efficient_duration
            proposed_efficient = total_efficient + self.dosage_durations[benchmarks[b + 1]].efficient_duration
            if proposed_efficient < 300:
                continue
            elif abs(total_efficient - 300) < abs(proposed_efficient - 300):
                efficient_winner = benchmarks[b]
                break
            else:
                efficient_winner = benchmarks[b + 1]
                break

        for b in range(0, len(benchmarks) - 1):
            total_complete += self.dosage_durations[benchmarks[b]].complete_duration
            proposed_complete = total_complete + self.dosage_durations[benchmarks[b + 1]].complete_duration
            if proposed_complete < 900:
                continue
            elif abs(total_complete - 900) < abs(proposed_complete - 900):
                complete_winner = benchmarks[b]
                break
            else:
                complete_winner = benchmarks[b + 1]
                break

        for b in range(0, len(benchmarks) - 1):
            total_comprehensive += self.dosage_durations[benchmarks[b]].comprehensive_duration
            proposed_comprehensive = total_comprehensive + self.dosage_durations[benchmarks[b + 1]].comprehensive_duration
            if proposed_comprehensive < 1800:
                continue
            elif abs(total_comprehensive - 1800) < abs(proposed_comprehensive - 1000):
                comprehensive_winner = benchmarks[b]
                break
            else:
                comprehensive_winner = benchmarks[b + 1]
                break

        if efficient_winner is not None:  # if None, don't reduce
            for ex, a in assigned_exercises.items():
                if len(a.dosages) > 0:

                    if efficient_winner == 5.0:
                        for d in a.dosages:
                            if d.severity() < 4.5:
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif efficient_winner == 4.5:
                        for d in a.dosages:
                            if d.severity() < 3.5:
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif efficient_winner == 3.5:
                        for d in a.dosages:
                            if d.severity() < 2.5:
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif efficient_winner == 2.5:
                        for d in a.dosages:
                            if d.severity() < 1.5:
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif efficient_winner == 1.5:
                        for d in a.dosages:
                            if d.severity() < 0.5:
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif efficient_winner == 0.5:
                        pass

                    if complete_winner == 5.0:
                        for d in a.dosages:
                            if d.severity() < 4.5:
                                d.complete_reps_assigned = 0
                                d.complete_sets_assigned = 0
                    elif complete_winner == 4.5:
                        for d in a.dosages:
                            if d.severity() < 3.5:
                                d.complete_reps_assigned = 0
                                d.complete_sets_assigned = 0
                    elif complete_winner == 3.5:
                        for d in a.dosages:
                            if d.severity() < 2.5:
                                d.complete_reps_assigned = 0
                                d.complete_sets_assigned = 0
                    elif complete_winner == 2.5:
                        for d in a.dosages:
                            if d.severity() < 1.5:
                                d.complete_reps_assigned = 0
                                d.complete_sets_assigned = 0
                    elif complete_winner == 1.5:
                        for d in a.dosages:
                            if d.severity() < 0.5:
                                d.complete_reps_assigned = 0
                                d.complete_sets_assigned = 0
                    elif complete_winner == 0.5:
                        pass

                    if comprehensive_winner == 5.0:
                        for d in a.dosages:
                            if d.severity() < 4.5:
                                d.comprehensive_reps_assigned = 0
                                d.comprehensive_sets_assigned = 0
                    elif comprehensive_winner == 4.5:
                        for d in a.dosages:
                            if d.severity() < 3.5:
                                d.comprehensive_reps_assigned = 0
                                d.comprehensive_sets_assigned = 0
                    elif comprehensive_winner == 3.5:
                        for d in a.dosages:
                            if d.severity() < 2.5:
                                d.comprehensive_reps_assigned = 0
                                d.comprehensive_sets_assigned = 0
                    elif comprehensive_winner == 2.5:
                        for d in a.dosages:
                            if d.severity() < 1.5:
                                d.comprehensive_reps_assigned = 0
                                d.comprehensive_sets_assigned = 0
                    elif comprehensive_winner == 1.5:
                        for d in a.dosages:
                            if d.severity() < 0.5:
                                d.comprehensive_reps_assigned = 0
                                d.comprehensive_sets_assigned = 0
                    elif comprehensive_winner == 0.5:
                        pass

    def calc_dosage_durations(self, benchmark_value, assigned_exercise, dosage):
        if dosage.efficient_reps_assigned is not None and dosage.efficient_sets_assigned is not None:
            self.dosage_durations[benchmark_value].efficient_duration += assigned_exercise.duration(
                dosage.efficient_reps_assigned, dosage.efficient_sets_assigned)
        if dosage.complete_reps_assigned is not None and dosage.complete_sets_assigned is not None:
            self.dosage_durations[benchmark_value].complete_duration += assigned_exercise.duration(
                dosage.complete_reps_assigned, dosage.complete_sets_assigned)
        if dosage.comprehensive_reps_assigned is not None and dosage.comprehensive_sets_assigned is not None:
            self.dosage_durations[benchmark_value].comprehensive_duration += assigned_exercise.duration(
                dosage.comprehensive_reps_assigned, dosage.comprehensive_sets_assigned)

    @abc.abstractmethod
    def fill_exercises(self, soreness_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, sports):
        pass

    @staticmethod
    def update_dosage(dosage, exercise):

        if dosage.goal.goal_type == AthleteGoalType.sport or dosage.goal.goal_type == AthleteGoalType.preempt_sport:
            if dosage.priority == "1" or dosage.priority == "2":
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2
            else:
                dosage.efficient_reps_assigned = 0
                dosage.efficient_sets_assigned = 0
                dosage.complete_reps_assigned = 0
                dosage.complete_sets_assigned = 0
                dosage.comprehensive_reps_assigned = 0
                dosage.comprehensive_sets_assigned = 0

        elif dosage.goal.goal_type == AthleteGoalType.on_request:
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

        elif (dosage.goal.goal_type == AthleteGoalType.sore and
                (dosage.soreness_source.historic_soreness_status is None or
                 dosage.soreness_source.is_dormant_cleared() or
                dosage.soreness_source.historic_soreness_status is HistoricSorenessStatus.doms) or
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

        dosage.default_reps_assigned = exercise.min_reps
        dosage.default_sets_assigned = exercise.min_sets

        return dosage

    @staticmethod
    def rank_dosages(target_collections):
        for target_collection in target_collections:
            for ex in target_collection.values():
                ex.set_dosage_ranking()


class ActiveRest(ModalityBase):
    def __init__(self, event_date_time, force_data=False):
        super().__init__(event_date_time)
        #self.high_relative_load_session = high_relative_load_session
        #self.high_relative_intensity_logged = high_relative_intensity_logged
        #self.muscular_strain_high = muscular_strain_high
        self.force_data = force_data
        self.event_date_time = event_date_time
        self.inhibit_exercises = {}
        self.static_integrate_exercises = {}
        self.static_stretch_exercises = {}
        self.isolated_activate_exercises = {}

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

    def conditions_for_increased_sensitivity_met(self, soreness_list, muscular_strain_high):

        if muscular_strain_high:
            return True
        else:
            for s in soreness_list:
                if (s.first_reported_date_time is not None and
                        (s.is_persistent_soreness() or
                         s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness)):
                    days_sore = (self.event_date_time - s.first_reported_date_time).days
                    if not s.pain and days_sore < 30:
                        return True
        return False

    def fill_exercises(self, soreness_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, sports):

        if soreness_list is not None and len(soreness_list) > 0:
            for s in soreness_list:
                self.check_reactive_recover_from_sport(soreness_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, sports)
                self.check_reactive_care_soreness(s, exercise_library)
                self.check_reactive_care_pain(s, exercise_library)
                self.check_prevention_soreness(s, self.event_date_time, exercise_library)
                self.check_prevention_pain(s, self.event_date_time, exercise_library)
        else:
            if self.force_data:
                self.get_general_exercises(exercise_library)

    def get_general_exercises(self, exercise_library):

        pass

    def check_reactive_recover_from_sport(self, soreness_list, exercise_library, high_relative_load_session,
                                          high_relative_intensity_logged, sports):
        if high_relative_load_session or high_relative_intensity_logged:
            goal = AthleteGoal("Recover from Sport", 1, AthleteGoalType.sport)
            #goal.trigger = "High Relative Volume or Intensity of Logged Session"
            goal.trigger_type = TriggerType.high_volume_intensity  # 0

            body_part_factory = BodyPartFactory()

            for sport_name in sports:
                alert = Alert(goal)
                alert.sport_name = sport_name
                self.alerts.append(alert)
                body_part = body_part_factory.get_body_part_for_sport(sport_name)

                prohibiting_soreness = False

                high_severity_list = list(s for s in soreness_list if s.severity >= 3.5)

                if len(high_severity_list) > 0:
                    prohibiting_soreness = True

                # Note: this is just returning the primary mover related exercises for sport
                if body_part is not None and not prohibiting_soreness:
                    self.copy_exercises(body_part.inhibit_exercises,
                                        self.inhibit_exercises, goal, "1", None, exercise_library)
                    if not prohibiting_soreness:
                        self.copy_exercises(body_part.static_stretch_exercises,
                                            self.static_stretch_exercises, goal, "1", None, exercise_library, sport_name)
                        self.copy_exercises(body_part.isolated_activate_exercises,
                                            self.isolated_activate_exercises, goal, "1", None, exercise_library, sport_name)


class ActiveRestBeforeTraining(ActiveRest, Serialisable):
    def __init__(self, event_date_time, force_data=False):
        super().__init__(event_date_time, force_data)
        self.active_stretch_exercises = {}

    def json_serialise(self):
        ret = {
            #'high_relative_load_session': self.high_relative_load_session,
            #'high_relative_intensity_logged': self.high_relative_intensity_logged,
            #'muscular_strain_high': self.muscular_strain_high,
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
            'default_plan': self.default_plan,
            'alerts': [g.json_serialise() for g in self.alerts]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        pre_active_rest = cls(#high_relative_load_session=input_dict.get('high_relative_load_session', False),
                              #high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
                              #muscular_strain_high=input_dict.get('muscular_strain_high', False),
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
        pre_active_rest.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]

        return pre_active_rest

    '''deprecated
    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.active_stretch_minutes = self.calc_active_time(self.active_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_integrate_exercises)
    '''

    def aggregate_dosages(self):

        self.aggregate_dosage_by_severity_exercise_collection(self.inhibit_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.static_stretch_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.active_stretch_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.static_integrate_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.isolated_activate_exercises)

    def get_general_exercises(self, exercise_library):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_general()

        goal = AthleteGoal("On Request", 1, AthleteGoalType.on_request)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                    exercise_library)
                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                    None, exercise_library)
                self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1",
                                    None, exercise_library)
                self.copy_exercises(agonist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "1",
                                    None, exercise_library)

        '''
        for g in body_part.antagonists:
                antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                if antagonist is not None:
                    self.copy_exercises(antagonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                        exercise_library)
                    self.copy_exercises(antagonist.static_stretch_exercises, self.static_stretch_exercises, goal,
                                        "1", None, exercise_library)
                    self.copy_exercises(antagonist.active_stretch_exercises, self.active_stretch_exercises, goal,
                                        "1", None, exercise_library)
        '''

        for y in body_part.synergists:
            synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
            if synergist is not None:
                self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", None,
                                    exercise_library)
                self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal, "2",
                                        None, exercise_library)
                self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "2",
                                    None, exercise_library)

        for t in body_part.stabilizers:
            stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if stabilizer is not None:
                self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", None,
                                    exercise_library)
                self.copy_exercises(stabilizer.active_stretch_exercises, self.active_stretch_exercises, goal, "3",
                                        None, exercise_library)
                self.copy_exercises(stabilizer.isolated_activate_exercises, self.isolated_activate_exercises, goal, "3",
                                    None, exercise_library)

        self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, "1", None,
                            exercise_library)

    def check_reactive_care_soreness(self, soreness, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.daily and not soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = AthleteGoal("Care for Soreness", 1, AthleteGoalType.sore)
            #goal.trigger = "Sore reported today"
            goal.trigger_type = TriggerType.sore_today  # 10

            if body_part is not None:
                alert = Alert(goal)
                alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                self.alerts.append(alert)
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

        if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None \
                and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
            days_sore = (event_date_time - soreness.first_reported_date_time).days
            if not soreness.pain and days_sore > 30:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 2, AthleteGoalType.corrective)
                #goal.trigger = "Pers, Pers-2 Soreness > 30d"
                goal.trigger_type = TriggerType.hist_sore_greater_30  # 19

                if body_part is not None:
                    alert = Alert(goal)
                    alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                    self.alerts.append(alert)
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

        if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None:
            # days_sore = (event_date_time - soreness.first_reported_date_time).days
            if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 2, AthleteGoalType.corrective)
                #goal.trigger = "Acute, Pers, Pers-2 Pain"
                goal.trigger_type = TriggerType.hist_pain  # 16

                if body_part is not None:
                    alert = Alert(goal)
                    alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                    self.alerts.append(alert)
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

            if not soreness.is_joint():
                #goal.trigger = "Painful joint reported today"
                if soreness.severity < 3:
                    goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
                else:
                    goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
                synergist_priority = "1"
            else:
                #goal.trigger = "Painful muscle reported today"
                if soreness.severity < 3:
                    goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
                else:
                    goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
                synergist_priority = "2"
            if body_part is not None:
                alert = Alert(goal)
                alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                self.alerts.append(alert)
                for a in body_part.agonists:
                    agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                    if agonist is not None:
                        self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)
                            self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1", soreness, exercise_library)

                if soreness.is_joint():
                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            self.copy_exercises(antagonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(antagonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)
                                self.copy_exercises(antagonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1", soreness, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal,
                                            synergist_priority, soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal,
                                                synergist_priority, soreness, exercise_library)

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
    def __init__(self, event_date_time, force_data=False):
        super().__init__(event_date_time, force_data)

    def json_serialise(self):
        ret = {
            #'high_relative_load_session': self.high_relative_load_session,
            #'high_relative_intensity_logged': self.high_relative_intensity_logged,
            #'muscular_strain_high': self.muscular_strain_high,
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'default_plan': self.default_plan,
            'alerts': [g.json_serialise() for g in self.alerts]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        post_active_rest = cls(#high_relative_load_session=input_dict.get('high_relative_load_session', False),
                               #high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
                               #muscular_strain_high=input_dict.get('muscular_strain_high', False),
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
        post_active_rest.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]

        return post_active_rest

    '''deprecated
    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_integrate_exercises)
    '''

    def aggregate_dosages(self):

        self.aggregate_dosage_by_severity_exercise_collection(self.inhibit_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.static_stretch_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.static_integrate_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.isolated_activate_exercises)

    def get_general_exercises(self, exercise_library):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_general()

        goal = AthleteGoal("On Request", 1, AthleteGoalType.on_request)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                    exercise_library)
                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                    None, exercise_library)
                self.copy_exercises(agonist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "1",
                                   None, exercise_library)

        '''
        for g in body_part.antagonists:
                antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                if antagonist is not None:
                    self.copy_exercises(antagonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                        exercise_library)
                    self.copy_exercises(antagonist.static_stretch_exercises, self.static_stretch_exercises, goal,
                                        "1", None, exercise_library)
                    self.copy_exercises(antagonist.isolated_activate_exercises, self.isolated_activate_exercises, goal, 
                                        "1", None, exercise_library)
        '''

        for y in body_part.synergists:
            synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
            if synergist is not None:
                self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", None,
                                    exercise_library)
                self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, "2",
                                    None, exercise_library)
                self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "2",
                                    None, exercise_library)

        for t in body_part.stabilizers:
            stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if stabilizer is not None:
                self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", None,
                                    exercise_library)
                self.copy_exercises(stabilizer.static_stretch_exercises, self.static_stretch_exercises, goal, "3",
                                        None, exercise_library)
                self.copy_exercises(stabilizer.isolated_activate_exercises, self.isolated_activate_exercises, goal, "3",
                                    None, exercise_library)

        self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, "1", None,
                            exercise_library)

    def check_reactive_care_soreness(self, soreness, exercise_library):

        body_part_factory = BodyPartFactory()

        if soreness.daily and not soreness.pain:

            body_part = body_part_factory.get_body_part(soreness.body_part)

            goal = AthleteGoal("Care for Soreness", 1, AthleteGoalType.sore)
            #goal.trigger = "Sore reported today"
            goal.trigger_type = TriggerType.sore_today  # 10

            if body_part is not None:
                alert = Alert(goal)
                alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                self.alerts.append(alert)
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

        if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None \
                and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
            days_sore = (event_date_time - soreness.first_reported_date_time).days
            if not soreness.pain and days_sore > 30:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 2, AthleteGoalType.corrective)
                #goal.trigger = "Pers, Pers-2 Soreness > 30d"
                goal.trigger_type = TriggerType.hist_sore_greater_30  # 19

                if body_part is not None:
                    alert = Alert(goal)
                    alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                    self.alerts.append(alert)
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

        if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None:
            # days_sore = (event_date_time - soreness.first_reported_date_time).days
            if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                goal = AthleteGoal("Prevention", 2, AthleteGoalType.corrective)
                #goal.trigger = "Acute, Pers, Pers-2 Pain"
                goal.trigger_type = TriggerType.hist_pain  # 16

                if body_part is not None:
                    alert = Alert(goal)
                    alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                    self.alerts.append(alert)
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

            if soreness.is_joint():
                #goal.trigger = "Painful joint reported today"
                if soreness.severity < 3:
                    goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
                else:
                    goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
                synergist_priority = "1"
            else:
                #goal.trigger = "Painful muscle reported today"
                if soreness.severity < 3:
                    goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
                else:
                    goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
                synergist_priority = "2"

            if body_part is not None:
                alert = Alert(goal)
                alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                self.alerts.append(alert)
                for a in body_part.agonists:
                    agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                    if agonist is not None:
                        self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", soreness, exercise_library)

                if soreness.is_joint():
                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            self.copy_exercises(antagonist.inhibit_exercises, self.inhibit_exercises, goal, "1", soreness,
                                                exercise_library)
                            if soreness.severity < 3.5:
                                self.copy_exercises(antagonist.static_stretch_exercises, self.static_stretch_exercises,
                                                    goal, "1", soreness, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, synergist_priority, soreness, exercise_library)
                        if soreness.severity < 3.5:
                            self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, synergist_priority, soreness, exercise_library)

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

    def fill_exercises(self, soreness_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, sports):
        for s in soreness_list:
            self.check_corrective_soreness(s, self.event_date_time, exercise_library)
            self.check_preempt_soreness(s, self.event_date_time, exercise_library)

    def check_preempt_soreness(self, soreness, event_date_time, exercise_library):

        if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None\
                and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
            days_sore = (event_date_time - soreness.first_reported_date_time).days
            if not soreness.pain and days_sore < 30:

                goal = AthleteGoal("Personalized Prepare for Training", 1, AthleteGoalType.preempt_personalized_sport)
                #goal.trigger = "Pers, Pers-2 Soreness > 30d"
                goal.trigger_type = TriggerType.hist_sore_greater_30

                self.assign_exercises(soreness, goal, exercise_library)

    def check_corrective_soreness(self, soreness, event_date_time, exercise_library):

        if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None \
                and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
            days_sore = (event_date_time - soreness.first_reported_date_time).days
            if soreness.pain or days_sore > 30:
                goal = AthleteGoal("Personalized Prepare for Training (Identified Dysfunction)", 1, AthleteGoalType.preempt_corrective)
                #goal.trigger = "Pers, Pers-2 Soreness > 30d"
                goal.trigger_type = TriggerType.hist_sore_greater_30

                self.assign_exercises(soreness, goal, exercise_library)

    def assign_exercises(self, soreness, goal, exercise_library):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part(soreness.body_part)

        if body_part is not None:
            alert = Alert(goal)
            alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
            self.alerts.append(alert)
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
    def __init__(self, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, event_date_time):
        super().__init__(event_date_time)
        #self.sport_name = sport_name
        self.high_relative_volume_logged = high_relative_load_session
        self.high_relative_intensity_logged = high_relative_intensity_logged
        self.muscular_strain_high = muscular_strain_high
        self.dynamic_stretch_exercises = {}
        self.dynamic_integrate_exercises = {}

    def json_serialise(self):
        ret = {
            #'sport_name': self.sport_name.value,
            'high_relative_load_session': self.high_relative_volume_logged,
            'high_relative_intensity_logged': self.high_relative_intensity_logged,
            'muscular_strain_high': self.muscular_strain_high,
            'dynamic_stretch_exercises': [p.json_serialise() for p in self.dynamic_stretch_exercises.values()],
            'dynamic_integrate_exercises': [p.json_serialise() for p in self.dynamic_integrate_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        cooldown = cls(#sport_name=input_dict.get('sport_name', 0),
                       high_relative_load_session=input_dict.get('high_relative_load_session', False),
                       high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
                       muscular_strain_high=input_dict.get('muscular_strain_high', False),
                       event_date_time=input_dict.get('event_date_time', None))
        cooldown.dynamic_stretch_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in input_dict['dynamic_stretch_exercises']}
        cooldown.dynamic_integrate_exercises = {s['library_id']: AssignedExercise.json_deserialise(s) for s in
                                                        input_dict['dynamic_integrate_exercises']}
        cooldown.start_date_time = input_dict.get('start_date_time', None)
        cooldown.completed_date_time = input_dict.get('completed_date_time', None)
        cooldown.completed = input_dict.get('completed', False)
        cooldown.active = input_dict.get('active', True)
        cooldown.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]

        return cooldown

    def aggregate_dosages(self):

        self.aggregate_dosage_by_severity_exercise_collection(self.dynamic_stretch_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.dynamic_integrate_exercises)

    def conditions_for_increased_sensitivity_met(self, soreness_list, muscular_strain_high):

        if self.muscular_strain_high:
            return True
        else:
            for s in soreness_list:
                if (s.first_reported_date_time is not None and
                        (s.is_persistent_soreness() or
                         s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness)):
                    days_sore = (self.event_date_time - s.first_reported_date_time).days
                    if (not s.pain and days_sore < 30) or s.pain:
                        return True
        return False

    def set_exercise_dosage_ranking(self):
        self.rank_dosages([self.dynamic_stretch_exercises])
        self.rank_dosages([self.dynamic_integrate_exercises])

    def check_recover_from_sport(self, soreness_list, sport_name, exercise_library):

        if self.high_relative_volume_logged or self.high_relative_intensity_logged:
            goal = AthleteGoal("Recover from Sport", 1, AthleteGoalType.sport)
            #goal.trigger = "High Relative Volume or Intensity of Logged Session"
            goal.trigger_type = TriggerType.high_volume_intensity  # 0
            alert = Alert(goal)
            alert.sport_name = sport_name
            self.alerts.append(alert)

            body_part_factory = BodyPartFactory()

            body_part = body_part_factory.get_body_part_for_sport(sport_name)

            prohibiting_soreness = False

            high_severity_list = list(s for s in soreness_list if s.severity >= 3.5)

            if len(high_severity_list) > 0:
                prohibiting_soreness = True

            # Note: this is just returning the primary mover related exercises for sport
            if body_part is not None and not prohibiting_soreness:
                self.copy_exercises(body_part.dynamic_stretch_exercises,
                                    self.dynamic_stretch_exercises, goal, "1", None, exercise_library, sport_name)
                self.copy_exercises(body_part.dynamic_integrate_exercises,
                                    self.dynamic_integrate_exercises, goal, "1", None, exercise_library, sport_name)

    def check_corrective(self, soreness, event_date_time, exercise_library):

        if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None\
                and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
            days_sore = (event_date_time - soreness.first_reported_date_time).days
            if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:
                goal = AthleteGoal("Personalized Prepare for Training (Identified Dysfunction)", 1, AthleteGoalType.preempt_corrective)
                goal.trigger_type = TriggerType.hist_sore_greater_30
                self.assign_exercises(soreness, goal, exercise_library)

            elif (soreness.is_persistent_soreness() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness and days_sore > 30):
                goal = AthleteGoal("Personalized Prepare for Training (Identified Dysfunction)", 1, AthleteGoalType.preempt_corrective)
                #goal.trigger = "Pers, Pers-2 Soreness > 30d or Historic Pain"
                goal.trigger_type = TriggerType.hist_pain

                self.assign_exercises(soreness, goal, exercise_library)

    def fill_exercises(self, soreness_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, sports):

        for sport_name in sports:
            self.check_recover_from_sport(soreness_list, sport_name, exercise_library)
        for s in soreness_list:
            self.check_corrective(s, self.event_date_time, exercise_library)

    def assign_exercises(self, soreness, goal, exercise_library):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part(soreness.body_part)

        if body_part is not None:
            alert = Alert(goal)
            alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
            self.alerts.append(alert)
            for a in body_part.agonists:
                agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                if agonist is not None:
                    if soreness.severity < 3.5:
                        self.copy_exercises(agonist.dynamic_stretch_exercises, self.dynamic_stretch_exercises, goal,
                                            "1", soreness,
                                            exercise_library)
                        self.copy_exercises(agonist.dynamic_integrate_exercises, self.dynamic_integrate_exercises, goal,
                                            "1", soreness,
                                            exercise_library)

            for y in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                if synergist is not None:
                    self.copy_exercises(synergist.dynamic_stretch_exercises, self.dynamic_stretch_exercises, goal, "2",
                                        soreness,
                                        exercise_library)
                    self.copy_exercises(synergist.dynamic_integrate_exercises, self.dynamic_integrate_exercises, goal, "2",
                                        soreness,
                                        exercise_library)


class IceSession(Serialisable):
    def __init__(self, minutes=0):
        self.minutes = minutes
        self.start_date_time = None
        self.completed_date_time = None
        self.event_date_time = None
        self.completed = False
        self.active = True
        self.body_parts = []
        self.alerts = []

    def json_serialise(self):

        ret = {
            'minutes': self.minutes,
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'body_parts': [ice.json_serialise() for ice in self.body_parts],
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        ice_session = cls(input_dict.get('minutes', 0))
        ice_session.start_date_time = input_dict.get('start_date_time', None)
        ice_session.completed_date_time = input_dict.get('completed_date_time', None)
        ice_session.event_date_time = input_dict.get('event_date_time', None)
        ice_session.completed = input_dict.get('completed', False)
        ice_session.active = input_dict.get('active', True)
        ice_session.body_parts = [Ice.json_deserialise(body_part) for body_part in input_dict.get('body_parts', [])]
        ice_session.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
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
    def __init__(self, body_part_location=None, side=0):
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

    def __eq__(self, other):
        return self.body_part_location == other.body_part_location and self.side == other.side

    @classmethod
    def json_deserialise(cls, input_dict):
        ice = cls(body_part_location=BodyPartLocation(input_dict['body_part_location']),
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
        self.alerts = []

    def json_serialise(self):
        ret = {
            'minutes': self.minutes,
            'after_training': self.after_training,
            'goals': [goal.json_serialise() for goal in self.goals],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(self.completed_date_time) if self.completed_date_time is not None else None,
            'event_date_time': format_datetime(self.event_date_time) if self.event_date_time is not None else None,
            'completed': self.completed,
            'active': self.active,
            'alerts': [alert.json_serialise() for alert in self.alerts]
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
        cold_water_immersion.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]

        return cold_water_immersion

    def __setattr__(self, name, value):
        if name in ['event_date_time', 'start_date_time', 'completed_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)
