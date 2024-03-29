from serialisable import Serialisable
from models.soreness import Soreness, Alert
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation, BodyPartSide
from models.exercise import AssignedExercise
from models.goal import AthleteGoalType, AthleteGoal
from models.trigger import TriggerType
from models.dosage import ExerciseDosage
from models.body_parts import BodyPartFactory, BodyPart
from models.sport import SportName
from models.movement_errors import MovementErrorType, MovementError, MovementErrorFactory
from utils import parse_datetime, format_datetime
import abc
import datetime


class ModalityGoal(Serialisable):
    def __init__(self):
        self.efficient_active = False
        self.complete_active = False
        self.comprehensive_active = False

    def json_serialise(self):
        ret = {
            'efficient_active': self.efficient_active,
            'complete_active': self.complete_active,
            'comprehensive_active': self.comprehensive_active
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        goal = cls()
        goal.efficient_active = input_dict.get('efficient_active', False)
        goal.complete_active = input_dict.get('complete_active', False)
        goal.comprehensive_active = input_dict.get('comprehensive_active', False)
        return goal


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
        self.default_plan = ""
        self.alerts = []
        self.dosage_durations = {}
        self.initialize_dosage_durations()
        self.efficient_winner = 1
        self.complete_winner = 1
        self.comprehensive_winner = 1
        self.goals = {}

    def get_total_exercises(self):
        pass

    def initialize_dosage_durations(self):

        self.dosage_durations[1] = DosageDuration(0, 0, 0)
        self.dosage_durations[2] = DosageDuration(0, 0, 0)
        self.dosage_durations[3] = DosageDuration(0, 0, 0)
        self.dosage_durations[4] = DosageDuration(0, 0, 0)
        self.dosage_durations[5] = DosageDuration(0, 0, 0)

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

    def reconcile_default_plan_with_active_time(self):

        efficient_duration = self.dosage_durations[self.efficient_winner].efficient_duration

        complete_duration = self.dosage_durations[self.complete_winner].complete_duration

        if complete_duration == 0 and self.default_plan == "Complete":
            self.reactivate_complete_goals()
        elif efficient_duration == 0 and complete_duration == 0:
            self.reactivate_complete_goals()
            self.default_plan = "Complete"

    def add_goals(self, dosages):

        for dosage in dosages:
            if dosage.goal.goal_type not in self.goals:
                self.goals[dosage.goal.goal_type] = ModalityGoal()

    def update_goals(self, dosage):

        if dosage.goal.goal_type not in self.goals:
            self.goals[dosage.goal.goal_type] = ModalityGoal()

        # self.goals[dosage.goal.goal_type].efficient_active = False
        # self.goals[dosage.goal.goal_type].complete_active = False
        # self.goals[dosage.goal.goal_type].comprehensive_active = False

        if dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0:
            self.goals[dosage.goal.goal_type].efficient_active = True
        if dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0:
            self.goals[dosage.goal.goal_type].complete_active = True
        if dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0:
            self.goals[dosage.goal.goal_type].comprehensive_active = True

    def set_plan_dosage(self, soreness_list, muscular_strain_high):

        care_for_pain_present = False
        pain_reported_today = False
        soreness_historic_status_present = False
        soreness_reported_today = False
        severity_greater_than_2 = False

        for s in soreness_list:
            if s.pain and (s.historic_soreness_status is None or s.is_dormant_cleared()) and s.severity > 1:
                care_for_pain_present = True
            if s.pain:
                pain_reported_today = True
            if not s.pain and s.daily:
                soreness_reported_today = True
            if (not s.pain and s.historic_soreness_status is not None and not s.is_dormant_cleared() and
                    s.historic_soreness_status is not HistoricSorenessStatus.doms):
                soreness_historic_status_present = True
            if s.severity >= 2:
                severity_greater_than_2 = True

        increased_sensitivity = self.conditions_for_increased_sensitivity_met(soreness_list, muscular_strain_high)

        if care_for_pain_present:
            self.default_plan = "Comprehensive"
        elif not severity_greater_than_2 and not pain_reported_today and not soreness_historic_status_present and soreness_reported_today:
            if not increased_sensitivity:
                self.default_plan = "Efficient"
            else:
                self.default_plan = "Complete"
        else:
            if not increased_sensitivity:
                self.default_plan = "Complete"
            else:
                self.default_plan = "Comprehensive"

    def copy_exercises(self, source_collection, target_collection, goal, priority, trigger, exercise_library, sports=[]):

        position_order = 0

        for s in source_collection:

            if s.exercise.id not in target_collection:
                target_collection[s.exercise.id] = AssignedExercise(library_id=str(s.exercise.id))
                exercise_list = [ex for ex in exercise_library if ex.id == str(s.exercise.id)]
                target_collection[s.exercise.id].exercise = exercise_list[0]
                target_collection[s.exercise.id].equipment_required = target_collection[s.exercise.id].exercise.equipment_required
                target_collection[s.exercise.id].position_order = position_order

            dosage = ExerciseDosage()
            dosage.priority = priority
            dosage.soreness_source = trigger
            dosage.sports = sports
            dosage.goal = goal
            dosage = self.update_dosage(dosage, target_collection[s.exercise.id].exercise)
            target_collection[s.exercise.id].dosages.append(dosage)
            position_order += 1

    def aggregate_dosages(self):
        pass

    def reactivate_complete_goals(self):
        pass

    def reactivate_complete_corrective_goals_by_collection(self, assigned_exercises):

        for ex, a in assigned_exercises.items():
            for d in a.dosages:
                if d.goal.goal_type == AthleteGoalType.corrective:
                    d.complete_reps_assigned = d.default_complete_reps_assigned
                    d.complete_sets_assigned = d.default_complete_sets_assigned
                    self.update_goals(d)

    def aggregate_dosage_by_severity_exercise_collection(self, assigned_exercises):

        for ex, a in assigned_exercises.items():
            if len(a.dosages) > 0:
                a.dosages = sorted(a.dosages, key=lambda x: (3-int(x.priority), x.severity(),
                                                             x.default_comprehensive_sets_assigned,
                                                             x.default_comprehensive_reps_assigned,
                                                             x.default_complete_sets_assigned,
                                                             x.default_complete_reps_assigned,
                                                             x.default_efficient_sets_assigned,
                                                             x.default_efficient_reps_assigned), reverse=True)

                self.add_goals(a.dosages)
                dosage = a.dosages[0]
                self.update_goals(dosage)

                if dosage.priority == "1":
                    self.calc_dosage_durations(1, a, dosage)
                elif dosage.priority == "2" and dosage.severity() > 2:
                    self.calc_dosage_durations(2, a, dosage)
                elif dosage.priority == "2" and dosage.severity() <= 2:
                    self.calc_dosage_durations(3, a, dosage)
                elif dosage.priority == "3" and dosage.severity() > 2:
                    self.calc_dosage_durations(4, a, dosage)
                elif dosage.priority == "3" and dosage.severity() <= 2:
                    self.calc_dosage_durations(5, a, dosage)

                '''dep
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
                '''

    def set_winners(self):

        # key off efficient as the guide
        total_efficient = 0
        total_complete = 0
        total_comprehensive = 0
        benchmarks = [1, 2, 3, 4, 5]

        for b in range(0, len(benchmarks) - 1):
            total_efficient += self.dosage_durations[benchmarks[b]].efficient_duration
            proposed_efficient = total_efficient + self.dosage_durations[benchmarks[b + 1]].efficient_duration
            if proposed_efficient < 720:
                continue
            elif abs(total_efficient - 720) < abs(proposed_efficient - 720):
                self.efficient_winner = benchmarks[b]
                break
            else:
                self.efficient_winner = benchmarks[b + 1]
                break

        '''later
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
                
        '''

    def scale_all_active_time(self):
        pass

    def scale_active_time(self, assigned_exercises):

        if self.efficient_winner is not None:  # if None, don't reduce
            for ex, a in assigned_exercises.items():
                if len(a.dosages) > 0:

                    if self.efficient_winner == 1:
                        for d in a.dosages:
                            if d.priority != '1':
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 2:
                        for d in a.dosages:
                            if d.priority == '3' or (d.priority == '2' and d.severity() <= 2):
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 3:
                        for d in a.dosages:
                            if d.priority == '3':
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 4:
                        for d in a.dosages:
                            if d.priority == '3' and d.severity() <= 2:
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 5:
                        pass
                    elif self.efficient_winner == 0:
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
    def fill_exercises(self, trigger_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, sports):
        pass

    @staticmethod
    def update_dosage(dosage, exercise):

        if dosage.goal.goal_type == AthleteGoalType.high_load or dosage.goal.goal_type == AthleteGoalType.preempt_sport:
            if dosage.priority == "1" or dosage.priority == "2":
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2
                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 2

        elif dosage.goal.goal_type == AthleteGoalType.asymmetric_session or dosage.goal.goal_type == AthleteGoalType.asymmetric_pattern:
            if dosage.priority == "1":
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1

            if dosage.priority == "1" or dosage.priority == "2":
                dosage.complete_reps_assigned = exercise.min_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.min_reps
                dosage.default_complete_sets_assigned = 1

            dosage.comprehensive_reps_assigned = exercise.min_reps
            dosage.comprehensive_sets_assigned = 1
            dosage.default_comprehensive_reps_assigned = exercise.min_reps
            dosage.default_comprehensive_sets_assigned = 1

        elif dosage.goal.goal_type == AthleteGoalType.on_request:
            if dosage.priority == "1":
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1

            if dosage.priority == "1" or dosage.priority == "2":
                dosage.complete_reps_assigned = exercise.min_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.min_reps
                dosage.default_complete_sets_assigned = 1

            dosage.comprehensive_reps_assigned = exercise.min_reps
            dosage.comprehensive_sets_assigned = 1
            dosage.default_comprehensive_reps_assigned = exercise.min_reps
            dosage.default_comprehensive_sets_assigned = 1

        elif dosage.goal.goal_type == AthleteGoalType.corrective:  # table 2 corrective

            if dosage.soreness_source.severity < 0.5:

                if dosage.priority == "1":
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                    dosage.comprehensive_reps_assigned = exercise.max_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.max_reps
                    dosage.default_comprehensive_sets_assigned = 1

            elif 0.5 <= dosage.soreness_source.severity < 1.5:

                if dosage.priority == "1":
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                    dosage.comprehensive_reps_assigned = exercise.max_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.max_reps
                    dosage.default_comprehensive_sets_assigned = 1

            elif 1.5 <= dosage.soreness_source.severity < 2.5:

                if dosage.priority == "1":
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1
                    dosage.comprehensive_reps_assigned = exercise.max_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.max_reps
                    dosage.default_comprehensive_sets_assigned = 1

            #trial
            elif 2.5 <= dosage.soreness_source.severity <= 5.0:
                dosage.default_efficient_reps_assigned = 0
                dosage.default_efficient_sets_assigned = 0
                dosage.default_complete_reps_assigned = 0
                dosage.default_complete_sets_assigned = 0
                dosage.comprehensive_reps_assigned = 0
                dosage.comprehensive_sets_assigned = 0
                dosage.default_comprehensive_reps_assigned = 0
                dosage.default_comprehensive_sets_assigned = 0

            '''trial
            elif 2.5 <= dosage.soreness_source.severity < 3.5:

                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 2

            elif 3.5 <= dosage.soreness_source.severity < 4.5:

                dosage.default_efficient_reps_assigned = exercise.max_reps
                dosage.default_efficient_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 3

            elif dosage.soreness_source.severity >= 4.5:

                dosage.default_efficient_reps_assigned = exercise.max_reps
                dosage.default_efficient_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 3
            '''

        elif (dosage.goal.goal_type == AthleteGoalType.sore and
                (dosage.soreness_source.historic_soreness_status is None or
                 dosage.soreness_source.is_dormant_cleared() or
                dosage.soreness_source.historic_soreness_status is HistoricSorenessStatus.doms) or
                #dosage.goal.goal_type == AthleteGoalType.preempt_personalized_sport or
              dosage.goal.goal_type == AthleteGoalType.preempt_corrective):  # table 1
            if dosage.soreness_source.severity < 0.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                    # trial to reduce active time
                    dosage.comprehensive_reps_assigned = exercise.min_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.min_reps
                    dosage.default_comprehensive_sets_assigned = 1
            elif 0.5 <= dosage.soreness_source.severity < 1.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                    # trial to reduce active time
                    dosage.comprehensive_reps_assigned = exercise.max_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.max_reps
                    dosage.default_comprehensive_sets_assigned = 1
            elif 1.5 <= dosage.soreness_source.severity < 2.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1
                #trial
                dosage.comprehensive_reps_assigned = exercise.min_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.min_reps
                dosage.default_comprehensive_sets_assigned = 1
            elif 2.5 <= dosage.soreness_source.severity < 3.5:
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                #trial
                dosage.complete_reps_assigned = exercise.min_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.min_reps
                dosage.default_complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 1
            elif 3.5 <= dosage.soreness_source.severity < 4.5:
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2
                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 2
            elif dosage.soreness_source.severity >= 4.5:
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3
                dosage.default_efficient_reps_assigned = exercise.max_reps
                dosage.default_efficient_sets_assigned = 1

                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 2
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 3

        else:  # table 2
            if dosage.soreness_source.severity < 0.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1

                    # trial
                    dosage.comprehensive_reps_assigned = exercise.max_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.max_reps
                    dosage.default_comprehensive_sets_assigned = 1
            elif 0.5 <= dosage.soreness_source.severity < 1.5:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.min_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.min_reps
                    dosage.default_complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 1
            elif 1.5 <= dosage.soreness_source.severity < 2.5:
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                dosage.complete_reps_assigned = exercise.min_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.min_reps
                dosage.default_complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 1

            elif 2.5 <= dosage.soreness_source.severity < 3.5:

                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 2
                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 2
            elif 3.5 <= dosage.soreness_source.severity < 4.5:
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3
                dosage.default_efficient_reps_assigned = exercise.max_reps
                dosage.default_efficient_sets_assigned = 1

                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 2
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 3
            elif dosage.soreness_source.severity >= 4.5:
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 2
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 3
                dosage.default_efficient_reps_assigned = exercise.max_reps
                dosage.default_efficient_sets_assigned = 1

                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 2
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 3

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
    def check_reactive_care_soreness(self, trigger, exercise_library, max_severity):
        pass

    @abc.abstractmethod
    def check_reactive_care_pain(self, trigger, exercise_library, max_severity):
        pass

    @abc.abstractmethod
    def check_corrective_soreness(self, trigger, event_date_time, exercise_library, max_severity):
        pass

    @abc.abstractmethod
    def check_corrective_pain(self, trigger, event_date_time, exercise_library, max_severity):
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
                    if days_sore < 30:
                        return True
        return False

    def fill_exercises(self, trigger_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, sports):

        max_severity = 0
        checked_recover_from_sport = False

        if trigger_list is not None:
            max_severity_list = list(t.severity for t in trigger_list if t.severity is not None)
            if len(max_severity_list) > 0:
                max_severity = max(max_severity_list)

        if self.force_data:
            self.get_general_exercises(exercise_library, max_severity)

        if trigger_list is not None and len(trigger_list) > 0:
            self.check_reactive_recover_from_sport(trigger_list, exercise_library, high_relative_load_session,
                                                   high_relative_intensity_logged,
                                                   muscular_strain_high,
                                                   sports, max_severity)
            checked_recover_from_sport = True
            for t in trigger_list:
                self.check_reactive_care_soreness(t, exercise_library, max_severity)
                self.check_reactive_care_pain(t, exercise_library, max_severity)
                # if max_severity < 3:
                self.check_corrective_soreness(t, self.event_date_time, exercise_library, max_severity)
                self.check_corrective_pain(t, self.event_date_time, exercise_library, max_severity)

        self.check_reactive_three_sensor(trigger_list, exercise_library)

        if ((high_relative_load_session or high_relative_intensity_logged or muscular_strain_high)
                and not checked_recover_from_sport):
            self.check_reactive_recover_from_sport(trigger_list, exercise_library, high_relative_load_session,
                                                   high_relative_intensity_logged,
                                                   muscular_strain_high,
                                                   sports, max_severity)

    def get_general_exercises(self, exercise_library, max_severity):

        pass

    def check_reactive_recover_from_sport_general(self, sports, exercise_library, goal, max_severity):

        pass

    def check_reactive_three_sensor(self, trigger_list, exercise_library):

        pass

    def check_reactive_recover_from_sport(self, trigger_list, exercise_library, high_relative_load_session,
                                          high_relative_intensity_logged, muscular_strain_high, sports, max_severity):
        # if muscular_strain_high:
        #     goal = AthleteGoal(None, 1, AthleteGoalType.sport)
        #     goal.trigger_type = TriggerType.overreaching_high_muscular_strain  # 8
        #     alert = Alert(goal)
        #     self.alerts.append(alert)

        # hist_soreness = list(s for s in soreness_list if not s.is_dormant_cleared() and not s.pain and
        #                      (s.is_persistent_soreness() or
        #                       s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
        #                      (self.event_date_time - s.first_reported_date_time).days < 30)

        # if len(hist_soreness) > 0:
        #     goal = AthleteGoal(None, 1, AthleteGoalType.sport)
        #     goal.trigger_type = TriggerType.hist_sore_less_30  # 7
        #     for soreness in hist_soreness:
        #         alert = Alert(goal)
        #         alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
        #         self.alerts.append(alert)

        for t in range(0, len(trigger_list)):
            #if trigger_list[t].trigger_type == TriggerType.hist_sore_less_30:  # 7
            #    goal = AthleteGoal(None, 1, AthleteGoalType.sport)
                #trigger_list[t].goals.append(goal)
            #elif trigger_list[t].trigger_type == TriggerType.overreaching_high_muscular_strain:  # 8
            #    goal = AthleteGoal(None, 1, AthleteGoalType.sport)
                #trigger_list[t].goals.append(goal)
            if trigger_list[t].trigger_type == TriggerType.high_volume_intensity:  # 0
                goal = AthleteGoal("High Load", 1, AthleteGoalType.high_load)
                #trigger_list[t].goals.append(goal)
                body_part_factory = BodyPartFactory()

        # if high_relative_load_session or high_relative_intensity_logged:
        #     goal = AthleteGoal("Expedite tissue regeneration", 1, AthleteGoalType.sport)
        #     goal.trigger_type = TriggerType.high_volume_intensity  # 0
        #
        #     body_part_factory = BodyPartFactory()
        #
        #     for sport_name in sports:
        #         alert = Alert(goal)
        #         alert.sport_name = sport_name
        #         self.alerts.append(alert)
                body_part = body_part_factory.get_body_part_for_sports(sports)

                # Note: this is just returning the primary mover related exercises for sport
                if body_part is not None: #and not prohibiting_soreness:
                    self.copy_exercises(body_part.inhibit_exercises,
                                        self.inhibit_exercises, goal, "1", trigger_list[t], exercise_library)
                    #if not prohibiting_soreness:
                    if max_severity < 3.5:
                        self.copy_exercises(body_part.static_stretch_exercises,
                                            self.static_stretch_exercises, goal, "1", trigger_list[t], exercise_library, sports)
                    if max_severity < 2.5:
                        self.copy_exercises(body_part.isolated_activate_exercises,
                                        self.isolated_activate_exercises, goal, "1", trigger_list[t], exercise_library, sports)

                self.check_reactive_recover_from_sport_general(sports, exercise_library, goal, max_severity)


class ActiveRestBeforeTraining(ActiveRest, Serialisable):
    def __init__(self, event_date_time, force_data=False):
        super().__init__(event_date_time, force_data)
        self.active_stretch_exercises = {}


    def get_total_exercises(self):
        return len(self.inhibit_exercises) +\
               len(self.static_stretch_exercises) +\
               len(self.active_stretch_exercises) +\
               len(self.isolated_activate_exercises) +\
               len(self.static_integrate_exercises)

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
            'alerts': [g.json_serialise() for g in self.alerts],
            'goals': {str(goal_type.value): goal.json_serialise() for (goal_type, goal) in self.goals.items()},
            'force_data': self.force_data
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        pre_active_rest = cls(#high_relative_load_session=input_dict.get('high_relative_load_session', False),
                              #high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
                              #muscular_strain_high=input_dict.get('muscular_strain_high', False),
                              event_date_time=input_dict.get('event_date_time', None),
                              force_data=input_dict.get('force_data', False))
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
        pre_active_rest.default_plan = input_dict.get('default_plan', 'Complete')
        pre_active_rest.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
        pre_active_rest.goals = {AthleteGoalType(int(goal_type)): ModalityGoal.json_deserialise(goal) for (goal_type, goal) in input_dict.get('goals', {}).items()}

        return pre_active_rest

    '''deprecated
    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.active_stretch_minutes = self.calc_active_time(self.active_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_integrate_exercises)
    '''

    def scale_all_active_time(self):

        self.scale_active_time(self.inhibit_exercises)
        self.scale_active_time(self.static_stretch_exercises)
        self.scale_active_time(self.active_stretch_exercises)
        self.scale_active_time(self.static_integrate_exercises)
        self.scale_active_time(self.isolated_activate_exercises)

    def aggregate_dosages(self):

        self.aggregate_dosage_by_severity_exercise_collection(self.inhibit_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.static_stretch_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.active_stretch_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.static_integrate_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.isolated_activate_exercises)

    def reactivate_complete_goals(self):

        self.reactivate_complete_corrective_goals_by_collection(self.inhibit_exercises)
        self.reactivate_complete_corrective_goals_by_collection(self.static_stretch_exercises)
        self.reactivate_complete_corrective_goals_by_collection(self.active_stretch_exercises)
        self.reactivate_complete_corrective_goals_by_collection(self.static_integrate_exercises)
        self.reactivate_complete_corrective_goals_by_collection(self.isolated_activate_exercises)

    def check_reactive_three_sensor(self, trigger_list, exercise_library):

        if trigger_list is not None:
            for t in trigger_list:
                if TriggerType.movement_error_apt_asymmetry == t.trigger_type or TriggerType.movement_error_historic_apt_asymmetry == t.trigger_type:
                    if TriggerType.movement_error_historic_apt_asymmetry == t.trigger_type:
                        goal = AthleteGoal("Core Instability", 1, AthleteGoalType.asymmetric_pattern)
                    else:
                        goal = AthleteGoal("Asymmetric Stress", 1, AthleteGoalType.asymmetric_session)
                    factory = MovementErrorFactory()
                    movement_error = factory.get_movement_error(MovementErrorType.apt_asymmetry, None)

                    body_part_factory = BodyPartFactory()

                    for o1 in movement_error.overactive_tight_first:
                        body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(o1), None))

                        self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1",
                                            None, exercise_library)

                        self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal,
                                            "1",
                                            None, exercise_library)

                    for o2 in movement_error.overactive_tight_second:
                        body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(o2), None))

                        self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "2",
                                            None, exercise_library)

                        self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal,
                                            "2",
                                            None, exercise_library)

                    for e in movement_error.elevated_stress:
                        body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(e), None))

                        self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "3",
                                            None, exercise_library)

                        self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal,
                                            "3",
                                            None, exercise_library)

                    if TriggerType.movement_error_historic_apt_asymmetry == t.trigger_type:
                        for e in movement_error.underactive_weak:
                            body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(e), None))

                            self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises,
                                                goal, "1",
                                                None, exercise_library)

                        self.copy_exercises(movement_error.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", None, exercise_library)

    def check_reactive_recover_from_sport_general(self, sports, exercise_library, goal, max_severity):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part_for_sports(sports)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                    exercise_library)
                #self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                #                    None, exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1",
                                        None, exercise_library)

        if max_severity < 2.5:
            for t in body_part.antagonists:
                antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                if antagonist is not None:
                    self.copy_exercises(antagonist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "1",
                                        None, exercise_library)

        if max_severity < 2.5:
            self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, "1", None,
                                exercise_library)

    def get_general_exercises(self, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_general()

        goal = AthleteGoal("Improve mobility", 1, AthleteGoalType.on_request)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                    exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                        None, exercise_library)
                    self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1",
                                        None, exercise_library)
                if max_severity < 2.5:
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
                if max_severity < 3.5:
                    self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal, "2",
                                            None, exercise_library)
                if max_severity < 2.5:
                    self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "2",
                                    None, exercise_library)

        for t in body_part.stabilizers:
            stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if stabilizer is not None:
                self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", None,
                                    exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(stabilizer.active_stretch_exercises, self.active_stretch_exercises, goal, "3",
                                            None, exercise_library)
                if max_severity < 2.5:
                    self.copy_exercises(stabilizer.isolated_activate_exercises, self.isolated_activate_exercises, goal, "3",
                                    None, exercise_library)

        if max_severity < 2.5:
                self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, "1", None,
                        exercise_library)

    def check_reactive_care_soreness(self, trigger, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        #if soreness.daily and not soreness.pain:
        if trigger.trigger_type in [TriggerType.sore_today,
                                    TriggerType.sore_today_doms,
                                    TriggerType.hist_sore_less_30_sore_today,
                                    TriggerType.hist_sore_greater_30_sore_today]:  # 10, 11, 12, 13

            body_part = body_part_factory.get_body_part(trigger.body_part)

            goal = AthleteGoal("Soreness", 1, AthleteGoalType.sore)

            # if soreness.historic_soreness_status == HistoricSorenessStatus.doms:
            #     goal.trigger_type = TriggerType.sore_today_doms  # 11
            # elif ((soreness.is_persistent_soreness() or
            #        soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
            #       (self.event_date_time - soreness.first_reported_date_time).days < 30):
            #     goal.trigger_type = TriggerType.hist_sore_less_30_sore_today  # 12
            # elif ((soreness.is_persistent_soreness() or
            #        soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
            #       (self.event_date_time - soreness.first_reported_date_time).days >= 30):
            #     goal.trigger_type = TriggerType.hist_sore_greater_30_sore_today  # 13
            # else: # somehow missed doms
            #     goal.trigger_type = TriggerType.sore_today  # 10

            if body_part is not None:
                # alert = Alert(goal)
                # alert.body_part = trigger.body_part
                # self.alerts.append(alert)

                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)
                    self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, "1", trigger, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", trigger, exercise_library)
                        if max_severity < 3.5:
                            self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal, "2", trigger,
                                                exercise_library)

                for t in body_part.stabilizers:
                    stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                    if stabilizer is not None:
                        self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", trigger, exercise_library)
                        if max_severity < 3.5:
                            self.copy_exercises(stabilizer.active_stretch_exercises, self.active_stretch_exercises, goal, "3", trigger,
                                                exercise_library)

    def check_corrective_soreness(self, trigger, event_date_time, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()
        #
        # if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None \
        #         and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
        #     days_sore = (event_date_time - soreness.first_reported_date_time).days
        #     if not soreness.pain and days_sore >= 30:
        #
        #         body_part = body_part_factory.get_body_part(soreness.body_part)
        #
        #         goal = AthleteGoal("Reduce injury risk factors", 2, AthleteGoalType.corrective)
        #         #goal.trigger = "Pers, Pers-2 Soreness > 30d"
        #         goal.trigger_type = TriggerType.hist_sore_greater_30  # 19
        #
        if trigger.trigger_type == TriggerType.hist_sore_greater_30: # 19

            body_part = body_part_factory.get_body_part(trigger.body_part)
            goal = AthleteGoal("Chronic Imbalances", 2, AthleteGoalType.corrective)

            if body_part is not None:
                # alert = Alert(goal)
                # alert.body_part = trigger.body_part
                # self.alerts.append(alert)
                if max_severity < 2.5:
                    self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)

                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", trigger, exercise_library)
                            self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", trigger, exercise_library)

                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            self.copy_exercises(antagonist.isolated_activate_exercises,
                                                    self.isolated_activate_exercises, goal,
                                                    "1", trigger, exercise_library)

                    general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                    self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", trigger, exercise_library)

    def check_corrective_pain(self, trigger, event_date_time, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        # if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None:
        #     # days_sore = (event_date_time - soreness.first_reported_date_time).days
        #     if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:
        #
        #         body_part = body_part_factory.get_body_part(soreness.body_part)
        #
        #         goal = AthleteGoal("Reduce injury risk factors", 2, AthleteGoalType.corrective)
        #         #goal.trigger = "Acute, Pers, Pers-2 Pain"
        #         goal.trigger_type = TriggerType.hist_pain  # 16
        if trigger.trigger_type == TriggerType.hist_pain:  # 16
            body_part = body_part_factory.get_body_part(trigger.body_part)
            goal = AthleteGoal("Chronic Imbalances", 2, AthleteGoalType.corrective)

            if body_part is not None:
                # alert = Alert(goal)
                # alert.body_part = trigger.body_part
                # self.alerts.append(alert)
                if max_severity < 2.5:
                    self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)

                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", trigger, exercise_library)
                            self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", trigger, exercise_library)

                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            self.copy_exercises(antagonist.isolated_activate_exercises,
                                                    self.isolated_activate_exercises, goal,
                                                    "1", trigger, exercise_library)

                    general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                    self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", trigger, exercise_library)

    def check_reactive_care_pain(self, trigger, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()
        synergist_priority = "2"

        # if soreness.daily and soreness.pain:
        #
        #     body_part = body_part_factory.get_body_part(soreness.body_part)
        #
        #     goal = AthleteGoal("Care for pain", 1, AthleteGoalType.pain)
        #
        #     if not soreness.is_joint():
        #         #goal.trigger = "Painful joint reported today"
        #         if soreness.severity < 3:
        #             if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
        #                     soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
        #                 goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
        #             else:
        #                 goal.trigger_type = TriggerType.hist_pain_pain_today_severity_1_2  # 23
        #         else:
        #             if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
        #                     soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
        #                 goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
        #             else:
        #                 goal.trigger_type = TriggerType.hist_pain_pain_today_severity_3_5  # 24
        #         synergist_priority = "2"
        #     else:
        #         #goal.trigger = "Painful muscle reported today"
        #         if soreness.severity < 3:
        #             if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
        #                     soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
        #                 goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
        #             else:
        #                 goal.trigger_type = TriggerType.hist_pain_pain_today_severity_1_2  # 23
        #         else:
        #             if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
        #                     soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
        #                 goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
        #             else:
        #                 goal.trigger_type = TriggerType.hist_pain_pain_today_severity_3_5  # 24
        #         synergist_priority = "2"

        if trigger.trigger_type in [TriggerType.no_hist_pain_pain_today_severity_1_2,
                                    TriggerType.no_hist_pain_pain_today_high_severity_3_5,
                                    TriggerType.hist_pain_pain_today_severity_1_2,
                                    TriggerType.hist_pain_pain_today_severity_3_5]:  # 14, 15, 23, 24

            body_part = body_part_factory.get_body_part(trigger.body_part)

            goal = AthleteGoal("Pain", 1, AthleteGoalType.pain)
            if body_part is not None:
                # alert = Alert(goal)
                # alert.body_part = trigger.body_part
                # self.alerts.append(alert)
                if body_part_factory.is_joint(body_part):
                    for a in body_part.agonists:
                        agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                        if agonist is not None:
                            self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                            if max_severity < 3.5:
                                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)
                                self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1", trigger, exercise_library)
                else:
                    self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger,
                                        exercise_library)
                    if max_severity < 3.5:
                        self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                            trigger, exercise_library)
                        self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, "1",
                                            trigger, exercise_library)

                if body_part_factory.is_joint(body_part):
                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            self.copy_exercises(antagonist.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                            if max_severity < 3.5:
                                self.copy_exercises(antagonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)
                                self.copy_exercises(antagonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1", trigger, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal,
                                            synergist_priority, trigger, exercise_library)
                        if max_severity < 3.5:
                            self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal,
                                                synergist_priority, trigger, exercise_library)

                for t in body_part.stabilizers:
                    stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                    if stabilizer is not None:
                        self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", trigger, exercise_library)
                        if max_severity < 3.5:
                            self.copy_exercises(stabilizer.active_stretch_exercises, self.active_stretch_exercises, goal, "3", trigger,
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

    def get_total_exercises(self):
        return len(self.inhibit_exercises) +\
               len(self.static_stretch_exercises) +\
               len(self.isolated_activate_exercises) +\
               len(self.static_integrate_exercises)

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
            'alerts': [g.json_serialise() for g in self.alerts],
            'goals': {str(goal_type.value): goal.json_serialise() for (goal_type, goal) in self.goals.items()},
            'force_data': self.force_data
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        post_active_rest = cls(#high_relative_load_session=input_dict.get('high_relative_load_session', False),
                               #high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
                               #muscular_strain_high=input_dict.get('muscular_strain_high', False),
                               event_date_time=input_dict.get('event_date_time', None),
                               force_data=input_dict.get('force_data', False))
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
        post_active_rest.default_plan = input_dict.get('default_plan', 'Complete')
        post_active_rest.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
        post_active_rest.goals = {AthleteGoalType(int(goal_type)): ModalityGoal.json_deserialise(goal) for (goal_type, goal) in input_dict.get('goals', {}).items()}

        return post_active_rest

    '''deprecated
    def calc_durations(self):

        self.inhibit_minutes = self.calc_active_time(self.inhibit_exercises)
        self.static_stretch_minutes = self.calc_active_time(self.static_stretch_exercises)
        self.isolated_activate_minutes = self.calc_active_time(self.isolated_activate_exercises)
        self.static_integrate_minutes = self.calc_active_time(self.static_integrate_exercises)
    '''

    def scale_all_active_time(self):

        self.scale_active_time(self.inhibit_exercises)
        self.scale_active_time(self.static_stretch_exercises)
        self.scale_active_time(self.static_integrate_exercises)
        self.scale_active_time(self.isolated_activate_exercises)

    def aggregate_dosages(self):

        self.aggregate_dosage_by_severity_exercise_collection(self.inhibit_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.static_stretch_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.static_integrate_exercises)
        self.aggregate_dosage_by_severity_exercise_collection(self.isolated_activate_exercises)

    def reactivate_complete_goals(self):

        self.reactivate_complete_corrective_goals_by_collection(self.inhibit_exercises)
        self.reactivate_complete_corrective_goals_by_collection(self.static_stretch_exercises)
        self.reactivate_complete_corrective_goals_by_collection(self.static_integrate_exercises)
        self.reactivate_complete_corrective_goals_by_collection(self.isolated_activate_exercises)

    def check_reactive_three_sensor(self, trigger_list, exercise_library):

        if trigger_list is not None:

            for t in trigger_list:
                if TriggerType.movement_error_apt_asymmetry == t.trigger_type or TriggerType.movement_error_historic_apt_asymmetry == t.trigger_type:
                    if TriggerType.movement_error_historic_apt_asymmetry == t.trigger_type:
                        goal = AthleteGoal("Core Instability", 1, AthleteGoalType.asymmetric_pattern)
                    else:
                        goal = AthleteGoal("Asymmetric Stress", 1, AthleteGoalType.asymmetric_session)
                    factory = MovementErrorFactory()
                    movement_error = factory.get_movement_error(MovementErrorType.apt_asymmetry, None)

                    body_part_factory = BodyPartFactory()

                    for o1 in movement_error.overactive_tight_first:
                        body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(o1), None))

                        self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1",
                                            None, exercise_library)

                        self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                            None, exercise_library)

                    for o2 in movement_error.overactive_tight_second:
                        body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(o2), None))

                        self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "2",
                                            None, exercise_library)

                        self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "2",
                                            None, exercise_library)

                    for e in movement_error.elevated_stress:
                        body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(e), None))

                        self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "3",
                                            None, exercise_library)

                        self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "3",
                                            None, exercise_library)

                    if TriggerType.movement_error_historic_apt_asymmetry == t.trigger_type:
                        for e in movement_error.underactive_weak:
                            body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(e), None))

                            self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal, "1",
                                                None, exercise_library)

                        self.copy_exercises(movement_error.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", None, exercise_library)


    def check_reactive_recover_from_sport_general(self, sports, exercise_library, goal, max_severity):

        goal = AthleteGoal("High Load", 1, AthleteGoalType.high_load)
        # goal.trigger = "High Relative Volume or Intensity of Logged Session"

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part_for_sports(sports)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                if max_severity < 3.5:
                    self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                        exercise_library)
                    self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                        None, exercise_library)

        for t in body_part.antagonists:
            antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if antagonist is not None:
                if max_severity < 2.5:
                    self.copy_exercises(antagonist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "1",
                                        None, exercise_library)

        if max_severity < 2.5:
            self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, "1", None,
                                exercise_library)

    def get_general_exercises(self, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_general()

        goal = AthleteGoal("Improve mobility", 1, AthleteGoalType.on_request)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                    exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                        None, exercise_library)
                if max_severity < 2.5:
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
                if max_severity < 3.5:
                    self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, "2",
                                        None, exercise_library)
                if max_severity < 2.5:
                    self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises, goal, "2",
                                        None, exercise_library)

        for t in body_part.stabilizers:
            stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if stabilizer is not None:
                self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", None,
                                    exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(stabilizer.static_stretch_exercises, self.static_stretch_exercises, goal, "3",
                                            None, exercise_library)
                if max_severity < 2.5:
                    self.copy_exercises(stabilizer.isolated_activate_exercises, self.isolated_activate_exercises, goal, "3",
                                        None, exercise_library)

        if max_severity < 2.5:
            self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, "1", None,
                                exercise_library)

    def check_reactive_care_soreness(self, trigger, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        # if soreness.daily and not soreness.pain:
        #
        #     body_part = body_part_factory.get_body_part(soreness.body_part)
        #
        #     goal = AthleteGoal("Care for soreness", 1, AthleteGoalType.sore)
        #     #goal.trigger = "Sore reported today"
        #     #goal.trigger_type = TriggerType.sore_today  # 10
        #     if soreness.historic_soreness_status == HistoricSorenessStatus.doms:
        #         goal.trigger_type = TriggerType.sore_today_doms  # 11
        #     elif ((soreness.is_persistent_soreness() or
        #            soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
        #           (self.event_date_time - soreness.first_reported_date_time).days < 30):
        #         goal.trigger_type = TriggerType.hist_sore_less_30_sore_today  # 12
        #     elif ((soreness.is_persistent_soreness() or
        #            soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
        #           (self.event_date_time - soreness.first_reported_date_time).days >= 30):
        #         goal.trigger_type = TriggerType.hist_sore_greater_30_sore_today  # 13
        #     else: # somehow missed doms
        #         goal.trigger_type = TriggerType.sore_today  # 10
        if trigger.trigger_type in [TriggerType.sore_today,
                                    TriggerType.sore_today_doms,
                                    TriggerType.hist_sore_less_30_sore_today,
                                    TriggerType.hist_sore_greater_30_sore_today]:

            body_part = body_part_factory.get_body_part(trigger.body_part)
            goal = AthleteGoal("Soreness", 1, AthleteGoalType.sore)

            if body_part is not None:
                # alert = Alert(goal)
                # alert.body_part = trigger.body_part
                # self.alerts.append(alert)

                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", trigger, exercise_library)
                        if max_severity < 3.5:
                            self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, "2", trigger, exercise_library)

                for t in body_part.stabilizers:
                    stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                    if stabilizer is not None:
                        self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", trigger, exercise_library)
                        if max_severity < 3.5:
                            self.copy_exercises(stabilizer.static_stretch_exercises, self.static_stretch_exercises, goal, "3", trigger, exercise_library)

    def check_corrective_soreness(self, trigger, event_date_time, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        # if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None \
        #         and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
        #     days_sore = (event_date_time - soreness.first_reported_date_time).days
        #     if not soreness.pain and days_sore >= 30:
        #
        #         body_part = body_part_factory.get_body_part(soreness.body_part)
        #
        #         goal = AthleteGoal("Reduce injury risk factors", 2, AthleteGoalType.corrective)
        #         #goal.trigger = "Pers, Pers-2 Soreness > 30d"
        #         goal.trigger_type = TriggerType.hist_sore_greater_30  # 19
        if trigger.trigger_type == TriggerType.hist_sore_greater_30:  # 19
            body_part = body_part_factory.get_body_part(trigger.body_part)
            goal = AthleteGoal("Chronic Imbalances", 2, AthleteGoalType.corrective)

            if body_part is not None:
                # alert = Alert(goal)
                # alert.body_part = trigger.body_part
                # self.alerts.append(alert)
                if max_severity < 2.5:

                    self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)

                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", trigger, exercise_library)
                            self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", trigger, exercise_library)

                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            self.copy_exercises(antagonist.isolated_activate_exercises,
                                                    self.isolated_activate_exercises, goal,
                                                    "1", trigger, exercise_library)

                    general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                    self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", trigger, exercise_library)

    def check_corrective_pain(self, trigger, event_date_time, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        # if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None:
        #     # days_sore = (event_date_time - soreness.first_reported_date_time).days
        #     if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:
        #
        #         body_part = body_part_factory.get_body_part(soreness.body_part)
        #
        #         goal = AthleteGoal("Reduce injury risk factors", 2, AthleteGoalType.corrective)
        #         #goal.trigger = "Acute, Pers, Pers-2 Pain"
        #         goal.trigger_type = TriggerType.hist_pain  # 16
        if trigger.trigger_type == TriggerType.hist_pain:  # 16
            body_part = body_part_factory.get_body_part(trigger.body_part)
            goal = AthleteGoal("Chronic Imbalances", 2, AthleteGoalType.corrective)

            if body_part is not None:
                # alert = Alert(goal)
                # alert.body_part = trigger.body_part
                # self.alerts.append(alert)
                if max_severity < 2.5:

                    self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)

                    for y in body_part.synergists:
                        synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                        if synergist is not None:
                            self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", trigger, exercise_library)
                            self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                                    goal, "2", trigger, exercise_library)

                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            self.copy_exercises(antagonist.isolated_activate_exercises,
                                                    self.isolated_activate_exercises, goal,
                                                    "1", trigger, exercise_library)

                    general_body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation.general, None))
                    self.copy_exercises(general_body_part.static_integrate_exercises, self.static_integrate_exercises,
                                            goal, "1", trigger, exercise_library)

    def check_reactive_care_pain(self, trigger, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        #if soreness.daily and soreness.pain:
        if trigger.trigger_type in [TriggerType.no_hist_pain_pain_today_severity_1_2,
                                    TriggerType.no_hist_pain_pain_today_high_severity_3_5,
                                    TriggerType.hist_pain_pain_today_severity_1_2,
                                    TriggerType.hist_pain_pain_today_severity_3_5]:  # 14, 15, 23, 24

            body_part = body_part_factory.get_body_part(trigger.body_part)

            goal = AthleteGoal("Pain", 1, AthleteGoalType.pain)

            synergist_priority = "2"

            # if not soreness.is_joint():
            #     #goal.trigger = "Painful joint reported today"
            #     if soreness.severity < 3:
            #         if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
            #                 soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
            #             goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
            #         else:
            #             goal.trigger_type = TriggerType.hist_pain_pain_today_severity_1_2  # 23
            #     else:
            #         if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
            #                 soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
            #             goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
            #         else:
            #             goal.trigger_type = TriggerType.hist_pain_pain_today_severity_3_5  # 24
            #     synergist_priority = "2"
            # else:
            #     #goal.trigger = "Painful muscle reported today"
            #     if soreness.severity < 3:
            #         if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
            #                 soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
            #             goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
            #         else:
            #             goal.trigger_type = TriggerType.hist_pain_pain_today_severity_1_2  # 23
            #     else:
            #         if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
            #                 soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
            #             goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
            #         else:
            #             goal.trigger_type = TriggerType.hist_pain_pain_today_severity_3_5  # 24
            #     synergist_priority = "2"

            if body_part is not None:
                # alert = Alert(goal)
                # alert.body_part = trigger.body_part
                # self.alerts.append(alert)

                if body_part_factory.is_joint(body_part):
                    for a in body_part.agonists:
                        agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                        if agonist is not None:
                            self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger, exercise_library)
                            if max_severity < 3.5:
                                self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1", trigger, exercise_library)
                else:
                    self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger,
                                        exercise_library)
                    if max_severity < 3.5:
                        self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                            trigger, exercise_library)

                if body_part_factory.is_joint(body_part):
                    for g in body_part.antagonists:
                        antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(g), None))
                        if antagonist is not None:
                            self.copy_exercises(antagonist.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger,
                                                exercise_library)
                            if max_severity < 3.5:
                                self.copy_exercises(antagonist.static_stretch_exercises, self.static_stretch_exercises,
                                                    goal, "1", trigger, exercise_library)

                for y in body_part.synergists:
                    synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                    if synergist is not None:
                        self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, synergist_priority, trigger, exercise_library)
                        if max_severity < 3.5:
                            self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, synergist_priority, trigger, exercise_library)

                for t in body_part.stabilizers:
                    stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                    if stabilizer is not None:
                        self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, "3", trigger, exercise_library)
                        if max_severity < 3.5:
                            self.copy_exercises(stabilizer.static_stretch_exercises, self.static_stretch_exercises, goal, "3", trigger, exercise_library)

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

    def get_total_exercises(self):
        return len(self.inhibit_exercises) +\
               len(self.static_stretch_exercises) +\
               len(self.active_or_dynamic_stretch_exercises) +\
               len(self.isolated_activate_exercises) +\
               len(self.dynamic_integrate_exercises) +\
               len(self.dynamic_integrate_with_speed_exercises)


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

    def fill_exercises(self, trigger_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, sports):

        if trigger_list is not None:
            for t in trigger_list:
                self.check_corrective_soreness(t, self.event_date_time, exercise_library)
                self.check_preempt_soreness(t, self.event_date_time, exercise_library)

    def check_preempt_soreness(self, trigger, event_date_time, exercise_library):

        # if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None\
        #         and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
        #     days_sore = (event_date_time - soreness.first_reported_date_time).days
        #     if not soreness.pain and days_sore < 30:
        if trigger.trigger_type == TriggerType.hist_sore_less_30:
            goal = AthleteGoal("Prep for Sport", 1, AthleteGoalType.preempt_personalized_sport)
            #goal.trigger = "Pers, Pers-2 Soreness > 30d"
            #goal.trigger_type = TriggerType.hist_sore_less_30
            #trigger.goals.append(goal)
            self.assign_exercises(trigger, goal, exercise_library)

    def check_corrective_soreness(self, trigger, event_date_time, exercise_library):

        # if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None \
        #         and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
        #     days_sore = (event_date_time - soreness.first_reported_date_time).days
        #     if not soreness.pain and days_sore >= 30:
        if trigger.trigger_type == TriggerType.hist_sore_greater_30:
            goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
            #goal.trigger = "Pers, Pers-2 Soreness > 30d"
            #goal.trigger_type = TriggerType.hist_sore_greater_30
            #trigger.goals.append(goal)
            self.assign_exercises(trigger, goal, exercise_library)

    def assign_exercises(self, trigger, goal, exercise_library):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part(trigger.body_part)

        if body_part is not None:
            # alert = Alert(goal)
            # alert.body_part = trigger.body_part
            # self.alerts.append(alert)
            for a in body_part.agonists:
                agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
                if agonist is not None:
                    self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", trigger,
                                        exercise_library)
                    if trigger.severity < 3.5:
                        self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                                            trigger, exercise_library)
                        self.copy_exercises(agonist.isolated_activate_exercises, self.isolated_activate_exercises,
                                            goal, "1", trigger, exercise_library)
                        self.copy_exercises(agonist.active_or_dynamic_stretch_exercises,
                                            self.active_or_dynamic_stretch_exercises,
                                            goal, "1", trigger, exercise_library)
            for y in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                if synergist is not None:
                    self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, "2", trigger,
                                        exercise_library)
                    if trigger.severity < 3.5:
                        self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises,
                                            goal, "2", trigger, exercise_library)
                        self.copy_exercises(synergist.active_or_dynamic_stretch_exercises,
                                            self.active_or_dynamic_stretch_exercises,
                                            goal, "2", trigger, exercise_library)

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

    def get_total_exercises(self):
        return len(self.dynamic_integrate_exercises) +\
               len(self.dynamic_stretch_exercises)

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
            'alerts': [alert.json_serialise() for alert in self.alerts],
            'goals': {str(goal_type.value): goal.json_serialise() for (goal_type, goal) in self.goals.items()},
            'default_plan': self.default_plan
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
        cooldown.goals = {AthleteGoalType(int(goal_type)): ModalityGoal.json_deserialise(goal) for (goal_type, goal) in input_dict.get('goals', {}).items()}
        cooldown.default_plan = input_dict.get('default_plan', 'Complete')

        return cooldown

    def scale_all_active_time(self):

        self.scale_active_time(self.dynamic_stretch_exercises)
        self.scale_active_time(self.dynamic_integrate_exercises)

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
                    if days_sore < 30:
                        return True
        return False

    def set_exercise_dosage_ranking(self):
        self.rank_dosages([self.dynamic_stretch_exercises])
        self.rank_dosages([self.dynamic_integrate_exercises])

    def check_recover_from_sport(self, trigger_list, sports, muscular_strain_high,exercise_library, max_severity):

        # if muscular_strain_high:
        #     goal = AthleteGoal(None, 1, AthleteGoalType.sport)
        #     goal.trigger_type = TriggerType.overreaching_high_muscular_strain  # 8
        #     alert = Alert(goal)
        #     self.alerts.append(alert)

        for t in range(0, len(trigger_list)):
            #if trigger_list[t].trigger_type == TriggerType.overreaching_high_muscular_strain:  # 8
            #    goal = AthleteGoal(None, 1, AthleteGoalType.sport)
            #    trigger_list[t].goals.append(goal)
            #elif trigger_list[t].trigger_type == TriggerType.hist_sore_less_30:  # 7
            #    goal = AthleteGoal(None, 1, AthleteGoalType.sport)
            #    trigger_list[t].goals.append(goal)

        # hist_soreness = list(s for s in soreness_list if not s.is_dormant_cleared() and not s.pain and
        #                      (s.is_persistent_soreness() or
        #                       s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
        #                      (self.event_date_time - s.first_reported_date_time).days < 30)
        #
        # if len(hist_soreness) > 0:
        #     goal = AthleteGoal(None, 1, AthleteGoalType.sport)
        #     goal.trigger_type = TriggerType.hist_sore_less_30  # 7
        #     # if sport_name is not None:
        #     for soreness in hist_soreness:
        #         #for sport_name in sports:
        #         alert = Alert(goal)
        #         #alert.sport_name = sport_name
        #         alert.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
        #         self.alerts.append(alert)

            if trigger_list[t].trigger_type == TriggerType.high_volume_intensity and max_severity < 2.5:  # 0
                goal = AthleteGoal("High Load", 1, AthleteGoalType.high_load)
                #trigger_list[t].goals.append(goal)

        # if max_severity < 2.5:  # note this is only a pain value for cooldown
        #     if self.high_relative_volume_logged or self.high_relative_intensity_logged:
        #         goal = AthleteGoal("Expedite tissue regeneration", 1, AthleteGoalType.sport)
        #         #goal.trigger = "High Relative Volume or Intensity of Logged Session"
        #         goal.trigger_type = TriggerType.high_volume_intensity  # 0
        #         for sport_name in sports:
        #             alert = Alert(goal)
        #             alert.sport_name = sport_name
        #             self.alerts.append(alert)

                body_part_factory = BodyPartFactory()

                body_part = body_part_factory.get_body_part_for_sports(sports)

                # Note: this is just returning the primary mover related exercises for sport
                if body_part is not None and max_severity < 3.5:
                    self.copy_exercises(body_part.dynamic_stretch_exercises,
                                        self.dynamic_stretch_exercises, goal, "1", None, exercise_library, sports)
                    self.copy_exercises(body_part.dynamic_integrate_exercises,
                                        self.dynamic_integrate_exercises, goal, "1", None, exercise_library, sports)

    # def check_corrective(self, trigger, event_date_time, exercise_library):
    #
    #     # if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None\
    #     #         and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:
    #     #     days_sore = (event_date_time - soreness.first_reported_date_time).days
    #     #     if soreness.is_acute_pain() or soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:
    #         if trigger.trigger_type == TriggerType.hist_pain:
    #             goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
    #             #goal.trigger_type = TriggerType.hist_pain
    #             #trigger.goals.append(goal)
    #             self.assign_exercises(trigger, goal, exercise_library)
    #
    #         #elif (soreness.is_persistent_soreness() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness and days_sore >= 30):
    #         elif trigger.trigger_type == TriggerType.hist_sore_greater_30:
    #             goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
    #             #goal.trigger_type = TriggerType.hist_sore_greater_30
    #             #trigger.goals.append(goal)
    #
    #             self.assign_exercises(trigger, goal, exercise_library)

    def fill_exercises(self, trigger_list, exercise_library, high_relative_load_session, high_relative_intensity_logged, muscular_strain_high, sports):

        max_severity = 0

        if trigger_list is not None:
            max_severity_list = list(t for t in trigger_list if t.severity is not None)
            if len(max_severity_list) > 0:
                pain_list = list(t for t in max_severity_list if t.pain)
                if len(pain_list) > 0:
                    max_severity = max(list(s.severity for s in pain_list))

        #for sport_name in sports:
        self.check_recover_from_sport(trigger_list, sports, muscular_strain_high, exercise_library, max_severity)
        # dynamic stretch not ready yet
        #for s in soreness_list:
        #    self.check_corrective(s, self.event_date_time, exercise_library)

    def assign_exercises(self, trigger, goal, exercise_library):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part(trigger.body_part)

        if body_part is not None:
            # alert = Alert(goal)
            # alert.body_part = trigger.body_part
            # self.alerts.append(alert)

            if trigger.severity < 3.5:
                self.copy_exercises(body_part.dynamic_stretch_exercises, self.dynamic_stretch_exercises, goal,
                                    "1", trigger,
                                    exercise_library)
                self.copy_exercises(body_part.dynamic_integrate_exercises, self.dynamic_integrate_exercises, goal,
                                    "1", trigger,
                                    exercise_library)

            for y in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(y), None))
                if synergist is not None:
                    self.copy_exercises(synergist.dynamic_stretch_exercises, self.dynamic_stretch_exercises, goal, "2",
                                        trigger,
                                        exercise_library)
                    self.copy_exercises(synergist.dynamic_integrate_exercises, self.dynamic_integrate_exercises, goal, "2",
                                        trigger,
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
