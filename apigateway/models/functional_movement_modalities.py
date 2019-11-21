from serialisable import Serialisable
from models.soreness import Soreness, Alert
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation, BodyPartSide
from models.exercise import AssignedExercise
from models.goal import AthleteGoalType, AthleteGoal
from models.trigger import TriggerType
from models.dosage import ExerciseDosage, DosageProgression
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
            'completed_date_time': format_datetime(
                self.completed_date_time) if self.completed_date_time is not None else None,
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
    def __init__(self, event_date_time, relative_load_level=3):
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
        self.relative_load_level = relative_load_level
        self.goals = {}
        self.rankings = set()

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

    def get_dosage_rank_and_progression(self, goal, severity, tier):

        if goal.goal_type == AthleteGoalType.pain or goal.goal_type == AthleteGoalType.sore:
            if 7 <= severity:
                if tier == 1:
                    return 1, DosageProgression.mod_max_super_max
                else:
                    return 2, DosageProgression.mod_max_super_max
            elif 4 <= severity < 7:
                if tier == 1:
                    return 1, DosageProgression.mod_max_super_max
                else:
                    return 2, DosageProgression.mod_max_super_max
            else:
                if tier == 1:
                    return 2, DosageProgression.min_mod_max
                else:
                    return 3, DosageProgression.min_mod_max

        elif goal.goal_type == AthleteGoalType.high_load:
            if tier == 1:
                return 1, DosageProgression.min_mod_max
            elif tier == 2:
                return 2, DosageProgression.min_mod_max
            elif tier == 3:
                return 3, DosageProgression.min_mod_max
            else:
                return 0, None

        elif goal.goal_type == AthleteGoalType.asymmetric_session or goal.goal_type == AthleteGoalType.on_request:
            if tier == 1:
                return 1, DosageProgression.min_mod_max
            elif tier == 2:
                return 2, DosageProgression.min_mod_max
            elif tier == 3:
                return 3, DosageProgression.min_mod_max
            else:
                return 0, None

        elif goal.goal_type == AthleteGoalType.corrective:
            if tier == 1:
                return 2, DosageProgression.min_mod_max
            elif tier == 2:
                return 3, DosageProgression.min_mod_max
            else:
                return 0, None
        else:
            return 0, None

    def add_goals(self, dosages):

        for dosage in dosages:
            if dosage.goal.goal_type not in self.goals:
                if ((dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0) or
                        (dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0) or
                        (dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0)):
                    self.goals[dosage.goal.goal_type] = ModalityGoal()

    def update_goals(self, dosage):

        if dosage.goal.goal_type not in self.goals:
            if ((dosage.efficient_reps_assigned > 0 and dosage.efficient_sets_assigned > 0) or
                    (dosage.complete_reps_assigned > 0 and dosage.complete_sets_assigned > 0) or
                    (dosage.comprehensive_reps_assigned > 0 and dosage.comprehensive_sets_assigned > 0)):
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

    def set_plan_dosage(self):

        # care_for_pain_present = False
        # pain_reported_today = False
        # soreness_historic_status_present = False
        # soreness_reported_today = False
        # severity_greater_than_2 = False
        #
        # for s in soreness_list:
        #     if s.pain and (s.historic_soreness_status is None or s.is_dormant_cleared()) and s.severity > 1:
        #         care_for_pain_present = True
        #     if s.pain:
        #         pain_reported_today = True
        #     if not s.pain and s.daily:
        #         soreness_reported_today = True
        #     if (not s.pain and s.historic_soreness_status is not None and not s.is_dormant_cleared() and
        #             s.historic_soreness_status is not HistoricSorenessStatus.doms):
        #         soreness_historic_status_present = True
        #     if s.severity >= 2:
        #         severity_greater_than_2 = True
        #
        # increased_sensitivity = self.conditions_for_increased_sensitivity_met(soreness_list, muscular_strain_high)
        #
        # if care_for_pain_present:
        #     self.default_plan = "Comprehensive"
        # elif not severity_greater_than_2 and not pain_reported_today and not soreness_historic_status_present and soreness_reported_today:
        #     if not increased_sensitivity:
        #         self.default_plan = "Efficient"
        #     else:
        #         self.default_plan = "Complete"
        # else:
        #     if not increased_sensitivity:
        #         self.default_plan = "Complete"
        #     else:
        #         self.default_plan = "Comprehensive"
        self.default_plan = "Complete"

    def copy_exercises(self, source_collection, target_collection, goal, tier, severity, exercise_library,
                       sports=[]):

        position_order = 0

        for s in source_collection:

            if s.exercise.id not in target_collection:
                target_collection[s.exercise.id] = AssignedExercise(library_id=str(s.exercise.id))
                exercise_list = [ex for ex in exercise_library if ex.id == str(s.exercise.id)]
                target_collection[s.exercise.id].exercise = exercise_list[0]
                target_collection[s.exercise.id].equipment_required = target_collection[
                    s.exercise.id].exercise.equipment_required
                target_collection[s.exercise.id].position_order = position_order

            ranking, progression = self.get_dosage_rank_and_progression(goal, severity, tier)

            if ranking > 0:
                self.rankings.add(ranking)
            dosage = ExerciseDosage()
            dosage.dosage_progression = progression
            dosage.tier = tier
            dosage.last_severity = severity
            dosage.ranking = ranking
            dosage.sports = sports
            dosage.goal = goal
            #dosage = self.update_dosage(dosage, target_collection[s.exercise.id].exercise)
            #if dosage.get_total_dosage() > 0:
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
                # a.dosages = sorted(a.dosages, key=lambda x: (3 - int(x.priority), x.severity(),
                #                                              x.default_comprehensive_sets_assigned,
                #                                              x.default_comprehensive_reps_assigned,
                #                                              x.default_complete_sets_assigned,
                #                                              x.default_complete_reps_assigned,
                #                                              x.default_efficient_sets_assigned,
                #                                              x.default_efficient_reps_assigned), reverse=True)

                a.dosages = sorted(a.dosages, key=lambda x: (3 - int(x.priority),
                                                             x.default_efficient_sets_assigned,
                                                             x.default_efficient_reps_assigned,
                                                             x.default_complete_sets_assigned,
                                                             x.default_complete_reps_assigned,
                                                             x.default_comprehensive_sets_assigned,
                                                             x.default_comprehensive_reps_assigned), reverse=True)

                self.add_goals(a.dosages)
                dosage = a.dosages[0]
                for goal_dosage in a.dosages:
                    self.update_goals(goal_dosage)

                if dosage.priority == "1":
                    self.calc_dosage_durations(1, a, dosage)
                elif dosage.priority == "2" and dosage.severity() > 4:
                    self.calc_dosage_durations(2, a, dosage)
                elif dosage.priority == "2" and dosage.severity() <= 4:
                    self.calc_dosage_durations(3, a, dosage)
                elif dosage.priority == "3" and dosage.severity() > 4:
                    self.calc_dosage_durations(4, a, dosage)
                elif dosage.priority == "3" and dosage.severity() <= 4:
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
            #proposed_efficient = total_efficient + self.dosage_durations[benchmarks[b + 1]].efficient_duration
            proposed_efficient = self.dosage_durations[benchmarks[b + 1]].efficient_duration
            if 0 < proposed_efficient < 720:
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
                            if d.priority == '3' or (d.priority == '2' and d.severity() <= 4):
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 3:
                        for d in a.dosages:
                            if d.priority == '3':
                                d.efficient_reps_assigned = 0
                                d.efficient_sets_assigned = 0
                    elif self.efficient_winner == 4:
                        for d in a.dosages:
                            if d.priority == '3' and d.severity() <= 4:
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
    def fill_exercises(self, exercise_library, injury_hist_dict):
        pass

    #@staticmethod
    def update_dosage(self, dosage, exercise):

        # if dosage.goal.goal_type == AthleteGoalType.high_load or dosage.goal.goal_type == AthleteGoalType.preempt_sport:
        #     if dosage.priority == "1" or dosage.priority == "2":
        #         dosage.efficient_reps_assigned = exercise.min_reps
        #         dosage.efficient_sets_assigned = 1
        #         dosage.complete_reps_assigned = exercise.max_reps
        #         dosage.complete_sets_assigned = 1
        #         dosage.comprehensive_reps_assigned = exercise.max_reps
        #         dosage.comprehensive_sets_assigned = 2
        #         dosage.default_efficient_reps_assigned = exercise.min_reps
        #         dosage.default_efficient_sets_assigned = 1
        #         dosage.default_complete_reps_assigned = exercise.max_reps
        #         dosage.default_complete_sets_assigned = 1
        #         dosage.default_comprehensive_reps_assigned = exercise.max_reps
        #         dosage.default_comprehensive_sets_assigned = 2

        if dosage.goal.goal_type == AthleteGoalType.high_load or dosage.goal.goal_type == AthleteGoalType.asymmetric_session:
            if self.relative_load_level == 3:
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

            elif self.relative_load_level == 2:
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

            elif self.relative_load_level == 1:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.max_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.max_reps
                    dosage.default_efficient_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.complete_reps_assigned = exercise.max_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.max_reps
                    dosage.default_complete_sets_assigned = 1

                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 1

        if dosage.goal.goal_type == AthleteGoalType.corrective:
            if dosage.priority == "1":
                dosage.efficient_reps_assigned = exercise.max_reps
                dosage.efficient_sets_assigned = 1
                dosage.default_efficient_reps_assigned = exercise.max_reps
                dosage.default_efficient_sets_assigned = 1

            if dosage.priority == "1" or dosage.priority == "2":
                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1

            dosage.comprehensive_reps_assigned = exercise.max_reps
            dosage.comprehensive_sets_assigned = 2
            dosage.default_comprehensive_reps_assigned = exercise.max_reps
            dosage.default_comprehensive_sets_assigned = 2

        if dosage.goal.goal_type == AthleteGoalType.pain or dosage.goal.goal_type == AthleteGoalType.sore:
            # if dosage.last_severity <= 5:
            #     dosage.efficient_reps_assigned = exercise.min_reps
            #     dosage.efficient_sets_assigned = 1
            #     dosage.complete_reps_assigned = exercise.max_reps
            #     dosage.complete_sets_assigned = 1
            #     dosage.comprehensive_reps_assigned = exercise.max_reps
            #     dosage.comprehensive_sets_assigned = 2
            #     dosage.default_efficient_reps_assigned = exercise.min_reps
            #     dosage.default_efficient_sets_assigned = 1
            #     dosage.default_complete_reps_assigned = exercise.max_reps
            #     dosage.default_complete_sets_assigned = 1
            #     dosage.default_comprehensive_reps_assigned = exercise.max_reps
            #     dosage.default_comprehensive_sets_assigned = 2
            # else:
            #     dosage.efficient_reps_assigned = exercise.max_reps
            #     dosage.efficient_sets_assigned = 1
            #     dosage.complete_reps_assigned = exercise.max_reps
            #     dosage.complete_sets_assigned = 2
            #     dosage.comprehensive_reps_assigned = exercise.max_reps
            #     dosage.comprehensive_sets_assigned = 3
            #     dosage.default_efficient_reps_assigned = exercise.max_reps
            #     dosage.default_efficient_sets_assigned = 1
            #     dosage.default_complete_reps_assigned = exercise.max_reps
            #     dosage.default_complete_sets_assigned = 2
            #     dosage.default_comprehensive_reps_assigned = exercise.max_reps
            #     dosage.default_comprehensive_sets_assigned = 3

            if dosage.last_severity < 1.0:
                if dosage.priority == "1":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1

                    dosage.complete_reps_assigned = exercise.max_reps
                    dosage.complete_sets_assigned = 1
                    dosage.default_complete_reps_assigned = exercise.max_reps
                    dosage.default_complete_sets_assigned = 1

                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.comprehensive_reps_assigned = exercise.min_reps
                    dosage.comprehensive_sets_assigned = 1
                    dosage.default_comprehensive_reps_assigned = exercise.min_reps
                    dosage.default_comprehensive_sets_assigned = 1

            elif 1.0 <= dosage.last_severity < 3.0:
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
            elif 3 <= dosage.last_severity < 5:
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
            elif 5 <= dosage.last_severity < 7:
                if dosage.priority == "1" or dosage.priority == "2":
                    dosage.efficient_reps_assigned = exercise.min_reps
                    dosage.efficient_sets_assigned = 1
                    dosage.default_efficient_reps_assigned = exercise.min_reps
                    dosage.default_efficient_sets_assigned = 1
                # trial
                dosage.complete_reps_assigned = exercise.min_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.min_reps
                dosage.default_complete_sets_assigned = 1
                dosage.comprehensive_reps_assigned = exercise.max_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.max_reps
                dosage.default_comprehensive_sets_assigned = 1
            elif 7 <= dosage.last_severity < 9:
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
            elif dosage.last_severity >= 9:
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

        #elif dosage.goal.goal_type == AthleteGoalType.asymmetric_session or dosage.goal.goal_type == AthleteGoalType.asymmetric_pattern:
        # elif dosage.goal.goal_type == AthleteGoalType.asymmetric_session:
        #     if dosage.priority == "1":
        #         dosage.efficient_reps_assigned = exercise.min_reps
        #         dosage.efficient_sets_assigned = 1
        #         dosage.default_efficient_reps_assigned = exercise.min_reps
        #         dosage.default_efficient_sets_assigned = 1
        #
        #     if dosage.priority == "1":
        #         dosage.complete_reps_assigned = exercise.min_reps
        #         dosage.complete_sets_assigned = 1
        #         dosage.default_complete_reps_assigned = exercise.min_reps
        #         dosage.default_complete_sets_assigned = 1
        #
        #     if dosage.priority == "1" or dosage.priority == "2":
        #         dosage.comprehensive_reps_assigned = exercise.min_reps
        #         dosage.comprehensive_sets_assigned = 1
        #         dosage.default_comprehensive_reps_assigned = exercise.min_reps
        #         dosage.default_comprehensive_sets_assigned = 1

        elif dosage.goal.goal_type == AthleteGoalType.on_request:
            if dosage.priority == "1":
                dosage.efficient_reps_assigned = exercise.min_reps
                dosage.efficient_sets_assigned = 1
                dosage.default_efficient_reps_assigned = exercise.min_reps
                dosage.default_efficient_sets_assigned = 1

                dosage.complete_reps_assigned = exercise.max_reps
                dosage.complete_sets_assigned = 1
                dosage.default_complete_reps_assigned = exercise.max_reps
                dosage.default_complete_sets_assigned = 1

            if dosage.priority == "1" or dosage.priority == "2":

                dosage.comprehensive_reps_assigned = exercise.min_reps
                dosage.comprehensive_sets_assigned = 1
                dosage.default_comprehensive_reps_assigned = exercise.min_reps
                dosage.default_comprehensive_sets_assigned = 1

#         elif dosage.goal.goal_type == AthleteGoalType.corrective:  # table 2 corrective
#
#             if dosage.last_severity < 1:
#
#                 if dosage.priority == "1":
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.default_complete_reps_assigned = exercise.min_reps
#                     dosage.default_complete_sets_assigned = 1
#
#                     dosage.comprehensive_reps_assigned = exercise.max_reps
#                     dosage.comprehensive_sets_assigned = 1
#                     dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                     dosage.default_comprehensive_sets_assigned = 1
#
#             elif 1 <= dosage.last_severity < 3:
#
#                 if dosage.priority == "1":
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.default_complete_reps_assigned = exercise.min_reps
#                     dosage.default_complete_sets_assigned = 1
#
#                     dosage.comprehensive_reps_assigned = exercise.max_reps
#                     dosage.comprehensive_sets_assigned = 1
#                     dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                     dosage.default_comprehensive_sets_assigned = 1
#
#             elif 3 <= dosage.last_severity < 5:
#
#                 if dosage.priority == "1":
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.default_complete_reps_assigned = exercise.min_reps
#                     dosage.default_complete_sets_assigned = 1
#                     dosage.comprehensive_reps_assigned = exercise.max_reps
#                     dosage.comprehensive_sets_assigned = 1
#                     dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                     dosage.default_comprehensive_sets_assigned = 1
#
#             # trial
#             elif 5 <= dosage.last_severity <= 10:
#                 dosage.default_efficient_reps_assigned = 0
#                 dosage.default_efficient_sets_assigned = 0
#                 dosage.default_complete_reps_assigned = 0
#                 dosage.default_complete_sets_assigned = 0
#                 dosage.comprehensive_reps_assigned = 0
#                 dosage.comprehensive_sets_assigned = 0
#                 dosage.default_comprehensive_reps_assigned = 0
#                 dosage.default_comprehensive_sets_assigned = 0
#
#             '''trial
#             elif 5 <= dosage.soreness_source.severity < 7:
#
#                 dosage.default_efficient_reps_assigned = exercise.min_reps
#                 dosage.default_efficient_sets_assigned = 1
#                 dosage.default_complete_reps_assigned = exercise.max_reps
#                 dosage.default_complete_sets_assigned = 1
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 2
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 2
#
#             elif 7 <= dosage.soreness_source.severity < 9:
#
#                 dosage.default_efficient_reps_assigned = exercise.max_reps
#                 dosage.default_efficient_sets_assigned = 1
#                 dosage.default_complete_reps_assigned = exercise.max_reps
#                 dosage.default_complete_sets_assigned = 2
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 3
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 3
#
#             elif dosage.soreness_source.severity >= 9:
#
#                 dosage.default_efficient_reps_assigned = exercise.max_reps
#                 dosage.default_efficient_sets_assigned = 1
#                 dosage.default_complete_reps_assigned = exercise.max_reps
#                 dosage.default_complete_sets_assigned = 2
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 3
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 3
#             '''
#
#         elif (dosage.goal.goal_type == AthleteGoalType.sore or
# #              (dosage.soreness_source.historic_soreness_status is None or
#  #              dosage.soreness_source.is_dormant_cleared() or
#   #             dosage.soreness_source.historic_soreness_status is HistoricSorenessStatus.doms) or
#               # dosage.goal.goal_type == AthleteGoalType.preempt_personalized_sport or
#               dosage.goal.goal_type == AthleteGoalType.preempt_corrective):  # table 1
#             if dosage.last_severity < 1:
#                 if dosage.priority == "1":
#                     dosage.efficient_reps_assigned = exercise.min_reps
#                     dosage.efficient_sets_assigned = 1
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.complete_reps_assigned = exercise.min_reps
#                     dosage.complete_sets_assigned = 1
#                     dosage.default_complete_reps_assigned = exercise.min_reps
#                     dosage.default_complete_sets_assigned = 1
#
#                     # trial to reduce active time
#                     dosage.comprehensive_reps_assigned = exercise.min_reps
#                     dosage.comprehensive_sets_assigned = 1
#                     dosage.default_comprehensive_reps_assigned = exercise.min_reps
#                     dosage.default_comprehensive_sets_assigned = 1
#             elif 1 <= dosage.last_severity < 3:
#                 if dosage.priority == "1":
#                     dosage.efficient_reps_assigned = exercise.min_reps
#                     dosage.efficient_sets_assigned = 1
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.complete_reps_assigned = exercise.min_reps
#                     dosage.complete_sets_assigned = 1
#                     dosage.default_complete_reps_assigned = exercise.min_reps
#                     dosage.default_complete_sets_assigned = 1
#
#                     # trial to reduce active time
#                     dosage.comprehensive_reps_assigned = exercise.max_reps
#                     dosage.comprehensive_sets_assigned = 1
#                     dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                     dosage.default_comprehensive_sets_assigned = 1
#             elif 3 <= dosage.last_severity < 5:
#                 if dosage.priority == "1":
#                     dosage.efficient_reps_assigned = exercise.min_reps
#                     dosage.efficient_sets_assigned = 1
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.complete_reps_assigned = exercise.min_reps
#                     dosage.complete_sets_assigned = 1
#                     dosage.default_complete_reps_assigned = exercise.min_reps
#                     dosage.default_complete_sets_assigned = 1
#                 # trial
#                 dosage.comprehensive_reps_assigned = exercise.min_reps
#                 dosage.comprehensive_sets_assigned = 1
#                 dosage.default_comprehensive_reps_assigned = exercise.min_reps
#                 dosage.default_comprehensive_sets_assigned = 1
#             elif 5 <= dosage.last_severity < 7:
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.efficient_reps_assigned = exercise.min_reps
#                     dosage.efficient_sets_assigned = 1
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#                 # trial
#                 dosage.complete_reps_assigned = exercise.min_reps
#                 dosage.complete_sets_assigned = 1
#                 dosage.default_complete_reps_assigned = exercise.min_reps
#                 dosage.default_complete_sets_assigned = 1
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 1
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 1
#             elif 7 <= dosage.last_severity < 9:
#                 dosage.efficient_reps_assigned = exercise.min_reps
#                 dosage.efficient_sets_assigned = 1
#                 dosage.complete_reps_assigned = exercise.max_reps
#                 dosage.complete_sets_assigned = 1
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 2
#                 dosage.default_efficient_reps_assigned = exercise.min_reps
#                 dosage.default_efficient_sets_assigned = 1
#                 dosage.default_complete_reps_assigned = exercise.max_reps
#                 dosage.default_complete_sets_assigned = 1
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 2
#             elif dosage.last_severity >= 9:
#                 dosage.efficient_reps_assigned = exercise.max_reps
#                 dosage.efficient_sets_assigned = 1
#
#                 dosage.complete_reps_assigned = exercise.max_reps
#                 dosage.complete_sets_assigned = 2
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 3
#                 dosage.default_efficient_reps_assigned = exercise.max_reps
#                 dosage.default_efficient_sets_assigned = 1
#
#                 dosage.default_complete_reps_assigned = exercise.max_reps
#                 dosage.default_complete_sets_assigned = 2
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 3
#
#         else:  # table 2
#             if dosage.last_severity < 1:
#                 if dosage.priority == "1":
#                     dosage.efficient_reps_assigned = exercise.min_reps
#                     dosage.efficient_sets_assigned = 1
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.complete_reps_assigned = exercise.min_reps
#                     dosage.complete_sets_assigned = 1
#                     dosage.default_complete_reps_assigned = exercise.min_reps
#                     dosage.default_complete_sets_assigned = 1
#
#                     # trial
#                     dosage.comprehensive_reps_assigned = exercise.max_reps
#                     dosage.comprehensive_sets_assigned = 1
#                     dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                     dosage.default_comprehensive_sets_assigned = 1
#             elif 1 <= dosage.last_severity < 3:
#                 if dosage.priority == "1":
#                     dosage.efficient_reps_assigned = exercise.min_reps
#                     dosage.efficient_sets_assigned = 1
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.complete_reps_assigned = exercise.min_reps
#                     dosage.complete_sets_assigned = 1
#                     dosage.default_complete_reps_assigned = exercise.min_reps
#                     dosage.default_complete_sets_assigned = 1
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 1
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 1
#             elif 3 <= dosage.last_severity < 5:
#                 if dosage.priority == "1" or dosage.priority == "2":
#                     dosage.efficient_reps_assigned = exercise.min_reps
#                     dosage.efficient_sets_assigned = 1
#                     dosage.default_efficient_reps_assigned = exercise.min_reps
#                     dosage.default_efficient_sets_assigned = 1
#                 dosage.complete_reps_assigned = exercise.min_reps
#                 dosage.complete_sets_assigned = 1
#                 dosage.default_complete_reps_assigned = exercise.min_reps
#                 dosage.default_complete_sets_assigned = 1
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 1
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 1
#
#             elif 5 <= dosage.last_severity < 7:
#
#                 dosage.efficient_reps_assigned = exercise.min_reps
#                 dosage.efficient_sets_assigned = 1
#                 dosage.complete_reps_assigned = exercise.max_reps
#                 dosage.complete_sets_assigned = 1
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 2
#                 dosage.default_efficient_reps_assigned = exercise.min_reps
#                 dosage.default_efficient_sets_assigned = 1
#                 dosage.default_complete_reps_assigned = exercise.max_reps
#                 dosage.default_complete_sets_assigned = 1
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 2
#             elif 7 <= dosage.last_severity < 9:
#                 dosage.efficient_reps_assigned = exercise.max_reps
#                 dosage.efficient_sets_assigned = 1
#
#                 dosage.complete_reps_assigned = exercise.max_reps
#                 dosage.complete_sets_assigned = 2
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 3
#                 dosage.default_efficient_reps_assigned = exercise.max_reps
#                 dosage.default_efficient_sets_assigned = 1
#
#                 dosage.default_complete_reps_assigned = exercise.max_reps
#                 dosage.default_complete_sets_assigned = 2
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 3
#             elif dosage.last_severity >= 9:
#                 dosage.efficient_reps_assigned = exercise.max_reps
#                 dosage.efficient_sets_assigned = 1
#
#                 dosage.complete_reps_assigned = exercise.max_reps
#                 dosage.complete_sets_assigned = 2
#                 dosage.comprehensive_reps_assigned = exercise.max_reps
#                 dosage.comprehensive_sets_assigned = 3
#                 dosage.default_efficient_reps_assigned = exercise.max_reps
#                 dosage.default_efficient_sets_assigned = 1
#
#                 dosage.default_complete_reps_assigned = exercise.max_reps
#                 dosage.default_complete_sets_assigned = 2
#                 dosage.default_comprehensive_reps_assigned = exercise.max_reps
#                 dosage.default_comprehensive_sets_assigned = 3

        return dosage

    @staticmethod
    def rank_dosages(target_collections):
        for target_collection in target_collections:
            for ex in target_collection.values():
                ex.set_dosage_ranking()

    def prioritize_dosages(self, exercise_collection, target_ranking, priority):
        for exercise_int, assigned_exercise in exercise_collection.items():
            for dosage in assigned_exercise.dosages:
                if dosage.ranking == target_ranking:
                    dosage.priority = str(priority)
                    dosage.set_reps_and_sets(assigned_exercise.exercise)


class ActiveRest(ModalityBase):
    def __init__(self, event_date_time, force_data=False, relative_load_level=3):
        super().__init__(event_date_time, relative_load_level)
        # self.high_relative_load_session = high_relative_load_session
        # self.high_relative_intensity_logged = high_relative_intensity_logged
        # self.muscular_strain_high = muscular_strain_high
        self.force_data = force_data
        self.event_date_time = event_date_time
        self.inhibit_exercises = {}
        self.static_integrate_exercises = {}
        self.static_stretch_exercises = {}
        self.isolated_activate_exercises = {}

    # @abc.abstractmethod
    # def check_reactive_care_soreness(self, trigger, exercise_library, max_severity):
    #     pass
    #
    # @abc.abstractmethod
    # def check_reactive_care_pain(self, trigger, exercise_library, max_severity):
    #     pass
    #
    # @abc.abstractmethod
    # def check_corrective_soreness(self, trigger, event_date_time, exercise_library, max_severity):
    #     pass
    #
    # @abc.abstractmethod
    # def check_corrective_pain(self, trigger, event_date_time, exercise_library, max_severity):
    #     pass
    @abc.abstractmethod
    def check_recovery(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
        pass

    # @abc.abstractmethod
    # def check_recovery_excessive_strain(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
    #     pass
    #
    # @abc.abstractmethod
    # def check_recovery_compensation(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
    #     pass

    @abc.abstractmethod
    def check_care(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
        pass

    # @abc.abstractmethod
    # def check_care_inflammation(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
    #     pass

    # @abc.abstractmethod
    # def check_care_knots(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
    #     pass

    # @abc.abstractmethod
    # def check_care_movement_pattern(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
    #     pass

    # @abc.abstractmethod
    # def check_care_muscle_spasm(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
    #     pass

    @abc.abstractmethod
    def check_prevention(self, body_part_side, body_part_injury_risk, exercise_library, max_severity):
        pass

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

    def is_body_part_overactive_short(self, body_part_injury_risk):

        #is_short = self.is_body_part_short(body_part_injury_risk)

        is_overactive_short = False

        if body_part_injury_risk.overactive_short_count_last_0_20_days >= 3:
            is_overactive_short = True

        return is_overactive_short

    def is_body_part_overactive_long(self, body_part_injury_risk):

        #is_short = self.is_body_part_short(body_part_injury_risk)

        is_overactive_long = False

        if body_part_injury_risk.overactive_long_count_last_0_20_days >= 3:
            is_overactive_long = True

        return is_overactive_long

    def is_body_part_underactive_long(self, body_part_injury_risk):

        #is_long = self.is_body_part_long(body_part_injury_risk)

        is_underactive_long = False

        if body_part_injury_risk.underactive_long_count_last_0_20_days >= 3:
            is_underactive_long = True

        return is_underactive_long

    def is_body_part_underactive_short(self, body_part_injury_risk):

        #is_short = self.is_body_part_short(body_part_injury_risk)

        is_underactive_short = False

        if body_part_injury_risk.underactive_short_count_last_0_20_days >= 3:
            is_underactive_short = True

        return is_underactive_short

    # def is_body_part_underactive_weak_short(self, body_part_injury_risk):
    #
    #     is_short = self.is_body_part_short(body_part_injury_risk)
    #
    #     is_underactive_weak = self.is_body_part_underactive_weak(body_part_injury_risk)
    #
    #     return is_short and is_underactive_weak

    def is_body_part_long(self, body_part_injury_risk):

        is_short = False

        if body_part_injury_risk.long_count_last_0_20_days >= 3:
            is_short = True
        return is_short

    def is_body_part_short(self, body_part_injury_risk):

        is_short = False

        if body_part_injury_risk.knots_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.tight_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.sharp_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.ache_count_last_0_20_days >= 4:
            is_short = True
        if body_part_injury_risk.short_count_last_0_20_days >= 3:
            is_short = True
        return is_short

    # def is_body_part_overactive(self, body_part_injury_risk):
    #
    #     is_overactive = False
    #
    #     if body_part_injury_risk.overactive_count_last_0_20_days >= 3:
    #         is_overactive = True
    #     return is_overactive

    def is_body_part_weak(self, body_part_injury_risk):

        is_weak = False

        if body_part_injury_risk.weak_count_last_0_20_days >= 3:
            is_weak = True

        return is_weak

    def is_functional_overreaching(self, body_part_injury_risk):
        if (body_part_injury_risk.last_functional_overreaching_date is not None and
              body_part_injury_risk.last_functional_overreaching_date == self.event_date_time.date()):
            return True
        else:
            return False

    def is_non_functional_overreaching(self, body_part_injury_risk):

        two_days_ago = self.event_date_time.date() - datetime.timedelta(days=1)

        if (body_part_injury_risk.last_non_functional_overreaching_date is not None and
              body_part_injury_risk.last_non_functional_overreaching_date >= two_days_ago):
            return True
        else:
            return False

    def is_excessive_strain(self, body_part_injury_risk):

        two_days_ago = self.event_date_time.date() - datetime.timedelta(days=1)

        if (body_part_injury_risk.last_excessive_strain_date is not None and
                body_part_injury_risk.last_excessive_strain_date == self.event_date_time.date()):
            return True
        elif (body_part_injury_risk.last_excessive_strain_date is not None and
              body_part_injury_risk.last_non_functional_overreaching_date is not None and
              body_part_injury_risk.last_non_functional_overreaching_date >= two_days_ago):
            return True
        else:
            return False

    def fill_exercises(self, exercise_library, injury_risk_dict):

        max_severity = 0
        for body_part, body_part_injury_risk in injury_risk_dict.items():
            if (body_part_injury_risk.last_sharp_level > 0 and body_part_injury_risk.last_sharp_date is not None
                    and body_part_injury_risk.last_sharp_date == self.event_date_time.date()):
                max_severity = max(max_severity, body_part_injury_risk.last_sharp_level)
            if (body_part_injury_risk.last_ache_level > 0 and body_part_injury_risk.last_ache_date is not None
                    and body_part_injury_risk.last_ache_date == self.event_date_time.date()):
                max_severity = max(max_severity, body_part_injury_risk.last_ache_level)

        if self.force_data:
            self.get_general_exercises(exercise_library, max_severity)
        else:
            for body_part, body_part_injury_risk in injury_risk_dict.items():
                #self.check_recovery_excessive_strain(body_part, body_part_injury_risk, exercise_library, max_severity)
                #self.check_recovery_compensation(body_part, body_part_injury_risk, exercise_library, max_severity)
                self.check_recovery(body_part, body_part_injury_risk, exercise_library, max_severity)
                #self.check_care_inflammation(body_part, body_part_injury_risk, exercise_library, max_severity)
                #self.check_care_muscle_spasm(body_part, body_part_injury_risk, exercise_library, max_severity)
                self.check_care(body_part, body_part_injury_risk, exercise_library, max_severity)
                #self.check_care_knots(body_part, body_part_injury_risk, exercise_library, max_severity)
                #self.check_care_movement_pattern(body_part, body_part_injury_risk, exercise_library, max_severity)
                self.check_prevention(body_part, body_part_injury_risk, exercise_library, max_severity)

    def get_last_severity(self, body_part_injury_risk):

        last_severity = 0

        if (body_part_injury_risk.last_sharp_level > 0 and body_part_injury_risk.last_sharp_date is not None
                and body_part_injury_risk.last_sharp_date == self.event_date_time.date()):
            last_severity = max(last_severity, body_part_injury_risk.last_sharp_level)
        if (body_part_injury_risk.last_ache_level > 0 and body_part_injury_risk.last_ache_date is not None
                and body_part_injury_risk.last_ache_date == self.event_date_time.date()):
            last_severity = max(last_severity, body_part_injury_risk.last_ache_level)
        if (body_part_injury_risk.last_tight_level > 0 and body_part_injury_risk.last_tight_date is not None
                and body_part_injury_risk.last_tight_date == self.event_date_time.date()):
            last_severity = max(last_severity, body_part_injury_risk.last_tight_level)
        if (body_part_injury_risk.last_knots_level > 0 and body_part_injury_risk.last_knots_date is not None
                and body_part_injury_risk.last_knots_date == self.event_date_time.date()):
            last_severity = max(last_severity, body_part_injury_risk.last_knots_level)

        return last_severity

    def get_general_exercises(self, exercise_library, max_severity):

        pass

    def check_reactive_recover_from_sport_general(self, sports, exercise_library, goal, max_severity):

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
            # if trigger_list[t].trigger_type == TriggerType.hist_sore_less_30:  # 7
            #    goal = AthleteGoal(None, 1, AthleteGoalType.sport)
            # trigger_list[t].goals.append(goal)
            # elif trigger_list[t].trigger_type == TriggerType.overreaching_high_muscular_strain:  # 8
            #    goal = AthleteGoal(None, 1, AthleteGoalType.sport)
            # trigger_list[t].goals.append(goal)
            if trigger_list[t].trigger_type == TriggerType.high_volume_intensity:  # 0
                goal = AthleteGoal("High Load", 1, AthleteGoalType.high_load)
                # trigger_list[t].goals.append(goal)
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
                if body_part is not None:  # and not prohibiting_soreness:
                    self.copy_exercises(body_part.inhibit_exercises,
                                        self.inhibit_exercises, goal, "1", trigger_list[t], exercise_library)
                    # if not prohibiting_soreness:
                    if max_severity < 7:
                        self.copy_exercises(body_part.static_stretch_exercises,
                                            self.static_stretch_exercises, goal, "1", trigger_list[t], exercise_library,
                                            sports)
                    if max_severity < 5:
                        self.copy_exercises(body_part.isolated_activate_exercises,
                                            self.isolated_activate_exercises, goal, "1", trigger_list[t],
                                            exercise_library, sports)

                self.check_reactive_recover_from_sport_general(sports, exercise_library, goal, max_severity)


class ActiveRestBeforeTraining(ActiveRest, Serialisable):
    def __init__(self, event_date_time, force_data=False, relative_load_level=3):
        super().__init__(event_date_time, force_data, relative_load_level)
        self.active_stretch_exercises = {}

    def get_total_exercises(self):
        return len(self.inhibit_exercises) + \
               len(self.static_stretch_exercises) + \
               len(self.active_stretch_exercises) + \
               len(self.isolated_activate_exercises) + \
               len(self.static_integrate_exercises)

    def json_serialise(self):
        ret = {
            # 'high_relative_load_session': self.high_relative_load_session,
            # 'high_relative_intensity_logged': self.high_relative_intensity_logged,
            # 'muscular_strain_high': self.muscular_strain_high,
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises.values()],
            'active_stretch_exercises': [p.json_serialise() for p in self.active_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(
                self.completed_date_time) if self.completed_date_time is not None else None,
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
        pre_active_rest = cls(  # high_relative_load_session=input_dict.get('high_relative_load_session', False),
            # high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
            # muscular_strain_high=input_dict.get('muscular_strain_high', False),
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
        pre_active_rest.goals = {AthleteGoalType(int(goal_type)): ModalityGoal.json_deserialise(goal) for
                                 (goal_type, goal) in input_dict.get('goals', {}).items()}

        return pre_active_rest

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

    def check_reactive_recover_from_sport_general(self, sports, exercise_library, goal, max_severity):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_body_part_for_sports(sports)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, "1", None,
                                    exercise_library)
                # self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
                #                    None, exercise_library)
                if max_severity < 7:
                    self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, "1",
                                        None, exercise_library)

        if max_severity < 5:
            for t in body_part.antagonists:
                antagonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
                if antagonist is not None:
                    self.copy_exercises(antagonist.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        "1",
                                        None, exercise_library)

        if max_severity < 5:
            self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, "1", None,
                                exercise_library)

    def get_general_exercises(self, exercise_library, max_severity):

        body_part_factory = BodyPartFactory()

        body_part = body_part_factory.get_general()

        goal = AthleteGoal("Improve mobility", 1, AthleteGoalType.on_request)

        for a in body_part.agonists:
            agonist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(a), None))
            if agonist is not None:
                self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, 1, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, 1, 0, exercise_library)
                    self.copy_exercises(agonist.active_stretch_exercises, self.active_stretch_exercises, goal, 1, 0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(agonist.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        1, 0, exercise_library)

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
                self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, 2, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal, 2, 0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        2, 0, exercise_library)

        for t in body_part.stabilizers:
            stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if stabilizer is not None:
                self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, 3, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(stabilizer.active_stretch_exercises, self.active_stretch_exercises, goal, 3, 0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(stabilizer.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        3, 0, exercise_library)

        if max_severity < 5:
            self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, 1, 0,
                                exercise_library)

    def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity):

        goals = []

        compensating = False
        high_load = False

        if body_part is not None:

            if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
                #goals.append(AthleteGoal("Recover from Training", 1, AthleteGoalType.high_load))
                high_load = True

            if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
                    body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):

                compensating = True
            elif (body_part_injury_risk.last_compensation_date is not None
                  and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
                  body_part_injury_risk.total_compensation_percent_tier <= 3):

                compensating = True

            #if compensating:
                #goals.append(AthleteGoal("Recover from Training", 1, AthleteGoalType.asymmetric_session))

            #for goal in goals:

            goal = AthleteGoal("Recover from Training", 1, AthleteGoalType.high_load)

            if high_load or compensating:

                if high_load:
                    tier = body_part_injury_risk.total_volume_percent_tier
                else: #compensating
                    tier = body_part_injury_risk.total_compensation_percent_tier

                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal,
                                    tier, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal,
                                        tier, 0, exercise_library)

            if high_load:

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        body_part_injury_risk.total_volume_percent_tier,
                                        0, exercise_library)


    # def check_recovery_excessive_strain(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     if body_part is not None:
    #
    #         goal = AthleteGoal("Elevated Stress", 1, AthleteGoalType.high_load)
    #
    #         if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, body_part_injury_risk.total_volume_percent_tier, 0, exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, body_part_injury_risk.total_volume_percent_tier,
    #                                     0, exercise_library)
    #             if max_severity < 5.0:
    #                 self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal, body_part_injury_risk.total_volume_percent_tier,
    #                                     0, exercise_library)
    #
    # def check_recovery_compensation(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     compensating = False
    #
    #     if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
    #         body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):
    #
    #         compensating = True
    #     elif (body_part_injury_risk.last_compensation_date is not None
    #             and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
    #             body_part_injury_risk.total_compensation_percent_tier <= 3):
    #
    #         compensating = True
    #
    #     if compensating:
    #
    #         goal = AthleteGoal("Compensations", 1, AthleteGoalType.asymmetric_session)
    #
    #         self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, body_part_injury_risk.total_compensation_percent_tier, 0,
    #                             exercise_library)
    #
    #         if max_severity < 7.0:
    #             self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises,
    #                                 goal, body_part_injury_risk.total_compensation_percent_tier, 0,
    #                                 exercise_library)

    def check_care(self, body_part, body_part_injury_risk, exercise_library, max_severity):

        goals = []

        muscle_spasm = False
        knots = False
        inflammation = False

        if (body_part_injury_risk.last_inflammation_date is not None and
                body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
            #goals.append(AthleteGoal("Care for symptoms", 1, AthleteGoalType.pain))
            inflammation = True

        if (body_part_injury_risk.last_muscle_spasm_date is not None and
                body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
            muscle_spasm = True

        if (body_part_injury_risk.last_knots_date is not None and
                body_part_injury_risk.last_knots_date == self.event_date_time.date()):
            knots = True

        # if muscle_spasm or knots:
        #     goals.append(AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore))

        #for goal in goals:
        goal = AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore)

        if muscle_spasm or knots or inflammation:

            last_severity = 0

            if muscle_spasm:
                last_severity = max(last_severity, body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
            if knots:
                last_severity = max(last_severity, body_part_injury_risk.get_knots_severity(self.event_date_time.date()))
            if inflammation:
                last_severity = max(last_severity, body_part_injury_risk.get_inflammation_severity(self.event_date_time.date()))

            self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 1, last_severity,
                                exercise_library)

            if max_severity < 7.0:
                self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, 1,
                                    last_severity, exercise_library)

            body_part_factory = BodyPartFactory()

            for s in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
                self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, 2, last_severity,
                                    exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(synergist.active_stretch_exercises, self.active_stretch_exercises, goal, 2,
                                        last_severity, exercise_library)

        if muscle_spasm or knots:

            last_severity = 0

            if muscle_spasm:
                last_severity = max(last_severity,
                                    body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
            if knots:
                last_severity = max(last_severity,
                                    body_part_injury_risk.get_knots_severity(self.event_date_time.date()))

            if max_severity < 7.0:
                self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 1,
                                    last_severity, exercise_library)

            body_part_factory = BodyPartFactory()

            for s in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))

                if max_severity < 7.0:
                    self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, 2,
                                        last_severity, exercise_library)

    # def check_care_inflammation(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     if (body_part_injury_risk.last_inflammation_date is not None and
    #             body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
    #
    #         goal = AthleteGoal("Inflammation", 1, AthleteGoalType.pain)
    #
    #         if body_part is not None:
    #
    #             last_severity = body_part_injury_risk.get_inflammation_severity(self.event_date_time.date())
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 0, last_severity, exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, 0,
    #                                     last_severity, exercise_library)
    #
    # def check_care_muscle_spasm(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     muscle_spasm = False
    #     knots = False
    #
    #     if (body_part_injury_risk.last_muscle_spasm_date is not None and
    #             body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
    #
    #         muscle_spasm = True
    #
    #     if (body_part_injury_risk.last_knots_date is not None and
    #             body_part_injury_risk.last_knots_date == self.event_date_time.date()):
    #
    #         knots = True
    #
    #     if muscle_spasm or knots:
    #
    #         goal = AthleteGoal("Tightness", 1, AthleteGoalType.sore)
    #
    #         if body_part is not None:
    #
    #             if muscle_spasm:
    #                 last_severity = body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date())
    #             else:
    #                 last_severity = body_part_injury_risk.get_knots_severity(self.event_date_time.date())
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 0, last_severity, exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 0,
    #                                     last_severity, exercise_library)
    #                 self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, 0,
    #                                     last_severity, exercise_library)

    # def check_care_knots(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     #body_part_factory = BodyPartFactory()
    #
    #     if (body_part_injury_risk.last_knots_date is not None and
    #             body_part_injury_risk.last_knots_date == self.event_date_time.date()):
    #
    #         #body_part = body_part_factory.get_body_part(body_part_side)
    #
    #         goal = AthleteGoal("Tightness", 1, AthleteGoalType.sore)
    #
    #         if body_part is not None:
    #
    #             # last_severity = self.get_last_severity(body_part_injury_risk)
    #             #last_severity = 2.5
    #             last_severity = body_part_injury_risk.get_knots_severity(self.event_date_time.date())
    #
    #             ranking = 3
    #
    #             if last_severity >= 7:
    #                 ranking = 1
    #             elif 4 <= last_severity < 7:
    #                 ranking = 2
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 0, last_severity, ranking,
    #                                 exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 0,
    #                                     last_severity, ranking, exercise_library)
    #                 self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, 0,
    #                                     last_severity, ranking, exercise_library)

    # def check_care_movement_pattern(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     #body_part_factory = BodyPartFactory()
    #
    #     if (body_part_injury_risk.last_overactive_short_date is not None and
    #             body_part_injury_risk.last_overactive_short_date == self.event_date_time.date() and
    #             body_part_injury_risk.overactive_short_count_last_0_20_days < 3):
    #
    #         #body_part = body_part_factory.get_body_part(body_part_side)
    #
    #         goal = AthleteGoal("Tightness", 1, AthleteGoalType.sore)
    #
    #         if body_part is not None:
    #
    #             #last_severity = self.get_last_severity(body_part_injury_risk)
    #             last_severity = 2.5
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", last_severity, exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
    #                                     last_severity, exercise_library)
    #                 self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, "1",
    #                                     last_severity, exercise_library)

    def check_prevention(self, body_part, body_part_injury_risk, exercise_library, max_severity):

        #body_part_factory = BodyPartFactory()

        #body_part = body_part_factory.get_body_part(body_part_side)

        if body_part is not None:

            is_short = self.is_body_part_short(body_part_injury_risk)
            #is_overactive = self.is_body_part_overactive(body_part_injury_risk)
            #is_underactive_weak = self.is_body_part_underactive_weak(body_part_injury_risk)
            #is_underactive_inhibited = self.is_body_part_underactive_inhibited(body_part_injury_risk)
            is_overactive_short = self.is_body_part_overactive_short(body_part_injury_risk)
            is_overactive_long = self.is_body_part_overactive_long(body_part_injury_risk)
            is_underactive_long = self.is_body_part_underactive_long(body_part_injury_risk)
            is_underactive_short = self.is_body_part_underactive_short(body_part_injury_risk)
            is_weak = self.is_body_part_weak(body_part_injury_risk)
            #is_underactive_weak_short = self.is_body_part_underactive_weak_short(body_part_injury_risk)

            #last_severity = self.get_last_severity(body_part_injury_risk)
            non_isolated_severity = 2.5
            if is_weak:
                isolated_severity = 7.5
            else:
                isolated_severity = 2.5

            tier_one = False

            if is_overactive_short:
                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 1, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 1,
                                        0, exercise_library)
                    # self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, "1",
                    #                     last_severity, exercise_library)

            elif is_underactive_long or is_weak:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal, 1,
                                        0, exercise_library)

            elif is_overactive_long:
                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 1, 0, exercise_library)

            elif is_underactive_short:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 1, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 1, 0, exercise_library)
                    self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, 1, 0, exercise_library)
                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal, 1, 0, exercise_library)

            elif is_short:
                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 2, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 1,
                                        0, exercise_library)

            if not tier_one and body_part_injury_risk.limited_mobility_tier == 2:
                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)

                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 2,
                                    0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 2, 0, exercise_library)
                    # self.copy_exercises(body_part.active_stretch_exercises, self.active_stretch_exercises, goal, "1",
                    #                     last_severity, exercise_library)

            if not tier_one and body_part_injury_risk.underactive_weak_tier == 2:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        2, 0, exercise_library)

    def set_exercise_dosage_ranking(self):
        ordered_ranks = sorted(self.rankings)
        rank_max = min(3, len(ordered_ranks))
        for r in range(0, rank_max):
            current_ranking = ordered_ranks[r]
            self.prioritize_dosages(self.inhibit_exercises, current_ranking, r + 1)
            self.prioritize_dosages(self.static_stretch_exercises, current_ranking, r + 1)
            self.prioritize_dosages(self.active_stretch_exercises, current_ranking, r + 1)
            self.prioritize_dosages(self.isolated_activate_exercises, current_ranking, r + 1)
            self.prioritize_dosages(self.static_integrate_exercises, current_ranking, r + 1)
        # self.rank_dosages([self.inhibit_exercises,
        #                    self.static_stretch_exercises,
        #                    self.active_stretch_exercises,
        #                    self.isolated_activate_exercises,
        #                    self.static_integrate_exercises])


class ActiveRestAfterTraining(ActiveRest, Serialisable):
    def __init__(self, event_date_time, force_data=False, relative_load_level=3):
        super().__init__(event_date_time, force_data, relative_load_level)

    def get_total_exercises(self):
        return len(self.inhibit_exercises) + \
               len(self.static_stretch_exercises) + \
               len(self.isolated_activate_exercises) + \
               len(self.static_integrate_exercises)

    def json_serialise(self):
        ret = {
            # 'high_relative_load_session': self.high_relative_load_session,
            # 'high_relative_intensity_logged': self.high_relative_intensity_logged,
            # 'muscular_strain_high': self.muscular_strain_high,
            'inhibit_exercises': [p.json_serialise() for p in self.inhibit_exercises.values()],
            'static_stretch_exercises': [p.json_serialise() for p in self.static_stretch_exercises.values()],
            'isolated_activate_exercises': [p.json_serialise() for p in self.isolated_activate_exercises.values()],
            'static_integrate_exercises': [p.json_serialise() for p in self.static_integrate_exercises.values()],
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'completed_date_time': format_datetime(
                self.completed_date_time) if self.completed_date_time is not None else None,
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
        post_active_rest = cls(  # high_relative_load_session=input_dict.get('high_relative_load_session', False),
            # high_relative_intensity_logged=input_dict.get('high_relative_intensity_logged', False),
            # muscular_strain_high=input_dict.get('muscular_strain_high', False),
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
        post_active_rest.goals = {AthleteGoalType(int(goal_type)): ModalityGoal.json_deserialise(goal) for
                                  (goal_type, goal) in input_dict.get('goals', {}).items()}

        return post_active_rest

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
                    self.copy_exercises(antagonist.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        "1",
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
                self.copy_exercises(agonist.inhibit_exercises, self.inhibit_exercises, goal, 1, 0,
                                    exercise_library)
                if max_severity < 7:
                    self.copy_exercises(agonist.static_stretch_exercises, self.static_stretch_exercises, goal, 1,
                                        0, exercise_library)
                if max_severity < 5:
                    self.copy_exercises(agonist.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        1, 0, exercise_library)

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
                self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, 2, 0,
                                    exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, 2,
                                        0, exercise_library)
                if max_severity < 2.5:
                    self.copy_exercises(synergist.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        2, 0, exercise_library)

        for t in body_part.stabilizers:
            stabilizer = body_part_factory.get_body_part(BodyPart(BodyPartLocation(t), None))
            if stabilizer is not None:
                self.copy_exercises(stabilizer.inhibit_exercises, self.inhibit_exercises, goal, 3, 0,
                                    exercise_library)
                if max_severity < 3.5:
                    self.copy_exercises(stabilizer.static_stretch_exercises, self.static_stretch_exercises, goal, 3,
                                        0, exercise_library)
                if max_severity < 2.5:
                    self.copy_exercises(stabilizer.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        3, 0, exercise_library)

        if max_severity < 2.5:
            self.copy_exercises(body_part.static_integrate_exercises, self.static_integrate_exercises, goal, 1, 0,
                                exercise_library)

    def check_recovery(self, body_part, body_part_injury_risk, exercise_library, max_severity):

        goals = []

        compensating = False
        high_load = False

        if body_part is not None:

            if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
                #goals.append(AthleteGoal("Recover from Training", 1, AthleteGoalType.high_load))
                high_load = True

            if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
                    body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):

                compensating = True
            elif (body_part_injury_risk.last_compensation_date is not None
                  and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
                  body_part_injury_risk.total_compensation_percent_tier <= 3):

                compensating = True

            # if compensating:
            #     goals.append(AthleteGoal("Recover from Training", 1, AthleteGoalType.asymmetric_session))

            #for goal in goals:
            goal = AthleteGoal("Recover from Training", 1, AthleteGoalType.high_load)

            if high_load or compensating:

                if high_load:
                    tier = body_part_injury_risk.total_volume_percent_tier
                else: #compensating
                    tier = body_part_injury_risk.total_compensation_percent_tier

                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal,
                                    tier, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal,
                                        tier, 0, exercise_library)

            if high_load:

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        body_part_injury_risk.total_volume_percent_tier,
                                        0, exercise_library)

    # def check_recovery_excessive_strain(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     if body_part is not None:
    #
    #         goal = AthleteGoal("Elevated Stress", 1, AthleteGoalType.high_load)
    #
    #         if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, body_part_injury_risk.total_volume_percent_tier, 0,
    #                                 exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, body_part_injury_risk.total_volume_percent_tier,
    #                                     0, exercise_library)
    #
    #             if max_severity < 5.0:
    #                 self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal,
    #                                     body_part_injury_risk.total_volume_percent_tier, 0, exercise_library)
    #
    # def check_recovery_compensation(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     compensating = False
    #
    #     if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
    #             body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):
    #
    #         compensating = True
    #     elif (body_part_injury_risk.last_compensation_date is not None
    #           and body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
    #           body_part_injury_risk.total_compensation_percent_tier <= 3):
    #
    #         compensating = True
    #
    #     if compensating:
    #
    #         goal = AthleteGoal("Compensations", 1, AthleteGoalType.asymmetric_session)
    #
    #         if body_part is not None:
    #
    #             # last_severity = self.get_last_severity(body_part_injury_risk)
    #             last_severity = 2.5  # hacking this now
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, body_part_injury_risk.total_compensation_percent_tier, 0,
    #                                 exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, body_part_injury_risk.total_compensation_percent_tier, 0,
    #                                     exercise_library)

    def check_care(self, body_part, body_part_injury_risk, exercise_library, max_severity):

        goals = []

        muscle_spasm = False
        knots = False
        inflammation = False

        if (body_part_injury_risk.last_inflammation_date is not None and
                body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
            #goals.append(AthleteGoal("Care for symptoms", 1, AthleteGoalType.pain))
            inflammation = True

        if (body_part_injury_risk.last_muscle_spasm_date is not None and
                body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
            muscle_spasm = True

        if (body_part_injury_risk.last_knots_date is not None and
                body_part_injury_risk.last_knots_date == self.event_date_time.date()):
            knots = True

        # if muscle_spasm or knots:
        #     goals.append(AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore))

        #for goal in goals:
        goal = AthleteGoal("Care for symptoms", 1, AthleteGoalType.sore)

        if muscle_spasm or knots or inflammation:

            last_severity = 0

            if muscle_spasm:
                last_severity = max(last_severity, body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
            if knots:
                last_severity = max(last_severity, body_part_injury_risk.get_knots_severity(self.event_date_time.date()))
            if inflammation:
                last_severity = max(last_severity, body_part_injury_risk.get_inflammation_severity(self.event_date_time.date()))

            self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 1, last_severity,
                                exercise_library)

            if max_severity < 7.0:
                self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 1,
                                    last_severity, exercise_library)

            body_part_factory = BodyPartFactory()

            for s in body_part.synergists:
                synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
                self.copy_exercises(synergist.inhibit_exercises, self.inhibit_exercises, goal, 2, last_severity,
                                    exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, 2,
                                        last_severity, exercise_library)

        # if muscle_spasm or knots:
        #
        #     last_severity = 0
        #
        #     if muscle_spasm:
        #         last_severity = max(last_severity,
        #                             body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date()))
        #     if knots:
        #         last_severity = max(last_severity,
        #                             body_part_injury_risk.get_knots_severity(self.event_date_time.date()))
        #
        #     if max_severity < 7.0:
        #         self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 1,
        #                             last_severity, exercise_library)
        #
        #     body_part_factory = BodyPartFactory()
        #
        #     for s in body_part.synergists:
        #         synergist = body_part_factory.get_body_part(BodyPart(BodyPartLocation(s), None))
        #
        #         if max_severity < 7.0:
        #             self.copy_exercises(synergist.static_stretch_exercises, self.static_stretch_exercises, goal, 2,
        #                                 last_severity, exercise_library)

    # def check_care_inflammation(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #
    #     if (body_part_injury_risk.last_inflammation_date is not None and
    #             body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
    #
    #         goal = AthleteGoal("Inflammation", 1, AthleteGoalType.pain)
    #
    #         if body_part is not None:
    #
    #             last_severity = body_part_injury_risk.get_inflammation_severity(self.event_date_time.date())
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 0, last_severity,
    #                                 exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 0,
    #                                     last_severity, exercise_library)
    #
    # def check_care_muscle_spasm(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     muscle_spasm = False
    #     knots = False
    #
    #     if (body_part_injury_risk.last_muscle_spasm_date is not None and
    #             body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
    #         muscle_spasm = True
    #
    #     if (body_part_injury_risk.last_knots_date is not None and
    #             body_part_injury_risk.last_knots_date == self.event_date_time.date()):
    #         knots = True
    #
    #     if muscle_spasm or knots:
    #
    #         goal = AthleteGoal("Tightness", 1, AthleteGoalType.sore)
    #
    #         if body_part is not None:
    #
    #             if muscle_spasm:
    #                 last_severity = body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date())
    #             else:
    #                 last_severity = body_part_injury_risk.get_knots_severity(self.event_date_time.date())
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 0, last_severity,
    #                                 exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 0,
    #                                     last_severity, exercise_library)

    # def check_care_knots(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     #body_part_factory = BodyPartFactory()
    #
    #     if (body_part_injury_risk.last_knots_date is not None and
    #             body_part_injury_risk.last_knots_date == self.event_date_time.date()):
    #
    #         #body_part = body_part_factory.get_body_part(body_part_side)
    #
    #         goal = AthleteGoal("Tightness", 1, AthleteGoalType.sore)
    #
    #         if body_part is not None:
    #
    #             # last_severity = self.get_last_severity(body_part_injury_risk)
    #             last_severity = 2.5
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", last_severity, exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
    #                                     last_severity, exercise_library)

    # def check_care_movement_pattern(self, body_part, body_part_injury_risk, exercise_library, max_severity):
    #
    #     #body_part_factory = BodyPartFactory()
    #
    #     if (body_part_injury_risk.last_overactive_short_date is not None and
    #             body_part_injury_risk.last_overactive_short_date == self.event_date_time.date() and
    #             body_part_injury_risk.overactive_short_count_last_0_20_days < 3):
    #
    #         #body_part = body_part_factory.get_body_part(body_part_side)
    #
    #         goal = AthleteGoal("Tightness", 1, AthleteGoalType.sore)
    #
    #         if body_part is not None:
    #
    #             # last_severity = self.get_last_severity(body_part_injury_risk)
    #             last_severity = 2.5
    #
    #             self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, "1", last_severity, exercise_library)
    #
    #             if max_severity < 7.0:
    #                 self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, "1",
    #                                     last_severity, exercise_library)

    def check_prevention(self, body_part, body_part_injury_risk, exercise_library, max_severity):

        if body_part is not None:

            is_short = self.is_body_part_short(body_part_injury_risk)
            is_overactive_short = self.is_body_part_overactive_short(body_part_injury_risk)
            is_overactive_long = self.is_body_part_overactive_long(body_part_injury_risk)
            is_underactive_short = self.is_body_part_underactive_short(body_part_injury_risk)
            is_underactive_long = self.is_body_part_underactive_long(body_part_injury_risk)
            is_weak = self.is_body_part_weak(body_part_injury_risk)

            # last_severity = self.get_last_severity(body_part_injury_risk)
            last_severity = 2.5
            if is_weak:
                isolated_severity = 7.5
            else:
                isolated_severity = 2.5

            tier_one = False

            if is_overactive_short:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 1, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 1,
                                        0, exercise_library)

            elif is_underactive_long or is_weak:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal, 1,
                                        0, exercise_library)

            elif is_overactive_long:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 1, 0, exercise_library)

            elif is_underactive_short:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 1, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 1, 0, exercise_library)

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        1, 0, exercise_library)

            elif is_short:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)
                tier_one = True
                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 2, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 2,
                                        0, exercise_library)

            if not tier_one and body_part_injury_risk.limited_mobility_tier == 2:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)

                self.copy_exercises(body_part.inhibit_exercises, self.inhibit_exercises, goal, 2, 0, exercise_library)

                if max_severity < 7.0:
                    self.copy_exercises(body_part.static_stretch_exercises, self.static_stretch_exercises, goal, 2,
                                        0, exercise_library)

            if not tier_one and body_part_injury_risk.underactive_weak_tier == 2:

                goal = AthleteGoal("Reduce injury risks", 1, AthleteGoalType.corrective)

                if max_severity < 5.0:
                    self.copy_exercises(body_part.isolated_activate_exercises, self.isolated_activate_exercises, goal,
                                        2, 0, exercise_library)

    def set_exercise_dosage_ranking(self):
        ordered_ranks = sorted(self.rankings)
        rank_max = min(3, len(ordered_ranks))
        for r in range(0, rank_max):
            current_ranking = ordered_ranks[r]
            self.prioritize_dosages(self.inhibit_exercises, current_ranking, r + 1)
            self.prioritize_dosages(self.static_stretch_exercises, current_ranking, r + 1)
            self.prioritize_dosages(self.isolated_activate_exercises, current_ranking, r + 1)
            self.prioritize_dosages(self.static_integrate_exercises, current_ranking, r + 1)

        # self.rank_dosages([self.inhibit_exercises,
        #                    self.static_stretch_exercises,
        #                    self.isolated_activate_exercises,
        #                    self.static_integrate_exercises])




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
            'completed_date_time': format_datetime(
                self.completed_date_time) if self.completed_date_time is not None else None,
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
            'completed_date_time': format_datetime(
                self.completed_date_time) if self.completed_date_time is not None else None,
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
